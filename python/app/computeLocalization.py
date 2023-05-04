print '***************************************************'
print ' COMPUTING THE LOCALIZATION ANALYSIS    ANALYSIS...'
Set(**ListToDict(sys.argv))
GRBtheta = lat[0].getGRBTheta()
grbname  = grb[0].Name
print ' GRBNAME: %s, Mode: %s' % (grbname, mode)
print '***************************************************'
if GRBtheta < 200.0:
    ResultsFileName = ReadResults()
    tstart   = results['GRBT05']
    tstop    = results['GRBT95']

    # 1) Find Position is from GRBT05 to GRBT95:
    if MakeSelect(mode=mode,tstart=tstart,tstop=tstop)>0: MakeGtFindSrc(mode=mode)    
    # ------------------------------------------------------ #
    # MakeSelect(mode=mode)
    # 2) Make the likelihood analysis and compute the tsmap:    
    MakeLikelihoodAnalysis(mode     = mode,
                           tstart   = tstart,
                           tstop    = tstop,
                           extended = 0,
                           pha      = 0)
    Done()
else:
    print '%%%%%%%%%%%%%%%%%%%%%%%% GRB %s is out of the FOV: Theta = %s ' % (grbname,GRBtheta)
    pass

