# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.synced_folder "mocks/sample_data", "/home/vagrant/error_log"

  config.vm.provider "virtualbox" do |vb|
    vb.gui = false
    vb.memory = "1024"
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/site.yaml"
    ansible.host_vars = {
      "default" => {
        "server_url": "https://api.coscene.cn",
        "project_slug": "default/yang-ming-zhuan-yong",
        "api_key": "xxxxxxxxxxxxxxxxxxxxxxxxx",
        "base_dir": "/home/vagrant/error_log"
      }
    }
  end
end
