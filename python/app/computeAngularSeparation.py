print '***************************************************'
print ' COMPUTE THE ANGULAR SEPARATION'
Set(**ListToDict(sys.argv))
grbname  = grb[0].Name
print ' GRBNAME: %s, Mode: %s' % (grbname, mode)
print '***************************************************'
# This reads the stored results. overw=1: over write the "Set" variables with the stored results.
ReadResults()
PlotAngularSeparation(mode=mode)
Print()
