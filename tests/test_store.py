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
"""ParameterCodec tests"""

import unittest
import mock

from ros3ddevcontroller.param.store import ParametersStore, ParameterLoader
from ros3ddevcontroller.param.parameter import Parameter, ReadOnlyParameter, Evaluator

class StoreLoadingTestCase(unittest.TestCase):
    def setUp(self):
        ParameterLoader.load()

    def tearDown(self):
        ParametersStore.clear_parameters()


class StoreLoadClearTestCase(unittest.TestCase):
    PARAMETERS = [
        Parameter('foo', 1, int),
        Parameter('bar', 2, float)
    ]

    def setUp(self):
        ParametersStore.clear_parameters()

    def test_load_clear(self):
        self.assertEqual(ParametersStore.PARAMETERS, {})

        ParametersStore.load_parameters(self.PARAMETERS)
        self.assertNotEqual(ParametersStore.PARAMETERS, {})
        self.assertIn('foo', ParametersStore.PARAMETERS)
        self.assertIn('bar', ParametersStore.PARAMETERS)

        ParametersStore.clear_parameters()
        self.assertEqual(ParametersStore.PARAMETERS, {})


class GetSetStoreTestCase(StoreLoadingTestCase):

    def test_get_existing(self):
        from ros3ddevcontroller.param.sysparams import SYSTEM_PARAMETERS

        for param in SYSTEM_PARAMETERS:
            name = param.name
            value = param.value

            try:
                from_store = ParametersStore.get(param.name)
            except KeyError:
                self.fail('Expecting key in the set')

            self.assertEqual(name, from_store.name)
            self.assertEqual(value, from_store.value)
            self.assertEqual(param.value_type, from_store.value_type)

    def test_get_missing(self):

        self.assertRaises(KeyError,
                          ParametersStore.get, 'non-existent-param')
        self.assertRaises(KeyError,
                          ParametersStore.get, '')
        self.assertRaises(KeyError,
                          ParametersStore.get, None)


    def test_set(self):
        # test that a parameter can be set
        test_param = 'focus_distance_m'
        test_val = 10.0

        self.assertTrue(ParametersStore.set(test_param, test_val))
        focus_set = ParametersStore.get(test_param)

        self.assertEqual(focus_set.value, test_val)

    def test_set_convert(self):
        # test that parameter can be set, and the value is
        # automatically converted to proper type
        test_param = 'focus_distance_m'
        test_val = 10
        expecting_type = float

        # test value is an int
        self.assertIsInstance(test_val, int)

        # first read it
        param = ParametersStore.get(test_param)
        self.assertEqual(param.value_type, expecting_type)
        self.assertIsInstance(param.value, expecting_type)

        # set
        ParametersStore.set(test_param, test_val)
        as_set = ParametersStore.get(test_param)
        # the type should have been converted according to parameter
        # description
        self.assertIsInstance(as_set.value, expecting_type)
        self.assertEqual(as_set.value, expecting_type(test_val))

    def test_set_validate_failed(self):
        # test setting of parameter where the automatic conversion fails
        # set

        test_param = 'focus_distance_m'
        test_val = 'foo'
        expecting_type = float

        # this will raise ValueError obviously
        self.assertRaises(ValueError, expecting_type, test_val)

        focus_before = ParametersStore.get(test_param)

        # same as this one
        self.assertRaises(ValueError, ParametersStore.set,
                          test_param, test_val)
        self.assertRaises(ValueError, ParametersStore.validate,
                          test_param, test_val)
        self.assertRaises(KeyError, ParametersStore.validate,
                          test_param + '=foo', test_val)
        self.assertRaises(KeyError, ParametersStore.set,
                          test_param + '=foo', test_val)

        # try to fetch the parameter again to compare that its value
        # is unchaged
        focus_after = ParametersStore.get(test_param)

        self.assertIs(focus_before, focus_after)

    def test_validate_pdesc_failed(self):
        # test setting of parameter where the automatic conversion fails
        # set

        test_param = 'focus_distance_m'
        test_val = 'foo'
        expecting_type = float

        param = Parameter(test_param, test_val, expecting_type)

        # we know the parameter, this should not raise anything
        ParametersStore.get(test_param)

        # same as this one
        self.assertRaises(ValueError, ParametersStore.set,
                          param.name, param.value)
        self.assertRaises(ValueError, ParametersStore.validate,
                          param.name, param.value)
        self.assertRaises(ValueError, ParametersStore.validate_desc,
                          param)

        # change value to correct one
        param.value = 10
        try:
            ParametersStore.validate_desc(param)
        except Exception as err:
            self.fail("Exception raised")

    def test_validate_not_pdesc_failed(self):
        param = 1

        # param is not Parameter(), this should fail
        self.assertRaises(AssertionError, ParametersStore.validate_desc,
                          param)


