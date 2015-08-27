#!/usr/bin/env python
from __future__ import print_function
from argparse import ArgumentParser
import logging

from stevedore import extension


def load_providers():
    logging.debug('Loading distro provider extensions')
    mgr = extension.ExtensionManager(
        namespace='chrooter.provider',
    )
    distros = {}
    for ext in mgr:
        distros[ext.name] = ext.plugin()
        logging.debug(
            'Logging extension %s for distro %s'
            % (ext.name, ext.plugin.__name__)
        )
    return distros


def get_parser(providers):
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(
        title='distro',
        description='Distribution to create the chroot for',
        dest='distro',
    )
    for provider_name, provider in providers.items():
        subparser = subparsers.add_parser(provider_name)
        provider.populate_parser(subparser)
    if not providers:
        raise Exception('Unable to load any distro providers')
    return parser


def main():
    logging.basicConfig(level=logging.INFO)
    providers = load_providers()
    parser = get_parser(providers)
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
    )
    parser.add_argument(
        '-s',
        '--execute-script',
        dest='script',
        action='append',
        help=(
            'Script ot run, can be specified more than once. Currently only '
            'scripts under the current dir are supported.'
        ),
    )
    parser.add_argument(
        '-S',
        '--shell',
        action='store_true',
        help=(
            'Run an interactive shell, if ant script is specified, the '
            'shell will be started after the script run'
        ),
    )
    args = parser.parse_args()
    if args.verbose:
        logging.root.setLevel(level=logging.DEBUG)
    providers[args.distro].run(
        args,
        scripts=args.script,
        interactive=args.shell,
    )
