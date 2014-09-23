require 'rubygems'
require 'erb'

module FuelNodes
  FUEL_ISO='/data/iso/MirantisOpenStack-5.0.iso'
  IMAGE_DIR='/home/dilyin/kvm'
  XML_DIR='/home/dilyin/kvm/xml'
  NODES_COUNT=8
  MEMORY=2097152
  CPUS=4
  DISK_TYPE='qcow2'
  DEBUG=false
  SIZE='50G'
  VNC_LISTEN='127.0.0.1'

  class Node
    def node_template
      <<-eos
<domain type='kvm'>
  <name><%= name %></name>
  <memory unit='KiB'><%= memory %></memory>
    <vcpu placement='static'><%= cpus %></vcpu>
  <os>
    <type arch='x86_64' machine='pc-i440fx-trusty'>hvm</type>
    <boot dev='network'/>
    <boot dev='hd'/>
    <bootmenu enable='yes'/>
    </os>
  <features>
    <acpi/>
    <apic/>
    <pae/>
    </features>
  <clock offset='localtime'/>
    <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
    <on_crash>restart</on_crash>
  <devices>
    <emulator>/usr/bin/kvm-spice</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='<%= disk_type %>'/>
    <source file='<%= disk %>'/>
    <target dev='vda' bus='virtio'/>
    <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
    </disk>
    <controller type='usb' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
    </controller>
    <controller type='pci' index='0' model='pci-root'/>
    <interface type='network'>
    <mac address='<%= mac 1 %>'/>
    <source network='<%= net 1 %>'/>
    <model type='virtio'/>
    <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <interface type='network'>
      <mac address='<%= mac 2 %>'/>
    <source network='<%= net 2 %>'/>
    <model type='virtio'/>
    <address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
    </interface>
    <interface type='network'>
      <mac address='<%= mac 3 %>'/>
    <source network='<%= net 3 %>'/>
    <model type='virtio'/>
    <address type='pci' domain='0x0000' bus='0x00' slot='0x08' function='0x0'/>
    </interface>
    <serial type='pty'>
      <target port='0'/>
    </serial>
    <console type='pty'>
      <target type='serial' port='0'/>
    </console>
    <input type='tablet' bus='usb'/>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    <graphics type='vnc' port='<%= vnc_port %>' sharePolicy='ignore'>
      <listen type='address' address='<%= vnc_listen %>'/>
    </graphics>
    <video>
      <model type='cirrus' vram='9216' heads='1'/>
    <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <memballoon model='virtio'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
    </memballoon>
  </devices>
</domain>
      eos
    end

    def nailgun_template
      <<-eos
<domain type='kvm'>
  <name><%= name %></name>
  <memory unit='KiB'><%= memory %></memory>
    <vcpu placement='static'><%= cpus %></vcpu>
  <os>
    <type arch='x86_64' machine='pc-i440fx-trusty'>hvm</type>
    <boot dev='hd'/>
    <boot dev='cdrom'/>
    <bootmenu enable='yes'/>
    </os>
  <features>
    <acpi/>
    <apic/>
    <pae/>
    </features>
  <clock offset='localtime'/>
    <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
    <on_crash>restart</on_crash>
  <devices>
    <emulator>/usr/bin/kvm-spice</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='<%= disk_type %>'/>
      <source file='<%= disk %>'/>
      <target dev='vda' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
    </disk>
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <source file='<%= iso %>'/>
      <target dev='hdc' bus='ide'/>
      <readonly/>
      <address type='drive' controller='0' bus='1' target='0' unit='0'/>
    </disk>
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <source file='<%= iso %>'/>
      <target dev='hdb' bus='ide'/>
      <readonly/>
      <address type='drive' controller='0' bus='0' target='0' unit='1'/>
    </disk>
    <controller type='usb' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
    </controller>
    <controller type='pci' index='0' model='pci-root'/>
    <controller type='ide' index='0'>
    <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>
    </controller>
    <interface type='network'>
      <mac address='<%= mac 0 %>'/>
    <source network='<%= net 1 %>'/>
    <model type='virtio'/>
    <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <serial type='pty'>
      <target port='0'/>
    </serial>
    <console type='pty'>
      <target type='serial' port='0'/>
    </console>
    <input type='tablet' bus='usb'/>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    <graphics type='vnc' port='<%= vnc_port %>' sharePolicy='ignore'>
      <listen type='address' address='<%= vnc_listen %>'/>
    </graphics>
    <video>
      <model type='cirrus' vram='9216' heads='1'/>
    <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <memballoon model='virtio'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
    </memballoon>
  </devices>
