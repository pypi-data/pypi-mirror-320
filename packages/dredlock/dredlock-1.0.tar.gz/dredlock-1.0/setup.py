#!/usr/bin/python3

# -*- coding: utf-8 -*-

import re, os
from setuptools import setup, find_packages
import datetime

url = 'https://github.com/krezreb/dredlock'

md_regex = r"\[([^\[]+)\](\(.*\))"

with open("../README.md", "r") as fh:
    long_description = fh.read()


# convert links in readme to absolute paths
matches = re.finditer(md_regex, long_description, re.MULTILINE)

for matchNum, match in enumerate(matches, start=1):
    replace = '(' + url + '/blob/master/' + match.groups(1)[1][1:-1] + ')'
    long_description = long_description.replace(match.groups(1)[1], replace)


with open("requirements.txt", "r") as fh:
    install_requires = fh.readlines()

release_version=os.getenv("DREDLOCK_RELEASE", "999.dev")

build_date = datetime.date.today().strftime('%Y-%m-%d')

setup(name='dredlock',
    version=release_version,
    description='A python implementation of redlock, with examples',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    author='krezreb',
    keywords="build_date:{}".format(build_date),
    author_email='josephbeeson@gmail.com',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires

)


