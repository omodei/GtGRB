pfiles  = os.environ['PFILES']
cleanUp = False

try:
    if os.environ['PIPELINE']=='YES':   cleanUp=True
    pass
except:
    pass

# Sets all the parameters, and starts from sratch

Set(**ListToDict(sys.argv))
if mode=='go':
    EraseOutputDir()
    Set(**ListToDict(sys.argv))
    pass

GRBtheta = lat[0].getGRBTheta()
grbname  = grb[0].Name

print '--------------------------------------------------'
now=time.localtime()
print ' GTGRB EXECUTION STARTED %s-%s-%s %s-%s-%s' % (now[0],now[1],now[2],now[3],now[4],now[5])
print ' GRBNAME    = ',grbname
print ' PFILES     = ',pfiles
print ' PYTHONPATH = ',os.environ['PYTHONPATH']
print ' INDIR      = ',os.environ['INDIR']
print ' OUTDIR     = ',os.environ['OUTDIR']
try:
    print ' ROOTISBATCH= ',os.environ['ROOTISBATCH']
except:
    pass

chatter = 2

# -------------------------------------------------- #
# PLOT ANGULAR SEPARATION
PlotAngularSeparation(mode=mode)
Print()
try: WEIGHBYEXPOSURE    = bool(results['WEIGHBYEXPOSURE'])
except: WEIGHBYEXPOSURE = True


# -------------------------------------------------- #
# CALCULATE THE GRB DURATION USING THE BKGE.
Prompt(['CALCULATELATT90'],mode)
if results['CALCULATELATT90'].upper()=='Y':
    #try:            
    CalculateLATT90(emin=lat[0].Emin, emax=lat[0].Emax, chatter=chatter, WEIGHBYEXPOSURE = WEIGHBYEXPOSURE, CROSSGTIS=True)
    Print()
    #except:
    #    print '#--------------------------------------------------#'
    #    print '#   Not possible to compute duration using BKGE    #'
    #    print '#--------------------------------------------------#'
    #    pass
    pass

# -------------------------------------------------- #
# SELECT EVENTS IN DIFFERENT TIME DOMAINS,
# COMPUTE PHA1 and RSP FILES
# -------------------------------------------------- #
t0=results['GBMT05']
t1=results['GRBT05']
t2=results['GBMT95']
t3=results['GRBT95']

Prompt(['MAKE_RSPGEN'],mode)
rspgen        = results['MAKE_RSPGEN']

pha_gbm_files = False

if t1>t0: # PRE
    tstart = t0
    tstop  = t1
    nevents = MakeSelectEnergyDependentROI(mode=mode,tstart=tstart,tstop=tstop,suffix='_PRE',rspgen=rspgen,plot=False)
    if pha_gbm_files: Make_PHA_GBM_Files(tstart=tstart,tstop=tstop)        
    # THIS IS FOR THE LAT:
    if rspgen: Make_BKG_PHA(start=tstart,stop=tstop)
    pass

if t2>t1: # JOINT
    tstart = t1
    tstop  = t2
    nevents = MakeSelectEnergyDependentROI(mode=mode,tstart=tstart,tstop=tstop,suffix='_JOINT',rspgen=rspgen,plot=False)
    if pha_gbm_files: Make_PHA_GBM_Files(tstart=tstart,tstop=tstop)
    # THIS IS FOR THE LAT:
    if rspgen: Make_BKG_PHA(start=tstart,stop=tstop)
    pass

if t3>t2: # LATEXT
    tstart = t2
    tstop  = t3
    nevents = MakeSelectEnergyDependentROI(mode=mode,tstart=tstart,tstop=tstop,suffix='_EXT',rspgen=rspgen,plot=False)
    # THIS IS FOR THE LAT:
    if rspgen: Make_BKG_PHA(start=tstart,stop=tstop)
    pass

if t2>t0 and t1>t0: # GBM 
    tstart = t0
    tstop  = t2
    nevents = MakeSelectEnergyDependentROI(mode=mode,tstart=tstart,tstop=tstop,suffix='_GBM',rspgen=rspgen,plot=False)
    if pha_gbm_files: Make_PHA_GBM_Files(tstart=tstart,tstop=tstop)
    # THIS IS FOR THE LAT:
    if rspgen: Make_BKG_PHA(start=tstart,stop=tstop)
    pass
