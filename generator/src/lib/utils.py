# -*- coding: utf-8 -*-

import re

from printer import Printer


class Utils(object):
    """ utils """

    @classmethod
    def get_python_name(cls, name):
        """ Transform a given name to python name """
        first_cap_re = re.compile('(.)([A-Z](?!s([A-Z])*)[a-z]+)')
        all_cap_re = re.compile('([a-z0-9])([A-Z])')

        def repl(matchobj):
            """ Replacement method """
            if matchobj.start() == 0:
                return matchobj.expand(r"\1\2")
            else:
                return matchobj.expand(r"\1_\2")

        s1 = first_cap_re.sub(repl, name)
        return all_cap_re.sub(r'\1_\2', s1).lower()

    @classmethod
    def get_python_type_name(cls, type_name, attribute_name=None, object_name=None):
        """ Returns a python type according to a java type """

        if type_name in ['string', 'str', 'enum']:
            return 'str'

        if type_name == 'long':
            return 'long'

        if type_name == 'boolean':
            return 'bool'

        if type_name in ['int', 'integer']:
            return 'int'

        if type_name in ['date']:
            return 'time'

        if type_name in ['double', 'float']:
            return 'float'

        # Known as wrong on the server side.
        if type_name in ['GWPersonality','ManagedObjectType','ActionType','Action','VPortTagEndPointType','TriggerType','FlowRedirectTargetType']:
            return 'str'

        clean_name = type_name.lower().strip()
        if clean_name.startswith('array') or clean_name.startswith('collection'):
            return 'list'

        # Special cases where we need to handle nested objects...
        if clean_name in ['vmresync', 'qosprimitive', 'egressqosprimitive', 'statisticspolicy', 'map', 'diffresult', 'object']:
            return 'object'

        return None

    @classmethod
    def get_singular_name(cls, plural_name):
        """ Returns the singular name of the plural name """

        if plural_name[-3:] == 'ies':
            return plural_name[:-3] + 'y'

        if plural_name[-1] == 's':
            return plural_name[:-1]

        return plural_name

    @classmethod
    def get_plural_name(cls, singular_name):
        """ Returns the plural name of the singular name """

        vowels = ['a', 'e', 'i', 'o', 'u', 'y']
        if singular_name[-1:] == 'y' and singular_name[-2] not in vowels:
            return singular_name[:-1] + 'ies'

        return singular_name + 's'

    @classmethod
    def get_version(self, server_version):
        """ Parse Server Api version to have a
            proper float version

            Args:
                server_version: version that can be like V3_0

            Returns:
                return a float number

        """
        if server_version.startswith('V'):
            server_version = server_version[1:]

        server_version = server_version.replace('_', '.')

        try:
            version = float(server_version)
        except:
            Printer.warn("Could not get a valid version from %s" % server_version)
            version = 0.0

        return version

    @classmethod
    def remove_slash(cls, path):
        """ Removes last slash

        """
        if path is None or len(path) == 0:
            return None

        if path[-1] == '/':
            return path[:-1]

        return path
