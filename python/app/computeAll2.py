##################################################
# 0 SETUP FILES AND PARAMETERS
##################################################
pfiles  = os.environ['PFILES']
cleanUp = False
mydict=ListToDict(sys.argv)

# Sets all the parameters, and starts from sratch

Set(**mydict)
if mode=='go':
    EraseOutputDir()
    Set(**mydict)
    pass

try:    timeShift = float(os.environ['TIMESHIFT']) #=-2.0 * 5733.0672 = 11466.1344)
except: timeShift=0

if timeShift!=0:
    dirToRemove = '%s/%s' % (os.environ['OUTDIR'],grb[0].Name)
    NewtriggerTime = grb[0].Ttrigger+timeShift
    SetVar('GRBTRIGGERDATE',NewtriggerTime)
    SetGRB()
    GRBtheta = lat[0].getGRBTheta()
    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
    print ' WARNING!!!! The trigger time has changed            '
    print ' New Theta of the bursts: %.2f ' % GRBtheta
    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
    print 'removing: %s ' % dirToRemove
    os.system('rm -rf %s' % dirToRemove)
    pass
else:
    if mode=='go':
        EraseOutputDir()
        Set(**mydict)
        pass
    pass

GRBtheta = lat[0].getGRBTheta()
grbname  = grb[0].Name

print ' GRBNAME: %s, THETA: %.1f s, Mode: %s' % (grbname, GRBtheta, mode)
print '***************************************************'

ReadResults()

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
# 1) PLOT ANGULAR SEPARATION
# -------------------------------------------------- #

Prompt(['PLOTANGULARSEPARATION'],mode)
if bool(results['PLOTANGULARSEPARATION']):
    print '*********************************************************************************************************************************************'
    PlotAngularSeparation(mode=mode)
    Print()
    pass

# -------------------------------------------------- #
# 2) CALCULATE THE GRB DURATION USING THE BKGE.
# -------------------------------------------------- #

Prompt(['CALCULATELATT90'],mode)
if bool(results['CALCULATELATT90']):
    print '*********************************************************************************************************************************************'
    Prompt(['WEIGHBYEXPOSURE'],mode)
    WEIGHBYEXPOSURE = bool(results['WEIGHBYEXPOSURE'])
    
    Prompt(['CROSSGTIS'],mode)
    CROSSGTIS       = bool(results['CROSSGTIS'])

    if WEIGHBYEXPOSURE: CROSSGTIS=False
    
    CalculateLATT90(emin=lat[0].Emin, emax=lat[0].Emax, chatter=chatter, WEIGHBYEXPOSURE = WEIGHBYEXPOSURE, CROSSGTIS=CROSSGTIS)
    Print()
    pass

# --------------------------------------------------
GBMT05 = results['GBMT05']
GRBT05 = results['GRBT05']
GBMT95 = results['GBMT95']
GRBT95 = results['GRBT95']

bins={'_BKGE' :(GRBT05,GRBT95),
      '_GBM'  :(GBMT05,GBMT95),
      '_PRE'  :(min(GBMT05,GRBT05),max(GBMT05,GRBT05)),
      '_JOINT':(max(GBMT05,GRBT05),min(GBMT95,GRBT95)),
      '_EXT'  :(min(GBMT95,GRBT95),max(GBMT95,GRBT95))}

pha_start_bins = [bins['_PRE'][0],bins['_GBM'][0],bins['_JOINT'][0],bins['_BKGE'][0],bins['_EXT'][0]]
pha_stop_bins  = [bins['_PRE'][1],bins['_GBM'][1],bins['_JOINT'][1],bins['_BKGE'][1],bins['_EXT'][1]]

if 'TSTART' in mydict.keys():
    GRBT05 = mydict['TSTART']
    GBMT05 = GRBT05
    bins={}
    pass

if 'TSTOP' in mydict.keys():
    GRBT95 = mydict['TSTOP']
    GBMT95 = GRBT95
    bins={}
    pass

if 'PHAstart' in mydict.keys():  pha_start_bins = results['PHAstart']
if 'PHAstop' in mydict.keys():   pha_stop_bins  = results['PHAstop']

