#!/usr/bin/env python3

import argparse
import datetime
import re
import os
import os.path
import shutil

def calc_1st_day_of_months_before(months, today):
    m = today.month - months
    y = today.year
    while m < 0:
        m += 12
        y -= 1
    return datetime.date(y, m, 1)

def calc_weekly_ranges(daily_end, monthly_begin):
    ranges = []
    d = daily_end
    d -= datetime.timedelta(1)
    while d > monthly_begin:
        if d.weekday() == 0: # Monday
            ranges.append(d)
        d -= datetime.timedelta(1)
    return ranges

def calc_monthly_ranges(monthly_begin, monthly_end):
    ranges = []
    d = monthly_begin
    while d >= monthly_end:
        ranges.append(d)
        y, m = {
          False: (d.year,     d.month - 1),
          True : (d.year - 1, 12),
        }[d.month == 1]
        d = datetime.date(y, m, 1)
    return ranges

def create_ranges(args, today):

    d_end = today - datetime.timedelta(args.all_keeping_days)
    ranges = [d_end,]

    m_beg = calc_1st_day_of_months_before(args.weekly_months, today)
    m_end = calc_1st_day_of_months_before(args.monthly_months, today)
    ranges += calc_weekly_ranges(d_end, m_beg)
    ranges += calc_monthly_ranges(m_beg, m_end)

    return ranges


def list_backup_dir(args):
    pattern = re.compile(r'^\d{8}-\d{6}$')
    dirs = os.listdir(args.backup_dir)
    return list(filter(lambda n: pattern.match(n), dirs))


def list_remove_dirs(ranges, backups):

    create_date = lambda n: datetime.date(int(n[0:4]), int(n[4:6]), int(n[6:8]))

    def exclude_daily_backups(bkup_dirs, end_date):
        while len(bkup_dirs) > 0:
            bkup_date = create_date(bkup_dirs[0])
            if bkup_date < end_date:
                return
            del bkup_dirs[0]

    remove_list = []
    range_idx = 1
    new_range = True

    bkup_dirs = sorted(backups)
    bkup_dirs.reverse()

    exclude_daily_backups(bkup_dirs, ranges[0])
    while len(bkup_dirs) > 0:
        bkdir = bkup_dirs[0]
        bkup_date = create_date(bkdir)

        while range_idx < len(ranges):
            if bkup_date < ranges[range_idx]:
                new_range = True
                range_idx += 1
            else:
                break
        else:
            break

        if new_range:
            new_range = False
        else:
            remove_list.append(bkdir)
        del bkup_dirs[0]

    remove_list += bkup_dirs
    return remove_list


def remove_old_backup(args, backups, remove_list, dry_run=False):
    for dirname in sorted(backups):
        should_rm = dirname in remove_list
        action = 'Del ' if should_rm else 'Keep'
        print("%s: %s" % (action, dirname))
        if not should_rm or args.dry_run:
            continue
        path = os.path.join(args.backup_dir, dirname)
        shutil.rmtree(path)


def run(args):
    ranges = create_ranges(args, datetime.date.today())
    backups = list_backup_dir(args)
    remove_list = list_remove_dirs(ranges, backups)
    remove_old_backup(args, backups, remove_list)


def main():
    parser = argparse.ArgumentParser(description='Deletes old backup directories.')
    parser.add_argument('-d', '--all-keeping-days', type=int, default=14,
                        help='Recent days in which all backups are kept')
    parser.add_argument('-w', '--weekly-months', type=int, default=3,
                        help='During recent this months, backups are kept weekly')
    parser.add_argument('-m', '--monthly-months', type=int, default=36,
                        help='During recent this months, backups are kept monthly. Dictories before this months are deleted.')
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('backup_dir', type=str)
    args = parser.parse_args()

    run(args)


if __name__ == "__main__":
    main()
