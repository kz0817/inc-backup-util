#!/usr/bin/env python3
import datetime
import subprocess
import os
import re
import argparse

def find_last_backup_dir(args, backup_dir):

    def extract_dirs(entries):
        for ent in entries:
            path = os.path.join(args.backup_base_dir, ent)
            if (os.path.isdir(path)):
                yield ent

    dirs = extract_dirs(os.listdir(args.backup_base_dir))
    re_bkdir = re.compile(r'^\d{8}-\d{6}$')
    bkdirs = list(filter(re_bkdir.match, dirs))
    if (len(bkdirs) == 0):
        return None
    return sorted(bkdirs)[-1]


def create_command(args, backup_dir):
    cmd = ['rsync', '-avS']

    if args.checksum:
        cmd.append('--checksum')
    if args.append_verify:
        cmd.append('--append-verify')

    last_backup_dir = find_last_backup_dir(args, backup_dir)
    if last_backup_dir is not None:
        cmd.append('--link-dest')
        cmd.append(os.path.join('..', last_backup_dir))

    cmd.extend((args.source_dir + os.sep, backup_dir))
    return cmd


def do_backup(args):
    subdir = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_dir = os.path.join(args.backup_base_dir, subdir)
    cmd = create_command(args, backup_dir)

    print(cmd)
    if (args.dry_run):
        return
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(description='Incremental backup utility.')
    parser.add_argument('source_dir', type=str)
    parser.add_argument('backup_base_dir', type=str)
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-c', '--checksum', action='store_true')
    parser.add_argument('-a', '--append-verify', action='store_true')
    args = parser.parse_args()
    do_backup(args)


if __name__ == "__main__":
    main()
