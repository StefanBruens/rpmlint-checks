# vim:sw=4:et
#############################################################################
# File          : LibraryPolicyCheck.py
# Package       : rpmlint
# Author        : Richard Guenther
# Purpose       : Verify shared library packaging policy rules
#############################################################################

import AbstractCheck
import Config
from Filter import addDetails
from Filter import printError
from Filter import printWarning
import os
import Pkg
import re
import rpm
import stat

from BinariesCheck import BinaryInfo

_policy_legacy_exceptions = (
    "libacl1",
    "libaio1",
    "libalut0",
    "libapr-1-0",
    "libaprutil-1-0",
    "libartskde1",
    "libattr1",
    "libcdaudio1",
    "libcdk4",
    "libcheck0",
    "libchewing3",
    "libchm0",
    "libclucene0",
    "libdar4",
    "libdbh-4_5-4",
    "libdbus-qt-1-1",
    "libdm0",
    "libdns_sd1",
    "libefence0",
    "libEMF1",
    "libevolutionglue",
    "libf2c0",
    "libffi4",
    "libflaim5_2",
    "libfontenc1",
    "libfreeradius-client2",
    "libgcc_s1",
    "libgcc_s4",  # only for hppa
    "libgconfmm-2_6-1",
    "libgfortran3",
    "libgif4",
    "libgimpprint1",
    "libgladesharpglue-2",
    "libglibsharpglue-2",
    "libgltt0",
    "libglut3",
    "libGLw1",
    "libgmcop1",
    "libgnet-2_0-0",
    "libgnomecanvasmm-2_6-1",
    "libgnomecups-1_0-1",
    "libgnomemm-2_6-1",
    "libgnomeprintui-2-2-0",
    "libgnomesharpglue-2",
    "libgnomeuimm-2_6-1",
    "libgomp1",
    "libgsfglue",
    "libgsf-gnome-1-114",
    "libgtksourceview-1_0-0",
    "libgtkspell0",
    "libhangul0",
    "libICE6",
    "libid3-3_8-3",
    "libid3tag0",
    "libidn11",
    "libiec61883-0",
    "libieee1284-3",
    "libilbc0",
    "libind_helper0",
    "libiterm1",
    "libjackasyn0",
    "libkakasi2",
    "libkeyutils1",
    "libksba8",
    "liblo0",
    "libmal0",
    "libmcrypt4",
    "libmdbodbc0",
    "libmeanwhile1",
    "libmhash2",
    "libmikmod2",
    "libmng1",
    "libnet6-1_3-0",
    "libnl1",
    "libnscd1",
    "libobjc3",
    "libodbcinstQ1",
    "liboil-0_3-0",
    "liboop4",
    "libopenal0",
    "libopenal1",
    "libpgeasy3",
    "libportaudio2",
    "libqnotify0",
    "libQt3Support4",
    "libqtc1",
    "libqtsharp0",
    "libQtSql4",
    "libquadmath0",
    "librdf0",
    "librsync1",
    "libsamplerate0",
    "libsecprog0",
    "libsexy2",
    "libsigc-1_2-5",
    "libSM6",
    "libsndfile1",
    "libstdc++6",
    "libstroke0",
    "libthai0",
    "libutempter0",
    "libvisual-0_4-0",
    "libXau6",
    "libxclass0_9_2",
    "libXdmcp6",
    "libXext6",
    "libxfce4util4",
    "libxfcegui4-4",
    "libXfixes3",
    "libxflaim3_2",
    "libXiterm1",
    "libxkbfile1",
    "libxml2-2",
    "libXp6",
    "libXprintUtil1",
    "libXrender1",
    "libXt6",
    "libXv1",
    "libz1",
    "libzio0"
)

