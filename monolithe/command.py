# -*- coding: utf-8 -*-

__all__ = ['Command']

import os
import shutil
import json

from .lib import SwaggerParser
from .lib import SDKWriter, DocWriter
from .lib import SpecificationTransformer
from .lib import SwaggerTransformer
from .lib import SpecificationParser
from .lib import TestsRunner

from monolithe.utils.printer import Printer

CODEGEN_DIRECTORY = './codegen'
DOCS_DIRECTORY = './docgen'
SPECGEN_DIRECTORY = './specgen'


class Command(object):
    """ Command

    """
    @classmethod
    def run_tests(cls, vsdurl, username, password, enterprise, version, data):
        """ Run all tests according to the given data

            `data` contains information:
                `spec`: the specification
                `parent`: the parent information
                `default_values`: the default values for the object

            Args:
                data (dict):

        """
        rest_name = None

        if 'RESTName' in data:
            Printer.log('******* %s' % data['RESTName'])
            rest_name = data['RESTName']

        parent_object = data['parentObject']
        default_values = data['defaultValues']

        spec = data['spec']

        if spec is None or len(spec) == 0:
            spec = Command.get_spec(vsdurl=vsdurl, apiversion=version, rest_name=rest_name)

        processed_spec = SpecificationTransformer.get_objects(specifications={spec['model']['RESTName']: spec})
        model = processed_spec[spec['model']['RESTName']]

        runner = TestsRunner(vsdurl=vsdurl, username=username, password=password, enterprise=enterprise, version=version, model=model, parent_resource=parent_object['resourceName'], parent_id=parent_object['id'], **default_values)

        return runner.run()

    @classmethod
    def get_spec(cls, vsdurl, apiversion, rest_name, path=None):
        """

        """
        if vsdurl is None and path is None:
            Printer.raiseError("Please provide a vsd url or a path to swagger json file")

        # Read Swagger
        swagger_parser = SwaggerParser(vsdurl=vsdurl, path=path, apiversion=apiversion)
        resources = swagger_parser.run(filters=[rest_name])

        # Convert Swagger models
        specs = SwaggerTransformer.get_specifications(resources=resources, filters=[rest_name])

        if rest_name in specs:
            return specs[rest_name]

        return None

    @classmethod
    def generate_specs(cls, vsdurl, path, apiversion, output_path=None):
        """ Generate specs

        """
        if vsdurl is None and path is None:
            Printer.raiseError("Please provide a vsd url or a path to swagger json file")

        # Read Swagger
        swagger_parser = SwaggerParser(vsdurl=vsdurl, path=path, apiversion=apiversion)
        resources = swagger_parser.run()

        # Convert Swagger models
        specs = SwaggerTransformer.get_specifications(resources=resources)

        if not output_path:
            output_path = SPECGEN_DIRECTORY

        output_path = '%s/%s' % (output_path, apiversion)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        for name, spec in specs.iteritems():

            file_path = '%s/%s.spec' % (output_path, spec['model']['entityName'].lower())
            with open(file_path, 'wb') as file:
                json.dump(spec, file, indent=4, sort_keys=True)

    @classmethod
    def generate_sdk(cls, vsdurl, path, apiversion, revision, output_path=None, force_removal=False, specs_path=None):
        """ Generate the Python SDK according to given parameters

            It will generate a new SDK from vanilla/vsdk sources or update the targeted repository.

            Args:
                vsdurl: the url to the vsd api
                apiversion: the version of the vsd api in a dotted notation (ex: 3.0)
                revision: the revision number
                output_path: the path to the output directory
                force: force removal of the existing codegen directory

        """
        if vsdurl is None and path is None:
            Printer.raiseError("Please provide a vsd url or a path to swagger json file")

        # Read Swagger
        swagger_parser = SwaggerParser(vsdurl=vsdurl, path=path, apiversion=apiversion)
        resources = swagger_parser.run()

        # Convert Swagger models
        specs = SwaggerTransformer.get_specifications(resources=resources)

        if specs_path is not None:
            candidates = SpecificationParser.run(specs_path)
            specs.update(candidates)

        # Process Swagger models
        processed_resources = SpecificationTransformer.get_objects(specifications=specs)

        # Compute output directory according to the version
        if apiversion is None:
            apiversion = swagger_parser.apiversion

        if output_path:
            directory = '%s/%s' % (output_path, apiversion)
        else:
            directory = '%s/%s' % (CODEGEN_DIRECTORY, apiversion)

        if force_removal and os.path.exists(directory):
            shutil.rmtree(directory)

        # Write Python sources
        sdk_writer = SDKWriter(directory=directory)
        sdk_writer.write(resources=processed_resources, apiversion=apiversion, revision=revision)

    @classmethod
    def generate_doc(cls, vsdurl, path, apiversion, output_path=None):
        """ Generate the Python SDK according to given parameters

            It will generate a new SDK from vanilla/vsdk sources or update the targeted repository.

            Args:
                vsdurl: the url to the vsd api
                apiversion: the version of the vsd api in a dotted notation (ex: 3.0)
                output_path: the path to the output directory

        """
        # Read Swagger
        swagger_parser = SwaggerParser(vsdurl=vsdurl, path=path, apiversion=apiversion)
        resources = swagger_parser.run()

        # Convert Swagger models
        specs = SwaggerTransformer.get_specifications(resources=resources)

        # Process Swagger models
        processed_resources = SpecificationTransformer.get_objects(specifications=specs)

        # Compute output directory according to the version
        if apiversion is None:
            apiversion = swagger_parser.apiversion

        if output_path:
            directory = '%s/%s' % (output_path, apiversion)
        else:
            directory = '%s/%s' % (DOCS_DIRECTORY, apiversion)

        # Write Python sources
        doc_writer = DocWriter(directory=directory)
        doc_writer.write(resources=processed_resources, apiversion=apiversion)
