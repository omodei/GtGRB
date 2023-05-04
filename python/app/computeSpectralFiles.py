print '***************************************************'
print 'Running test sequence... '
print ' GRBNAME: %s, Mode: %s' % (grbname, mode)
print '***************************************************'
mydict = ListToDict(sys.argv)
# This set up the GRB
Set(**mydict)
#
baseDir = '%s/%s' % (os.environ['OUTDIR'],grb[0].Name)
results_fileName='%s/results_%s.txt' % (baseDir,grb[0].Name)
# -------------------------------------------------- #
try:    ReadResults(results_fileName) # This reads the stored results.
except: pass
# ------------------------------------------------------ #
Print()
# ------------------------------------------------------ #
try: FLAT_ROI    = bool(results['FLAT_ROI'])
except: FLAT_ROI = False

try:    tstart=results['PHAstart']
except: tstart = results['GBMT05']

try:    tstop=results['PHAstop']
except: tstop  = results['GBMT95']    

try:    flat_roi = results['FLAT_ROI']
except: flat_roi = 1

try:    gbm_spectra = results['GBM_SPECTRA']
except: gbm_spectra = 0

try:    bkge        = results['BKGE']
except: bkge        = 0


MakeLATSpectra(tstart=tstart,tstop=tstop,flat_roi=flat_roi,bkge=bkge)
if gbm_spectra:    
  GetGBMFiles()
  MakeGBMSpectra(tstart=tstart,tstop=tstop,mode='go')



'''
# THIS IS FOR THE LAT:
# ENERGY DEPENDENT ROI:

MakeLATSpectra()

nevents = MakeSelectEnergyDependentROI(mode=mode,tstart=tstart,tstop=tstop,rspgen=True)    
# MakePHA_RSP_Files(tstart=tstart,tstop=tstop)

#THIS PRODUCES ENERGY DEPENDENT ROI BACKGROUND:
Make_BKG_PHA(start=tstart,stop=tstop)

##################################################
# THIS IS FOR THE LAT:
# ENERGY INDEPENDENT ROI:

nevents = MakeSelect(mode=mode,tstart=tstart,tstop=tstop,rspgen=True)    
# MakePHA_RSP_Files(tstart=tstart,tstop=tstop)

#THIS PRODUCES ENERGY DEPENDENT ROI BACKGROUND:
Make_BKG_PHA(flat_roi=1,start=tstart,stop=tstop)


# This is for the GBM:
MakeGBMSpectra(tstart=tstart,tstop=tstop)
'''

# FINISHING UP
Done()