</domain>
      eos
    end

    attr_accessor :index

    def debug?
      !!FuelNodes::DEBUG
    end

    def run(cmd)
      if debug?
        puts cmd
        0
      else
        puts cmd
        system cmd
        $?.exitstatus
      end
    end

    def initialize(index=0)
      @index = index if index and index.is_a? Numeric
    end

    def memory
      FuelNodes::MEMORY.to_s
    end

    def cpus
      FuelNodes::CPUS.to_s
    end

    def disk_type
      FuelNodes::DISK_TYPE.to_s
    end

    def image_dir
      FuelNodes::IMAGE_DIR.to_s
    end

    def disk_file
      "#{name}.#{disk_type}"
    end

    def disk
      File.join image_dir, disk_file
    end

    def iso
      FuelNodes::FUEL_ISO.to_s
    end

    def size
      FuelNodes::SIZE.to_s
    end

    def nailgun?
      index == 0
    end

    def mac(ifnum)
      ifnum = ifnum.to_s.rjust 2, '0'
      "52:54:00:00:#{ifnum}:#{number}"
    end

    def net(netnum)
      "fuel#{netnum}"
    end

    def vnc_port
      (5900 + 10 + index).to_s
    end

    def vnc_listen
      FuelNodes::VNC_LISTEN.to_s
    end

    def number
      index.to_s.rjust 2, '0'
    end

    def name
      return 'nailgun' if nailgun?
      "node-#{number}"
    end

    def xml_file
      File.join FuelNodes::XML_DIR, name + '.xml'
    end

    def xml
      template = ERB.new(nailgun? ? nailgun_template : node_template)
      template.result(binding)
    end

    def remove_disk
      run "rm -f '#{disk}'"
    end

    def create_disk
      run "qemu-img create -f '#{disk_type}' -o preallocation=metadata '#{disk}' '#{size}'"
    end

    def remove_xml
      File.delete xml_file if File.exists? xml_file
    end

    def create_xml
      File.open(xml_file, 'w') { |file| file.write xml}
    end

    def undefine_domain
      remove_xml
      run "virsh undefine #{name}"
    end

    def define_domain
      create_xml
      run "virsh define #{xml_file}"
    end

    def recreate_disk
      remove_disk
      create_disk
    end

    def redefine_domain
      undefine_domain
      define_domain
    end

    def recreate_node
      recreate_disk
      redefine_domain
    end

    def create_snapshot(snapshot='snapshot')
      run "virsh suspend #{name}"
      run "virsh snapshot-create-as #{name} #{snapshot}"
      run "virsh resume #{name}"
    end

    def revert_snapshot(snapshot='snapshot')
      run "virsh suspend #{name}"
      run "virsh snapshot-revert #{name} #{snapshot}"
      run "virsh resume #{name}"
    end

    def list_snapshots
      run "virsh snapshot-list #{name}"
    end

    def delete_snapshots
      code = 0
      until code != 0
        code = run "snapshot-delete #{name} --current"
      end
    end

  end

  def self.nodes
    nodes = []
    nodes << Node.new(0)
    (1..NODES_COUNT).each do |i|
      nodes << Node.new(i)
    end
    nodes
  end

  def self.recreate_env
    self.nodes.each do |n|
      n.recreate_node
    end
  end

  def self.redefine_env
    self.nodes.each do |n|
      n.redefine_domain
    end
  end

  def self.remove_env
    self.nodes.each do |n|
      n.undefine_domain
      n.remove_disk
    end
  end

  def self.snapshot_nodes(*nodes)
    nodes.map do |n|
      node = Node.new n
      node.create_snapshot '1'
    end
  end

  def self.revert_nodes(*nodes)
    nodes.map do |n|
      node = Node.new n
      node.revert_snapshot '1'
    end
  end

  def self.list_snapshot_nodes(*nodes)
    nodes.map do |n|
      node = Node.new n
      node.list_snapshots
    end
  end

end

require 'pry'
binding.pry
