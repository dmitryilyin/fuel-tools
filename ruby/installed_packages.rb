#!/usr/bin/env ruby
require 'date'

DPKG_LOG = '/var/log/dpkg.log'
YUM_LOG  = '/var/log/yum.log'

def parse_dpkg_log
  packages = []
  File.open(DPKG_LOG, 'r') do |file|
    file.each do |line|
      next unless line.include? ' install '
      fields = line.split /\s+/
      date = "#{fields[0]} #{fields[1]}"
      package = fields[3]
      version = fields.last
      next unless date and package and version
      package = package + '-' + version
      date = DateTime.parse date
      package = {
          :package    => package,
          :date    => date,
      }
      packages << package
    end
  end
  packages
end

def parse_yum_packages
  packages = []
  File.open(YUM_LOG, 'r') do |file|
    file.each do |line|
      next unless line.include? 'Installed:'
      fields = line.split /\s+/
      date = "#{fields[0]} #{fields[1]} #{fields[2]}"
      package = fields[4]
      date = DateTime.parse date
      package = {
          :package    => package,
          :date    => date,
      }
      packages << package
    end
  end
  packages
end

def output_packages(packages)
  packages.each do |package|
    puts "#{package[:date].strftime('%Y-%m-%d_%H:%M:%S')} #{package[:package]}"
  end
end

#===================================

if File.file? DPKG_LOG
  packages = parse_dpkg_log
elsif File.file? YUM_LOG
  packages = parse_yum_packages
end

output_packages packages if packages
