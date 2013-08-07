#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python ZIP Generator
Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

generator_python_zip.py: Generator for Python ZIP

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation; either version 2 
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

import sys
import os
import shutil
import subprocess
import re

sys.path.append(os.path.split(os.getcwd())[0])
import common
from python_released_files import released_files

device = None

def copy_examples_for_zip():
    if not device.is_released():
        return

    examples = common.find_examples(device, common.path_binding, 'python', 'example_', '.py')
    dest = os.path.join('/tmp/generator/egg/examples/', 
                        device.get_category().lower(),
                        device.get_underscore_name())

    if not os.path.exists(dest):
        os.makedirs(dest)

    for example in examples:
        shutil.copy(example[1], dest)
  
def make_files(device_, directory):
    global device
    device = device_

    copy_examples_for_zip()

def generate(path):
    # Make temporary generator directory
    if os.path.exists('/tmp/generator'):
        shutil.rmtree('/tmp/generator/')
    os.makedirs('/tmp/generator/egg/source/tinkerforge')
    os.chdir('/tmp/generator')

    # Copy examples
    common.generate(path, 'en', make_files, None, None, False)
    shutil.copy(common.path_binding.replace('/generators/python', '/doc/en/source/Software/example.py'),
                '/tmp/generator/egg/examples/example_enumerate.py')

    # Copy bindings and readme
    for filename in released_files:
        shutil.copy(os.path.join(path, 'bindings', filename), '/tmp/generator/egg/source/tinkerforge')

    shutil.copy(path + '/ip_connection.py', '/tmp/generator/egg/source/tinkerforge')
    shutil.copy(path + '/changelog.txt', '/tmp/generator/egg')
    shutil.copy(path + '/readme.txt', '/tmp/generator/egg')

    # Write setup.py
    version = common.get_changelog_version(path)
    file('/tmp/generator/egg/source/setup.py', 'wb').write("""
#!/usr/bin/env python

from setuptools import setup

setup(name='tinkerforge',
      version='{0}.{1}.{2}',
      description='TCP/IP based library for Bricks and Bricklets',
      author='Tinkerforge GmbH',
      author_email='olaf@tinkerforge.com',
      url='http://www.tinkerforge.com',
      packages=['tinkerforge'])
""".format(*version))

    # Make egg
    os.chdir('/tmp/generator/egg/source')
    args = ['/usr/bin/python',
            'setup.py',
            'bdist_egg']
    if subprocess.call(args) != 0:
        raise Exception("Command '{0}' failed".format(' '.join(args)))

    # Remove build stuff
    shutil.rmtree('/tmp/generator/egg/source/build')
    shutil.rmtree('/tmp/generator/egg/source/tinkerforge.egg-info')
    shutil.copy('/tmp/generator/egg/source/dist/' + 
                os.listdir('/tmp/generator/egg/source/dist')[0], 
                '/tmp/generator/egg/tinkerforge.egg')
    shutil.rmtree('/tmp/generator/egg/source/dist')

    # Make __init__.py
    f = open('/tmp/generator/egg/source/tinkerforge/__init__.py', 'w')
    f.write(' ')
    f.close()

    # Make zip
    common.make_zip('python', '/tmp/generator/egg', path, version)

if __name__ == "__main__":
    generate(os.getcwd())
