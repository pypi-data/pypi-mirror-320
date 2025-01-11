# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2024 OpenLP Developers                              #
# ---------------------------------------------------------------------- #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################
"""
This module contains tests for the plugin class Alerts plugin.
"""
import pytest
from unittest.mock import MagicMock, patch

from openlp.core.state import State
from openlp.core.common.registry import Registry
from openlp.core.common.settings import Settings
from openlp.plugins.alerts.alertsplugin import AlertsPlugin


@pytest.fixture
@patch('openlp.plugins.alerts.alertsplugin.DBManager')
def alerts_plugin(mocked_manager: MagicMock, settings: Settings, state: State, registry: Registry):
    """An instance of the AlertsPlugin"""
    registry.register('main_window', None)
    mocked_manager.return_value = MagicMock()
    return AlertsPlugin()


def test_plugin_about():
    """Test the About text string"""
    # GIVEN an environment
    result = AlertsPlugin.about()

    assert result == (
        '<strong>Alerts Plugin</strong>'
        '<br />The alert plugin controls the displaying of alerts on the display screen.'
    )


def test_plugin_state(alerts_plugin: AlertsPlugin, settings: Settings):
    """Test changing state"""
    # GIVEN an environment
    alerts_plugin.alerts_active = settings.value('alerts/status')
    # WHEN: I toggle the settings
    alerts_plugin.toggle_alerts_state()
    # THEN: the state has changed
    assert settings.value('alerts/status') != alerts_plugin.alerts_active


def test_alerts_trigger(alerts_plugin: AlertsPlugin):
    """Test triggering the Alerts dialog"""
    # GIVEN an environment
    alerts_plugin.alert_form = MagicMock()
    # WHEN: I request the form
    alerts_plugin.on_alerts_trigger()
    # THEN: the form is loaded
    alerts_plugin.alert_form.load_list.assert_called_once()
    alerts_plugin.alert_form.exec.assert_called_once()


def test_alerts_initialise(alerts_plugin: AlertsPlugin):
    """Test the initialise functionality"""
    # GIVEN an environment
    alerts_plugin.tools_alert_item = MagicMock()
    # WHEN: I request the form
    with patch('openlp.plugins.alerts.alertsplugin.ActionList.instance') as mocked_actionlist:
        alerts_plugin.initialise()
        # THEN: the form is loaded
        mocked_actionlist.add_action.assert_called_once()
        alerts_plugin.tools_alert_item.setVisible.assert_called_once_with(True)


def test_alerts_finalise(alerts_plugin: AlertsPlugin):
    """Test the finalise functionality"""
    # GIVEN an environment
    alerts_plugin.tools_alert_item = MagicMock()
    # WHEN: I request the form
    with patch('openlp.plugins.alerts.alertsplugin.ActionList.instance') as mocked_actionlist:
        alerts_plugin.finalise()
        # THEN: the form is loaded
        mocked_actionlist.remove_action.assert_called_once()
        alerts_plugin.tools_alert_item.setVisible.assert_called_once_with(False)
