# si470x-RDS_Logger
RDS message logger using a silicon labs si470x FM radio receiver connected to a raspberry pi model B

Scripts to allow a raspberry pi model B to control an si470x FM Reciever and log received RDS messages.
The main purpose of this project is to log the songs a local radio station plays.

*I swear the station plays a handful of songs over and over again - I just want to prove it*


##### si470xOriginal.py
This is the original code from the Raspberry Pi forum by KansasCoder https://www.raspberrypi.org/forums/viewtopic.php?t=28920


##### si470x.py
This is an altered version of si470xOriginal.py that continually polls the si470x board and logs the data to a file.  The log file is rotated every hour.  Use at your own risk.  It was quickly put together from other people's work.  There is no exception handling.  There may be an issue with low signal strength that causes non ASCII characters to be received and crash the program.  The script has been tested with 40 hours of continuous operation and no problems arose.  The logging code is from Stephen Phillips http://blog.scphillips.com/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/


##### si470x.sh
This is the script for /etc/init.d that allows the script to auto-run on startup as a service.  This is once again from Stephen Phillips http://blog.scphillips.com/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/


##### si470xDropBox.sh
This script uploads the rotated log files to dropbox for backup.  The plan was to run it as a cron job, but manual operation served the purpose. DropBox-Uploader by Andrea Fabrizi needs to be installed first https://github.com/andreafabrizi/Dropbox-Uploader


##### Connecting the Raspberry Pi to the si470x Breakout Board
The breakout board is conencted to the raspberry pi via an I2C connection.  The reset line also needs to be connected to Pin 16 - GPIO 23 as shown in the image below.


![Connecting the si470x breakout board to a model B Raspberry Pi](/images/gpio-pinout.png)
