import scipy as sp
import matplotlib
matplotlib.use('Agg')
pfiles  = os.environ['PFILES']


cleanUp = False
LLE_ANALYSIS                      = 1
LIKELIHOOD_GBM_ANALYSIS           = 1
LIKELIHOOD_SU_ANALYSIS            = 1
TIME_BIN_LIKELIHOOD_ANALYSIS      = 0#0
TIME_RESOLVED_LIKELIHOOD_ANALYSIS = 1

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

GRBTHETA    = float(results['THETA'])
GRBZENITH   = float(results['ZENITH'])
grbname     = grb[0].Name
GRBT05      = float(results['GRBT05'])
GRBT95      = float(results['GRBT95'])
GBMT05      = float(results['GBMT05'])
GBMT95      = float(results['GBMT95'])
GRBMET      = float(results['GRBMET'])
GRB_RA      = float(results['RA'])
GRB_DEC     = float(results['DEC'])
SU_DURATION = float(results['SU_DURATION'])

output_ez   = os.environ['OUTDIR']
#if '160625945' in grbname: GBMT95=GRBT05+50

##################################################
print '--------------------------------------------------'
now=time.localtime()
print ' GTGRB EXECUTION STARTED %s-%s-%s %s-%s-%s' % (now[0],now[1],now[2],now[3],now[4],now[5])
print ' GRBNAME    = ',grbname
print ' PFILES     = ',pfiles
print ' PYTHONPATH = ',os.environ['PYTHONPATH']
print ' INDIR      = ',os.environ['INDIR']
print ' OUTDIR     = ',os.environ['OUTDIR']
try:     print ' ROOTISBATCH= ',os.environ['ROOTISBATCH']
except:  pass
chatter = 2

##################################################
# PLOT ANGULAR SEPARATION
##################################################
PlotAngularSeparation(nav_start=60,nav_stop=300,mode=mode)
PlotAngularSeparation(nav_start=60,nav_stop=SU_DURATION,mode=mode)
if os.getenv('GETGBMDATA', '0')=='1':  
    GetGBMFiles()
    LLE_ANALYSIS                      = 1
    LIKELIHOOD_GBM_ANALYSIS           = 0
    LIKELIHOOD_SU_ANALYSIS            = 0
    TIME_BIN_LIKELIHOOD_ANALYSIS      = 0
    TIME_RESOLVED_LIKELIHOOD_ANALYSIS = 0
    pass
make_tsmap=True
if 'MAKE_TSMAP' in results.keys():
    make_tsmap = int(results['MAKE_TSMAP'])
    pass
#if os.getenv('MAKE_TSMAP', '1')=='0': make_tsmap=False
#Done()
#exit()

NaIFiles=[]
BGOFiles=[]
try:
    closer_detectors=GetNearestDet()
    for gbm_det_n in closer_detectors:
        gbm_det=gbm_det_n.lower()
        print 'Working on...: ',gbm_det
        gbm             = GBM.GBM(grb=grb[0],detector_name=gbm_det)
        tte_filename    = gbm.tte_File
        print tte_filename
        if tte_filename is not None and os.path.exists(tte_filename):
            if 'n' in gbm_det: NaIFiles.append(tte_filename)
            else: BGOFiles.append(tte_filename)
            pass
        pass
except:
    pass
print 'NaI files:',NaIFiles
print 'BGO files:',BGOFiles
if os.getenv('GETGBMDATA', '0')=='1':  Print()


