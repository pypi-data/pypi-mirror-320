# -*- coding: utf-8; -*-

from wuttaweb.testing import WebTestCase

from sideshow_corepos import web as mod


class TestIncludeme(WebTestCase):

    def test_coverage(self):
        mod.includeme(self.pyramid_config)
