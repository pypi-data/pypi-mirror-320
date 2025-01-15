"""
TPass
"""
__version__ = '1.0b4'

import os
import sys
import subprocess
import tomlkit
import readline
from chacha import get_passphrase, ChaChaContext
from .totp import TOTPGenerator

class TPass:
    def __init__(self):
        if sys.platform == 'win32':
            home = os.environ['USERPROFILE']
        else:
            home = os.environ['HOME']
        self.filename = filename = os.path.join(home, '.accounts.cha')
        if not os.path.exists(filename):
            print('The encrypted credentials file does not exist.')
            print('Use the tpass-setup command to initialize it.')
        self.context = ChaChaContext(get_passphrase())
        decrypted = self.context.decrypt_file_to_bytes(filename)
        self.data = tomlkit.loads(decrypted.decode('utf-8'))

    def save(self):
        plaintext = tomlkit.dumps(self.data).encode('utf-8')
        self.context.encrypt_file_from_bytes(plaintext, self.filename)

    def add_account(self, account):
        """
        Add a new table to the toml document, ensuring that the
        required keys exist.
        """
        new_account = tomlkit.table()
        print('Creating a new account named', account)
        print('The domain, userid and password fields are required.')
        domain = input('domain: ')
        if not domain:
            print('Aborting.')
            return
        new_account.add('domain', domain)
        userid = input('userid: ')
        if not userid:
            print('Aborting.')
            return
        new_account.add('userid', userid)
        password = input('password: ')
        if not password:
            print('Aborting.')
            return
        new_account.add('password', password)
        self.data[account] = new_account
        self.save()

usage = """Usage: tpass <account>
The userid for the specified account is printed and the password is
copied to the clipboard.

To initialize an encrypted credentials file, or to change the pass
phrase on an existing credentials file, use the tpass-setup command.

To edit data in the encrypted credentials file, use the tpass-edit
command.
"""

if sys.platform == 'darwin':
        def copy_as_clip(text):
            result = subprocess.run([
                'defaults', '-currentHost', 'read',
                'com.apple.coreservices.useractivityd',
                'ActivityAdvertisingAllowed', '-bool'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            advertising_allowed = (result.stdout == 'on')
            result = subprocess.run([
                'defaults', '-currentHost', 'read',
                'com.apple.coreservices.useractivityd',
                'ActivityReceivingAllowed', '-bool'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            receiving_allowed = (result.stdout == 'on')
            if advertising_allowed:
                subprocess.call([
                    'defaults', '-currentHost', 'write',
                    'com.apple.coreservices.useractivityd',
                    'ActivityAdvertisingAllowed', '-bool', 'no'])
            if receiving_allowed:
                subprocess.call([
                    'defaults', '-currentHost', 'write',
                    'com.apple.coreservices.useractivityd',
                    'ActivityReceivingAllowed', '-bool', 'no'])
            proc = subprocess.Popen(['/usr/bin/pbcopy'], stdin=subprocess.PIPE)
            proc.communicate(text.encode('utf-8'))
            if advertising_allowed:
                subprocess.call([
                    'defaults', '-currentHost', 'write',
                    'com.apple.coreservices.useractivityd',
                    'ActivityAdvertisingAllowed', '-bool', 'yes'])
            if receiving_allowed:
                subprocess.call([
                    'defaults', '-currentHost', 'write',
                    'com.apple.coreservices.useractivityd',
                    'ActivityReceivingAllowed', '-bool', 'yes'])
else:
    if sys.platform == 'linux':
        if "WAYLAND_DISPLAY" in os.environ:
            clip_commands = [['/usr/bin/wl-copy', '-p'], ['/usr/bin/wl-copy']]
        elif "DISPLAY" in os.environ:
            clip_commands = [['/usr/bin/xsel', '-p', '-c']]
        else:
            print("An X11 or Wayland server is required to use the clipboard.")
    else:
        clip_commands = ['clip']
    def copy_as_clip(text):
        for command in clip_commands:
            proc = subprocess.Popen(command, stdin=subprocess.PIPE)
            proc.communicate(text.encode('utf-8'))
        
def main():
    nargs = len(sys.argv)
    if nargs != 2 or nargs == 2 and sys.argv[1] in ('-h', '-help'):
        print(usage)
        sys.exit(1) 
    tpass = TPass()
    account_name = sys.argv[1]
    if account_name in tpass.data:
        account = tpass.data[sys.argv[1]]
        print('userid:', account['userid'])
        copy_as_clip(account['password'])
        print('The password has been copied to your clipboard.')
        if 'totp_key' in account:
            key = account['totp_key'].encode('utf-8')
            generator = TOTPGenerator(key)
            generator()
    else:
        print("Unknown account:", account_name)
        answer = input(
            'Type yes to view known accounts, <Enter> to quit ')
        if answer == 'yes':
            for name in sorted(tpass.data.keys()):
                print(name)
