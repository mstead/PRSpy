#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def find_files(in_dir):
    return [os.path.join(in_dir, f) for f in os.listdir(in_dir)]

setup(
	name = 'prspy',
	version = '0.1',
	description = 'GitHub pull request monitor',
	author = 'Michael Stead',
	author_email = 'michael.stead@gmail.com',
	url = 'bugsquat.net',
	license = 'GPLLv2+',
	package_dir={
		'prspy':'src/prspy',
	},
	packages=find_packages('src'),
	include_package_data=True,
        data_files=[('prspy/gui/data', find_files("src/prspy/gui/data")),
                    ('prspy/gui/img', find_files('src/prspy/gui/img')),
                    ('/usr/share/applications', find_files("desktop")),
                    ('/usr/share/icons/', ['prspy.png'])],
	scripts = [
		'bin/prspy',
	],

	classifiers=[
        	'License :: OSI Approved :: GNU General Public License (GPL)',
        	'Development Status :: 0.1',
        	'Environment :: GUI',
        	'Intended Audience :: Developers',
        	'Intended Audience :: Information Technology',
        	'Programming Language :: Python'
    	],
)
