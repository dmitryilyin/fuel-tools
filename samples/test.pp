file { '/tmp/1' :
  ensure => present
}

class tst {
  notify { 'test' :}
  exec { '/bin/true' :}
}

include tst
