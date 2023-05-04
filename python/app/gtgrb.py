#!/usr/bin/env python
import matplotlib
matplotlib.use('Agg')
import pyIrfLoader
from GTGRB import *
import commands,pyfits,numpy
import sys,time
import glob
import ROOT
import UnbinnedAnalysis
from UnbinnedAnalysis import pyLike
#import scripts.GRBs as grbs
from scripts import getGBMTriggers
from math import *
import shutil, shlex, subprocess
from GTGRB import autofit
from GTGRB import genutils
from GTGRB.genutils import runShellCommand
from GTGRB import setROOTStyle
from GTGRB import commandDefiner
from GTGRB import guiParameters
#from LLE import *
from GTGRB import latutils,genutils
import makeLLEproducts
import os, subprocess
import GtApp
import socket
from GTGRB import commandDefinitions
from GTGRB.guiParameters import *
import collections
#Set up the GBM package
import GBMtools
dumpdir         =  os.path.join(os.environ['BASEDIR'],'gtgrb_data/GBMtoolsDumps')
GBMtools.setDataPath(dumpdir)

#First thing define the custom exception handler
def custom_exc(shell, etype, evalue, tb, tb_offset=None):
    # My exception handling:
    #Flush stdout so the exception is always shown at the end
    #(even in the notebook)
    sys.stdout.flush()
    if(os.environ.get('GUIPARAMETERS')=='yes'):
      import Tkinter
      from tkMessageBox import showerror
      root = Tkinter.Tk()
      root.withdraw()
      showerror("Error","An error occurred:\n\n%s\n\nSee the output of the last executed command for more details." %(evalue))
      root.destroy()
    else:
      #Do nothing particular, the output from IPython is enough
      pass
    # also do what IPython would have done, if you want:
    shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)

# Tell IPython to use it for any/all Exceptions:
try:
  get_ipython().set_custom_exc((Exception,), custom_exc)
except:
  #Maybe we are not running in ipython after all... (for example,
  #we have been called in a script)
  pass

##################################################
# THIS IS QUITE COOL: IT FORCES ALL THE "print" statement to be flushed
class flushfile(object):
    def __init__(self, f):
        self.f = f
        pass
    def write(self, x):
        self.f.write(x)
        self.f.flush()            
        pass
    pass

#import sys
#sys.stdout = flushfile(sys.stdout)
##################################################

print '------------------------------------------------------------------------------------------'
print "current working directory: ", os.path.abspath(os.curdir)
print '------------------------------------------------------------------------------------------'
ROOT.gStyle.SetOptStat(0)
try:
    ROOT.gSystem.Load('librootIrfLoader')
    ROOT.gSystem.Load('libBKGE')
    ROOT.gSystem.Load('libDurationEstimator')
    from ROOT import TOOLS, BackgroundEstimator
    TOOLS.Set("GRB_NAME","") #this is to create the datadir directory of the bkg estimator (kluge)
    TOOLS.Set("BASEDIR",os.environ['BASEDIR'])
except:
    print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    print '                  BackgroundEstimator not available                      '
    print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    pass

try:
    lle_dir       = os.environ['LLEPIPELINE']
except:
    lle_dir       = os.environ['LLE_DIR']
    pass
print ' LLE Dir: ',lle_dir

try:
    ROOT.gSystem.Load('libLLE')
except:
    print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    print '                  LLE lib not available                      '
    print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    pass

##################################################
#ROOT.gROOT.LoadMacro('%s/%s' % (os.environ['GTGRB_DIR'],'GTGRB/rootlogon.C'))

ROOT.gStyle.SetFillStyle(1)
ROOT.gStyle.SetHistFillStyle(0)
##################################################


MeV2erg                       = 1.60217646e-6

results                       = collections.OrderedDict()

lat                           = [None]
grb                           = [None]

globalQueryMode               = "query"

def UpdatePosition(new_ra,new_dec):
    print 'Udate the position: (%s,%s) -> (%.3f,%.3f)' %(results['RA'],
                                                         results['DEC'],
                                                         new_ra,
                                                         new_dec)
    results['RA']               = new_ra
    results['DEC']              = new_dec
    grb[0].ra                   = results['RA']
    grb[0].dec                  = results['DEC']
    pass

def Help(command=None,forceNoGui=False):
    if(os.environ.get('GUIPARAMETERS')=='yes' and forceNoGui==False):
      helpGUI(commandDefinitions.commands,command)
    else:  
      if(command!=None):
        if(command in commandDefinitions.commands.keys()):
          commandDefinitions.commands[command].getHelp()
        else:
          raise ValueError("Command not found: %s" %(command))
        pass
      else:
        for k,v in commandDefinitions.commands.iteritems():
          print("\n")
          v.getHelp()
          print("\n")
        pass
      pass  
    pass
pass

def cmdlineHelp():
    txt='''
    NAME
         gtgrb.py -- Fermi LAT GRB analysis framework
    SYNOPSIS
         gtgrb.py [-nox -go -exe <filename> -list -Help [var=val]]
    DESCRIPTION
                
    OPTIONS
        -nox
        \t disable the x11 forwarding
        -go
        \t Execute the jiob without asking (see the pfiles for input parameters)
        -l -list
        \t list all the GRB in the database
        -exe app/test.py
        \t run the program called app/test.py (see in the folder app/ for more scripts)
        -H -Help
        \t print the commnd line help

        you can set variables using the sintax var=val, where var is the name of the variable, val is its value.
        
    Loading this module in python (or ipython) the following methods are accessible:'''
#    GRBNames(filter=None)    
#    \t return all the list of GRB
#    Set(grbname=grbname,mode='ql')
#    \t inizialize the analysis. If <grbname> is provided it loads default value for the given GRB.
#    Mode set to 'ql' run the analisis taking all the default values in the gtgrb.par pfile.
#    This function also set the FT1 and FT2 file. If there are no file available in the INDIR, the code
#    download them using the astroserver. gtmktime is also applied.
#    PlotAngularSeparation()
#    \t Plot the distance of the GRB from the local zenit and from the spacecraft z axis (LAT boresight)
#    GetGBMFiles()
#    \t Download GBM file, using wget.
#    MakeGBMLightCurves()
#    \t Make the GBM light curve.
#    MakeSelect()
#    \t Select the LAT data using gtselect. LightCurve and sky map is also displayed.
#    MakeSelectEnergyDependentROI()
#    \t Select the LAT events that are compatible with 95% containment radius, from the Point Spread Function.
#    MakeGtFindSrc()
#    \t optimize the position of the GRB looking at LAT burst.
#    CalculateBackground()
#    \t Compute the background using the BGKE code by Vlasios
#    CalculateLATT90()
#    \t Use the background estimator to compute the LAT duration.
#    MakeComputePreburstBackground()
#    \t compute the preburst background
#    MakeLikelihoodAnalysis()
#    \t Make a likelihood analysis during the GRB duration.        
#    Print()
#    \t Print the current result on the screen and on a file in the output directory (default DATA/GRBOUT/GRBYYMMAAFFF/gtgrb_results.txt
#    Done()
#    \t close all the open files and save the results.

#    type ?<command> to see more text
#    '''
    print txt
    Help(forceNoGui=True)
    pass

def switchToNotInteractiveExecution():
    global globalQueryMode
    globalQueryMode = 'go'
pass

def switchToInteractiveExecution():
    global globalQueryMode
    globalQueryMode = 'query'
pass

def forceNonInteractive(kwargs):
    #This returns a copy of the input dictionary,
    #with the 'mode' keyword set to 'go'
    newDict                 = kwargs.copy()
    queryKey                = filter(lambda x:x.lower()=='mode',newDict.keys())
    if(queryKey==[]):
      newDict['mode']       = 'go'
    else:
      newDict[queryKey[0]]  = 'go'
    pass
    return newDict
pass

def harvestParameters(thisCommand,kwargs):
    try:
      queryKey                = filter(lambda x:x.lower()=='mode',kwargs.keys())
      if(queryKey==[]):
        queryMode             = globalQueryMode
      else:
        queryMode             = kwargs[queryKey[0]]
      pass  
      thisCommand.harvestParameters(kwargs,results,queryMode)      
    except commandDefinitions.UserError as error:
      raise RuntimeError(error.message)
pass

'''
def CalculateLATT90(**kwargs):
    thisCommand               = commandDefinitions.commands['CalculateLATT90']
    harvestParameters(thisCommand,kwargs)
    chatter,Emin,Emax,WeighByExposure,overwrite,CrossGTIs = thisCommand.getParameters("chatter,Emin,Emax,WeighByExposure,overwrite,CrossGTIs")
    
    if WeighByExposure==True and CrossGTIs==True:
        print "Cannot use CrossGTIs==True and WeighByExposure==True at the same time."
	return

    if (Emin<=0): Emin = 50.0 #float(results['EMIN'])
    if (Emax<=0): Emax = 300000.0 #float(results['EMAX'])
    if chatter>1 : TOOLS.PrintConfig()
    
    DurationOK = True
    from ROOT import DurationEstimator
    myDurationEstimator = DurationEstimator(lat[0].FilenameFT1, lat[0].FilenameFT2, lat[0]._ResponseFunction, grb[0].Ttrigger, grb[0].Name, Emin, Emax, chatter,WeighByExposure,CrossGTIs,overwrite)
    
    
    if myDurationEstimator.CalculateLATT90()<0 : DurationOK=False
    else : 
        ROOTFile = ROOT.TFile(myDurationEstimator.ResultsRootFilename,'OPEN')    
        if ROOTFile.ErrorCode!=None:  DurationOK=False
        pass
    
    FailedFraction           = myDurationEstimator.FailedFraction
    print '--------------------------------------------------'
    #print ' --- CalculateLATT90. FailedFraction = %.2f' % FailedFraction
    #print ' ---                  DurationOK     = %s' % DurationOK
    
    ROOTFile = ROOT.TFile(myDurationEstimator.ResultsRootFilename,'OPEN')
    
    if DurationOK:
        print ' --- The duration computation was succesful. Get the value from the TNamed object...'
        
        T05_T95_T90   = ROOTFile.f_MED_T05_T95_T90.GetTitle().split('_')
        UT05_T95_T90  = ROOTFile.f_UL_T05_T95_T90.GetTitle().split('_')
        LT05_T95_T90  = ROOTFile.f_LL_T05_T95_T90.GetTitle().split('_')
        
        BKGET05 = float(T05_T95_T90[0])
        BKGET95 = float(T05_T95_T90[1])
        BKGET90 = float(T05_T95_T90[2])
        BKGET05U = float(UT05_T95_T90[0])
        BKGET95U = float(UT05_T95_T90[1])
        BKGET90U = float(UT05_T95_T90[2])
        BKGET05L = float(LT05_T95_T90[0])
        BKGET95L = float(LT05_T95_T90[1])
        BKGET90L = float(LT05_T95_T90[2])
        
        if (FailedFraction>0.2):
            print '--->   The BKGE Duration Estimate is likely a lower limit (failed fraction=%.2f)' %FailedFraction
            pass
        pass
    else:        
        print ' --- The duration computation was NOT succesful....'
        try:
            ProcessedUntilTime       = float(ROOTFile.ProcessedUntilTime.GetTitle())
        except:
            ProcessedUntilTime       = 0.0
            pass        
        print '                 ProcessedUntilTime=',ProcessedUntilTime
        print '                 ReportedError     =',ROOTFile.ErrorCode.GetTitle()
        
        BKGET05L = 0.0
        BKGET95L = ProcessedUntilTime 
        try:
    	    LT05_T95_T90  = ROOTFile.f_LL_T05_T95_T90.GetTitle().split('_')
    	    BKGET05L = float(LT05_T95_T90[0])
            BKGET95L = float(LT05_T95_T90[1])
	except:  pass
        
        BKGET05  = BKGET05L
        BKGET95  = BKGET95L
        BKGET90  = BKGET95-BKGET05
        BKGET05U = BKGET05
        BKGET95U = BKGET95
        BKGET90U = BKGET90
        BKGET90L = BKGET90
        pass
    
    results['BKGE_FailedFraction'] = FailedFraction
    results['BKGE_DurationOK']     = DurationOK
    results['BKGET05']  = BKGET05
    results['BKGET95']  = BKGET95
    results['BKGET90']  = BKGET90
    results['BKGET05U'] = BKGET05U
    results['BKGET95U'] = BKGET95U
    results['BKGET90U'] = BKGET90U
    results['BKGET05L'] = BKGET05L
    results['BKGET95L'] = BKGET95L
    results['BKGET90L'] = BKGET90L
    
    print '**************************************************'
    print '---> ONSET AND DURATION RESULTS OF THE BACKGROUND ESTIMATOR (BKGE)'
    print '---> Burst Name..............: %s'   % results['GRBNAME']
    print '---> BKGE FailedFraction.....: %.2f' % results['BKGE_FailedFraction']
    print '---> BKGE DurationOK.........: %s'   % results['BKGE_DurationOK']
    print '---> BKGE T05................: MED %s UL %s LL %s sec' % (BKGET05, BKGET05U,BKGET05L)
    print '---> BKGE T95................: MED %s UL %s LL %s sec' % (BKGET95, BKGET95U,BKGET95L)
    print '---> BKGE T90................: MED %s UL %s LL %s sec' % (BKGET90, BKGET90U,BKGET90L)
    print '---> GBM T05.................: %s sec' % results['GBMT05']
    print '---> GBM T95.................: %s sec' % results['GBMT95']
    print '---> GBM T90.................: %s sec' % results['GBMT90']
    print '**************************************************'
    ROOTFile.Close()    
    pass
'''

'''
def CalculateBackground(**kwargs):
    import BKGE_interface
    BKGE_interface.setResponseFunction(lat[0]._ResponseFunction)

    thisCommand               = commandDefinitions.commands['CalculateBackground']
    harvestParameters(thisCommand,kwargs)
    chatter,emin,emax,ebins,overwrite,start,stop,MaxROIRadius = thisCommand.getParameters("chatter,emin,emax,ebins,overwrite,start,stop,MaxROIRadius")
    print 'chatter=',chatter
    return BKGE_interface.CalculateBackground(start,stop,
                                              grb_trigger_time=lat[0].GRB.Ttrigger+start,
                                              RA=lat[0].GRB.ra, DEC=lat[0].GRB.dec,
                                              FT1=lat[0].FilenameFT1,
                                              FT2=lat[0].FilenameFT2,
                                              OUTPUT_DIR=lat[0].out_dir,
                                              emin=emin,emax=emax,
                                              EvaluateMaps=False,
                                              ROI_Calculate=0,
                                              ROI_Max_Radius=MaxROIRadius,
                                              GRB_NAME=lat[0].GRB.Name,
                                              chatter=chatter)


'''

'''
def Make_BKG_PHA2(**kwargs):
    import BKGE_interface
    thisCommand               = commandDefinitions.commands['Make_BKG_PHA2']
    harvestParameters(thisCommand,kwargs)
    chatter,emin,emax,ebins,overwrite,start,stop,dt,bindef,flat_roi = thisCommand.getParameters("chatter,emin,emax,ebins,overwrite,start,stop,dt,bindef,flat_roi")
    if flat_roi==1:
        ROI_Calculate=0
        ROI_MAX_RADIUS=lat[0].radius
    else:
        ROI_Calculate=0
        ROI_MAX_RADIUS=12
        pass
    
    if suffix=='' and flat_roi==1:     suffix='_ROI'
    elif suffix=='' and flat_roi==0:   suffix='_ROI_E'
    
    return BKGE_Tools.Make_BKG_PHA2(grb_trigger_time=lat[0].GRB.Ttrigger+start,
                                    RA=lat[0].GRB.ra, DEC=lat[0].GRB.dec,
                                    FT1=lat[0].FilenameFT1,
                                    FT2=lat[0].FilenameFT2,
                                    emin=emin,emax=emax,ebins=ebins,                                    
                                    EvaluateMaps=False,
                                    ROI_Calculate=ROI_Calculate,                                    
                                    ROI_Max_Radius=ROI_MAX_RADIUS,
                                    ROI_Radius=ROI_MAX_RADIUS,
                                    OUTPUT_DIR=lat[0].out_dir,
                                    GRB_NAME=lat[0].GRB.Name,
                                    chatter=chatter)
'''

'''
def Make_BKG_PHA(**kwargs):
    import BKGE_interface
    BKGE_interface.setResponseFunction(lat[0]._ResponseFunction)

    thisCommand               = commandDefinitions.commands['Make_BKG_PHA']
    harvestParameters(thisCommand,kwargs)
    chatter,emin,emax,ebins,start,stop,flat_roi,suffix = thisCommand.getParameters("chatter,emin,emax,ebins,start,stop,flat_roi,suffix")
    
    if flat_roi==1:
        ROI_Calculate=0
        ROI_MAX_RADIUS=lat[0].radius
    else:
        ROI_Calculate=0
        ROI_MAX_RADIUS=12
        pass
    
    if suffix=='' and flat_roi==1:     suffix='_ROI'
    elif suffix=='' and flat_roi==0:   suffix='_ROI_E'
    detector='ROI'
    if flat_roi==0: detector='ROI_E'
    
    out_dir    = lat[0].out_dir+'/' + suffix
    runShellCommand('mkdir -p %s' % out_dir)
    bak_file   = out_dir+'/'+lat[0].grb_name+'_LAT_'+detector+'_%.2f_%.2f.bak' %(start,stop)
    
    
    bak_file_0=BKGE_interface.Make_BKG_PHA(start,stop,
                                           grb_trigger_time=lat[0].GRB.Ttrigger+start,
                                           RA=lat[0].GRB.ra, DEC=lat[0].GRB.dec,
                                           FT1=lat[0].FilenameFT1,
                                           FT2=lat[0].FilenameFT2,
                                           emin=emin,emax=emax,ebins=ebins,
                                           OUTPUT_DIR=lat[0].out_dir,                
                                           ROI_Calculate=ROI_Calculate,
                                           ROI_Max_Radius=ROI_MAX_RADIUS,
                                           GRB_NAME=lat[0].GRB.Name,
                                           chatter=chatter)
    runShellCommand('mv %s %s' % (bak_file_0,bak_file))
    return bak_file
'''

# def Prompt(parameters, mode='ql'):
#    ''' Reads the parameters in @par parameters and prompt them using the pfile interface '''
#    
#    for item in parameters:
#        if item in commandLineArguments: #1 Check if the item is in the list of command line arguments
#            try:
#                results[item] = float(commandLineArguments[item]) # this overwrite the parameters with the one passed from the command line
#            except:
#                if commandLineArguments[item].lower()=='y' or commandLineArguments[item].lower()=='yes':  commandLineArguments[item] = 1
#                elif commandLineArguments[item].lower()=='n' or commandLineArguments[item].lower()=='no':   commandLineArguments[item] = 0            
#                results[item] = commandLineArguments[item] # this overwrite the parameters with the one passed from the command line
#                pass
#            # pargroup[item] = results[item]
#            pass
#        else:            
#            if mode=='ql':
#                try:
#                    pargroup.Prompt(item)      # query the parameters          
#                except:
#                    print '%s not in pfiles' % item                
#                    continue
#                pass
#            
#            try: results[item] = float(pargroup[item]) # or used the passed parameter, or read the parameter from the pfile.
#            except ValueError:  results[item] = pargroup[item]   # or used the passed parameter, or read the parameter from the pfile.            
#            pass
#        pass
#    pargroup.Save()
#    pass

def GRBNames(filter='None'):
  ''' returns a dictionary of GBM GRB names (from online GBM GRB catalog)
  You can pass a filter as parameter like:
  GRBNames() will return only the names that contains
  '''    
  known_grbs              = getGBMTriggers.downloadListGRB() # grbs.GRBs
  #for k in sorted(known_grbs.keys()): print k,known_grbs[k]
  #print known_grbs.keys()
  #grbs.PrintGRBs(filter)
  return known_grbs

def TriggerNames(filter='None'):
  ''' returns a dictionary of GBM triggers (from online GBM trigger catalog)
  You can pass a filter as parameter like:
  TriggerNames() will return only the names that contains
  '''    
  known_grbs              = getGBMTriggers.downloadListTrigger() # grbs.GRBs
  #for k in sorted(known_grbs.keys()): print k,known_grbs[k]
  #print known_grbs.keys()
  #grbs.PrintGRBs(filter)
  return known_grbs