_essential_dependencies = (
    "ld-linux.so.2",
    "libacl.so.1",
    "libanl.so.1",
    "libanonymous.so.2",
    "libattr.so.1",
    "libaudit.so.0",
    "libauparse.so.0",
    "libBrokenLocale.so.1",
    "libbz2.so.1",
    "libcidn.so.1",
    "libck-connector.so.0",
    "libcom_err.so.2",
    "libcrack.so.2",
    "libcrypto.so.0.9.8",
    "libcrypt.so.1",
    "libc.so.6",
    "libdbus-1.so.3",
    "libdbus-glib-1.so.2",
    "libdes425.so.3",
    "libdl.so.2",
    "libexpat.so.1",
    "libform.so.5",
    "libformw.so.5",
    "libgcc_s.so.1",
    "libgcrypt.so.11",
    "libgdbm_compat.so.3",
    "libgdbm.so.3",
    "libgfortran3",
    "libgio-2.0.so.0",
    "libglib-2.0.so.0",
    "libgmodule-2.0.so.0",
    "libgobject-2.0.so.0",
    "libgpg-error.so.0",
    "libgssapi_krb5.so.2",
    "libgssrpc.so.4",
    "libgthread-2.0.so.0",
    "libhal.so.1",
    "libhal-storage.so.1",
    "libhd.so.14",
    "libhistory.so.5",
    "libk5crypto.so.3",
    "libkadm5clnt.so.5",
    "libkadm5srv.so.5",
    "libkdb5.so.4",
    "libkeyutils.so.1",
    "libkrb4.so.2",
    "libkrb5.so.3",
    "libkrb5support.so.0",
    "libksba.so.8",
    "liblber-2.4.so.2",
    "libldap-2.4.so.2",
    "libldap_r-2.4.so.2",
    "liblogin.so.2",
    "liblog_syslog.so.1",
    "libltdl.so.3",
    "libmagic.so.1",
    "libmenu.so.5",
    "libmenuw.so.5",
    "libm.so.6",
    "libncurses.so.5",
    "libncursesw.so.5",
    "libnscd.so.1",
    "libnsl.so.1",
    "libnss_compat.so.2",
    "libnss_dns.so.2",
    "libnss_files.so.2",
    "libnss_hesiod.so.2",
    "libnss_nisplus.so.2",
    "libnss_nis.so.2",
    "libopenct.so.1",
    "libopensc.so.2",
    "libpamc.so.0",
    "libpam_misc.so.0",
    "libpam.so.0",
    "libpanel.so.5",
    "libpanelw.so.5",
    "libparted-1.8.so.8",
    "libpcrecpp.so.0",
    "libpcreposix.so.0",
    "libpcre.so.0",
    "libpcsclite.so.1",
    "libpkcs15init.so.2",
    "libpolkit-dbus.so.2",
    "libpolkit-grant.so.2",
    "libpolkit.so.2",
    "libpopt.so.0",
    "libpthread.so.0",
    "libpth.so.20",
    "libreadline.so.5",
    "libresmgr.so.0.9.8",
    "libresmgr.so.1",
    "libresolv.so.2",
    "librt.so.1",
    "libsasl2.so.2",
    "libsasldb.so.2",
    "libscconf.so.2",
    "libslp.so.1",
    "libsmbios.so.1",
    "libssl.so.0.9.8",
    "libss.so.2",
    "libstdc++.so.6",
    "libthread_db.so.1",
    "libtic.so.5",
    "libusb-0.1.so.4",
    "libusbpp-0.1.so.4",
    "libutil.so.1",
    "libuuid.so.1",
    "libvolume_id.so.0",
    "libwrap.so.0",
    "libX11.so.6",
    "libX11-xcb.so.1",
    "libXau.so.6",
    "libxcb-composite.so.0",
    "libxcb-damage.so.0",
    "libxcb-dpms.so.0",
    "libxcb-glx.so.0",
    "libxcb-randr.so.0",
    "libxcb-record.so.0",
    "libxcb-render.so.0",
    "libxcb-res.so.0",
    "libxcb-screensaver.so.0",
    "libxcb-shape.so.0",
    "libxcb-shm.so.0",
    "libxcb.so.1",
    "libxcb-sync.so.0",
    "libxcb-xevie.so.0",
    "libxcb-xf86dri.so.0",
    "libxcb-xfixes.so.0",
    "libxcb-xinerama.so.0",
    "libxcb-xlib.so.0",
    "libxcb-xprint.so.0",
    "libxcb-xtest.so.0",
    "libxcb-xvmc.so.0",
    "libxcb-xv.so.0",
    "libxcrypt.so.1",
    "libzio.so.0",
    "libz.so.1",
)


