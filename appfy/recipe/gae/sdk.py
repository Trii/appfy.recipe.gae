# -*- coding: utf-8 -*-
"""
appfy.recipe.gae:sdk
--------------------

Downloads and installs the App Engine SDK in the buildout directory.

Options
~~~~~~~

:url: URL to the App Engine SDK file. Default is to download the latest version
    from storage.googleapis.com.
:destination: Destination of the extracted SDK. Default is the parts directory.
:clear-destination: If `true`, deletes the destination dir before
    extracting the download. Default is `true`.

Example
~~~~~~~

::

  [gae_sdk]
  # Downloads and extracts the App Engine SDK.
  recipe = appfy.recipe.gae:sdk
  # Omit `url` to always use the latest from https://appengine.google.com/api/updatecheck
  url = http://googleappengine.googlecode.com/files/google_appengine_1.9.11.zip
  destination = ${buildout:parts-directory}
  hash-name = false
  clear-destination = true
"""
import logging
import os
import urllib2

import yaml

from appfy.recipe import download


class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"


class SDKCouldNotBeFound(Exception):
    pass


class Recipe(download.Recipe):

    URL = "https://appengine.google.com/api/updatecheck"
    PYTHON_SDK_URL_TPL = "https://storage.googleapis.com/appengine-sdks/featured/google_appengine_{version}.zip"

    def __init__(self, buildout, name, options):
        self.logger = logging.getLogger(name)

        parts_dir = os.path.abspath(buildout['buildout']['parts-directory'])
        options.setdefault('destination', parts_dir)
        options.setdefault('clear-destination', 'true')

        super(Recipe, self).__init__(buildout, name, options)

    def install(self):
        if not self.option_url:
            self.option_url = self.find_latest_sdk_url()
        self.logger.info('Using SDK version found at %s', self.option_url)
        return super(Recipe, self).install()

    def find_latest_sdk_url(self):
        update_check_yaml = urllib2.urlopen(self.URL).read()
        try:
            update_check = yaml.load(update_check_yaml)
        except yaml.YAMLError:
            raise SDKCouldNotBeFound('Invalid yaml from {}'.format(self.URL))

        if 'release' not in update_check:
            raise SDKCouldNotBeFound(
                'Could not find a usable SDK version automatically'
            )

        return self.PYTHON_SDK_URL_TPL.format(version=update_check['release'])
