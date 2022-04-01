#!/bin/bash
cd /var/www/website/website
sudo rm -rf wsgi.py
cd /home/ec2-user
cp wsgi.py /var/www/website/website
cd /var/www
sudo chown -R apache.apache website
cd /home/ec2-user
sudo systemctl restart httpd.service
