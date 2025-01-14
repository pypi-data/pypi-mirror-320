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
Sideshow-COREPOS config extension
"""

from wuttjamaican.conf import WuttaConfigExtension


class SideshowCoreposConfig(WuttaConfigExtension):
    """
    Config extension for Sideshow-COREPOS.

    This establishes some config defaults specific to Sideshow-COREPOS.
    """
    key = 'sideshow_corepos'

    def configure(self, config):
        """ """

        # batch handlers
        config.setdefault(f'{config.appname}.batch.neworder.handler.spec',
                          'sideshow_corepos.batch.neworder:NewOrderBatchHandler')

        # web app menu
        config.setdefault(f'{config.appname}.web.menus.handler.spec',
                          'sideshow_corepos.web.menus:SideshowMenuHandler')
