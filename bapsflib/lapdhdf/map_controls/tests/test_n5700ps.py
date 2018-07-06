#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of the bapsflib package, a Python toolkit for the
# BaPSF group at UCLA.
#
# http://plasma.physics.ucla.edu/
#
# Copyright 2017-2018 Erik T. Everson and contributors
#
# License: Standard 3-clause BSD; see "LICENSES/LICENSE.txt" for full
#   license terms and contributor agreement.
#
from ..n5700ps import hdfMap_control_n5700ps
from .common import ControlTestCase

from bapsflib.lapdhdf.tests import FauxHDFBuilder

import unittest as ut


class TestN5700PS(ControlTestCase):
    """Test class for hdfMap_control_n5700ps"""

    def setUp(self):
        self.f = FauxHDFBuilder(
            add_modules={'N5700_PS': {'n_configs': 1}})
        self.mod = self.f.modules['N5700_PS']

    def tearDown(self):
        self.f.cleanup()

    @property
    def map(self):
        return hdfMap_control_n5700ps(self.cgroup)

    @property
    def cgroup(self):
        return self.f['Raw data + config/N5700_PS']

    def test_map_basics(self):
        self.assertControlMapBasics(self.map, self.cgroup)

    def test_info(self):
        self.assertEqual(self.map.info['group name'], 'N5700_PS')
        self.assertEqual(self.map.info['group path'],
                         '/Raw data + config/N5700_PS')
        self.assertEqual(self.map.info['contype'], 'power')

    def test_one_config(self):
        # reset to one config
        if self.mod.knobs.n_configs != 1:
            self.mod.knobs.n_configs = 1

        # assert details
        self.assertWaveformDetails()

    def test_three_configs(self):
        # reset to 3 configs
        if self.mod.knobs.n_configs != 3:
            self.mod.knobs.n_configs = 3

        # assert details
        self.assertWaveformDetails()

    def assertWaveformDetails(self):
        # test dataset names
        self.assertEqual(self.map.dataset_names, ['Run time list'])

        # test construct_dataset_names
        # TODO: how to test 'construct_dataset_names'

        # re-test all sub-group names
        self.assertSubgroupNames(self.map, self.cgroup)

        # test attribute 'group'
        self.assertEqual(self.map.group, self.cgroup)

        # test for command list
        self.assertTrue(self.map.has_command_list)

        # test attribute 'one_config_per_dataset'
        if self.mod.knobs.n_configs == 1:
            self.assertTrue(self.map.one_config_per_dset)
        else:
            self.assertFalse(self.map.one_config_per_dset)

        # test that 'configs' attribute is setup correctly
        self.assertConfigs()

    def assertConfigs(self):
        self.assertEqual(len(self.map.configs),
                         self.mod.knobs.n_configs)

        for config in self.map.configs:
            # keys 'dataset fields' and 'dset to numpy field' tested in
            # assertControlMapBasic
            #
            self.assertIn(config, self.mod.config_names)
            self.assertIn('IP address', self.map.configs[config])
            self.assertIn('device model', self.map.configs[config])
            self.assertIn('init command', self.map.configs[config])


if __name__ == '__main__':
    ut.main()