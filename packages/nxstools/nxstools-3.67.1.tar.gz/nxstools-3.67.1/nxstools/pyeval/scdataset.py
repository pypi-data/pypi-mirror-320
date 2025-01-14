#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2018 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
#

"""  pyeval helper functions for scicat ingestor """

import os
import socket
import tango
import json
import time

# from sardana.macroserver.macro import Macro


def append_scicat_dataset(macro, status_info=True, reingest=False):
    """ append scan name to the dataset scan list file

    :param macro: hook macro
    :type macro: :class:`sardana.macroserver.macro.Macro`
    :param status_info: status info flag
    :type status_info: :obj:`bool`
    :param reingest: reingest flag
    :type reingest: :obj:`bool`
    :return: scan name if appended
    :rtype: :obj:`str`
    """
    sname = ""
    append = get_env_var(macro, "AppendSciCatDataset", None)
    nxsappend = get_env_var(macro, "NXSAppendSciCatDataset", None)
    if not append and not (nxsappend and reingest):
        return sname

    sfl = macro.getEnv('ScanFile')
    sid = macro.getEnv('ScanID')

    # find scan name for the master file
    if isinstance(sfl, str):
        sfl = [sfl]
    scanname = ""
    nexus = False
    if sfl and isinstance(sfl, list) or isinstance(sfl, tuple):
        for sf in sfl:
            scname, ext = os.path.splitext(str(sf))
            if ext in [".nxs", ".nx", ".h5", ".ndf"] and scname:
                scanname = str(scname)
                nexus = True
                break
        if not scanname:
            for sf in sfl:
                scname, ext = os.path.splitext(str(sf))
                if ext in [".fio"] and scname:
                    scanname = str(scname)
                    nxsappend = None
                    break
        if not scanname:
            for sf in sfl:
                scname, ext = os.path.splitext(str(sf))
                if scname:
                    scanname = str(scname)
                    nxsappend = None
                    break
    if scanname and (not nxsappend or reingest):
        appendentry = False
        entryname = "scan"
        try:
            nsd = get_env_var(macro, "NeXusSelectorDevice", None)
            if nsd:
                tnsd = tango.DeviceProxy(nsd)
                appendentry = bool(tnsd.appendentry)
                variables = json.loads(tnsd.configvariables)
                if isinstance(variables, dict) and "entryname" in variables:
                    entryname = variables["entryname"]
        except Exception:
            macro.warning("NeXusSelectorDevice is not available")
        if not nexus or appendentry is False:
            sname = "%s_%05i" % (scanname, sid)
        else:
            sname = "%s::/%s%i;%s_%05i" % (
                scanname, entryname, sid, scanname, sid)
        if reingest:
            sname = "%s:%s" % (sname, time.time())

        # auto grouping
        grouping = bool(get_env_var(macro, 'SciCatAutoGrouping', False))
        if grouping:
            commands = []
            fdir = macro.getEnv('ScanDir')
            try:
                sm = dict(get_env_var(macro, 'SciCatMeasurements', {}))
            except Exception:
                sm = {}

            if fdir in sm.keys():
                cgrp = sm[fdir]
                if cgrp != scanname:
                    commands.append("__command__ stop")
                    commands.append("%s:%s" % (cgrp, time.time()))
                    commands.append("__command__ start %s" % scanname)
            else:
                commands.append("__command__ start %s" % scanname)
            commands.append(sname)
            commands.append("__command__ stop")
            commands.append("%s:%s" % (scanname, time.time()))
            commands.append("__command__ start %s" % scanname)
            sname = "\n".join(commands)

            sm[fdir] = scanname
            macro.setEnv('SciCatMeasurements', sm)

        append_scicat_record(macro, sname, status_info=True)
    return sname


def append_scicat_record(macro, sname, status_info=True):
    """ append scan name to the dataset scan list file

    :param macro: hook macro
    :type macro: :class:`sardana.macroserver.macro.Macro`
    :param sname: scingestor record
    :type sname: :obj:`bool`
    :param macro: status info flag
    :type macro: :obj:`bool`
    :return: scan name if appended
    :rtype: :obj:`str`
    """
    # get beamtime id
    fdir = macro.getEnv('ScanDir')
    bmtfpath = get_env_var(macro, "BeamtimeFilePath", "/gpfs/current")
    bmtfprefix = get_env_var(
        macro, "BeamtimeFilePrefix", "beamtime-metadata-")
    bmtfext = get_env_var(macro, "BeamtimeFileExt", ".json")
    beamtimeid = beamtime_id(fdir, bmtfpath, bmtfprefix, bmtfext)
    beamtimeid = beamtimeid or "00000000"

    # get scicat dataset list file name
    defprefix = "scicat-datasets-"
    defaulthost = get_env_var(macro, "SciCatDatasetListFileLocal", None)
    hostname = None
    if defaulthost:
        hostname = socket.gethostname()
    if hostname and hostname is not True and hostname.lower() != "true":
        defprefix = "%s%s-" % (defprefix, str(hostname))
    dslprefix = get_env_var(
        macro, "SciCatDatasetListFilePrefix", defprefix)
    dslext = get_env_var(macro, "SciCatDatasetListFileExt", ".lst")
    dslfile = "%s%s%s" % (dslprefix, beamtimeid, dslext)
    if fdir:
        dslfile = os.path.join(fdir, dslfile)

    # append the scan name to the list file
    with open(dslfile, "a+") as fl:
        fl.write("\n%s" % sname)
    if status_info:
        macro.output("Appending '" + sname + "' to " + dslfile)


def beamtime_id(fpath, bmtfpath, bmtfprefix, bmtfext):
    """ code for beamtimeid  datasource

    :param fpath:  scan file directory
    :type fpath: :obj:`str`
    :param bmtfpath:  beamtime file directory
    :type bmtfpath: :obj:`str`
    :param bmtfprefix:  beamtime file prefix
    :type bmtfprefix: :obj:`str`
    :param bmtfext:  beamtime file postfix
    :type bmtfext: :obj:`str`
    :returns: beamtime id
    :rtype: :obj:`str`
    """
    result = ""
    if fpath.startswith(bmtfpath):
        try:
            if os.path.isdir(bmtfpath):
                btml = [fl for fl in os.listdir(bmtfpath)
                        if (fl.startswith(bmtfprefix)
                            and fl.endswith(bmtfext))]
                result = btml[0][len(bmtfprefix):-len(bmtfext)]
        except Exception:
            pass
    return result


def get_env_var(macro, name, defvalue):
    """ get environment variable

    :param macro: hook macro
    :type macro: :class:`sardana.macroserver.macro.Macro`
    :param name: variable name
    :type name: :obj:`str`
    :param defvalue: default value
    :type defvalue: :obj:`str`
    """
    try:
        return macro.getEnv(name)
    except Exception:
        return defvalue
