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

import logging

import numpy as np

'''
Section with global variables that define general configurations of the script.
'''
root_folder = '/tmp/' # Root folder, where all the files are
bing_link = 'http://www.bing.com/' # Link of the figure
directory = 'figures' # Directory where all the figures are saved
config_file='mail.cfg' # Config file where are expected some configurations, like username and password of the mail server
artigos_file='artigos.json'
section='configs' #Section of the config file
receivers_folder='receivers' # folder where all the json files of the receivers can be found
log_file='bing.log'
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

    LOG_INFO('New image founded: [' + image_name + ']')

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
            LOG_INFO('Decoding...')
            LOG_INFO(f)
            config = json.load(f)

        toAddr = config['email']
        #if 'plrocha' not in toAddr:
        #    continue

        LOG_INFO(toAddr)

        message = config['message']
        #message = message.replace('*',unicode(image_description,'utf-8'))
        message = message.replace('*',image_description)
        if '\n#\n' in message:
            message = message.replace('\n#\n','\n' + get_artigo() + '\n')

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

def get_logger_object(level=logging.INFO):
    logger = logging.getLogger('BingApp')
    hdlr = logging.handlers.RotatingFileHandler(root_folder+log_file, maxBytes=2000000,backupCount=5)
    #hdlr = logging.FileHandler(root_folder+log_file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(level)
    return logger

def LOG_ERROR(ex):
    '''
    Log info in string to log file
    '''

    logger_obj.error(ex, exc_info=True)


def LOG_INFO(string):
    '''
    Log info in string to log file
    '''

    logger_obj.info(string)

def get_img_and_description():
    '''
    Crawls dnd ownloads the image of the day
    '''
    n_counts = 0
    max_counts = 10

    while n_counts < max_counts:

        try:
            n_counts += 1
            LOG_INFO('Temptative ' + str(n_counts) + '/' + str(max_counts))
            call_crawller()
            LOG_INFO('Crawled...')

            with open(datetime.now().strftime("%w") + ".json",'r') as f:
                data = json.load(f)[0]

            img_name = download_image(data['img_link'])
            description = "\n\"" + data['title'] + '\"\n\n' + data['description'].replace('<div>','').replace('</div>','') + "\n"

            LOG_INFO('Description:[' + description.encode('utf-8') + ']')
            LOG_INFO('Image name:[' + img_name.encode('utf-8') + ']')

            if not ( 'NONE' in img_name or 'NONE' in description):
                LOG_INFO('ALL OK....')
                n_counts = max_counts
        
        except Exception as e:

            LOG_ERROR(e)

    return description,img_name

def get_artigo():
    if not os.path.isfile(get_file_location(artigos_file)):
        LOG_INFO('Not found: ' + artigos_file)
        return ''
    with open(get_file_location(artigos_file)) as f:
        data = json.load(f)

    string=''
    while data is not None:
        size = len(data)
        pos = np.random.randint(size)
        key = list(data.keys())[pos]
        string += key + ' - '
        data = data[key]
        if 'Art.' in data:
            string += '\n' + data
            data = None

    return string

def call_crawller():
    '''
    Calls the scraper of the bing website, and soters the result in a json file with the name of the weekday that the script has be runned.
    '''
    try:
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
    except Exception as e:

        LOG_ERROR(e)



def main():

    LOG_INFO('Started!')
    #Download and send all the mails
    #image_description,image_name = get_image_and_description()
    image_description,image_name = get_img_and_description()
    send_mails(directory + '/' + image_name, image_description)

if __name__ == "__main__":
    logger_obj = get_logger_object()
    main()
