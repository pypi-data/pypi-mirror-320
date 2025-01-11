
from roc.rpl.constants import INVALID_PACKET_DATA, VALID_PACKET, INVALID_PACKET_HEADER
from roc.rpl.exceptions import PacketParsingError
from roc.rpl.packet_structure.data import Data

from roc.rpl.packet_parser import PacketParser
from roc.rpl.packet_parser.parser.identify_packets import identify_packets

__all__ = ["parse_packets"]

cpdef dict parse_packet(int packet_idx, dict packet_data, object packet_parser):
    cdef:
        object name
        object srdb_id
        object palisade_id
        object raw_data
        object utc_time
        object byte_data
        object packet
        object result
        object message
        object status
        object comment

    # now extract parameter values for each identified packet

    # name of the packet
    name = packet_data.get('srdb_id')
    palisade_id = packet_data.get('palisade_id')
    utc_time = packet_data.get('utc_time')
    raw_data = packet_data.get('binary')
    status = packet_data.get('status')
    comment = packet_data.get('comment')
    if comment is None:
        packet_data['comment'] = ''

    # If not valid packet skip data extraction
    if (name is None or
            palisade_id is None or
            raw_data is None or
            status != VALID_PACKET):
        packet_data['comment'] += f'Input packet cannot be parsed ({packet_data}). '
        return packet_data

    # logger.debug(f'Extracting data for packet {palisade_id} {{{name}}} at
    # {utc_time}...')

    # convert the hexa raw data in bytes
    byte_data = PacketParser.hex_to_bytes(raw_data)

    # only put in the database events with data inside
    if byte_data is None:
        packet_data['comment'] += "Packet (#{0} {1}, {2}, {3}) doesn't have raw data, skip data extraction! ".format(
            packet_idx, palisade_id, name, utc_time)
        return packet_data

    # check that the packet is a correct packet name
    if palisade_id not in packet_parser.idb.packets:
        packet_data['comment'] += ("Packet (#{0}, {1}, {2} {3}) has not been "
                                   "recognized in the current IDB, skip data extraction! "
                                   ).format(packet_idx, palisade_id, name, utc_time)
        packet_data['status'] = INVALID_PACKET_HEADER
        return packet_data

    # get the packet and extract the data
    packet = packet_parser.packet(palisade_id)
    try:
        result = packet.extract_data(
            Data(bytes(byte_data), len(byte_data)),
            packet_data=packet_data,
        )
        packet_data['data'] = result
    # cases for packet parsing
    except PacketParsingError as e:
        packet_data["status"] = INVALID_PACKET_DATA
        packet_data['comment'] += e.message + '. '
        packet.is_valid = False
        packet_parser.extract_error(e.message)
    # system exit
    except SystemExit:
        raise
    # keyboard interrupt
    except KeyboardInterrupt:
        raise
    # all other cases (compression, etc)
    except Exception as e:
        packet_data["status"] = INVALID_PACKET_DATA
        message = (f"Issue with packet "
                   f"(#{packet_idx} {palisade_id} {{{name}}} "
                   f"at {utc_time}): {e}. ")
        packet_data["comment"] += message
        packet.is_valid = False
        packet_parser.extract_error(message)

    return packet_data

cpdef list parse_packets(object packet_parser, list packet_list,
                         start_time=None,
                         end_time=None,
                         no_identification=False):
    """
    Parse input RPW TM/TC packets and store their information
    in the packet structure.

    :param packet_parser: instance of packet_parser object
    :param packet_list: List of raw binary data of the packets
    :return: Store results in the PacketParser object
    """
    cdef:
        list identified_packet_list
        list parsed_packet_list
        Py_ssize_t packet_idx
        long packet_count
        dict current_packet

    # Extract packet header info and names
    if not no_identification:
        identified_packet_list = identify_packets(
            packet_parser, packet_list,
            start_time=start_time,
            end_time=end_time)
    else:
        identified_packet_list = packet_list

    # Add packets to the Packet class instance
    added_list = [packet_parser.add_packet(current_packet)
                  for current_packet in identified_packet_list]

    # If only not valid packet, exit method
    packet_count = len(identified_packet_list)
    if packet_count == 0:
        return identified_packet_list

    # initialize the packet structure
    packet_parser.packet.initialize_all()

    parsed_packet_list = [parse_packet(packet_idx,
                                       identified_packet_list[packet_idx],
                                       packet_parser)
                          for packet_idx in range(packet_count)]

    return parsed_packet_list
