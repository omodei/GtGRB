print '***************************************************'
print ' COMPUTE THE DURATION using the BKGE ' 
print '***************************************************'
Set(**ListToDict(sys.argv))
GRBtheta = lat[0].getGRBTheta() 
if GRBtheta < 100.0:
    baseDir = '%s/%s' % (os.environ['OUTDIR'],grb[0].Name)
    results_fileName='%s/results_%s.txt' % (baseDir,grb[0].Name)    
    try:
        ReadResults(ResultsFileName = results_fileName, overw=1) # This reads the stored results. overw=1: over write the "Set" variables with the stored results.
    except:
        pass
    # ------------------------------------------------------ #
    MakeSelect(mode=mode)
    CalculateLATT90(emin=lat[0].Emin, emax=lat[0].Emax)
    Done()
else:
    print '%%%%%%%%%%%%%%%%%%%%%%%% GRB %s is out of the FOV: Theta = %s ' % (grb[0].Name,GRBtheta)
    pass
