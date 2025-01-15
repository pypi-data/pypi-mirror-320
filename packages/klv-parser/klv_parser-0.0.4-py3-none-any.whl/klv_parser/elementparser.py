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

from abc import ABCMeta
from abc import abstractmethod
from klv_parser.element import Element
from klv_parser.common import bytes_to_datetime, imapb_to_float, float_to_imapb
from klv_parser.common import bytes_to_int
from klv_parser.common import bytes_to_float
from klv_parser.common import bytes_to_hexstr
from klv_parser.common import bytes_to_str
from klv_parser.common import datetime_to_bytes
from klv_parser.common import float_to_bytes
from klv_parser.common import str_to_bytes
from klv_parser.common import ieee754_bytes_to_fp
                                           


class ElementParser(Element, metaclass=ABCMeta):
    """Construct a Element Parser base class.

    Element Parsers are used to enforce the convention that all Element Parsers
    already know the key of the element they are constructing.

    Element Parser is a helper class that simplifies known element definition
    and makes a layer of abstraction for functionality that all known elements
    can share. The parsing interfaces are cleaner and require less coding as
    their definitions (subclasses of Element Parser) do not need to call init
    on super with class key and instance value.
    """

    def __init__(self, value):
        super().__init__(self.key, value)

    @property
    @classmethod
    @abstractmethod
    def key(cls):
        pass

    def __repr__(self):
        """Return as-code string used to re-create the object."""
        return '{}({})'.format(self.name, bytes(self.value))


class BaseValue(metaclass=ABCMeta):
    """Abstract base class (superclass) used to insure internal interfaces are maintained."""
    @abstractmethod
    def __bytes__(self):
        """Required by element.Element"""
        pass

    @abstractmethod
    def __str__(self):
        """Required by element.Element"""
        pass


class BytesElementParser(ElementParser, metaclass=ABCMeta):
    def __init__(self, value):
        super().__init__(BytesValue(value))


class BytesValue(BaseValue):
    def __init__(self, value):
        self.value = value

    def __bytes__(self):
        return bytes(self.value)

    def __str__(self):
        return bytes_to_hexstr(self.value, start='0x', sep='')


class DateTimeElementParser(ElementParser, metaclass=ABCMeta):
    def __init__(self, value):
        super().__init__(DateTimeValue(value))


class DateTimeValue(BaseValue):
    def __init__(self, value):
        self.value = bytes_to_datetime(value)

    def __bytes__(self):
        return datetime_to_bytes(self.value)

    def __str__(self):
        return self.value.isoformat(sep=' ')


class StringElementParser(ElementParser, metaclass=ABCMeta):
    def __init__(self, value):
        super().__init__(StringValue(value))


class StringValue(BaseValue):
    def __init__(self, value):
        try:
            self.value = bytes_to_str(value)
        except TypeError:
            self.value = value

    def __bytes__(self):
        return str_to_bytes(self.value)

    def __str__(self):
        if self.value is not None:
            return str(self.value)
        return ""


class MappedElementParser(ElementParser, metaclass=ABCMeta):
    def __init__(self, value):
        super().__init__(MappedValue(value, self._domain, self._range, self._error))

    @property
    @classmethod
    @abstractmethod
    def _domain(cls):
        pass

    @property
    @classmethod
    @abstractmethod
    def _range(cls):
        pass

    @property
    @classmethod
    @abstractmethod
    def _error(cls):
        pass

class MappedValue(BaseValue):
    def __init__(self, value, _domain, _range, _error):
        self._domain = _domain
        self._range = _range
        self._error = _error

        try:
            if min(self._domain) == min(self._range) and max(self._domain) == max(self._range):
                self.value = bytes_to_int(value, signed=(min(_domain) < 0))
            else:
                self.value = bytes_to_float(value, self._domain, self._range, self._error)
        except TypeError:
            self.value = value

    def __bytes__(self):
        return float_to_bytes(self.value, self._domain, self._range, self._error)

    def __str__(self):
        if self.value is not None:
            return format(self.value)
        return ""

    def __float__(self):
        return self.value

class LocationElementParser(ElementParser, metaclass=ABCMeta):
    def __init__(self, value):
        super().__init__(LocationValue(value))

class IMAPBElementParser(ElementParser, metaclass=ABCMeta):
    def __init__(self, value):
        super().__init__(IMAPBValue(value, self._range))

    @property
    @classmethod
    @abstractmethod
    def _range(cls):
        pass

class IMAPBValue(BaseValue):
    def __init__(self, value, _range):
        self._range = _range
        self._length = len(value)
        self.value = imapb_to_float(value, self._range)

    def __bytes__(self):
        return float_to_imapb(self.value, self._length, self._range)

    def __str__(self):
        return str(self.value)

class LocationValue(BaseValue):
    def __init__(self, value):
        self.value = (imapb_to_float(value[0:4], (-90, 90)),
                    imapb_to_float(value[4:8], (-180, 180)),
                    imapb_to_float(value[8:10], (-900, 19000)))

    def __bytes__(self):
        lat, long, alt = self.value
        return (float_to_imapb(lat, 4, (-90, 90)) +
                float_to_imapb(long, 4, (-180, 180)) +
                float_to_imapb(alt, 2, (-900, 19000)))

    def __str__(self):
        return str(self.value)


class IEEE754ElementParser(ElementParser, metaclass=ABCMeta):
    def __init__(self, value):
        super().__init__(IEEE754Value(value))


class IEEE754Value(BaseValue):
    def __init__(self, value):
        try:
            self.value = ieee754_bytes_to_fp(value)
        except TypeError:
            self.value = value

    def __bytes__(self):
        #TODO
        return ieee754_double_to_bytes(self.value)

    def __str__(self):
        return bytes_to_hexstr(self.value, start='0x', sep='')



