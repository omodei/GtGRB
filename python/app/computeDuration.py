pfiles  = os.environ['PFILES']
cleanUp = False
Set(**ListToDict(sys.argv))
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
if results['CALCULATELATT90'].upper()=='Y':
    #try:            
    CalculateLATT90(emin=lat[0].Emin, emax=lat[0].Emax, overwrite=True,chatter=2)
    Print()
    #except:
    #    print '#--------------------------------------------------#'
    #    print '#   Not possible to compute duration using BKGE    #'
    #    print '#--------------------------------------------------#'
    #    pass
    pass

# ##################################################
# SELECT THE EVENTS FROM TSTART AND TSTOP AS SPECIFIED IN THE PAR FILE,
# CALCULATE MakeGtFindSrc AND CALCULATE PROBABILITY OF BEING GRB EVENT
# ##################################################

nevents = MakeSelect(mode=mode)
if nevents>0:
    MakeGtFindSrc(mode=mode)    
    # ComputeDuration()
    # ComputeKEYDuration()
    # ComputeProbabilities()
    ComputeBayesProbabilities()
    pass
Print()

##################################################
# MAKE LLE ANALYSIS
##################################################

Prompt(['MAKELLE'],mode)
if results['MAKELLE'].upper()=='Y':
    GetLLE()                                             # This will get the data.
    print 'Executing MakeLLELightCurves...'
    MakeLLELightCurves(**(ListToDict(sys.argv))) # Jack's code
    try:
        print 'LLE_DetMaxSign = %.2f ' % results['LLE_DetMaxSign']
        if results['LLE_DetMaxSign'] > 4.0:          # Pre Trial Probability in sigma
            tmpdict={'task':'duration'}
            tmpdict.update(ListToDict(sys.argv))        
            MakeLLELightCurves(**(tmpdict))          # Jack's code
            pass    
        print '--------------------------------------------------------------------\n'
    except:
        pass
    MakeLLEDetectionAndDuration() # Fred's Code
    Print()
    pass
Done(cleanUp)        
pass
