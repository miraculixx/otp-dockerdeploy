##

define nginxproxy ($members) {

  class { 'nginx':
    service_ensure => 'stopped',
  }

  nginx::resource::vhost { '_default':
    ensure         => present,
    proxy          => "http://otp",
  }

  nginx::resource::upstream { 'otp':
    ensure         => present,
    members        => $members,
  }

}
