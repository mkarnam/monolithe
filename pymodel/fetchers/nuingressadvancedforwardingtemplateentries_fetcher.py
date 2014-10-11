# -*- coding: utf-8 -*-

from restnuage import NURESTFetcher


class NUIngressAdvancedForwardingTemplateEntriesFetcher(NURESTFetcher):
    """ IngressAdvancedForwardingTemplateEntry fetcher """

    @classmethod
    def managed_class(cls):
        """ Managed class """

        from .. import NUIngressAdvancedForwardingTemplateEntry
        return NUIngressAdvancedForwardingTemplateEntry