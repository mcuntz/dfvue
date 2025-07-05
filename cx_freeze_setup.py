#!/usr/bin/env python
r'''
Make stand-alone version of dfvue with cx_Freeze.

On macOS, use minimal virtual environment
   if [[ "$(uname -m)" == "arm64" ]] ; then
       export OPENBLAS="$(brew --prefix openblas)"
   fi
   pyenv virtualenv 3.12.8 dfvue-install
   pyenv local dfvue-install
   # or:
   # pyenv virtualenv 3.12.8 dfvue-install-ctkinter
   # pyenv local dfvue-install-ctkinter
   pyenv rehash
   python -m pip install -r requirements.txt
   # if dfvue-install-ctkinter:
   #     python -m pip install customtkinter
   python -m pip install -ve ./
   python -m pip install cx_freeze

Check in Windows Powershell
    $env:PYTHONPATH = "C:/Users/mcuntz/prog/github/dfvue"
    python -m dfvue
Executable for testing
    python cx_freeze_setup.py build
macOS app
    python cx_freeze_setup.py bdist_mac
macOS dmg
    python cx_freeze_setup.py bdist_dmg
    cd build
    xcrun notarytool submit dfvue-6.2.aqua.intel.dmg --keychain-profile "notarytool-password"
    xcrun notarytool log 6d0cb58d-867d-4f91-a3e6-98c27c58f3e9 --keychain-profile "notarytool-password" developer_log.json
    xcrun stapler staple dfvue-6.2.aqua.intel.dmg
    scp dfvue-6.2.aqua.intel.dmg macu.de@ssh.strato.de:extra/
Windows installer
    python cx_freeze_setup.py bdist_msi

'''
import os
import codecs
import re
import sys
import glob
import shutil

from cx_Freeze import setup, Executable


# find __version__
def _iread(*fparts):
    ''' Read file data. '''
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *fparts), 'r') as fp:
        return fp.read()


def _find_version(*file_paths):
    '''Find version without importing module.'''
    version_file = _iread(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


package   = 'dfvue'
doclines  = 'A minimal GUI for a quick view of csv files'
author    = 'Matthias Cuntz'
copyright = 'Copyright (c) 2023-2024 Matthias Cuntz - mc (at) macu (dot) de'

version = _find_version('src/' + package, '_version.py')

script        = 'src/dfvue/__main__.py'
packages      = []  # others detected automatically
excludes      = ['pyflakes', 'mccabe', 'pycodestyle', 'flake8',  # flake8
                 'gtk', 'PyQt4', 'PyQt5', 'wx']                  # matplotlib
includes      = []
# no need to include images and themes because dfvue gets installed as module
# include_files = [('dfvue/images', 'images'), ('dfvue/themes', 'themes')]
include_files = []

if sys.platform == 'win32':
    base = 'Win32GUI'
    exe  = 'dfvue.exe'
    icon = 'src/dfvue/images/dfvue_icon.ico'
    msvcr = True
    shortcutname = 'dfvue'
    shortcutdir  = 'ProgramMenuFolder'
elif sys.platform == 'darwin':
    base = None
    exe  = 'dfvue'
    icon = 'docs/images/dfvue_icon.icns'
    msvcr = False
    shortcutname = 'dfvue'
    shortcutdir  = None
else:
    base = None
    exe  = 'dfvue'
    icon = 'src/dfvue/images/dfvue_icon.ico'
    msvcr = False
    shortcutname = 'dfvue'
    shortcutdir  = None

build_exe_options = {'packages': packages,
                     'excludes': excludes,
                     'includes': includes,
                     'include_files': include_files,
                     'include_msvcr': msvcr}

executables = [Executable(script,
                          target_name=exe,
                          copyright=copyright,
                          base=base,
                          icon=icon,
                          shortcut_name=shortcutname,
                          shortcut_dir=shortcutdir)]

# Check codesign
#     spctl -a -t exec -vvv build/dfvue.app
bdist_mac_options = {
    'iconfile': icon,
    'bundle_name': package,
    # Create certificate
    #     https://developer.apple.com/help/account/create-certificates/create-developer-id-certificates
    # Check ID (Team ID is in parenthesis)
    #     security find-identity -p codesigning -v
    'codesign_identity': 'MATTHIAS OSKAR CUNTZ (R5T7LWQ224)',
    'codesign_options': 'runtime',  # Ensure codesign uses 'hardened runtime'
    'codesign_verify': True,  # Get more verbose logging for codesign
    'spctl_assess': False,  # rejects codesign because not notarized yet
    'plist_items': [('NSPrincipalClass', 'NSApplication'),
                    ('NSHighResolutionCapable', True)]
}

# Install intermediate certificates as in answer of FrostyBagg on
#     https://forums.developer.apple.com/forums/thread/86161
# Do not change the trust settings.
#     xcrun notarytool submit dfvue-5.1.dev1.dmg --keychain-profile "notarytool-password" --wait
# Check codesign
#     spctl -a -t open -vvv --context context:primary-signature build/dfvue-5.1.dev1.dmg
bdist_dmg_options = {
    'applications_shortcut': True
}

bdist_msi_options = {
    'add_to_path': True,
    'all_users': True,
    'data': {'ProgId': [('Prog.Id', None, None, doclines,
                         'IconId', None)]},
    'summary_data': {'author': author,
                     'comments': doclines,
                     'keywords': 'visualisation pandas data-visualization quickcheck'},
    'install_icon': icon}

setup(name=package,
      version=version,
      description=doclines,
      options={'build_exe': build_exe_options,
               'bdist_mac': bdist_mac_options,
               'bdist_dmg': bdist_dmg_options,
               'bdist_msi': bdist_msi_options},
      executables=executables,
      )
