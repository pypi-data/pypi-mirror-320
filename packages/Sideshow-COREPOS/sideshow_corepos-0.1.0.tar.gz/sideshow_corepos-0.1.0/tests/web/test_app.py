# -*- coding: utf-8; -*-

from wuttjamaican.testing import FileTestCase, ConfigTestCase

from asgiref.wsgi import WsgiToAsgi
from pyramid.router import Router

from sideshow_corepos.web import app as mod


class TestMain(FileTestCase):

    def test_basic(self):
        global_config = None
        myconf = self.write_file('my.conf', '')
        settings = {'wutta.config': myconf}
        app = mod.main(global_config, **settings)
        self.assertIsInstance(app, Router)


class TestMakeWsgiApp(ConfigTestCase):

    def test_basic(self):
        wsgi = mod.make_wsgi_app()
        self.assertIsInstance(wsgi, Router)


class TestMakeAsgiApp(ConfigTestCase):

    def test_basic(self):
        asgi = mod.make_asgi_app()
        self.assertIsInstance(asgi, WsgiToAsgi)
