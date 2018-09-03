from tools import run
import os
import shutil
import crypt
import grp
import pwd
import base64

# cloud_config = {}

# groups = run('groups', fail=True)
groups = [g.gr_name for g in grp.getgrall()]
users = [p.pw_name for p in pwd.getpwall()]

for user in cloud_config.get('Users', []):
    for group in user.get('Groups', []):
        # if group not in groups.stdout.split():
        if group not in groups:
            groupadd_cmd = 'groupadd '
            if user.get('System'):
                groupadd_cmd += '--system '
            print('Creating missing group: {}'.format(group))
            run(groupadd_cmd + group, fail=True)

    if user['Name'] not in users:
        adduser_cmd = 'adduser --disabled-password --gecos "" '
        if user.get('System'):
            adduser_cmd += '--system '
        print('Creating user {}'.format(user['Name']))
        run(adduser_cmd + user['Name'], fail=True)

    for group in user.get('Groups', []):
        print('Adding user to group {}'.format(group))
        run('adduser {} {}'.format(user['Name'], group))

    if user.get('Password'):
        print('Setting password')
        submitted_password = ''.join(user['Password']) if isinstance(user['Password'], list) else user['Password']
        encrypted = base64.b64decode(submitted_password)
        openssl_decrypt = run('openssl rsautl -inkey {}/private.pem -decrypt'.format(WORKING_DIR), stdin=encrypted, suppress_output=True)
        decrypted_pass = openssl_decrypt.stdout.decode().rstrip()
        salt = crypt.mksalt(crypt.METHOD_SHA512)
        password = crypt.crypt(decrypted_pass, salt)
        run('usermod --password {} {}'.format(password, user['Name']), fail=True)

    if user.get('SshKey'):
        print('Adding SSH key')
        home_path = os.path.expanduser('~{}'.format(user['Name']))
        keys_path = '{}/.ssh'.format(home_path)
        os.makedirs(keys_path, mode=0o755, exist_ok=True)
        for directory in home_path, keys_path:
            shutil.chown(directory, user=user['Name'], group=user['Name'])
        ssh_key = ''.join(user['SshKey']) if isinstance(user['SshKey'], list) else user['SshKey']
        authorized_keys_path = '{}/authorized_keys'.format(keys_path)
        with open(authorized_keys_path, 'a') as f:
            f.write(ssh_key)
        os.chmod(authorized_keys_path, 0o644)
        shutil.chown(authorized_keys_path, user=user['Name'], group=user['Name'])

    if user.get('Sudo'):
        print('Adding sudoers config')
        os.makedirs('/etc/sudoers.d/', mode=0o750, exist_ok=True)
        with open('/etc/sudoers.d/{}'.format(user['Name']), 'w') as sudoers:
            sudoers.write('{} {}'.format(user['Name'], user['Sudo']))
        os.chmod('/etc/sudoers.d/{}'.format(user['Name']), 0o440)