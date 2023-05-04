#__all__ = ['GBM','LAT','GRB','Detector','FTmerge','plotter','genutils','latutils','XSPEC']
import pyIrfLoader
import os,sys
#import BKGE_Tools
import Detector
import GRB
import LAT
import GBM
from GtGRB_IO import *
import autofit
import math
import astropy.io.fits as pyfits
import time
import sunpos

logfile='gtgrb-%s.log'%time.strftime('%Y-%m-%d')

def checkROOT():
    import ROOT
    try:
        if os.environ['ROOTISBATCH']=='YES':
            ROOT.gROOT.SetBatch(True)
            print 'ROOT is Set in batch mode'
            print 'Unset the variable ROOTISBATCH to turn on graphical output'
            pass
        pass
    except:
        pass
    
    
def checkST():
    status='OK'
    try :
        #too basic!
        import UnbinnedAnalysis
    except:
        status= '*****FAILED*****'
        os.environ['NOST'] = ''
    print 'Testing loading UnbinnedAnalysis.... %s'% status 
    return
    
def checkHEA():
    #print "checking HEASARC installation..."
    return

def banner():
    print '*****************************************************'
    print '* WELCOME TO THE GLAST GRB QUICK ANALYSIS FRAMEWORK *'
    print '* BASED ON PYTHON and the GLAST ScienceTools        *'
    print '* For Question and Troubleshooting:                 *'
    print '*       nicola.omodei@slac.stanford.edu             *'
    print '*****************************************************'
    pass

def set_log():
    if os.getenv('LOGS') is None:
        os.environ['LOGS']=os.path.join(os.environ['PWD'],'logfiles')
        pass
    if not os.path.exists(os.environ['LOGS']):
        os.mkdir(os.environ['LOGS'])
        pass
    pass
banner()
set_log()

checkST()
checkHEA()
checkROOT()