def SetVar(var,val):
  ''' This function is use to set the value of a variable
  \t var is the name of the variable
  \t val is its value
  '''
  
  if var not in results.keys():
    print 'WARNING: Variable %s is not in the parameter dictionary. Will be added! Available variables are:' % var
    print results.keys()
    pass
  try:
    results[var] = float(val)
  except:
    results[var] = val
    pass    
  print 'Variable %s = %s [Run SetGRB() to make it effective.]' %(var,val)
  pass

def ListToDict(myList):
  ''' Convert a list of the type of <var=val,...> into a dictionary '''
  dict                      = collections.OrderedDict()
  for elem in myList:
    try:
      vars = elem.split('=')
      dict[vars[0].replace(" ","")] = vars[1]
      #dict[vars[0].replace(" ","").upper()] = vars[1]
    except:
      pass
    pass
  return dict

def convertToUppercase(inp):
  ''' Convert dictionary keys to upper case
  '''
  new                         = {}
  for k,v in inp.iteritems():
    new[k.upper()]            = v
  pass
  return new

def Set(**kwargs):
    #This is to get rid of all saved plots/histograms (if any)
    ROOT.gROOT.Reset()    
    results.clear() # clean the dictionary
    #First of all copy all the keywords in the results dictionary. This allow the user to set at this stage
    #values for parameters for following commands, even if they are not known to the Set command
    for k,v in kwargs.iteritems():
        if k == 'GRBNAME': 
            results[k]   = v
        else:
            try:    results[k]              = float(v)
            except: results[k]              = v
            pass
        pass
    #If mode='go' in Set() then switch to non-interactive mode
    queryKey                = filter(lambda x:x.lower()=='mode',results.keys())
    if(queryKey!=[] and results[queryKey[0]]=='go'):
        switchToNotInteractiveExecution()
        pass
    
    #Convert kwargs to upper case
    kwargs = convertToUppercase(kwargs)
    #Look if GRBname has been set in the kwargs, if yes and it is contained
    #in the database, fill all the known quantities (they won't be prompted again)
    #if('GRBNAME' in kwargs.keys()):        
    #    # Look for the GRB in the database
    #    known_grbs              = getGBMTriggers.downloadListGRB() # grbs.GRBs
    #    if kwargs['GRBNAME'] in known_grbs.keys():        
    #        print("\nFound %s in the GRB database\n" %(kwargs['GRBNAME']))
    #        _my_grb=known_grbs[kwargs['GRBNAME']]
    #        kwargs['GRBTRIGGERDATE']=_my_grb[0]
    #        kwargs['RA']=_my_grb[1]
    #        kwargs['DEC']=_my_grb[2]
    #        kwargs['ERR']=_my_grb[3]
    #        kwargs['GBMT90']=_my_grb[4]
    #        kwargs['GBMT05']=_my_grb[5]        
    #        kwargs['GRBT90']=_my_grb[4]
    #        kwargs['GRBT05']=_my_grb[5]        
    #        # for k,v in known_grbs[kwargs['GRBNAME']].iteritems():
    #        #  if k=='ERR' and known_grbs[kwargs['GRBNAME']]['LOCINSTRUMENT']=='GBM':
    #        #        kwargs[k]     = sqrt(v*v+9.0)
    #        #        print 'Loc instrument is GBM. Adding 3 degrees of sys error in quadrature. The new error is:',  kwargs[k]
    #        #  else:
    #        #    kwargs[k]           = v
    #        # pass
    #    else:
    #        known_grbs              = getGBMTriggers.downloadListTrigger() # grbs.GRBs
    #        if kwargs['GRBNAME'] in known_grbs.keys():
    #            print("\nFound %s in the Trigger database\n" %(kwargs['GRBNAME']))
    #            _my_grb=known_grbs[kwargs['GRBNAME']]
    #            kwargs['GRBTRIGGERDATE']=_my_grb[0]
    #            kwargs['RA']=_my_grb[1]
    #            kwargs['DEC']=_my_grb[2]
    #            kwargs['ERR']=_my_grb[3]
    #            kwargs['GBMT90']=_my_grb[4]
    #            kwargs['GBMT05']=_my_grb[5]        
    #            kwargs['GRBT90']=_my_grb[4]
    #            kwargs['GRBT05']=_my_grb[5]   
    #            pass
    #        else:
    #            print("%s is not a valid GRB name. Use GRBNames() to have a list" %(kwargs['GRBNAME']))	
    #            pass
    #        pass
    #    pass
    try:
        thisCommand               = commandDefinitions.commands['Set']
        harvestParameters(thisCommand,kwargs)
    except commandDefinitions.UserError as error:
        print(error.message)
        return

    try:
        float(results['GRBTRIGGERDATE'])
    except:
        print 'Sorry, You must provide either a BURST name or a MET.'
        print 'To see the list of saved GRB: GRBNames() '
        print '  or run gtgrb from the command line with the option -l'
        return 1
    
    results['GBMT90']          = float(results['GRBT90'])
    results['GBMT05']          = float(results['GRBT05'])
    results['GBMT95']          = float(results['GBMT90']+results['GBMT05'])
    results['GRBT95']          = float(results['GBMT95'])
    try: results['GBMT90_ERR'] = float(results['GRBT90_ERR'])      
    except: results['GBMT90_ERR']   = 0.0

    results['GRBT90_ERR']   = results['GBMT90_ERR']
    cmdline='Set('
    for k in results.keys():
        if isinstance(results[k],str):
            cmdline+='%s="%s",'%(k,results[k])
        else:
            cmdline+='%s=%s,'%(k,results[k])
            pass
        pass    
    cmdline=cmdline[:-1]
    cmdline+=')'
    print cmdline
    SetGRB(**results)
    pass

def SetFromName(**kwargs):
    grbs=GRBNames()
    kwargs = convertToUppercase(kwargs)
    try:_my_grb=grbs[kwargs['GRBNAME']]
    except: return None
    kwargs['GRBTRIGGERDATE']=_my_grb[0]
    kwargs['RA']=_my_grb[1]
    kwargs['DEC']=_my_grb[2]
    kwargs['ERR']=_my_grb[3]
    kwargs['GRBT90']=_my_grb[4]
    kwargs['GRBT05']=_my_grb[5]
    Set(**kwargs)
    return _my_grb

# #################################################
# THIS START THE SETTINGS OF THE PARAMETERS
# #################################################
def SetGRB(**kwargs):
    ''' This methods propagate the parameters to the various methods.
    Looks for the FT1 and FT2 files, and initialize the run'''
    
    #print 'SetGRB: ', kwargs
    chatter = 1 # controls verbosity
    quick=False

    #decide on deltat
    deltat = 3*3600
        
    #if you are not running at SLAC then the data files might be too big to transfer
    #in that case do not +-1 day around the GRB, but just +-5 hrs
    #The deltat is overridable by a deltat Set() argument. 
    
    if  socket.getfqdn().find("slac.stanford.edu")==-1:  deltat=3*3600
    deltat=max(deltat,results['GRBT95'])
    if 'TSTOP' in results.keys(): deltat=max(deltat,results['TSTOP'])
    if 'EXTENDED_TSTOP' in results.keys(): deltat=max(deltat,results['EXTENDED_TSTOP'])
    if 'AFTER' in results.keys(): deltat=max(deltat,results['AFTER'])

    gtmktimecut = None
    for key in kwargs.keys():
        if key.lower()=="chatter":       chatter      = kwargs[key]
        elif key.lower()=="quick":       quick        = kwargs[key]
        elif key.lower()=="gtmktimecut": gtmktimecut  = kwargs[key]
        elif key.lower()=="deltat":      deltat       = float(kwargs[key])
        pass
    if 'GRBNAME' in results.keys(): grb_name=results['GRBNAME']
    else:                           grb_name=''
    grb[0]                   = GRB.GRB(grb_trigger=results['GRBTRIGGERDATE'], grb_name=grb_name, 
                                       gbm=None, lat=None, chatter=chatter)    

    grb[0].ra                = results['RA']
    grb[0].dec               = results['DEC']
    grb[0].T05               = results['GRBT05']
    grb[0].T90               = results['GRBT90']
    grb[0].T95               = results['GRBT95']
    grb[0].LocalizationError = results['ERR']
    grb[0].redshift          = results['REDSHIFT']
    grb[0].CreateROOTFile()
    print '------------------------------------------------------------------------------------'
    if 'GCNNAME' not in results.keys():  results['GCNNAME'] = grb[0].Name
    else: print ' NAME   OF THE GRB GCN..: %s' % results['GCNNAME']    
    print ' NAME   OF THE GRB FULL.: %s' % grb[0].Name        
    print ' DATE   OF THE GRB .....: %s' % grb[0].Date
    print ' M.E.T. OF THE GRB......: %s' % grb[0].Ttrigger
    print '------------------------------------------------------------------------------------'
    print ' GRB T05=%.3f, T95=%.3f (T90=%.3f) ' % (grb[0].T05, grb[0].T95, grb[0].T90)
    print ' GBM T05=%.3f, T95=%.3f (T90=%.3f) ' % (results['GBMT05'],results['GBMT95'],results['GBMT90'])
    print '------------------------------------------------------------------------------------'
    lat[0]                   = LAT.LAT(grb=grb[0])    
    lat[0].chatter           = chatter    
    lat[0].Emin              = results['EMIN']
    lat[0].Emax              = results['EMAX']  
    lat[0].radius            = results['ROI']
    lat[0].zmax              = results['ZMAX']   
    lat[0].SetResponseFunction(results['IRFS'])
    #lat[0].Ebins             = int(results['EBINS'])

    try:     ft1=results['FT1']
    except:  ft1=None # lat[0].FindFITS('FT1', results['FT1'])
    try:     ft2=results['FT2']
    except:  ft2=None # lat[0].FindFITS('FT1', results['FT1'])
    
    if ft1.lower()=='none' or len(ft1)<2: ft1=None
    if ft2.lower()=='none' or len(ft2)<2: ft2=None
    if ft1 is not None:
        if not os.path.exists(ft1): ft1=None
        pass
    if ft2 is not None:
        if not os.path.exists(ft2): ft2=None
        pass
    checkFile = file('%s/jobTag.txt' % lat[0].out_dir ,'w')
    checkFile.write(grb[0].Name)
    checkFile.close()

    # #################################################
    # This try to download the file using the astroserver :
    # #################################################
    
    UseAstroserver = True
    
    try:
        if os.environ['GTGRB_USE_DATACATALOG'].lower()=='yes':  UseAstroserver = False
	print ' USE ASTROSERVER: %s ' % UseAstroserver
        pass
    except:
        UseAstroserver = True
        pass
        
    UseDatacatalog = not UseAstroserver
    
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% #
    
    if(ft1==None or ft2==None):
        if(results.get('BEFORE')==None):    tstart   = grb[0].Ttrigger - 500
        else:                               tstart   = grb[0].Ttrigger - float(results['BEFORE'])
        tend     = grb[0].Ttrigger + deltat
        OneSec=1
        if deltat>200000.0: OneSec=0
        if UseAstroserver:
            from  scripts.getLATFitsFiles import getFilesAstroServer
            ft1,ft2 = getFilesAstroServer(grb[0].Name,tstart,tend,
                                          emin=results['EMIN'], emax=results['EMAX'],
                                          ra=results['RA'], dec=results['DEC'], radius=results['ROI']+10.,
                                          sample=lat[0]._Astroserver,ResponseFunction=lat[0]._ResponseFunction,chatter=chatter,OneSec=OneSec)
            tmin=0
            tmax=0
            if not os.path.exists(ft1):
                print 'WARNING: FT1 NOT available in the astroserver'
                UseDatacatalog=True
                if os.path.exists(ft2):  runShellCommand('rm %s' % ft2)
                pass
            else:
                try:
                    tmin,tmax             = lat[0].GetTMaxMin(ft1)
                except:
                    tmin=0
                    tmax=0
                    UseDatacatalog=True
                    print 'WARNING: probably no data available in the ASTROSERVER yet...'
                    pass
                pass
            
            if not UseDatacatalog and tmax  < grb[0].Ttrigger:                
                print ' WARNING: Data are not yet available in the astroserver... tmax - trigger = %d.' % ( tmax - grb[0].Ttrigger)
                UseDatacatalog = True
                if os.path.exists(ft1):  runShellCommand('rm %s' % ft1)
                if os.path.exists(ft2):  runShellCommand('rm %s' % ft2)
                pass
            pass
        
        if UseDatacatalog:            
            from  scripts.getLATFitsFiles import getFilesDataCatalog
	    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
            print '% WARNING THE DATACATALOG IS USED AND EVENT_CLASS MIGHT BE WRONG!!! %'                        
	    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
    	    release='P6'
            if 'P7' in lat[0]._ResponseFunction: release='P7'
            
	    ft1,ft2=getFilesDataCatalog(name=grb[0].Name,
                                        tstart=tstart,tend=tend,
                                        logicalPath=lat[0]._Datacatalog) # Note that the datacatalog do not make any selection, therefore the files are typically much larger
    	    pass
	pass
    
    # Here you have to have a ft1 and ft2 or the code will crash!
    if ft1==None:
        txt = '''
        The Data file was not available neither locally neither in the astroserver and neither in the datacatalog!
        If you are using a valid predicted FT2 file you can still run PlotAngularSeparation() to see a predicted position of the GRB'''        
        raise IOError(txt)
    
    if (quick): tmin,tmax= lat[0].GetTMaxMin_quick(ft1)
    else      : tmin,tmax= lat[0].GetTMaxMin(ft1)
    
    if tmax  < grb[0].Ttrigger:                
        if os.path.exists(ft1): runShellCommand('rm %s' % ft1)
        if os.path.exists(ft2): runShellCommand('rm %s' % ft2)
        pass
    
    if os.path.exists(ft1): ft1=lat[0].FindFITS('FT1', ft1)
    if os.path.exists(ft2): ft2=lat[0].FindFITS('FT2', ft2)
    if not os.path.exists(ft1): raise IOError(' No FT1 data file covers the interval of time tiy selected.')
    if not os.path.exists(ft2): raise IOError(' No FT2 data file covers the interval of time tiy selected.')
    
    # #################################################    
    
    if (quick): emin,emax=(0,0)
    else:       emin,emax=lat[0].GetEMaxMin(ft1)
    
    if (quick): tmin,tmax= lat[0].GetTMaxMin_quick(ft1)
    else      : tmin,tmax= lat[0].GetTMaxMin(ft1)
    # #################################################
    
    #tstart   = grb[0].Ttrigger + results['TSTART']
    #tend     = tmax    
    #EXPOSURE = results['TSTOP'] - results['TSTART']    
    #if(EXPOSURE>0):
    #    tend = tstart     + EXPOSURE
    #    pass
    
    #lat[0].setTmin(tstart)
    #lat[0].setTmax(tend)
    ##################################################
    # THIS STORE SOME RESULTS:
    results['GRBNAME']  = grb[0].Name
    results['GRBDATE']  = grb[0].Date
    results['GRBMET']   = grb[0].Ttrigger
    results['FT1_EMIN'] = emin
    results['FT1_EMAX'] = emax
    results['FT1_TMIN'] = tmin-grb[0].Ttrigger
    results['FT1_TMAX'] = tmax-grb[0].Ttrigger
    results['FT1']      = ft1
    results['FT2']      = ft2
    # ##################################################
    # THIS OPTIMIZE THE CHOICE OF THE ROI:

    zGRB = lat[0].getGRBZenith()
    tGRB = lat[0].getGRBTheta()
    results['THETA'] =lat[0].getGRBTheta()
    results['ZENITH']=lat[0].getGRBZenith()
    (results['MCILWAIN_L'],results['MCILWAIN_B']) = lat[0].getMcIlWain()
    try: CHANGE_ZMAX    = bool(float(results['CHANGE_ZMAX']))
    except: CHANGE_ZMAX = True
    
    ROI  = lat[0].radius
    zMAX = lat[0].zmax    
    if zGRB > 90 and CHANGE_ZMAX:
        print ' =====>> Z MAX CHANGED: <<======='                
        zMAX = max(zMAX,110)
        ROI  = min(ROI,10.0)
        pass
    
    if zGRB > zMAX:
        print ' =====> NO EVENTS WILL BE SELECTED <======'        

    results['ZMAX']  = zMAX
    lat[0].zmax   = results['ZMAX']
    results['ROI']   = ROI
    lat[0].radius = results['ROI']
    if chatter>0:        
        print ' --------------------------------------------------'
        print ' Angle with the LAT z-axis....: %.1f' % tGRB
        print ' --------------------------------------------------'
        print ' Maximum Zenith Angle (zmax)..: %.1f' % zMAX        
        print '     GRB Zenith Angle (z GRB).: %.1f' % zGRB
        print '     ROI......................: %.1f' % ROI
        print ' --------------------------------------------------'
    
    # APPLY GTMKTIME ONCE FOR ALL:
    filter='IN_SAA!=T && LIVETIME>0'    
    filter_2='(ANGSEP(RA_ZENITH,DEC_ZENITH,%s,%s) + %s < %s)' %(grb[0].ra,grb[0].dec,lat[0].radius,lat[0].zmax)    
    try:    strategy=results['strategy']
    except: strategy='time'
    
    if lat[0].zmax < 180 and strategy=='time':
        filter='%s && %s' %(filter,filter_2)
        pass
    if gtmktimecut is None:
        gtmktimecut=filter
    else:
        gtmktimecut='(%s && %s)' %(filter,gtmktimecut)        
        pass
    
    if not quick:
        lat[0].make_gtmktime(filter=gtmktimecut)
    elif chatter>0:
        print 'Quick Mode, skipping gtmktime!'
        
    # ##################################################

    if results['REDSHIFT'] > 0:
        from astropy.cosmology import WMAP9 as cosmo
        from astropy import units as u
        results['LUMINOSITY_DISTANCE'] = cosmo.luminosity_distance(z=results['REDSHIFT']).to(u.cm).value
    else:
        results['LUMINOSITY_DISTANCE'] = 0.0
        pass
    return 0

def SetSunPosition(offset=0):
    ''' This method set the position of the source at the Sun position at the time of the trigger + offset.
    Default offset is 0 '''
    MET = grb[0].Ttrigger + offset
    SD=sunpos.getSunPosition(MET)
    RA_SUN,DEC_SUN=SD.ra(),SD.dec()    
    SetVar('RA',RA_SUN)
    SetVar('DEC',DEC_SUN)    
    SetGRB()
    print 'Position set at Sun Position Ra=%.4f Dec=%.4f (offset from trigger: %.3f)' %(RA_SUN,DEC_SUN,offset)
    pass


def Print(suffix='',ResultsFileName=None):
    ''' Print the parameters currentlky in use.'''    
    if ResultsFileName is None: ResultsFileName='%s/results_%s%s.txt' % (lat[0].out_dir,grb[0].Name,suffix)
    ResultsFile=file(ResultsFileName,'w')
    ResultsFile.write('# Input Parameters\n')

    keys= sorted(results.keys())
    print '====> Print () ======================================================='
    print '# Stored Parameters --------------------------------------------------'    
    for item in keys:
        if not 'FGL ' in item: print item,' = ', results[item]
        ResultsFile.write('%30s = %10s\n' %(item,results[item])) 
        pass
    print '# Output Results --------------------------------------------------'
    ResultsFile.close()
    print '# output written in %s ' % ResultsFileName
    print '=================================================='
    pass

def ReadResults(**kwargs):
    '''
    This method read the results stored in e
ach GRBOUT directory so that runs can be divided into
    independent steps
    Options are:
       string: ResultsFileName, default is <lat[0].out_dir>/results_<grb[0].Name>.txt: File to read.
       int:    overw, default is 1 (True). This overwrite the result dictionary in memory.
                                           If this is set to false, it will add the keys from the file,
                                           but it will keep the existing one as they are stored in memory.        
    '''
    ResultsFileName = None; overw = 1; new=0
    for key in kwargs.keys():
        if   key.upper()=="RESULTSFILENAME": ResultsFileName = kwargs[key]
        elif key.upper()=="OVERW"                  : overw           = int(kwargs[key])
        elif key.upper()=="NEW"                    : new             = int(kwargs[key])
        pass
    
    if ResultsFileName is None:
        ResultsFileName='%s/results_%s.txt' % (lat[0].out_dir,grb[0].Name)
        pass
    if not os.path.exists(ResultsFileName):
        print '--------------------------------------------------'
        print ' Results file does not exist %s. overw=%d' %  (ResultsFileName,overw)
        print '--------------------------------------------------'
        return None

    if new==1: results={}

    for l in file(ResultsFileName,'r').readlines():
        #print l
        if '#' in l: continue
        name = l.split('=')[0].strip()
        value = l.split('=')[1].strip()
        if(name=='GRBNAME'):
            # This is to avoid that a GRB name saved as 100724029.0 would
            # be restored as a floating point number, since GRBNAME is used
            # to build pathnames
            try:
                finnal_value= "%09i" %(float(value))
            except:
                finnal_value = "%s" %(value)
                pass
            pass
        else:
            try:
                finnal_value = float(value)
            except:
                finnal_value = value
                pass
            pass
        
        if name in results.keys():
            if overw==1: results[name]=finnal_value
        else: results[name]=finnal_value
        pass
    print '--------------------------------------------------'
    print ' Results read from file %s. overw=%d' %  (ResultsFileName,overw)
    print '--------------------------------------------------'    
    return results#ResultsFileName

