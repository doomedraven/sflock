# Copyright (C) 2015-2018 Jurriaan Bremer.
# Copyright (C) 2018 Hatching B.V.
# This file is part of SFlock - http://www.sflock.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os
import subprocess
import tempfile

from sflock.abstracts import Unpacker
from sflock.exception import UnpackException

class Zip7File(Unpacker):
    name = "7zfile"
    exe = "/usr/bin/7z"
    exts = ".7z", ".iso", ".zip"
    # TODO Should we use "isoparser" (check PyPI) instead of 7z?
    magic = "7-zip archive", "ISO 9660"
    priority = 1

    def handles(self):
        if super(Zip7File, self).handles():
            return True
        if self.f.stream.read(2) == b"PK":
            return True
        return False

    def unpack(self, depth=0, password=None, duplicates=None):
        self.f.archive = True
        dirpath = tempfile.mkdtemp()

        if password:
            raise UnpackException(
                "Currently password-protected .7z files are not supported "
                "due to a ZipJail-related monitoring issue (namely, due to "
                "7z calling clone(2) when a password has been provided)."
            )

        if self.f.filepath:
            filepath = self.f.filepath
            temporary = False
        else:
            filepath = self.f.temp_path(b".7z")
            temporary = True

        ret = self.zipjail(
            filepath, dirpath, "x", "-mmt=off", "-o%s" % dirpath, filepath
        )
        if not ret:
            return []

        if temporary:
            os.unlink(filepath)

        return self.process_directory(dirpath, duplicates, depth)

class GzipFile(Unpacker):
    name = "gzipfile"
    exe = "/usr/bin/7z"
    exts = ".gzip"
    magic = "gzip compressed data, was"

    def unpack(self, depth=0, password=None, duplicates=None):
        dirpath = tempfile.mkdtemp()

        if self.f.filepath:
            filepath = self.f.filepath
            temporary = False
        else:
            filepath = self.f.temp_path(".7z")
            temporary = True

        ret = self.zipjail(
            filepath, dirpath, "x", "-o%s" % dirpath, filepath
        )
        if not ret:
            return []

        if temporary:
            os.unlink(filepath)

        return self.process_directory(dirpath, duplicates, depth)

class LzhFile(Unpacker):
    name = "lzhfile"
    exe = "/usr/bin/7z"
    exts = ".lzh", ".lha"
    magic = "LHa ("

    def unpack(self, depth=0, password=None, duplicates=None):
        dirpath = tempfile.mkdtemp()

        if self.f.filepath:
            filepath = self.f.filepath
            temporary = False
        else:
            filepath = self.f.temp_path(".7z")
            temporary = True

        ret = self.zipjail(
            filepath, dirpath, "x", "-o%s" % dirpath, filepath
        )
        if not ret:
            return []

        if temporary:
            os.unlink(filepath)

        return self.process_directory(dirpath, duplicates, depth)



class VHDFile(Unpacker):
    name = "vhdfile"
    exe = "/usr/bin/7z"
    exts = ".vhd", ".vhdx"
    magic = " Microsoft Disk Image"

    def unpack(self, depth=0, password=None, duplicates=None):
        dirpath = tempfile.mkdtemp()

        if self.f.filepath:
            filepath = self.f.filepath
            temporary = False
        else:
            filepath = self.f.temp_path(".vhd")
            temporary = True

        ret = self.zipjail(
            filepath, dirpath, "x", "-xr![SYSTEM]*", "-o%s" % dirpath, filepath
        )

        if not ret:
            return []

        if temporary:
            os.unlink(filepath)

        return self.process_directory(dirpath, duplicates, depth)
