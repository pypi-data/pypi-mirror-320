# type: ignore
import datetime
from unittest import TestCase

from singlestoredb import converters
from singlestoredb.mysql.converters import escape_string


__all__ = ['TestConverter']


class TestConverter(TestCase):

    def test_escape_string(self):
        self.assertEqual(escape_string('foo\nbar'), 'foo\\nbar')

    def test_convert_datetime(self):
        expected = datetime.datetime(2007, 2, 24, 23, 6, 20)
        dt = converters.datetime_or_none('2007-02-24 23:06:20')
        self.assertEqual(dt, expected)

    def test_convert_datetime_with_fsp(self):
        expected = datetime.datetime(2007, 2, 24, 23, 6, 20, 511581)
        dt = converters.datetime_or_none('2007-02-24 23:06:20.511581')
        self.assertEqual(dt, expected)

    def _test_convert_timedelta(self, with_negate=False, with_fsp=False):
        d = {'hours': 789, 'minutes': 12, 'seconds': 34}
        s = '%(hours)s:%(minutes)s:%(seconds)s' % d
        if with_fsp:
            d['microseconds'] = 511581
            s += '.%(microseconds)s' % d

        expected = datetime.timedelta(**d)
        if with_negate:
            expected = -expected
            s = '-' + s

        tdelta = converters.timedelta_or_none(s)
        self.assertEqual(tdelta, expected)

    def test_convert_timedelta(self):
        self._test_convert_timedelta(with_negate=False, with_fsp=False)
        self._test_convert_timedelta(with_negate=True, with_fsp=False)

    def test_convert_timedelta_with_fsp(self):
        self._test_convert_timedelta(with_negate=False, with_fsp=True)
        self._test_convert_timedelta(with_negate=False, with_fsp=True)

    def test_convert_time(self):
        expected = datetime.time(23, 6, 20)
        time_obj = converters.time_or_none('23:06:20')
        self.assertEqual(time_obj, expected)

    def test_convert_time_with_fsp(self):
        expected = datetime.time(23, 6, 20, 511581)
        time_obj = converters.time_or_none('23:06:20.511581')
        self.assertEqual(time_obj, expected)