def CheckGRB():
    '''
    This method check if all the required variables are properly set...
    '''
    # if the key GRB is not defined yet, ask for it (or get it from the pfile).
    needed = ['GRBTRIGGERDATE','GRBT05','GRBT90','RA','DEC']
    for v in needed:
        if v not in results:
            return False
        pass
    return True
    
def SubmitJob(exe='app/computeAll.py',run=0):
    '''Execute job in the pipeline.
    \t exe=\'app/computeAll.py\' execute the script app/computeAll.py
    \t run=0   print the job command =1: send the job to the pipeline    
    '''
    
    GRBTRIGGERDATE = results['GRBMET']
    RA             = results['RA']
    DEC            = results['DEC']
    GRBT05         = results['GRBT05']
    GRBT90         = results['GRBT90']
    cmd = './pipeline/submitJob.py GRBTRIGGERDATE=%s RA=%s DEC=%s GRBT05=%s GRBT90=%s -exe %s -q xlong' %(GRBTRIGGERDATE,RA,DEC,GRBT05,GRBT90,exe)
    print 'Execute Job In the pipeline:'
    print cmd
    if run:
        runShellCommand(cmd)
    else:
        print 'add run=1 as argument to run the job'
        print 'SubmitJob(exe=%s,run=1)' % exe
        pass
    pass
    
def AddResults(mydict):
    ''' Add the results stored in mydict to the general results dictionary.
    \t mydict dictionary containing the resulys'''
    for k in mydict.keys():
        try:
            results[k]=float(mydict[k])
        except:
            results[k]=mydict[k]
            pass
        pass
    pass

def GetLLEFiles():
    print("====> GetLLEFiles()")
    from scripts import getLLEfiles
    getter                     = getLLEfiles.LLEdataCollector(results['GRBNAME'])
    getter.get()
    
pass

def GetGBMFiles(dataType=['tte','rsp','tcat','cspec']):
    print '====> GetGBMFiles()'
    try:
        if os.environ['PIPELINE']=='YES':
            print '*--------------------------------------------------*'
            print '* You are running in the batch farm,               *'
            print '* It is not possible to download data via ftp      *'
            print '* Try to see if there are something already saved  *'
            print '* Looking in:                                      *'
            print '%s/GBM/%s'  % (os.environ['INDIR'],grb[0].Name)
            runShellCommand('ls -l %s/GBM/%s'  % (os.environ['INDIR'],grb[0].Name))
            print '*--------------------------------------------------*'
            pass
        pass
    except:            
        #print 'DataTypes: ',dataType
        from  scripts.getGBMfiles import getGBMfiles        
        getGBMfiles(grb[0].Name, dataType)
        pass
    pass



def GetLLE():
    ''' Download the LLE event data from the Datacatalog    
    '''
    rootfile = "%s/lle_events.root" % lat[0].out_dir
    if os.path.exists(rootfile):
        print '%s already exists. Remove it if you want to get it again.' % rootfile
    else:
        try:
            lle_dir       = os.environ['LLEPIPELINE']
        except:
            lle_dir       = os.environ['LLE_DIR']
            pass
        if(socket.getfqdn().find("slac.stanford.edu")==-1):
          print("You are not at SLAC. I will download LLE data at slac (using your account), then I will transfer them here")
          from scripts import downloadLLEfromRemote
          downloadLLEfromRemote.go(lle_dir)
	else:
          print 'lle_dir: ',lle_dir
          print 'Available resources in: '
          runShellCommand('pwd')
          print 'is:'
          runShellCommand('df -h .')
          lle_macropath = os.path.join(lle_dir, 'src/macros/make_LLE_histogram_dur.C')
          ROOT.gROOT.LoadMacro(lle_macropath)
          
          theta   = lat[0].getGRBTheta()
          ft2file = lat[0].FilenameFT2
          t90     = float(results['GBMT90']) # Why this is not float ?????
          
          meritfiles            =     run_LLE.find_merit_files(grb[0].Ttrigger,(-1000,1000))
          ROOT.make_LLE_histogram(meritfiles,
                                  lat[0].out_dir,
                                  grb[0].Ttrigger,
                                  grb[0].ra,
                                  grb[0].dec,
                                  theta, t90, True)
          outfile  = "%s/lle_events.txt"  % lat[0].out_dir
          fitsfile = "%s/lle_events.fits" % lat[0].out_dir
          # LLE.writeto(outfile, fitsfile)        
        pass
    return rootfile

def MakeLLE_GSFC(**kwargs):
    ''' this is the new interface which is the same as the one used to export LLE files at Goddard'''
    thisCommand               = commandDefinitions.commands['MakeLLE_GSFC']
    harvestParameters(thisCommand,kwargs)
    #THETA_MIN=89
    LLE_VERSION,DURATION,OFFSET,DT,ZENITHMAX,THETAMAX,BEFORE,AFTER,NSIGMA,RADIUS = thisCommand.getParameters("LLE_VERSION,DURATION,OFFSET,DT,ZENITHMAX,THETAMAX,BEFORE,AFTER,NSIGMA,RADIUS")
    print 'MakeLLE_GSFC:',LLE_VERSION,DURATION,OFFSET,DT,ZENITHMAX,THETAMAX,BEFORE,AFTER,NSIGMA,RADIUS
    #if GRBtheta < THETA_MIN:
    import makeLLE
    output_ez=os.environ['OUTDIR']
    makeLLE.GenerateLLE(output_ez=output_ez,
                        version=LLE_VERSION,
                        GRBNAME=grb[0].Name,
                        MET=grb[0].Ttrigger,
                        RA=grb[0].ra,
                        DEC= grb[0].dec,
                        DURATION=DURATION,
                        OFFSET=OFFSET,
                        DT=DT,
                        BEFORE=BEFORE,
                        AFTER=AFTER,
                        ZENITHMAX=ZENITHMAX,
                        THETAMAX=THETAMAX,
                        RADIUS=RADIUS,
                        mode=['pha','forReal'])
    LLE_SIG, LLE_T0, LLE_T1 = makeLLE.ComputeLLEDetection(output_ez,LLE_VERSION,grb[0].Name,lat[0].FilenameFT2,grb[0].ra, grb[0].dec,grb[0].Ttrigger,NSIGMA)
    results['LLE_SIG'] = LLE_SIG
    results['LLE_T0']  = LLE_T0
    results['LLE_T1']  = LLE_T1
    
#def MakeLLELightCurves(**kwargs):
#    ''' This is the old interface OBSOLETE '''
#    thisCommand               = commandDefinitions.commands['MakeLLELightCurves']
#    harvestParameters(thisCommand,kwargs)
#    diggerArguments           = thisCommand.getParameters("lledt,lleds,N,task,srctmin,srctmax,lctmin,lctmax",dictionary=True)
#    print 'diggerArguments=',diggerArguments
#    # Get LLE data
#    rootfile                  = GetLLE()
#    
#    gbmT90                    = results['GBMT90']
#    
#    #Instantiate and run the digger    
#    digger                    = LLEdigger.Digger(grb,lat,rootfile,results)
#    LLEresults                = digger.dig(**diggerArguments)
#    
#    #Add results to the dictionary    
#    AddResults(LLEresults)
#    pass
#def MakeLLEDetectionAndDuration(**kwargs):
#
#    ''' This is the old interfce '''
#    # useDiggerBinning=True, useDiggerLag=True, useDiggerStart=False, useDiggerStop=False, RoiMaxRadius=0):
#    thisCommand               = commandDefinitions.commands['MakeLLEDetectionAndDuration']
#    harvestParameters(thisCommand,kwargs)
#    useDiggerBinning,useDiggerLag,useDiggerStart,useDiggerStop,RoiMaxRadius = thisCommand.getParameters("useDiggerBinning,useDiggerLag,useDiggerStart,useDiggerStop,RoiMaxRadius")
#    
#    print '====> MakeLLEDetectionAndDuration'
#    from ROOT import std
#    from ROOT import LLE_NS 
#    from LLE.read_data import read_data#
#
#    burst_name = 'GRB'+grb[0].Name
#    trigger    = grb[0].Ttrigger
#    ra         = grb[0].ra
#    dec        = grb[0].dec
#    GBMT90     = float(results['GBMT90'])#
#
#    # take LLE digger results as inputs?
#    llet5  =0.
#    llet95 =0.
#    llet0  =0.
#    llet100=0.
#    lletbin=0.#
#
#    if (useDiggerBinning==True):
#        try:
#            lletbin=results['LLESelectedBin']
#            if (isinstance(lletbin,float)==True):
#                print 'Using LLEdigger binning as input to LLEdetdur: ',lletbin
#            else:
#                print 'Using LLEdigger binning as input to LLEdetdur is not possible: ',lletbin
#                lletbin=0.
#        except:
#            pass#
#
#   if (useDiggerLag==True):
#        try:
#            llet5  =results['LLET05_1']
#            llet95 =results['LLET95_1']
#            llet90 =llet95-llet5#
#
#            llet0tmp =results['LLET0_1']
#
#            # check for significant lag
#            if (llet5>llet90):
#                llet0=llet0tmp
#                print 'LLEdigger found a significant lag (T5>T90) -> Using LLEdigger start time as input to LLEdetdur: ',llet0
#        except:
#            pass#
#
#    if (useDiggerStart==True):
#        try:
#            llet0  =results['LLET0_1']
#            print 'Using LLEdigger start time as input to LLEdetdur: ',llet0
#        except:
#            pass
#    if (useDiggerStop==True):
#        try:
#            llet100=results['LLET100_1']
#            print 'Using LLEdigger stop time as input to LLEdetdur: ',llet100
#        except:
#            pass
#
#    # Get LLE data
#    LLErootfile = GetLLE()#
#
#    # Main GRB analysis
#    shrink=False
#    computedur=True
#    print ''
#    print '<><><><>'
#    print '<><><><>', burst_name,' trigger=',trigger,' RA=',ra,' Dec=',dec,' GBMT90=',GBMT90,' RoiMaxRadius=',RoiMaxRadius,' input t0/t100/bin=',llet0,'/',llet100,'/',lletbin
#    print '<><><><>'
#    print ''
#
#    LLE_NS.make_LLEdetdur(LLErootfile, lat[0].FilenameFT2, lat[0].out_dir, burst_name, trigger, ra, dec, GBMT90, RoiMaxRadius, shrink, computedur, llet0, llet100, lletbin)

    # store results in dictionnary
#    mydict={}
#    col1, col2, col3, col4 = read_data('%s/%s_LLEdetdur_Res.txt' %(lat[0].out_dir,burst_name))#

#    mydict['LLEt05']     =col1[0]
#    mydict['LLEt05loerr']=col2[0]
#    mydict['LLEt05hierr']=col3[0]
#    mydict['LLEt05obs']  =col4[0]
#
#    mydict['LLEt10']     =col1[1]
#    mydict['LLEt10loerr']=col2[1]
#    mydict['LLEt10hierr']=col3[1]
#    mydict['LLEt10obs']  =col4[1]
#
#    mydict['LLEt25']     =col1[2]
#    mydict['LLEt25loerr']=col2[2]
#    mydict['LLEt25hierr']=col3[2]
#    mydict['LLEt25obs']  =col4[2]
#
#    mydict['LLEt75']     =col1[3]
#    mydict['LLEt75loerr']=col2[3]
#    mydict['LLEt75hierr']=col3[3]
#    mydict['LLEt75obs']  =col4[3]
#
#    mydict['LLEt90']     =col1[4]
#    mydict['LLEt90loerr']=col2[4]
#    mydict['LLEt90hierr']=col3[4]
#    mydict['LLEt90obs']  =col4[4]
#
#    mydict['LLEt95']     =col1[5]
#    mydict['LLEt95loerr']=col2[5]
#    mydict['LLEt95hierr']=col3[5]
#    mydict['LLEt95obs']  =col4[5]

#    mydict['LLET90']     =col1[6]
#    mydict['LLET90loerr']=col2[6]
#    mydict['LLET90hierr']=col3[6]
#    mydict['LLET90obs']  =col4[6]

#    mydict['LLET80']     =col1[7]
#    mydict['LLET80loerr']=col2[7]
#    mydict['LLET80hierr']=col3[7]
#    mydict['LLET80obs']  =col4[7]

#    mydict['LLET50']     =col1[8]
#    mydict['LLET50loerr']=col2[8]
#    mydict['LLET50hierr']=col3[8]#
#    mydict['LLET50obs']  =col4[8]

#    mydict['LLENSIG']    =col1[9]
#    mydict['LLENSIGBAYES']   =col2[9]
#    mydict['LLETSIG']    =col3[9]
#    mydict['LLESTAT']    =col4[9]
#    mydict['LLETH0']      =col1[10]
#    mydict['LLEZTH0']     =col2[10]
#    print 'T90=',mydict['LLET90'],'-',mydict['LLET90loerr'],'+',mydict['LLET90hierr'],' s'
#    print 'T80=',mydict['LLET80'],'-',mydict['LLET80loerr'],'+',mydict['LLET80hierr'],' s'
#    print 'T50=',mydict['LLET50'],'-',mydict['LLET50loerr'],'+',mydict['LLET50hierr'],' s'
#    print 'LLE max significance=',mydict['LLENSIG'],' at T0+',mydict['LLETSIG'],' s'
#
#    AddResults(mydict)
#    pass

def MakeGBMLightCurves(**kwargs):
    
    print '====> MakeGBMLightCurve()'
    
    thisCommand               = commandDefinitions.commands['MakeGBMLightCurves']
    harvestParameters(thisCommand,kwargs)
    detlist_s                 = thisCommand.getParameters("detlist",dictionary=True)
    if detlist_s.get('DETLIST')=="NONE":  return 0
    
    naiangle                  = thisCommand.getParameters("naiangle",dictionary=True)
    dt,tstart,tstop           = thisCommand.getParameters("dt,tstart,tstop")
    if(detlist_s!={}):
        closer_detectors=GetNearestDet(**forceNonInteractive(detlist_s))
    else:
        closer_detectors=GetNearestDet(**forceNonInteractive(naiangle))
    pass
    
    Ndetectors=len(closer_detectors)
    
    tmin0 = grb[0].TStart
    tmax0 = grb[0].TStop
    tmin = grb[0].Ttrigger + tstart
    tmax = grb[0].Ttrigger + tstop
    lat[0].setTmin(tmin)
    lat[0].setTmax(tmax)
    i=0
    for gbm_det_n in closer_detectors:
        gbm_det=gbm_det_n.lower()
        print "Processing %s..." %(gbm_det)
        gbm=GBM.GBM(grb=grb[0],detector_name=gbm_det)
        try:
          gbm.make_time_select(tmin,tmax)
        except:
          raise RuntimeError("gtselect on GBM file failed! Did you run GetGBMFiles()?")
        #if not os.path.exists(gbm.evt_file.replace('.fit','.root').replace('.roots','.root')):
        gbm.saveEvents2Root()
        # pass
        
        gbm.make_LightCurve(dt)
        #gbm.save_LightCurve_ROOT()
        gbm.plotLC_PYLAB()
    pass
    lat[0].setTmin(tmin0)
    lat[0].setTmax(tmax0)
    results['DT'] = float(dt)
    return 1

def Make_PHA_GBM_Files(**kwargs):
    print '====> Make_PHA_GBM_Files()'
    
    harvestParameters(thisCommand,kwargs)
    detlist_s                 = thisCommand.getParameters("detlist",dictionary=True)
    naiangle                  = thisCommand.getParameters("naiangle",dictionary=True)
    tstart,tstop,suffix       = thisCommand.getParameters("tstart,tstop,suffix")    
    
    out_dir =  lat[0].out_dir
    if suffix is not '':
        out_dir = lat[0].out_dir+'/' + suffix
        runShellCommand('mkdir -p %s' % out_dir)
        pass
        
    tmin                      = grb[0].Ttrigger + tstart
    tmax                      = grb[0].Ttrigger + tstop    
    
    if detlist_s.get('DETLIST')=="NONE":  return 0
    if(detlist_s!={}):
        closer_detectors=GetNearestDet(**forceNonInteractive(detlist_s))
    else:
        closer_detectors=GetNearestDet(**forceNonInteractive(**naiangle))
    pass
    
    Ndetectors                = len(closer_detectors)    
    
    for gbm_det_n in closer_detectors:
        gbm_det               = gbm_det_n.lower()
        print "Processing %s..." %(gbm_det)
        gbm            = GBM.GBM(grb=grb[0],detector_name=gbm_det)
        evt_file       = out_dir+'/'+lat[0].grb_name+'_'+gbm_det+'_%.2f_%.2f.fits'%(tstart,tstop)
        sp_outFile     = out_dir+'/'+lat[0].grb_name+'_'+gbm_det+'_%.2f_%.2f.pha'%(tstart,tstop)
        gbm.evt_file   = evt_file
        gbm.sp_outFile = sp_outFile
        gbm.make_time_select(tmin,tmax)
        gbm.make_pha1()
        print("\n==> Spectrum produced: %s\n" %(sp_outFile))
        pass
    return 1

##################################################
def _translateDetlist(detlist):
    
    knownDetectors = ['b0','b1','n0','n1','n2','n3','n4','n5','n6','n7','n8','n9','na','nb']
    
    
    if detlist.upper()=="ALL":
        DETLIST=knownDetectors
    elif detlist.upper()=='TRIG':
        from  scripts.getGBMfiles import getTriggerDetectors
        DETLIST = getTriggerDetectors(grb[0].Name).split(",")   
    else:
        DETLIST=detlist.replace(" ","").split(",")
        # Check for legal detectors
        for det in DETLIST:
            try:
                knownDetectors.index(det.lower())
            except:
                raise ValueError("Detector %s is not known." %(det))
            pass
        pass
    return DETLIST

##################################################
def GetNearestDet(**kwargs):
    print '====> GetNearestDet()'
    
    thisCommand               = commandDefinitions.commands['GetNearestDet']
    harvestParameters(thisCommand,kwargs)
    naiangle,bgoangle,detlist = thisCommand.getParameters("naiangle,bgoangle,detlist")
  
    # Clean the list
    cleanDetlist              = _translateDetlist(detlist)
    
    n                         = GBMtools.DetDir(cleanDetlist,
                                                lat[0].FilenameFT2,
                                                grb[0].Ttrigger)
    
    angles                    = n.getSourceAngle(grb[0].ra,grb[0].dec,0.0)
    
    # Sort the dictionary (closer detector first)
    keys                      = sorted(angles, key=angles.get)
      
    # This will print (and return) the NaI detectors with angle < angleThresh,
    # and the BGO(s) with an angle < bgoangle
    print("   Detector              Angle")
    print("                         (deg)")
    print("   ------------------------------")
    selectedKeys              = []

    form                      = '   {0:20} {1:5.3f}'
    for key in keys:
        if(angles[key] <= naiangle):
            print form.format(key.rjust(5), angles[key])
            selectedKeys.append(key)
            pass
        elif((key=='b0' or key=='b1') and angles[key] <= bgoangle):
            print form.format(key.rjust(5), angles[key])
            selectedKeys.append(key)
            pass
        pass
    return selectedKeys
##################################################

