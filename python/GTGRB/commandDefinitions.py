import collections
from commandDefiner import *
import os

authors                       = "N. Omodei (nicola.omodei@stanford.edu), G.Vianello (giacomov@stanford.edu), Vlasios Vasileiou (vlasios.vasileiou@lupm.in2p3.fr), Johan Bregeon (johan.bregeon@pi.infn.it), Frederic Piron (piron@in2p3.fr)"

#This file define all the commands of the public interface of GtGRB

commands                      = collections.OrderedDict()

#Possible IRFS
from GtBurst import IRFS
nativeIRFS=[]
for x in IRFS.IRFS.keys(): nativeIRFS.append(x.upper())
try:     customIRFS           = os.environ['CUSTOM_IRF_NAMES'].split(",")
except:  customIRFS           = []
irfs                          = nativeIRFS+customIRFS
#Unique values
irfs                          = list(set(irfs))
################ Set() #############################
commandName                   = "Set"
version                       = "1.0.0"
shortDescription              = """Set up the analysis for a GRB"""
author                        = authors
commands[commandName]               = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter('GRBNAME','Name of a GRB contained in the database (if you use this, you can leave empty GRBTRIGGERDATE, RA, DEC, ERR, LOCINSTRUMENT, REDSHIFT, GRBT05, GRBT90). Ex. GRB080916C',HIDDEN,partype=STRING)
commands[commandName].addParameter('GRBTRIGGERDATE','Trigger time for the GRB (MET or yyyy-mm-dd hh:mm:ss.ss)\nExample: 301624927.98, or 2010-07-24 00:42:05.98',OPTIONAL,partype=REAL)
commands[commandName].addParameter('RA','R.A. (J2000, deg)',OPTIONAL,partype=REAL)
commands[commandName].addParameter('DEC','Dec. (J2000, deg)',OPTIONAL,partype=REAL)
commands[commandName].addParameter('ERR','Localization error (deg)',OPTIONAL,partype=REAL)
commands[commandName].addParameter('LOCINSTRUMENT','Localizing instrument. Ex. Swift/XRT',OPTIONAL,partype=STRING)
commands[commandName].addParameter('REDSHIFT','Redshift (insert 0 if unknown)',OPTIONAL,0,partype=REAL)
commands[commandName].addParameter('GRBT05','Start time of the GRB respect to the trigger time at low energies (s)',OPTIONAL,partype=REAL)
commands[commandName].addParameter('GRBT90','Approximate duration of the GRB at low energies (s)',OPTIONAL,partype=REAL)
commands[commandName].addParameter('ROI','Radius of the Region of Interest (deg)',MANDATORY,12,partype=REAL)
commands[commandName].addParameter('IRFS','LAT Data Class (IRF)',MANDATORY,'P8_TRANSIENT010E',partype=STRING,possibleValues=irfs)
commands[commandName].addParameter('EMIN','Minimum energy (MeV) for the analysis',MANDATORY,100,partype=REAL)
commands[commandName].addParameter('EMAX','Maximum energy (MeV) for the analysis',MANDATORY,100000,partype=REAL)
commands[commandName].addParameter('ZMAX','Zenith cut angle (deg)',MANDATORY,105,partype=REAL)
commands[commandName].addParameter('FT1','Custom FT1 file for the analysis',HIDDEN,partype=INPUTFILE)
commands[commandName].addParameter('FT2','Custom FT2 file for the analysis',HIDDEN,partype=INPUTFILE)
commands[commandName].addParameter('MODE','Global parameter mode (use "go" for scripts!")',HIDDEN,'query',partype=STRING)
commands[commandName].addParameter('CHATTER','Verbosity level (0-4)',HIDDEN,2,partype=INTEGER)
commands[commandName].addParameter('QUICK','Set to "yes" to avoid gtmktime',HIDDEN,'no',partype=BOOLEAN,possibleValues=['yes','no'])
##################################################################
'''
################ CalculateLATT90 #############################
commandName                   = "CalculateLATT90"
version                       = "1.0.0"
shortDescription              = """Calculate T90 using V.Vasileiou's background estimator."""
author                        = authors
commands[commandName]   = Command(commandName,shortDescription,version,author)

#Define the command parameters
commands[commandName].addParameter("EMIN","Minimum energy for the selection of the events (MeV)",MANDATORY,50,partype=REAL)
commands[commandName].addParameter("EMAX","Maximum energy for the selection of the events (MeV)",MANDATORY,250000,partype=REAL)
commands[commandName].addParameter("WEIGHBYEXPOSURE","Weight the events by the exposure?",OPTIONAL,'no',partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("CROSSGTIS","Cross GTIs?",OPTIONAL,'no',partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("OVERWRITE","Overwrite previous computation?",OPTIONAL,'no',possibleValues=['yes','no'])
commands[commandName].addParameter('CHATTER','Verbosity level (0-4)',HIDDEN,2,partype=INTEGER)

##################################################################

################ CalculateBackground #############################
commandName                   = "CalculateBackground"
version                       = "1.0.0"
shortDescription              = """Calculate The background using V.Vasileiou\'s background estimator.
                                   The background contains both CR and gamma rays (including sources).
                                   Albedo is not included."""
author                        = authors
commands[commandName] = Command(commandName,shortDescription,version,author)

#Define the command parameters
commands[commandName].addParameter("START","Start time of the extracted spectrum (seconds relative to trigger time)",MANDATORY,0,partype=REAL)
commands[commandName].addParameter("STOP","Stop time of the extracted spectrum (seconds relative to trigger time)",MANDATORY,10,partype=REAL)
commands[commandName].addParameter("EMIN","Minimum energy for the selection of the events (MeV)",MANDATORY,100,partype=REAL)
commands[commandName].addParameter("EMAX","Maximum energy for the selection of the events (MeV)",MANDATORY,250000,partype=REAL)
commands[commandName].addParameter("EBINS","Number of energy bins in the final PHA file (logarithmically spaced)",MANDATORY,10,partype=INTEGER)
commands[commandName].addParameter("MAXROIRADIUS","Desired ROI radius in deg (this could be truncated if too close to the Zenith)",OPTIONAL,12,partype=REAL)
commands[commandName].addParameter("OVERWRITE","Overwrite existing files?",OPTIONAL,'no',partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter('CHATTER','Verbosity level (0-4)',HIDDEN,2,partype=INTEGER)

##################################################################

################ Make_BKG_PHA2 #############################
commandName                   = "Make_BKG_PHA2"
version                       = "1.0.0"
shortDescription              = """Calculate a PHA2 containing the background using V.Vasileiou's background estimator.
                                   The background contains both CR and gamma rays (including sources).
                                   Albedo is not included."""
author                        = authors
commands[commandName]     = Command(commandName,shortDescription,version,author)

#Define the command parameters
commands[commandName].addParameter("START","Start time of the extracted spectrum (seconds relative to trigger time)",MANDATORY,partype=REAL)
commands[commandName].addParameter("STOP","Stop time of the extracted spectrum (seconds relative to trigger time)",MANDATORY,partype=REAL)
commands[commandName].addParameter("DT","Time bins duration",MANDATORY,partype=REAL)
commands[commandName].addParameter("EMIN","Minimum energy for the selection of the events (MeV)",MANDATORY,100,partype=REAL)
commands[commandName].addParameter("EMAX","Maximum energy for the selection of the events (MeV)",MANDATORY,250000,partype=REAL)
commands[commandName].addParameter("EBINS","Number of energy bins in the final PHA file (logarithmically spaced)",MANDATORY,10,partype=INTEGER)
commands[commandName].addParameter("FLAT_ROI","Use a flat ROI? Choose 'no' to use a energy-dependent ROI.",MANDATORY,'yes',partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("BINDEF","Bin definition file (from gtgbindef)",HIDDEN,'',partype=INPUTFILE)
commands[commandName].addParameter('CHATTER','Verbosity level (0-4)',HIDDEN,2,partype=INTEGER)
##################################################################

################ MAKE_BKG_PHA #############################
commandName                   = "Make_BKG_PHA"
version                       = "1.0.0"
shortDescription              = """Calculate The background using V.Vasileiou's background estimator.
                                   This produces a PHA I file containing the expected background.
                                   The background contains both CR and gamma rays (including sources).
                                   Albedo is not included."""
author                        = authors
commands[commandName]      = Command(commandName,shortDescription,version,author)

#Define the command parameters
commands[commandName].addParameter("START","Start time of the extracted spectrum (seconds relative to trigger time)",MANDATORY,partype=REAL)
commands[commandName].addParameter("STOP","Stop time of the extracted spectrum (seconds relative to trigger time)",MANDATORY,partype=REAL)
commands[commandName].addParameter("EMIN","Minimum energy for the selection of the events (MeV)",MANDATORY,100,partype=REAL)
commands[commandName].addParameter("EMAX","Maximum energy for the selection of the events (MeV)",MANDATORY,250000,partype=REAL)
commands[commandName].addParameter("EBINS","Number of energy bins in the final PHA file (logarithmically spaced)",MANDATORY,10,partype=INTEGER)
commands[commandName].addParameter("FLAT_ROI","Use a flat ROI? Choose 'no' to use a energy-dependent ROI.",MANDATORY,'yes',partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("BINDEF","Bin definition file (from gtgbindef)",HIDDEN,'',partype=INPUTFILE)
commands[commandName].addParameter("SUFFIX","Suffix for the directory",HIDDEN,'',partype=STRING)
commands[commandName].addParameter('CHATTER','Verbosity level (0-4)',HIDDEN,2,partype=INTEGER)

##################################################################

################ CalculateCRBackground_LC #############################
commandName                   = "CalculateCRBackground_LC"
version                       = "1.0.0"
shortDescription              = """Calculate the background using V.Vasileiou's background estimator.
                                   This compute the bakground as a function of time for several intervals from START to STOP in
                                   time bin of width DT"""
author                        = authors
commands[commandName] = Command(commandName,shortDescription,version,author)

#Define the command parameters
commands[commandName].addParameter("START","Start time  (seconds relative to trigger time)",MANDATORY,partype=REAL)
commands[commandName].addParameter("STOP","Stop time (seconds relative to trigger time)",MANDATORY,partype=REAL)
commands[commandName].addParameter("DT","Time bins duration",MANDATORY,partype=REAL)
commands[commandName].addParameter('CHATTER','Verbosity level (0-4)',HIDDEN,2,partype=INTEGER)


##################################################################

################ Make_CRBKG_Template_Fast #############################
commandName                   = "Make_CRBKG_Template_Fast"
version                       = "1.0.0"
shortDescription              = """Calculate The background using V.Vasileiou's background estimator.
                                   This method provide a fast way to obtain the likelihood template files, but
                                   CalculateCRBackground_LC() must be computed before."""
author                        = authors
commands[commandName] = Command(commandName,shortDescription,version,author)

#Define the command parameters
commands[commandName].addParameter("START","Start time  (seconds relative to trigger time)",MANDATORY,partype=REAL)
commands[commandName].addParameter("STOP","Stop time (seconds relative to trigger time)",MANDATORY,partype=REAL)
commands[commandName].addParameter('CHATTER','Verbosity level (0-4)',HIDDEN,2,partype=INTEGER)

##################################################################
'''