#MakeGBMLightCurves(mode=mode)
#GetLLE()
##################################################
# SELECT ON THE SU DURATION
##################################################
dt=1.0
if results['SU_DURATION']>100: dt=5
if results['SU_DURATION']>300: dt=30
if results['SU_DURATION']>1000:dt=60
MakeSelect(mode=mode,tstart=0.0,tstop=SU_DURATION,plot=1,dt=dt)
# #################################################
# LLE ANALYSIS AND FILE GENERATION
##################################################
LLE_VERSION=1
LLEONLY=os.getenv('LLEONLY', '0')=='1'
print 'GRB location: theta,zenith=',GRBTHETA,GRBZENITH,'LLEONLY',LLEONLY
if LLE_ANALYSIS:
    if GRBTHETA < 89.0 and results['MAKE_LLE']==1:
        import makeLLE
        

        if 'P8' in results['IRFS']: 
            os.environ['LLEIFILE'] ='/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-10-00-02/makeLLEproducts/python/config_LLE_DRM/Pass8.txt'
            os.environ['MCBASEDIR']='/MC-Tasks/ServiceChallenge/GRBSimulator-Pass8'
        else:
            os.environ['LLEIFILE'] ='/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-10-00-02/makeLLEproducts/python/config_LLE_DRM/Pass7.txt'
            os.environ['MCBASEDIR']='/MC-Tasks/ServiceChallenge/GRBSimulator-Pass7'
            pass

        LLE_results=makeLLE.do(outdir  = output_ez,
                               version = LLE_VERSION,
                               ttime   = GRBMET,
                               tstart  = GBMT05,
                               tstop   = GBMT95,
                               ra      = GRB_RA,              
                               dec     = GRB_DEC,
                               deltat  = 1.0,
                               name    = grbname,
                               zmax    = max(100.0,GRBZENITH+20),
                               thetamax= max(90.0,GRBTHETA+20),
                               radius  = -1,
                               ignore_theta=1,
                               before=1000,
                               after=1000,
                               clobber=1,
                               lle=1,drm=0,detect=1,
                               regenerate_after_detection=1)
        
        for k in LLE_results.keys():   results[k]=LLE_results[k]
        # results['LLEBBBD_SIG_DETECTED']= LLE_results['LLEBBBD_SIG_DETECTED']
        #results['LLEBBBD_SIG']         = LLE_results['LLEBBBD_SIG']
        #results['LLEBBBD_T0']          = LLE_results['LLEBBBD_T0']
        # results['LLEBBBD_T1']          = LLE_results['LLEBBBD_T1']
        # results['LLE_SIG'] = LLE_results['LLE_SIG']
        # results['LLE_T0']  = LLE_results['LLE_T0']
        # results['LLE_T1']  = LLE_results['LLE_T1']
        # copy the FT2 file in the output directory
        #cmd_cp = 'cp %(FT2)s %(output_ez)s/%(grbname)s/v%(LLE_VERSION)02d/gll_pt_bn%(grbname)s_v%(LLE_VERSION)02d.fit' %locals()
        #print cmd_cp
        #os.system(cmd_cp)
        pass
    Print()
    pass

if bool(LLEONLY): 
    LIKELIHOOD_GBM_ANALYSIS           = 0
    LIKELIHOOD_SU_ANALYSIS            = 0
    TIME_BIN_LIKELIHOOD_ANALYSIS      = 0
    TIME_RESOLVED_LIKELIHOOD_ANALYSIS = 0    
    pass

try: WEIGHBYEXPOSURE    = bool(results['WEIGHBYEXPOSURE'])
except: WEIGHBYEXPOSURE = True
##################################################
# INTEGRATED LIKELIHOOD ANALYSIS
##################################################
##################################################
# GBM LIKELIHOOD ANALYSIS
##################################################
likelihoods=[]
Print()
if LIKELIHOOD_GBM_ANALYSIS:
    suffix='LIKE_GBM'
    MakeLikelihoodAnalysis(tstart=GRBT05,tstop=GRBT95,prob=1,suffix=suffix)
    likelihoods.append(suffix)
    Print()    
    pass
# FROM SU ANALYSIS
if LIKELIHOOD_SU_ANALYSIS:
    suffix='LIKE_SU'
    rc=MakeLikelihoodAnalysis(tstart=0.0,tstop=SU_DURATION,prob=1,suffix=suffix)
    likelihoods.append(suffix)
    if rc>0:
        if make_tsmap: MakeGtTsMap(LIKE_SUFFIX='LIKE_SU')
        MakeGtFindSrc(UPDATE_POS=0,LIKE_SUFFIX='LIKE_SU')
        pass
    Print()
    pass

like_max    = None
like_ts_max = 0
t0_ts_max   = 0
t1_ts_max   = 0

if TIME_BIN_LIKELIHOOD_ANALYSIS:
    timeWindows = [1,3,10,30,100,300,1000,3000]        
    for tw  in timeWindows:
        suffix='LIKE_MY_%d' % tw
        MakeLikelihoodAnalysis(mode=mode, tstart=0, tstop=tw, extended=0, pha=0, prob=0, suffix=suffix)
        likelihoods.append(suffix)
        kkk=('%s_TS_GRB' % suffix)
        if kkk in results.keys():
            if float(results[kkk]) > like_ts_max:
                like_max  = suffix
                t0_ts_max = 0
                t1_ts_max = tw
                like_ts_max= float(results[kkk])
                pass
            pass
        Print()
        pass        
    if like_max is not None:             
        print '--------------------------------------------------'
        print ' => DETECTION STEP (%s)' % like_max
        print '    HIGHEST TS = %.1f' % like_ts_max
        print '    FROM %.3f TO %.3f ' %(t0_ts_max,t1_ts_max)
        print '--------------------------------------------------'
        # MakeGtFindSrc(UPDATE_POS=1,LIKE_SUFFIX=like_max)
        # Print()
        # --------------------------------------------------#
        # if results['FindSrc_UPDATE'] == 1: suffix_up='%s_UP' % like_max
        # else: suffix_up=like_max            
        # EXTENDED EMISSION (TIME RESOLVED ANALYSIS)
        # MakeLikelihoodAnalysis(mode=mode, tstart=0, tstop=0, extended=1, pha=1, suffix=suffix, prob=1)
        # Print()
        pass
    pass

        
