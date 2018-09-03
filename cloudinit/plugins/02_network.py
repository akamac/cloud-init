# cloud_config = {}
from tools import run

import os
import ipaddress
import re

hostname = cloud_config['HostName'].lower()
domain = cloud_config['Domain']['Name']
fqdn = '.'.join([hostname, domain])

dns_search_list = [cloud_config['Domain']['Name']]
dns_search_list.extend(cloud_config['DNS'].get('DomainSearch', []))
print('DNS search list: {}'.format(dns_search_list))


def update_hosts(ip):
    current_hostname = os.uname().nodename
    if current_hostname != hostname:
        print('Setting hostname {}'.format(hostname))
        # hostname is initialized early on boot from initramfs, hostnamectl is not available when unit is started
        run('sysctl -w kernel.hostname="{}"'.format(hostname))
        with open('/etc/hostname', 'w') as f:
            f.write(hostname)
    with open('/etc/hosts') as f:
        hosts_content = f.read()
        pattern = r'^[0-9.]{{7,15}}.*{}$'.format(current_hostname)
        hosts_content = re.sub(pattern, '{}\t{}\t{}'.format(ip, fqdn, hostname), hosts_content, flags=re.MULTILINE)
    print('Updating /etc/hosts')
    with open('/etc/hosts', 'w') as f:
        f.write(hosts_content)


print('Reading interfaces from /sys/class/net/')
interfaces = {}
for interface in os.listdir('/sys/class/net/'):
    with open('/sys/class/net/{}/address'.format(interface)) as f:
        mac = f.read().rstrip()
        interfaces.update({mac: interface})

print('Checking if network is managed by systemd')
networkd_status = run('systemctl is-enabled systemd-networkd')
if networkd_status.stdout.rstrip() in [b'enabled', b'enabled-runtime']:
    print('Generating networkd config files')
    main_ip = True
    for nic in cloud_config['NIC']:
        try:
            name = interfaces[nic['Mac'].lower()]
            nic_config = '[Match]\nName={}\n\n[Network]\n'.format(name)
            for ip in nic['Ip']:
                nic_config += 'Address={}\n'.format(ip)
                if nic.get('Gw') and main_ip:
                    main_ip = False
                    nic_config += 'Gateway={}\n'.format(nic['Gw'])
                    for dns_server in cloud_config['DNS']['Servers']:
                        nic_config += 'DNS={}\n'.format(dns_server)
                    nic_config += 'Domains={}\n'.format(' '.join(dns_search_list))
                    update_hosts(ip.split('/')[0])
            print('Dumping {} config'.format(name))
            with open('/etc/systemd/network/50-static-{}.network'.format(name), 'w') as f:
                f.write(nic_config)
        except KeyError:
            print('No NIC with MAC {}. Skipping..'.format(nic['Mac']))
    # print('Restart networking')
    # run('systemctl restart systemd-networkd')
else:
    print('Generating /etc/network/interfaces')
    content = '''auto lo
iface lo inet loopback
'''

    main_ip = True
    for nic in cloud_config['NIC']:
        try:
            name = interfaces[nic['Mac'].lower()]
            nic_config = '\n\nauto {}'.format(name)
            for ip in nic['Ip']:
                interface = ipaddress.ip_interface(ip)
                nic_config += '''
iface {name} inet static
    address {address}
    netmask {netmask}'''.format(name=name,
                                address=interface.ip,
                                netmask=interface.netmask)
                               # network=interface.network.network_address,
                               # broadcast=interface.network.broadcast_address)

                if nic.get('Gw') and main_ip:
                    main_ip = False
                    nic_config += '''
    gateway {gw}
    dns-nameservers {nameservers}
    dns-search {dns_search_list}
'''.format(gw=nic['Gw'],
           nameservers=' '.join(cloud_config['DNS']['Servers']),
           dns_search_list=' '.join(dns_search_list))

                    update_hosts(str(interface.ip))

            content += nic_config
        except KeyError:
            print('No NIC with MAC {}. Skipping..'.format(nic['Mac']))

    content += '\n'
    print('Updating /etc/network/interfaces')
    with open('/etc/network/interfaces', 'w') as f:
        f.write(content)

    # print('Restart networking')
    # run('ip address flush scope global')
    # run('systemctl restart networking')