################ MakeLLE_GSFC #############################
commandName                   = "MakeLLE_GSFC"
version                       = "1.0.0"
shortDescription              = """This code calculate LLE data file and detection significance. This is the same code run to produce the LLE file we export at Goddard"""
author                        = authors
commands[commandName]= Command(commandName,shortDescription,version,author)

#Define the command parameters
commands[commandName].addParameter("LLE_VERSION","Version of the LLE file",OPTIONAL,1,partype=INTEGER)
commands[commandName].addParameter("DURATION","Approximate duration of the LLE emission.",OPTIONAL,100.0,partype=REAL)
commands[commandName].addParameter("OFFSET","Offset time with respect the triggertime.",OPTIONAL,0.0,partype=REAL)
commands[commandName].addParameter("DT","Binning of the LLE lighcturve.",OPTIONAL,1.0,partype=REAL)
commands[commandName].addParameter("ZENITHMAX","Maximum Zenith Angle.",OPTIONAL,90,partype=REAL)
commands[commandName].addParameter("THETAMAX","Maximum Theta Angle.",OPTIONAL,90,partype=REAL)
commands[commandName].addParameter("BEFORE","How many seconds of background before the trigger?",OPTIONAL,1000,partype=REAL)
commands[commandName].addParameter("AFTER","How many seconds of background after the trigger?",OPTIONAL,1000,partype=REAL)
commands[commandName].addParameter("NSIGMA","Threshold for detection",OPTIONAL,4.0,partype=REAL)
commands[commandName].addParameter("RADIUS","Radius of the LLE detection (negative numbers are numbers of PSF, positive numbers are degrees",OPTIONAL,-1,partype=REAL)
##################################################################

