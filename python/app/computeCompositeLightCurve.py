#!/urs/bin/env python

print '***************************************************'
print ' MAKE THE COMPOSITE LIGHT CURVE '
print '***************************************************'
mydict=ListToDict(sys.argv)
Set(**mydict)
print mydict

remake = False

ResultsFileName = ReadResults()

if ResultsFileName is None: remake = True

if not remake and 'REMAKE' in mydict:
    REMAKE = mydict['REMAKE']
    if 'true' in REMAKE.lower(): remake = True
    elif 'false' in REMAKE.lower(): remake = False
    else:
        print 'REMAKE should be either "True" or "False". Current value is: %s ' % REMAKE
        pass
    pass

if remake:
    print 'Regenerating some quantities...'
    PlotAngularSeparation(mode=mode)
    GetGBMFiles()
    MakeGBMLightCurves(mode=mode)
    GetLLE() # This will get the data.
    ##################################################
    # This is from TSRAT to TSTOP, saving the output in _ROI_E directory    
    #MakeSelectEnergyDependentROI(mode=mode) # This provides the events
    ##################################################
    pass
GetLLE() # This will get the data.
#Print() # Save all in the results
#try:
#    mydict['DT']=results['LLE_DetBin']
#except:
#    pass
#Print()
#MakeGBMLightCurves(mode=mode) # This provide the GBM curves
MakeCompositeLightCurve(**mydict) # combine the LC to make a beautiful plot
Done() # Save and exit



