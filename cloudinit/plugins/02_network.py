# cloud_config = {}
from tools import run

import os
import ipaddress
import re

dns_search_list = [cloud_config['Domain']['Name']]
dns_search_list.extend(cloud_config['DNS'].get('DomainSearch', []))
print('DNS search list: {}'.format(dns_search_list))

print('Reading interfaces from /sys/class/net/')
interfaces = {}
for interface in os.listdir('/sys/class/net/'):
    with open('/sys/class/net/{}/address'.format(interface)) as f:
        mac = f.read().rstrip('\n')
        interfaces.update({mac: interface})

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

                fqdn = os.uname().nodename
                hostname = fqdn.split('.')[0]
                with open('/etc/hosts') as f:
                    hosts_content = f.read()
                    pattern = r'[0-9.]{{7,15}}(\s+{}\s+{})'.format(fqdn, hostname)
                    hosts_content = re.sub(pattern, str(interface.ip) + r'\1', hosts_content)
                print('Updating /etc/hosts')
                with open('/etc/hosts', 'w') as f:
                    f.write(hosts_content)

        content += nic_config
    except KeyError:
        print('No NIC with MAC {}. Skipping..'.format(nic['Mac']))

content += '\n'
print('Updating /etc/network/interfaces')
with open('/etc/network/interfaces', 'w') as f:
    f.write(content)

print('Restart networking')
run('ip address flush scope global')
run('systemctl restart networking')