################ MakeLLELightCurves #############################
commandName                   = "MakeLLELightCurves"
version                       = "1.0.0"
shortDescription              = """This code iterates on various binsize and binshift for LLE lighctcurves, to find
                                   excesses corresponding to the currently set GRB and find the significance of the
                                   detection."""
author                        = authors
commands[commandName]= Command(commandName,shortDescription,version,author)

#Define the command parameters
commands[commandName].addParameter("TASK","Task to perform",MANDATORY,'detection',partype=STRING,possibleValues=['detection','duration'])
commands[commandName].addParameter("SRCTMIN","Start time of the source window. Leave it empty for automatic determination of the window.",OPTIONAL,partype=REAL)
commands[commandName].addParameter("SRCTMAX","Stop time of the source window. Leave it empty for automatic determination of the window.",OPTIONAL,partype=REAL)
commands[commandName].addParameter("LCTMIN","Start time of the light curve. Leave it empty for automatic determination.",OPTIONAL,partype=REAL)
commands[commandName].addParameter("LCTMAX","Stop time of the light curve. Leave it empty for automatic determination.",OPTIONAL,partype=REAL)
commands[commandName].addParameter("LLEDT","""Bin sizes for the light curves. Leave it empty for default choices based on the duration of the GRB.
                                 If DT is a number, it compute the Light curve with one bin width. 
                                 DT can also be a two elements comma-separated list of values (like '1,10') with the minimum and the maximum
                                 binsize. In this case you have also to provide a number of steps (like N=10), and
                                 the algorithm will make N lightcurves with binsize going from the minimum to the maximum.
                                 """,OPTIONAL,partype=LISTOFREALS,private=True)
commands[commandName].addParameter("N","Number of binsize between min(DT) and max(DT). Use this parameter only if you used DT above.",OPTIONAL,partype=REAL,private=True)
commands[commandName].addParameter("LLEDS","""Bin shifts for every light curve. Leave DS empty for the default shifts. If you put DS equal to zero, 
                                 the light curves won't be shifted. If DS is a list the provided shifts will be used. Example: [0,0.1,0.5]
                                 means that for each binsize 3 light curve will be computed, with respectively no shift, 
                                 a 10% shift and a 50% shift of the bins.""",OPTIONAL,partype=LISTOFREALS,private=True)
##################################################################

################ MakeLLEDetectionAndDuration #############################
commandName                   = "MakeLLEDetectionAndDuration"
version                       = "1.0.0"
shortDescription              =  """By Fred Piron (piron@in2p3.fr). 
                                    This code computes the duration and the significance using Fred's code, 
                                    using simulation to estimate the associated errors.
                                    If MakeLLELightCurves() (=Giacomo's LLEdigger code) has been run, the code uses this information
                                 """

