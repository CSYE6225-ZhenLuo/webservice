variable "aws_access_key" {
  type    = string
  default = "AKIAZAJCF6G3BKJGRSCK"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "aws_secret_key" {
  type    = string
  default = "3CvT5avvFQ4U32DrJzPJ6j7LHZo+5qaxDsnF2Eis"
}

variable "source_ami" {
  type    = string
  default = "ami-048ff3da02834afdc"
}

variable "ssh_username" {
  type    = string
  default = "ec2-user"
}

variable "subnet_id" {
  type    = string
  default = ""
}

locals { timestamp = regex_replace(timestamp(), "[- TZ:]", "") }

source "amazon-ebs" "autogenerated_1" {
  access_key      = "${var.aws_access_key}"
  ami_description = "Amazon Linux 2 AMI for CSYE 6225"
  ami_name        = "csye6225_spring2022_${local.timestamp}"
  ami_users = [
    "619083854262",
    "489783191838",
  ]
  instance_type = "t2.micro"
  launch_block_device_mappings {
    delete_on_termination = true
    device_name           = "/dev/xvda"
    volume_size           = 20
    volume_type           = "gp2"
  }
  region       = "${var.aws_region}"
  secret_key   = "${var.aws_secret_key}"
  source_ami   = "${var.source_ami}"
  ssh_username = "${var.ssh_username}"
  subnet_id    = "${var.subnet_id}"
}

build {
  sources = ["source.amazon-ebs.autogenerated_1"]

  provisioner "file" {
    source      = "../webservice"
    destination = "/tmp"
  }
  provisioner "shell" {
    environment_vars = [
      "root_password=newPassRoot@3306",
    ]
    inline = [
      "sudo yum -y update",
      "sudo yum -y groupinstall \"Development Tools\"",
      "sudo yum -y install -y amazon-linux-extras",
      "sudo amazon-linux-extras enable python3.8",
      "sudo yum -y install python3.8",
      "sudo yum -y install python38-devel mysql-devel",
      "sudo yum -y install python38-tkinter.x86_64",
      "python3.8 -m venv venv",
      "source venv/bin/activate",

      "pip install django==4.0.3 djangorestframework==3.13.1 mysqlclient==2.1.0 bcrypt==3.2.0",

      "sudo yum -y install https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm",
      "sudo amazon-linux-extras install epel -y",
      "sudo rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2022",
      "sudo yum install -y mysql-community-server",
      "sudo systemctl enable --now mysqld",
      "pa=$(sudo grep 'temporary password' /var/log/mysqld.log | awk -F 'root@localhost: ' '{print $2}')",
      "mysqladmin --user=root -p$pa password \"$root_password\"",
      "mysql -uroot -p$root_password -e \"CREATE DATABASE Django\" --connect-expired-password",
      "mysql -uroot -p$root_password -e \"CREATE USER 'Django'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Django@localhost3306'\" --connect-expired-password",
      "mysql -uroot -p$root_password -e \"GRANT All ON Django.* TO 'Django'@'localhost'\" --connect-expired-password",
      "cd /tmp/webservice",
      "python manage.py makemigrations",
      "python manage.py migrate",
      

    ]
  }
}