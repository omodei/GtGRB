print '***************************************************'
print ' COMPUTING THE LIKELIHOOD ANALYSIS...'
Set(**ListToDict(sys.argv))
GRBtheta = lat[0].getGRBTheta()
grbname  = grb[0].Name
print ' GRBNAME: %s, Mode: %s' % (grbname, mode)
print '***************************************************'
if GRBtheta < 200.0:
    ResultsFileName = ReadResults()
    try: tstart = float(results['LIKETSTART'])
    except:  tstart=0
    try: tstop  = float(results['LIKETSTOP'])
    except: tstop=0
    try: extended  = int(results['EXTENDED'])
    except: extended=0
    try: extended_tstart  = float(results['EXTENDED_TSTART'])
    except: extended_tstart=0.01
    try: extended_tstop   = float(results['EXTENDED_TSTOP'])
    except: extended_tstop=86400
    if extended_tstart==extended_tstop: extended=0
    
    try: tsmap            = int(results['MAKE_TSMAP'])
    except: tsmap=0
    try: UPDATE_POS_TSMAP  = int(results['UPDATE_POS_TSMAP'])
    except: UPDATE_POS_TSMAP=0
    # ------------------------------------------------------ #
    print '=================================================='
    print ' PlotAngularSeparation(nav_start=%f, nav_stop=%f, mode=mode)' % (tstart, tstop)
    print '=================================================='
    PlotAngularSeparation(nav_start=tstart, nav_stop=tstop, mode=mode)
    MakeSelect(tstart=tstart,tstop=tstop,prob=1,pha=1,mode=mode)        
    MakeLikelihoodAnalysis(mode=mode,
                           tstart=tstart,
                           tstop=tstop,
                           pha=0,
                           prob=1,
                           suffix='MY_LIKE',
                           EXTENDED_TSTART=extended_tstart,
                           EXTENDED_TSTOP=extended_tstop,
                           extended=extended)

    if tsmap: MakeGtTsMap(UPDATE_POS=UPDATE_POS_TSMAP,LIKE_SUFFIX='MY_LIKE',REFITTING='no')
    Print()
    Done()
else:
    print '%%%%%%%%%%%%%%%%%%%%%%%% GRB %s is out of the FOV: Theta = %s ' % (grbname,GRBtheta)
    pass

