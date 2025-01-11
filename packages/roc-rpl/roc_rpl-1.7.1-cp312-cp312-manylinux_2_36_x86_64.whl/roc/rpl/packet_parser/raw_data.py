#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from operator import itemgetter
from typing import Union, List
from datetime import datetime

import numpy as np

from poppy.core.logger import logger

from roc.rpl.packet_parser import PacketParser
from roc.rpl.constants import (
    INVALID_PACKET_HEADER,
    RAW_DATA_DEF,
    TM_RAW_DATA_DEF,
    TC_RAW_DATA_DEF,
)

__all__ = ["RawData"]


class RawData:
    def __init__(
        self,
        packet_list: List[dict],
        packet_parser: PacketParser,
    ):
        self.packet_list = packet_list
        self.idb_version = ""
        self._idb_source = ""
        self._packet_parser: Union[PacketParser, None] = None
        self._invalid_packet_list: list[dict] = []

        self.packet_parser = packet_parser

    @property
    def packet_list(self) -> list[dict]:
        """
        Get list of packets.

        :return: list of packets
        """
        return self._packet_list

    @packet_list.setter
    def packet_list(self, value: list[dict]):
        """
        Set list of packets.

        :param value: new list of packets
        :type value: list
        :return: None
        """
        self._packet_list = value

    @property
    def invalid_packet_list(self) -> List[dict]:
        """
        Get list of invalid packets

        :return: list of invalid packets
        :rtype: list
        """
        return self._invalid_packet_list

    @invalid_packet_list.setter
    def invalid_packet_list(self, value: List[dict]):
        """
        Set list of invalid packets

        :param value: new list of invalid packets
        :return: None
        """
        self._invalid_packet_list = value

    @property
    def packet_parser(self) -> Union[PacketParser, None]:
        return self._packet_parser

    @packet_parser.setter
    def packet_parser(self, packet_parser_instance: PacketParser):
        """
        Set PacketParser instance of RawData
        (Only possible if a PacketParser instance is not already defined with different
        Packet class instance)

        :param packet_parser_instance: PacketParser class instance
        :type packet_parser_instance: PacketParser
        :return: None
        """

        if (
            self._packet_parser
            and hasattr(self._packet_parser, "packet")
            and self._packet_parser.packet != packet_parser_instance.packet
        ):
            logger.warning(
                "RawData.packet_parser already defined: "
                "please delete the current RawData instance first!"
            )
        else:
            self._packet_parser = packet_parser_instance

            # Ensure that values of idb_version and idb_source attributes always
            # match with the packet_parser ones
            self.idb_version = self._packet_parser.idb_version
            self.idb_source = self._packet_parser.idb_source

    @property
    def binary(self) -> List[str]:
        """
        Get list of binary data from the packet list.

        :return: list of binary data
        :rtype: list
        """
        return [pkt["binary"] for pkt in self._packet_list]

    @property
    def packet_scet_time(self) -> list:
        """
        Get packet creation SCET time from packet list.

        :return: list of packet creation SCET time
        :rtype: list
        """
        return [pkt["scet"] for pkt in self._packet_list]

    @property
    def packet_utc_time(self) -> List[datetime]:
        """
        Get packet creation UTC time from packet list.

        :return: list of packet creation UTC time
        :rtype: list
        """
        return [pkt["utc_time"] for pkt in self._packet_list]

    @property
    def packet_srdb_id(self) -> List[str]:
        """
        Get packet names (SRBD ID).

        :return: list of packet SRBD ID name
        :rtype: list
        """
        return self.packet_name

    @property
    def packet_name(self) -> List[str]:
        """
        Get list of packet name (SRDB ID).

        :return: list of packet name (SRDB ID)
        :rtype: list
        """
        return [pkt["srdb_id"] for pkt in self._packet_list]

    @property
    def packet_palisade_id(self) -> List[str]:
        """
        get list of packet palisade ID.

        :return: packet palisade IDs
        :rtype: list
        """
        return [pkt["palisade_id"] for pkt in self._packet_list]

    @property
    def packet_unique_id(self) -> List[str]:
        """
        Get list of packet unique IDs.

        :return: packet unique IDs
        :rtype: list
        """
        return [pkt["unique_id"] for pkt in self._packet_list]

    @property
    def packet_dates(self) -> List[datetime]:
        """
        Get list of packet UTC time dates

        :return: packet UTC time dates
        :rtype: list
        """
        return [pkt["utc_time"].date() for pkt in self._packet_list]

    def add_packet(self, packet_data: dict) -> bool:
        """
        Add a packet dictionary to the packet_list

        :param packet_data:
        :return: return True if the packet is added, False otherwise
        """
        if packet_data not in self._packet_list:
            self._packet_list.append(packet_data)
            return True
        else:
            return False

    @staticmethod
    def filter(
        packet_list,
        by_srdbid_and_utc_time=None,
        by_palisadeid_and_utc_time=None,
        by_utc_start=None,
        by_utc_end=None,
        by_srdbid=None,
        by_palisadeid=None,
        by_utc_time=None,
        by_binary=None,
        by_date=None,
        by_type=None,
    ):
        """
        Filter input packet list by attributes (name,
        descr, time, binary).

        :param packet_list: list of packets to filter
        :param by_srdbid_and_utc_time: tuple containing the SRDB_ID and UTC time of the packets to return
        :param by_palisadeid_and_utc_time: tuple containing the PALISADE_ID and UTC time of the packets to return
        :param by_name: SRDB_ID of the packets to return
        :param by_utc_start: Return packets for which UTC time is greater or equal than by_utc_start
        :param by_utc_end: Return packets for which UTC time is lesser than by_utc_end
        :param by_descr: PALISADE ID of the packets to return
        :param by_utc_time: UTC time of the packets (datetime object) to return
        :param by_binary: raw binary data of the packets (hexa string) to return
        :param by_date: date (datetime.date object) of packets to return
        :param by_type: type (TM or TC) of packets to return
        :return: return list of packets filtered
        """

        filtered_packet_list = []

        # Loop over the packets to look for the requested
        for current_packet in packet_list:
            if not current_packet:
                continue

            if (
                by_srdbid_and_utc_time
                and by_srdbid_and_utc_time
                == (current_packet["srdb_id"], current_packet["utc_time"])
                and current_packet not in filtered_packet_list
            ):
                filtered_packet_list.append(current_packet)

            if (
                by_palisadeid_and_utc_time
                and by_palisadeid_and_utc_time
                == (current_packet["palisade_id"], current_packet["utc_time"])
                and current_packet not in filtered_packet_list
            ):
                filtered_packet_list.append(current_packet)

            if (
                by_srdbid
                and by_srdbid == current_packet["srdb_id"]
                and current_packet not in filtered_packet_list
            ):
                filtered_packet_list.append(current_packet)

            if (
                by_palisadeid
                and by_palisadeid == current_packet["palisade_id"]
                and current_packet not in filtered_packet_list
            ):
                filtered_packet_list.append(current_packet)

            if (
                by_utc_start
                and by_utc_start <= current_packet["utc_time"]
                and current_packet not in filtered_packet_list
            ):
                filtered_packet_list.append(current_packet)

            if (
                by_utc_end
                and by_utc_end > current_packet["utc_time"]
                and current_packet not in filtered_packet_list
            ):
                filtered_packet_list.append(current_packet)

            if (
                by_utc_time
                and by_utc_time == current_packet["utc_time"]
                and current_packet not in filtered_packet_list
            ):
                filtered_packet_list.append(current_packet)

            if (
                by_binary
                and by_binary == current_packet["binary"]
                and current_packet not in filtered_packet_list
            ):
                filtered_packet_list.append(current_packet)

            if (
                by_date
                and by_date == current_packet["utc_time"].date()
                and current_packet not in filtered_packet_list
            ):
                filtered_packet_list.append(current_packet)

            if (
                by_type
                and by_type == current_packet["type"]
                and current_packet not in filtered_packet_list
            ):
                filtered_packet_list.append(current_packet)

        return filtered_packet_list

    @staticmethod
    def check_packet_name(packet_list, expected_names):
        """
        Check input packets against expected list of expected packet names (SRDB_ID)

        :param packet_list: list of input packets to check
        :param expected_names: list of expected packet names
        :return: True if the checking has passed, else False (if wrong input, then return None)
        """

        npkt = len(packet_list)
        nexp = len(expected_names)
        if nexp != npkt:
            logger.error(
                f'Input "expected_names" '
                f"must have {npkt} element(s), but {nexp} found!"
            )
            return None

        for i, current_packet in enumerate(packet_list):
            expected_name = expected_names[i]

            packet_name = current_packet["srdb_id"]

            try:
                logger.debug(
                    "Comparing reconstructed names with given one: "
                    f"{packet_name} ?= {expected_name}"
                )
                assert packet_name == expected_name
            except Exception as e:
                # If not the same name, then set the status of the packet to invalid
                packet_list[i]["status"] = INVALID_PACKET_HEADER
                logger.warning(
                    f"Packet #{i} has a wrong name: "
                    f'"{packet_name}" found but "{expected_name}" expected '
                )
                logger.debug(e)
                continue

        return packet_list

    @staticmethod
    def by_increasing_time(packet_list, decreasing=False, by_scet=False):
        """
        Sort input packet list by increasing packet time.

        :param deacreasing: if True, then sort by decreasing scet
        :param by_scet: if True, use scet time instead of utc_time
        :return:
        """

        if by_scet:
            packet_time = [pkt["scet"] for pkt in packet_list]
        else:
            packet_time = [pkt["utc_time"] for pkt in packet_list]

        if packet_time:
            index_list = sorted(range(len(packet_time)), key=lambda k: packet_time[k])
            if decreasing:
                index_list = reversed(index_list)

            return list(itemgetter(*index_list)(packet_list))
        else:
            return None

    def is_packet(self, packet_id):
        """
        Check if a given packet exists in the current PacketParser object

        :param packet_id: ID of the packet (can be SRBD ID or PALISADE ID)
        :return: True if packet has been found, False otherwise
        """

        # Check if input packet id is a PALISADE or SRBD ID
        if packet_id.startswith("TM_") or packet_id.startswith("TC_"):
            packet_ids = self.packet_palisade_id
        elif packet_id.startswith("YIW") or packet_id.startswith("ZIW"):
            packet_ids = self.packet_name
        else:
            logger.error(f"Unknown input packet id: {packet_id}")
            return False

        return packet_id in packet_ids

    @staticmethod
    def sort_by_utc_time(packet_list, packet_utc_time=None):
        """
        Return input packet_list sorted by increasing utc time.


        :return: sorted packet_list
        """

        if packet_utc_time is None:
            packet_utc_time = [pkt["utc_time"] for pkt in packet_list]

        # get indices of sorted utc_time list
        sorted_indices = np.argsort(packet_utc_time)

        return list(np.array(packet_list)[sorted_indices])

    @staticmethod
    def is_identified(packet_data):
        """
        Check if a packet has been already identified.

        :param packet_data: packet data as a dictionary
        :return: True, if the packet has been already identified, False otherwise
        """

        # Check if generic parameters are present
        for key in RAW_DATA_DEF.keys():
            # Get parameter value from packet_data dictionary
            # If not found, then set to NoneType value by default
            if not packet_data.get(key, None):
                # If at least one of the parameter is not defined (i.e., has NoneType value)
                # then return False
                return False

        # Additional checks
        # srdb id format should be as expected
        if not packet_data["srdb_id"].startswith("YIW") and not packet_data[
            "srdb_id"
        ].startswith("ZIW"):
            return False

        # status should be 'VALID'
        if packet_data["status"] != "VALID":
            return False

        # Check if generic parameters are present
        if packet_data["type"] == "TM":
            raw_data_def_dict = TM_RAW_DATA_DEF
        elif packet_data["type"] == "TC":
            raw_data_def_dict = TC_RAW_DATA_DEF
        else:
            # if not expected packet type, then return false
            return False

        # Loop on raw_data_def_dict default keywords
        for key in raw_data_def_dict.keys():
            # Get parameter value from packet_data dictionary
            # If not found, then set the NoneType value by default
            if not packet_data.get(key, None):
                # If at least one of the parameter is not defined (i.e., has NoneType value)
                # then return False
                return False

        return True

    @staticmethod
    def init_packet_data(packet_data):
        """
        Initialize content of packet_data dictionary

        :param packet_data: dictionary with packet data
        :return: packet_data with default values
        """

        for key, val in RAW_DATA_DEF.items():
            # if keyword (key) not found in packet_data, then set default value (val)
            packet_data[key] = packet_data.get(key, val)

        return packet_data
