print '***************************************************'
print ' SELECT EVENTS, MAKING LAT LIGHTCURVE and SKYMAP *ENERGY DEPENDENT ROI)...'
Set(**ListToDict(sys.argv))
grbname  = grb[0].Name
print ' GRBNAME: %s, Mode: %s' % (grbname, mode)
print '***************************************************'
ResultsFileName = ReadResults()
MakeSelectEnergyDependentROI(mode=mode)

#####################################################################################################
# FINISHING UP
Done()    
#####################################################################################################