# -------------------------------------------------- #
# 3) MAKE SELECT:
Prompt(['MAKESELECT'],mode)
if bool(results['MAKESELECT']):
    print '*********************************************************************************************************************************************'
    # -------------------------------------------------- #
    # SELECT EVENTS IN DIFFERENT TIME DOMAINS,
    # COMPUTE PHA1 and RSP FILES
    # -------------------------------------------------- #
    
    Prompt(['MAKE_RSPGEN'],mode)
    rspgen              = int(results['MAKE_RSPGEN'])
    
    Prompt(['MAKE_ENERGYDEPENDENTROI'],mode)
    EnergyDependentRoi  = int(results['MAKE_ENERGYDEPENDENTROI'])
    flat_roi = not bool(EnergyDependentRoi)
    
    for suff in bins.keys():
        t0  = bins[suff][0]
        t1  = bins[suff][1]
        if t0 < t1 :
            # --- Energy Dependent ROI:
            if EnergyDependentRoi: MakeSelectEnergyDependentROI(mode=mode,tstart=t0,tstop=t1,suffix='%s_ROIE' % suff,rspgen=rspgen, plot=False)
            # --- Simple ROI:
            MakeSelect(mode=mode,tstart=t0,tstop=t1,suffix=suff, rspgen=rspgen, plot=False)
            pass
        else: print '==== %s: tstart (%.2f) >= tstop (%.2f) ====' % (suff,t0,t1)
        pass
    
    
    # SELECT THE EVENTS FROM TSTART AND TSTOP AS SPECIFIED IN THE PAR FILE,
    # CALCULATE MakeGtFindSrc AND CALCULATE PROBABILITY OF BEING GRB EVENT
    # A) PROBABILITIES ARE FROM TSTART - max(TMIN,TMAX)
    TMIN = -20.0
    TMAX = 1.0e3
    if MakeSelect(mode=mode,tstart=TMIN,tstop=TMAX,plot=False)>0: ComputeBayesProbabilities()
    
    # B) Find Position is from offset to duration:
    if MakeSelect(mode=mode,tstart=results['GRBT05'],tstop=results['GRBT95'],plot=False)>0: MakeGtFindSrc(mode=mode)
    elif MakeSelect(mode=mode,tstart=results['GRBT95'],tstop=1000,plot=False)>0: MakeGtFindSrc(mode=mode)
    
    Prompt(['SEPARATE_FB'],mode)
    if bool(results['SEPARATE_FB']):
        MakeSelectFrontBack(mode=mode)
        if EnergyDependentRoi: MakeSelectEnergyDependentROIFrontBack(mode=mode)
        pass
    
    # C) This is from TSTART and TSTOP, here we save the output (in the _ROI_E directory)
    if EnergyDependentRoi: MakeSelectEnergyDependentROI(mode=mode)
    # C) This resets the selected events to TSTART and TSTOP and we save the output (in the _ROI directory)
    MakeSelect(mode=mode)
    # Make_BKG_PHA(flat_roi=1)
    Print()
    pass

Prompt(['MAKE_GBM_XSPECTUM'],mode)
MAKE_GBM_XSPECTUM       = int(results['MAKE_GBM_XSPECTUM'])
Prompt(['MAKE_LAT_XSPECTRUM'],mode)
MAKE_LAT_XSPECTRUM      = int(results['MAKE_LAT_XSPECTRUM'])

try:    bkge        = results['BKGE']
except: bkge        = 0

if MAKE_GBM_XSPECTUM:
    GetGBMFiles()
    MakeGBMSpectra(tstart=pha_start_bins,tstop=pha_stop_bins,mode=mode)
    pass

if MAKE_LAT_XSPECTRUM:
    Prompt(['MAKE_BKGE_XSPECTRUM'],mode)
    MAKE_BKGE_XSPECTRUM      = int(results['MAKE_BKGE_XSPECTRUM'])
    MakeLATSpectra(tstart=pha_start_bins,tstop=pha_stop_bins,flat_roi=flat_roi,bkge=MAKE_BKGE_XSPECTRUM)
    
##################################################
# MAKE LLE ANALYSIS
##################################################

Prompt(['MAKELLE'],mode)
if bool(results['MAKELLE']):
    GetLLE()                                             # This will get the data.
    print '*** Executing MakeLLELightCurves...'
    #if GRBtheta<89.9:
    try:
        MakeLLELightCurves(**(mydict)) # Jack's code
        try:
            print '********* LLE_DetMaxSign = %.2f ' % results['LLE_DetMaxSign']
            if float(results['LLE_DetMaxSign']) > 4.0:          # Pre Trial Probability in sigma
                tmpdict={'task':'duration'}
                tmpdict.update(mydict)
                MakeLLELightCurves(**tmpdict)          # Jack's code
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

# ##################################################
# LIKELIHOOD ANALYSIS
# ##################################################
Prompt(['MAKE_LIKE'],mode)
if bool(results['MAKE_LIKE']):
    try: tstart      = results['LIKETSTART']
    except:  tstart  = 0
    try: tstop       = results['LIKETSTOP']
    except: tstop    = 0
    try: extended    = results['EXTENDED']
    except: extended = 1
    try: makepha     = results['LIKEPHA']
    except: makepha  = 0
    
    try: tsmap       = results['TSMAP']
    except: tsmap   = 1
    # ------------------------------------------------------ #
    PlotAngularSeparation(mode=mode)
    MakeSelect(mode=mode)        
    MakeLikelihoodAnalysis(mode=mode,
                           tstart=tstart,
                           tstop=tstop,
                           extended=extended,
                           tsmap=1,
                           pha=makepha)    
    Print()
    #Prompt(['UPDATE_POS'],mode='go')
    #UPDATE_POS = results['UPDATE_POS']
    #results['TSMAP_UPDATE'] = 0
    #try:
    #    newRA  = results['TSMAP_RAMAX']
    #    newDEC = results['TSMAP_DECMAX']
    #    err68  = results['TSMAP_ERR68']
    #    tsmax  = results['TSMAP_MAX']
    #    sep    = results['TSMAP_SEP']        
    #    if tsmax>9 and err68<results['ERR']:
    #        results['TSMAP_UPDATE'] = 1
    #        
    #Print()
    
    pass
# #################################################
# THIS RETRIEVE THE GBM FILES and make the GBM LIGHTCURVES
# #################################################
Prompt(['COMPOSITELC'],mode)
if bool(results['COMPOSITELC']):
    Prompt(['REMAKE_COMPOSITELC'],mode)
    if bool(results['REMAKE_COMPOSITELC']):
        PlotAngularSeparation(mode=mode)
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
        GetLLE() # This will get the data.
        #MakeSelectEnergyDependentROI(mode=mode) # This provides the events
        pass
    Print()
    MakeCompositeLightCurve()
    pass

    
Done(cleanUp)        
pass
