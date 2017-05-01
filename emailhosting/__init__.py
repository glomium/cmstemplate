#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import absolute_import
from __future__ import unicode_literals


VERSION = ((0, 1, 0), ('a', 0))


def get_version(dev=True):
    """
    return a version number consistent with PEP386
    """
    assert len(VERSION) == 2
    assert VERSION[1][0] in ('a', 'b', 'rc', 'final')

    version = '.'.join(map(str, VERSION[0]))

    if VERSION[1][0] == "final":  # pragma: no cover
        return version

    version += VERSION[1][0] + str(VERSION[1][1])

    if VERSION[1][1] == 0 and dev:
        import os
        import subprocess
        import datetime

        # get version information from git
        repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        get_time = subprocess.Popen(
            'git log --pretty=format:%ct --quiet -1 HEAD',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd=repo_dir,
            universal_newlines=True,
        )

        timestamp = get_time.communicate()[0]
        try:
            timestamp = datetime.datetime.utcfromtimestamp(int(timestamp))
            version += '.dev%s' % timestamp.strftime('%Y%m%d%H%M%S')
        except ValueError:  # pragma: no cover
            pass

    return version

__version__ = get_version(dev=False)
__docformat__ = 'restructuredtext'

default_app_config = 'emailhosting.apps.HostingConfig'
