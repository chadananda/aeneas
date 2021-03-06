#!/usr/bin/env python
# coding=utf-8

"""
Global common functions. 
"""

import math
import os
import shutil
import sys
from lxml import etree

import aeneas.globalconstants as gc

__author__ = "Alberto Pettarin"
__copyright__ = """
    Copyright 2012-2013, Alberto Pettarin (www.albertopettarin.it)
    Copyright 2013-2015, ReadBeyond Srl (www.readbeyond.it)
    """
__license__ = "GNU AGPL v3"
__version__ = "1.0.0"
__email__ = "aeneas@readbeyond.it"
__status__ = "Production"

def custom_tmp_dir():
    """
    Return the path of the temporary directory to use.

    On Linux and OS X, return the value of
    :class:`aeneas.globalconstants.TMP_PATH`
    (e.g., ``/tmp/``).

    On Windows, return ``None``, so that ``tempfile``
    will use the environment directory.

    :rtype: string (path)
    """
    if sys.platform in ["linux", "linux2", "darwin"]:
        return gc.TMP_PATH
    return None

def file_name_without_extension(path):
    """
    Return the file name without extension.

    Examples: ::

        /foo/bar.baz => bar
        /foo/bar     => bar
        None         => None

    :param path: the file path
    :type  path: string (path)
    :rtype: string (path)
    """
    if path == None:
        return None
    return os.path.splitext(os.path.basename(path))[0]

def safe_float(string, default=None):
    """
    Safely parse a string into a float.

    On error return the ``default`` value.

    :param string: string value to be converted
    :type  string: string
    :param default: default value to be used in case of failure
    :type  default: float
    """
    value = default
    try:
        value = float(string)
    except TypeError:
        pass
    except ValueError:
        pass
    return value

def safe_int(string, default=None):
    """
    Safely parse a string into an int.

    On error return the ``default`` value.

    :param string: string value to be converted
    :type  string: string
    :param default: default value to be used in case of failure
    :type  default: int
    """
    value = safe_float(string, default)
    if value != None:
        value = int(value)
    return value

def remove_bom(string):
    """
    Remove the BOM character (if any) from the given string.

    :param string: a string, possibly with BOM
    :type  string: string
    :rtype: string
    """
    tmp = None
    try:
        tmp = string.decode('utf-8-sig')
        tmp = tmp.encode('utf-8')
    except UnicodeError:
        pass
    return tmp

def norm_join(prefix, suffix):
    """
    Join ``prefix`` and ``suffix`` paths
    and return the resulting path, normalized.

    :param prefix: the prefix path
    :type  prefix: string (path)
    :param suffix: the suffix path
    :type  suffix: string (path)
    :rtype: string (path)
    """
    return os.path.normpath(os.path.join(prefix, suffix))

def config_txt_to_string(string):
    """
    Convert the contents of a TXT config file
    into the corresponding configuration string ::

        key_1=value_1|key_2=value_2|...|key_n=value_n

    :param string: the contents of a TXT config file
    :type  string: string
    :rtype: string
    """
    if string == None:
        return None
    pairs = [l for l in string.splitlines() if len(l) > 0]
    return gc.CONFIG_STRING_SEPARATOR_SYMBOL.join(pairs)

def config_string_to_dict(string, result=None):
    """
    Convert a given configuration string ::

        key_1=value_1|key_2=value_2|...|key_n=value_n

    into the corresponding dictionary ::

        dictionary[key_1] = value_1
        dictionary[key_2] = value_2
        ...
        dictionary[key_n] = value_n

    :param string: the configuration string
    :type  string: string
    :rtype: dict
    """
    if string == None:
        return dict()
    pairs = string.split(gc.CONFIG_STRING_SEPARATOR_SYMBOL)
    return pairs_to_dict(pairs, result)

def config_xml_to_dict(contents, result, parse_job=True):
    """
    Convert the contents of a XML config file
    into the corresponding dictionary ::

        dictionary[key_1] = value_1
        dictionary[key_2] = value_2
        ...
        dictionary[key_n] = value_n

    :param contents: the XML configuration contents
    :type  contents: string
    :param parse_job: if ``True``, parse the job properties;
                      if ``False``, parse the tasks properties
    :type  parse_job: bool
    :rtype: dict (``parse_job=True``) or list of dict (``parse_job=False``)
    """
    try:
        root = etree.fromstring(contents)
        pairs = []
        if parse_job:
            # parse job
            for elem in root:
                if (elem.tag != gc.CONFIG_XML_TASKS_TAG) and (elem.text != None):
                    pairs.append("%s%s%s" % (
                        elem.tag,
                        gc.CONFIG_STRING_ASSIGNMENT_SYMBOL,
                        elem.text.strip()
                    ))
            return pairs_to_dict(pairs)
        else:
            # parse tasks
            output_list = []
            for task in root.find(gc.CONFIG_XML_TASKS_TAG):
                if task.tag == gc.CONFIG_XML_TASK_TAG:
                    pairs = []
                    for elem in task:
                        if elem.text != None:
                            pairs.append("%s%s%s" % (
                                elem.tag,
                                gc.CONFIG_STRING_ASSIGNMENT_SYMBOL,
                                elem.text.strip()
                            ))
                    output_list.append(pairs_to_dict(pairs))
            return output_list
    except:
        result.passed = False
        result.add_error("An error occurred while parsing XML file")
        return dict()

