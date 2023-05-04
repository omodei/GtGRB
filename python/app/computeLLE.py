print '***************************************************'
print ' COMPUTING THE LLE LIGHT CURVES...'
print '***************************************************'
mydict=ListToDict(sys.argv)
Set(**mydict)
timeShift = 0.0 #-2.0 * 5733.0672

GRBtheta = lat[0].getGRBTheta()
grbname  = grb[0].Name
irfs     = lat[0]._ResponseFunction

print 'Theta of the bursts: %.2f ' % GRBtheta
if timeShift!=0:
    dirToRemove = '%s/%s' % (os.environ['OUTDIR'],grbname)
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

try:    IGNORE_THETA = bool(float(results['IGNORE_THETA']))
except: IGNORE_THETA = False
print ' &IGNORE_THETA = ',IGNORE_THETA
if GRBtheta < 89.0 or IGNORE_THETA:
    #ResultsFileName = ReadResults()
    PlotAngularSeparation(mode=mode)
    # ------------------------------------------------------ #
    import makeLLE
    LLE_VERSION=1
    if 'P8' in irfs: 
        os.environ['LLEIFILE'] ='/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-10-00-02/makeLLEproducts/python/config_LLE_DRM/Pass8.txt'
        os.environ['MCBASEDIR']='/MC-Tasks/ServiceChallenge/GRBSimulator-Pass8'
    else:
        os.environ['LLEIFILE'] ='/afs/slac/g/glast/groups/grb/SOFTWARE/GRBAnalysis_ScienceTools-10-00-02/makeLLEproducts/python/config_LLE_DRM/Pass7.txt'
        os.environ['MCBASEDIR']='/MC-Tasks/ServiceChallenge/GRBSimulator-Pass7'
        pass
    output_ez= os.environ['OUTDIR']
    OBJECT   = results['GRBNAME']
    GRBMET   = float(results['GRBMET'])
    GRB_RA   = float(results['RA'])
    GRB_DEC  = float(results['DEC'])
    FT2      = lat[0].FilenameFT2
    GBMT05   = float(results['GBMT05'])
    GBMT95   = float(results['GBMT95'])
    GRBTHETA    = float(results['THETA'])
    GRBZENITH   = float(results['ZENITH'])

    LLE_results=makeLLE.do(outdir  = output_ez,
                           version = LLE_VERSION,
                           ttime   = GRBMET,
                           tstart  = GBMT05,
                           tstop   = GBMT95,
                           ra      = GRB_RA,              
                           dec     = GRB_DEC,
                           deltat  = 1.0,
                           name    = OBJECT,
                           zmax    = min(115,GRBZENITH+20),
                           thetamax= GRBTHETA+20,
                           radius  = -1,
                           ignore_theta=1,
                           before=1000,
                           after=1000,
                           clobber=1,
                           lle=1,drm=0,detect=1,
                           regenerate_after_detection=1)
    
    for k in LLE_results.keys():   results[k]=LLE_results[k]
    

    output_dir_version='%(output_ez)s/%(OBJECT)s/v%(LLE_VERSION)02d' % locals()
    output_lle_filename='%(output_dir_version)s/gll_lle_bn%(OBJECT)s_v%(LLE_VERSION)02d.fit' % locals()
    output_lc_filename=output_lle_filename.replace('.fit','.png')

    #if not os.path.exists(output_lle_filename):
    #    makeLLE.GenerateLLE(output_ez,version,OBJECT,TRIGTIME, RA_OBJ,DEC_OBJ,T90,
    #                        mode=['pha','forReal'])        
    #    pass
    #makeLLE.ComputeLLEDetection(output_ez,version,OBJECT,FT2,RA_OBJ,DEC_OBJ,TRIGTIME,NSIGMA=4.0)
    #cmd_cp = 'cp %(FT2)s %(output_dir_version)s/gll_pt_bn%(OBJECT)s_v%(version)02d.fit' %locals()
    #print cmd_cp
    #os.system(cmd_cp)
    LCTSTART =-20
    LCTSTOP  = 290
    DT       = 1.0
    if GBMT95-GBMT05<2.0:
        LCTSTART = -2
        LCTSTOP  = 29
        DT       = 0.25
        pass
    import scripts.CompositeLightCurve_MPL as CLC
    LC=CLC.CompositeLC(GRBMET,TMIN=LCTSTART,TMAX=LCTSTOP,DT=DT)
    LC.SetLLE1([output_lle_filename],0,100)
    LC.SetLLE2([output_lle_filename],100,10000)
    LC.SetOutput(output_lc_filename)
    LC.Plot()
    print 'PNG output file = ' ,  output_lc_filename
else:
    print '%%%%%%%%%%%%%%%%%%%%%%%% GRB %s is out of the FOV: Theta = %s ' % (grb[0].Name,GRBtheta)
    pass
Done()
