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


def create_rsync_command(args, backup_dir, last_backup_dir):
    cmd = ['rsync', '-avS']

    if args.checksum:
        cmd.append('--checksum')
    if args.append_verify:
        cmd.append('--append-verify')

    if last_backup_dir is not None:
        cmd.append('--link-dest')
        cmd.append(os.path.join('..', last_backup_dir))

    if args.reflink:
        cmd.extend(('--inplace', '--delete'))

    cmd.extend((args.source_dir + os.sep, backup_dir))
    return cmd


def run_command(args, cmd):
    print(cmd)
    if (args.dry_run):
        return
    subprocess.run(cmd)


def do_copy_last_backup_with_reflink(args, backup_dir, last_backup_dir):
    if last_backup_dir is None:
        return


    def add_base_dir(path):
        return os.path.join(args.backup_base_dir, path)

    run_command(args, [
        'cp', '-ax', '--reflink=always',
        add_base_dir(last_backup_dir),
        add_base_dir(backup_dir)
    ])


def do_rsync(args, subdir, last_backup_dir):
    backup_dir = os.path.join(args.backup_base_dir, subdir)
    cmd = create_rsync_command(args, backup_dir, last_backup_dir)
    run_command(args, cmd)


def do_backup(args):
    subdir = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    last_backup_dir = find_last_backup_dir(args, subdir)
    if args.reflink:
        do_copy_last_backup_with_reflink(args, subdir, last_backup_dir)
        last_backup_dir = None
    do_rsync(args, subdir, last_backup_dir)


def main():
    parser = argparse.ArgumentParser(description='Incremental backup utility.')
    parser.add_argument('source_dir', type=str)
    parser.add_argument('backup_base_dir', type=str)
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-c', '--checksum', action='store_true')
    parser.add_argument('-a', '--append-verify', action='store_true')
    parser.add_argument('-l', '--reflink', action='store_true')
    args = parser.parse_args()
    do_backup(args)


if __name__ == "__main__":
    main()
