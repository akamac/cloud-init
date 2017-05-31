# cloud_config = {}
from tools import run

import os
import re


hostname = cloud_config['HostName'].lower()
domain = cloud_config['Domain']['Name']
fqdn = '.'.join([hostname, domain])

old_fqdn = os.uname().nodename
old_hostname = old_fqdn.split('.')[0]

if fqdn != old_fqdn:
    print('Setting fqdn ' + fqdn)
    run('hostnamectl set-hostname ' + fqdn)
    print('Updating /etc/hosts')
    with open('/etc/hosts') as f:
        content = f.read()
        pattern = r'{0}\s+{1}'.format(old_fqdn, old_hostname)
        content = re.sub(pattern, ' '.join([fqdn, hostname]), content)
    with open('/etc/hosts', 'w') as f:
        f.write(content)