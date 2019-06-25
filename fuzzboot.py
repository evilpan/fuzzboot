#!/usr/bin/env python3

"""
Author: Roee Hay / Aleph Research / HCL Technologies
"""

import device
from oemtester import OEMTester
import argparse
from config import Config
import log
from log import *
import aboot
import image


def main():

    adjustLevels()
    parser = argparse.ArgumentParser("fuzzboot", description="Fastboot oem commands fuzzer.")
    subparsers = parser.add_subparsers(dest='extend', help='extend commands')

    parser.add_argument('-e','--oem', dest='oem', help='Specify OEM to load ABOOT strings of, otherwise try to autodetect')
    parser.add_argument('-d','--device', dest='device', help='Specify device to load ABOOT strings of, otherwise try to autodetect')
    parser.add_argument('-b','--build', dest='build', help='Specify build to load ABOOT strings of, otherwise try to autodetect')
    parser.add_argument('-B','--blob', action='store_true', default=False, dest='treat_as_blob', help="Treat specified path as ABOOT blob")

    parser.add_argument('-r', '--resume', type=int, default=0, dest='index', help='Resume from specified string index')
    parser.add_argument('-i', '--ignore', dest='ignore_re', help='Ignore pattern (regexp)')
    parser.add_argument('-g', '--use-strings-generator', action='store_true', default=False, dest='use_strings_generator', help='Use strings generator instead of loading everything a priori (fast but degrades progress)')
    parser.add_argument('-o', '--output', action='store_true', dest='show_output', help="Show output of succeeded fastboot commands. Verbose logging overrides this")
    parser.add_argument('-l','--aboots-list', action='store_true', help="List available ABOOTs")

    parser.add_argument('-s','--device-serial', dest='serial', help="Specify device fastboot SN")
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='Enable verbose logging')
    parser.add_argument('-vv', '--moreverbose', action='store_true', dest='moreverbose', help='Even more logging')
    parser.add_argument('-t', '--timeout', type=int, default=5000, dest='timeout', help='USB I/O timeout (ms)')

    parser_add = subparsers.add_parser('add', help='add target image')
    parser_add.add_argument('-p','--images-path', help="Add ABOOT strings from OTA/Factory images. Either a file or a directory.")
    parser_add.add_argument('-S','--string-prefix', default="", dest='string_prefix', help="When inserting new images, only treat strings with specified prefix")

    args = parser.parse_args()
    if args.verbose:
        log.setVerbose()

    if args.moreverbose:
        log.setVerbose(True)

    I("Welcome to fuzzboot")

    Config.overlay(args.__dict__)
    T("Config = %s", Config)

    if args.treat_as_blob:
        if not args.oem or not args.device or not args.build:
            E("Missing OEM/Device/Build specifiers")
            return 1

    if args.aboots_list:
        I("BY OEM:")
        I("-------")
        dump_data(aboot.by_oem())
        I("")
        I("BY DEVICE:")
        I("----------")
        dump_data(aboot.by_device())

        return 0

    if args.extend == 'add':
        if args.images_path:
            if Config.get_config().treat_as_blob:
                Config.get_config().oem = Config.get_config().oem or 'oem'
                Config.get_config().device = Config.get_config().device or 'device'
                Config.get_config().build = Config.get_config().build or 'build'
            image.add(args.images_path)
            return 0

    dev = device.Device(args.serial)

    name = dev.device()
    adjustLevels()
    if name:
        I("Device reported name = %s", name)

    OEMTester(dev).test(args.index)

    return 0


def dump_data(data):
    keys = list(data.keys())
    keys.sort()
    nkeys = len(keys)
    for i in range(0, nkeys - 1, 2):
        I("%17s: %3d    %17s: %3d", keys[i], len(data[keys[i]]), keys[i + 1], len(data[keys[i + 1]]))

    if 1 == nkeys % 2:
        I("%17s: %3d", keys[nkeys - 1], len(data[keys[nkeys - 1]]))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('')
        I("User interrupted, quitting...")

