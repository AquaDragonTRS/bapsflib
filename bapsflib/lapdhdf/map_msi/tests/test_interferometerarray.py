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
from ..interferometerarray import hdfMap_msi_interarr
from .common import MSIDiagnosticTestCase

from bapsflib.lapdhdf.tests import FauxHDFBuilder

import numpy as np
import unittest as ut


class TestInterferometerArray(MSIDiagnosticTestCase):
    """Test class for hdfMap_msi_interarr"""

    def setUp(self):
        self.f = FauxHDFBuilder(
            add_modules={'Interferometer array': {}}
        )
        self.mod = self.f.modules['Interferometer array']

    def tearDown(self):
        self.f.cleanup()

    @property
    def map(self):
        """Map object of diagnostic"""
        return self.map_diagnostic(self.dgroup)

    @property
    def dgroup(self):
        """Diagnostic group"""
        return self.f['MSI/Interferometer array']

    @staticmethod
    def map_diagnostic(group):
        """Mapping function"""
        return hdfMap_msi_interarr(group)

    def test_map_basics(self):
        """Test all required basic map features."""
        self.assertMSIDiagMapBasics(self.map, self.dgroup)

    def test_not_h5py_group(self):
        """Test error if object to map is not h5py.Group"""
        with self.assertRaises(TypeError):
            self.map_diagnostic(None)

    def test_map_failures(self):
        """Test conditions that result in unsuccessful mappings."""
        # any failed build must throw a UserWarning
        #
        # not all required datasets are found                       ----
        # - Datasets should be:
        #   ~ 'Interferometer summary list'
        #   ~ 'Interferometer trace'
        # - removed 'Interferometer summary list' from faux HDF file
        #
        self.mod.knobs.n_interferometers = 1
        del self.mod['Interferometer [0]/Interferometer summary list']
        with self.assertWarns(UserWarning):
            self.assertFalse(self.map.build_successful)
        self.mod.knobs.reset()

        # -- 'Interferometer summary list' does NOT match           ----
        # -- expected format                                        ----
        #
        # 'Interferometer summary list' is missing a required field
        name = 'Interferometer [0]/Interferometer summary list'
        data = self.mod[name][:]
        fields = list(data.dtype.names)
        fields.remove('Peak density')
        del self.mod[name]
        self.mod.create_dataset(name, data=data[fields])
        with self.assertWarns(UserWarning):
            self.assertFalse(self.map.build_successful)
        self.mod.knobs.reset()

        # 'Interferometer summary list' is not a structured numpy array
        data = np.empty((2, 100), dtype=np.float64)
        del self.mod[name]
        self.mod.create_dataset(name, data=data)
        with self.assertWarns(UserWarning):
            self.assertFalse(self.map.build_successful)
        self.mod.knobs.reset()

        # 'Interferometer summary list' does NOT have consistent shape
        # for all interferometers
        name = 'Interferometer [3]/Interferometer summary list'
        dtype = self.mod[name].dtype
        shape = (self.mod[name].shape[0] + 1, )
        data = np.empty(shape, dtype=dtype)
        del self.mod[name]
        self.mod.create_dataset(name, data=data)
        with self.assertWarns(UserWarning):
            self.assertFalse(self.map.build_successful)
        self.mod.knobs.reset()

        # 'Interferometer trace' does NOT match expected format     ----
        #
        # dataset has fields
        name = 'Interferometer [0]/Interferometer trace'
        data = np.empty((2,), dtype=np.dtype([('field1', np.float64),
                                              ('field2', np.float64)]))
        del self.mod[name]
        self.mod.create_dataset(name, data=data)
        with self.assertWarns(UserWarning):
            self.assertFalse(self.map.build_successful)
        self.mod.knobs.reset()

        # shape is not 2 dimensional
        data = np.empty((2, 5, 100), dtype=np.float64)
        del self.mod[name]
        self.mod.create_dataset(name, data=data)
        with self.assertWarns(UserWarning):
            self.assertFalse(self.map.build_successful)
        self.mod.knobs.reset()

        # number of rows is NOT consistent with
        # 'Interferometer summary list'
        dtype = self.mod[name].dtype
        shape = (self.mod[name].shape[0] + 1,
                 self.mod[name].shape[1])
        data = np.empty(shape, dtype=dtype)
        del self.mod[name]
        self.mod.create_dataset(name, data=data)
        with self.assertWarns(UserWarning):
            self.assertFalse(self.map.build_successful)
        self.mod.knobs.reset()

        # A later 'Interferometer trace' has correct shape, but also
        # has fields
        name = 'Interferometer [3]/Interferometer trace'
        shape = self.mod[name].shape
        data = np.empty(shape, dtype=np.dtype([('field1', np.float64),
                                               ('field2', np.float64)]))
        del self.mod[name]
        self.mod.create_dataset(name, data=data)
        with self.assertWarns(UserWarning):
            self.assertFalse(self.map.build_successful)
        self.mod.knobs.reset()

        # Num. of discovered interferometers does not match the     ----
        # 'Interferometer count' attribute                          ----
        source = 'Interferometer [3]'
        dest = 'Wrong inter name'
        self.mod.move(source, dest)
        with self.assertWarns(UserWarning):
            self.assertFalse(self.map.build_successful)
        self.mod.knobs.reset()

    def test_configs_general_items(self):
        """
        Test behavior for the general, polymorphic elements of the
        `configs` mapping dictionary.
        """
        # get map instance
        _map = self.map

        # ensure general items are present
        self.assertIn('n interferometer', _map.configs)
        self.assertIn('calib tag', _map.configs)
        self.assertIn('interferometer name', _map.configs)
        self.assertIn('t0', _map.configs)
        self.assertIn('dt', _map.configs)
        self.assertIn('n_bar_L', _map.configs)
        self.assertIn('z', _map.configs)

        # ensure general items have expected values
        self.assertEqual(
            [self.dgroup.attrs['Interferometer count']],
            _map.configs['n interferometer'])
        self.assertEqual(
            [self.dgroup.attrs['Calibration tag']],
            _map.configs['calib tag'])
        inter_names = []
        t0 = []
        dt = []
        n_bar_L = []
        z = []
        for name in self.dgroup:
            inter_names.append(name)
            t0.append(self.dgroup[name].attrs['Start time'])
            dt.append(self.dgroup[name].attrs['Timestep'])
            n_bar_L.append(self.dgroup[name].attrs['n_bar_L'])
            z.append(self.dgroup[name].attrs['z location'])
        self.assertEqual(inter_names,
                         _map.configs['interferometer name'])
        self.assertEqual(t0, _map.configs['t0'])
        self.assertEqual(dt, _map.configs['dt'])
        self.assertEqual(n_bar_L, _map.configs['n_bar_L'])
        self.assertEqual(z, _map.configs['z'])

        # check warning if an item is missing or incorrect
        # - a warning is thrown, but mapping continues
        #
        # remove attribute 'Interferometer count' from main group
        del self.dgroup.attrs['Interferometer count']
        with self.assertWarns(UserWarning):
            _map = self.map
            self.assertIn('n interferometer', _map.configs)
            self.assertEqual(_map.configs['n interferometer'], [])
        self.mod.knobs.reset()

        # remove attribute 'Timestep' from a sub-group
        del self.dgroup['Interferometer [1]'].attrs['Timestep']
        test_vals = dt.copy()
        test_vals[1] = None
        with self.assertWarns(UserWarning):
            _map = self.map
            self.assertIn('dt', _map.configs)
            self.assertEqual(_map.configs['dt'], test_vals)
        self.mod.knobs.reset()

        # check warnings if 'Interferometer count' is NOT an integer
        self.dgroup.attrs['Interferometer count'] = b'none'
        with self.assertWarns(UserWarning):
            _map = self.map
            self.assertIn('n interferometer', _map.configs)
            self.assertEqual(_map.configs['n interferometer'],
                             [b'none'])
        self.mod.knobs.reset()

        # check warnings if 'Interferometer count' is integer array
        self.dgroup.attrs['Interferometer count'] = np.array([4, 5])
        with self.assertWarns(UserWarning):
            _map = self.map
            self.assertIn('n interferometer', _map.configs)
            self.assertTrue(np.array_equal(
                _map.configs['n interferometer'], np.array([4, 5])))
        self.mod.knobs.reset()


if __name__ == '__main__':
    ut.main()
