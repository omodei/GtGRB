# -*- python -*-
# $Id: SConscript,v 1.52 2014/08/27 18:23:33 omodei Exp $
# Authors: Nicola Omodei <omodei@slac.stanford.edu>, Giacomo Vianello <giacomov@slac.stanford.edu>
# Version: GtGRB-01-13-03

Import('baseEnv')
Import('listFiles')
progEnv = baseEnv.Clone()
##libEnv  = baseEnv.Clone()

# Uncomment to install python files.  Replace
# listFiles(['.. with an actual list to only install
# some of the files
progEnv.Tool('registerTargets', package = 'GtGRB',
             python = listFiles(['python/GTGRB/*.py',\
                                 'python/app/*.py',\
                                 'python/app/*.sh',\
                                 'python/app/*.csh',\
                                 'python/pipeline/*.py',\
                                 'python/scripts/*.py']),
             pfiles = listFiles(['pfiles/*.par']) )

