#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""System parameters wrappers"""

from __future__ import absolute_import

import logging

_log = logging.getLogger(__name__)


class ParameterStatus(object):
    """Paramter status wrapper"""
    HARDWARE = 'hardware'
    SOFTWARE = 'software'

    def __init__(self, read=True, write=True,
                 status_type=HARDWARE):
        self.read = read
        self.write = write
        self.status = status_type

    def as_dict(self):
        """Return a JSON serializable dict"""
        return {
            'read': bool(self.read),
            'write': bool(self.write),
            'status': str(self.status)
        }


class Parameter(object):
    """System parameter wrapper"""

    def __init__(self, name, value, value_type,
                 status=None, min_val=None, max_val=None):
        """Initialize a parameter

        :param str name: parameter name
        :param value: parameter value, corresponding to value_type
        :param typr value_type: type of parameter value
        :param ParameterStatus status: status info, if None, defaults to a hardware paramter
        :param min_val: minimum value
        :param max_val: maximum value
        """
        self.name = name
        self.value = value
        self.value_type = value_type

        if not status:
            self.status = ParameterStatus(read=True, write=True,
                                          status_type=ParameterStatus.HARDWARE)
        else:
            assert isinstance(status, ParameterStatus)
            self.status = status

        self.min_value = min_val
        self.max_value = max_val

    def as_dict(self):
        """Return a JSON serializable dict describing the parameter"""
        ad = {
            "value": self.value,
            "valueType": self.value_type.__name__,
            "status:": self.status.as_dict(),
        }

        if self.min_value:
            ad["minValue"] = self.min_value
        if self.max_value:
            ad["maxValue"] = self.max_value

        return ad