if t3>t1: #BKGE
    tstart = t1
    tstop  = t3
    nevents = MakeSelectEnergyDependentROI(mode=mode,tstart=tstart,tstop=tstop,suffix='_BKGE',rspgen=rspgen,plot=False)
    # THIS IS FOR THE LAT:
    if rspgen: Make_BKG_PHA(start=tstart,stop=tstop)
    pass
pass

# SELECT THE EVENTS FROM TSTART AND TSTOP AS SPECIFIED IN THE PAR FILE,
# CALCULATE MakeGtFindSrc AND CALCULATE PROBABILITY OF BEING GRB EVENT
# A) PROBABILITIES ARE FROM TSTART - max(TMIN,TMAX)
TMIN = -20.0
TMAX = 1.0e4
if MakeSelect(mode=mode,tstart=TMIN,tstop=TMAX,plot=False)>0: ComputeBayesProbabilities()

# B) Find Position is from offset to duration:
if MakeSelect(mode=mode,tstart=results['GRBT05'],tstop=results['GRBT95'],plot=False)>0: MakeGtFindSrc(mode=mode)

Prompt(['SEPARATE_FB'],mode)
if results['SEPARATE_FB'].upper()=='Y':        
    MakeSelectFrontBack(mode=mode)
    MakeSelectEnergyDependentROIFrontBack(mode=mode)
    pass

# C) This is from TSTART and TSTOP, here we save the output (in the _ROI_E directory)
#try:
MakeSelectEnergyDependentROI(mode=mode)
#except:
#    print '--- An error occourred: MakeSelectEnergyDependentROI --- '
#    pass
# C) This resets the selected events to TSTART and TSTOP and we save the output (in the _ROI directory)
MakeSelect(mode=mode)
#Make_BKG_PHA(flat_roi=1)
Print()

##################################################
# MAKE LLE ANALYSIS
##################################################

Prompt(['MAKELLE'],mode)
if results['MAKELLE'].upper()=='Y':
    GetLLE()                                             # This will get the data.
    print '*** Executing MakeLLELightCurves...'
    #if GRBtheta<89.9:
    try:
        MakeLLELightCurves(**(ListToDict(sys.argv))) # Jack's code
        try:
            print '********* LLE_DetMaxSign = %.2f ' % results['LLE_DetMaxSign']
            if float(results['LLE_DetMaxSign']) > 4.0:          # Pre Trial Probability in sigma
                tmpdict={'task':'duration'}
                tmpdict.update(ListToDict(sys.argv))        
                MakeLLELightCurves(**(tmpdict))          # Jack's code
                pass    
            pass
        except:
            print ' ****** Failed to compute MakeLLELightCurves - Duration'
            pass
        pass
    except:
        print ' ****** Failed to compute MakeLLELightCurves - Detection'
        pass
    # pass
    # else:
    # print ' ****** GRB theta is %.1f (>89.9) the LLE code will fail. ***' % GRBtheta
    # pass    
    MakeLLEDetectionAndDuration() # Fred's Code
    Print()
    pass
# #################################################
# THIS RETRIEVE THE GBM FILES and make the GBM LIGHTCURVES
# #################################################
GetGBMFiles()
try:
    MakeGBMLightCurves(mode=mode)
except:
    print '#--------------------------------------------------#'
    print '#       skipping GBM light curve generation        #'
    print '#       Something went wrong                       #'
    print '#--------------------------------------------------#'
    print '* Listing:                                         *'
    print '%s/GBM/%s'  % (os.environ['INDIR'],grbs.GetFullName(grbname))
    os.system('ls -l %s/GBM/%s'  % (os.environ['INDIR'],grbs.GetFullName(grbname)))            
    print '*--------------------------------------------------*'        
    pass

MakeCompositeLightCurve()

Print()
# ##################################################
# LIKELIHOOD ANALYSIS
# ##################################################
Prompt(['like_model'], mode)
if 'PREFIT' in results['like_model']:                
    MakeComputePreburstBackground(mode)
    pass

MakeLikelihoodAnalysis(mode=mode)

Done(cleanUp)        
pass
