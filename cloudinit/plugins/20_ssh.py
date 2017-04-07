# cloud_config
from .tools import run

import os
import glob

map(os.remove, glob.glob('/etc/ssh/ssh_host_*'))
run('dpkg-reconfigure openssh-server')