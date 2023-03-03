NODES_NUM = 3
START_INTERFACE_ID = 1
START_NODES_ID = 1
INTERFACE_PREFFIX = "eth"
FROM_IP = "192.168.0.220"
ALL_NODES_IN_CLUSTER = ["192.168.0.220","192.168.0.221","192.168.0.222"]
HOSTNAME_PREF = 'h'

def get_nodes (count, from_ip, hostname_pref)
  nodes = []
  ip_arr = from_ip.split('.')
  first_ip_part = "#{ip_arr[0]}.#{ip_arr[1]}.#{ip_arr[2]}"
  count.times do |i|
      hostname = "%s%01d" % [hostname_pref, (i+START_INTERFACE_ID)]
      nodes.push([i+START_NODES_ID, hostname, "#{first_ip_part}.#{ip_arr.last.to_i+i}", "#{INTERFACE_PREFFIX}#{i+START_INTERFACE_ID}"])
  end
  nodes
end

Vagrant.configure("2") do |config|
  config.vm.box = "generic/ubuntu2004"
  config.vm.provider "virtualbox" do |v|
    v.memory = 4096
    v.cpus = 1
  end

  nodes = get_nodes(NODES_NUM, FROM_IP, HOSTNAME_PREF)

  # (1..N).each do |i|
  #   config.vm.define "node_#{i}" do |node|
  #     node.vm.network "private_network", type: "dhcp"
  #     # config.vm.network "public_network", ip: "192.168.0.21#{i}"
  #     node.vm.network :public_network, ip: "#{hostaddr}", bridge: "#{interface}"
  #     node.vm.hostname = "vm#{i}"
  #     node.vm.provider :vmware_desktop do |vb|
  #       vb.memory = 2048
  #       vb.cpus = 1
  #       vb.gui = false
  #     end
  #   end
  # end
  config.vm.provision "shell" do |s|
    ssh_pub_key = File.readlines("/home/eugene/.ssh/eugene.pub").first.strip
    s.inline = <<-SHELL
      mkdir /root/.ssh
      echo #{ssh_pub_key} >> /home/vagrant/.ssh/authorized_keys
      echo #{ssh_pub_key} >> /root/.ssh/authorized_keys
    SHELL
  end
  nodes.each do |in_cluster_position, hostname, hostaddr, interface|
    config.vm.define hostname do |box|
        box.vm.hostname = "#{hostname}"
        #box.vm.network :private_network, ip: "#{hostaddr}", :netmask => "255.255.0.0"
        #box.vm.network :private_network, ip: "#{hostaddr}", :netmask => "255.255.0.0",  virtualbox__intnet: true
        box.vm.network :public_network, ip: "#{hostaddr}", bridge: "#{interface}"
        # box.vm.provision :shell, :inline => provision_node(hostaddr, ALL_NODES_IN_CLUSTER)
        # if in_cluster_position == 1
        #     box.vm.provision :shell, :inline => start_cluster()
        # else
        #     box.vm.provision :shell, :inline => attachnode()
        # end
    end
  end
end
