from setux.core.action import Actions, Action
from setux.actions.user import User_
from setux.actions.transfer import Sender


class Sudoer(Action):
    '''Add User to sudoers

    context:
        user : user name
    '''

    @property
    def label(self):
        return f'Sudoer {self.user}'

    def check(self):
        grp = self.target.groups.fetch(self.user)
        ok = 'wheel' in grp.get()

        ret, out, err = self.target.run(f'sudo -l -U {self.user}')
        ok = ok and '(ALL) NOPASSWD: ALL' in (line.strip() for line in out)
        return ok

    def deploy(self):
        grp = self.target.groups.fetch(self.user)
        grp.add('wheel')

        ok = self.target.write(
            f'/etc/sudoers.d/{self.user}',
            f'{self.user} ALL=(ALL) NOPASSWD: ALL',
        )
        return ok


class CopyId(Action):
    '''Send Public Key to Target
    context:
        user : User name
        pub  : Public key
    '''

    @property
    def label(self):
        return f'Copy ID {self.user}'

    def check(self):
        if not getattr(self, 'pub', None): return True

        user = self.target.user.fetch(self.user)
        if user.check() is not True: return False

        pub = self.local.file(self.pub, verbose=False)
        if pub.size == 0:
            raise SystemExit(f' ! {pub.key} is empty')

        path = f'/home/{self.user}/.ssh/authorized_keys'
        autorized = self.target.file.fetch(
            path, mode='600', user=self.user, group=user.group.name
        )
        ok = autorized.check() is True and autorized.size != 0

        if ok:
            ok = autorized.hash == pub.hash

        return ok

    def deploy(self):
        user = self.target.user.fetch(self.user)
        pub = self.local.file(self.pub, verbose=False)
        if pub.size == 0:
            raise SystemExit(f' ! {pub.key} is empty')

        path = f'/home/{self.user}/.ssh'
        ssh = self.target.dir(
            path, mode='700', user=self.user, group=user.group.name
        )
        if ssh.check() is not True: return False

        full = f'{path}/authorized_keys'
        self.target.run('rm -f {full}', sudo='root')
        sent = Sender(self.target, src=self.pub, dst=full, **self.context)()
        if sent is not True: return False

        key = self.target.file(
            full, mode='600', user=self.user, group=user.group.name
        )
        return key.check() is True and key.size > 0


class Admin(Actions):
    '''Set User as sudoer
    context:
        user : User name
        pub  : Public key

    - Create User if not present
    - Add User to sudoers
    - Send User's public key
    '''

    @property
    def label(self):
        return f'Admin {self.user}'

    @property
    def actions(self):
        return [
            User_,
            Sudoer,
            CopyId,
        ]

