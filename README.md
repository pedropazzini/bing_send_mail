# bing_send_mail
Python script that downloads and sends the bing image of the day thru e-mail with a specific message for each of multiple receivers.

# Configuration
Mail configurations such as username, password should be done mail.cfg file. The receivers configuration should be done in the receivers folder, and each file on it saves the configurations for one receiver.

The easiest way to use it is via Docker. So just build the Dockerfile:
```sh
docker build -t bing_send_mail .
```

And then run:

```sh
/usr/bin/docker run -v /home/pedro/doc/python/bing_send_mail/:/tmp/ bing_send_mail
```

#Cron jobs
It's easy to make a cron job for it by adding the following to your crontab (after editing for your specific installation folder):

```sh
00 6 * * * /usr/bin/docker run -v /home/pedro/doc/python/bing_send_mail/:/tmp/ bing_send_mail
```
