# Secure Smart Building

This software demonstrates the use of a CyberHive Connect VPN and an ARM Morello machine to
secure the smart technology in a commercial building.

## Warning and License

This software was created for use in a technology demonstrator. It is neither
designed nor intended to be used for any other purpose. In particular, the
authors strongly advise against the use of this software for commercial
purposes, or in any situation where its reliability or security against attack
is important. The software was not designed to operate for more than
a short period of time sufficient for the purposes of demonstration, nor to
operate unsupervised by a person, and is not designed to be secure against
attack by hackers.

The above notice does not form part of the license under which this software
is released, and is for informational purposes only. See LICENSE for details
of how you may use this software, and for the disclaimer of warranties.

The script `attack device/tplink_smartplug.py` was obtained from the GitHub repository
[softScheck/tplink-smartplug](https://github.com/softScheck/tplink-smartplug).
It was originally written by Lubomir Stroetmann and is copyright 2016 by softScheck GmbH.
It is used here under the Apache License, Version 2.0 (see the script itself for further
details).

## Overview

The increasing proliferation of smart devices in many domains offers the promise of
significant advancements in the capabilities and convenience of technology. However,
this comes with a huge increase in the risk of cyberattacks. Thus, cybersecurity is
becoming an increasingly prominent theme in technology deployment.

The use of smart technology in both residential and commercial buildings is evolving
rapidly, with a trend towards the use of Building Operating Systems (BOS). A BOS
is a central point of control for all smart technology in a building (it can be purely
software, or a combination of software and dedicated hardware). By ensuring that all smart
technology is controlled by the BOS, we can begin to move towards a more unified security
policy. However, the BOS and the smart devices must still communicate over some network,
and buildings' networks often lack meaningful security, and are vulnerable to physical
attack as well as attack from the Internet. Thus it is necessary to secure communication
between these devices. This is particularly important given the very poor security of
many common smart technology devices, since an attacker who can gain network access to
these devices can often compromise them with relative ease.

A good solution to this problem is to protect the vulnerable smart devices behind a
VPN, so that no unauthorised devices can access them. The devices are often not capable
of being members of the VPN themselves, but by connecting them to a physically segregated
network segment which is governed by a router which can be a member of the VPN, we can
nevertheless give them the protection of the VPN. Our demonstrator does exactly this,
making use of [CyberHive Connect](https://www.cyberhive.com/product/cyberhive-connect/),
a mesh VPN system which allows traffic to flow directly between devices over a local
network (rather than via a remote relay).

However, it is almost always necessary to allow some access into a secure network in order
for it to perform a useful function. This access should be through some dedicated secure
gateway, which performs authentication before allowing access. It is vital that the gateway
itself is secure against attack, but unfortunately vulnerabilities seem to be an
unavoidable feature of current software. [CHERI](https://www.cl.cam.ac.uk/research/security/ctsrd/cheri/)
offers a powerful mitigation against memory-access vulnerabilities, including the ubiquitous
buffer overflow, which requires little or no change to existing codebases. Our demonstrator
uses an ARM Morello machine as a secure gateway, and includes a demonstration of the ability
of CHERI to mitigate buffer overflows.

## Structure of the demonstrator

Our demonstrator consists of a number of devices connected via Ethernet and WiFi networks.
The scenario represented by our demonstrator is a commercial building with a number of
smart devices managed by a BOS. The building has two tenants, each with their own section
of the building, including a dedicated network segment. There is a building manager who
has overall control of the building.

The following diagrams show the logical and physical structure of the demonstrators.

### Physical Structure
![](images/physical.svg)

### Logical Structure

![](images/logical.svg)

The key components are as follows.

- A collection of common consumer smart devices, including smart bulbs, a smart plug,
  a temperature sensor, and a button-pressing device repurposed as a door-opener.
- A [*Home Assistant Green*](https://www.home-assistant.io/green/) device. This is a
  dedicated platform which runs [*Home Assistant*](https://www.home-assistant.io/),
  an open source home automation system which we use in the role of a BOS.
- Three GL.iNet Shadow Routers (Model GL-AR300M16-Ext). These are small portable routers
  which we use to partition the whole building network into segregated segments.
  We shall collectively refer to these devices as **segmentation routers**.
- An ARM Morello machine, which we use as a secure gateway via which authorised users
  can control the building's smart devices. We shall call this the **control gateway**.
- A main building router, which governs the top-level building network and provides
  Internet access.
- A Raspberry Pi Zero which plays the role of a compromised device on the main building
  network (Note that this device is not shown in the diagrams above).

As shown above, the demonstrator's network structure consists of a primary network, the
**main building LAN**, which is connected to the Internet, and three sub-networks
connected to the main building LAN. Each is connected to the main building LAN via a
small router, which controls traffic between the sub-network and the main building LAN
according to routing/firewall rules. The sub-networks are:
- The **smart device LAN**, which hosts the BOS machine and all the smart devices. By
  restricting access to this sub-network, we can protect these devices from attack.
- The **tenant 1 LAN**, which represents a LAN given to a tenant to use for their
  devices. This sub-network allows access to the Internet and to an interface which allows
  the tenant to control the smart devices in their part of the building. No direct
  access is permitted to the smart device LAN.
- The **tenant 2 LAN** is identical to the tenant 1 LAN. It serves to illustrate the
  possibility of multiple isolated tenant networks.

The communication between different parts of the network is the key to understanding the
demonstrator. The demonstrator can operate in two different modes, **Connect On** mode where
CyberHive Connect is used to create a secure VPN for devices to communicate over the (untrusted)
main building LAN, and **Connect Off** mode which represents how the building network might be
structured with out CyberHive Connect. In Connect Off mode, some communication between devices
has to be sent over the main building LAN, causing security vulnerabilities.

In Connect On mode, the three segmentation routers and the control gateway are all members of
a Connect TAN. This TAN runs on top of the main building LAN, but the traffic is authenticated
and encrypted to prevent unauthorised access. The segmentation router governing the smart device
LAN is configured to prevent any traffic passing from the main building LAN into the smart device
LAN (outward connections from the smart devices are permitted, as some devices rely on cloud services
to function, and inbound traffic on these connections is permitted). This prevents attackers who
gain access to the main building LAN from extending their access into the smart device LAN, and in
particular prevents them from accessing the BOS machine. However, it is necessary to have a mechanism
for accessing the BOS machine in order to allow authorised users to control and monitor the smart
devices. The segmentation router allows traffic to flow freely between the smart device LAN and the TAN.
The control gateway (i.e. the Morello machine) provides an interface which is accessible from the tenant
LANs and the main building LAN, via which authorised users can log in to control or monitor smart devices.
The control gateway is a member of the TAN, and so can send commands to the BOS machine via the TAN and
the smart device LAN.

In Connect Off mode, the control gateway still provides an interface for authorised users to control
smart devices via commands sent to the BOS, but the connection between the control gateway and the segmentation
router governing the smart device LAN must run over the untrusted main building LAN. This in turn means that
the segmentation router must allow traffic from the main building LAN into the smart device LAN, opening up this
network to attack (our demonstrator includes a demonstration of this).

## Demonstration of vulnerabilities and mitigations

Our demonstrator includes two technologies for security, namely CHERI and CyberHive Connect. For both technologies,
the demonstrator includes a demonstration of the vulnerability which is caused by not using the technology, and a
demonstration of how the technology mitigates the vulnerability.

The demonstration of CHERI shows how the use of CHERI can prevent the exploitation of bug in the software running
on the control gateway. When a user attempts to log in via the gateway web interface, the "middleware" software
passes the supplied credentials to an external binary for checking. This binary is compiled from a small
piece of C code. However, this C code contains a (deliberate) buffer
overflow vulnerability. The code copies whatever password is entered into a small fixed-length
buffer without any checking of length. If the C code has been compiled with the clang compiler,
then the memory directly after this buffer contains a boolean variable which records whether
authentication was successful.

If CHERI protections are not enabled, then a malicious user can log in by entering a legitimate user name,
any 10 character string in the password box. This will overflow the buffer (note that the buffer
has been made artificially short to allow ease of demonstration) and overwrite the boolean
variable, making the program think that authentication was successful. However, if CHERI is
enabled, then the processor will detect the illegal memory access and kill the password-checking
program before the illicit log in can succeed.

By toggling a switch on the login screen, a user can choose whether a login attempt will be handled by
a binary compiled with CHERI enabled, or without. The two binaries are compiled from exactly the same
C source code. Thus a user can do a direct side-by-side comparison of CHERI vs non-CHERI.

For CyberHive Connect,the demonstrator has the Connect On and Connect Off modes mentioned above. The demonstrator
includes a small device (in our version, a Raspberry Pi zero) connected to the main building LAN. This device
represents an attacker who has gained access to the main building LAN. The user of the demonstrator can access this
device via a simple web interface using a browser. This interface allows the user to toggle Connect on and off. The user
can run a network scan targeting the smart device LAN, and see the results. When Connect is off, the scan yields information
about the smart devices, while if Connect is on then no such information is gained. Further, when Connect is off, the user
can send commands over the network to turn the smart plug on or off, even though they have no authorisation to do so. This
attack exploits the weak security of the type of smart plug we use. This kind of weak security seems to be alarmingly
common in such consumer-level smart devices. The use of Connect prevents this attack.

## Running the demonstrator

We now explain in detail how the demonstrator can be used once it is up and running. For details of setting up the
demonstrator, see the next section.

To use the demonstrator, use any device which supports WiFi to connect to the WiFi of the tenant 1 LAN (network name is
`demo-tenant-1-network`, password is `demo-tenant-1-network-123`). The things to demonstrate are listed below

### Internet access
Visit some public web page to prove that there is Internet access.

### CHERI
Navigate to the address `openwrt:5000` (i.e. port 5000 on host `openwrt`). This is a port on the LAN
interface of the segmentation router which governs the tenant 1 LAN. The web interface of the control gateway is
forwarded to this port. You will see a login interface.
The three legitimate usernames are `manager`, `tenant_1`,
and `tenant_2`, all with the password `abc123`. Logging in with these credentials will give access to a screen
where smart devices can be monitored or controlled, with the tenants having access to a few devices and the manager
having access to all the devices, including the door control. Screenshots of these interfaces are shown below.

manager view             |  tenant view
:-------------------------:|:-------------------------:
![](/images/mw-manager-view-screenshot.png)  |  ![](/images/mw-tenant-view-screenshot.png)

As mentioned above, the code which checks the credentials entered has a buffer overflow vulnerability. There is a
toggle switch on the login screen to enable or disable the use of CHERI. With CHERI disabled, any 10 character
string can be entered as the password with a legitimate username to achieve a successful login. With CHERI disabled,
this will not work, as the illegal memory access is detected and the login aborted before access can be granted.

### Connect
Navigate to the address `openwrt:5001` (i.e. port 5001 on host `openwrt`). This is a port on the LAN interface
of the segmentation router which governs the tenant 1 LAN. The web interface of the Raspberry Pi Zero which
represents an attacker's access to the main building LAN is forwarded to this port. This interface allows
switching the demonstrator between Connect On mode and Connect Off mode. The interface also allows the running
of a network scan and viewing its results, and attempting to turn a smart plug at a specified IP address on or off.

With Connect off, running a scan will scan the network segment `192.168.38.0/24`, which is the IP address range
of the smart device LAN. Without Connect, there is nothing to stop this scan succeeding. Thus the scan yields
information on what IP addresses are being used, and what ports they have open. Looking down the results will
reveal one IP address with port `9999` open, which an attacker can recognise as a sign that there is a vulnerable
smart plug at that address. The user can enter this IP address as the "target IP" in the interface, set it via the
button, and then send on/off commands via the buttons. Again, with nothing to stop this unauthorised access, the
commands will succeed in turning the plug on/off. The sending of commands is performed using the script
`tplink_smartplug.py`.

With Connect off, both the network scan and the sending of commands will fail.


## Setting up the demonstrator

The demonstrator can be set up using the code found in this repository, plus some items of hardware. This section explains
how to assemble the demonstrator and set everything up. After completing the steps below, starting the demonstrator and running
all the software only requires powering up all the devices and connecting the main building LAN router's WAN connection to some
network which provides Internet access.

To create the demonstrator, we used the following hardware.
- A router running OpenWrt to govern the main building LAN
- Three routers running OpenWrt to act as segmentation routers. Small "portable" type routers are fine for this role
   (We used GL.iNet Shadow Routers, Model GL-AR300M16-Ext). It is easiest if these routers run OpenWrt, as this
   allows the configuration instructions below to be used. All of the routers we used were also wireless access points,
   a feature which will almost certainly be needed for the smart device LAN router since consumer smart devices rarely support
   Ethernet.
- A Home Assistant Green. We opted to use this device as it comes pre-installed with Home Assistant, but any device
  running Home Assistant would work
- A selection of smart devices which are in some way compatible with Home Assistant. We used a smart plug, two smart bulbs,
  a temperature/humidity sensor, and a button-pushing device (which we used to represent a door opening mechanism).
  Any selection of devices would work, but in order to demonstrate the illicit control in the demonstration of Connect Off
  mode, you will need a device which can be targeted by the `tplink_smartplug.py` script. We used a Kasa Smart Wi-Fi Plug Slim
  (model KP115). See [the tplink-smartplug GitHub repo](https://github.com/softScheck/tplink-smartplug) for a list of
  possible products.
- A device to represent an attacker's access to the main building LAN. Any device capable of running Python would work
  here, we chose a Raspberry Pi Zero. We shall call this the **attack device**.
- An ARM Morello board running [Morello Linux](https://www.morello-project.org/) to act as the control gateway.

You will also need some device to use to access the demonstrator. This device needs to be able to connect to the
tenant 1 LAN (by WiFi or Ethernet), and needs to have a web browser.

Four of the devices (the three segmentation routers and the control gateway) need to have CyberHive Connect installed.
To do this, you will need a CyberHive account and the appropriate Connect binary and config files.
See the [CyberHive website](https://www.cyberhive.com/product/cyberhive-connect/) for information on this. The instructions
below assume that Connect is installed on all these devices and that the devices have been added to the TAN. You will also need
the TAN IP addresses of some of the devices in the demonstrator for the configuration below. These TAN IP addresses are assigned
by CyberHive Connect, and can be found in the CyberHive Connect Organisation web interface.

The following sections describe how to construct the demonstrator.

### 1 - Configure main building LAN

Set up the router for the main building LAN to use the network `192.168.37.0/24`. Reserve the following static IP addresses
- For the router itself, `192.168.37.1` (if the router does not already default to this)
- For the smart device LAN segmentation router, `192.168.37.200`
- For the tenant 1 LAN segmentation router, `192.168.37.201`
- For the tenant 2 LAN segmentation router, `192.168.37.202`
- For the attack device, `192.168.37.210`
- For the control gateway, `192.168.37.14`

On OpenWrt, the above can easily be done via the router's graphical interface, or alternatively by editing the configuration
files in `/etc/config/`. Instructions on how to do this are readily available online.

All of these devices should be connected to the main building LAN after they have been set up below.

### 2 - Configure segmentation routers

The configuration of the three segmentation routers is fairly uniform. All need CyberHive Connect installed
as mentioned above. Note that CyberHive Connect will need (at least) slightly more than 2MB of non-volatile
storage to store the large public keys which it uses. This can require the use of additional storage space (e.g.
a USB flash drive) on some devices.

The primary configuration needed for each router is to configure the firewall via the file `/etc/config/firewall`.
Each router has two versions of this file, on for Connect On mode, and one for Connect Off mode. The switching
between these two versions, as well as the process of starting or stopping CyberHive Connect, is managed by a
script called `switch-mode`. This script is called from the attack device when a mode switch is performed. The segmentation
routers for the tenant LANs and the segmentation routers for the smart device LAN have slightly different firewall configurations.

Before setting up the firewall configurations, there are a few other configurations needed.

1. Add the following stanza to `/etc/config/dropbear` to enable ssh access from the main building LAN. Of course, this
   configuration would not be present in a real secure smart building set-up. It is only needed to allow for switching
   between Connect On mode and Connect Off mode.
```
config dropbear
	option PasswordAuth 'on'
	option RootPasswordAuth 'on'
	option Port         '5055'
	option Interface 'wan'
```
2. Edit the file `/etc/config/network` as follows.
   - in the stanza beginning `config interface 'lan'`, change the value of `option ipaddr`
     to `'192.168.38.1` for the smart device LAN router, `'192.168.39.1'` for both tenant LAN routers.
   - add a new stanza
     ```
     config interface 'tan'
        option device 'connect'
     ```
3. Configure the wireless network of the router, if applicable, by editing `/etc/config/wireless` (instructions
   on how to do this are readily available online).
4. On the smart device LAN router, fix the Home Assistant device to have the fixed IP address `192.168.38.2` by adding
   a stanza to the end of `/etc/config/dhcp` as follows
   ```
   config host
        option mac 'xx:xx:xx:xx:xx:xx'
        option ip '192.168.38.2'
   ```
   where `'xx:xx:xx:xx:xx:xx'` should be replaced with the MAC address of the network interface of the Home Assistant device.


In the directories under `segmentation routers` you will find the files for firewall configuration in the demonstrator.
There are two sub-directories `smart building LAN` and `tenant LAN`, each with three files: `firewall-no-connect`,
`firewall-connect`, `switch-mode`. To configure the firewall on each segmentation router, simply take the appropriate set
of 3 files, copy them to some directory on the router, make sure `switch-mode` is executable, and update the two `ln` commands
in `switch-mode` to reflect the location of the files (the versions given here assume the files are in `/mnt/usb-storage/connect-switcher/`).

For the two tenant LAN routers, in the file `firewall-connect`, find the stanza which begins
```
config redirect
        option name		port-forward-for-tenant-access
```
and replace the `xxx.xxx.xxx.xxx` in the `option dest_ip` line with the TAN IP address of the control gateway.

Finally, run `switch-mode on` to start using the new configuration in Connect On mode.

All necessary port forwarding is handled by the firewall configuration. See the various `firewall-*` files for details.

When the above has all been done, connect the WAN interface of the segmentation routers to the main building LAN. It is best to ensure
that all of the segmentation routers are restarted before going further.

### 3 - Configure Home Assistant and smart devices

Connect the Home Assistant device to the smart building LAN, and get Home Assistant set up. Use any username and password you like
to configure Home Assistant.

Configure all the smart devices to use the smart device LAN, and integrate them all into Home Assistant. See the
[Home Assistant web page](https://www.home-assistant.io/) for information on how to do this.

### 4 - Configure control gateway and middleware

The code for the control gateway is in `control gateway`. We refer to this software as the **middleware**.
To set this up on the ARM Morello machine, do the following
(all commands should be run as `root`). These instructions assume that the ARM Morello machine is running Morello Linux,
and that Docker and CyberHive Connect have been installed and configured.

1. Copy the contents of `control gateway` to some directory on the ARM Morello Machine.
   We used `/root/homeassistant-mw-modeswitch`.
2. Run the  `build-on-morello.sh` script
```
chmod +x build-on-morello.sh
./build-on-morello.sh
```
3. Obtain a *Long-lived access token* from your Home Assistant installation, and copy it into the two files `env-connect` and
   `env-no-connect` as the value of `HOMEASSISTANT_TOKEN` in place of the long string of `x` characters.
4. In the `env-connect` file, replace the `xxx.xxx.xxx.xxx` in the `HOMEASSISTANT_HOST` line with the TAN IP of the smart device
   LAN segmentation router.
5. Move the file `demo_server.service` to `/etc/systemd/system/` (you will need to modify this file if the path to the directory
   where you have put the middleware is different to the one we used), and run `systemctl enable demo_server && systemctl start demo_server`.
   This will start the middleware, and set it to start automatically whenever the system is booted.
6. Ensure the `switch-mode` script is executable

Connect the control gateway to the main building LAN and reboot it.

### 5 - Configure attack device

The attack device needs to be capable of running Python and have the utilities `nmap`, `ip`, and `ssh` installed.
We found that a Raspberry Pi Zero running Raspberry Pi OS worked well in this role.
Other platforms would work, provided that python is available, along with `nmap`, `ip`, and `ssh`. Any version of Linux
which uses `ip` would probably be fine.

The software on this device consists of a small Python+Flask web server. This server allows the user to turn Connect on or off, and then
to run network scans and target devices for attack.

Both tenant LAN segmentation routers forward the port where the server listens on the attack device to port 5001 on their LAN interfaces.
This is purely for practicality and convenience of running the demonstrator, since it allows the user to access the attack device from the
same tenant LAN which they join to do the CHERI demonstration.

We assume that you are using some device which has Python and the `nmap` and `ip` utilities installed (or else that `app.py` has been modified
as described above). The files needed for the set up are in the directory `attack device`. Put the files `app.py`  `switch-mode` and
`tplink_smartplug.py` into some directory. We used `/home/user/demo` on our Raspberry Pi Zero.

Connect the attack device to the main building LAN.

In the directory where you placed the files, create a python venv with Flask by doing the following.
```
python3 -m venv venv
source venv/bin/activate
pip install Flask
```

The `switch-mode` script is responsible for switching the demonstrator between Connect On and Connect Off modes. It does this by using `ssh` to
run commands on the segmentation routers and the control gateway. Thus it is necessary to set up public key authentication to allow this to happen.
It may also be necessary to modify the `switch-mode` script.
- If necessary, modify the `switch-mode` script to use the actual paths to the `switch-mode` scripts on the segmentation routers and control
  gateway.
- If necessary, generate an ssh key pair by running the following command as root (and accepting all defaults)
  ```ssh-keygen -t ed25519```
- Set up access to the other devices by running each of the following commands as root, and following the instructions.
  ```
  ssh-copy-id -p 5055 root@192.168.37.200
  ssh-copy-id -p 5055 root@192.168.37.201
  ssh-copy-id -p 5055 root@192.168.37.202
  ssh-copy-id root@192.168.37.14
  ```
  
The commands to run the software on the attack device are as follows, run as root from the directory where `app.py` was put.
```
source venv/bin/activate
flask run --host 0.0.0.0 --port 80
```
We found it convenient to have these commands run automatically on start up. On a Raspberry Pi, this can be arranged by use of
`/etc/rc.local`. An `rc.local` file is provided here. To use it, just move it to `/etc/rc.local`, make it executable, and reboot.





















