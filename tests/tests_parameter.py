#
# Copyright (c) 2015 Open-RnD Sp. z o.o.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""System parameters wrappers"""

from __future__ import absolute_import

import unittest
import mock

from ros3ddevcontroller.param.parameter import Parameter, ReadOnlyParameter, ParameterStatus, Infinity

class ParameterTestCase(unittest.TestCase):
    def test_new_no_status(self):
        par = Parameter('foo', 'bar', str)

        self.assertEqual(par.name, 'foo')
        self.assertEqual(par.value, 'bar')
        self.assertIsInstance(par.value, str)
        self.assertEqual(par.value_type, str)

        self.assertTrue(hasattr(par, 'status'))
        status = par.status
        self.assertIsInstance(status, ParameterStatus)
        self.assertEqual(status.read, True)
        self.assertEqual(status.write, True)
        self.assertEqual(status.status, ParameterStatus.SOFTWARE)

    def test_new_status(self):
        st = ParameterStatus()

        par = Parameter('foo', 1, int, status=st, min_val=0, max_val=10)

        self.assertEqual(par.name, 'foo')
        self.assertEqual(par.value, 1)
        self.assertIsInstance(par.value, int)
        self.assertEqual(par.value_type, int)
        self.assertEqual(par.min_value, 0)
        self.assertEqual(par.max_value, 10)
        self.assertIs(par.status, st)

    def test_new_bad_status(self):
        self.assertRaises(AssertionError, Parameter,
                          'foo', 'bar', str, status=1)

    def test_read_only(self):
        par = Parameter('foo', 'bar', str)

        self.assertFalse(par.is_read_only())

        par = ReadOnlyParameter('foo', 'bar', str)
        self.assertTrue(par.is_read_only())

    def test_set_status(self):

        status = ParameterStatus(status_type=ParameterStatus.SOFTWARE)

        status.set_status(ParameterStatus.HARDWARE)
        self.assertEqual(status.status, ParameterStatus.HARDWARE)


class FloatInfinityTestCase(unittest.TestCase):
    def test_convert_to(self):
        self.assertEqual(Infinity.convert_to(1e100), Infinity.PLUS)
        self.assertEqual(Infinity.convert_to(-1e100), Infinity.MINUS)
        self.assertEqual(Infinity.convert_to(10e20), 10e20)
        self.assertEqual(Infinity.convert_to(-10e20), -10e20)
        self.assertEqual(Infinity.convert_to(float('inf')), Infinity.PLUS)
        self.assertEqual(Infinity.convert_to(float('-inf')), Infinity.MINUS)
        self.assertEqual(Infinity.convert_to(0.3333), 0.3333)
        self.assertEqual(Infinity.convert_to(128), 128)

    def test_convert_from(self):
        self.assertEqual(Infinity.convert_from(Infinity.PLUS), float('inf'))
        self.assertEqual(Infinity.convert_from(Infinity.MINUS), float('-inf'))
        self.assertEqual(Infinity.convert_from(10e20), 10e20)
        self.assertEqual(Infinity.convert_from(-10e20), -10e20)
        self.assertEqual(Infinity.convert_from(float('inf')), float('inf'))
        self.assertEqual(Infinity.convert_from(float('-inf')), float('-inf'))
        self.assertEqual(Infinity.convert_from(0.3333), 0.3333)
        self.assertEqual(Infinity.convert_from(128), 128)