author                        = authors
commands[commandName]= Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("USEDIGGERBINNING","Use the bin size found by a previous run of MakeLLELightCurves (if any)",OPTIONAL,'yes',partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("USEDIGGERLAG","Use the bin shift found by a previous run of MakeLLELightCurves (if any)",OPTIONAL,'yes',partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("USEDIGGERSTART","Use the start of the source time window as found by a previous run of MakeLLELightCurves (if any)",OPTIONAL,'yes',partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("USEDIGGERSTOP","Use the stop of the source time window as found by a previous run of MakeLLELightCurves (if any)",OPTIONAL,'yes',partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("ROIMAXRADIUS","Maximum radius for the region of interest (leave empty for default)",OPTIONAL,0,partype=REAL)
##################################################################

################ MakeGBMLightCurves #############################
commandName                   = "MakeGBMLightCurves"
version                       = "1.0.0"
shortDescription              =  """This methods performs the following operation (for each selected GBM detectors):
                                    select GBM events between tmin and tmax, save GBM events in a root tile, make a lightcurve, 
                                    save the Lightcurve in the GRB root file, plot the LC.
                                 """

author                        = authors
commands[commandName]= Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("TSTART","Start time for the light curve",MANDATORY,-30,partype=REAL,private=True)
commands[commandName].addParameter("TSTOP","Stop time for the light curve",MANDATORY,300,partype=REAL,private=True)
commands[commandName].addParameter("DT","Binsize for the light curve",MANDATORY,1.0,partype=REAL,private=True)
commands[commandName].addParameter("NAIANGLE","""All NaI detectors seeing the source with an angle <= NAIANGLE will be included. When using this keyword,
                                                          the output will include ALWAYS the closest BGO detector, 
                                                          and if both BGO detectors have an angle <= 100.0, it will
                                                          include both of them.
                                                       """,OPTIONAL,50,partype=REAL)
commands[commandName].addParameter("DETLIST","""Explicit lists of GBM detectors for which a light curve is desired (Ex. 'n0,n10,n11,b0'). 
                                                         You can use 'all' for use all GBM detectors or 'trig" to use only triggered detectors.
                                                         """,OPTIONAL,partype=STRING)
##################################################################

################ Make_PHA_GBM_Files #############################
commandName                   = "Make_PHA_GBM_Files"
version                       = "1.0.0"
shortDescription              = """From tte file, Make a selection in time and create PHA1 file."""
author                        = authors
commands[commandName]= Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("TSTART","Start time for the spectrum",MANDATORY,-30,partype=REAL,private=True)
commands[commandName].addParameter("TSTOP","Stop time for the spectrum",MANDATORY,300,partype=REAL,private=True)
commands[commandName].addParameter("NAIANGLE","""All NaI detectors seeing the source with an angle <= NAIANGLE will be included. When using this keyword,
                                                          the output will include ALWAYS the closest BGO detector, 
                                                          and if both BGO detectors have an angle <= 100.0, it will
                                                          include both of them.
                                                       """,OPTIONAL,50,partype=REAL)
commands[commandName].addParameter("DETLIST","""Explicit lists of GBM detectors for which a spectrum is desired (Ex. 'n0,n10,n11,b0'). 
                                                         You can use 'all' for using all GBM detectors or 'trig" to use only triggered detectors.
                                                         """,OPTIONAL,partype=STRING)
commands[commandName].addParameter("SUFFIX","""Directory under the OUTDIR under which the spectra will be created. Normally this should be left empty.""",HIDDEN,'',partype=STRING)
##################################################################

################ GetNearestDet #############################
commandName                   = "GetNearestDet"
version                       = "1.0.0"
shortDescription              = """Compute the angle between the source and each of the GBM detectors, 
                                   and return a list ordered from the closest to the farthest."""
author                        = authors
commands[commandName]= Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("NAIANGLE","""All NaI detectors seeing the source with an angle <= NAIANGLE will be included. When using this keyword,
                                                          the output will include ALWAYS the closest BGO detector, 
                                                          and if both BGO detectors have an angle <= BGOANGLE, it will
                                                          include both of them.
                                                       """,OPTIONAL,50,partype=REAL)
commands[commandName].addParameter("BGOANGLE","""The output will include ALWAYS the closest BGO detector, 
                                                          but if both BGO detectors have an angle <= BGOANGLE, it will
                                                          include both of them.
                                                       """,OPTIONAL,100,partype=REAL)
commands[commandName].addParameter("DETLIST","""Restrict the output to an explicit list of GBM detectors (Ex. 'n0,n10,n11,b0'. 
                                                         You can use 'all' for using all GBM detectors or 'trig" to use only triggered detectors.
                                                         """,OPTIONAL,'All',partype=STRING)


##################################################################
################ SelectGBMTimeInterval #############################
commandName                   = "SelectGBMTimeInterval"
version                       = "1.0.0"
shortDescription              = """Select one or more time intervals by choosing interactively on the light curve made with the data of the provided detector."""
author                        = authors
commands[commandName]= Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("BINSIZE",'Bin size for the light curve',MANDATORY,1.0,partype=REAL,private=True)
commands[commandName].addParameter("DETECTOR",'''The GBM detector to use for the light curve (Ex. "n5" or "n11" or "b0").
                                                           Leave it empty to use the NaI detector with the boresight closest to the GRB.
                                                           ''',OPTIONAL,partype=STRING,private=True)
commands[commandName].addParameter("DATAFILE",'The path of an optional TTE-like file to use for the light curve',OPTIONAL,partype=INPUTFILE,private=True)


##################################################################
################ GetGBMFiles #############################
commandName                   = "GetGBMFiles"
version                       = "1.0.0"
shortDescription              = """Download all GBM data for this trigger (cspec,tte,ctime,rsp,rsp2) from the FSSC website."""
author                        = authors
##################################################################
################ GetLLEFiles #############################
commandName                   = "GetLLEFiles"
version                       = "1.0.0"
shortDescription              = """Download all LLE data for this trigger (cspec,lle,rsp,rsp2) from the FSSC website."""
author                        = authors
##################################################################

################ FindTimeBins #############################
commandName                   = "FindTimeBins"
version                       = "1.0.0"
shortDescription              = """Adaptively bin the data for the specified detectors (which must have already a background model obtained with MakeGBMSpectra).
                                   You can bin by constant signal-to-noise, constant significance, constant number of counts, or Bayesian Blocks.
                                   Note that the current implementation of the Bayesian Block technique is unbinned,
                                   and thus usable only for a 
                                   single instrument, it is VERY slow for GBM detectors (which have many events), and assumes 
                                   a constant background."""
author                        = authors
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("TSTART","Start time of the time range to consider for binning",MANDATORY,-30,partype=REAL,private=True)
commands[commandName].addParameter("TSTOP","Stop time of the time range to consider for binning",MANDATORY,300,partype=REAL,private=True)
commands[commandName].addParameter("REBIN_SN","""Desired signal-to-noise OR (if negative) desired prior for the BB algorithm.
                                              """,OPTIONAL,10,partype=REAL)
commands[commandName].addParameter("REBIN_BY_SIGNIFICANCE",'Use significance = (counts-backgr)/sqrt(backgr) instead of signal-to-noise?(ignored for BB)',OPTIONAL,'yes',partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("MINNUMBEROFEVENTS","Minimum number of events in every bin (0 means no constraints)",HIDDEN,5,partype=REAL,private=True)
commands[commandName].addParameter("MAXBINSIZE","Force time bins to be less than a certain size (leave it empty for no constraints)",HIDDEN,1E9,partype=REAL,private=True)
commands[commandName].addParameter("MINEVTENERGY","Minimum energy for an event to be considered (keV)",OPTIONAL,8,partype=REAL,private=True)
commands[commandName].addParameter("MAXEVTENERGY",'''Maximum energy for an event to be considered (keV). 
                                                        Note that overflow channel in GBM data is always excluded.
                                                        ''',OPTIONAL,1e9,partype=REAL,private=True)
commands[commandName].addParameter("DETLIST","""Set to 'all' to use
                                                   all detectors having a background model, or use an explicit list of GBM detectors (Ex. 'n0,n10,n11,b0'). 
                                                   Their background MUST have been already modeled using MakeGBMSpectra. Set this empty here
                                                   and USELLE='yes' if you want to use just LLE data. 
                                                   """,OPTIONAL,"all",partype=STRING)
commands[commandName].addParameter("USELLE",'Include LLE data?',OPTIONAL,'no',private=True,partype=BOOLEAN,possibleValues=['yes','no'])

##################################################################

################ MakeGBMSpectra #############################
commandName                   = "MakeGBMSpectra"
version                       = "1.0.0"
shortDescription              = """Accumulate spectra, background spectra and responses for GBM data needed in order
                                   to perform a spectral analysis with PerformSpectralAnalysis()."""
author                        = authors
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("SP_TSTARTS","Start times of the desired time intervals. Ex. '0.0,5.3,10.2'.",MANDATORY,partype=LISTOFREALS)
commands[commandName].addParameter("SP_TSTOPS","Start times of the desired time intervals. Ex. '5.3,10.2,30.0'.",MANDATORY,partype=LISTOFREALS)
commands[commandName].addParameter("NAIANGLE","""All NaI detectors seeing the source with an angle <= NAIANGLE will be used. Also,
                                                          the closest BGO detector will be used, 
                                                          and if both BGO detectors have an angle <= 100.0, both will be included.
                                                       """,OPTIONAL,50,partype=REAL)
commands[commandName].addParameter("DETLIST","""If you use NAIANGLE above, leave this empty. Otherwise, use this to provide
                                                     an explicit list of GBM detectors (Ex. 'n0,n10,n11,b0'). 
                                                     Use 'auto' to use all the detectors which already
                                                     have a background model (from a previous call to MakeGBMSpectra).
                                                   """,OPTIONAL,partype=STRING)


##################################################################

################ MakeLATSpectra #############################
commandName                   = "MakeLATSpectra"
version                       = "1.0.0"
shortDescription              = """Accumulate spectra, background spectra and responses for LAT data needed in order
                                   to perform a spectral analysis with PerformSpectralAnalysis()."""
author                        = authors
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("SP_TSTARTS","Start times of the desired time intervals. Ex. '0.0,5.3,10.2'.",MANDATORY,partype=LISTOFREALS)
commands[commandName].addParameter("SP_TSTOPS","Start times of the desired time intervals. Ex. '5.3,10.2,30.0'.",MANDATORY,partype=LISTOFREALS)
commands[commandName].addParameter("EBINS","""Number of energy bins
                                                       """,OPTIONAL,10,partype=INTEGER)
commands[commandName].addParameter("FLAT_ROI","""Use a flat ROI? If 'no', then a energy-dependent ROI will be used.
                                                       """,OPTIONAL,'no',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("BKGE","""Produce also background spectra using the Background Estimator?
                                                       """,OPTIONAL,'yes',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("RSPGEN","""Produce also a response file?
                                                       """,OPTIONAL,'yes',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("SUFFIX","""Suffix for the directory name""",HIDDEN,partype=STRING)

##################################################################
################ MakeLLESpectra #############################
commandName                   = "MakeLLESpectra"
version                       = "1.0.0"
shortDescription              = """Accumulate spectra, background spectra and responses for LAT/LLE data needed in order
                                   to perform a spectral analysis with PerformSpectralAnalysis()."""
author                        = authors
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("SP_TSTARTS","Start times of the desired time intervals. Ex. '0.0,5.3,10.2'.",MANDATORY,partype=LISTOFREALS)
commands[commandName].addParameter("SP_TSTOPS","Start times of the desired time intervals. Ex. '5.3,10.2,30.0'.",MANDATORY,partype=LISTOFREALS)
##################################################################
################ PerformSpectralAnalysis #############################
commandName                   = "PerformSpectralAnalysis"
version                       = "1.0.0"
shortDescription              = """Accumulate spectra, background spectra and responses for LAT/LLE data needed in order
                                   to perform a spectral analysis with PerformSpectralAnalysis()."""
author                        = authors
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("SP_TSTARTS","Start times of the desired time intervals. Ex. '0.0,5.3,10.2'.",MANDATORY,partype=LISTOFREALS)
commands[commandName].addParameter("SP_TSTOPS","Start times of the desired time intervals. Ex. '5.3,10.2,30.0'.",MANDATORY,partype=LISTOFREALS)
##################################################################

################ PerformSpectralAnalysis #############################
commandName                   = "PerformSpectralAnalysis"
version                       = "1.0.0"
shortDescription              = """Accumulate spectra, background spectra and responses for LAT/LLE data needed in order
                                   to perform a spectral analysis with PerformSpectralAnalysis()."""
author                        = authors
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("SP_TSTARTS","Start times of the desired time intervals. Ex. '0.0,5.3,10.2'.",MANDATORY,partype=LISTOFREALS)
commands[commandName].addParameter("SP_TSTOPS","Start times of the desired time intervals. Ex. '5.3,10.2,30.0'.",MANDATORY,partype=LISTOFREALS)
##################################################################

################ PerformSpectralAnalysis #############################
commandName                   = "PerformSpectralAnalysis"
version                       = "1.0.0"
shortDescription              = """Perform a spectral analysis using Autofit."""
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("EFFECTIVEAREACORRECTION","Use the effective area correction?",OPTIONAL,'no',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("PERFORMFIT","Perform the fit? If 'no', only the Xspec scripts will be written.",HIDDEN,'yes',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("FLUXENERGYBANDS","""Energy bands in which you want to compute fluxes/fluences (in keV). 
                                                                      Ex.: '10-1000,1000-1E5,1E5-1E7' """,OPTIONAL,"10-1E7",partype=STRING)
commands[commandName].addParameter("COMPONENTBYCOMPONENT","""Compute fluxes/fluences/Eiso/Liso component by component?
                                                                 If 'yes' then for all multi-component models (like Band+Power law) 
                                                                 fluxes/fluences/Eiso/Liso will be computed also component by component
                                                                 (in that case, separately for Band and for the Power law). Using this option
                                                                 will slow down the process quite a bit.""",OPTIONAL,'no',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
                                                                      

##################################################################

################ PlotAngularSeparation #############################
commandName                   = "PlotAngularSeparation"
version                       = "1.0.0"
shortDescription              = """Plot the angular distance between the Zenith and the GRB, and the LAT boresight and the GRB,
                                   as a function of time."""
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("BEFORE","backward compatibility",HIDDEN,partype=REAL)
commands[commandName].addParameter("AFTER","backward compatibility",HIDDEN,partype=REAL)
commands[commandName].addParameter("NAV_START","Start time for the plot (in seconds from the trigger)",OPTIONAL,-300,partype=REAL)
commands[commandName].addParameter("NAV_STOP","Stop time for the plot (in seconds from the trigger)",OPTIONAL,1000,partype=REAL)                                                                     

##################################################################

################ MakeSelectEnergyDependentROI #############################
commandName                   = "MakeSelectEnergyDependentROI"
version                       = "1.0.0"
shortDescription              = """Use the PSF(E) to select the event compatible with the position of the burst, from TSTART and TSTOP.
                                   This saves also the events into a root file, plot the LC and the skymap."""
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("TSTART","Start time for the selection.",MANDATORY,partype=REAL)
commands[commandName].addParameter("TSTOP","Stop time for the selection.",MANDATORY,partype=REAL)
commands[commandName].addParameter("SUFFIX","Suffix for the directory",HIDDEN,'_ROI_E',partype=STRING)
commands[commandName].addParameter("RSPGEN","""Produce also a response file?
                                                       """,OPTIONAL,'no',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("PLOT","""Plot sky map and LC?""",OPTIONAL,'yes',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("DT","""Bin size for the light curve in seconds (use this only if PLOT='yes')""",OPTIONAL,1.0,partype=REAL)
commands[commandName].addParameter("BINSZ","""Size of the sky pixel for the sky map in deg (use this only if PLOT='yes')""",OPTIONAL,0.1,partype=REAL)
commands[commandName].addParameter("USEINCOMPOSITE","""Use LAT events in composite light curve?""",HIDDEN,'yes',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
##################################################################

################ MakeLATLightCurve #############################
commandName                   = "MakeLATLightCurve"
version                       = "1.0.0"
shortDescription              = """Make a light curve with LAT events"""
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("DT","""Bin size for the light curve.""",MANDATORY,1.0,partype=REAL)
##################################################################

################ MakeSkyMap #############################
commandName                   = "MakeSkyMap"
version                       = "1.0.0"
shortDescription              = """Make a light curve with LAT events"""
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("BINSZ","""Size of the sky pixel for the sky map in deg""",MANDATORY,0.1,partype=REAL)
##################################################################

################ MakeSelect #############################
commandName                   = "MakeSelect"
version                       = "1.0.0"
shortDescription              = """Select the event inside the ROI, from TSTART and TSTOP.
                                   This saves also the events into a root file, plot the LC and the skymap."""
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("TSTART","Start time for the selection.",MANDATORY,partype=REAL)
commands[commandName].addParameter("TSTOP","Stop time for the selection.",MANDATORY,partype=REAL)
commands[commandName].addParameter("SUFFIX","Suffix for the directory",HIDDEN,'_ROI',partype=STRING)
commands[commandName].addParameter("RSPGEN","""Produce also a response file?
                                                       """,OPTIONAL,'no',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("PLOT","""Plot sky map and LC?""",OPTIONAL,'yes',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("DT","""Bin size for the light curve in seconds (use this only if PLOT='yes')""",OPTIONAL,1.0,partype=REAL)
commands[commandName].addParameter("BINSZ","""Size of the sky pixel for the sky map in deg (use this only if PLOT='yes')""",OPTIONAL,0.1,partype=REAL)
commands[commandName].addParameter("USEINCOMPOSITE","""Use LAT events in composite light curve?""",HIDDEN,'yes',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
##################################################################

################ MakeSelectFrontBack #############################
commandName                   = "MakeSelectFrontBack"
version                       = "1.0.0"
shortDescription              = """Select the event inside the ROI, from TSTART and TSTOP, for front- and back-converting events separately.
                                   This saves also the events into a root file, plot the LCs and the skymaps."""
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("TSTART","Start time for the selection.",MANDATORY,partype=REAL)
commands[commandName].addParameter("TSTOP","Stop time for the selection.",MANDATORY,partype=REAL)
commands[commandName].addParameter("RSPGEN","""Produce also a response file?
                                                       """,OPTIONAL,'no',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("PLOT","""Plot sky map and LC?""",OPTIONAL,'yes',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("DT","""Bin size for the light curve in seconds (use this only if PLOT='yes')""",OPTIONAL,1.0,partype=REAL)
commands[commandName].addParameter("BINSZ","""Size of the sky pixel for the sky map in deg (use this only if PLOT='yes')""",OPTIONAL,0.1,partype=REAL)
##################################################################

################ MakeSelectEnergyDependentROIFrontBack #############################
commandName                   = "MakeSelectEnergyDependentROIFrontBack"
version                       = "1.0.0"
shortDescription              = """Use the PSF(E) to select the event compatible with the position of the burst, from TSTART and TSTOP.
                                   Handle front- and back-converting events separately.
                                   This saves also the events into a root file, plot the LC and the skymap."""
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("TSTART","Start time for the selection.",MANDATORY,partype=REAL)
commands[commandName].addParameter("TSTOP","Stop time for the selection.",MANDATORY,partype=REAL)
commands[commandName].addParameter("RSPGEN","""Produce also a response file?
                                                       """,OPTIONAL,'no',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("PLOT","""Plot sky map and LC?""",OPTIONAL,'yes',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("DT","""Bin size for the light curve in seconds (use this only if PLOT='yes')""",OPTIONAL,1.0,partype=REAL)
commands[commandName].addParameter("BINSZ","""Size of the sky pixel for the sky map in deg (use this only if PLOT='yes')""",OPTIONAL,0.1,partype=REAL)
##################################################################

################ MakeLikelihoodAnalysis #############################
commandName                   = "MakeLikelihoodAnalysis"
version                       = "1.0.0"
shortDescription              = """Perform a Likelihood analysis between TSTART and TSTOP, using the provided likelihood model."""
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("TSTART","Start time for the selection.",MANDATORY,partype=REAL)
commands[commandName].addParameter("TSTOP","Stop time for the selection.",MANDATORY,partype=REAL)
commands[commandName].addParameter("TSMIN","""Minimum TS for considering the GRB detected 
                                            (if TS < TSMIN upper limits will be computed instead of fluxes)""",OPTIONAL,20,partype=REAL)
commands[commandName].addParameter("FEMIN","""Lower bound for the energy range for flux (or upper limit) computation (MeV)""",OPTIONAL,100,partype=REAL)
commands[commandName].addParameter("FEMAX","""Higher bound for the energy range for flux (or upper limit) computation (MeV)""",OPTIONAL,100000,partype=REAL)
commands[commandName].addParameter("PROB","""Run gtsrcprob to compute photon by photon the probability that it belongs to the GRB 
                                             (according to the best fit likelihood model)""",OPTIONAL,'no',partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("SUFFIX","Suffix to append to all files (if you use twice the same prefix, old files will be overwritten)",OPTIONAL,'LIKE_MY',partype=STRING)
commands[commandName].addParameter("PHA","""Produce also a PHA file?
                                                       """,HIDDEN,'no',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("EXTENDED","""Perform a time-resolved likelihood analysis with the 
                                                 bin scheme chosen in LIKE_TIMEBINS below?
                                                 """,OPTIONAL,'no',partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("LIKE_TIMEBINS","""Binning scheme for the time-resolved likelihood analysis: 
                                                      LOG = logarithmically spaced bins, LIN = linearly spaced bins, 
                                                      CONSTANT_TS = bin with constant TS, BB = Bayesian Blocks,
                                                      USER_PROVIDED = provide manually the time bins using USER_TIME_BINS """,
                                   OPTIONAL,'LOG',partype=STRING,possibleValues=['LOG','LIN','CONSTANT_TS','BB','USER_PROVIDED'])
commands[commandName].addParameter("NLIKEBINS","""Number of bins.
To be used if you specified LOG (= logarithmically spaced bins) or LIN (= linearly spaced bins), 
for the parameter LIKE_TIMEBINS """,
                                   OPTIONAL,5,partype=INTEGER)

commands[commandName].addParameter("EXTENDED_TSTART","Start time for the time extended emission.",OPTIONAL,0,partype=REAL)
commands[commandName].addParameter("EXTENDED_TSTOP","Stop time for the time extended emission.",OPTIONAL,10000,partype=REAL)


commands[commandName].addParameter("TSMIN_EXT","""The target TS for the CONSTANT_TS binning scheme.""",OPTIONAL,18,partype=REAL)
commands[commandName].addParameter("BB_PRIOR","""The prior for the BB binning scheme.""",OPTIONAL,3,partype=REAL)
commands[commandName].addParameter("USER_TIME_BINS","""The time bins used for the USER_PROVIDED binning scheme.
                                                       Comma separated list of extremes. Ex. '0,10,30,40' will
                                                       produce 3 likelihood analyses in 0-10,10-30,30-40 time bins'""",OPTIONAL,partype=LISTOFREALS)

##################################################################
################ CustomizeSpectralPlots #############################
commandName                   = "CustomizeSpectralPlots"
version                       = "1.0.0"
shortDescription              = """After running PerformSpectralAnalysis(), you can use this to customize the plots of 
                                   counts spectra and nuFnu spectra"""
commands[commandName]      = Command(commandName,shortDescription,version,author)

commands[commandName].addParameter("INTERACTIVE","""Stop to allow user customization""",HIDDEN,'yes',private=True,partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("NUFNUUNITS","""nuFnu type: choose 'keV' for (keV^2 x dn/dE), or 'erg' for (erg^2 x exposure x dn/dE)""",OPTIONAL,'keV',partype=STRING,possibleValues=['keV','erg'])
##################################################################

################ MakeGtFindSrc #############################
commandName                   = "MakeGtFindSrc"
version                       = "1.0.0"
shortDescription              = """After running a likelihood analysis, you can use this command to 
                                   optimize the source position"""
commands[commandName]      = Command(commandName,shortDescription,version,author)
commands[commandName].addParameter("UPDATE_POS","""Update the position with the results of gtfindsrc?""",OPTIONAL,'no',partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("LIKE_SUFFIX","""Suffix of the likelihood analysis results to be used""",OPTIONAL,'LIKE_MY',partype=STRING)
##################################################################

################ MakeGtTsMap #############################
commandName                   = "MakeGtTsMap"
version                       = "1.0.0"
shortDescription              = """After running a likelihood analysis, you can use this command to 
                                   optimize the source position using gttsmap"""
commands[commandName]      = Command(commandName,shortDescription,version,author)
commands[commandName].addParameter("UPDATE_POS","""Update the position with the results of gttsmap?""",OPTIONAL,'no',partype=BOOLEAN,possibleValues=['yes','no'])
commands[commandName].addParameter("LIKE_SUFFIX","""Suffix of the likelihood analysis results to be used""",OPTIONAL,'LIKE_MY',partype=STRING)
commands[commandName].addParameter("REFITTING","""refits the background after removing the point source""",OPTIONAL,'no',possibleValues=['yes','no'])

##################################################################
