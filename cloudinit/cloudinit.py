#!/usr/bin/env python3

import os
import json
import sys
from glob import glob
import shutil
import runpy
import argparse

from .plugins.tools import run

WORKING_DIR = '/var/lib/cloud-init'


def main():
    os.makedirs(WORKING_DIR, exist_ok=True)
    state_path = os.path.join(WORKING_DIR, 'state')

    parser = argparse.ArgumentParser(description='framework for early Ubuntu/Debian guest initialization')
    parser.add_argument('--set-state', type=int, help='set current execution step')
    args = parser.parse_args()

    if args.__contains__('set_state'):
        with open(state_path, 'w') as state:
            state.write(args.set_state)
        return

    print('Starting cloud-init')

    found = False
    print('Searching for cloud-config.json on cd')
    blkid = run('blkid /dev/cdrom')
    if blkid.stdout:
        mount = run('mount /dev/cdrom /media/cdrom')
        if mount.returncode == 0:
            try:
                with open('/media/cdrom/cloud-config.json', encoding='utf-8-sig') as f:
                    cloud_config = json.loads(f.read())
                # remove passwords before dumping to disk
                shutil.copy('/media/cdrom/cloud-config.json', os.path.join(WORKING_DIR, '_cloud-config.json'))
                run('eject -v')
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
    plugins = glob(plugins_dir + '/[0-9][0-9]_[a-z]*.py')
    for plugin in sorted(plugins):
        plugin_name = os.path.basename(plugin).rstrip('.py')
        plugin_order = int(plugin_name.split('_')[0])
        if plugin_order > state:
            try:
                print('Running ' + plugin_name)
                res = runpy.run_path(plugin, init_globals={'cloud_config': cloud_config,
                                                           'WORKING_DIR': WORKING_DIR})
            except:
                sys.exit('Error occured while running plugin {}'.format(plugin_name))

            with open(state_path, 'w') as f:
                f.write(plugin_order)
            if res['reboot']:
                print('Plugin {} requested reboot'.format(plugin_name))
                run('systemctl reboot --message="cloud-init restart"')
                sys.exit()

    print('Disabling cloud-init')
    run('systemctl disable cloud-init')


if __name__ == '__main__':
    main()
