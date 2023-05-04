print '***************************************************'
print ' SELECT EVENTS, MAKING LAT LIGHTCURVE and SKYMAP...'
mydict=ListToDict(sys.argv)
Set(**mydict)

##################################################
try:
    timeShift = float(os.environ['TIMESHIFT']) #=-2.0 * 5733.0672 = 11466.1344)
except:
    timeShift=0
    pass

if timeShift!=0:
    dirToRemove = '%s/%s' % (os.environ['OUTDIR'],grb[0].Name)
    NewtriggerTime = grb[0].Ttrigger+timeShift
    SetVar('GRBTRIGGERDATE',NewtriggerTime)
    SetGRB()
    GRBtheta = lat[0].getGRBTheta()
    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
    print ' WARNING!!!! The trigger time has changed            '
    print ' New Theta of the bursts: %.2f ' % GRBtheta
    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
    print 'removing: %s ' % dirToRemove
    os.system('rm -rf %s' % dirToRemove)
    pass
else:                                               
    if mode=='go':
        EraseOutputDir()
        Set(**ListToDict(sys.argv))
        pass
    pass

GRBtheta = lat[0].getGRBTheta()
grbname  = grb[0].Name

print ' GRBNAME: %s, THETA: %.1f s, Mode: %s' % (grbname, GRBtheta, mode)
print '***************************************************'

ResultsFileName = ReadResults()

# ------- #
GBMT05 = results['GBMT05']
GBMT95 = results['GBMT95']
GRBT05 = results['GRBT05']
GRBT95 = results['GRBT95']

bins={'_BKGE' :(GRBT05,GRBT95),
      '_GBM'  :(GBMT05,GBMT95),
      '_PRE'  :(min(GBMT05,GRBT05),max(GBMT05,GRBT05)),
      '_JOINT':(max(GBMT05,GRBT05),min(GBMT95,GRBT95)),
      '_EXT'  :(min(GBMT95,GRBT95),max(GBMT95,GRBT95))}


if 'TSTART' in mydict.keys():
    GRBT05 = mydict['TSTART']
    GBMT05 = GRBT05
    bins={}
    pass

if 'TSTOP' in mydict.keys():
    GRBT95 = mydict['TSTOP']
    GBMT95 = GRBT95
    bins={}
    pass

for suff in bins.keys():
    t0  = bins[suff][0]
    t1  = bins[suff][1]
    if t0>t1 :
        # --- Energy Dependent ROI:
        # MakeSelectEnergyDependentROI(mode=mode,tstart=tstart,tstop=tstop,suffix='_GBM_ROIE')
        # --- Simple ROI:
        nevents = MakeSelect(mode=mode,tstart=t0,tstop=t1,suffix=suff, plot=False)
        pass
    pass

# SELECT THE EVENTS FROM TSTART AND TSTOP AS SPECIFIED IN THE PAR FILE,
# CALCULATE MakeGtFindSrc AND CALCULATE PROBABILITY OF BEING GRB EVENT

# A) PROBABILITIES ARE FROM TMIN - TMAX:
TMIN = -20.0
TMAX = 1.0e4

if MakeSelect(mode=mode,tstart=TMIN,tstop=TMAX,plot=False)>0: ComputeBayesProbabilities()

# B) Find Position is from offset to duration:
if MakeSelect(mode=mode,tstart=GRBT05,tstop=GRBT95,plot=False)>0: MakeGtFindSrc(mode=mode)

#####################################################################################################
# This makes the last selection from TSTART - TSTOP and it saves in the directory _ROI

MakeSelect()

#####################################################################################################
# FINISHING UP

Done()    

#####################################################################################################