##################################################
# TIME RESOLVED LIKELIHOOD ANALYSIS
##################################################
if TIME_RESOLVED_LIKELIHOOD_ANALYSIS:
    logbins=sp.logspace(log10(results['EXTENDED_TSTART']),
                        log10(results['EXTENDED_TSTOP']),
                        results['NLIKEBINS'])
    
    
    if 'LIKE_SU_gtsrcprob' in results.keys():
        fileName = results['LIKE_SU_gtsrcprob']
        hdulist  = pyfits.open(fileName)
        hdulist.info()
        tbdata   = hdulist[1].data
        prob_times     = tbdata.field('TIME')-GRBMET
        probabilities  = tbdata.field('GRB')
        prob           = 0.9
        user_time_bins=prob_times[probabilities>prob][::3]
        if len(user_time_bins)>0:
            if user_time_bins[-1]!=prob_times[-1]: user_time_bins=sp.append(user_time_bins,prob_times[-1])
            user_time_bins=sp.append(logbins[logbins<user_time_bins[0]],user_time_bins)
            user_time_bins=sp.append(user_time_bins,logbins[logbins>user_time_bins[-1]])
        else:
            user_time_bins=logbins
            pass
    else:    user_time_bins=logbins
    
    user_time_bins=user_time_bins.tolist()
    like_timeBins='USER_PROVIDED'
    
    MakeLikelihoodAnalysis(tstart=0,tstop=0,prob=1,extended=1,suffix='LIKE_SU',like_timeBins=like_timeBins,user_time_bins=user_time_bins)
    Print()
    if 'LIKE_DURMIN' in results.keys() and 'LIKE_DURMAX' in results.keys():
        suffix='LIKE_AG'
        likelihoods.append(suffix)
        MakeLikelihoodAnalysis(tstart=results['LIKE_DURMIN'],tstop=results['LIKE_DURMAX'],prob=1,extended=0,suffix=suffix)
        # Print()
        # THIS IS THE EXT: EXTENDED ENISSION ONLY:
        if GRBT95<float(results['LIKE_DURMAX']):
            suffix='LIKE_EXT'
            likelihoods.append(suffix)            
            MakeLikelihoodAnalysis(tstart=GRBT95,tstop=results['LIKE_DURMAX'],prob=1,extended=0,suffix=suffix)
            pass
        Print()        
        pass

    # THIS IS THE LIKELIHOOD WITH THE HIGHER TS:
    for suffix in likelihoods:
        kkk=('%s_TS_GRB' % suffix)
        if kkk in results.keys():
            if float(results[kkk]) > like_ts_max:
                t0_ts_max=float(results['%s_T0' % suffix])
                t1_ts_max=float(results['%s_T1' % suffix])
                like_max=suffix
                like_ts_max= float(results[kkk])
                pass
            pass
        pass
    # THIS IS ALWAYS THE BEST LIKELIHOOD:
    suffix='LIKE_BEST'
    #likelihoods.append(suffix)
    MakeLikelihoodAnalysis(mode=mode, tstart=t0_ts_max, tstop=t1_ts_max, extended=0, pha=1, prob=1, suffix=suffix)
    Print()
    pass

#MakeGtTsMap(LIKE_SUFFIX='LIKE_BEST')
#Print()
##################################################
# COMPOSITE LC
##################################################
print '===>MAKING THE COMPOSITE LC'
import scripts.CompositeLightCurve_MPL as CLC
LLEFiles = glob.glob('%s/%s/v%02d/gll_lle*fit' % (output_ez,grbname,LLE_VERSION))
if 'use_in_composite' in results.keys():
    LATFiles = [results['use_in_composite'].replace('.root','.fits')]
else:
    LATFiles=[]
LCTSTART =-20
LCTSTOP  = 290
DT       = 1.0
if GRBT95-GRBT05<2.0:
    LCTSTART = -2
    LCTSTOP  = 29
    DT       = 0.25
    pass
LC=CLC.CompositeLC(GRBMET,TMIN=LCTSTART,TMAX=LCTSTOP,DT=DT)
if len(NaIFiles)>0: LC.SetNaI1(NaIFiles,10,520)
if len(BGOFiles)>0: LC.SetBGO1(BGOFiles,520,10000)
if len(LLEFiles)>0: LC.SetLLE1(LLEFiles,30,100)
if len(LATFiles)>0: LC.SetLAT1(LATFiles,100,100000)
LC.SetOutput('%s/%s/%s_CompoLC.png' % (os.environ['OUTDIR'],grbname,grbname))
LC.Plot()

##################################################
# FINISHING UP
##################################################
Done()
