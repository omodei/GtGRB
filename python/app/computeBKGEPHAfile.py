print '***************************************************'
print 'Running test sequence... '
print ' GRBNAME: %s, Mode: %s' % (grbname, mode)
print '***************************************************'
#mode = 'go'
#Set(grbname, mode=mode)
Set(**ListToDict(sys.argv))
GRBtheta = lat[0].getGRBTheta()



if GRBtheta < 100.0:
    ReadResults()
    # ------------------------------------------------------ #
    # full sequence: comment out what you don't need, but remember relavive dipendences...
    #MakeSelect(mode=mode)

    # THIS IS FOR THE GBM:
    Print()
    GetGBMFiles()
    try:
        tstart=results['PHAstart']
        tstop=results['PHAstop']
    except:
        tstart = results['GRBT05']
        tstop  = results['GRBT95']
        pass
    
    Make_PHA_GBM_Files(tstart=tstart,tstop=tstop)
    # THIS IS FOR THE LAT:
    nevents = MakeSelectEnergyDependentROI(mode=mode,
                                           tstart=tstart,
                                           tstop=tstop,
                                           rspgen=True,
                                           plot=False)
    
    Make_BKG_PHA(start=tstart,stop=tstop)
    # FINISHING UP
    #nevents = MakeSelectEnergyDependentROI(mode=mode)    
    Done()
    
else:
    print '%%%%%%%%%%%%%%%%%%%%%%%% GRB %s is out of the FOV: Theta = %s ' % (grbname,GRBtheta)
    pass
