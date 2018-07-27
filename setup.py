#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
RESTful endpoints for createing/showing/deleting a user's Jumpbox in vLab
"""
from setuptools import setup, find_packages


setup(name="vlab-jumpbox-api",
      author="Nicholas Willhite,",
      author_email='willnx84@gmail.com',
      version='2018.07.25',
      packages=find_packages(),
      include_package_data=True,
      package_files={'vlab_jumpbox_api' : ['app.ini']},
      description="Create/delete a Jumpbox for connecting to your virtual lab",
      install_requires=['flask', 'ldap3', 'pyjwt', 'uwsgi', 'vlab-api-common',
                        'ujson', 'cryptography', 'vlab-inf-common', 'celery']
      )