##################################################
def SelectGBMTimeInterval(**kwargs):
    print '====> SelectGBMTimeInterval()'
    
    thisCommand               = commandDefinitions.commands['SelectGBMTimeInterval']
    harvestParameters(thisCommand,kwargs)
    detector,binsize,datafile = thisCommand.getParameters("detector,binsize,datafile")
    
    if(detector==''):
      #Use closest NaI
      detector                = filter(lambda x:x.find("n")==0,GetNearestDet(naiangle=180,bgoangle=100.0,detlist='All'))[0];
    outdir                    =  lat[0].out_dir
    
    if(datafile==''):
      gbm                     = GBM.GBM(grb=grb[0],detector_name=detector)

      tte_filename            = gbm.tte_File
    
      #Check that we have the proper files to work with
      if(tte_filename==None):
        raise RuntimeError("No TTE file for this detector/GRB. Did you run GetGBMFiles()?")
      pass
      datafile                = tte_filename
    pass
    
    #Now run GTBIN
    outfile                   = os.path.join(lat[0].out_dir,"%s_lightCurve.fits" %(detector))
    gtbin                     = GtApp.GtApp('gtbin')
    gtbin['evfile']           = datafile
    gtbin['outfile']          = outfile
    gtbin['algorithm']        = "LC"
    gtbin['clobber']          = "yes"
    gtbin['tbinalg']          = "LIN"
    gtbin['dtime']            = binsize
    gtbin['tstart']           = results['GRBTRIGGERDATE']-30.0
    gtbin['tstop']            = results['GRBTRIGGERDATE']+300.0
    gtbin['scfile']           = results['FT2']
    gtbin['lcemin']           = 0.01
    gtbin['lcemax']           = 1.0
    gtbin.run()
    
    #Now load the LC in a THisto
    import array
    f                         = pyfits.open(outfile)
    rate                      = f['RATE']
    counts                    = rate.data.field('COUNTS')
    tstart                    = array.array('d',rate.data.field('TIME')-results['GRBTRIGGERDATE'])
    histo                     = ROOT.TH1D("Light curve","Light curve",len(tstart)-1,tstart)
    for i in range(len(tstart)):
      histo.SetBinContent(i+1,counts[i])
    f.close()
    histo.GetXaxis().SetTitle("Time since trigger (s)")
    histo.GetYaxis().SetTitle("Counts per bin")
    histo.SetTitle("Light curve of %s (binsize = %s)" %(detector,binsize))
    
    canvas                    = ROOT.TCanvas()
    canvas.cd()
    histo.Draw("HIST")
    import my_iCanvas
    tstart,tstop              = my_iCanvas.iTimeIntervals(canvas,histogram=histo)
    canvas.Close()
    
    #Register the results
    print("\nYour selections are:")
    for t1,t2 in zip(tstart,tstop):
      print("%s - %s" %(t1,t2))
    print("\nYour selections have been saved in results['SP_TSTARTS'] and results['SP_TSTOPS'].")
    results['SP_TSTARTS']     = ",".join(map(lambda x:str(x),tstart))
    results['SP_TSTOPS']      = ",".join(map(lambda x:str(x),tstop))
pass

def SelectGBMTimeIntervalsAllDetectors(**kwargs):
    '''
    Interactively select a time interval from a background subtracted light curve built using 
    all the events from all the detectors having a background model.
    
    Usage:
      > tstart, tstop = SelectGBMTimeIntervalsAllDetectors()
    
    Optional parameters:
    \t binsize               = size of the time bin (in seconds, default = 1)
    \t sn                    = signal-to-noise ratio, for a adaptive binning light curve (default = None).
    \t tstart                = start time for the light curve (default: GBM T05 - GBM T90)
    \t tstop                 = stop time for the light curve (default: GBMT95 + GBM T90)
    '''
    sn                       = 100000000
    binsize                  = 1
    verbose                  = False
    tstart                   = results['GBMT05']-results['GBMT90']
    tstop                    = results['GBMT95']+results['GBMT90']
    for key in kwargs.keys():
      if  (key.lower()=="binsize")   :         binsize     = kwargs[key]
      elif(key.lower()=="tstart")    :         tstart      = kwargs[key]
      elif(key.lower()=="tstop")     :         tstop       = kwargs[key]
      elif(key.lower()=="sn")        :         sn          = kwargs[key]
    pass
    
    kwargs['sn']             = sn
    kwargs['maxbinsize']     = binsize
    kwargs['verbose']        = verbose
    kwargs['tstart']         = tstart
    kwargs['tstop']          = tstop

    tstart,tstop,sn          = FindTimeBins(**kwargs)
    results['Rebinner'].canvas.Draw()
    import my_iCanvas
    tstart,tstop             = my_iCanvas.iTimeIntervals(results['Rebinner'].canvas,results['GBMT05'],results['GBMT95'])

    return tstart, tstop    
pass

def FindTimeBins(**kwargs):
    print '====> FindTimeBins()'  
        
    thisCommand               = commandDefinitions.commands['FindTimeBins']
    harvestParameters(thisCommand,kwargs)
    (tstart,tstop,sn,
     maxBinSize,
     minNumberOfEvents, 
     minEvtEnergy,
     maxEvtEnergy,detlist,
     useLLE,significance)     = thisCommand.getParameters("tstart,tstop,rebin_sn,maxBinSize,minNumberOfEvents,minEvtEnergy,maxEvtEnergy,detlist,useLLE,rebin_by_significance")

    #Default values
    out_dir                   =  lat[0].out_dir 
    
    if(detlist!="" and detlist!=None and detlist!="all"):
      #user provided detector list
      closer_detectors        = detlist.split(",")
    elif(detlist.lower()=="all"):
      #Use default: all the detectors for which a background model exists        
      #Select the detectors having an available background model (in the dumpdir directory)
      dumpFiles        = filter(lambda el: el.rfind(results['GRBNAME']) > 0, os.listdir(dumpdir))
      if(len(dumpFiles)==0):
        raise ValueError("No pre-fitted detectors found in directory %s'." %(dumpdir))
      pass
      closer_detectors = []
      for thisFile in dumpFiles:
        if(thisFile.rfind('NAI') > 0):
          #this is a NAI
          naiNumber  = float(thisFile.split("_")[2])
          if(naiNumber==10): 
            naiNumber = 'a' 
          elif(naiNumber==11): 
            naiNumber = 'b' 
          else: 
            naiNumber = '%1.0f' % (naiNumber)
          pass
          naiName     = 'n%s' % (naiNumber)
          closer_detectors.append(naiName)
        elif(thisFile.rfind('BGO') > 0):
          #this is a BGO 
          bgoNumber  = float(thisFile.split("_")[2])
          bgoNumber  = '%1.0f' % (bgoNumber)
          closer_detectors.append('b%s' % (bgoNumber))
        pass
      pass
    elif(detlist==''):
      if(useLLE==False):
        raise RuntimeError("You have to either use GBM detectors, or LLE, or both. No detector specified.")
      pass
      #No GBM detectors
      closer_detectors  = []
    pass
        
    Ndetectors=len(closer_detectors)    
    i=0
    
    tteFiles            = []
    cspecFiles          = []
    for gbm_det_n in closer_detectors:
      gbm_det         = gbm_det_n.lower()
              
      gbm             = GBM.GBM(grb=grb[0],detector_name=gbm_det)

      tte_filename    = gbm.tte_File
      cspec_filename  = gbm.cspec_File
      
      #Check that we have the proper files to work with
      if(tte_filename==None):
        raise RuntimeError("No TTE file for this detector/GRB. Did you run GetGBMFiles()?")
      elif(cspec_filename==None):
        raise RuntimeError("No CSPEC file for this detector/GRB. Did you run GetGBMFiles()?")
      pass
      tteFiles.append(tte_filename)
      cspecFiles.append(cspec_filename)
    pass
    
    #Add LLE
    if(useLLE):
      from scripts import getLLEfiles
      
      indir                      = os.path.join(os.environ['INDIR'],"LAT",results['GRBNAME']+"_LLE")
      getter                     = getLLEfiles.LLEdataCollector(results['GRBNAME'])
      getter.get()
       
      pha                        = getter.cspecFile
      ft1                        = getter.ft1File
      
      phafile                    = os.path.join(indir,pha)
      ft1file                    = os.path.join(indir,ft1)
      
      tteFiles.append(ft1file)
      cspecFiles.append(phafile)
      
    pass
    
    import eventBinner
    rebinner                         = eventBinner.rebinner(cspecFiles,tteFiles,
                                             tstart,tstop,results['GRBTRIGGERDATE'],
                                             results['GRBNAME'],dumpdir,
                                             minEvtEnergy,maxEvtEnergy,False)
    if(sn>0):
      tstarts, tstops, sns             = rebinner.findBinsBySignalToNoise(sn,minNumberOfEvents,maxBinSize,
                                                  significance=significance)
      results['Rebinner']              = rebinner
      print("\nThe %s intervals found have been saved in results['SP_TSTARTS'] and results['SP_TSTOPS']." %(len(tstarts)))
      results['SP_TSTARTS']            = ",".join(map(lambda x:str(x),tstarts))
      results['SP_TSTOPS']             = ",".join(map(lambda x:str(x),tstops))
      #return tstarts,tstops,sns
    else:
      #Bayesian Blocks
      prior                            = abs(sn)
      tstarts, tstops                  = rebinner.findBayesianBlocks(prior)
      results['Rebinner']              = rebinner
      print("\nThe %s intervals found have been saved in results['SP_TSTARTS'] and results['SP_TSTOPS']." %(len(tstarts)))
      results['SP_TSTARTS']            = ",".join(map(lambda x:str(x),tstarts))
      results['SP_TSTOPS']             = ",".join(map(lambda x:str(x),tstops))
      return tstarts, tstops       
pass

def MakeGBMSpectra(**kwargs):
    print '====> MakeGBMSpectra()'  
    import rmfit_lu
    
    thisCommand               = commandDefinitions.commands['MakeGBMSpectra']
    harvestParameters(thisCommand,kwargs)
    (tstart,tstop,detlist,naiangle) = thisCommand.getParameters("sp_tstarts,sp_tstops,detlist,naiangle")

    out_dir             =  lat[0].out_dir
        
    #Decide detectors to use
    
    if(detlist.lower()=='auto'):
       #Select the detectors having an available background model (in the dumpdir directory)
       dumpFiles        = filter(lambda el: el.rfind(results['GRBNAME']) > 0, os.listdir(dumpdir))
       if(len(dumpFiles)==0):
         raise ValueError("No pre-fitted detectors found in directory %s: you cannot use detlist='auto'!" %(dumpdir))
       pass
       closer_detectors = []
       for thisFile in dumpFiles:
         if(thisFile.rfind('NAI') > 0):
           #this is a NAI
           naiNumber  = float(thisFile.split("_")[2])
           if(naiNumber==10): 
             naiNumber = 'a' 
           elif(naiNumber==11): 
             naiNumber = 'b' 
           else: 
             naiNumber = '%1.0f' % (naiNumber)
           pass
           naiName     = 'n%s' % (naiNumber)
           closer_detectors.append(naiName)                              
         elif(thisFile.rfind('BGO') > 0):
           #this is a BGO 
           bgoNumber  = float(thisFile.split("_")[2])
           bgoNumber  = '%1.0f' % (bgoNumber)
           closer_detectors.append('b%s' % (bgoNumber))
         pass
       pass     
    else:
      if(detlist!="" and detlist!=None and detlist.lower() !="all" and detlist.lower() !="auto"):
        #User provided detlist
        detlist_s             = {'detlist': detlist,'naiangle': 180}
        closer_detectors=GetNearestDet(**forceNonInteractive(detlist_s))
      else:
        if(naiangle==""):
          raise ValueError("You have to provide either a detector list or a value for NAIANGLE!")
        else:
          naiangle_s          = {'naiangle': naiangle}
          closer_detectors=GetNearestDet(**forceNonInteractive(naiangle_s))
      pass    
    pass
        
    Ndetectors=len(closer_detectors)    
    i=0
    
    #Now check and fix the time intervals
    goodStart    = []
    goodStop     = []
    for i in range(len(tstart)):
      if(tstop[i] > tstart[i]): 
        goodStart.append(tstart[i])
        goodStop.append(tstop[i])
      else:
        print ("Invalid time interval requested: %s - %s. Skipping..." % (tstart[i],tstop[i]))
      pass
    pass
    
    if(len(goodStart) < 1): 
      print("No valid intervals, nothing to do!")
      return
    
    #Now create the directory ./rmfit , it will contain the lookup tables and soft links to the data files
    #to be used to repeat the same analysis in Rmfit
    runShellCommand('mkdir -p %s/rmfit' % os.path.abspath(lat[0].out_dir))
    
    PHA2files = []
    backFiles = []
    RSPfiles  = []
    
    for gbm_det_n in closer_detectors:
        gbm_det=gbm_det_n.lower()
        
        print 'Working on...: ',gbm_det
        
        gbm             = GBM.GBM(grb=grb[0],detector_name=gbm_det)

        tte_filename    = gbm.tte_File
        cspec_filename  = gbm.cspec_File
        if(gbm.rsp2_File==None):
          response      = gbm.rsp_File
        else:
          response      = gbm.rsp2_File
        
        #Check that we have the proper files to work with
        if(tte_filename==None):
            # raise RuntimeError("No TTE file for this detector/GRB. Did you run GetGBMFiles()?")
            print "No TTE file for this detector/GRB. Did you run GetGBMFiles()?"
        elif(cspec_filename==None):
            print "No CSPEC file for this detector/GRB. Did you run GetGBMFiles()?"
            #raise RuntimeError("No CSPEC file for this detector/GRB. Did you run GetGBMFiles()?")
        elif(response==None):
            print "No response (RSP/RSP2) file for this detector/GRB. Did you run GetGBMFiles()?"
            pass
        if tte_filename==None and cspec_filename==None and response==None:
            raise RuntimeError("No files available for this detector/GRB. Did you run GetGBMFiles()?")

        
        #Now check that the position in the responses is not too different from the one currently
        #defined
        rspf            = pyfits.open(response)
        ra_obj          = rspf["SPECRESP MATRIX",1].header["RA_OBJ"]
        dec_obj         = rspf["SPECRESP MATRIX",1].header["DEC_OBJ"]
        rspf.close()
        dist            = genutils.angsep(ra_obj,dec_obj,results['RA'],results['DEC'])
        print("\nAngular distance between current position (%s,%s) and position in response (%s,%s): %s\n" %(results['RA'],results['DEC'],ra_obj,dec_obj,dist))
         
        if(dist > 1.0):
          raise RuntimeError("The angular distance between the position in GBM responses and the one currently set is greater than 1 deg!")
        
        s               = GBMtools.GRBspectra(tte_filename, cspec_filename, response,results=results,**kwargs)
        pha2, back, rsp = s.getGRBspectra(goodStart,goodStop,lat[0].out_dir)
        PHA2files.append(os.path.join(lat[0].out_dir,pha2))
        backFiles.append(os.path.join(lat[0].out_dir,back))
        RSPfiles.append(os.path.join(lat[0].out_dir,rsp))
        
        #Now write the lookup table
        #This is hard coded: it is not nice, but I have no time now to make it nicer... :-)
        if(gbm_det.find("n")>=0):
          #This is a NaI
          emin           = [8.0,36.0]
          emax           = [31.0,900.0]
        elif(gbm_det.find("b1")>=0):
          #This is BGO 1
          emin           = [174.0]
          emax           = [40511.0]
        elif(gbm_det.find("b0")>=0):
          #This is BGO 0
          emin           = [252.]
          emax           = [40107.0]
        pass
        
        for start,stop in zip(goodStart,goodStop):
          
          #Create the directory for this time interval
          dirName        = "%.4f_%.4f" % (start,stop)
          dirPath        = "%s/rmfit/%s" % (os.path.abspath(lat[0].out_dir),dirName)
          runShellCommand('mkdir -p %s' % (dirPath))
          
          #Get the time intervals used for the background fit
          backTstarts, backTstops, polyOrder = s.getBackgroundIntervals()                    
          
          #Instantiate the lookup table class for CSPEC
          lu             = rmfit_lu.rmfit_lookup(emin,emax,[tstart[0]],[tstop[0]],backTstarts,backTstops, polyOrder)                    
          #Write the lookup table
          lu.write("%s/%s.lu" % (dirPath,os.path.basename(cspec_filename).split(".")[0]))
          
          #Instantiate the lookup table class for CSPEC
          lu             = rmfit_lu.rmfit_lookup(emin,emax,[tstart[0]],[tstop[0]],backTstarts,backTstops, polyOrder)                    
          #Write the lookup table
          lu.write("%s/%s.lu" % (dirPath,os.path.basename(tte_filename).split(".")[0]))
          
          #Now create a soft link to the data. I will use try/expect because shutil.copyfile fails if the link is already there
          #CSPEC
          cspecrelpath   = os.path.relpath(os.path.abspath(cspec_filename),os.path.abspath(dirPath))
          try:
            shutil.copyfile(cspecrelpath, "%s/%s" % (dirPath,os.path.basename(cspec_filename)))
          except:
            pass
          #TTE
          tterelpath     = os.path.relpath(os.path.abspath(tte_filename),os.path.abspath(dirPath))
          try:
            shutil.copyfile(tterelpath, "%s/%s" % (dirPath,os.path.basename(tte_filename)))
          except:
            pass
          #RSP (or RSP2)
          rsprelpath     = os.path.relpath(os.path.abspath(response),os.path.abspath(dirPath))
          try:
            shutil.copyfile(rsprelpath, "%s/%s" % (dirPath,os.path.basename(response)))
          except:
            pass
        
        pass
            
    pass
    
    myDict                = {}
    myDict['PHA2filesGBM']      = PHA2files
    myDict['backFilesGBM']      = backFiles
    myDict['RSPfilesGBM']       = RSPfiles
    #Add the produced files to the results dictionary
    AddResults(myDict)
    
    #Now create the soft links in the directory myDict['SpectraWorkDir']/to_fit
    _addSpectraToFitDirectory(PHA2files,backFiles,RSPfiles,os.path.abspath(lat[0].out_dir))            
    
    return 1

##################################################
def _addSpectraToFitDirectory(PHA2files,backFiles,RSPfiles,workdir):

    curdir                = os.getcwd()

    runShellCommand('mkdir -p %s/to_fit' % workdir)
    
    for myfile in PHA2files + backFiles + RSPfiles:
        abspath  = os.path.abspath(myfile)
        os.chdir('%s/to_fit' % workdir)
        relpath  = os.path.relpath(abspath)        
        basename = os.path.basename(myfile)
        if os.path.exists(basename): runShellCommand('rm -rf %s' %basename)
        if os.path.exists(relpath):
            print basename,'->',relpath
            shutil.copyfile(relpath, basename)
            pass
        os.chdir(curdir)        
        pass

    os.chdir(curdir)
    
