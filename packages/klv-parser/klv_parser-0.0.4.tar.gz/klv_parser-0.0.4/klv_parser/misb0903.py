#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2017 Matthew Pare (paretech@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from klv_parser.element import UnknownElement
from klv_parser.elementparser import BytesElementParser
from klv_parser.elementparser import DateTimeElementParser
from klv_parser.elementparser import MappedElementParser
from klv_parser.elementparser import StringElementParser
from klv_parser.elementparser import LocationElementParser
from klv_parser.misb0601 import UASLocalMetadataSet
from klv_parser.seriesparser import SeriesParser
from klv_parser.setparser import SetParser


class UnknownElement(UnknownElement):
    pass


@UASLocalMetadataSet.add_parser
class VMTILocalSet(SetParser):
    """MISB ST0903 VMTI Local Set"""
    key = b'\x4A'
    name = 'VMTI_Local_Set'
    TAG = 74
    UDSKey = "06 0E 2B 34 02 0B 01 01 0E 01 03 03 06 00 00 00"
    LDSName = "VMTI Local Set"
    ESDName = ""
    UDSName = "Video Moving Target Indicator Local Set"

    key_length = 1
    parsers = {}

    _unknown_element = UnknownElement


@VMTILocalSet.add_parser
class Checksum(BytesElementParser):
    """Checksum used to detect errors within a UAV Local Set packet.

    Checksum formed as lower 16-bits of summation performed on entire
    LS packet, including 16-byte US key and 1-byte checksum length.

    Initialized from bytes value as BytesValue.
    """
    key = b'\x01'
    TAG = 1
    UDSKey = "-"
    LDSName = "Checksum"
    ESDName = ""
    UDSName = ""


@VMTILocalSet.add_parser
class PrecisionTimeStamp(DateTimeElementParser):
    """Precision Timestamp represented in microseconds.

    Precision Timestamp represented in the number of microseconds elapsed
    since midnight (00:00:00), January 1, 1970 not including leap seconds.

    See MISB ST 0601.11 for additional details.
    """
    key = b'\x02'
    TAG = 2
    UDSKey = "06 0E 2B 34 01 01 01 03 07 02 01 01 01 05 00 00"
    LDSName = "Precision Time Stamp"
    ESDName = ""
    UDSName = "User Defined Time Stamp"


@VMTILocalSet.add_parser
class SystemName(StringElementParser):
    """Mission ID is the descriptive mission identifier.

    Mission ID value field free text with maximum of 127 characters
    describing the event.
    """
    key = b'\x03'
    TAG = 3
    UDSKey = "06 0E 2B 34 01 01 01 01 01 05 05 00 00 00 00 00"
    LDSName = "Mission ID"
    ESDName = "Mission Number"
    UDSName = "Episode Number"
    min_length, max_length = 0, 127


@VMTILocalSet.add_parser
class LSVersionNumber(MappedElementParser):
    key = b'\x04'
    TAG = 4
    UDSKey = "-"
    LDSName = "Platform Tail Number"
    ESDName = "Platform Tail Number"
    UDSName = ""
    min_length, max_length = 0, 127
    _domain = (0, 2 ** 16 - 1)
    _range = (0, 65535)
    _error = None


@VMTILocalSet.add_parser
class TotalTragetsNumber(MappedElementParser):
    key = b'\x05'
    TAG = 5
    _domain = (0, 2 ** 24 - 1)
    _range = (0, 2 ** 24 - 1)
    _error = None

@VMTILocalSet.add_parser
class NumberDetectedTargets(MappedElementParser):
    key = b'\x05'
    TAG = 5
    UDSKey = "-"
    LDSName = "Number of Detected Targets"
    ESDName = "Number of Detected Targets"
    UDSName = ""
    _domain = (0, 2 ** 24 - 1)
    _range = (0, 2 ** 24 - 1)
    _error = None

@VMTILocalSet.add_parser
class NumberReportedTargets(MappedElementParser):
    key = b'\x06'
    TAG = 6
    UDSKey = "-"
    LDSName = "Number of Reported Targets"
    ESDName = "Number of Reported Targets"
    UDSName = ""

    _domain = (0, 2 ** 24 - 1)
    _range = (0, 2 ** 24 - 1)
    _error = None

