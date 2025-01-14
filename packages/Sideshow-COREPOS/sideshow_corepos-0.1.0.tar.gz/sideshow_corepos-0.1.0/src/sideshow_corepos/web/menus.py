# -*- coding: utf-8; -*-
################################################################################
#
#  Sideshow-COREPOS -- Case/Special Order Tracker for CORE-POS
#  Copyright © 2025 Lance Edgar
#
#  This file is part of Sideshow.
#
#  Sideshow is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Sideshow is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Sideshow.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Sideshow-COREPOS - custom menus
"""

from sideshow.web import menus as base


class SideshowMenuHandler(base.SideshowMenuHandler):
    """
    Custom menu handler for Sideshow, which adds CORE-POS entries.
    """

    def make_customers_menu(self, request, **kwargs):
        """
        This adds the entry for CORE-POS Members.
        """
        menu = super().make_customers_menu(request, **kwargs)

        menu['items'].extend([
            {'type': 'sep'},
            {
                'title': "CORE-POS Members",
                'route': 'corepos_members',
                'perm': 'corepos_members.list',
            },
        ])

        return menu

    def make_products_menu(self, request, **kwargs):
        """
        This adds the entry for CORE-POS Products.
        """
        menu = super().make_products_menu(request, **kwargs)

        menu['items'].extend([
            {'type': 'sep'},
            {
                'title': "CORE-POS Products",
                'route': 'corepos_products',
                'perm': 'corepos_products.list',
            },
        ])

        return menu

    def make_other_menu(self, request, **kwargs):
        """
        This adds the entry for CORE Office.
        """
        menu = super().make_other_menu(request, **kwargs)

        corepos = self.app.get_corepos_handler()
        url = corepos.get_office_url()
        if url:
            menu['items'].extend([
                {
                    'title': "CORE Office",
                    'url': url,
                    'target': '_blank',
                },
            ])

        return menu
