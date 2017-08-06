# This file is part of the bapsflib package, a Python toolkit for the
# BaPSF group at UCLA.
#
# http://plasma.physics.ucla.edu/
#
# Copyright 2017 Erik T. Everson and contributors
#
# License:
#
'''
Check Template

Generated by LaPD ~~~~~~~~~~~~~~~~ yes    (v1.1)
Item                               Found  Note
MSI/ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ yes
|-- Discharge ~~~~~~~~~~~~~~~~~~~~ yes    in mapping context
|-- Gas pressure ~~~~~~~~~~~~~~~~~ yes    in mapping context
|-- Heater ~~~~~~~~~~~~~~~~~~~~~~~ yes    in mapping context
|-- Interferometer array ~~~~~~~~~ yes    in mapping context
|-- Magnetic field ~~~~~~~~~~~~~~~ yes    in mapping context
Raw data + config/ ~~~~~~~~~~~~~~~ yes
|-- SIS 3301 ~~~~~~~~~~~~~~~~~~~~~ yes
|-- |-- Configurations Detected
|-- |-- |-- 'config name'                 used/ not used
|-- |-- |-- |-- 'crate' ~~~~~~~~~~ yes    14-bit, 100 MHz
|-- |-- |-- |-- |-- Connections (br, [ch,])
|-- |-- |-- |-- |-- |-- (0, [1,2,5])
|-- |-- |-- |-- |-- |-- (1, [3,4,5])

'''
import h5py
import os
import sys

from .hdferrors import *
from .hdfmappers import get_hdfMap


