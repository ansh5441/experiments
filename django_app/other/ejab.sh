#!/usr/bin/env bash
apt-get install -y git
git clone https://github.com/royneary/ejabberd.git
# for latest erlang version (without this older version will be installed)
wget http://packages.erlang-solutions.com/erlang-solutions_1.0_all.deb
dpkg -i erlang-solutions_1.0_all.deb
apt-get update
apt-get -y upgrade
apt-get install -y autoconf-archive
apt-get install -y build-essential
apt-get install -y libssl-dev
apt-get install -y libyaml-dev
apt-get install -y libexpat1-dev
apt-get install -y esl-erlang=1:17.5.3

git clone https://github.com/royneary/mod_push.git
# copy the source code folder to the module sources folder of your ejabberd
# installation (may be different on your machine)
# if done right ejabberdctl will list mod_push as available module
# automatically compile and install mod_push


cd ejabberd
sudo ./autogen.sh && sudo ./configure && sudo make && sudo make install
cd ..
sudo cp -R mod_push /var/spool/jabber/.ejabberd-modules/sources/
#ejabberdctl modules_available
ejabberdctl modules-update-specs
ejabberdctl module_install mod_push

#sudo apt-get remove -y esl-erlang && sudo apt-get autoremove -y esl-erlang && sudo apt-get purge -y esl-erlang && sudo apt-get remove -y erlang-* && sudo apt-get autoremove -y erlang-* && sudo apt-get purge -y erlang-*