# -*- coding: utf-8 -*-
import re
import urllib
import os
import smtplib

from os.path import basename,abspath
from os import listdir
from ConfigParser import ConfigParser
import json

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

'''
Section with global variables that define general configurations of the script.
'''
root_folder = '/tmp/' # Root folder, where all the files are
bing_link = 'http://www.bing.com/' # Link of the figure
directory = 'figures' # Directory where all the figures are saved
config_file='mail.cfg' # Config file where are expected some configurations, like username and password of the mail server
section='configs' #Section of the config file
receivers_folder='receivers' # folder where all the json files of the receivers can be found
#receivers_folder='receivers_example'
#config_file='mail_example.cfg'

def get_file_location(filename):
    '''
    Returns the location of a file within the root folder. This method is usefull for cron jobs

    Returns: string
    ----------------------------

    Representing the complete location of the file
    '''
    return root_folder + filename

def get_image_and_description():
    '''
    Download and store the bing image of the day. 

    Returns: tuple (string,string)
    ----------------------------

    The name of the file containig the image and a description of the image.
    '''

    # Downloads the image and description
    body = urllib.urlopen(bing_link).read()
    link_image = re.search("az(.*?)jpg", body).group(0).replace('\\','')
    image_description = re.findall("alt=\"(.*?)\"", body)[0]

    full_image_link = bing_link + link_image
    image_name = full_image_link.split('/')[-1]

    # stores the image in the specified folder
    direc = get_file_location(directory)
    if not os.path.exists(direc):
        os.makedirs(direc)

    urllib.urlretrieve(full_image_link,direc + '/' + image_name)

    return image_description,image_name

def send_mails(filename,image_description):
    '''
    Send all the mails to the receivers.

    Returns: None
    '''

    # Reads the configuration file of the mail server and user
    cp = ConfigParser()
    cp.read(get_file_location(config_file))

    fromAddr = cp.get(section,'sender_mail')
    username = cp.get(section,'username')
    password = cp.get(section,'password')
    subject = cp.get(section,'subject')

    # Connect to the server
    server = smtplib.SMTP(cp.get(section,'mail_server'))
    server.ehlo()
    server.starttls()
    server.login(username,password)

    # Iterates trough all the receiver contained in the receivers folder (in the json format)
    for json_file in os.listdir(get_file_location(receivers_folder)):
        with open(get_file_location(receivers_folder) + '/' + json_file,'r') as f:
            config = json.load(f)

        toAddr = config['email']
        message = config['message']
        message = message.replace('*',unicode(image_description,'utf-8'))

        msg = MIMEMultipart(
                From=fromAddr,
                #To=COMMASPACE.join(send_to),
                To=toAddr,
                Date=formatdate(localtime=True)
            )
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain', 'utf-8'))

        files = [filename]
        for f in files or []:
            with open(get_file_location(f), "rb") as fil:
                msg.attach(MIMEApplication(
                    fil.read(),
                    Content_Disposition='attachment; filename="%s"' % basename(f),
                    Name=basename(f)
                ))

        server.sendmail(fromAddr,toAddr,msg.as_string())

    server.quit()

def main():

    #Download and send all the mails
    image_description,image_name = get_image_and_description()
    send_mails(directory + '/' + image_name, image_description)

if __name__ == "__main__":
    main()
