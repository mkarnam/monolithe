# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Alcatel-Lucent Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its contributors
#       may be used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import shutil
from collections import OrderedDict
from ConfigParser import RawConfigParser

from monolithe.lib import SDKUtils
from monolithe.generators.lib import TemplateFileWriter


class _GoSDKAPIVersionFileWriter(TemplateFileWriter):
    """ Provide usefull method to write Go files.

    """
    def __init__(self, monolithe_config, api_info):
        """ Initializes a _GoSDKAPIVersionFileWriter

        """
        super(_GoSDKAPIVersionFileWriter, self).__init__(package="monolithe.generators.sdk.go")

        self.api_version = api_info["version"]
        self.api_root = api_info["root"]
        self.api_prefix = api_info["prefix"]

        self.monolithe_config = monolithe_config
        self._sdk_output = self.monolithe_config.get_option("sdk_output", "sdk")
        self._sdk_name = self.monolithe_config.get_option("sdk_name", "sdk")
        self._product_accronym = self.monolithe_config.get_option("product_accronym")
        self._product_name = self.monolithe_config.get_option("product_name")

        self.output_directory = "%s/go/%s/%s" % (self._sdk_output, SDKUtils.get_string_version(self.api_version), self._sdk_name)

        self.attrs_defaults = RawConfigParser()
        path = "%s/go/__attributes_defaults/attrs_defaults.ini" % self._sdk_output
        self.attrs_defaults.optionxform = str
        self.attrs_defaults.read(path)

        with open("%s/go/__code_header" % self._sdk_output, "r") as f:
            self.header_content = f.read()

    def write_sdkapiversion(self, model_filenames, fetcher_filenames):
        """
        """

        self.write(destination=self.output_directory, filename="sdkinfo.go", template_name="sdkinfo.go.tpl",
                   version=self.api_version,
                   product_accronym=self._product_accronym,
                   sdk_root_api=self.api_root,
                   sdk_api_prefix=self.api_prefix,
                   product_name=self._product_name,
                   sdk_name=self._sdk_name,
                   header=self.header_content)

        self.write(destination=self.output_directory, filename="session.go", template_name="session.go.tpl",
                   version=self.api_version,
                   sdk_root_api=self.api_root,
                   sdk_api_prefix=self.api_prefix,
                   sdk_name=self._sdk_name,
                   header=self.header_content)


    def write_model(self, specification, specification_set):
        """ Write autogenerate specification file

        """
        filename = "%s.go" % (specification.entity_name.lower())

        defaults = {}
        section = specification.entity_name
        if self.attrs_defaults.has_section(section):
            for attribute in self.attrs_defaults.options(section):
                defaults[attribute] = self.attrs_defaults.get(section, attribute)

        self.write(destination=self.output_directory, filename=filename, template_name="model.go.tpl",
                   specification=specification,
                   specification_set=specification_set,
                   sdk_name=self._sdk_name,
                   header=self.header_content,
                   attribute_defaults=defaults)

        return (filename, specification.entity_name)
