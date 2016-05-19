# bing_send_mail
Python script that downloads and sends the bing image of the day thru e-mail

# Configuration
 Mail configurations such as username, password should be done mail.cfg file. Other configurations such as the root installation shoud be done at the file bing_send_mail.py

#Cron jobs
It's easy to make it a cron job, by adding the following to your crontab (after editing for your specific folder):

00 6 * * * /home/pedro/doc/python/bing_send_mail/bin/python2.7 /home/pedro/doc/python/bing_send_mail/bing_send_mail.py >> /home/pedro/doc/python/bing_send_mail/bing_send_mail.log 2>&1