pass
##################################################
def MakeLATSpectra(**kwargs):
    print '====> MakeLATSpectra()'  
        
    thisCommand               = commandDefinitions.commands['MakeLATSpectra']
    harvestParameters(thisCommand,kwargs)
    (tstart,tstop,flat_roi,bkge,rspgen,suffix,ebins) = thisCommand.getParameters("sp_tstarts,sp_tstops,flat_roi,bkge,rspgen,suffix,ebins")
    
    lat[0].Ebins = int(ebins)
    
    if suffix=="" and flat_roi==1:   suffix='_ROI'
    elif suffix=="" and flat_roi==0: suffix='_ROI_E'
    detector='ROI'
    if flat_roi==False: detector='ROI_E'
    
    out_dir    = lat[0].out_dir+'/' + suffix
    runShellCommand('mkdir -p %s' % out_dir)
    
    PHA2Name = out_dir+'/'+lat[0].grb_name+'_LAT_'+detector+'.pha2'
    BAK2Name = out_dir+'/'+lat[0].grb_name+'_LAT_'+detector+'.bak2'
    RSP2Name = out_dir+'/'+lat[0].grb_name+'_LAT_'+detector+'.rsp2'
    
    
    Nintervals = len(tstart)

    PHA1_files = []
    BAK1_files = []
    RSP1_files = []
    goodStart  = []
    goodStop   = []
    
    for i in range(Nintervals):
        t1 = tstart[i]
        t2 =  tstop[i]
        
        if t2<=t1: 
            #Invalid time interval
            print ("Invalid time interval requested: %s - %s. Skipping..." % (t1,t2))
            continue
        else:            
            print '-------------------------------------------------- %.3f - %.3f --------------------------------------------------' %(t1,t2)
        
        validInterval = True
            
        filesOutput          = Make_PHA_RSP_Files(tstart=t1,tstop=t2,flat_roi=flat_roi,suffix=suffix,rspgen=rspgen,mode='go')
        pha_File             = filesOutput['PHA1']        
        rsp_File             = filesOutput['RSP']
        
        bak_File             = None
        if bkge: bak_File    = Make_BKG_PHA(start=t1,stop=t2,flat_roi=flat_roi,mode='go')
       
        for fuffa in (pha_File,rsp_File):
            print 'file: ', fuffa
            if fuffa == None:
                validInterval = False
                continue
            
            if os.path.exists(fuffa):
                validInterval = True
            else:
                validInterval = False
                pass
            pass

        if bkge: 
            print 'file: ', bak_File
            if bak_File==None:
                validInterval = False
            
            if os.path.exists(bak_File):
                validInterval = True
            else:
                validInterval = False
            pass

        else:
            print 'WARNING!! THE BACKGROUND FILE HAS NOT BEEN GENERATED!! ALL THE RELATIVE KEYWORDS WILL BE SET TO none!!!'
            pass
            
        print validInterval, len(goodStart)
        
        if validInterval:
            goodStart.append(t1)
            goodStop.append(t2)
            PHA1_files.append(pha_File)
            RSP1_files.append(rsp_File)
            if bkge: BAK1_files.append(bak_File)
            pass
        pass
            
    if(len(goodStart) < 1): 
        print("No valid intervals, nothing to do!")
        return
    
    try:
        genutils.PHA1s_to_PHA2(goodStart,goodStop,PHA1_files,PHA2Name, lat[0].GRB.Ttrigger)        
        genutils.RSPs_to_RSP2(goodStart,goodStop,RSP1_files,RSP2Name, lat[0].GRB.Ttrigger)        
        if bkge: genutils.PHA1s_to_PHA2(goodStart,goodStop,BAK1_files,BAK2Name, lat[0].GRB.Ttrigger)
    except:
        print  ' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Something went wrong in the generation of the PHA2 files....'
        print "Unexpected error:", sys.exc_info()[0]
        print "Try to continue anyway"
    
    #Now fix the keywords RESPFILE and BACKFILE, and add the corresponding columns
    thisPha2            = pyfits.open(PHA2Name,'update')
    specExt             = thisPha2['SPECTRUM']
    specExt.header.update('RESPFILE','none')
    specExt.header.update('BACKFILE','none')
    #Add the columns "RESPFILE" and "BACKFILE"
    respfileList        = []
    backfileList        = []
    for intervalID in range(specExt.data.size):
        respfileList.append('%s{%s}' % (os.path.basename(RSP2Name),intervalID+1))
        if bkge: backfileList.append('%s{%s}' % (os.path.basename(BAK2Name),intervalID+1))
        pass
    respfileCol         = pyfits.Column(name='RESPFILE',format='32A',
                                        array=numpy.array(respfileList))
    if bkge:
        backfileCol         = pyfits.Column(name='BACKFILE',format='32A',
                                            array=numpy.array(backfileList))
        coldefs             = pyfits.ColDefs([respfileCol,backfileCol])
    else:
        coldefs             = pyfits.ColDefs([respfileCol])
        
    newTable            = pyfits.new_table(coldefs)
    newTable.writeto('__columns.fits',clobber=True)
    thisPha2.close()
    
    #now merge the table with the two columns with the PHA file    
    cmdline = "faddcol infile=%s\[SPECTRUM] colfile=__columns.fits colname='-'" %(PHA2Name)
    args = shlex.split(cmdline)
    p = subprocess.check_call(args)
    os.remove('__columns.fits')         
    
    myDict                = {}
    myDict['PHA2filesLAT']      = PHA2Name
    if bkge: myDict['backFilesLAT']      = BAK2Name
    else:    myDict['backFilesLAT']      = 'None'
    
    myDict['RSPfilesLAT']       = RSP2Name
    #Add the produced files to the results dictionary
    AddResults(myDict)

    #Now create the soft links in the directory myDict['SpectraWorkDir']/to_fit
    _addSpectraToFitDirectory([PHA2Name],[BAK2Name],[RSP2Name],os.path.abspath(lat[0].out_dir))
    
    pass

##################################################
def MakeLLEproducts(**kwargs):
    '''
    MakeLLEproducts([rspTstart=rspTstart,rspTstop=rspTstop,
                     zenithTheta=zenithTheta,ssd=ssd,notransient=notransient,configFile=configFile]
    
    
    Create the RSP, PHA and FT1 file with LLE data for the current GRB.
    
    Mandatory parameters:
    (none)               Without any parameters, all the defaults are used (see below). 
        
    Optional parameters:
    rspTstart            Start time for the computation of the RSP file (default: GBM T05)
    rspTstop             Stop time for the computation of the RSP file (default: GBM T95)
    zenithTheta          Angle to use as Zenith cut (default: the current value for results["ZMAX"])
    ssd                  (True or False) Specify if use the additional SSD cut (default: False)
    notransient          (True or False) Specify if exclude or not Transient events from the LLE sample.
                         If you want to use LLE data for spectral fitting at the same time as Transient
                         event, you should set this to True, to make the LLE sample and the Transient sample
                         independent from each other.
    configFile           The file to be used as configuration (change only if you know what you are doing...)
    mode= drm|pha        Decide to make only the drm or the pha. Default=all
    prefix=GRB|SF        Prefix to search MC directories. Default = GRB
    NOTE: apart from the standard LLE cut, also the PSF cut will be used.
    '''
    prefix                    = 'GRB'
    ra                        = results['RA']
    dec                       = results['DEC']
    trigtime                  = results['GRBTRIGGERDATE']
    try:
        rspTstart                 = results['GBMT05']
    except:
        #No GBM duration available, let's hope the use 
        rspTstart                 = None
        pass
    try:  
        rspTstop                  = results['GBMT95']
    except:
        rspTstop                  = None
        pass
    
    radius_roi                = -1
    zeniththeta               = results['ZMAX']
    theta                     = 100.0
    ssd                       = 0
    notransient               = 0
    outdir                    = os.path.join(os.environ['INDIR'],"LAT",results['GRBNAME']+"_LLE")
    ft2file                   = lat[0].FilenameFT2
    configFile                = os.path.join(os.environ['GTGRB_DIR'],"python","config_LLE_DRM","DefaultLLE.txt")
    mode                      = None
    for key in kwargs.keys():
        if   key.lower()=="rsptstart"   : rspTstart   = eval(str(kwargs[key]))
        elif key.lower()=="rsptstop"    : rspTstop    = eval(str(kwargs[key]))
        elif key.lower()=="zeniththeta" : zeniththeta = int(kwargs[key])
        elif key.lower()=="ssd"         : ssd         = bool(kwargs[key])
        elif key.lower()=="notransient" : notransient = bool(kwargs[key])                
        elif key.lower()=="configfile"  : configFile  = str(kwargs[key])
        elif key.lower()=="mode"        : mode        = str(kwargs[key])
        elif key.lower()=="prefix"      : prefix      = str(kwargs[key])
        else:
            print("Parameter not recognized! %s" %(key))
            return
        pass
    
    if(rspTstart==None or rspTstop==None):
        raise ValueError("Could not get rspTstart and rspTstop, please specify them")

    if not (mode is 'drm' or mode is 'pha'): mode = None
    basename                  = prefix+results['GRBNAME']


    #This produces the 
    makeLLEproducts.makeLLEproducts(ra=ra,dec=dec,basename=basename,
                                    trigtime=trigtime,rspTstart=rspTstart,rspTstop=rspTstop,
                                    radius_roi=radius_roi,zeniththeta=zeniththeta,theta=theta,
                                    ssd=ssd,outdir=outdir,ft2file=ft2file,notransient=notransient,
                                    configFile=configFile, mode=mode)
    
    pass

def MakeLLESpectra(**kwargs):
    print '====> MakeLLESpectra()'  
        
    thisCommand               = commandDefinitions.commands['MakeLLESpectra']
    harvestParameters(thisCommand,kwargs)
    (tstart,tstop) = thisCommand.getParameters("sp_tstarts,sp_tstops")
    
    #Default values
    mode                = 'ciaps'
    outdir              =  lat[0].out_dir
    
    for key in kwargs.keys():
        if   key.lower()=="tstart"   : tstart     = eval(str(kwargs[key]))
        elif key.lower()=="tstop"    : tstop      = eval(str(kwargs[key]))        
        elif key.lower()=="mode"     : mode       = kwargs[key]
    pass 
    
    #Get a list of available response, FT1s and PHAs:    
    
    from scripts import getLLEfiles
    
    indir                      = os.path.join(os.environ['INDIR'],"LAT",results['GRBNAME']+"_LLE")
    getter                     = getLLEfiles.LLEdataCollector(results['GRBNAME'])
    getter.get()
       
    pha                        = getter.cspecFile
    rsp                        = getter.rspFile
    ft1                        = getter.ft1File
      
    phafile                    = os.path.join(indir,pha)
    ft1file                    = os.path.join(indir,ft1)
    response                   = os.path.join(indir,rsp)
    
    print("Files in use:")
    print(phafile)
    print(ft1file)
    print(response)
    
    #Now check that the position in the responses is not too different from the one currently
    #defined
    rspf            = pyfits.open(response)
    ra_obj          = rspf["SPECRESP MATRIX",1].header["RA_OBJ"]
    dec_obj         = rspf["SPECRESP MATRIX",1].header["DEC_OBJ"]
    rspf.close()
    dist            = genutils.angsep(ra_obj,dec_obj,results['RA'],results['DEC'])
    print("\nAngular distance between current position (%s,%s) and position in response (%s,%s): %s\n" %(results['RA'],results['DEC'],ra_obj,dec_obj,dist))
    if(dist > 1.0):
      raise RuntimeError("The angular distance between the position in LLE responses and the one currently set is greater than 1 deg!")

    g        = GBMtools.GRBspectra(ft1file,phafile,response,results=results,FT2=lat[0].FilenameFT2,**kwargs)
    pha2, back, rsp = g.getGRBspectra(tstart,tstop,outdir)
    
    #Now place the soft links in the "to_fit" directory
    PHA2files = []
    backFiles = []
    RSPfiles  = []
    PHA2files.append(os.path.join(lat[0].out_dir,pha2))
    backFiles.append(os.path.join(lat[0].out_dir,back))
    RSPfiles.append(os.path.join(lat[0].out_dir,rsp))            
    _addSpectraToFitDirectory(PHA2files,backFiles,RSPfiles,os.path.abspath(lat[0].out_dir))    
pass

##################################################
def PerformSpectralAnalysis(**kwargs):  
    print '====> PerformSpectralAnalysis()'  

    #Get the models to be used in the fit
    if(filter(lambda x:x.lower()=="models",kwargs.keys())==[]):
      #No specified models, ask for them
      if(os.environ.get('GUIPARAMETERS')=='yes'):
        modelslist            = xspecModels.allModels.keys()
        modelslist.sort()
        ll                    = ListBoxChoice("Choose the models", 
                                              "Pick one or more models to be used in the fit.",
                                              modelslist)
        returnValue           = ll.returnValue()
        suffixes = []
        if(returnValue!=None):
          for fancy in returnValue:
            suffixes.append(xspecModels.allModels[fancy].suffix.replace("_",""))
          pass
          xspecModels.useModels(",".join(suffixes))
          results['MODELS']   = ",".join(suffixes)
        else:
          print("Command interrupted")
          return
      else:
        print("\nWARNING: using predefined models:")
        xspecModels.listActiveModels()
        suffixes = []
        for fancy in xspecModels.models.keys():
          suffixes.append(xspecModels.allModels[fancy].suffix.replace("_",""))
        pass
        xspecModels.useModels(",".join(suffixes))
        results['MODELS']   = ",".join(suffixes)
      pass
    else:
      userSupplied            = kwargs[filter(lambda x:x.lower()=="models",kwargs.keys())[0]]
      xspecModels.useModels(userSupplied)
    pass
    
    xspecModels.listActiveModels()
    
    #Get the configuration (if any)
    confkey                   = filter(lambda x:x.lower()=="configuration",kwargs.keys())
    if(confkey==[]):
      configuration           = None
      print("\nUsing default configuration.")
    else:
      configuration           = kwargs[confkey[0]]
      print("\nUsing user-provided configuration")
    pass
    
    thisCommand               = commandDefinitions.commands['PerformSpectralAnalysis']
    harvestParameters(thisCommand,kwargs)
    (performFit,effAreaCorr,fluxEnergyBands,componentByComponent) = thisCommand.getParameters("performFit,effectiveAreaCorrection,fluxEnergyBands,componentByComponent")
    
    if(effAreaCorr):
      print("\n*** Using effective area correction ***")
    
    toFitDirectory              = '%s/%s/to_fit/' % (os.environ['OUTDIR'],results['GRBNAME'])
    grbName                     = results['GRBNAME']
    trigger                     = results['GRBTRIGGERDATE']
    
    #If GUI is active, select files to be fitted
    if(os.environ.get('GUIPARAMETERS')=='yes'):
      import Tkinter
      import tkFileDialog
      root                    = Tkinter.Tk()
      root.withdraw()
      files = tkFileDialog.askopenfilenames(parent = root, filetypes =
                                            [('PHA files (must be type II)', ('*.pha','*.pha2'))], title = "Select spectra to fit",
                                            multiple = True, initialdir=toFitDirectory )
      root.destroy()
      if(len(files)<1):
        raise RuntimeError("No files selected for fitting. Cannot continue...")
      else:
        PHAfilesRaw           = map(lambda x:os.path.basename(x),files)
    else:
      PHAfilesRaw             = None
    pass
    
    if(PHAfilesRaw!=None):
      #Register it in the results dictionary
      results['PHAFILESRAW']  = ",".join(PHAfilesRaw)
    else:
      results['PHAFILESRAW']  = None
    pass
    
    #Instantiate an Autofit class
    fitter                      = autofit.autofit(toFitDirectory, grbName, trigger, 
                                                  configuration,closestNaI=GetNearestDet(**forceNonInteractive({})),
                                                  fluxEnergyBands=fluxEnergyBands,
                                                  component=componentByComponent,phafilesraw=PHAfilesRaw)
    
    #Flush the output (this is needed when running on the pipeline)
    import sys
    sys.stdout.flush()
    
    #Write xspec scripts
    fitter.writeXspecScript(results['REDSHIFT'],effAreaCorr)
    
    #Perform the fitting
    if(performFit): 
      fitter.performFit(results['REDSHIFT'],effectiveAreaCorrection=effAreaCorr)
      fitter._producePlots()
    else:
      print("\nFit NOT performed, as per user request\n")
    pass  
pass

def CustomizeSpectralPlots(**kwargs):
    thisCommand               = commandDefinitions.commands['CustomizeSpectralPlots']
    harvestParameters(thisCommand,kwargs)
    (interactive,nuFnuUnits)  = thisCommand.getParameters("interactive,nuFnuunits")
    
    PHAfilesRaw               = results.get('PHAFILESRAW')
    if(PHAfilesRaw=='' or PHAfilesRaw==None):
      PHAfilesRaw             = None
    else:
      PHAfilesRaw             = PHAfilesRaw.split(",")
    
    toFitDirectory            = '%s/%s/to_fit/' % (os.environ['OUTDIR'],results['GRBNAME'])
    grbName                   = results['GRBNAME']
    trigger                   = results['GRBTRIGGERDATE']
    auto                      = autofit.autofit(toFitDirectory, grbName, trigger,phafilesraw=PHAfilesRaw);
    auto._producePlots(interactive=interactive,nuFnuUnits=nuFnuUnits)
pass

