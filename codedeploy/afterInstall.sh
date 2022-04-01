#!/bin/bash
cd /var/www/website/website
rm wsgi.py
cd /home
cp wsgi.py /var/www/website/website
cd /var/www
sudo chown -R apache.apache website
cd /home/ec2-user
sudo systemctl restart httpd.service
