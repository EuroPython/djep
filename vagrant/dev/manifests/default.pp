node default {
  include apt
  class { 'postgresql::server': }

  package {
    "python-dev": ensure => installed;
    "tmux": ensure => installed;
    "python-setuptools": ensure => installed;
    "postgresql": ensure => installed;
    "libpq-dev": ensure => installed;
    "git": ensure => installed;
    "gettext": ensure => installed;
    "nodejs":
      ensure => installed,
      require => Apt::Ppa["ppa:chris-lea/node.js"];
    "redis-server":
      ensure => installed,
      require => Apt::Ppa["ppa:chris-lea/redis-server"];
    "grunt-cli":
      ensure   => installed,
      require  => Package["nodejs"],
      provider => "npm";
    "bower":
      ensure   => installed,
      require  => Package["nodejs"],
      provider => "npm";
    "sass":
      ensure   => "3.2.12",
      provider => "gem";
    "compass":
      ensure   => "0.12.2",
      provider => "gem"
  }

  apt::ppa {
    "ppa:chris-lea/node.js":;
    "ppa:chris-lea/redis-server":
  }

  exec { "/etc/init.d/redis-server stop ; update-rc.d -f redis-server remove":
    alias => "disable_default_redis",
    onlyif => "/usr/bin/test -f /etc/rc3.d/S20redis-server",
    subscribe => Package["redis-server"]
  }

  exec { "/usr/bin/easy_install virtualenv":
    alias => "install_virtualenv",
    creates => "/usr/local/bin/virtualenv",
    require => Package["python-setuptools"]
  }

  exec { "/usr/bin/easy_install pip":
    alias => "install_pip",
    creates => "/usr/local/bin/pip",
    require => Package["python-setuptools"]
  }

  exec { "/usr/local/bin/virtualenv /opt/venv":
    alias => "create_venv",
    creates => "/opt/venv/bin/activate",
    require => Exec["install_virtualenv"]
  }

  file { "/opt/venv":
    ensure  => "directory",
    owner   => "vagrant",
    recurse => true,
    require => Exec["create_venv"]
  }

  file { "/home/vagrant/.bash_aliases":
    owner   => "vagrant",
    ensure  => "file",
    content => "source /opt/venv/bin/activate
    export DJANGO_CONFIGURATION=Dev
    export DJANGO_DATABASE_URL=postgres:///djep
    export DJANGO_ADDR='0.0.0.0:8000'
    export DJANGO_SECRET_KEY='dev_secret_key'
    if [ -f /vagrant/.env ]; then
      source /vagrant/.env
    fi
    ",
    require => Exec["create_venv"]
  }


  /* Init postgresql */
  exec { "/usr/bin/pg_createcluster 9.1. main":
    onlyif => "/usr/bin/test !-d /var/lib/postgresql/9.1/main"
  }

  postgresql::server::db { 'vagrant': user => 'vagrant', password => 'vagrant'}
  postgresql::server::db { 'djep': user    => 'vagrant', password => 'vagrant'}

  include os
}
