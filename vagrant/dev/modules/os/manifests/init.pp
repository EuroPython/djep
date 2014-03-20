class os {
  file { "/etc/update-motd.d/60-djepintro":
    ensure  => file,
    source  => "puppet:///modules/os/motd.sh",
    mode    => "0755"
  }
}
