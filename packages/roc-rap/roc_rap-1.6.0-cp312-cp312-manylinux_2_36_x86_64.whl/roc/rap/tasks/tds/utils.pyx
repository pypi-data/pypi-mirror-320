#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
cimport numpy as np


__all__ = ["find", "group", "count_swf"]


def find(iterable, name):
    """
    Find the parameter with name in the list in argument.
    """
    for x in iterable:
        if x.name == name:
            return x

    raise ValueError("Parameter {0} not found in list of parameters")


cpdef tuple group(np.ndarray[np.uint8_t, ndim=1] x):
    """
    Method use to group HIST2D packets (with PA_TDS_HIST2D_PKT_NR)
    
    :param x: 
    :return: 
    """
    cdef:
        Py_ssize_t i
        Py_ssize_t nmax = x.shape[0]
        np.ndarray result = np.zeros(nmax, dtype=np.uint64)
        Py_ssize_t counter = 0

    for i in range(1, nmax):
        if x[i] <= x[i-1]:
            counter += 1
        result[i] = counter

    return result, counter + 1


cpdef tuple count_swf(np.ndarray[np.uint32_t, ndim=1] x):
    """
    Method use to count SWF packets using index of snapshots.
    
    :param x: snapshot ids in packets
    :return: 2-elements tuple with corresponding list of counters and counter max. value
    """
    cdef:
        Py_ssize_t i
        Py_ssize_t nmax = x.shape[0]
        np.ndarray result = np.zeros(nmax, dtype=np.uint32)
        Py_ssize_t counter = 0

    for i in range(1, nmax):
        if x[i] != x[i-1]:
            counter += 1
        result[i] = counter

    return result, counter + 1