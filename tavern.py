#!/usr/bin/env python

# By Jonathan DePrizio, April 16, 2012
# Uploaded to Github on Feb 13, 2013
# Released into the public domain

####################
####################

WIRELESS_LOOKUP = {	'VerizonWireless':'vtext.com',
			'VerizonPix':'vzwpix.com',
			'ATT':'txt.att.net',
			'SprintPCS-CDMA':'messaging.sprintpcs.com',
			'VirginMobile':"vmobi.com"}

DEFAULT_CONFIG = "~/.tavernrc"

import subprocess, smtplib, sys
from email import Encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from optparse import OptionParser
from socket import gethostname
import os

CONFIGITEMS={	'SMTPSERVER':'',
		'SMTPUSER':'',
		'SMTPPASS':'',
		'SMTPSSL':'',
		'SMTPPORT':'',

		'PHONETARGET':'undef',
		'EMAILTARGET':'undef',
		'WIRELESSPROVIDER':'undef'}

def parseConfigFile(configLines):
	# goes through the lines read from the file specified with -f 
	# and fills in proper details.
	#
	# Required entries: SMTPSERVER, SMTPUSER, SMTPPASS, SMTPSSL, SMTPPORT
	# Optional entries: PHONETARGET, EMAILTARGET, WIRELESSPROVIDER

	for rawline in configLines:
		line = rawline.split("#")[0].replace("\n", "")
		
		if (line.count("=") != 1):
			if len(line) != 0:
				print "Warning - invalid line in config: " + line
				continue
		else: 
			line = line.split("=") 
			descriptor = line[0]
			value = line[1]
			if descriptor in CONFIGITEMS:
				CONFIGITEMS[descriptor] = value
			else:
				print "Warning - Unrecognized configuration option: " + descriptor


options = OptionParser()
options.add_option("-c", help="The command you want to run.", dest="cmd", default=None)
options.add_option("-f", help="Configuration file.  Default is ~/.tavernrc", dest="configFile", default=DEFAULT_CONFIG)
options.add_option("-v", help="Show debug messages when connecting to the mail server.", dest="mailDebug", default=False,action="store_true")
options.add_option("-m", help="Message to send", dest="message", default="nomessage")
options.add_option("-a", help="Attachment (not supported on basic SMS services)", dest="attachment_file_path")
opts, args = options.parse_args()

opts.configFile = os.path.expanduser(opts.configFile)
try:
	cf = open(opts.configFile, 'r')
except:
	if opts.configFile == DEFAULT_CONFIG:
		# user didn't specify a config file
		print "Please setup your configuration file in ~/.tavernrc"
		print "An example configuration file is provided for your enjoyment."
		sys.exit(1)
	else:
		print "Failed to open specified config file: " + opts.configFile
		sys.exit(1)
else:
	parseConfigFile(cf.readlines())
	cf.close()

if not opts.cmd:
	print "You must specify a command to run with -c."
        sys.exit(1)

if (CONFIGITEMS["WIRELESSPROVIDER"] != "undef"):
	if (CONFIGITEMS["WIRELESSPROVIDER"] not in WIRELESS_LOOKUP.keys()):
		print "Your wireless provider is not supported."
		sys.exit(1)

DEST_EMAIL_ADDRESSES = []
if CONFIGITEMS["PHONETARGET"] != "undef":
	DEST_EMAIL_ADDRESSES.append(str(CONFIGITEMS["PHONETARGET"]) + "@" + WIRELESS_LOOKUP[CONFIGITEMS["WIRELESSPROVIDER"]])
if CONFIGITEMS["EMAILTARGET"] != "undef":
	DEST_EMAIL_ADDRESSES.append(CONFIGITEMS["EMAILTARGET"])

cmdExec = subprocess.Popen([opts.cmd], shell=True)
rt = cmdExec.wait()

#msgBody = opts.cmd + " rt=" + str(rt)
msgBody = opts.message
msg = MIMEMultipart()
msg['From'] = gethostname()
msg.attach(MIMEText(msgBody, 'plain'))

part = MIMEBase('application', 'octet-stream')
if opts.attachment_file_path != "":
	part.set_payload(open(opts.attachment_file_path, "rb").read())
	Encoders.encode_base64(part)
	part.add_header('Content-Disposition', 'attachment; filename="image.png"')
	msg.attach(part)

for DEST_EMAIL in DEST_EMAIL_ADDRESSES:
	msg['To'] = DEST_EMAIL
	try:
		mailconn = smtplib.SMTP_SSL(CONFIGITEMS["SMTPSERVER"], CONFIGITEMS["SMTPPORT"])
		mailconn.set_debuglevel(opts.mailDebug)
		mailconn.login(CONFIGITEMS["SMTPUSER"], CONFIGITEMS["SMTPPASS"])
		mailconn.sendmail(CONFIGITEMS["SMTPUSER"], DEST_EMAIL, msg.as_string())
		mailconn.quit()
	except:
		print "An error occurred sending the email to " + DEST_EMAIL + ".  Uh oh!"
		sys.exit(1)
