import os

def get_user_input(prompt):
    user_input = input(f"{prompt}: ")
    return user_input.strip()

# Collect user input for various configuration options
hostname = get_user_input("Enter the hostname")
username = get_user_input("Enter the username")

# IP Configuration
manual_ip_config = input("Do you want to manually configure the IP address? (y/n): ").lower() == 'y'
if manual_ip_config:
    ip_address = get_user_input("Enter the IP address")
    subnet_mask = get_user_input("Enter the subnet mask")
    gateway = get_user_input("Enter the gateway")
else:
    ip_address = subnet_mask = gateway = None

# Firewall settings
enable_firewall = input("Enable firewall? (y/n): ").lower() == 'y'
allowed_ports = []
if enable_firewall:
    allowed_ports = get_user_input("Enter allowed TCP ports (comma-separated)").split(',')

# Additional packages for environment.systemPackages
additional_packages = get_user_input("Enter additional packages (comma-separated)").split(',')

# Generate the NixOS configuration file
config_content = f'''
{{ config, pkgs, ... }}:

{{
  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix
    ];

  boot.loader.grub.enable = true;
  boot.loader.grub.device = "/dev/sda";
  boot.loader.grub.useOSProber = true;

  networking.hostName = "{hostname}";
  networking.networkmanager.enable = true;
  networking.networkmanager.enable = true;

  {f'networking.interfaces.enp0s3.useDHCP = false; networking.interfaces.enp0s3.ipAddrs = ["{ip_address}/24"]; networking.interfaces.enp0s3.subnetMask = "{subnet_mask}"; networking.interfaces.enp0s3.gateway = "{gateway}";' if manual_ip_config else ''}

  services.xserver.enable = true;
  services.xserver.displayManager.lightdm.enable = true;
  services.xserver.desktopManager.lxqt.enable = true;

  console.keyMap = "uk";

  users.users.{username} = {{
    isNormalUser = true;
    extraGroups = [ "networkmanager", "wheel" ];
    packages = with pkgs; [
      firefox
    ];
  }};

  environment.systemPackages = with pkgs; [
    {', '.join(additional_packages)}
  ];

  services.openssh.enable = true;

  services.xrdp.enable = true;
  services.xrdp.defaultWindowManager = "startplasma-x11";
  services.xrdp.openFirewall = {str(enable_firewall).lower()};

  networking.firewall.allowedTCPPorts = [{', '.join(allowed_ports)}];
}};

'''

# Write the configuration to a file
config_file_path = "/etc/nixos/configuration.nix"
with open(config_file_path, 'w') as config_file:
    config_file.write(config_content)

print(f"Configuration file written to: {config_file_path}")
