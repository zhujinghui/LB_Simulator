#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import zipfile
import os


def zipdir(path, test_id):
    zipf = zipfile.ZipFile(test_id + '.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        if root != "./":  # get rid of other dirs
            continue
        for file in files:
            if file.split('.')[1] == 'zip' or file.startswith("."):  # get rid of hidden files and zip itself
                continue
            zipf.write(os.path.join(root, file))
    zipf.close()