class hdfCheck(object):
    _hdf_lapd_version = ''
    _print_found_tab = 35
    _print_note_tab = 7

    def __init__(self, hdf_obj):
        if isinstance(hdf_obj, h5py.File):
            self.__hdf_obj = hdf_obj
        else:
            raise NotHDFFileError

        status = self.is_lapd_generated(silent=False)[0]
        if status:
            self.__hdf_map = get_hdfMap(self._hdf_lapd_version,
                                        self.__hdf_obj)
            self.full_check()

    def full_check(self):
        """
            Run all pre-defined file checks.
        """
        status_print('Item', 'Found', 'Note', item_found_pad=' ')

        status = self.exist_msi(silent=False)
        if status:
            self.exist_msi_diagnostics_all(silent=False)
        self.exist_data_group(silent=False)
        status = self.exist_sis_group(silent=False)
        if status:
            self.identify_data_configs()

    def is_lapd_generated(self, silent=True):
        """
            Checks the loaded HDF5 file to see if it was generated by
            the LaPD Control System.

            :param silent:
            :return:
        """
        if silent:
            sys.stdout = open(os.devnull, 'w')

        is_lapd = False
        for key in self.__hdf_obj.attrs.keys():
            if 'lapd' in key.casefold() and 'version' in key.casefold():
                self._hdf_lapd_version = \
                    self.__hdf_obj.attrs[key].decode('utf-8')
                is_lapd = True
                break

        item = 'Generated by LaPD'
        found = 'yes' if is_lapd else 'no'
        note = '(v{})\n'.format(self._hdf_lapd_version) if is_lapd\
            else '\n'
        status_print(item, found, note)

        if not is_lapd:
            raise NotLaPDHDFError

        if silent:
            sys.stdout = sys.__stdout__

        return is_lapd, self._hdf_lapd_version

    def exist_msi(self, silent=True):
        """
            Check for the existence of the MSI Group.

            :param silent:
            :return:
        """
        if silent:
            sys.stdout = open(os.devnull, 'w')

        msi_detected = False
        for key in self.__hdf_obj.keys():
            if key.casefold() == self.__hdf_map.msi_group.casefold():
                msi_detected = True

        item = self.__hdf_map.msi_group + '/ '
        found = 'yes' if msi_detected else 'no'
        status_print(item, found, '')
        if not msi_detected:
            raise NoMSIError

        if silent:
            sys.stdout = sys.__stdout__

        return msi_detected

    def exist_msi_diagnostic(self, diag_group_name, silent=True):
        """
            Check for an MSI diagnostc group by the name of
            diag_group_name.

            :param diag_group_name
            :param silent:
            :return:
        """
        if silent:
            sys.stdout = open(os.devnull, 'w')

        diag_detected = False

        # scan if diag_group_name is among the sub-groups in the MSI
        # group
        for key in self.__hdf_obj[self.__hdf_map.msi_group].keys():
            if key.casefold() == diag_group_name.casefold():
                diag_detected = True
                break

        # check if the diag_group_name is known in the pre-defined
        # mapping context
        diag_in_context = False
        for name in self.__hdf_map.msi_diagnostic_groups:
            if name.casefold() == diag_group_name.casefold():
                diag_in_context = True
                break

        item = diag_group_name + ' '
        found = 'yes' if diag_detected else 'no'
        note = 'in mapping context' if diag_in_context else ''
        status_print(item, found, note, indent=1)

        if silent:
            sys.stdout = sys.__stdout__

        return diag_detected

    def exist_msi_diagnostics_all(self, silent=True):
        """
            Check for all pre-defined MSI Diagnostic groups.

            Pre-defined diagnostic group are set in
            self._msi_diagnostic_groups,

            :param silent:
            :return:
        """
        all_diags_exist = False

        all_possible_groups = \
            list(self.__hdf_obj[self.__hdf_map.msi_group])
        all_possible_groups.extend(self.__hdf_map.msi_diagnostic_groups)
        all_possible_groups.sort()
        all_possible_groups = list(set(all_possible_groups))
        all_possible_groups.sort()

        for ii, diag in enumerate(all_possible_groups):
            status = self.exist_msi_diagnostic(diag, silent=silent)

            if ii == 0:
                all_diags_exist = status
            else:
                all_diags_exist = (all_diags_exist and status)

        return all_diags_exist, self.__hdf_map.msi_diagnostic_groups

    def exist_data_group(self, silent=True):
        """
            Check for the existence of the 'Raw data + config' Group.

            :param silent:
            :return:
        """
        if silent:
            sys.stdout = open(os.devnull, 'w')

        data_detected = False
        for key in self.__hdf_obj.keys():
            if key.casefold() == self.__hdf_map.data_group.casefold():
                data_detected = True

        item = self.__hdf_map.data_group + '/ '
        found = 'yes' if data_detected else 'no'
        status_print(item, found, '')

        if silent:
            sys.stdout = sys.__stdout__

        return data_detected

    def exist_sis_group(self, silent=True):
        """
            Check for existence of SIS group.

            :param silent:
            :return:
        """
        if silent:
            sys.stdout = open(os.devnull, 'w')

        detected = (self.__hdf_map.sis_path()
                    in self.__hdf_obj.listHDF_files)

        item = self.__hdf_map.sis_group + ' '
        found = 'yes' if detected else 'no'
        status_print(item, found, '', indent=1)

        if silent:
            sys.stdout = sys.__stdout__

        return detected

    def identify_data_configs(self):
        if self.__hdf_map.data_configs.keys().__len__() != 0:
            status_print('Configurations Detected', '', '', indent=2,
                         item_found_pad=' ')

            for key in self.__hdf_map.data_configs.keys():
                item  = key
                found = ''
                note = 'used' \
                    if self.__hdf_map.data_configs[key]['active'] \
                    else 'not used'
                status_print(item, found, note, indent=3,
                             item_found_pad= ' ')
        else:
            status_print('Configurations Detected', '', 'None',
                         indent=2,
                         item_found_pad=' ')

    def get_hdf_mapping(self):
        return self.__hdf_map


def status_print(item, found, note, indent=0, item_found_pad='~'):
    _found_tab = 35
    _note_tab = 7

    str_print = ('|-- ' * indent) + str(item) + ' '
    str_print = str_print.ljust(_found_tab - 1, item_found_pad) + ' '
    str_print += str(found).ljust(_note_tab) + str(note)

    print(str_print)
