print '--------------------------------------------------'
print ' *********** computeDetection v1.1.2 *************'
now=time.localtime()
print ' GTGRB EXECUTION STARTED %s/%s/%s %s:%s:%s' % (now[0],now[1],now[2],now[3],now[4],now[5])
pfiles  = os.environ['PFILES']
##################################################

if mode=='go': Set(**ListToDict(sys.argv))
pass

GRBtheta = lat[0].getGRBTheta()
grbname  = grb[0].Name
irfs     = lat[0]._ResponseFunction
#------------------------#
print ' GRBNAME    = ',grbname
print ' THETA      = ',GRBtheta
print ' PFILES     = ',pfiles
print ' PYTHONPATH = ',os.environ['PYTHONPATH']
print ' INDIR      = ',os.environ['INDIR']
print ' OUTDIR     = ',os.environ['OUTDIR']
try:    print ' ROOTISBATCH= ',os.environ['ROOTISBATCH']
except: pass

try:    IGNORE_THETA = bool(float(results['IGNORE_THETA']))
except: IGNORE_THETA = False

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
    try:    MAKE_TSMAP   = bool(float(results['MAKE_TSMAP']))
    except: MAKE_TSMAP   = 1
    # -------------------------------------------------- #
    # PLOT ANGULAR SEPARATION
    # -------------------------------------------------- #    
    PlotAngularSeparation(mode=mode)
    # -------------------------------------------------- #
    # SELECT EVENTS, CALCULATE PROBABILITY OF BEING GRB EVENT
    # -------------------------------------------------- #
    #if MakeSelect(mode=mode,tstart=-100,tstop=1000,plot=0)>0:  ComputeBayesProbabilities()        
    MakeSelect(mode=mode)
    Print()    
    # #################################################

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
    
    
    if GRBtheta < 89.0 and MAKE_LLE and 1==0:
        GetLLE()                                             # This will get the data.
        try:
            print 'Executing MakeLLELightCurves...'
            tmpdict={'task':'detection'}
            tmpdict.update(ListToDict(sys.argv))        
            MakeLLELightCurves(**(tmpdict)) # Jack's code        
            if float(results['LLE_DetMaxSign']) > 4.0:          # Pre Trial Probability in sigma
                tmpdict={'task':'duration'}
                tmpdict.update(ListToDict(sys.argv))        
                MakeLLELightCurves(**(tmpdict))          # Jack's code
                pass    
            print '--------------------------------------------------------------------\n'
            Print()
        except:
            print '##################################################'
            print 'An error occourced in computig MakeLLELightCurves!'
            print '##################################################'
            pass                
        try:
            #print 'Executing MakeLLEDetectionAndDuration()...'
            #MakeLLEDetectionAndDuration() # Fred's Code
            pass
        except:
            print '##################################################'
            print 'An error occourced in computig MakeLLELightCurves!'
            print '##################################################'
            pass
        print '--------------------------------------------------------------------\n'
        pass
    # #################################################
    like_max    = None
    like_ts_max = 0
    t0_ts_max   = 0
    t1_ts_max   = 0
    
    if MAKE_LIKE:
        #--------------------------------------------------#
        # 1. Run likelihood analysis in different time windows:                
        #--------------------------------------------------#
        timeWindows = [1,3,10,30,100,300,1000,3000,10000]        
        for tw  in timeWindows:
            suffix='LIKE_MY_%d' % tw
            MakeLikelihoodAnalysis(mode=mode, tstart=0, tstop=tw, extended=0, pha=0, prob=1, suffix=suffix)            
            kkk=('%s_TS_GRB' % suffix)
            if kkk in results.keys():
                if float(results[kkk]) > like_ts_max:
                    like_max=suffix
                    t0_ts_max=0
                    t1_ts_max=tw
                    like_ts_max= float(results[kkk])
                    pass
                pass
            pass        
        Print()
        if like_max is not None:             
            print '--------------------------------------------------'
            print ' => DETECTION STEP (%s)' % like_max
            print '    HIGHEST TS = %.1f' % like_ts_max
            print '    FROM %.3f TO %.3f ' %(t0_ts_max,t1_ts_max)
            print '--------------------------------------------------'
            MakeGtFindSrc(UPDATE_POS=1,LIKE_SUFFIX=like_max)
            Print()
            # --------------------------------------------------#
            if results['FindSrc_UPDATE'] == 1: suffix_up='%s_UP' % like_max
            else: suffix_up=like_max            
            # EXTENDED EMISSION (TIME RESOLVED ANALYSIS)
            MakeLikelihoodAnalysis(mode=mode, tstart=0, tstop=0, extended=1, pha=1, suffix=suffix, prob=1)
            Print()
            if 'LIKE_DURMIN' in results.keys() and 'LIKE_DURMAX' in results.keys():
                MakeLikelihoodAnalysis(mode=mode,tstart=results['LIKE_DURMIN']-0.01,tstop=results['LIKE_DURMAX']+0.01,prob=1,extended=0,suffix='LIKE_AG')
                Print()
                pass
            twoMore=[suffix_up,'LIKE_AG']
            for suffix in twoMore:
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
            MakeLikelihoodAnalysis(mode=mode, tstart=t0_ts_max, tstop=t1_ts_max, extended=0, pha=1, prob=1, suffix='LIKE_BEST')            
            Print()
            # RUN TSMAP, OPTIMIZE THE LOCATION:        
            tsmap = 0
            if like_ts_max>9: tsmap = MAKE_TSMAP
            if tsmap: MakeGtTsMap(UPDATE_POS=0,LIKE_SUFFIX='LIKE_BEST',REFITTING=0)
            Print()
            # --------------------------------------------------#
            pass
        print '--------------------------------------------------'
        print ' ===> SUMMARY <====' 
        print ' INTERVAL WITH HIGHEST TS: %s' % like_max
        print ' HIGHEST TS = %.1f'  % like_ts_max
        print ' FROM %.3f TO %.3f ' % (t0_ts_max,t1_ts_max)
        print '--------------------------------------------------'
        pass
    pass
else: print 'THETA > 89 DEGREES. SKIPPING GRB:%s' % grbname
print '--------------------------------------------------'
Done(True)