##################################################
def MakeCompositeLightCurve(**kwargs):
    '''    Make composite Light Curves
    This script will automatically display
    all the available Light curves,    reading the root files in the GRB output directory:    
    Some useful parameters you might want to change: 
    \t XMIN=<value> Minimum value of the X axis
    \t XMAX=<value> Maximum value of the X axis
    \t YMIN1=<value> Minimum value of the Y axis of the 1st panel (from top)
    \t YMAX1=<value> Maximum value of the Y axis of the 1st panel (from top)    
    \t TMIN=<value> Minimum value of the background fitting (to 0)
    \t TMAX=<value> Maximum value of the background fitting (from GRB duration)
    \t DT=<value>   Bin size
    \t BK=y         Make the background Subtraction (tentative)
    \t DETLIST= List of detectors. It could be: Trig|All|b0|b0,n0,n2|...
    \t NAIANGLE = (Optional) All NaI detectors seeing the source with an angle <= NAIANGLE will be included. When using this keyword,
    \t LAT1 = (ENERGY in MeV) Add a LAT lightcurve with a minimum energy specified in the argument (OPTIONAL),
    \t LAT2 = (ENERGY in MeV) Add a LAT lightcurve with a minimum energy specified in the argument (OPTIONAL),
    \t LAT3 = (ENERGY in MeV) Add a LAT lightcurve with a minimum energy specified in the argument (OPTIONAL),
    \t LAT4 = (ENERGY in MeV) Add a LAT lightcurve with a minimum energy specified in the argument (OPTIONAL).
    \t NOTHETA = (True|False) Suppress the plot of the theta angle.
    the output will include ALWAYS the closest BGO detector, and if both BGO detectors have an angle <= 100.0, it will
    include both of them.    
    \t REMAKE=False
    '''
    #baseDir = '%s/%s' % (os.environ['OUTDIR'],grb[0].Name)

    #try:
    baseDir = '%s/%s' % (os.environ['OUTDIR'],grb[0].Name)
    results_fileName='%s/results_%s.txt' % (baseDir,grb[0].Name)
    # This reads the stored results. overw=1: over write the "Set" variables with the stored results.
    ReadResults(ResultsFileName = results_fileName, overw=1)
    #Print()
    # except:
    #       pass
    
    #gtsrcprob='%s/*_gtsrcprob_LIKE_BKGE_*' % baseDir
    #try:
    #    gtsrcprob_fits = glob.glob('%s.fits' % gtsrcprob)[0]
    #except:
    #    gtsrcprob='%s/*_gtsrcprob_LIKE_GBM_*' % baseDir            
    #    try:
    #        gtsrcprob_fits = glob.glob('%s.fits' % gtsrcprob)[0]
    #    except:
    #        gtsrcprob_fits=None
    #        pass
    #    pass
        
    
    #print gtsrcprob
    #try: gtsrcprob_root = glob.glob('%s.root' % gtsrcprob)[0]
    #except: gtsrcprob_root=None
    
    #try: gtsrcprob_fits = glob.glob('%s.fits' % gtsrcprob)[0]
    #except: gtsrcprob_fits=None


    #if not gtsrcprob_fits is None and gtsrcprob_root is None:   latutils.convert(gtsrcprob_fits)
    
    #Print()
    try: detlist_s = results['DETLIST']
    except: detlist_s='all'
    try: naiangle  = results['NAIANGLE']
    except: naiangle=50    
    try: bgoangle  = results['BGOANGLE']
    except: bgoangle=180
    DT        = results['DT']

    BK=0; chatter=1; REMAKE=False;  XMIN=-20; XMAX=100; TMIN=-20; TMAX=300 # Total window
    LAT1=0;LAT2=0;LAT3=0;LAT4=0;NOTHETA=False;
    YMAX={}
    YMIN={}
    YMAX.clear()
    YMIN.clear()
    
    for key in kwargs.keys():
        if   key.upper()=="CHATTER": chatter=kwargs[key]
        elif key.upper()=="DT"     : DT=float(kwargs[key]);   REMAKE = True
        elif key.upper()=="XMIN"   : XMIN=float(kwargs[key]); REMAKE = True
        elif key.upper()=="XMAX"   : XMAX=float(kwargs[key]); REMAKE = True
        elif key.upper()=="TMIN"   : TMIN=float(kwargs[key]); REMAKE = True
        elif key.upper()=="TMAX"   : TMAX=float(kwargs[key]); REMAKE = True
        elif key.upper()=="DETLIST": detlist_s = kwargs[key]; REMAKE = True
        elif key.lower()=="naiangle": naiangle   = float(kwargs[key]); REMAKE = True
        elif key.lower()=="bgoangle": bgoangle   = float(kwargs[key]); REMAKE = True
        elif key.upper()=="REMAKE" and REMAKE==False:         REMAKE = True
        elif key.upper()=="LAT1": LAT1 = float(kwargs[key]); REMAKE = True
        elif key.upper()=="LAT2": LAT2 = float(kwargs[key]); REMAKE = True
        elif key.upper()=="LAT3": LAT3 = float(kwargs[key]); REMAKE = True
        elif key.upper()=="LAT4": LAT4 = float(kwargs[key]); REMAKE = True
        elif 'YMAX' in key.upper():  YMAX[key]=float(kwargs[key])
        elif 'YMIN' in key.upper():  YMIN[key]=float(kwargs[key])
        elif key.upper()=="BK": BK=int(kwargs[key]); REMAKE=True;
        elif key.upper()=="NOTHETA": NOTHETA=bool(kwargs[key]);
        pass
    
    

    ################################################
    # THIS IS THE SELECTED FILE TO BE USED FOR EVENT
    ################################################
    if 'use_in_composite' not in results.keys(): MakeSelect(tstart=XMIN,tstop=XMAX,use_in_composite=1)
    Print()
    
    selected_file = None
    if 'use_in_composite' in results.keys(): selected_file = results['use_in_composite'].replace('.root','.fits')
    # ##############################################
    # TRY TO APPEND PROBABILITY CALCULATION
    # ##############################################
    use_gtsrcprob = 1

    if selected_file is not None and os.path.exists(selected_file):
        if use_gtsrcprob:
            # 1) Use the time resolved analysis:
            gtsrcprob_fits=None
            print ' --- Using the probability computed by gtsrcprob...'            
            list = sorted(glob.glob('%s/ExtendedEmission/gtsrcprob_*.fits' % baseDir))            
            if len(list)>0:
                gtsrcprob_fits=('%s/gtsrcprob_extended.fits' % baseDir)
                file_list=('%s/gtsrcprob_filelist.txt' % baseDir)
                file_list_file=file(file_list,'w')
                for l in list:  file_list_file.write('%s\n'%l)
                file_list_file.close()                
                print ' Merging from %s into %s' %(file_list,gtsrcprob_fits)
                # fmerge = GtApp.GtApp('fmerge')
                # fmerge['infiles'] = '@' + file_list
                # fmerge['outfile'] = gtsrcprob_fits
                # fmerge['clobber'] = 'yes'
                # fmerge['columns'] = ' '
                # fmerge['mextname'] = ' '
                # fmerge['lastkey'] = ' '
                # fmerge.run()
                
                cmd='fmerge infiles=@%s outfile=%s columns="-" clobber=yes' %(file_list,gtsrcprob_fits)
                print cmd
                runShellCommand(cmd)
                if not os.path.exists(gtsrcprob_fits):
                    print 'file %s not found!' % gtsrcprob_fits
                    gtsrcprob_fits=None
                    pass
                pass
            
            if gtsrcprob_fits is None:
                list = sorted(glob.glob('%s/*_gtsrcprob_LIKE_BKGE_*.fits' % baseDir))
                if len(list)==0: list=sorted(glob.glob('%s/*_gtsrcprob_LIKE_BKGE_*.fits' % baseDir))
                if len(list)>0:  gtsrcprob_fits=list[0]
                else: gtsrcprob_fits=None
                pass
            
            if gtsrcprob_fits is not None:
                #if os.path.exists(gtsrcprob_fits)
                print 'Appending probabilities...'
                selected_file = latutils.AppendEventProbability(selected_file,gtsrcprob_fits)
                pass
            else:
                print 'There are no files containing the probability in:'
                print '%s/ExtendedEmission/gtsrcprob_*.fits' % baseDir
                pass
            pass
        print ' ==> Now convert the fits file...'
        latutils.convert(selected_file,grb[0].Ttrigger)
        selected_file_root = selected_file.replace('.fits','.root')
    else:
        selected_file_root = None
        selected_file      = None
        pass
    
    
    from scripts import CompositeLightCurve
    from CLC import runLC
    
    if REMAKE:   print 'Regenerating the configuration file...'

    #lc_compo_file_path = '%s/%s_%.2f_%d_%.2f_%.2f_CompoLC.txt' % (lat[0].out_dir,grb[0].Name,DT,BK,XMIN,XMAX)
    lc_compo_file_path = '%s/%s_%d_CompoLC.txt' % (lat[0].out_dir,grb[0].Name,BK)
    
    
    print 'The configuration file will be saved as:',lc_compo_file_path
    print 'To regenerate it, use the option: REMAKE=Yes'
    NAIDETLIST =[]
    BGODETLIST =[]
    if detlist_s.upper()!="NONE":
        if(naiangle == 180.0): closer_detectors=GetNearestDet(detlist=detlist_s)
        else:                  closer_detectors=GetNearestDet(naiangle=naiangle,bgoangle=bgoangle,detlist='all')
        
        for closdet in closer_detectors:
            if 'n' in closdet.lower():    NAIDETLIST.append(closdet.lower())
            elif 'b' in closdet.lower():  BGODETLIST.append(closdet.lower())
            pass
        print 'NaI detectors used:', NAIDETLIST
        print 'BGO detectors used:', BGODETLIST
        pass
    if (not os.path.exists(lc_compo_file_path)) or REMAKE or len(file(lc_compo_file_path,'r').readlines(0))==0:
        lc_compo_file      = file(lc_compo_file_path,'w')        
        txt                = CompositeLightCurve.makeCompositeLightCurve(grb[0].Name,DT,BK,
                                                                         XMIN,XMAX,
                                                                         TMIN,TMAX,
                                                                         NAIDETLIST,BGODETLIST,YMAX,YMIN,LAT1,LAT2,LAT3,LAT4)    
        lc_compo_file.write(txt)
        lc_compo_file.close()
        pass
    runLC.ReadConfiguration(lc_compo_file_path)
    #theta  = latutils.GetTheta(self.GRB.ra, self.GRB.dec, trsp, self.FilenameFT2)
    if(NOTHETA):
      runLC.Do()
    else:
      runLC.Do(lat[0].FilenameFT2,grb[0].ra,grb[0].dec)
    pass

def PlotAngularSeparation(**kwargs):
    print '====> PlotAngularSeparation()'
        
    thisCommand               = commandDefinitions.commands['PlotAngularSeparation']
    harvestParameters(thisCommand,kwargs)
    (before,after,nav_start,nav_stop) = thisCommand.getParameters("before,after,nav_start,nav_stop")
    
    #if(before==''):
    #  before                  = abs(nav_start)
    #if(after==''):
    #  after                   = abs(nav_stop)
    #results['AFTER']          = float(after)
    #results['BEFORE']         = float(before)
    #before = max(30.0,fabs(results['BEFORE']))
    #after  = max(10.0,results['AFTER'])
    
    obj = lat[0].plotAngSeparation(BEFORE=abs(nav_start),AFTER=abs(nav_stop))

def MakeSelectEnergyDependentROI(**kwargs):
    print '====> MakeSelectEnergyDependentROI'
        
    thisCommand               = commandDefinitions.commands['MakeSelectEnergyDependentROI']
    harvestParameters(thisCommand,kwargs)
    (tstart,tstop,suffix,
     rspgen,plot,
     use_in_composite,
     dt,binsz)                = thisCommand.getParameters("tstart,tstop,suffix,rspgen,plot,useincomposite,dt,binsz")
    
    out_dir =  lat[0].out_dir
    outfiles = []
        
    if suffix is not '_ROI_E':
        out_dir = lat[0].out_dir+'/' + suffix
        runShellCommand('mkdir -p %s' % out_dir)
        pass    
        
    filesOutput = Make_PHA_RSP_Files(tstart   = tstart,
                                     tstop    = tstop,
                                     flat_roi = 0,
                                     suffix   = suffix,
                                     rspgen   = rspgen)
    ##################################################
    # This is the number of events in the ROI(E) file
    ##################################################
    lat[0].evt_file = filesOutput['FIT']
    nevents = latutils.getNumberOfEvents(filesOutput['FIT'])
    print '##################################################'
    print 'Event File set to: %s ' % lat[0].evt_file
    print '---->             (%d events)' % nevents
    print '##################################################'
    legend=['T','S','D','C']
    if nevents>0:
        if plot:
            lat[0].saveEvents2Root()    
            MakeLATLightCurve(dt=dt)
            MakeSkyMap(binsz=binsz)
            outfiles.append(lat[0].lc_outFile)        
            outfiles.append(lat[0].lc_outFile.replace('_lc.fits','_lc.png'))
            outfiles.append(lat[0].mp_outFile)
            outfiles.append(lat[0].mp_outFile.replace('.fits','.png'))
            
            # outfiles.append(lat[0].evt_file)
            # outfiles.append(lat[0].evt_file.replace('.fits','.root'))
            # outfiles.append(lat[0].evt_file.replace('.fits','.txt'))
            evtpng_old = lat[0].evt_file.replace('.fits','evt.png')
            evtpng_new = lat[0].lc_outFile.replace('_lc.fits','_evt.png')
            if os.path.exists(evtpng_old): runShellCommand('mv %s %s' %(evtpng_old,evtpng_new))
            outfiles.append(evtpng_new)
            
            suff_s='%s/%s'%(lat[0].out_dir,suffix)        
            runShellCommand('mkdir -p %s' % suff_s)
            for outfile in outfiles:
                if os.path.exists(outfile): runShellCommand('cp %s %s/.' %(outfile,suff_s))
                pass
            if use_in_composite: results['use_in_composite']='%s' %(lat[0].evt_file.replace('.fits','.root'))
            pass
        
        for evtcls in [0,1,2,3]:
            evt_tmax, evt_emax = lat[0].getMaximumEvent(tstart,tstop,evtcls)
            Nevt               = lat[0].countEVT(tstart,tstop,evtcls)            
            Nevt100MeV         = lat[0].countEVT(tstart,tstop,evtcls,100.0)            
            Nevt1GeV           = lat[0].countEVT(tstart,tstop,evtcls,1000.0)            
            Nevt10GeV          = lat[0].countEVT(tstart,tstop,evtcls,10000.0)            
            results['EnergyMax_Energy_%s%s'%(legend[evtcls],suffix)]              = evt_emax
            results['EnergyMax_Time_%s%s'  %(legend[evtcls],suffix)]              = evt_tmax
            
            results['NumberOfEvents_%s%s'  %(legend[evtcls],suffix)]              = Nevt
            results['NumberOfEvents100MeV_%s%s'  %(legend[evtcls],suffix)]        = Nevt100MeV
            results['NumberOfEvents1GeV_%s%s'    %(legend[evtcls],suffix)]        = Nevt1GeV
            results['NumberOfEvents10GeV_%s%s'   %(legend[evtcls],suffix)]        = Nevt10GeV            
            pass
        T0                 = lat[0].GetFirstTimeAfter()
        results['FirstEventTime%s'  %(suffix)] = T0
        
        # for k in filesOutput.keys():
        #    f = filesOutput[k]
        #    if f is not None: lat[0].AddFileToSave(genutils.addExtension(f,ext,opt='mv'))
        #    pass        
        pass
    else:
        for evtcls in [0,1,2,3]:
            results['EnergyMax_Energy_%s%s'%(legend[evtcls],suffix)]              = nevents
            results['EnergyMax_Time_%s%s'  %(legend[evtcls],suffix)]              = nevents        
            results['NumberOfEvents_%s%s'  %(legend[evtcls],suffix)]              = nevents
            results['NumberOfEvents100MeV_%s%s'  %(legend[evtcls],suffix)]        = nevents
            results['NumberOfEvents1GeV_%s%s'    %(legend[evtcls],suffix)]        = nevents
            results['NumberOfEvents10GeV_%s%s'   %(legend[evtcls],suffix)]        = nevents
            pass
        results['FirstEventTime%s'  %(suffix)] = nevents
        pass
    results['NumberOfEvents%s'  %(suffix)]              = nevents
    pass

def MakeLATLightCurve(**kwargs):
    print '====> MakeLATLightCurve()'
    thisCommand               = commandDefinitions.commands['MakeLATLightCurve']
    harvestParameters(thisCommand,kwargs)
    (dt) = thisCommand.getParameters("dt")

    if os.path.exists(lat[0].evt_file):        
        lat[0].make_LightCurve(dt)
        #lat[0].save_LightCurve_ROOT()
        lat[0].plotLC_PYLAB()
    else:
        print 'MakeLATLightCurve - file : %s Doesn\'t exists, run MakeSelect() or MakeSelectEnergyDependentROI' % lat[0].evt_file
        pass
    pass


def Make_PHA2_File(**kwargs):
    ''' compute select from tstart and tstop. Make the PHA2 file
    \t tstart 
    \t tstop
    \t suffix
    \t dtime
    '''
    
    tstart  = results['TSTART']
    tstop   = results['TSTOP']
    out_dir =  lat[0].out_dir
    suffix  = None
    dtime   = results['DT']
    for key in kwargs.keys():
        if   key.lower()=="tstart": tstart = float(kwargs[key])
        elif key.lower()=="tstop" : tstop  = float(kwargs[key])        
        elif key.lower()=="suffix": suffix = kwargs[key].upper()
        elif key.lower()=="dtime" :  dtime = float(kwargs[key])
        pass
    if suffix is not None:
        out_dir = lat[0].out_dir+'/' + suffix
        runShellCommand('mkdir -p %s' % out_dir)
        pass    
    
    evt_file        = out_dir+'/'+lat[0].grb_name+'_LAT_ROI_%.2f_%.2f.fits' %(tstart,tstop)    
    pha2_outFile    = out_dir+'/'+lat[0].grb_name+'_LAT_%.2f_%.2f.pha2' %(tstart,tstop)
    
    tmin       =  grb[0].Ttrigger + tstart
    tmax       =  grb[0].Ttrigger+tstop
    
    # This will make special pha and rsp and fits file    
    nevents    = lat[0].make_select(outfile=evt_file,tmin=tmin,tmax=tmax)
    if nevents > 0:
        lat[0].make_pha2(evfile=evt_file, outfile=pha2_outFile,tstart=tmin,tstop=tmax,dtime=dtime)
        pass
    pass

def Make_PHA_RSP_Files(**kwargs):
    ''' compute select from tstart and tstop. Make the PHA1 file and RSP.
    Notice that this will produce a fixed ROI selection.
    \t tstart 
    \t tstop
    \t flat_roi = 1|0
    \t suffix   = None
    \t rspgen   = 1|0
    '''

    tstart  = 0 #results['TSTART']
    tstop   = 10 #results['TSTOP']
    
    out_dir   =  lat[0].out_dir
    flat_roi  = 1
    rspgen    = 1
    suffix    = None
    for key in kwargs.keys():
        if   key.lower()=="tstart":   tstart   = float(kwargs[key])
        elif key.lower()=="tstop":    tstop    = float(kwargs[key])        
        elif key.lower()=="flat_roi": flat_roi = int(kwargs[key])
        elif key.lower()=="suffix":   suffix   = kwargs[key].upper()
        elif key.lower()=="rspgen":   rspgen   = int(kwargs[key])                
        pass
    
    
    if suffix is not None:
        out_dir = lat[0].out_dir+'/' + suffix
        runShellCommand('mkdir -p %s' % out_dir)
        pass    
    
    detector='ROI'
    if flat_roi==0: detector='ROI_E'
    
    evt_file        = out_dir+'/'+lat[0].grb_name+'_LAT_'+detector+'_%.2f_%.2f.fits' %(tstart,tstop)
    sp_outFile      = out_dir+'/'+lat[0].grb_name+'_LAT_'+detector+'_%.2f_%.2f.pha'%(tstart,tstop)
    rsp_File        = out_dir+'/'+lat[0].grb_name+'_LAT_'+detector+'_%.2f_%.2f.rsp'%(tstart,tstop)

    filesOutput={}

    filesOutput['PHA1'] = sp_outFile
    filesOutput['RSP']  = rsp_File
    filesOutput['FIT']  = evt_file

    if not rspgen: filesOutput['RSP'] = None
    
    # Set the tstart and tstop...
    tmin       =  grb[0].Ttrigger + tstart
    tmax       =  grb[0].Ttrigger + tstop
    lat[0].setTmin(tmin)
    lat[0].setTmax(tmax)
    ##################################################
    print 'Make_PHA_RSP_Files(tstart=%s, tstop=%s, flat_roi=%s, rspgen=%s, suffix=%s)' %(tstart,tstop,flat_roi,rspgen,suffix)

    ###################################################
    # THIS IS TO RESET THE INITIAL SELECTION
    # IT CREATES AN EVENT FILE BASED ON A FLAT ROI
    #     
    nevents    = lat[0].make_select(outfile=evt_file)
    
    if flat_roi: # Case when the ROI is FLAT
        # This will make special pha and rsp and fits file    
        lat[0].make_pha1(evfile=evt_file,outfile=sp_outFile)
        if rspgen: lat[0].make_rsp(specfile=sp_outFile,outfile=rsp_File)
        pass
    elif flat_roi==0: # Case when the ROI is ENERGY DEPENDENT
        print("\n\nENERGY DEPENDENT ROI\n\n")
        myfiles={}
        PHAtype  = 'PHA1'
        if rspgen: myfiles.update(lat[0].make_rsp2(PHAtype)) # this makes the PHA2/PHA1 file and the RSP file
        myfiles.update(lat[0].make_rsp2('FIT')) # this makes only the events file
        for k in myfiles.keys(): runShellCommand('mv %s %s' % (myfiles[k],filesOutput[k]))
        pass
    else:
        print 'option not recognize.'
        filesOutput={}
        pass
    print '--------------------------------------------------'                
    try:
        print 'FILE %s CONTAINS %i EVENTS' % (filesOutput['FIT'], latutils.getNumberOfEvents(filesOutput['FIT']))
    except:
        print 'FILE %s DOES NOT EXIST!' % (filesOutput['FIT'])
        pass
    print '--------------------------------------------------'    
    return filesOutput



def MakeSelect(**kwargs):
    print '====> MakeSelect()'
        
    thisCommand               = commandDefinitions.commands['MakeSelect']
    harvestParameters(thisCommand,kwargs)
    (tstart,tstop,suffix,
     rspgen,plot,
     use_in_composite,
     dt,binsz)                = thisCommand.getParameters("tstart,tstop,suffix,rspgen,plot,useincomposite,dt,binsz")
    out_dir =  lat[0].out_dir
    outfiles = []
        
    if suffix!='ROI':
        out_dir = lat[0].out_dir+'/' + suffix
        runShellCommand('mkdir -p %s' % out_dir)
        pass    
    
    filesOutput = Make_PHA_RSP_Files(tstart   = tstart,
                                     tstop    = tstop,
                                     flat_roi = 1,
                                     suffix   = suffix,
                                     rspgen   = rspgen)
    lat[0].evt_file     = filesOutput['FIT']
    nevents = latutils.getNumberOfEvents(filesOutput['FIT'])
    
    results['NumberOfEvents%s'  %(suffix)]              = nevents
    results['pha_file'] = filesOutput['PHA1']            
    if rspgen:   results['rsp_File'] = filesOutput['RSP']

    #duration = results['GBMT90'] # grb[0].TStop-grb[0].TStart
    legend=['T','S','D','C']
    if nevents>0:
        if plot:
            #lat[0].saveEvents2Root()        
            MakeLATLightCurve(dt=dt,mode='go')
            MakeSkyMap(binsz=binsz,mode='go')
            
            outfiles.append(lat[0].lc_outFile)        
            outfiles.append(lat[0].lc_outFile.replace('_lc.fits','_lc.png'))
            outfiles.append(lat[0].mp_outFile)
            outfiles.append(lat[0].mp_outFile.replace('.fits','.png'))

            # outfiles.append(lat[0].evt_file)
            # outfiles.append(lat[0].evt_file.replace('.fits','.root'))
            # outfiles.append(lat[0].evt_file.replace('.fits','.txt'))
            # outfiles.append(lat[0].evt_file.replace('.fits','evt.png'))
            
            evtpng_old = lat[0].evt_file.replace('.fits','evt.png')
            evtpng_new = lat[0].lc_outFile.replace('_lc.fits','_evt.png')
            if os.path.exists(evtpng_old): runShellCommand('mv %s %s' %(evtpng_old,evtpng_new))
            outfiles.append(evtpng_new)
            
            suff_s='%s/%s'%(lat[0].out_dir,suffix)        
            runShellCommand('mkdir -p %s' % suff_s)
            for outfile in outfiles:
                if os.path.exists(outfile): runShellCommand('cp %s %s/.' %(outfile,suff_s))
                pass
            if use_in_composite: results['use_in_composite']='%s' %(lat[0].evt_file.replace('.fits','.root'))

            pass
        
        for evtcls in [0,1,2,3]:
            evt_tmax, evt_emax = lat[0].getMaximumEvent(tstart,tstop,evtcls)
            Nevt               = lat[0].countEVT(tstart,tstop,evtcls)
            Nevt100MeV         = lat[0].countEVT(tstart,tstop,evtcls,100.0)            
            Nevt1GeV           = lat[0].countEVT(tstart,tstop,evtcls,1000.0)            
            Nevt10GeV          = lat[0].countEVT(tstart,tstop,evtcls,10000.0)            
            results['EnergyMax_Energy_%s%s'%(legend[evtcls],suffix)]              = evt_emax
            results['EnergyMax_Time_%s%s'  %(legend[evtcls],suffix)]              = evt_tmax
            
            results['NumberOfEvents_%s%s'  %(legend[evtcls],suffix)]              = Nevt
            results['NumberOfEvents100MeV_%s%s'  %(legend[evtcls],suffix)]        = Nevt100MeV
            results['NumberOfEvents1GeV_%s%s'    %(legend[evtcls],suffix)]        = Nevt1GeV
            results['NumberOfEvents10GeV_%s%s'   %(legend[evtcls],suffix)]        = Nevt10GeV            
            pass
        T0                 = lat[0].GetFirstTimeAfter()
        results['FirstEventTime%s'  %(suffix)] = T0
        # lat[0].SaveFiles(suffix=suffix)
    else:
        for evtcls in [0,1,2,3]:
            results['EnergyMax_Energy_%s%s'%(legend[evtcls],suffix)]              = nevents
            results['EnergyMax_Time_%s%s'  %(legend[evtcls],suffix)]              = nevents            
            results['NumberOfEvents_%s%s'  %(legend[evtcls],suffix)]              = nevents
            results['NumberOfEvents100MeV_%s%s'  %(legend[evtcls],suffix)]        = nevents
            results['NumberOfEvents1GeV_%s%s'    %(legend[evtcls],suffix)]        = nevents
            results['NumberOfEvents10GeV_%s%s'   %(legend[evtcls],suffix)]        = nevents
            pass
        results['FirstEventTime%s'  %(suffix)] = nevents
        pass
    
    
    return nevents
    
