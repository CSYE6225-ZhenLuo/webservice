#!/bin/bash

sudo chown -R Apache.Apache /var/www/website
sudo systemctl restart httpd.service