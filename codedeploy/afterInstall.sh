#!/bin/bash
cd /var/www/website/website
sudo rm -rf wsgi.py
cd /home/ec2-user
sudo cp wsgi.py /var/www/website/website
cd /var/www
sudo chown -R apache.apache website
cd /home/ec2-user
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/amazon-cloudwatch-config.json
sudo systemctl restart httpd.service
