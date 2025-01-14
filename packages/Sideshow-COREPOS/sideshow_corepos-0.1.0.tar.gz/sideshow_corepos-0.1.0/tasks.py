# -*- coding: utf-8; -*-
"""
Tasks for Sideshow-COREPOS
"""

import os
import shutil

from invoke import task


@task
def release(c, skip_tests=False):
    """
    Release a new version of Sideshow-COREPOS
    """
    if not skip_tests:
        c.run('pytest')

    # rebuild pkg
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('Sideshow_COREPOS.egg-info'):
        shutil.rmtree('Sideshow_COREPOS.egg-info')
    c.run('python -m build --sdist')

    # upload
    c.run('twine upload dist/*')
