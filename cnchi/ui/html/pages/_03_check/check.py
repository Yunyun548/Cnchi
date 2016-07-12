#!/usr/bin/env python
#  -*- coding: utf-8 -*-
#
#  welcome.py
#
#  Copyright © 2016 Antergos
#
#  This file is part of The Antergos Build Server, (AntBS).
#
#  AntBS is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  AntBS is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  The following additional terms are in effect as per Section 7 of the license:
#
#  The preservation of all legal notices and author attributions in
#  the material or in the Appropriate Legal Notices displayed
#  by works containing it is required.
#
#  You should have received a copy of the GNU General Public License
#  along with AntBS; If not, see <http://www.gnu.org/licenses/>.

import os

from ui.html.pages._html_page import HTMLPage, bg_thread, json


class CheckPage(HTMLPage):
    """
    The first page shown when the app starts.

    Class Attributes:
        Also see `HTMLPage.__doc__`

    """

    def __init__(self, name='check', *args, **kwargs):
        """
        Attributes:
            Also see `HTMLPage.__doc__`.

        Args:
            name (str): A name for this widget.

        """

        super().__init__(name=name, *args, **kwargs)

        self.signals = ['space-check', 'power-check', 'update-check', 'iso-check']
        self.checked_items = []

        self._create_signals()
        self._connect_signals()

    def _connect_signals(self):


    @staticmethod
    def _get_checked_items_info():
        return {
            'reboot_required': (
                'close',
                'red',
                _('No Incomplete Install Attempts'),
                _('You must reboot before trying again.')
            ),
            'enough_space': (
                'remove',
                'gray',
                _('Has Enough Storage Space'),
                _('This system has at least 10GB* of available storage space.')
            ),
            'power_source': (
                'remove',
                'gray',
                _('Has Power Source'),
                _('This system is connected to a power source.')
            ),
            'latest_cnchi': (
                'remove',
                'gray',
                _('Installer Updated'),
                _('Cnchi is up to date.')
            ),
            'recent_iso': (
                'remove',
                'gray',
                _('Install Media Is Recent'),
                _('This system was booted using a recent ISO image.')
            )
        }

    def _get_default_template_vars(self):
        signals = json.dumps(self.signals)
        checked_items = self.get_checks_info()
        return {
            'page_name': self.name,
            'signals': signals,
            'tabs_list': self._tabs_list,
            'checked_items': checked_items
        }

    def get_checks_info(self):
        items = self._get_checked_items_info()

        if os.path.exists("/tmp/.cnchi_partitioning_completed"):
            self.checked_items.append(items['reboot_required'])

        for item, item_info in items.items():
            if item_info not in self.checked_items:
                self.checked_items.append(item_info)

        return self.checked_items

    def prepare(self):
        """ Prepare to become the current (visible) page. """
        self._set_active_tab()

    def store_values(self):
        """ This must be implemented by subclasses """
        self.logger.info('We have Internet connection.')
        self.logger.info("We're connected to a power source.")
        self.logger.info('We have enough disk space.')
