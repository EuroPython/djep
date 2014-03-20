#!/bin/bash
locale-gen en_GB.UTF-8

# This first of all updates puppet to the latest stable release for
# Ubuntu and then installs some helper moodules.

if [ ! -f "puppetlabs-release-precise.deb" ]; then
    wget https://apt.puppetlabs.com/puppetlabs-release-precise.deb
    dpkg -i puppetlabs-release-precise.deb
    apt-get update
    apt-get dist-upgrade --yes
fi

cd /etc/puppet/modules

puppet module list --modulepath /etc/puppet/modules | grep puppetlabs-apt
if [ $? -ne 0 ]; then
    puppet module install puppetlabs/apt
fi

puppet module list --modulepath /etc/puppet/modules | grep jfryman-nginx
if [ $? -ne 0 ]; then
    puppet module install jfryman/nginx
fi

puppet module list --modulepath /etc/puppet/modules | grep puppetlabs-nodejs
if [ $? -ne 0 ]; then
    puppet module install puppetlabs/nodejs
fi

puppet module list --modulepath /etc/puppet/modules | grep puppetlabs-postgresql
if [ $? -ne 0 ]; then
    puppet module install puppetlabs/postgresql
fi
