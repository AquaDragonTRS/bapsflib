.. _hdfmap_details:

HDF5 File Mapping (:class:`~bapsflib._hdf.maps.hdfmap.HDFMap`)
==============================================================

.. contents:: Contents
    :depth: 3
    :local:

:class:`~bapsflib._hdf.map.hdfmap.HDFMap` constructs the mapping for
a given HDF5 file.  When a HDF5 file is opened with
:class:`~bapsflib.lapd.file.File`,
:class:`~bapsflib._hdf.maps.hdfmap.HDFMap` is automatically called to
construct the map and an instance of the mapping object is bound
to the file object as :attr:`~bapsflib.lapd.file.File.file_map`.
Thus, the file mappings for :file:`test.hdf5` can be accessed like::

    >>> f = lapd.File('test.hdf5')
    >>> f.file_map
    <bapsflib._hdf.maps.hdfmap.HDFMap>

.. include:: mapping.inc.rst
.. include:: add_map_module.inc.rst