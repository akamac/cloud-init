# cloud_config
from tools import run

import os
import glob

print('Deleting host SSH keys')
map(os.remove, glob.glob('/etc/ssh/ssh_host_*'))
print('Reconfiguring openssh-server')
run('dpkg-reconfigure openssh-server')