#!/usr/bin/env python3
import unittest
import housekeeper as hk
import datetime as dt

class Args(object):
    def __init__(self, all_keeping_days, weekly_months, monthly_months):
        self.all_keeping_days = all_keeping_days
        self.weekly_months = weekly_months
        self.monthly_months = monthly_months

class TestHoseKeeper(unittest.TestCase):

    def test_create_ranges(self):
        self.maxDiff = None
        args = Args(14, 2, 24)
        today = dt.date(2018, 6, 20)
        ranges = hk.create_ranges(args, today)
        expected = ([
          dt.date(2018, 6, 6),
          dt.date(2018, 6, 4),
          dt.date(2018, 5, 28),
          dt.date(2018, 5, 21),
          dt.date(2018, 5, 14),
          dt.date(2018, 5, 7),
          dt.date(2018, 4, 30),
          dt.date(2018, 4, 23),
          dt.date(2018, 4, 16),
          dt.date(2018, 4, 9),
          dt.date(2018, 4, 2)] +
          [dt.date(2018, m, 1) for m in range(4, 0, -1)] +
          [dt.date(2017, m, 1) for m in range(12, 0, -1)] +
          [dt.date(2016, m, 1) for m in range(12, 5, -1)])
        self.assertEqual(ranges, expected)


    def test_list_remove_dirs(self):
        ranges = [
          dt.date(2018, 6, 8),
          dt.date(2018, 6, 3),
          dt.date(2018, 5, 1),
          dt.date(2018, 4, 30)]
        backups = [
          '20180610-123456',
          '20180609-123456',
          '20180608-123456',
          '20180607-123456',
          '20180605-123456',
          '20180604-123456',
          '20180603-123456',
          '20180602-123456',
          '20180601-123456',
          '20180531-123456',
          '20180502-123456',
          '20180501-123456',
          '20180430-123456',
          '20180429-123456',
          '20011110-123456',
        ]
        rm_list = hk.list_remove_dirs(ranges, backups)
        expected = [
          # '20180607-123456',
          '20180605-123456',
          '20180604-123456',
          '20180603-123456',
          # '20180602-123456',
          '20180601-123456',
          '20180531-123456',
          '20180502-123456',
          '20180501-123456',
          #'20180430-123456',
          '20180429-123456',
          '20011110-123456',
        ]
        self.assertEqual(rm_list, expected)


if __name__ == '__main__':
    unittest.main()
