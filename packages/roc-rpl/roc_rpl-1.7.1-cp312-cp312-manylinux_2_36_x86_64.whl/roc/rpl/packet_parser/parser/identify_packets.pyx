#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from roc.idb.parsers.idb_parser import IDBParser

from roc.rpl import Time
from roc.rpl.packet_parser.extended_data import ExtendedData
from roc.rpl.constants import TM_PACKET_TYPE, \
    TC_PACKET_TYPE, INVALID_UTC_DATETIME, \
    UNKNOWN_UNIQUE_ID, UNKNOWN_ACK_STATE, INVALID_PACKET_HEADER, \
    OUTSIDE_RANGE_PACKET, VALID_PACKET, INVALID_PACKET_TIME

from roc.rpl.packet_parser import PacketParser

__all__ = ["identify_packets"]

cpdef tuple get_packet_id(object raw_binary_packet, object idb,
                          srdb_id=None, palisade_id=None):
    """
    Get packet ids (SRDB_ID and PALISADE_ID)

    :param raw_binary_packet: String containing the binary raw data of the packet (in hexa)
    :param idb: idb manager (from PacketParser class instance)
    :param srdb_id: packet SRDB ID (if passed, skip srdb id retrieval from database)
    :param palisade_id: packet PALISADE ID (if passed, skip srdb id retrieval from database)
    :return: srdb_id, palisade_id, packet_header, data_field_header
    """
    cdef:
        object byte_data

    # Convert hex to bytes
    byte_data = PacketParser.hex_to_bytes(raw_binary_packet)
    # Get IDs of the packet
    return ExtendedData(bytes(byte_data),
                        len(byte_data),
                        idb).get_packet_summary(srdb_id=srdb_id,
                                                palisade_id=palisade_id)


