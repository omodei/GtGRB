#!/urs/bin/env python

print '***************************************************'
print ' GET THE GBM FILES '
print '***************************************************'
mydict=ListToDict(sys.argv)
Set(**mydict)
print mydict

ResultsFileName = ReadResults()

if ResultsFileName is None: remake = True
PlotAngularSeparation(mode=mode)
GetGBMFiles()
#GetLLE() # This will get the data.
Done() # Save and exit     
