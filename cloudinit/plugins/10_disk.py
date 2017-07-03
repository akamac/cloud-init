# cloud_config = {}
from tools import run

import os
import glob
import sys
import time

DEFAULT_FILE_SYSTEM = 'ext4'

vm_disks = []
for scsi_disk in os.listdir('/sys/class/scsi_disk/'):
    device = os.listdir('/sys/class/scsi_disk/{}/device/block'.format(scsi_disk))[0]
    vm_disks.append((scsi_disk, device))
vm_disks.sort(key=lambda x: x[0])

config_disks = sorted(cloud_config['HDD'], key=lambda x: x['DeviceNode'])

for vm_disk, config_disk in zip(vm_disks, config_disks):
    scsi_disk, device = vm_disk
    mount_point = config_disk.get('MountPoint')
    if not mount_point:
        print('No mount point specified for {}. Skipping formatting..'.format(config_disk['DeviceNode']))
        continue

    if glob.glob('/sys/class/scsi_disk/{0}/device/block/{1}/{1}*'.format(*vm_disk)):
        print('Disk {} contains partitions. Skipping..'.format(config_disk['DeviceNode']))
    else:
        print('Creating partition on /dev/{}'.format(device))
        run('parted --script /dev/{} mklabel gpt mkpart primary 2048KiB 100%'.format(device), fail=True)
        time.sleep(1)

        file_system = config_disk.get('FileSystem', DEFAULT_FILE_SYSTEM)
        label = config_disk.get('Label', os.path.basename(mount_point))

        print('Creating and mounting file system on partition /dev/{}1'.format(device))
        if file_system == 'ext4':
            # if config_disk.get('LVM'):
            # run('mkfs.ext4 -L {0} /dev/{1}/{2}'.format(label, vg_name, lv_name), fail=True)
            # else:
            run('mkfs.ext4 -L {0} /dev/{1}1'.format(label, device), fail=True)
        else:
            sys.exit('Not supported file system')

        print('Adding {} to fstab'.format(label))
        os.makedirs(mount_point, exist_ok=True)
        with open('/etc/fstab', 'a') as fstab:
            fstab.write('\nLABEL={0}  {1}  {2}  defaults  0  0\n'.format(label, config_disk['MountPoint'], file_system))

        print('Mounting {}'.format(label))
        run('mount -a', fail=True)
