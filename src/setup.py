"""
Script for building a distributable OS X app.

Usage:
    python setup.py py2app
"""
from distutils.core import setup
import py2app

setup(
    name="iTunes-Discogs",
    app=["main.py"],
)