def MakeSelectFrontBack(**kwargs):
    print '====> MakeSelectFrontBack()'
        
    thisCommand               = commandDefinitions.commands['MakeSelectFrontBack']
    harvestParameters(thisCommand,kwargs)
    (tstart,tstop,
     rspgen,plot,
     dt,binsz)                = thisCommand.getParameters("tstart,tstop,rspgen,plot,dt,binsz")
    
    irf0=lat[0]._ResponseFunction
    for suff in ('FRONT','BACK'):
        print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
        print '                  ',suff
        print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'                
        suffix = '_ROI_%s' % suff
        lat[0].SetResponseFunction(irf0+'::'+suff)
        nevents = MakeSelect(suffix=suffix, tstart=tstart, tstop=tstop,rspgen=rspgen,plot=plot,dt=dt,binsz=binsz)
    pass
    lat[0].SetResponseFunction(irf0)
    pass


def MakeSelectEnergyDependentROIFrontBack(**kwargs):
    print '====> MakeSelectEnergyDependentROIFrontBack()'
        
    thisCommand               = commandDefinitions.commands['MakeSelectEnergyDependentROIFrontBack']
    harvestParameters(thisCommand,kwargs)
    (tstart,tstop,
     rspgen,plot,
     dt,binsz)                = thisCommand.getParameters("tstart,tstop,rspgen,plot,dt,binsz")

    irf0=lat[0]._ResponseFunction
    for suff in ['FRONT','BACK']:
        try:
            lat[0].SetResponseFunction(irf0+'::'+suff)
            suff_e='_'+suff+'_ROIE'
            MakeSelectEnergyDependentROI(suffix=suff_e,
                                         tstart=tstart,
                                         tstop=tstop,
                                         rspgen=rspgen,
                                         plot=plot,
                                         dt=dt,
                                         binsz=binsz)
        except:
            pass
        pass
    lat[0].SetResponseFunction(irf0)
    pass

    
def MakeSkyMap(**kwargs):
    import plotMAP
    print '====> MakeSkyMap()'
    thisCommand               = commandDefinitions.commands['MakeSkyMap']
    harvestParameters(thisCommand,kwargs)
    (BINSZ) = thisCommand.getParameters("binsz")

    ROI   = results['ROI']
    
    #energyw=0
    for key in kwargs.keys():
        if key.upper()  =="BINSZ":   BINSZ   = float(kwargs[key])
    #    if key.lower()  =="energyw": energyw = int(kwargs[key])
        pass
    lat[0].make_skymap(nxpix=int(2*ROI/BINSZ), nypix=int(2*ROI/BINSZ), binsz=BINSZ)
    plotMAP.plotCMAP(cmap_file=lat[0].mp_outFile,evt_file=lat[0].evt_file,out_file=lat[0].mp_outFile.replace('_map.fits','_map.png'),radius=None,txt=None,show=False)    
    #lat[0].plotCMAP(drawopt="colz",nbins=int(ROI/BINSZ), energyw=0)
    #lat[0].plotCMAP(drawopt="colz",nbins=int(ROI/BINSZ), energyw=1)
    pass


def MakeGtFindSrc(**kwargs):
    ''' Compute the best localization using gtfindsrc
    \t  UPDATE_POS: Update the position if the new localization is within the ERR (0|1)
    '''        
    
    print '====> MakeGtFindSrc()'
    thisCommand               = commandDefinitions.commands['MakeGtFindSrc']
    harvestParameters(thisCommand,kwargs)
    (UPDATE_POS,LIKE_SUFFIX) = thisCommand.getParameters("UPDATE_POS,LIKE_SUFFIX")
    print UPDATE_POS,LIKE_SUFFIX
    try:
        expcube  = results['%s_expcube'      % LIKE_SUFFIX]
        expmap   = results['%s_expmap'       % LIKE_SUFFIX]
        srcmdl   = results['%s_src_filePath' % LIKE_SUFFIX]
        evfile   = results['%s_evt_file'     % LIKE_SUFFIX]
        
        kwargs['expcube'] = expcube
        kwargs['expmap']  = expmap
        kwargs['srcmdl']  = srcmdl
        kwargs['evfile']  = evfile 
    except:
        print("WARNING: could not retrieve results from likelihood with suffix %s... " %(LIKE_SUFFIX))
        print("         Make sure you provide yourself expcube, expmap and XML model, OR that you know what you are doing...")
        pass
    lat[0].gtfindsrc(**kwargs)
    outfile=open(lat[0].findsrc_outFile,'r')
    lines=outfile.readlines()
    error = float(lines[0].split()[3])
    for l in lines:
        if l.find('initial starting values:')>=0:
            vals=l.split(':')[1].strip().split()
            ra0 = float(vals[0])
            dec0= float(vals[1])
        elif l.find('final values:')>=0:
            vals=l.split(':')[1].strip().split()                        
            ra1 = float(vals[0])
            dec1= float(vals[1])
        elif l.find('angular separation:')>=0:
            vals=l.split(':')[1].strip().split()
            sep=float(vals[0])
            pass
        pass
    results['FindSrc_RA0']    = ra0
    results['FindSrc_DEC0']   = dec0
    results['FindSrc_RA1']    = ra1
    results['FindSrc_DEC1']   = dec1
    results['FindSrc_Sep']    = sep    
    results['FindSrc_ERR']    = error
    results['FindSrc_UPDATE'] = 0
    print '--------------------------------------------------'
    print ' *** GTFINDSRC RESULTS ***'
    print ' NEW POSITION [RA,DEC].....: %.3f, %.3f' %(ra1,dec1)
    print ' ERROR [68%%,90%%]...........: %.3f, %.3f' %(error,1.4*error)
    print '--------------------------------------------------'
    if error < results['ERR']:
        if UPDATE_POS:
            UpdatePosition(new_ra=ra1,new_dec=dec1)
            results['FindSrc_UPDATE']=1
            pass
        pass    
    pass

def MakeComputePreburstBackground(mode='ql'):
    print '====> MakeComputePreburstBackground()'
    #Prompt(['PREBURST'], mode=mode)
    preburst=1000#results['PREBURST']    
    if mode=='ql':
        FIXING=1
    else:
        FIXING=0
        pass

    ##################################################
    EXP_CUBE_BKG='%s/bkg_ltcube.fits' %lat[0].out_dir
    EXP_MAP_BKG ='%s/bkg_expmap.fits' %lat[0].out_dir
    bkg_filePath='%s/bkg_model.xml' %lat[0].out_dir
    EXP_CUBE_SRC='none'
    EXP_MAP_SRC ='none'
    src_filePath    ='%s/%s_model.xml' %(lat[0].out_dir,grb[0].Name)
    ##################################################
    
    tBGstart = grb[0].Ttrigger-preburst
    tBGend   = grb[0].Ttrigger
    tstart   = grb[0].TStart
    tstop    = grb[0].TStop
    
    #lat[0].setEmin(results['EMIN'])
    lat[0].setTmin(tBGstart)
    lat[0].setTmax(tBGend)
    lat[0].print_parameters()
    
    latutils.CreateSource_XML(bkg_filePath)
    # Add the Isotropic Component
    latutils.Add_IsoPower_XML(xmlFileName=bkg_filePath)
    # Add the Galactic Component
    latutils.Add_GalacticDiffuseComponent_XML(xmlFileName=bkg_filePath)

    latutils.Close_XML(bkg_filePath)        

    lat[0].make_select()
    
    if(not EXP_CUBE_BKG=='none'):
        lat[0].make_expCube(outfile=EXP_CUBE_BKG)
        pass
    lat[0].make_expMap(expcube=EXP_CUBE_BKG,outfile=EXP_MAP_BKG)
    lat[0].make_gtdiffrsp(srcmdl=bkg_filePath)
    
    like = lat[0].pyLike(model=bkg_filePath,expcube=EXP_CUBE_BKG,expmap=EXP_MAP_BKG,fixing=FIXING)
    print '===================================== Fitting the background ================================='
    logLike = like.fit(covar=True)
    NobsTot = like.nobs.sum()
    
    like.writeXml(xmlFile=bkg_filePath)
    print like.model
    sourceNames = like.sourceNames()
    for srcN in sourceNames:
        Ts      = like.Ts(srcN)
        emin = max(100.,results['EMIN'])
        emax = min(10000.,results['EMAX'])
        
        Npred_100_1000    =like[srcN].src.Npred(emin,1000)
        Npred_1000_10000  =like[srcN].src.Npred(1000,emax)
        # Npred_10000_100000=like[srcN].src.Npred(10000,100000)
        print 'TS                        (%s)     = %.2f' % (srcN,Ts)
        print 'N Predicted [%.1f -  1 GeV] from %s = %s ' % (emin/1000.,srcN,Npred_100_1000) 
        print 'N Predicted [1    - %.1f GeV] from %s = %s ' % (emax/1000.,srcN, Npred_1000_10000) 
        print '..................................................'
        pass
    print ' N Observed (%s - %s) MeV  = %i ' % (results['EMIN'],results['EMAX'],NobsTot)
    print ' logLikelihood             = %s ' % (logLike)
    like.plot()
    like.residualPlot.canvas.Print('%s/BKGresidualPlot.png' % lat[0].out_dir )
    like.spectralPlot.canvas.Print('%s/BKGspectralPlot.png' % lat[0].out_dir )
    
    lat[0].setTmin(tstart)
    lat[0].setTmax(tstop)
    lat[0].print_parameters()
    lat[0].make_select()
    pass


def MakeLikelihoodAnalysis(**kwargs):
    print '====> MakeLikelihoodAnalysis()'
    return_code=1
    like_model_keys           = filter(lambda x:x.lower()=="like_model",kwargs.keys())
    if(like_model_keys==[]):
      #No specified models, ask for them
      if(os.environ.get('GUIPARAMETERS')=='yes'):
        if(results['IRFS'].find("P7REP_TRANSIENT")>=0):
          modelslist            = ['GRB: a point source with a power law spectrum (you have always to include this or the next)',
                                   'GRBEXP: a point source with a power law spectrum and exponential cut-off (or this)',      
                                   'ISO: isotropic template with power law spectrum',
                                   'GAL0: the Galactic template with fixed normalization',
                                   'GAL: the Galactic template with free normalization',
                                   'BKGE_GAL_GAMMAS: the Galactic component as estimated by the BKGE',
                                   'BKGE_CR_EGAL: the extra-Galactic and cosmic rays component as estimated by the BKGE',
                                   'BKGE_TOTAL: the total background as estimated by the BKGE']
          defaultChoice         = [0,3,6]
        else:          
          modelslist            = ['GRB: a point source with a power law spectrum (you have always to include this or the next)',
                                   'GRBEXP: a point source with a power law spectrum and exponential cut-off (or this)',
                                   'ISO: isotropic template with power law spectrum',
                                   'TEM: extra-galactic template',
                                   'GAL0: the Galactic template with fixed normalization',
                                   'GAL: the Galactic template with free normalization']
          defaultChoice         = [0,3,4]
        pass
        
        returnValue           = ListBoxChoice("Choose the models", 
                                              "Pick one or more models to be used in the likelihood",
                                              modelslist,defaultChoice).returnValue()
        suffixes = []
        if(returnValue!=None and returnValue!=[]):
          for fancy in returnValue:
            suffixes.append(fancy.split(":")[0])
          pass
          results['like_model']   = "+".join(suffixes)
        else:
          print("Command interrupted")
          return
      else:
        #Check if like_model is in results
        if(not 'like_model' in results.keys()):
          print("\nWARNING: using predefined models:")
          if(results['IRFS'].find("TRANSIENT")>=0):
            results['like_model'] = "GRB+BKGE_CR_EGAL+GAL0"
          else:
            results['like_model'] = "GRB+TEM+GAL0"
        pass
      pass
    else:
      results['like_model'] = kwargs[like_model_keys[0]]
    pass
    
    print("\n Likelihood model: %s" %(results['like_model']))
    
    thisCommand               = commandDefinitions.commands['MakeLikelihoodAnalysis']
    harvestParameters(thisCommand,kwargs)
    (tstart,tstop,pha,extended,gtsrcprob,suffix,
     BB_prior,user_time_bins,TSMIN,TSMIN_EXT,
     femin,femax,like_timeBins,nlikebins,extended_tstart,extended_tstop) = thisCommand.getParameters("tstart,tstop,pha,extended,prob,suffix,BB_prior,user_time_bins,tsmin,tsmin_ext,femin,femax,like_timeBins,NLIKEBINS,EXTENDED_TSTART,EXTENDED_TSTOP")
    expomapradius = lat[0].radius+10.0
    
    # #################################################
    # SAVE THE CURRENT SETUP:
    T00       = grb[0].TStart
    T01       = grb[0].TStop
    evt_file0 = lat[0].evt_file
    # #################################################
    
    chatter = 1
    from scripts import LikelihoodFit
    bkg_filePath = '%s/bkg_model.xml'   % lat[0].out_dir
    #Prompt(['TSMIN'], mode=mode)
    #TSMIN = results['TSMIN']
    #Prompt(['TSMIN_EXT'], mode=mode)
    #TSMIN_EXT = results['TSMIN_EXT']
    print '==================================================> MakeLikelihoodAnalysis()<=================================================='
    
    if globalQueryMode=='query':
        FIXING=1
    elif(globalQueryMode=='go'):
        FIXING=0
    else:
        print("Mode is not recognized! Asking for parameters...")
        FIXING=1
    pass
    #################################################    
    #Prompt(['like_model'], mode=mode)
    like_model                = results['like_model']
    ##################################################
    EMIN                      = float(results['EMIN'])
    EMAX                      = float(results['EMAX'])
    ##################################################    
    if 'PREFIT' in like_model:
        if not os.path.exists(bkg_filePath):
            MakeComputePreburstBackground(mode)
            pass
        pass
    
    ##################################################    
    # STEP 1 DEFINE SOME INTERVALS....
    ##################################################
    LIKELIHOODS = {}
    
    if tstart<tstop:
        ##################################################
        #      CASE A: USER DEFINED INTERVAL             #
        ##################################################
        name             = suffix
        LIKELIHOODS[name]= [tstart,tstop]
        pass
    # #################################################
    #   TIME RESOLVED LIKELIHOOD ANALYSIS
    # #################################################
    if extended==1:
        print '=============================================================================================='
        print '           Now run the likelihood time-resolved analysis                        '
        print '=============================================================================================='
        from scripts import MakeOptimalBinning        
        #Prompt(['like_timeBins'], mode=mode); 
        like_timeBins_string       = "%s,%s,%s" %(like_timeBins,extended_tstart,extended_tstop)
        # #################################################
        bins0=[]
        bins1=[]
        xscale='log'
        #if 'AUTO' in like_timeBins_string.upper():
        #    print 'Select AUTO binning...'
        #    tmin_offset = results['GRBT05']
        #    tmax_offset = float(like_timeBins_string.split(',')[3])
            
        #   EvtPerBin = int(like_timeBins_string.split(',')[1])        

        #    tmin      = grb[0].Ttrigger + tmin_offset
        #    tmax      = grb[0].Ttrigger + tmax_offset

        #    try:     Expo      = float(like_timeBins_string.split(',')[4])
        #    except:  Expo      = 0
        #    
        #    lat[0].setTmin(tmin)
        #    lat[0].setTmax(tmax)
        #    lat[0].make_select()
        #    bins0,bins1  = MakeOptimalBinning.EqualNumberOfEvents(lat[0],EvtPerBin,Expo,results['GBMT95'])        
        #    if results['GRBT05']>0:
        #        bins0.insert(0,grb[0].Ttrigger)
        #        bins1.insert(0,grb[0].Ttrigger+results['GRBT05'])
        #        pass
        #    pass
        # #################################################
        if 'CONSTANT_TS' in like_timeBins_string.upper():
            print 'Select CONSTANT_TS binning...'
            tmin_offset=float(like_timeBins_string.split(',')[1])
            tmax_offset=float(like_timeBins_string.split(',')[2])
            tmin      = grb[0].Ttrigger + tmin_offset
            tmax      = grb[0].Ttrigger + tmax_offset
            lat[0].setTmin(tmin)
            lat[0].setTmax(tmax)
            lat[0].make_select()
            bins=[tmin_offset,tmax_offset]        
            bins0,bins1  = MakeOptimalBinning.SplitForGTI(lat[0],bins,chatter=chatter)        
            # #################################################
        #elif 'CONSTANT_FLUENCE' in like_timeBins_string.upper():
        #    print 'Select CONSTANT_FLUENCE binning...'
        #    tmin_offset=float(like_timeBins_string.split(',')[1])
        #    tmax_offset=float(like_timeBins_string.split(',')[2])
        #    tmin      = grb[0].Ttrigger + tmin_offset
        #    tmax      = grb[0].Ttrigger + tmax_offset
        #    Fluence_per_bin = float(like_timeBins_string.split(',')[3])
        #    lat[0].setTmin(tmin)
        #    lat[0].setTmax(tmax)
        #    lat[0].make_select()
        #    bins         = MakeOptimalBinning.ConstantFluence(lat[0],tmin_offset,tmax_offset,Fluence_per_bin)        
        #    if len(bins)==0:
        #        print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
        #        print ' Cannot use ConstantFluence binning. Using: 0 - On - Dur - 2 Dur - 5 Dur'
        #        print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'            
        #        bins = [0.0,results['GRBT05'],results['GRBT95'],2*results['GRBT95'],5*results['GRBT95']]
        #        pass
        #    bins0,bins1  = MakeOptimalBinning.SplitForGTI(lat[0],bins,chatter=chatter) 
        #    # #################################################
        elif 'BB' in like_timeBins_string.upper():
            print 'Select Bayesian Block binning...'
            tmin_offset=float(like_timeBins_string.split(',')[1])
            tmax_offset=float(like_timeBins_string.split(',')[2])
            tmin      = grb[0].Ttrigger + tmin_offset
            tmax      = grb[0].Ttrigger + tmax_offset
            lat[0].setTmin(tmin)
            lat[0].setTmax(tmax)
            lat[0].make_select()
            bins0,bins1      = MakeOptimalBinning.BayesianBlocks(lat[0],prior=BB_prior)
            # #################################################
        elif 'LOG' in like_timeBins_string.upper():
            print 'Select LOG binning...'
            tmin_offset=float(like_timeBins_string.split(',')[1])
            tmax_offset=float(like_timeBins_string.split(',')[2])
            if tmin_offset==0:   tmin_offset = 1e-3*min(1.0,tmax_offset)

            tmin      = grb[0].Ttrigger + tmin_offset
            tmax      = grb[0].Ttrigger + tmax_offset
            nbins     = int(nlikebins)+1
            bins=[]
            for i in range(nbins):    bins.append(tmin_offset*pow(tmax_offset/tmin_offset,1.0*i/(nbins-1.)))                        
            lat[0].setTmin(tmin)
            lat[0].setTmax(tmax)
            lat[0].make_select()
            bins0,bins1      = MakeOptimalBinning.SplitForGTI(lat[0], bins,chatter=chatter)
            # #################################################
        elif 'LIN' in like_timeBins_string.upper():
            xscale='lin'
            print 'Select LIN binning...'
            tmin_offset=float(like_timeBins_string.split(',')[1])
            tmax_offset=float(like_timeBins_string.split(',')[2])
            tmin      = grb[0].Ttrigger + tmin_offset
            tmax      = grb[0].Ttrigger + tmax_offset
            nbins     = int(nlikebins)+1
            bins=[]
            for i in range(nbins):    bins.append(tmin_offset+(tmax_offset-tmin_offset)*i/(nbins-1.))

            lat[0].setTmin(tmin)
            lat[0].setTmax(tmax)
            lat[0].make_select()
            bins0,bins1      = MakeOptimalBinning.SplitForGTI(lat[0], bins,chatter=chatter)
            # #################################################
        elif 'USER_PROVIDED' in like_timeBins_string.upper():
            bins=[]
            try:
                bins = user_time_bins
                tmin_offset = bins[0]
                tmax_offset = bins[-1]
                tmin      = grb[0].Ttrigger + tmin_offset
                tmax      = grb[0].Ttrigger + tmax_offset
                
                lat[0].setTmin(tmin)
                lat[0].setTmax(tmax)
                lat[0].make_select()
                try: 
                    split_gti=(os.environ['SPLIT_GTI']=='yes')
                except:
                    split_gti=True
                    pass
                if split_gti: bins0,bins1      = MakeOptimalBinning.SplitForGTI(lat[0], bins,chatter=chatter)
                else:         bins0,bins1      = bins[:-1],bins[1:]                
                # #################################################
            except:
                print 'No bins provided. Skip time resolved analysis.'
                bins0=[]
                bins1=[]
                pass
            pass
        
        # #################################################        
        print ' RESETTING THE SELECTION...(%.3f-%.3f) (%s)' %(T00,T01,evt_file0)
        lat[0].setTmin(T00)
        lat[0].setTmax(T01)
        lat[0].evt_file = evt_file0 # THIS HAS NO DIFF RESP    
        # #################################################    
        # YOU NEED A SRC FILE PATH FOR THE EXTENDED EMISSION...
        # #################################################    
        
        NBINS = len(bins0)
        if NBINS > 0:
            equalTS=False
            if 'CONSTANT_TS' in like_timeBins_string.upper():  equalTS = True
            
            results_filename = LikelihoodFit.RunExtendedEmission(lat[0],like_model,results,[bins0,bins1],gtsrcprob=gtsrcprob,ts_min=TSMIN_EXT,equalTS=equalTS)
            lat[0].SetResponseFunction(results['IRFS'])
            from scripts import PlotExtendedEmission_MPL as PlotExtendedEmission
            results1 = PlotExtendedEmission.PlotExtendedEmission(results_filename,results,xscale=xscale,ts_min=TSMIN_EXT,xmin=tmin_offset,xmax=tmax_offset,include_ul=True)            
            AddResults(results1)


            prob_filename = results_filename.replace('.txt','_emax.txt')

            results1=latutils.ParseProbabilityFile(prob_filename)
            AddResults(results1)
            
            if 'LIKE_DURMIN' in results.keys() and 'LIKE_DURMAX' in results.keys():
                t0 =  results['LIKE_DURMIN']
                t1 =  results['LIKE_DURMAX']
            else:
                t0=0
                t1=0
                pass
            if t1>t0:  LIKELIHOODS['LIKE_AG']=[t0,t1]
            print ' LIKELIHOOD DONE. RESETTING THE SELECTION...(%.3f-%.3f) (%s)' %(T00,T01,evt_file0)                    
            lat[0].setTmin(T00)
            lat[0].setTmax(T01)
            lat[0].evt_file = evt_file0 # THIS HAS NO DIFF RESP
            pass
            return
        pass
    # #################################################
    # NOW RUNNING LIKELIHOOD IN SELECTED TIME BINS
    # #################################################
    print '-----------------------------------------------------------------------------------------------------'
    print 'LIKELIHOOD WILL BE COMPUTED IN THE FOLLOWING INTERVALS:'
    for k in LIKELIHOODS.keys(): print k,':',LIKELIHOODS[k][0],',',LIKELIHOODS[k][1] 
    print '-----------------------------------------------------------------------------------------------------'
    
    maximum_TS = -999
    like_maxts = None
    kmax = ''
    
    for k in LIKELIHOODS.keys():
        t0 = LIKELIHOODS[k][0]; t1 = LIKELIHOODS[k][1]            
        # remove previously stored results...
        for k1 in results.keys():
            if k in k1: results.pop(k1)
            pass
        like = LikelihoodFit.MakeFullLikelihood(lat[0],
                                                bkg_filePath = bkg_filePath,
                                                like_model   = like_model,
                                                t1           = t0,
                                                t2           = t1,
                                                results      = results,
                                                ts_min       = TSMIN,
                                                prefix       = k,
                                                FIXING       = FIXING,
                                                gtsrcprob    = gtsrcprob,
                                                mode         = globalQueryMode,
                                                expomapradius = expomapradius)
        try: # This saves in case like=0 because of the 0 events.
            if like.Ts('GRB') > maximum_TS:
                kmax = k
                maximum_TS = like.Ts('GRB')
                like_maxts = like
                pass
            print '-----------------------------------------------------------------------------------------------------'                    
            EXP_MAP_SRC   = results['%s_expmap'       % k]
            EXP_CUBE_SRC  = results['%s_expcube'      % k]
            src_filePath  = results['%s_src_filePath' % k]
            evt_file      = results['%s_evt_file'     % k]
            count_spectra = results['%s_count_spectra'% k]
            if pha and os.path.exists(count_spectra): # This should be better understood...
                print '...now generating the background file and the pha1 corresponding file. RSP will also be generated...'            
                filesOutput = Make_PHA_RSP_Files(tstart=t0,tstop=t1)
                results['pha_file'] = filesOutput['PHA1']            
                results['rsp_File'] = filesOutput['RSP']
                
                latutils.CreatePHA_BKG_fromLikelihood(results['pha_file'],
                                                      count_spectra.replace('.fits','.bak'),
                                                      lat[0].FilenameFT2,
                                                      EXP_CUBE_SRC,
                                                      EXP_MAP_SRC,
                                                      lat[0]._ResponseFunction,
                                                      src_filePath,
                                                      target='GRB')
                pass
            print '-----------------------------------------------------------------------------------------------------'
            pass
        except:
            print 'Likelihood returned: ',like 
            return_code=0
            pass            
        print '=============================================================================================='            
        pass
    # ##################################################
    #                  RESETTING                       #
    # ##################################################
    print ' LIKELIHOOD DONE. RESETTING THE SELECTION...(%.3f-%.3f) (%s)' %(T00,T01,evt_file0)
    lat[0].setTmin(T00)
    lat[0].setTmax(T01)
    lat[0].evt_file = evt_file0 # THIS HAS NO DIFF RESP    
    print ' -------------------------------------------------- LIKELIHOOD ANALYSIS DONE --------------------------------------------------'
    lat[0].print_parameters()
    return return_code


