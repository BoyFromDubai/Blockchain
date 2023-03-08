Vagrant.configure("2") do |config|

  N = 4

  (1..N).each do |i|
    config.vm.box = "generic/ubuntu2004"
    config.vm.define "node_#{i}" do |node|
      node.vm.network "public_network", type: "dhcp"
      # config.vm.network "public_network", ip: "192.168.0.21#{i}"
      node.vm.hostname = "vm#{i}"
      node.vm.provider :vmware_desktop do |vb|
        vb.memory = 2048
        vb.cpus = 1
        vb.gui = false
      end
    end
  end
  config.vm.provision "shell" do |s|
    ssh_pub_key = File.readlines("/home/eugene/.ssh/eugene.pub").first.strip
    s.inline = <<-SHELL
      mkdir /root/.ssh
      echo #{ssh_pub_key} >> /home/vagrant/.ssh/authorized_keys
      echo #{ssh_pub_key} >> /root/.ssh/authorized_keys
    SHELL
  end
end
