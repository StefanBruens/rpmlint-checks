# vim:sw=4:et
#---------------------------------------------------------------
# Module          : rpmlint
# File            : CheckPkgConfig
# Author          : Stephan Kulow, Dirk Mueller
# Purpose         : Check for errors in Pkgconfig files
#---------------------------------------------------------------

from Filter import *
import AbstractCheck
import rpm
import re
import commands
import Config
import os

class PkgConfigCheck(AbstractCheck.AbstractFilesCheck):
    def __init__(self):
        AbstractCheck.AbstractFilesCheck.__init__(self, "PkgConfigCheck", ".*/pkgconfig/.*\.pc$")
        # currently causes too many failures (2008-03-05)
        #self.suspicious_dir=re.compile('(?:/usr/src/\w+/BUILD|/var/tmp|/tmp|/home|\@\w{1,50}\@)')
        self.suspicious_dir=re.compile('(?:/usr/src/\w+/BUILD|/var/tmp|/tmp|/home)')

    def check_file(self, pkg, filename):
        if pkg.isSource():
            return

        if pkg.grep(self.suspicious_dir, filename):
            printError(pkg, "invalid-pkgconfig-file", filename)

check=PkgConfigCheck()

if Config.info:
    addDetails(
'invalid-pkgconfig-file',
'''Your .pc file appears to be invalid. Possible causes are:
- it contains traces of $RPM_BUILD_ROOT or $RPM_BUILD_DIR.
- it contains unreplaced macros (@have_foo@)
- it references invalid paths (e.g. /home or /tmp)

Please double-check and report false positives.
'''
)
