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
This module contains tests for the lib submodule of the Bible plugin.
"""
import pytest
from unittest.mock import MagicMock

from openlp.core.common.registry import Registry
from openlp.plugins.bibles.lib.biblestab import BiblesTab

__default_settings__ = {
    'bibles/verse separator': 'verse separator',
    'bibles/range separator': 'range separator',
    'bibles/list separator': 'list separator',
    'bibles/end separator': 'end separator'
}


@pytest.fixture()
def form(settings):
    Registry().register('settings_form', MagicMock())
    Registry().get('settings').extend_default_settings(__default_settings__)
    frm = BiblesTab(None, 'Songs', None, None)
    frm.settings_form.register_post_process = MagicMock()
    return frm


def test_load_when_seperators_set_on_default(form):
    """
    Test that the separator checkboxes are still checked even when the default is used
    """
    # GIVEN: Seperator settings set as the default
    form.settings.setValue('bibles/verse separator', form.settings.value('bibles/verse separator'))
    form.settings.setValue('bibles/range separator', form.settings.value('bibles/range separator'))
    form.settings.setValue('bibles/list separator', form.settings.value('bibles/list separator'))
    form.settings.setValue('bibles/end separator', form.settings.value('bibles/end separator'))

    # WHEN: Load is invoked
    form.load()

    # THEN: The checkboxes should be checked
    assert form.verse_separator_check_box.isChecked() is True
    assert form.range_separator_check_box.isChecked() is True
    assert form.list_separator_check_box.isChecked() is True
    assert form.end_separator_check_box.isChecked() is True


def test_load_when_seperators_unset(form):
    """
    Test that the separator checkboxes are not checked when the setting is not set
    """
    # GIVEN: Seperator settings non existant
    form.settings.remove('bibles/verse separator')
    form.settings.remove('bibles/range separator')
    form.settings.remove('bibles/list separator')
    form.settings.remove('bibles/end separator')

    # WHEN: Load is invoked
    form.load()

    # THEN: The checkboxes should be checked
    assert form.verse_separator_check_box.isChecked() is False
    assert form.range_separator_check_box.isChecked() is False
    assert form.list_separator_check_box.isChecked() is False
    assert form.end_separator_check_box.isChecked() is False
