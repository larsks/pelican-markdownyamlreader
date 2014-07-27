#!/usr/bin/python

import setuptools

setuptools.setup(
    install_requires=open('requires.txt').readlines(),
    version = 2,
    name = 'markdownyamlreader',
    py_modules = ['markdownyamlreader'],
)

