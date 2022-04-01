#!/bin/bash
cd /var/www
sudo chown -R apache.apache website
cd /home/ec2-user
sudo systemctl restart httpd.service