class ListenerTestCase(StoreLoadingTestCase):
    def test_called(self):
        # verify that a callback was called only once for each set
        tmock = mock.Mock()

        test_param = 'focus_distance_m'
        test_value = 10.0

        # register mock callback a couple of times, only one
        # registration is used
        ParametersStore.change_listeners.add(tmock)
        ParametersStore.change_listeners.add(tmock)
        ParametersStore.change_listeners.add(tmock)

        # set a parameter
        ParametersStore.set(test_param, test_value)

        # has to be called
        self.assertTrue(tmock.called)
        # called only once
        self.assertEquals(tmock.call_count, 1)
        self.assertEquals(len(tmock.call_args), 2)
        # grab the first list parameter
        pdesc = tmock.call_args[0][0]
        self.assertIsInstance(pdesc, Parameter)
        self.assertEquals(pdesc.name, test_param)
        self.assertEquals(pdesc.value, test_value)

        # set once again
        ParametersStore.set(test_param, test_value + 1)
        self.assertEquals(tmock.call_count, 2)
        # grab the first list parameter
        pdesc = tmock.call_args[0][0]
        self.assertEquals(pdesc.value, test_value + 1)

        # remove callback
        ParametersStore.change_listeners.remove(tmock)
        # and again, should not fail
        ParametersStore.change_listeners.remove(tmock)
        # now something different
        ParametersStore.change_listeners.remove(None)


class CameraServoTestCase(StoreLoadingTestCase):

    def setUp(self):
        super(CameraServoTestCase, self).setUp()
        from ros3ddevcontroller.param.sysparams import SERVO_PARAMETERS, CAMERA_PARAMETERS
        self.servo_parameters = SERVO_PARAMETERS
        self.camera_parameters = CAMERA_PARAMETERS

    def test_servo(self):

        for p in self.servo_parameters:
            self.assertTrue(ParametersStore.is_servo_parameter(p))
        for p in self.camera_parameters:
            self.assertFalse(ParametersStore.is_servo_parameter(p))

    def test_camera(self):

        for p in self.camera_parameters:
            self.assertTrue(ParametersStore.is_camera_parameter(p))
        for p in self.servo_parameters:
            self.assertFalse(ParametersStore.is_camera_parameter(p))


class ReadOnlyParameterTestCase(unittest.TestCase):

    def setUp(self):

        ParametersStore.load_parameters([
            ReadOnlyParameter('foo-readonly', 'bar', str),
            Parameter('foo-writable', 'bar', str)
        ])

    def test_parameter_readonly(self):

        self.assertTrue(ParametersStore.is_read_only('foo-readonly'))
        self.assertFalse(ParametersStore.is_read_only('foo-writable'))


class ParameterGetValueTestCase(unittest.TestCase):
    PARAMETERS = [
            Parameter('foo', 1, int),
            Parameter('bar', 'baz', str)
    ]

    def setUp(self):
        ParametersStore.load_parameters(self.PARAMETERS)

    def tearDown(self):
        ParametersStore.clear_parameters()

    def find_key_param(self, name):
        found = [pdesc for pdesc in self.PARAMETERS
                 if pdesc.name == name]
        return found[0]

    def test_get_value(self):

        for param_in in self.PARAMETERS:
            pdesc = ParametersStore.get(param_in.name)
            self.assertEqual(param_in.name, pdesc.name)
            self.assertEqual(param_in.value, pdesc.value)
            self.assertEqual(param_in.value_type, pdesc.value_type)

            pvalue = ParametersStore.get_value(param_in.name)
            self.assertEqual(pvalue, param_in.value)
            self.assertEqual(type(pvalue), param_in.value_type)


class ParameterEvaluationTestCase(unittest.TestCase):
    class BarEvaluator(Evaluator):
        REQUIRES = [
            'foo'
        ]

        def __call__(self, foo=None):
            return foo + 1

    class BazEvaluator(Evaluator):
        REQUIRES = [
            'foo',
            'bar'
        ]

        def __call__(self, foo=None, bar=None):
            return foo * bar + 1

    class CafeEvaluator(Evaluator):
        REQUIRES = [
            'baz',
            'bar'
        ]

        def __call__(self, baz=None, bar=None):
            return baz ** 2 + bar

    PARAMETERS = [
        Parameter('foo', 1, int),
        Parameter('cafe', 0, int, evaluator=CafeEvaluator),
        Parameter('bar', 0, int, evaluator=BarEvaluator),
        Parameter('baz', 0, int, evaluator=BazEvaluator),
    ]

    def setUp(self):
        ParametersStore.load_parameters(self.PARAMETERS)

    def tearDown(self):
        ParametersStore.clear_parameters()

    def test_set_value(self):

        self.assertNotEqual(ParametersStore.DEPENDENCIES, {})
        pdesc_bar = ParametersStore.get('bar')

        ParametersStore.set('foo', 3)
        bar_val = ParametersStore.get_value('bar')
        # bar = foo + 1
        self.assertEqual(bar_val, 4)
        baz_val = ParametersStore.get_value('baz')
        # baz = foo * bar + 1
        self.assertEqual(baz_val, 13)
        # cafe = baz ** 2 + bar
        cafe_val = ParametersStore.get_value('cafe')
        self.assertEqual(cafe_val, 173)
