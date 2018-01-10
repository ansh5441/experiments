
#!/usr/bin/env bash

# UBUNTU SETUP
apt-get update
apt-get install -y apache2
apt-get install -y libapache2-mod-wsgi-py3
apt-get install -y python3-dev
apt-get install -y libmysqlclient-dev
apt-get install -y python3-pip
apt-get install -y libjpeg-dev
# geodjango
apt-get install -y binutils
apt-get install -y libproj-dev
apt-get install -y gdal-bin
# celery
apt-get install -y rabbitmq-server

pip3 install -r requirements.txt
chown www-data -R logs


#apt-get install -y phpmyadmin
#apt-get install -y mysql-server
#cp hifi_api/settings.py.dist hifi_api/settings.py

#python3 manage.py migrate
#python3 manage.py makemigrations
# AMI setup
#sudo yum install httpd
#yum install -y python34
#yum install -y python34-virtualenv
#yum install -y libjpeg*
#cd /home/ec2-user/
#virtualenv-3.4 myproject
#pip install -r requirements.txt