def config_dict_to_string(dictionary):
    """
    Convert a given config dictionary ::

        dictionary[key_1] = value_1
        dictionary[key_2] = value_2
        ...
        dictionary[key_n] = value_n

    into the corresponding string ::

        key_1=value_1|key_2=value_2|...|key_n=value_n

    :param dictionary: the config dictionary
    :type  dictionary: dict
    :rtype: string
    """
    parameters = []
    for key in dictionary:
        parameters.append("%s%s%s" % (
            key,
            gc.CONFIG_STRING_ASSIGNMENT_SYMBOL,
            dictionary[key]
        ))
    return gc.CONFIG_STRING_SEPARATOR_SYMBOL.join(parameters)

def pairs_to_dict(pairs, result=None):
    """
    Convert a given list of ``key=value`` strings ::

        key_1=value_1|key_2=value_2|...|key_n=value_n

    into the corresponding dictionary ::

        dictionary[key_1] = value_1
        dictionary[key_2] = value_2
        ...
        dictionary[key_n] = value_n

    :param pairs: the list of key=value strings
    :type  pairs: list of strings
    :rtype: dict
    """
    dictionary = dict()
    for pair in pairs:
        if len(pair) > 0:
            tokens = pair.split(gc.CONFIG_STRING_ASSIGNMENT_SYMBOL)
            if ((len(tokens) == 2) and
                    (len(tokens[0])) > 0 and
                    (len(tokens[1]) > 0)):
                dictionary[tokens[0]] = tokens[1]
            elif result != None:
                result.add_warning("Invalid key=value string: '%s'" % pair)
    return dictionary

def copytree(source_directory, destination_directory, ignore=None):
    """
    Recursively copy the contents of a source directory
    into a destination directory.
    Both directories must exist.

    NOTE: this function does not copy the root directory ``source_directory``
    into ``destination_directory``.

    NOTE: ``shutil.copytree(src, dst)`` requires ``dst`` not to exist,
    so we cannot use for our purposes.

    NOTE: code adapted from http://stackoverflow.com/a/12686557

    :param source_directory: the source directory, already existing
    :type  source_directory: string (path)
    :param destination_directory: the destination directory, already existing
    :type  destination_directory: string (path)
    """
    if os.path.isdir(source_directory):
        if not os.path.isdir(destination_directory):
            os.makedirs(destination_directory)
        files = os.listdir(source_directory)
        if ignore is not None:
            ignored = ignore(source_directory, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                copytree(
                    os.path.join(source_directory, f),
                    os.path.join(destination_directory, f),
                    ignore
                )
    else:
        shutil.copyfile(source_directory, destination_directory)

def time_to_ssmmm(time_value):
    """
    Format the given time value into a ``SS.mmm`` string.

    Examples: ::

        12        => 12.000
        12.345    => 12.345
        12.345432 => 12.345
        12.345678 => 12.346

    :param time_value: a time value, in seconds
    :type  time_value: float
    :rtype: string
    """
    return "%.3f" % (time_value)

def time_to_hhmmssmmm(time_value, decimal_separator="."):
    """
    Format the given time value into a ``HH:MM:SS.mmm`` string.

    Examples: ::

        12        => 00:00:12.000
        12.345    => 00:00:12.345
        12.345432 => 00:00:12.345
        12.345678 => 00:00:12.346
        83        => 00:01:23.000
        83.456    => 00:01:23.456
        83.456789 => 00:01:23.456
        3600      => 01:00:00.000
        3612.345  => 01:00:12.345

    :param time_value: a time value, in seconds
    :type  time_value: float
    :param decimal_separator: the decimal separator, default ``.``
    :type  decimal_separator: char
    :rtype: string
    """
    tmp = time_value
    hours = math.floor(tmp / 3600)
    tmp -= (hours * 3600)
    minutes = math.floor(tmp / 60)
    tmp -= minutes * 60
    seconds = math.floor(tmp)
    tmp -= seconds
    milliseconds = math.floor(tmp * 1000)
    return "%02d:%02d:%02d%s%03d" % (
        hours,
        minutes,
        seconds,
        decimal_separator,
        milliseconds
    )

def time_to_srt(time_value):
    """
    Format the given time value into a ``HH:MM:SS,mmm`` string,
    as used in the SRT format.

    Examples: ::

        12        => 00:00:12,000
        12.345    => 00:00:12,345
        12.345432 => 00:00:12,345
        12.345678 => 00:00:12,346
        83        => 00:01:23,000
        83.456    => 00:01:23,456
        83.456789 => 00:01:23,456
        3600      => 01:00:00,000
        3612.345  => 01:00:12,345

    :param time_value: a time value, in seconds
    :type  time_value: float
    :rtype: string
    """
    return time_to_hhmmssmmm(time_value, ",")



