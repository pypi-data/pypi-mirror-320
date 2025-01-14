# -*- coding: utf-8; -*-

from wuttaweb.testing import WebTestCase

from sideshow_corepos.web import menus as mod


class TestSideshowMenuHandler(WebTestCase):

    def make_handler(self):
        return mod.SideshowMenuHandler(self.config)

    def test_make_customers_menu(self):
        handler = self.make_handler()
        menu = handler.make_customers_menu(self.request)
        item = menu['items'][-1]
        self.assertEqual(item, {
            'title': "CORE-POS Members",
            'route': 'corepos_members',
            'perm': 'corepos_members.list',
        })

    def test_make_products_menu(self):
        handler = self.make_handler()
        menu = handler.make_products_menu(self.request)
        item = menu['items'][-1]
        self.assertEqual(item, {
            'title': "CORE-POS Products",
            'route': 'corepos_products',
            'perm': 'corepos_products.list',
        })

    def test_make_other_menu(self):
        handler = self.make_handler()

        # no url configured by default
        menu = handler.make_other_menu(self.request)
        if menu['items']:
            item = menu['items'][-1]
            self.assertNotEqual(item['title'], "CORE Office")

        # entry added if url configured
        self.config.setdefault('corepos.office.url', 'http://localhost/fannie/')
        menu = handler.make_other_menu(self.request)
        item = menu['items'][-1]
        self.assertEqual(item, {
            'title': "CORE Office",
            # nb. trailing slash gets stripped
            'url': 'http://localhost/fannie',
            'target': '_blank',
        })