@VMTILocalSet.add_parser
class FrameNumber(MappedElementParser):
    key = b'\x07'
    TAG = 5
    UDSKey = "-"
    LDSName = "Frame Number"
    ESDName = "Frame Number"
    UDSName = ""

    _domain = (0, 2 ** 24 - 1)
    _range = (0, 2 ** 24 - 1)
    _error = None


@VMTILocalSet.add_parser
class FrameWidth(MappedElementParser):
    key = b'\x08'
    TAG = 8
    UDSKey = "-"
    LDSName = "Frame Width"
    ESDName = "Frame Width"
    UDSName = ""

    _domain = (0, 2 ** 24 - 1)
    _range = (0, 2 ** 24 - 1)
    _error = None


@VMTILocalSet.add_parser
class FrameHeight(MappedElementParser):
    key = b'\x09'
    TAG = 9
    UDSKey = "-"
    LDSName = "Frame Height"
    ESDName = "Frame Height"
    UDSName = ""

    _domain = (0, 2 ** 24 - 1)
    _range = (0, 2 ** 24 - 1)
    _error = None

@VMTILocalSet.add_parser
class SourceSensor(StringElementParser):
    key = b'\x0A'
    TAG = 10
    UDSKey = "-"
    LDSName = "Source Sensor"
    ESDName = "Source Sensor"
    UDSName = ""

    _encoding = 'UTF-8'
    min_length, max_length = 0, 127


@VMTILocalSet.add_parser
class VTargetSeries(SeriesParser):
    key = b'\x65'
    TAG = 101

    name = "VTarget Series"
    parser = None


@VTargetSeries.set_parser
class VTargetPack(SetParser):
    name = "VMTI Target Pack"
    parsers = {}

    def __init__(self, value):
        """All parser needs is the value, no other information"""
        self.key = value[0].to_bytes(1, byteorder='big')
        super().__init__(value[1:])


@VTargetPack.add_parser
class CentroidPixel(MappedElementParser):
    key = b'\x01'
    TAG = 1
    UDSKey = "-"
    LDSName = "Centroid Pixel"
    ESDName = "Centroid Pixel"
    UDSName = ""

    _domain = (0, 2 ** 24 - 1)
    _range = (0, 2 ** 24 - 1)
    _error = None


@VTargetPack.add_parser
class BoundingBoxTopLeftPixel(MappedElementParser):
    key = b'\x02'
    TAG = 2
    UDSKey = "-"
    LDSName = "Bounding Box Top Left Pixel"
    ESDName = "Bounding Box Top Left Pixel"
    UDSName = ""

    _domain = (0, 2 ** 24 - 1)
    _range = (0, 2 ** 24 - 1)
    _error = None


@VTargetPack.add_parser
class BoundingBoxBottomRightPixel(MappedElementParser):
    key = b'\x03'
    TAG = 3
    UDSKey = "-"
    LDSName = "Bounding Box Bottom Right Pixel"
    ESDName = "Bounding Box Bottom Right Pixel"
    UDSName = ""

    _domain = (0, 2 ** 24 - 1)
    _range = (0, 2 ** 24 - 1)
    _error = None


@VTargetPack.add_parser
class DetectionCount(MappedElementParser):
    key = b'\x06'
    TAG = 6
    UDSKey = "-"
    LDSName = "Detection Count"
    ESDName = "Detection Count"
    UDSName = ""

    _domain = (0, 2 ** 24 - 1)
    _range = (0, 2 ** 24 - 1)
    _error = None


@VTargetPack.add_parser
class TargetIntensity(MappedElementParser):
    key = b'\x09'
    TAG = 9
    UDSKey = "-"
    LDSName = "Target Intensity"
    ESDName = "Target Intensity"
    UDSName = ""

    _domain = (0, 2 ** 24 - 1)
    _range = (0, 2 ** 24 - 1)
    _error = None


@VTargetPack.add_parser
class TargetLocation(LocationElementParser):
    key = b'\x11'
    TAG = 17
    UDSKey = "-"
    LDSName = "Target Location"
    ESDName = "Target Location"
    UDSName = ""

