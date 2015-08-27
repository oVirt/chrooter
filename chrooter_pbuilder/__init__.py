#!/bin/env python
from __future__ import print_function

import logging
import os
import sys

from chrooter.provider import Provider
from chrooter.utils import (
    call,
    timed,
)


LOGGER = logging.getLogger(__name__)
ROOT_UID = 0


class PbuilderEnv(object):
    def __init__(self, distro):
        self.rootdir = os.path.realpath(
            os.path.join(os.curdir, 'pdbuilder_root')
        )
        self.aptcachedir = os.path.join(
            self.rootdir,
            'apt-cache',
        )
        self.basetgz = os.path.join(
            self.rootdir,
            distro + '.base.tgz',
        )
        self.command = [
            'pbuilder',
        ]
        self.extra_options = [
            '--buildplace', self.rootdir,
            '--aptcache', self.rootdir,
            '--basetgz', self.basetgz,
        ]
        if distro.startswith('deb-'):
            distro = distro[4:]
        self.distro = distro
        if not os.path.exists(self.rootdir):
            os.makedirs(self.rootdir)

    def start_interactive_shell(self):
        command = list(self.command)
        command.append('--login')
        command.extend(self.extra_options)
        return call(command)

    @timed(logger_name=__name__ + '.execute_script')
    def execute_script(self, script):
        if os.path.exists(self.basetgz):
            self.update()
        else:
            self.create()
        command = list(self.command)
        command.append(
            '--execute',
        )
        command.extend(self.extra_options)
        command.extend((
            '--',
            script,

        ))
        return call(command)

    def create(self, extra_packages=None):
        command = list(self.command)
        if extra_packages:
            command.append((
                '--extrapackages',
                ','.join(extra_packages)
            ))
        command.extend((
            '--create',
            '--distribution', self.distro,
        ))
        command.extend(self.extra_options)
        return call(command)

    def update(self):
        command = list(self.command)
        command.extend((
            '--update',
            '--distribution', self.distro,
        ))
        command.extend(self.extra_options)
        return call(command)


class PbuilderProvider(Provider):
    def run(self, args, scripts=None, interactive=False):
        if os.geteuid() != ROOT_UID:
            logging.error("You need to be root to run pbuilder")
            sys.exit(2)
        rc = 0
        pbuilder_env = PbuilderEnv(distro=args.distro)
        for script in scripts:
            rc = pbuilder_env.execute_script(script)
            if rc != 0:
                sys.exit(rc)
        if interactive:
            rc = pbuilder_env.start_interactive_shell()
        sys.exit(rc)

    def populate_parser(self, parser):
        parser.add_argument(
            '--extra-package',
            action='append',
            help='Also install the given package when creating the chroot'
        )
