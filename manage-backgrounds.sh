#!/bin/bash

# This script will manage several different jobs dealing with managing images
# downloaded as potential backgrounds.

LOCAL='/Users/cyclops/Backgrounds'
OD='/Users/cyclops/Library/CloudStorage/OneDrive-Personal/Pictures'
NBG='/Users/cyclops/Library/CloudStorage/OneDrive-Personal/New Backgrounds'
SCRIPTS='/Users/cyclops/Scripts'
GD='/Users/cyclops/Library/CloudStorage/GoogleDrive-david.hagar@gmail.com/My Drive'
BACKUP='/Users/cyclops/Library/CloudStorage/OneDrive-Personal/Backups/Archives'
TEMP='/Users/cyclops/Temporary'
RSYNC='/usr/local/bin/rsync -ruWth --size-only --inplace --delete'
RAR='/usr/local/bin/rar a -y -rr -m5'

date

echo "Begin cleaning new backgrounds."
"$SCRIPTS/clean-backgrounds.py" "$NBG"

echo "Begin copying backgrounds."
cd "$LOCAL"
chmod 644 ./*
"$SCRIPTS/md5-rename.sh" ./

$RSYNC ./* "$GD/Backgrounds"
$RSYNC ./* "$OD/Backgrounds"

echo "Begin backing up backgrounds."
rm ".DS_store" > /dev/null 2>&1
$RAR "$TEMP/Backgrounds.rar" "./*" > /dev/null
rm "$BACKUP/Backgrounds.rar"
cp "$TEMP/Backgrounds.rar" "$BACKUP"
rm "$TEMP/Backgrounds.rar"