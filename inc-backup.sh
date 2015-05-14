#!/bin/sh

if [ $# -lt 2 ]; then
  echo "Usage:"
  echo ""
  echo "  $ inc-backup.sh TargetDir BackupDir"
  echo ""
  exit 1
fi

TARGET_DIR=$1
BACKUP_BASE_DIR=$2
BACKUP_DIR=`date "+%Y%m%d-%H%M%S"`

# search the most recent backup dir.
LAST_BACKUP_DIR=`\ls $BACKUP_BASE_DIR | sort -n -r | head -1`
if [ ! -z $LAST_BACKUP_DIR ]; then
  LINK_DEST_OPT="--link-dest ../$LAST_BACKUP_DIR"
fi

CMD="rsync -av $LINK_DEST_OPT $TARGET_DIR/ $BACKUP_BASE_DIR/$BACKUP_DIR"
echo $CMD
exec $CMD

