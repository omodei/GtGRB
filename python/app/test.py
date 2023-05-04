print '***************************************************'
print 'Running test sequence... '
print ' GRBNAME: %s, Mode: %s' % (grbname, mode)
print '***************************************************'

TestOptimalBinning       = False
TestSplitForGTI          = False
TestPlotExtendedEmission = False

#mode = 'go'
Set(**ListToDict(sys.argv)))

GRBtheta = lat[0].getGRBTheta() 
if GRBtheta < 100.0:
    baseDir = 'DATA/GRBOUT/%s' % (grb[0].Name)
    like_fileName='%s/ExtendedEmission/like_%s.txt' % (baseDir,grb[0].Name)
    # PlotAngularSeparation('go')
    # Print()    
    results_fileName = ReadResults() # This reads the stored results.
    
    # this makes the optimal binning
    if(TestOptimalBinning):
        lat[0].setTmin(grb[0].Ttrigger)
        lat[0].setTmax(grb[0].Ttrigger+10000)
        lat[0].make_select()
        from scripts import MakeOptimalBinning        
        bins0,bins1      = MakeOptimalBinning.EqualNumberOfEvents(lat[0],10,0.5,float(results['GBMT95']))
        print '--------------------------------------------------'
        pass
    
    # this tests the SplitForGTI
    if TestSplitForGTI:
        bins             = range(-1,10000,100)
        bins0,bins1      = MakeOptimalBinning.SplitForGTI(lat[0],bins)
        pass
    # this remakes all the results plot:
    if TestPlotExtendedEmission:
        from scripts import LikelihoodFit    
        results1 = LikelihoodFit.PlotExtendedEmission(like_fileName)
        AddResults(results1)
        pass
    
    #        LD = float(results['LUMINOSITY_DISTANCE'])
    #        if LD>0:
    #            Area                    = 4.0*math.pi*pow(LD*100.0,2.0) # cm^2
    #            results['EISO52']         = float(results['FLUENCE_ENE'])     * Area /1.0e52# erg
    #            results['EISO52_ERR']     = float(results['FLUENCE_ENE_ERR']) * Area /1.0e52# erg
    #            print ' Eiso (z=%.3f) = (%lf +/- %lf) x 10^52 ergs' %(pars['REDSHIFT'],results['EISO52'],results['EISO52_ERR'])
    #            pass
    # ------------------------------------------------------ #
    # full sequence: comment out what you don't need, but remember relavive dipendences...
    #print 'Executing MakeLLELightCurves...'
    #MakeLLELightCurves(**(ListToDict(sys.argv))) # Jack's code
    #if results['LLE_DetMaxSign'] > 4.0:          # Pre Trial Probability in sigma
    #    tmpdict={'task':'duration'}
    #    tmpdict.update(ListToDict(sys.argv))        
    #    MakeLLELightCurves(**(tmpdict))          # Jack's code
    #    pass    
    #print '--------------------------------------------------------------------\n'
    #MakeLLEDetectionAndDuration() # Fred's Code
    #Print()
    #pass
    # #################################################
    # MakeSelect(mode=mode)
    # MakeGtFindSrc()
    # ComputeDuration()
    # ComputeKEYDuration()
    # ComputePoissonProbabilities()
    # ComputeProbabilities()
    # ComputeBayesProbabilities()
    # MakeSelectFrontBack()
    # MakeSelectEnergyDependentROIFrontBack(mode)
    # MakeSelectEnergyDependentROI(mode)
    
    # MakeSelect()        
    # Print()
    # GetGBMFiles()
    # MakeGBMLightCurves(mode)
    # Print()
    MakeLikelihoodAnalysis(mode=mode)
    Done()
else:
    print '%%%%%%%%%%%%%%%%%%%%%%%% GRB %s is out of the FOV: Theta = %s ' % (grbname,GRBtheta)
    pass
