#!/usr/bin/env python3

import os
import json
import sys
from glob import glob
import shutil
import runpy
import argparse
from pkg_resources import get_distribution

from .plugins.tools import run

WORKING_DIR = '/usr/lib/cloud-init'
# __version__ = get_distribution('cloudinit').version


def main():
    os.makedirs(WORKING_DIR, exist_ok=True)
    state_path = os.path.join(WORKING_DIR, 'state')

    parser = argparse.ArgumentParser(description='framework for early Ubuntu/Debian guest initialization')
    parser.add_argument('--set-state', type=int, help='set current execution step')
    parser.add_argument('--version', action='store_true', help='print version')
    args = parser.parse_args()

    if args.version:
        print(get_distribution('cloudinit').version)
        return

    if args.set_state is not None:
        with open(state_path, 'w') as state:
            state.write(str(args.set_state))
        return

    print('Starting cloud-init')

    found = False
    print('Searching for cloud-config.json on cd')
    blkid = run('blkid /dev/cdrom')
    if blkid.stdout:
        os.makedirs('/media/cdrom', mode=0o755, exist_ok=True)
        mount = run('mount /dev/cdrom /media/cdrom')
        if mount.returncode == 0:
            try:
                with open('/media/cdrom/cloud-config.json', encoding='utf-8-sig') as f:
                    cloud_config = json.loads(f.read())
                # remove passwords before dumping to disk
                shutil.copy('/media/cdrom/cloud-config.json', os.path.join(WORKING_DIR, '_cloud-config.json'))
                run('eject')
                found = True
            except:
                run('umount /media/cdrom')

    print('Searching for cloud-config.json on local drive')
    file_path = os.path.join(WORKING_DIR, 'cloud-config.json')
    if os.path.isfile(file_path):
        with open(file_path, encoding='utf-8-sig') as f:
            try:
                cloud_config = json.loads(f.read())
            except:
                sys.exit('Error loading json')
            found = True

    if not found:
        sys.exit('No config source found')

    print('Reading state file')

    if os.path.isfile(state_path):
        try:
            with open(state_path) as f:
                state = int(f.read())
        except:
            sys.exit('Invalid state file content')
    else:
        state = 0
    print('State is {}'.format(state))

    print('Running plugins')
    plugins_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'plugins')
    sys.path.insert(0, plugins_dir)
    plugins = glob(plugins_dir + '/[0-9][0-9]_[a-z]*.py')
    for plugin in sorted(plugins):
        plugin_name = os.path.basename(plugin)[:-3]
        plugin_order = int(plugin_name.split('_')[0])
        if plugin_order > state:
            try:
                print('Running {} plugin'.format(plugin_name))
                res = runpy.run_path(plugin, init_globals={'cloud_config': cloud_config,
                                                           'WORKING_DIR': WORKING_DIR})
            except:
                sys.exit('Error occured while running plugin {}'.format(plugin_name))

            with open(state_path, 'w') as f:
                f.write(str(plugin_order))
            if res.get('reboot'):
                print('Plugin {} requested reboot'.format(plugin_name))
                run('systemctl reboot --message="cloud-init restart"')
                sys.exit()

    sys.path.remove(plugins_dir)
    print('Disabling cloud-init')
    run('systemctl disable cloud-init')


if __name__ == '__main__':
    main()
