## cloud-init

cloud-init provides a framework for early Ubuntu/Debian guest initialization
similar to [CloudInit](http://cloudinit.readthedocs.io/en/latest/).
In VMware and Hyper-V environments it replaces guest customization with
more flexible and extensible mechanism.
Compared to original cloud-init project it's more lightweight, but with a limited set of features, though extensible through plugins.
Python >=3.5 is required!

List of bundled plugins:
- 01_hostname.py
- 02_network.py
- 10_disk.py
- 15_user.py
- 20_ssh.py
- 21_cleanup.py

Currently the only supported config source is cloud-config.json file stored on cdrom or locally in /var/lib/cloud-init/ directory:
```
{
  "HostName": "cloud-init",
  "HDD": [
    {
      "Capacity": 40,
      "DeviceNode": "scsi0:0"
    },
    {
      "Capacity": 10,
      "DeviceNode": "scsi1:0",
      "Label": "data",
      "FileSystem": "ext4",
      "MountPoint": "/home"
    }
  ],
  "NIC": [
    {
      "Ip": [
        "10.9.3.105/24",
        "10.9.3.106/24"
      ],
      "Mac": "00:15:5d:2e:21:16",
      "Gw": "10.9.3.1"
    },
    {
      "Ip": [
        "10.250.157.10/24"
      ],
      "Mac": "00:50:56:97:1d:28"
    }
  ],
  "DNS": {
    "DomainSearch": [
      "domain.local",
      "company.net"
    ],
    "Servers": [
      "8.8.8.8"
    ]
  },
  "Domain": {
    "Name": "server.net"
  },
  "Users": [
    {
        "Name": "localadmin",
        "Groups": [ "admin" ],
        "System": false,
        "Password": [
            "PV+j7zZWctl3HvccGzJUetBblhV5qOjhaPdlvr/FFSZEWBmyCoYCB6A0V0iYyqIU",
            "4JrU7pljAnzvcvXK1eh4PD4yr6S9wj/7bBynxsYGH2YlYI4uDwv5sFUP8p2kwNAd",
            "qafVuuItZFWzNDeg/Ta/w+UJbXjsXn7+PfAc5wo1sMX9tgUV7G6FJh7kVwzxl7Ax",
            "/Oegu0a94fUMSZJaU8cJJ4JFUHpopmtSkOQyVxykHPKYCX8njdaabnRwhzc0jugU",
            "+l5pCx0ljpEJbkVtfbOHij5IZFD0AKsoWJg1Uzmfjs7hwcFQmDaXUajBK3Fq5XNs",
            "WiQIKnXzk5ppTxJEL66KtQ=="
        ],
        "Sudo": "ALL=(ALL) NOPASSWD:ALL",
        "SshKey": [
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDAVbC/lowrfIEUZMSFgp1FeVhmlDhWfudCwZ0euEz",
            "KTZdQxXfMc75DOVAs/5rNNZy6jafwTOSF/2xxzX4KpJ+j/7CyLbw67+F/JdHmDlx8lENwnK4FDMO8d1",
            "4jdFuglvfz+bxS7EtTHWNKdE3nYY7/j/JqRYrCqKRwbQbZu87qtf+EV7AVtfVrhy1rVRbZalERnUWAV",
            "xhkxtLdb/IToBXZfRs1PWQ+Mbv8gTBvNghMYiI/fMIzQ6N4BAPQBgH70PyoyvrdQGAmjol2HAiwoqWs",
            "5YZS/1Mz+Qu82kq42hlFmCnAtF+qJYuweI8B5jsIBHq4FVIyJBn4c8a3OCWfrjKMs4aqSzVFvpDXqlQ",
            "k70K7pornOAykAgLJzs8ilPEZR2Qcvx3nUIKHcQX/PYldyHcLb9ya2OcMG6kk9bhroS/76BpaEidt22",
            "VkC56gxAvp0dF8/ZB4+si+3T+AC7BKMjdpAxFJoWxCgqWqoOF00l3qoqajxvoAwhoI3VRauEOCRatgf",
            "nhqcvj3DqdvaT94dYOAImGl134WRkPHpmHleVzQ9WeQqeR8tvrGad46AwfIrxHwx7ZHfwAeTyH+okI2",
            "I/k7gF2WmHEuaYUf0iDbRoutIeI6LTdg11sC3wj6twE3tjbF8df04+xP4hshgb/CHjVuGdrui7lLWhx",
            "fq1KiVHF98w== corporate@company.com"
        ]
         
    }
  ]
}

```

How to install and enable to run on startup:
```
sudo -H pip3 install git+https://github.com/akamac/cloud-init.git
cd /etc/systemd/system/
wget https://github.com/akamac/cloud-init/raw/master/cloudinit/cloud-init.service
systemctl daemon-reload
systemctl enable cloud-init
```

Put unencrypted private RSA key (private.pem) to /var/lib/cloud-init so that cloud-init can decrypt user passwords, supplied via cloud-config.json  

Script logs are available via:
`journalctl -u cloud-init.service`

Few things to know:
- after successful run module disables itself 
- already partitioned disks are not touched
- disk plugin supports only ext4 filesystem at the moment
- json used for configuration is saved locally and can be checked at `/var/lib/cloud-init/_cloud-config.json` (passwords are cleared)

The module targets Debian-based installations and has been tested on:
- Debian 8 Jessie
- Ubuntu 16.04 LTS Xenial


## For developers
To develop a new plugin create Python 3 scripts, prepend the name with double-digit number according 
to the order when the plugin is intended to be run and put it into the *plugins* folder. 
`cloud_config` dict variable is exposed to your script with parsed content of cloud-config.json.
Also you can use bundled `from tools import run` function to execute arbitrary bash commands.

If you need to restart system after plugin execution, set `reboot = True` before exiting the script,
so the module can suspend execution of the next plugin
and resume after system has been restarted. To handle reboots the module keeps
a *state* file in `/var/lib/cloud-init/` directory where it stores a current execution step.
To reset the state run `cloud-init --set-state 0`

## openssl rsautl
### generate rsa key pair
`openssl genrsa -out keypair.pem -aes128 4096`  

### export public key
`openssl rsa -in keypair.pem -outform PEM -pubout -out public.pem`  

### export unencrypted private key (to be stored in a template)
`openssl rsa -in keypair.pem -out private.pem -outform PEM`  

### encrypt data
#### windows
`New-Password | cmd '/c openssl rsautl -inkey public.pem -pubin -encrypt | openssl enc -base64'`  
#### linux
`echo 'password' | openssl rsautl -inkey public.pem -pubin -encrypt | openssl enc -base64 > encrypted`  

### decrypt data
#### windows
`cat encrypted | cmd '/c openssl enc -d -base64 | openssl rsautl -inkey private.pem -decrypt'`  
#### linux
`cat encrypted | openssl enc -d -base64 | openssl rsautl -inkey private.pem -decrypt`  