cdef dict identify_packet(int packet_idx,
                          dict packet_data,
                          object packet_parser,
                          start_time=None,
                          end_time=None):
    """
    Given a dict containing the binary data [and optionally the utc time] of the packet, return an identified packet
     and allocate space for data in the packet manager.

    :param packet_idx: Index of the current packet
    :param packet_data: dictionary containing packet data
    :param packet_parser: Instance of PacketParser class
    :param start_time: Only keep packet(s) created/executed after start_time (UTC)
    :param end_time: Only keep packet(s) created/executed before end_time (UTC)
    :return: dictionary with packet information (empty packet is returned if outside start_time/end_time)
    """
    cdef:
        unsigned long coarse
        unsigned long fine
        unsigned long expected_length
        unsigned long actual_length
        object comment

    # Make sure to have comment in packet_data dict
    comment = packet_data.get('comment')
    if comment is None:
        packet_data['comment'] = ''

    # Check if input packet has the required keyword
    packet_data['binary'] = packet_data.get('binary',
                                            PacketParser.get_binary(packet_data))
    if packet_data['binary'] is None:
        return packet_data

    # Store idb_source in packet_data
    packet_data['idb_source'] = packet_parser.idb_source

    # Store idb_version in packet_data
    packet_data['idb_version'] = packet_parser.idb_version

    # Retrieve packet SRDB_ID, PALISADE_ID using IDB version stored in the ROC database
    # (return the packet header and data_header at the same time)
    try:
        packet_data['srdb_id'], packet_data['palisade_id'], packet_data['header'], \
            packet_data['data_header'] = get_packet_id(packet_data["binary"], packet_parser.idb,
                                                       srdb_id=packet_data.get(
                                                           'srdb_id'),
                                                       palisade_id=packet_data.get('palisade_id'))
    except:
        msg = f'Packet #{packet_idx + 1} cannot be analysed! [{packet_data["binary"]}]'
        packet_data['comment'] = msg
        packet_data['status'] = INVALID_PACKET_HEADER
        return packet_data


    # skip the next steps if the name is unknown
    if packet_data['srdb_id'] is None:
        msg = f'Packet #{packet_idx + 1} cannot be identified! [{packet_data["binary"]}]. '
        packet_data['status'] = INVALID_PACKET_HEADER
        packet_data['comment'] += msg
        return packet_data

    # Compute APID
    try:
        packet_data['apid'] = IDBParser.compute_apid(packet_data['header'].process_id,
                                                     packet_data['header'].packet_category)
    except:
        msg = f'APID cannot be computed for {packet_data}. '
        packet_data['comment'] += msg

    # Get/create packet category
    packet_data['category'] = packet_data.get('category',
                                              packet_parser.palisade_metadata[packet_data['srdb_id']]['packet_category'])

    # Get UTC time of the packet generation if TM...
    if packet_data['header'].packet_type == TM_PACKET_TYPE:

        packet_data['type'] = 'TM'
        # Get packet scet or compute it
        packet_data['scet'] = packet_data.get('scet',
                                              Time().cuc_to_scet([packet_data['data_header'].time])[0])

        # Get utc_time or compute it for current TM packet
        try:
            packet_data['utc_time'] = Time().obt_to_utc(
                [packet_data['data_header'].time[:2]], to_datetime=True)[0]
        except:
            packet_data['utc_time'] = INVALID_UTC_DATETIME

        # Get time sync flag
        packet_data['sync_flag'] = (
            packet_data['data_header'].time[2] == 0)

       # Get/create on-board time using SPICE format
        coarse = packet_data['data_header'].time[0]
        fine = packet_data['data_header'].time[1]
        packet_data['obt_time'] = packet_data.get('obt_time',
                                                  f"1/{coarse}:{fine}")

    # If TC packet, then get execution time from tc report
    elif packet_data['header'].packet_type == TC_PACKET_TYPE:

        # Convert TC execution UTC time in datetime object
        packet_data['utc_time'] = packet_data.get('utc_time',
                                                  INVALID_UTC_DATETIME)
        packet_data['type'] = 'TC'
        packet_data['scet'] = None

        # Get TC acknowledgement status (acceptance and execution)
        packet_data['ack_exe_state'] = packet_data.get(
            'ack_exe_state', UNKNOWN_ACK_STATE)
        packet_data['ack_acc_state'] = packet_data.get(
            'ack_acc_state', UNKNOWN_ACK_STATE)

        # Get unique ID (if any)
        packet_data['unique_id'] = packet_data.get(
            'unique_id', UNKNOWN_UNIQUE_ID)

        # Get unique ID (if any)
        packet_data['sequence_name'] = packet_data.get('sequence_name', None)

    else:
        msg = f"Unknown packet_type {packet_data['header'].packet_type} " \
            f"for packet #{packet_idx} [{packet_data['srdb_id']}]. "
        packet_data['comment'] += msg
        packet_data['status'] = INVALID_PACKET_HEADER
        return packet_data

    # Get/create packet SHA
    packet_data['sha'] = PacketParser.get_packet_sha(packet_data)

    # Check that the packet length is as expected
    expected_length = packet_data['header'].packet_length + 7
    packet_data['length'] = expected_length
    actual_length = len(PacketParser.hex_to_bytes(packet_data['binary']))
    if expected_length != actual_length:
        msg = f"Packet {packet_data['palisade_id']} {{{packet_data['srdb_id']}}} on " \
            f"{packet_data['utc_time']} has not expected length: " \
            f"expected is {expected_length} and actual is {actual_length}. "
        packet_data['status'] = INVALID_PACKET_HEADER
        packet_data['comment'] += msg
        return packet_data

    # If input argument start_time has been provided...
    if (packet_data['utc_time'] != INVALID_UTC_DATETIME and
            start_time and start_time > packet_data['utc_time']):
        packet_data['status'] = OUTSIDE_RANGE_PACKET
        msg = (f"Packet {packet_data['palisade_id']} {{{packet_data['srdb_id']}}} on "
               f"{packet_data['utc_time']} is outside the time range. ")
        packet_data["comment"] += msg
        return packet_data

    # If input argument end_time has been provided...
    if (packet_data['utc_time'] != INVALID_UTC_DATETIME and
            end_time and end_time < packet_data['utc_time']):
        packet_data["status"] = OUTSIDE_RANGE_PACKET
        msg = (f"Packet {packet_data['palisade_id']} {{{packet_data['srdb_id']}}} on "
               f"{packet_data['utc_time']} is outside the time range. ")
        packet_data["comment"] += msg
        return packet_data

    if packet_data['utc_time'] == INVALID_UTC_DATETIME:
        packet_data["status"] = INVALID_PACKET_TIME
        packet_data['comment'] = f'Packet generation time cannot be converted into valid UTC time'
        return packet_data

    packet_data['status'] = VALID_PACKET

    return packet_data


cpdef list identify_packets(object packet_parser,
                            list packet_list,
                            start_time=None,
                            end_time=None):
    """
    Given a list of packets, analyze the binary content
    to identify the packets and allocate space for data.

    :param packet_parser: instance of PacketParser class
    :param packet_list: List of packets to identify
    :param start_time: Only keep packet(s) created/executed after start_time
    :param end_time: Only keep packet(s) created/executed before end_time
    :return: Store results in the PacketParser object
    """
    cdef:
        long packet_count
        Py_ssize_t packet_idx
        list analyzed_packet
        object palisade_version

    # init the class for managing packets for a given instance (do it for
    # each initialization to avoid problems)
    packet_parser.reset()

    # get number of packets to identify
    packet_count = len(packet_list)

    # Loop over packets
    analyzed_packet = [
        identify_packet(packet_idx, packet_list[packet_idx],
                        packet_parser,
                        start_time=start_time,
                        end_time=end_time)
        for packet_idx in range(packet_count)
    ]

    return analyzed_packet
