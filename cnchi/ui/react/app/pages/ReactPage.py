#!/usr/bin/env python
#  -*- coding: utf-8 -*-
#
#  page.py
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

# Standard Lib
from _base_object import (
    os
)

# 3rd-party Libs
from ui.base_widgets import (
    Gtk,
    GLib
)

# This application
from ui.base_widgets import (
    bg_thread,
    DataObject,
    BaseObject,
    SharedData
)


class ReactPage(BaseObject):
    """
    Represents a page in the installation process.

    Class Attributes:
        Also see `BaseObject.__doc__`

    """

    _top_level_tabs = SharedData('_top_level_tabs')

    def __init__(self, name='ReactPage', index=0, module=None, *args, **kwargs):
        """
        Attributes:
            Also see `BaseObject.__doc__`.

        Args:
            name (str): A name for this widget.

        """

        super().__init__(name=name, *args, **kwargs)

        self.signals = ['page-navigation-request', '--trigger-event', 'get-state', 'set-state']
        self.tabs = []
        self.index = index
        self.module = module
        self.logger.debug('page index is %s', index)

        if self._top_level_tabs is None:
            self.logger.debug('Generating main navigation tabs list..')
            self._generate_tabs_list()

        self._prepare_signals_list()
        self._create_and_connect_signals()
        self.state = self._get_default_state()

    def _create_and_connect_signals(self):
        """
        Creates the page's signals and connects them to their callbacks (handlers).
        Signals be appended to `self.signals` prior to calling this method.

        A corresponding result signal will be created for each signal and added to the
        allowed signals list automatically. Signal names will have 'do-' prepended to them.
        Their corresponding result signal will have '-result' appended to it.

        The name of the callback method that will be registered for each signal will be the
        signal name as it appears in `self.signals` at the time of calling this method with
        hyphens replaced by underscores and should end with '_cb'.

        A callback is not automatically connected for signals that start with two hyphens.

        Example:
            >>> self.signals = ['some-action', 'some-other-action', '--private-action']
            >>> self._create_and_connect_signals()
            >>> self.signals
                ['do-some-action', 'some-action-result', 'do-other-action',
                 'other-action-result', 'private-action']

            With the above, these callback methods will have been registered (they must exist):
                'do-some-action':  `self.some_action_cb`
                'do-other-action': `self.other_action_cb`

        """

        signals = []

        for _signal in self.signals:
            result_signal_name = '{}-result'.format(_signal)
            signal_name = 'do-{}'.format(_signal) if not _signal.startswith('--') else _signal[2:]

            signals_to_add = [
                s for s in [signal_name, result_signal_name]
                if s not in self._allowed_signals
            ]

            for name in signals_to_add:
                self._allowed_signals.append(name)
                self._main_window.create_custom_signal(name)
                signals.append(name)

            if _signal.startswith('--'):
                continue

            callback_name = '{}_cb'.format(_signal.replace('-', '_'))

            if '-get-' in _signal:
                callback = getattr(self.module, callback_name)
            else:
                callback = getattr(self, callback_name)

            self._main_window.connect(signal_name, callback)

        self.signals = signals

    def _generate_tabs_list(self):
        tabs = self._pages_helper.get_page_names()
        excluded = ['language', 'welcome']
        self._top_level_tabs = [t for t in tabs if t not in excluded]

    def _get_default_state(self):
        this_page_state = self.module.get_default_state()
        default_state = {
            'page_name': self.name,
            'top_level_tabs': self._top_level_tabs,
            'page_index': self.index
        }

        default_state.update(this_page_state)

        return default_state

    def _prepare_signals_list(self):
        install_options = self.settings.install_options[self.name.capitalize()]
        get_data = ['get-{}'.format(d) for d in install_options.data]

        self.signals.extend(get_data)

    def get_state_cb(self, *args):
        self._controller.emit_js(
            'trigger-event', 'get-initial-state-result', self.state
        )

    def prepare(self):
        """ This must be implemented by subclasses """
        pass

    def set_state_cb(self, widget, state, *args):
        pass