def libname_from_soname(soname):
    libname = str.split(soname, '.so.')
    if len(libname) == 2:
        if libname[0][-1:].isdigit():
            libname = '-'.join(libname)
        else:
            libname = ''.join(libname)
    else:
        libname = soname[:-3]
    libname = libname.replace('.', '_')
    return libname


class LibraryPolicyCheck(AbstractCheck.AbstractCheck):
    def __init__(self):
        AbstractCheck.AbstractCheck.__init__(self, "LibraryPolicyCheck")
        self.map = []
        self.strongly_versioned_re = re.compile(r'-[\d\.]+\.so$')

    def check(self, pkg):
        global _policy_legacy_exceptions

        if pkg.isSource():
            return

        # Only check unsuffixed lib* packages
        if pkg.name.endswith('-devel') or pkg.name.endswith('-doc'):
            return

        files = pkg.files()

        # Search for shared libraries in this package
        libs = set()
        libs_needed = set()
        libs_to_dir = dict()
        dirs = set()
        reqlibs = set()
        pkg_requires = set(map(lambda x: str.split(x[0], '(')[0],
                               pkg.requires()))

        for f, pkgfile in files.items():
            if '.so.' in f or f.endswith('.so'):
                filename = pkg.dirName() + '/' + f
                if stat.S_ISREG(files[f].mode) and pkgfile.magic.startswith('ELF '):
                    bi = BinaryInfo(pkg, filename, f, False, True)
                    libs_needed = libs_needed.union(bi.needed)
                    if bi.soname != 0:
                        lib_dir = '/'.join(f.split('/')[:-1])
                        libs.add(bi.soname)
                        libs_to_dir[bi.soname] = lib_dir
                        dirs.add(lib_dir)
                    if bi.soname in pkg_requires:
                        # But not if the library is used by the pkg itself
                        # This avoids program packages with their own
                        # private lib
                        # FIXME: we'd need to check if somebody else links
                        # to this lib
                        reqlibs.add(bi.soname)

        std_dirs = dirs.intersection((
            '/lib', '/lib64', '/usr/lib', '/usr/lib64',
            '/opt/kde3/lib', '/opt/kde3/lib64'))

        # If this is a program package (all libs it provides are
        # required by itself), bail out
        if not pkg.name.startswith("lib") and len(libs.difference(reqlibs)) == 0:
            return

        std_lib_package = False
        if pkg.name.startswith("lib") and pkg.name[-1].isdigit():
            std_lib_package = True

        # ignore libs in a versioned non_std_dir
        if std_lib_package:
            for lib in libs.copy():
                lib_dir = libs_to_dir[lib]
                if lib_dir.startswith("/opt/kde3"):
                    continue
                for lib_part in lib_dir.split('/'):
                    if len(lib_part) == 0:
                        continue
                    if lib_part[-1].isdigit() and not lib_part.endswith("lib64"):
                        libs.remove(lib)
                        break

        # Check for non-versioned libs in a std lib package
        if std_lib_package:
            for lib in libs.copy():
                if (not (lib[-1].isdigit() or
                         self.strongly_versioned_re.search(lib))):
                    printWarning(pkg, "shlib-unversioned-lib", lib)

        # If this package should be or should be splitted into shlib
        # package(s)
        if len(libs) > 0 and len(std_dirs) > 0:
            # If the package contains a single shlib, name after soname
            if len(libs) == 1:
                soname = libs.copy().pop()
                libname = libname_from_soname(soname)
                if libname.startswith('lib') and pkg.name != libname and \
                        pkg.name != libname + "-mini":
                    if libname in _policy_legacy_exceptions:
                        printWarning(pkg, 'shlib-legacy-policy-name-error', libname)
                    else:
                        printError(pkg, 'shlib-policy-name-error', libname)

            elif not pkg.name[-1:].isdigit():
                printError(pkg, 'shlib-policy-missing-suffix')

        if (not pkg.name.startswith('lib')) or pkg.name.endswith('-lang'):
            return

        if not libs:
            if pkg.name in _policy_legacy_exceptions:
                printWarning(pkg, 'shlib-legacy-policy-missing-lib', pkg.name)
            else:
                printError(pkg, 'shlib-policy-missing-lib')

        # Verify no non-lib stuff is in the package
        dirs = set()
        for f in files:
            if os.path.isdir(pkg.dirName() + f):
                dirs.add(f)

        # Verify shared lib policy package doesn't have hard dependency on non-lib packages
        if std_lib_package:
            for dep in pkg.requires():
                if (dep[0].startswith('rpmlib(') or dep[0].startswith('config(')):
                    continue
                if (dep[1] & (rpm.RPMSENSE_GREATER | rpm.RPMSENSE_EQUAL)) == rpm.RPMSENSE_EQUAL:
                    printWarning(pkg, "shlib-fixed-dependency", Pkg.formatRequire(dep[0], dep[1], dep[2]))

        # Verify non-lib stuff does not add dependencies
        if libs:
            for dep in pkg_requires.difference(_essential_dependencies):
                if '.so.' in dep and dep not in libs and dep not in libs_needed:
                    printError(pkg, 'shlib-policy-excessive-dependency', dep)

        # Check for non-versioned directories beyond sysdirs in package
        sysdirs = ('/lib', '/lib64', '/usr/lib', '/usr/lib64',
                   '/usr/share', '/usr/share/licenses',
                   '/usr/share/doc/packages')
        cdirs = set()
        for sysdir in sysdirs:
            done = set()
            for dir in dirs:
                if dir.startswith(sysdir + '/'):
                    ssdir = str.split(dir[len(sysdir) + 1:], '/')[0]
                    if not ssdir[-1].isdigit():
                        cdirs.add(sysdir + '/' + ssdir)
                    done.add(dir)
            dirs = dirs.difference(done)
        map(lambda dir: printError(pkg, 'shlib-policy-nonversioned-dir', dir), cdirs)


