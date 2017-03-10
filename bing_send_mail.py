# -*- coding: utf-8 -*-
import re
import urllib
import os
import smtplib

from os.path import basename,abspath
from os import listdir
from configparser import ConfigParser
import json

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

from script import bing
from scrapy.crawler import CrawlerProcess
from datetime import datetime

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

    image_name = download_image(full_image_link)


    return image_description,image_name

def download_image(full_image_link):

    '''
    Downloads and soters the image from the link of the bing image.
    '''
    image_name = full_image_link.split('/')[-1]

    # stores the image in the specified folder
    direc = get_file_location(directory)
    if not os.path.exists(direc):
        os.makedirs(direc)

    urllib.urlretrieve(full_image_link,direc + '/' + image_name)

    print('New image founded: [' + image_name + ']')

    return image_name

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
        #message = message.replace('*',unicode(image_description,'utf-8'))
        message = message.replace('*',image_description)

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

def call_crawller():

    '''
    Calls the scraper of the bing website, and soters the result in a json file with the name of the weekday that the script has be runned.
    '''

    fname =  datetime.now().strftime("%w") + '.json'
    if os.path.isfile(fname):
        os.remove(fname)
    process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'FEED_FORMAT': 'json',
            'FEED_URI': fname
            })

    process.crawl(bing)
    process.start()

def get_img_and_description():
    '''
    Crawls dnd ownloads the image of the day
    '''
    n_counts = 0
    max_counts = 10

    while n_counts < max_counts:

        n_counts += 1

        print('Temptative ' + str(n_counts) + '/' + str(max_counts))

        call_crawller()
        with open(datetime.now().strftime("%w") + ".json",'r') as f:
            data = json.load(f)[0]

        img_name = download_image(data['img_link'])

        description = "\n\"" + data['title'] + '\"\n\n' + data['description'].replace('<div>','').replace('</div>','') + "\n"

        print('Description:[' + description.encode('utf-8') + ']')
        print('Image name:[' + img_name.encode('utf-8') + ']')

        if not (img_name == 'NONE' or description == 'NONE'):
            print('ALL OK....')
            n_counts = max_counts

    return description,img_name

def main():

    #Download and send all the mails
    #image_description,image_name = get_image_and_description()
    image_description,image_name = get_img_and_description()
    send_mails(directory + '/' + image_name, image_description)

if __name__ == "__main__":
    main()
