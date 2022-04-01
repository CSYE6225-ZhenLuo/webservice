#!/bin/bash
cd /var/www/website/website
cp wsgi.py /home/ec2-user
cd /var/www/
sudo rm -rf website
mkdir website
sudo chown -R apache.apache website
cd /home/ec2-user
