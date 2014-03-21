# -*- mode: ruby -*-
# vi: set ft=ruby :
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "precise32"
  config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-i386-vagrant-disk1.box"

  config.vm.network :forwarded_port, guest: 8000, host: 8080

  config.vm.provision :shell do |shell|
      shell.path = "vagrant/dev/bootstrap.sh"
  end

  config.vm.provision "puppet" do |puppet|
      puppet.manifests_path = "vagrant/dev/manifests"
      puppet.manifest_file = "default.pp"
      puppet.options = [
          "--modulepath=/etc/puppet/modules:/vagrant/vagrant/dev/modules"
      ]
  end

end
