from tools import run
import os
import crypt
import grp
import pwd
import base64

# cloud_config = {}

# groups = run('groups', fail=True)
groups = [g.gr_name for g in grp.getgrall()]
users = [p.pw_name for p in pwd.getpwall()]

for user in cloud_config.get('Users'):
    for group in user.get('Groups'):
        # if group not in groups.stdout.split():
        if group not in groups:
            groupadd_cmd = 'groupadd '
            if user.get('System'):
                groupadd_cmd += '--system '
            print('Creating missing group: ' + group)
            run(groupadd_cmd + group, fail=True)

    if user not in users:
        adduser_cmd = 'adduser --disabled-password --gecos "" '
        if user.get('System'):
            adduser_cmd += '--system '
        print('Creating user ' + user['Name'])
        run(adduser_cmd + user['Name'], fail=True)

    for group in user.get('Groups'):
        print('Adding user to group ' + group)
        run('adduser {} {}'.format(user['Name'], group))

    if user.get('Password'):
        print('Setting password')
        encrypted = base64.b64decode('\n'.join(user['Password']))
        openssl_decrypt = run('openssl rsautl -inkey {}/private.pem -decrypt'.format(WORKING_DIR), stdin=encrypted, suppress_output=True)
        decrypted_pass = openssl_decrypt.stdout.decode('utf-8').rstrip()
        salt = crypt.mksalt(crypt.METHOD_SHA512)
        password = crypt.crypt(decrypted_pass, salt)
        run('usermod --password {} {}'.format(password, user['Name']), fail=True)

    if user.get('SshKey'):
        print('Adding SSH key')
        keys_path = os.path.expanduser('~{}/.ssh'.format(user['Name']))
        os.makedirs(keys_path, exist_ok=True)
        with open('{}/authorized_keys'.format(keys_path), 'a') as f:
            f.write('\n'.join(user['SshKey']))

    if user.get('Sudo'):
        print('Adding sudoers config')
        os.makedirs('/etc/sudoers.d/', exist_ok=True)
        with open('/etc/sudoers.d/{}'.format(user['Name']), 'w') as sudoers:
            sudoers.write('{} {}'.format(user['Name'], user['Sudo']))