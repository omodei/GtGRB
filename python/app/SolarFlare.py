pfiles  = os.environ['PFILES']
cleanUp = False

try:
    if os.environ['PIPELINE']=='YES':
        cleanUp=True
        pass
    pass
except:
    pass

# Sets all the parameters, and starts from sratch

Set(**ListToDict(sys.argv))
if mode=='go':
    EraseOutputDir()
    Set(**ListToDict(sys.argv))
    pass

GRBtheta = lat[0].getGRBTheta()
grbname  = grb[0].Name

print '--------------------------------------------------'
now=time.localtime()
print ' GTGRB EXECUTION STARTED %s-%s-%s %s-%s-%s' % (now[0],now[1],now[2],now[3],now[4],now[5])
print ' GRBNAME    = ',grbname
print ' PFILES     = ',pfiles
print ' PYTHONPATH = ',os.environ['PYTHONPATH']
print ' INDIR      = ',os.environ['INDIR']
print ' OUTDIR     = ',os.environ['OUTDIR']
try:
    print ' ROOTISBATCH= ',os.environ['ROOTISBATCH']
except:
    pass

chatter = 2

# -------------------------------------------------- #
# PLOT ANGULAR SEPARATION
PlotAngularSeparation(mode=mode)
Print()

# -------------------------------------------------- #
# CALCULATE THE GRB DURATION USING THE BKGE.
Prompt(['CALCULATELATT90'],mode)
if results['CALCULATELATT90']:
    #try:            
    CalculateLATT90(emin=lat[0].Emin, emax=lat[0].Emax, chatter=chatter)
    Print()
    #except:
    #    print '#--------------------------------------------------#'
    #    print '#   Not possible to compute duration using BKGE    #'
    #    print '#--------------------------------------------------#'
    #    pass
    pass

# -------------------------------------------------- #
# SELECT EVENTS IN DIFFERENT TIME DOMAINS,
# COMPUTE PHA1 and RSP FILES
# -------------------------------------------------- #
tstart = results['TSTART']
tstop  = results['TSTOP']
print tstart,tstop

nevents = MakeSelect(mode=mode,tstart=tstart,tstop=tstop,rspgen=True)
# THIS IS FOR THE LAT:
# if nevents>0: Make_PHA_RSP_Files(tstart=tstart,tstop=tstop)

# B) Find Position is from offset to duration:
# if MakeSelect(mode=mode,tstart=tstart,tstop=tstop): MakeGtFindSrc(mode=mode)

Print()

# ##################################################
# LIKELIHOOD ANALYSIS
# ##################################################
Prompt(['like_model'], mode)
if 'PREFIT' in results['like_model']:  MakeComputePreburstBackground(mode)

MakeLikelihoodAnalysis(mode   = mode,
                       tstart = tstart,
                       tstop  = tstop)

Print()
Done(cleanUp)