def MakeGtTsMap(**kwargs):
    ''' Compute the TSMAP using gttsmap
    \t  UPDATE_POS: Update the position if the new localization is within the ERR (0|1)
    \t  LIKE_SUFFIX: Use the previously saved results from MakeLikelihoodAnalysis
    \t  REFITTING: Refit the data with the background model (0|1)
    '''
    print '====> MakeGtTsMap()'
    thisCommand               = commandDefinitions.commands['MakeGtTsMap']
    harvestParameters(thisCommand,kwargs)
    (UPDATE_POS,LIKE_SUFFIX,REFITTING) = thisCommand.getParameters("UPDATE_POS,LIKE_SUFFIX,REFITTING")
    
    # #################################################
    # SAVE THE CURRENT SETUP:
    T00       = grb[0].TStart
    T01       = grb[0].TStop
    evt_file0 = lat[0].evt_file
    # #################################################
    # COMPUTE THE TSMAP IN THE MOST SIGNIFICATIVE INTERVAL:
    # ################################################# 
    try:
        T0           = float(results['%s_T0'       % LIKE_SUFFIX])
        T1           = float(results['%s_T1'       % LIKE_SUFFIX])
        EXP_MAP_SRC  = results['%s_expmap'       % LIKE_SUFFIX]
        EXP_CUBE_SRC = results['%s_expcube'      % LIKE_SUFFIX]
        src_filePath = results['%s_src_filePath' % LIKE_SUFFIX]
        evt_file     = results['%s_evt_file'     % LIKE_SUFFIX]
        this_TS      = float(results['%s_TS_%s' % (LIKE_SUFFIX,'GRB')])
    except:
        print 'NO likelihood available!!!'
        return
    print '--------------------------------------------------'
    print '... ComputeTSMAP on (%.3f,%.3f) with: ' %(T0,T1)
    print 'TS...........: %.f' % this_TS
    print 'exp map......: ', EXP_MAP_SRC
    print 'exp cube.....: ', EXP_CUBE_SRC
    print 'src_filePath.: ', src_filePath
    print 'evt_file.....: ', evt_file
    # SETTING THE LAT TO THE CURRENT CHOICE:
    lat[0].setTmin(T0)
    lat[0].setTmax(T1)
    lat[0].evt_file = evt_file
    tsmap_outFile = lat[0].tsmap_outFile.replace('_LAT_tsmap.fits','_LAT_tsmap_%s.fits' % (LIKE_SUFFIX))
    print '========== TSFILE WILL BE SAVED IN %s:' % tsmap_outFile
    if not os.path.exists(tsmap_outFile):
        print '=============================================================================================='
        print '========== COMPUTING TS MAP USING THE FITTED BACKGROUND MODEL =============='
        like_maxts    = lat[0].pyLike(model=src_filePath,expmap=EXP_MAP_SRC,expcube=EXP_CUBE_SRC)
        src_filePath_bkg = src_filePath.replace('_model_','_model_bkg_')
        like_maxts.deleteSource('GRB')
        print like_maxts.model
        if REFITTING:
            print '==========  REFITTING THE BACKGROUND: '
            like_maxts.fit()
            print like_maxts.model
            pass
        like_maxts.writeXml(src_filePath_bkg)
        
        # I set the binsize such that the error on the location of the GRB are well determined.
        # The map size is 6x6, 5x5 or 4x4 degrees
        # nxpix = 60
        # binsz=0.1
        nxpix = 60
        binsz = lat[0].radius*1.4/nxpix
        
        if this_TS>100:
            binsz=0.05
            nxpix=100
            pass
        if this_TS>200:
            binsz=0.005
            nxpix=200
            pass
        nypix=nxpix
        
        print 'TSMAP binsz=%s, nxpix=%d, nypix=%d' % (binsz,nxpix,nypix)
        lat[0].make_tsmap(expmap=EXP_MAP_SRC,
                          expcube=EXP_CUBE_SRC,
                          srcmdl=src_filePath_bkg,
                          nxpix=nxpix,
                          nypix=nypix,
                          binsz=binsz,
                          outfile=tsmap_outFile)
        pass
    # I change the name of the tsmap, so I save all of them in case of multiple file definitions...
    
    tsmax,ra_tsmax,dec_tsmax, err68, err90, err95, err99 = lat[0].plot_tsmap(filename=tsmap_outFile)
    tsmap_sep = genutils.angsep(results['RA'],results['DEC'],ra_tsmax,dec_tsmax)
    results['TSMAP_SEP']    = tsmap_sep
    results['TSMAP_MAX']    = tsmax
    results['TSMAP_RAMAX']  = ra_tsmax
    results['TSMAP_DECMAX'] = dec_tsmax
    results['TSMAP_ERR68']  = err68
    results['TSMAP_ERR90']  = err90
    results['TSMAP_ERR95']  = err95
    results['TSMAP_ERR99']  = err99
    results['TSMAP_UPDATE'] = 0
    # --------------------------------------------------#
    results['TSMAP_SEP_%s' % LIKE_SUFFIX]    = tsmap_sep
    results['TSMAP_MAX_%s' % LIKE_SUFFIX]    = tsmax
    results['TSMAP_RAMAX_%s' % LIKE_SUFFIX]  = ra_tsmax
    results['TSMAP_DECMAX_%s' % LIKE_SUFFIX] = dec_tsmax
    results['TSMAP_ERR68_%s' % LIKE_SUFFIX]  = err68
    results['TSMAP_ERR90_%s' % LIKE_SUFFIX]  = err90
    results['TSMAP_ERR95_%s' % LIKE_SUFFIX]  = err95
    results['TSMAP_ERR99_%s' % LIKE_SUFFIX]  = err99
    results['TSMAP_UPDATE_%s' % LIKE_SUFFIX] = 0
    # --------------------------------------------------#
    if err68 < results['ERR']:
        if UPDATE_POS:
            UpdatePosition(new_ra=ra_tsmax,new_dec=dec_tsmax)
            results['TSMAP_UPDATE'] = 1
            results['TSMAP_UPDATE_%s' % LIKE_SUFFIX] = 1
            pass
        pass
    # RESET THE DURATION
    print '=== RESETTING THE TIME SELECTION TO: %s, %s, %s ' % (T00,T01,evt_file0)
    lat[0].setTmin(T00)
    lat[0].setTmax(T01)
    lat[0].evt_file = evt_file0
    pass






# def ComputeDuration():    
#    results1=lat[0].make_ComputeDuration()
#    AddResults(results1)
#    pass

#def ComputeKEYDuration():
#    results1=lat[0].make_ComputeKEYDuration()
#    AddResults(results1)
#    pass


#def ComputeBKGEProbabilities(**kwargs):
#    ''' compute the probability using the bkge to estimate the background
#    \t TSTART = GRB.T05
#    \t TSTOP  = GRB.T95
#    \t EMIN   = LAT.EMIN
#    \t EMAX   = LAT.EMAX
#    \t EBINS  = LAT.EBINS
#    \t OVERWRITE = 0
#    '''
#    start=0; stop=0; chatter=1; emin=-1; emax=-1; ebins=-1; overwrite=0; EvaluateMaps=True;
#    for key in kwargs.keys():
#        if   key.upper()=="CHATTER"  : chatter    = kwargs[key]
#        elif key.upper()=="TSTART"   : start      = float(kwargs[key])
#        elif key.upper()=="TSTOP"    : stop       = float(kwargs[key])
#        elif key.upper()=="EMIN"     : emin       = float(kwargs[key])
#        elif key.upper()=="EMAX"     : emax       = float(kwargs[key])
#        elif key.upper()=="EBINS"    : ebins      = int(kwargs[key])
#        elif key.upper()=="OVERWRITE": overwrite  = int(kwargs[key])
#        else: 
#    	    print "Unknown parameter %s was passed..." %key;
#    	    return 
#	pass
#    
#    
#    BKGE_NDET,BKGE_NEXP,BKGE_SIGNIF,BKGE_SIGNIF_WITH_UNCERTAINTY = BKGE_Tools.CalculateBackground(lat[0],
#                                                                                                  start   = start,
#                                                                                                  stop    = stop,
#                                                                                                  chatter = chatter,
#                                                                                                  emin=emin,
#                                                                                                  emax=emax,
#                                                                                                  ebins=ebins,
#                                                                                                  overwrite=overwrite,
#                                                                                                  EvaluateMaps=True)
#    
#    results['BKGE_NDET']                    = BKGE_NDET
#    results['BKGE_NEXP']                    = BKGE_NEXP
#    results['BKGE_SIGNIF']                  = BKGE_SIGNIF
#    results['BKGE_SIGNIF_WITH_UNCERTAINTY'] = BKGE_SIGNIF_WITH_UNCERTAINTY
#    results['BKGE_PROB_TSTART']             = start
#    results['BKGE_PROB_TSTOP']              = stop
#    results['BKGE_PROB_EMIN']               = emin    
#    results['BKGE_PROB_EMAX']               = emax
#    pass

def ComputeBayesProbabilities():
    '''Calculate the probability for each event using the Bayesian approach described in the catalog paper.
    It uses Kernel Probability function for estimating the background'''
    results1 = lat[0].make_ComputeBayesProbabilities()
    AddResults(results1)    
    pass

#def ComputePoissonProbabilities():
#    results1=lat[0].make_ComputePoissonProbabilities()
#    AddResults(results1)
##################################################
def Done(cleanUp=False):
    try:
        grb[0].CloseROOTFile()
    except:
        pass
    
    Print()
    if cleanUp:
        print 'cleaning up...'
        # removing big files from main directory:
        cmd='rm -rf %s/*expmap*.fits' % OutputDir()
        print cmd
        runShellCommand(cmd)
        cmd='rm -rf %s/*ltcube*.fits' % OutputDir()
        print cmd
        runShellCommand(cmd)
        cmd='rm -rf %s/*MKT.fits' % OutputDir()
        print cmd
        runShellCommand(cmd)
        
        cmd='rm -rf %s/*select.fits' % OutputDir()
        print cmd
        runShellCommand(cmd)
        
        cmd='rm -rf %s/lle_events*' % OutputDir()
        print cmd
        runShellCommand(cmd)
        
        cmd='rm -rf %s/*LLEdetdur.root' % OutputDir()
        print cmd
        runShellCommand(cmd)

        # removing big files from sub directories directory:
        cmd='rm -rf %s/Bkg_Estimates/*/*.fits' % OutputDir()
        print cmd
        runShellCommand(cmd)
        
        cmd='rm -rf %s/Bkg_Estimates/*/*.root' % OutputDir()
        print cmd
        runShellCommand(cmd)

        cmd='rm -rf %s/*/*expmap*.fits' % OutputDir()
        print cmd
        runShellCommand(cmd)
        cmd='rm -rf %s/*/*ltcube*.fits' % OutputDir()
        print cmd
        runShellCommand(cmd)
        
        cmd='rm -rf %s/*/*MKT.fits' % OutputDir()
        print cmd
        runShellCommand(cmd)
        
        runShellCommand('ls -l %s' % OutputDir()) 
        pass
    
    now   =  time.localtime()    
    runShellCommand('rm %s/jobTag.txt' % OutputDir())
    print 'Removed jobTag.txt file'
    print ' EXECUTION ENDED %s-%s-%s %s-%s-%s' % (now[0],now[1],now[2],now[3],now[4],now[5])
    print '--------------------------------------------------'
    results={}
    
    try:
        del results
    except:
        pass
    Exit()
    pass

def Exit():
    try:
        _ip.magic('Exit')
    except:
        try:
            sys.exit()
        except:
            pass
        pass
    pass

def EraseOutputDir():
    #try:
    #    Done()
    #except:
    #    pass    
    cmd = 'rm -rf %s ' % OutputDir()
    runShellCommand(cmd);
    pass

def OutputDir():
    return lat[0].out_dir


if __name__=='__main__':
    #print sys.argv
    grbname=''; mode='ql'; debug = True; infile=''
    results                   = ListToDict(sys.argv)
    print '---------------------------------------------------'
    print results
    print '---------------------------------------------------'
    
    for ai,av in enumerate(sys.argv):
        if av=='-go':
            mode='go'
            sys.argv.append('mode=go')
        elif av=='-nox':
            os.environ['ROOTISBATCH']='Y'
            os.environ['DISPLAY']='/dev/null'
            ROOT.gROOT.SetBatch(True)
        elif av=='-exe': infile=sys.argv[ai+1]
        elif av=='-Help' or av=='-H': Help(); sys.exit()
        elif av=='-list' or av=='-l':            
            try:  GRBNames(sys.argv[ai+1])
            except: GRBNames()
            sys.exit()
            pass
        pass    
    if infile!="":
        if os.path.exists(infile): execfile(infile)
        elif os.path.exists(os.environ['GTGRB_DIR']+'/python/app/'+infile+'.py'):
            execfile(os.environ['GTGRB_DIR']+'/python/app/'+infile+'.py')
        else:  print 'File %s does not exists!'  % infile; Help()
    else: cmdlineHelp(); sys.exit()    
    pass
    
