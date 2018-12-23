#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from python_terraform import *
import os
import subprocess
import requests
import httplib2
import requests
from configparser import ConfigParser

from bs4 import BeautifulSoup
import requests

html = requests.get('http://www.jianshu.com/').content
soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
rst = soup('script')

cfg = ConfigParser()
cfg.read(html)

print(cfg.sections())