check = LibraryPolicyCheck()

if Config.info:
    addDetails(
'shlib-policy-missing-suffix',
"""Your package containing shared libraries does not end in a digit and
should probably be split.""",
'shlib-policy-devel-file',
"""Your shared library package contains development files. Split them into
a -devel subpackage.""",
'shlib-policy-name-error',
"""Your package contains a single shared library but is not named after its SONAME.""",
'shlib-policy-nonversioned-dir',
"""Your shared library package contains non-versioned directories. Those will not
allow to install multiple versions of the package in parallel.""",
'shlib-legacy-policy-name-error',
"""Your shared library package is not named after its SONAME, but it has been added to the list
of legacy exceptions. Please do not rename the package until SONAME changes, but if you have
to rename it for another reason, make sure you name it correctly.""",
'shlib-policy-excessive-dependency',
"""Your package starts with 'lib' as part of its name, but also contains binaries
that have more dependencies than those that already required by the libraries.
Those binaries should probably not be part of the library package, but split into
a seperate one to reduce the additional dependencies for other users of this library.""",
'shlib-policy-missing-lib',
"""Your package starts with 'lib' as part of its name, but does not provide
any libraries. It must not be called a lib-package then. Give it a more
sensible name.""",
'shlib-fixed-dependency',
"""Your shared library package requires a fixed version of another package. The
intention of the Shared Library Policy is to allow parallel installation of
multiple versions of the same shared library, hard dependencies likely make that
impossible. Please remove this dependency and instead move it to the runtime uses
of your library.""",
'shlib-unversioned-lib',
"""Your package matches the Shared Library Policy Naming Scheme but contains an
unversioned library. Therefore it is very unlikely that your package can be installed
in parallel to another version of this library package. Consider moving unversioned
parts into a runtime package."""
)
