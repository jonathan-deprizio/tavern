#!/usr/bin/python

# By Jonathan DePrizio, April 16, 2012
# Licensed under "do whatever the hell you please with it" license.

####################
#  Configuration - this is required.

SMTPSERVER=""
SMTPUSER=""
SMTPPASS=""
SMTPPORT=5125

# Your wireless provider.  Currently supported: verizonwireless.
# It's easy to add more; just add them to the dictionary above
# the import lines below.

WIRELESS_PROVIDER = "verizonwireless"

#  End of user-configurable options
####################

WIRELESS_LOOKUP = {'verizonwireless':'vtext.com'}

import subprocess, smtplib, sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from optparse import OptionParser
from socket import gethostname

options = OptionParser()
options.add_option("-n", help="Your cell number.", default=False, dest="cellNumber")
options.add_option("-c", help="The command you want to run.", dest="cmd", default=False)
opts, args = options.parse_args()

if (not opts.cellNumber) or (not opts.cmd):
        print "All arguments are required. Use -h for help."
        sys.exit(1)

if WIRELESS_PROVIDER not in WIRELESS_LOOKUP.keys():
        print "Your wireless provider is not supported."
        sys.exit(1)

DEST_EMAIL = str(opts.cellNumber) + "@" + WIRELESS_LOOKUP[WIRELESS_PROVIDER]

cmdExec = subprocess.Popen([opts.cmd], shell=True)
rt = cmdExec.wait()
msg = MIMEMultipart('alternative')
msg['From'] = gethostname()
msg['To'] = DEST_EMAIL
msg.attach(MIMEText(msgBody, 'plain'))

try:
        mailconn = smtplib.SMTP(SMTPSERVER, SMTPPORT)
        mailconn.set_debuglevel(1)
        mailconn.login(SMTPUSER, SMTPPASS)
        mailconn.sendmail(SMTPUSER, DEST_EMAIL, msg.as_string())
        mailconn.quit()
except:
        print "An error occurred sending the email.  Uh oh!"
        sys.exit(1)
