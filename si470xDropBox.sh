# Script to upload log files to DropBox
# DropBox-Uploader by Andrea Fabrizi needs to be installed first
# https://github.com/andreafabrizi/Dropbox-Uploader
# by Grant Trebbin www.grant-trebbin.com

#! /bin/bash
LOG_DIR="/var/log/si470x/"
DBUpload="/home/pi/Dropbox-Uploader/dropbox_uploader.sh"

# The dropbox-upload script needs is called as follows for each file
# dropbox_uploader.sh upload <directory to filename>/<filename> <filename>
find $LOG_DIR -type f -name 'si470x.log.*' -exec sh -c '
    file="$0"
    fname=$(basename "$file")
    '$DBUpload' "upload" "$file" "$fname"
' {} ';'
