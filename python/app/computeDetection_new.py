print '--------------------------------------------------'
now=time.localtime()
print ' GTGRB EXECUTION STARTED %s-%s-%s %s-%s-%s' % (now[0],now[1],now[2],now[3],now[4],now[5])
pfiles  = os.environ['PFILES']

##################################################
try:    timeShift = float(os.environ['TIMESHIFT']) #=-2.0 * 5733.0672 = 11466.1344)
except: timeShift=0
##################################################
Set(**ListToDict(sys.argv))

GRBtheta = lat[0].getGRBTheta()
grbname  = grb[0].Name
irfs     = lat[0]._ResponseFunction
#------------------------#

print ' GRBNAME     = ',grbname
print ' PFILES      = ',pfiles
print ' PYTHONPATH  = ',os.environ['PYTHONPATH']
print ' INDIR       = ',os.environ['INDIR']
print ' OUTDIR      = ',os.environ['OUTDIR']
try:    print ' ROOTISBATCH = ',os.environ['ROOTISBATCH']
except: pass
print ' mode        = ',mode
try:    IGNORE_THETA = bool(float(results['IGNORE_THETA']))
except: IGNORE_THETA = False
print ' IGNORE_THETA = ',IGNORE_THETA

if GRBtheta < 89.0 or IGNORE_THETA:
    # -------------------------------------------------- #
    ResultsFileName = ReadResults()    
    # -------------------------------------------------- #
    try:    EXTENDED     = bool(float(results['EXTENDED']))
    except: EXTENDED     = 1
    try:    MAKE_LLE     = bool(float(results['MAKE_LLE']))
    except: MAKE_LLE     = 0
    try:    MAKE_LIKE    = bool(float(results['MAKE_LIKE']))
    except: MAKE_LIKE    = 0
    # -------------------------------------------------- #
    # PLOT ANGULAR SEPARATION
    PlotAngularSeparation(mode=mode)
    Print()
    # -------------------------------------------------- #
    if GRBtheta < 89.0 and MAKE_LLE:
        import makeLLE
        version=1
        DURATION=100
        if 'P8' in irfs: 
            os.environ['LLEIFILE'] ='/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-10-00-02/makeLLEproducts/python/config_LLE_DRM/Pass8.txt'
            os.environ['MCBASEDIR']='/MC-Tasks/ServiceChallenge/GRBSimulator-Pass8'
        else:
            os.environ['LLEIFILE'] ='/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-10-00-02/makeLLEproducts/python/config_LLE_DRM/Pass7.txt'
            os.environ['MCBASEDIR']='/MC-Tasks/ServiceChallenge/GRBSimulator-Pass7'
            pass
        
        output_ez= os.environ['OUTDIR']
        OBJECT   = results['GRBNAME']
        TRIGTIME = float(results['GRBMET'])
        RA_OBJ   = float(results['RA'])
        DEC_OBJ  = float(results['DEC'])
        FT2      = lat[0].FilenameFT2
        
        makeLLE.GenerateLLE(output_ez,version,OBJECT,TRIGTIME, RA_OBJ,DEC_OBJ,DURATION,
                            mode=['pha','forReal'])        
        makeLLE.ComputeLLEDetection(output_ez,version,OBJECT,FT2,RA_OBJ,DEC_OBJ,TRIGTIME,NSIGMA=4.0)
        output_dir_version='%(output_ez)s/%(OBJECT)s/v%(version)02d' % locals()
        cmd_cp = 'cp %(FT2)s %(output_dir_version)s/gll_pt_bn%(OBJECT)s_v%(version)02d.fit' %locals()
        print cmd_cp
        os.system(cmd_cp)
        pass
    # -------------------------------------------------- #
    if MAKE_LIKE:
        LIKES={}
        RA0  = results['RA']
        DEC0 = results['DEC']
        t05  = results['GRBT05']
        t90  = results['GRBT90']
        
        # OPERATE ON DIFFERENT TIME SCALES:
        #for tw  in [1,3,10,30,100,300,1000,3000]:
        for tw  in [t05+t90]:
            UpdatePosition(RA0,DEC0)
            suffix='LIKE_MY_%d' % tw
            if MakeSelect(mode=mode, tstart=0.0, tstop=tw, plot=0,suffix=suffix)>0:            
                MakeLikelihoodAnalysis(mode=mode, tstart=0.0, tstop=tw, extended=0, pha=0, prob=1, suffix=suffix)            
                ts   = float(results['%s_TS_%s' % (suffix,'GRB')])
                LIKES[suffix]=[ts,0,tw, grb[0].ra, grb[0].dec]
                # 1 GTFINDSRC:
                MakeGtFindSrc(UPDATE_POS='yes',LIKE_SUFFIX=suffix)            
                # 1 GTTSMAP:
                # MakeGtTsMap(UPDATE_POS='yes',LIKE_SUFFIX=suffix)                        
                if results['FindSrc_UPDATE']:
                    suffix     = 'LIKE_UP_%d' % tw        
                    MakeSelect(mode=mode, tstart=0.0, tstop=tw, plot=0,suffix=suffix)
                    MakeLikelihoodAnalysis(mode=mode, tstart=0.0, tstop=tw, extended=0, pha=0,suffix=suffix)                            
                    ts   = float(results['%s_TS_%s' % (suffix,'GRB')])
                    LIKES[suffix]=[ts,0.0,tw, grb[0].ra, grb[0].dec]
                    pass
                pass
            pass
        like_max    = None
        like_ts_max = 0
        t0_ts_max   = 0.0
        t1_ts_max   = t90+t05
        ra_ts_max   = RA0
        dec_ts_max  = DEC0
        for k in LIKES.keys():
            if LIKES[k][0] > like_ts_max: 
                like_max=k
                like_ts_max = LIKES[k][0]
                t0_ts_max   = LIKES[k][1]
                t1_ts_max   = LIKES[k][2]
                ra_ts_max   = LIKES[k][3]
                dec_ts_max  = LIKES[k][4]
                pass
            pass
        
        if like_max is not None:      print ' *** BEST LIKELIHOOD:',like_max,LIKES[like_max]
        else:   like_max = 'LIKE_MY'
        
        UpdatePosition(ra_ts_max,dec_ts_max)
        MakeSelect(mode=mode, tstart=t0_ts_max, tstop=t1_ts_max, plot=1,suffix=like_max)
        if EXTENDED:
            MakeSelect(mode=mode, tstart=t0_ts_max, tstop=t1_ts_max, plot=0,suffix='EXTENDED')
            MakeLikelihoodAnalysis(mode=mode, tstart=0, tstop=0, extended=1, pha=1, prob=1)
            Print()
            if 'LIKE_DURMIN' in results.keys() and 'LIKE_DURMAX' in results.keys():
                suffix='LIKE_AG'
                t0=float(results['LIKE_DURMIN'])
                t1=float(results['LIKE_DURMAX'])
                MakeSelect(mode=mode, tstart=t0, tstop=t1, plot=0,suffix=suffix)
                MakeLikelihoodAnalysis(mode=mode,tstart=t0,tstop=t1,prob=1,extended=0,suffix=suffix)
                ts   = float(results['%s_TS_%s' % (suffix,'GRB')])
                LIKES[suffix]=[ts,t0,t1, grb[0].ra, grb[0].dec]
                k=suffix
                if LIKES[k][0] > like_ts_max:
                    like_max=k
                    like_ts_max = LIKES[k][0]
                    t0_ts_max   = LIKES[k][1]
                    t1_ts_max   = LIKES[k][2]
                    ra_ts_max   = LIKES[k][3]
                    dec_ts_max  = LIKES[k][4]
                    pass
                pass
            pass
        for k in results.keys():
            if like_max in k: 
                value=results[k]
                results[k.replace(like_max,'LIKE_BEST')]=value
                pass
            pass
        pass
    pass
Done(True)
