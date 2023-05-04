#! /usr/bin/env python

import os,datetime,sys
if __name__=='__main__':
    now=datetime.datetime.now()
    EMIN=100

    TEST   = False
    GRBTEST='GRB080825C'
    orbits=0
    
    # FILTER
    FILTER='GRB'
    FLAVOR='FULL'
    #FLAVOR='DIFFUSE'
    
    #FLAVOR='QUICK'
    #FLAVOR='ENERGYDUR'    
    ALLOWED_FLAVORS=['FULL','FULL_P7T','DIFF','DIFF_F','DIFF_B','QUICK','VQUICK','ENERGYDUR','DETECTION','LATBA_P6_T','LATBA_P7_T','LATBA_P7_T_PHA','LATBA_P7_T_EXTENDED','LATBA_P7_S']
    
    OUTDIR=None

    LATBA={}
    BA=False
    EXECUTE=True
    RA=None
    DEC=None
    
    for ai,av in enumerate(sys.argv):
        if av=='-o': OUTDIR = sys.argv[ai+1]
        elif av=='-t':
            TEST=True
            GRBTEST = sys.argv[ai+1]
        elif av=='-tt':
            EXECUTE=False
        elif av=='-f':
            FILTER = sys.argv[ai+1]
        elif av=='-mode':
            FLAVOR=sys.argv[ai+1]
            if FLAVOR not in ALLOWED_FLAVORS:
                FLAVOR='FULL'
                print 'WARNING. %s not allowed, using %s' %(sys.argv[ai+1],FLAVOR)
                pass
            pass
        
        elif av=='-orbits':
            orbits = int(sys.argv[ai+1])
            pass
        
        elif av=='-ra':
            RA = float(sys.argv[ai+1])
            pass
        elif av=='-dec':
            DEC = float(sys.argv[ai+1])
            pass
        
        elif av=='-ba':
            try:
                BA=True
                LATBA['GRBTRIGGERDATE']   = sys.argv[ai+1]
                LATBA['GRBT05']           = sys.argv[ai+2]
                LATBA['GRBT90']           = sys.argv[ai+3]            
                LATBA['RA']               = sys.argv[ai+4]
                LATBA['DEC']              = sys.argv[ai+5]
                LATBA['ERR']              = sys.argv[ai+6]
                LATBA['PHAStart']         = sys.argv[ai+7]
                LATBA['PHAStop']          = sys.argv[ai+8]
                LATBA['LIKETSTART']        = sys.argv[ai+9]
                LATBA['LIKETSTOP']         = sys.argv[ai+10]
                print ' --- Running BA configuration --- '
                for x in LATBA.keys(): print '%20s=%10s' %(x,LATBA[x])
            except:
                print 'MET T05 T90 RA DEC ERR PHAStart PHAStop LIKETSTART LIKETSTOP'
                pass
            pass
        pass

    TIMESHIFT = (orbits*5733.0672)
    os.environ['TIMESHIFT']='%.4f' % TIMESHIFT
    print 'TIMESHIFT=%s' % os.environ['TIMESHIFT']
    BASEDIR = os.environ['BASEDIR']
    if OUTDIR is None:
        OUTDIR = '%s/DATA/%02i%02i%02i-%s-%s' %(BASEDIR,now.year-2000,now.month,now.day,FLAVOR.strip(),FILTER.strip())
        #OUTDIR = '%s/%02i%02i%02i-CAT-TEM-GAL0-DIFFUSE-R4d' %(BASEDIR,now.year-2000,now.month,now.day)
        #OUTDIR = '%s/DATA/%02i%02i%02i-CATALOG-LOG-DIFFUSE-ISO-GAL0' %(BASEDIR,now.year-2000,now.month,now.day)
        #OUTDIR = '%s/DATA/%02i%02i%02i-CATALOG-ENERGYDUR_WE_%s' %(BASEDIR,now.year-2000,now.month,now.day,EMIN)      
        pass
    if 'ENERGYDUR' in FLAVOR: OUTDIR+='_%s' % EMIN

    if orbits!=0: OUTDIR += '_ORB%i' %(orbits)
    if OUTDIR[0] is not '/': OUTDIR='%s/%s' %(BASEDIR,OUTDIR)

    print '--------------------------------------------------'
    print 'OUTDIR=',OUTDIR
    print 'TEST=',TEST
    print 'FILTER=',FILTER
    if TEST: print 'GRBTEST=',GRBTEST
    print 'FLAVOR =', FLAVOR 
    print '--------------------------------------------------'
    
    os.environ['OUTDIR'] = OUTDIR
    os.system('mkdir -p $OUTDIR')
    
    # Catalog Analysis.
    GeneralForAll = "FT1=None FT2=None TSTART=-20 TSTOP=300 BEFORE=600 AFTER=3600 EMIN=100 EMAX=100000 TSMIN=20 TSMIN_EXT=16 ULINDEX=-2.00 ZMAX=105 ROI=12 FEMIN=100 FEMAX=100000 "
    if RA is not None: GeneralForAll+='RA=%.4f ' %RA
    if DEC is not None: GeneralForAll+='DEC=%.4f ' %DEC
        
    # This is the default configuration, for reference.
    if FLAVOR=='FULL':
        General = GeneralForAll+"IRFS=\'P6_V3_TRANSIENT\' like_model=\'GRB+BKGE_CR_EGAL+GAL0\' like_timeBins=\'LOG,0.01,10000,48\' "

        tasks = {'PLOTANGULARSEPARATION':   1,
                 'CALCULATELATT90':         1,
                 'WEIGHBYEXPOSURE':         1,
                 'CROSSGTIS':               0,
                 'MAKESELECT':              1,
                 'MAKE_RSPGEN':             0,
                 'MAKE_ENERGYDEPENDENTROI': 1,
                 'UPDATE_POS':              0,
                 'MAKE_GBM_XSPECTUM':       0,
                 'MAKE_LAT_XSPECTRUM':      0,
                 'MAKE_BKGE_XSPECTRUM':     0,
                 'MAKELLE':                 1,
                 'COMPOSITELC':             1,
                 'MAKE_LIKE':               1,
                 'EXTENDED':                1,
                 'LIKEPHA':                 0,
                 'TSMAP':                   1}
        # --------------------------------------------------
    elif FLAVOR=='FULL_P7T':
        General = GeneralForAll+"IRFS=\'P7TRANSIENT_V6\' like_model=\'GRB+BKGE_CR_EGAL+GAL0\' like_timeBins=\'LOG,0.01,10000,48\' "
        
        tasks = {'PLOTANGULARSEPARATION':   1,
                 'CALCULATELATT90':         1,
                 'WEIGHBYEXPOSURE':         1,
                 'CROSSGTIS':               0,
                 'MAKESELECT':              1,
                 'MAKE_RSPGEN':             0,
                 'MAKE_ENERGYDEPENDENTROI': 1,
                 'UPDATE_POS':              0,
                 'MAKE_GBM_XSPECTUM':       0,
                 'MAKE_LAT_XSPECTRUM':      0,
                 'MAKE_BKGE_XSPECTRUM':     0,
                 'MAKELLE':                 1,
                 'COMPOSITELC':             1,
                 'MAKE_LIKE':               1,
                 'EXTENDED':                1,
                 'LIKEPHA':                 0,
                 'TSMAP':                   1}
        # --------------------------------------------------
    elif FLAVOR=='DIFF':
        General = GeneralForAll+"IRFS=\'P6_V3_DIFFUSE\' like_model=\'GRB+TEM+GAL0\' like_timeBins=\'LOG,0.01,100000,30\'"
        
        tasks = {'PLOTANGULARSEPARATION':   1,
                 'CALCULATELATT90':         0,
                 'WEIGHBYEXPOSURE':         1,
                 'CROSSGTIS':               0,
                 'MAKESELECT':              1,
                 'MAKE_RSPGEN':             0,
                 'MAKE_ENERGYDEPENDENTROI': 0,
                 'UPDATE_POS':              0,
                 'MAKE_GBM_XSPECTUM':       0,
                 'MAKE_LAT_XSPECTRUM':      0,
                 'MAKE_BKGE_XSPECTRUM':     0,
                 'MAKELLE':                 0,
                 'COMPOSITELC':             0,
                 'MAKE_LIKE':               1,
                 'EXTENDED':                1,
                 'LIKEPHA':                 0,
                 'TSMAP':                   1}
        # --------------------------------------------------
        
    elif FLAVOR=='DIFF_F':
        General = GeneralForAll+"IRFS=\'P6_V3_DIFFUSE::FRONT\' like_model=\'GRB+TEM+GAL0\' like_timeBins=\'LOG,0.01,100000,30\'"
        
        tasks = {'PLOTANGULARSEPARATION':   1,
                 'CALCULATELATT90':         0,
                 'WEIGHBYEXPOSURE':         1,
                 'CROSSGTIS':               0,
                 'MAKESELECT':              0,
                 'MAKE_RSPGEN':             0,
                 'MAKE_ENERGYDEPENDENTROI': 0,
                 'UPDATE_POS':              0,
                 'MAKE_GBM_XSPECTUM':       0,
                 'MAKE_LAT_XSPECTRUM':      0,
                 'MAKE_BKGE_XSPECTRUM':     0,
                 'MAKELLE':                 0,
                 'COMPOSITELC':             0,
                 'MAKE_LIKE':               1,
                 'EXTENDED':                1,
                 'LIKEPHA':                 0,
                 'TSMAP':                   1}
        # --------------------------------------------------
        
    elif FLAVOR=='DIFF_B':
        General = GeneralForAll+"IRFS=\'P6_V3_DIFFUSE::BACK\' like_model=\'GRB+TEM+GAL0\' like_timeBins=\'LOG,0.01,100000,30\'"
        
        tasks = {'PLOTANGULARSEPARATION':   1,
                 'CALCULATELATT90':         0,
                 'WEIGHBYEXPOSURE':         1,
                 'CROSSGTIS':               0,
                 'MAKESELECT':              0,
                 'MAKE_RSPGEN':             0,
                 'MAKE_ENERGYDEPENDENTROI': 0,
                 'UPDATE_POS':              0,
                 'MAKE_GBM_XSPECTUM':       0,
                 'MAKE_LAT_XSPECTRUM':      0,
                 'MAKE_BKGE_XSPECTRUM':     0,
                 'MAKELLE':                 0,
                 'COMPOSITELC':             0,
                 'MAKE_LIKE':               1,
                 'EXTENDED':                1,
                 'LIKEPHA':                 0,
                 'TSMAP':                   1}
        # --------------------------------------------------
    elif FLAVOR=='QUICK':
        #  Cutsom :    
        General = GeneralForAll+"IRFS=\'P6_V3_TRANSIENT\' TSTART=-20 TSTOP=300 like_model=\'GRB+BKGE_CR_EGAL+GAL0\' like_timeBins=\'LOG,0.01,10000,48\'"
        
        tasks = {'PLOTANGULARSEPARATION':   1,
                 'CALCULATELATT90':         0,
                 'WEIGHBYEXPOSURE':         1,
                 'CROSSGTIS':               0,
                 'MAKESELECT':              1,
                 'MAKE_RSPGEN':             0,
                 'MAKE_ENERGYDEPENDENTROI': 0, #1,
                 'UPDATE_POS':              0,
                 'MAKE_GBM_XSPECTUM':       0,
                 'MAKE_LAT_XSPECTRUM':      0,
                 'MAKE_BKGE_XSPECTRUM':     0,
                 'MAKELLE':                 1,
                 'COMPOSITELC':             0,
                 'MAKE_LIKE':               1,
                 'EXTENDED':                1,
                 'LIKEPHA':                 0,
                 'TSMAP':                   1}
        pass
    elif FLAVOR=='DETECTION':
        #  Cutsom :    
        General = GeneralForAll+"IRFS=\'P6_V3_TRANSIENT\' TSTART=-20 TSTOP=300 like_model=\'GRB+BKGE_CR_EGAL+GAL0\' like_timeBins=\'LOG,0.01,10000,48\'"
        
        tasks = {'PLOTANGULARSEPARATION':   1,
                 'CALCULATELATT90':         0,
                 'WEIGHBYEXPOSURE':         1,
                 'CROSSGTIS':               0,
                 'MAKESELECT':              1,
                 'MAKE_RSPGEN':             0,
                 'MAKE_ENERGYDEPENDENTROI': 0, #1,
                 'UPDATE_POS':              1,
                 'MAKE_GBM_XSPECTUM':       0,
                 'MAKE_LAT_XSPECTRUM':      0,
                 'MAKE_BKGE_XSPECTRUM':     0,
                 'MAKELLE':                 1,
                 'COMPOSITELC':             0,
                 'MAKE_LIKE':               1,
                 'EXTENDED':                1,
                 'LIKEPHA':                 0,
                 'TSMAP':                   1}
        pass
    elif FLAVOR=='LATBA_P6_T':
        General =GeneralForAll+"IRFS=\'P6_V3_TRANSIENT\' like_model=\'GRB+BKGE_CR_EGAL+GAL0\' like_timeBins=\'LOG,0.01,10000,48\'"
        tasks = {'PLOTANGULARSEPARATION':   1,
                 'CALCULATELATT90':         0,
                 'WEIGHBYEXPOSURE':         1,
                 'CROSSGTIS':               0,
                 'MAKESELECT':              1,
                 'MAKE_RSPGEN':             1,
                 'MAKE_ENERGYDEPENDENTROI': 1,
                 'UPDATE_POS':              1,
                 'MAKE_GBM_XSPECTUM':       0,
                 'MAKE_LAT_XSPECTRUM':      1,
                 'MAKE_BKGE_XSPECTRUM':     1,
                 'MAKELLE':                 1,
                 'COMPOSITELC':             0,
                 'MAKE_LIKE':               1,
                 'EXTENDED':                0,
                 'LIKEPHA':                 1,
                 'TSMAP':                   1}
        pass
    elif FLAVOR=='LATBA_P7_T':
        General = GeneralForAll+"IRFS=\'P7TRANSIENT_V6\' like_model=\'GRB+ISO+GAL0\' like_timeBins=\'LOG,0.01,10000,48\'"        
        tasks = {'PLOTANGULARSEPARATION':   1,
                 'CALCULATELATT90':         0,
                 'WEIGHBYEXPOSURE':         1,
                 'CROSSGTIS':               0,
                 'MAKESELECT':              1,
                 'MAKE_RSPGEN':             1,
                 'MAKE_ENERGYDEPENDENTROI': 1,
                 'UPDATE_POS':              1,
                 'MAKE_GBM_XSPECTUM':       0,
                 'MAKE_LAT_XSPECTRUM':      1,
                 'MAKE_BKGE_XSPECTRUM':     1,
                 'MAKELLE':                 1,
                 'COMPOSITELC':             0,
                 'MAKE_LIKE':               1,
                 'EXTENDED':                0,
                 'LIKEPHA':                 1,
                 'TSMAP':                   1}
        pass
    elif FLAVOR=='LATBA_P7_T_PHA':
        General = GeneralForAll+"IRFS=\'P7TRANSIENT_V6\' like_model=\'GRB+ISO+GAL0\' like_timeBins=\'LOG,0.01,10000,48\'"        
        tasks = {'PLOTANGULARSEPARATION':   0,
                 'CALCULATELATT90':         0,
                 'WEIGHBYEXPOSURE':         0,
                 'CROSSGTIS':               0,
                 'MAKESELECT':              1,
                 'MAKE_RSPGEN':             1,
                 'MAKE_ENERGYDEPENDENTROI': 1,
                 'UPDATE_POS':              0,
                 'MAKE_GBM_XSPECTUM':       0,
                 'MAKE_LAT_XSPECTRUM':      1,
                 'MAKE_BKGE_XSPECTRUM':     1,
                 'MAKELLE':                 0,
                 'COMPOSITELC':             0,
                 'MAKE_LIKE':               1,
                 'EXTENDED':                0,
                 'LIKEPHA':                 1,
                 'TSMAP':                   0}
        pass
    elif FLAVOR=='LATBA_P7_T_EXTENDED':
        General = GeneralForAll+"IRFS=\'P7TRANSIENT_V6\' like_model=\'GRB+ISO+GAL0\' like_timeBins=\'LOG,0.01,10000,48\'"        
        tasks = {'PLOTANGULARSEPARATION':   0,
                 'CALCULATELATT90':         0,
                 'WEIGHBYEXPOSURE':         0,
                 'CROSSGTIS':               0,
                 'MAKESELECT':              0,
                 'MAKE_RSPGEN':             0,
                 'MAKE_ENERGYDEPENDENTROI': 0,
                 'UPDATE_POS':              0,
                 'MAKE_GBM_XSPECTUM':       0,
                 'MAKE_LAT_XSPECTRUM':      0,
                 'MAKE_BKGE_XSPECTRUM':     0,
                 'MAKELLE':                 0,
                 'COMPOSITELC':             0,
                 'MAKE_LIKE':               0,
                 'EXTENDED':                1,
                 'LIKEPHA':                 0,
                 'TSMAP':                   0}
        pass
    elif FLAVOR=='LATBA_P7_S':
        General = GeneralForAll+"IRFS=\'P7SOURCE_V6\' like_model=\'GRB+ISO+GAL0\' like_timeBins=\'CONSTANT_TS,0.01,10000\'"        
        tasks = {'PLOTANGULARSEPARATION':   1,
                 'CALCULATELATT90':         0,
                 'WEIGHBYEXPOSURE':         1,
                 'CROSSGTIS':               0,
                 'MAKESELECT':              1,
                 'MAKE_RSPGEN':             1,
                 'MAKE_ENERGYDEPENDENTROI': 1, #1,
                 'UPDATE_POS':              1,
                 'MAKE_GBM_XSPECTUM':       0,
                 'MAKE_LAT_XSPECTRUM':      1,
                 'MAKE_BKGE_XSPECTRUM':     1,
                 'MAKELLE':                 1,
                 'COMPOSITELC':             0,
                 'MAKE_LIKE':               1,
                 'EXTENDED':                0,
                 'LIKEPHA':                 1,
                 'TSMAP':                   1}
        pass
    elif FLAVOR=='VQUICK':
        #  Cutsom :
        General = GeneralForAll+"IRFS=\'P6_V3_TRANSIENT\' like_model=\'GRB+ISO+GAL0\' like_timeBins=\'LOG,0.01,10000,48\'"
        
        tasks = {'PLOTANGULARSEPARATION':   1,
                 'CALCULATELATT90':         0,
                 'WEIGHBYEXPOSURE':         0,
                 'CROSSGTIS':               0,
                 'MAKESELECT':              0,
                 'MAKE_RSPGEN':             0,
                 'MAKE_ENERGYDEPENDENTROI': 0, #1,
                 'UPDATE_POS':              0,
                 'MAKE_GBM_XSPECTUM':       0,
                 'MAKE_LAT_XSPECTRUM':      0,
                 'MAKE_BKGE_XSPECTRUM':     0,
                 'MAKELLE':                 0,
                 'COMPOSITELC':             0,
                 'MAKE_LIKE':               1,
                 'EXTENDED':                1,
                 'LIKEPHA':                 0,
                 'TSMAP':                   1}
        pass
    elif FLAVOR=='ENERGYDUR':
        #  Cutsom :
        General = GeneralForAll.replace("EMIN=100","EMIN=%s" % EMIN)+"IRFS=\'P6_V3_TRANSIENT\'"
        tasks = {'PLOTANGULARSEPARATION':   0,
                 'CALCULATELATT90':         1,
                 'WEIGHBYEXPOSURE':         0,
                 'CROSSGTIS':               0,
                 'MAKESELECT':              0,
                 'MAKE_RSPGEN':             0,
                 'MAKE_ENERGYDEPENDENTROI': 0,
                 'UPDATE_POS':              0,
                 'MAKE_GBM_XSPECTUM':       0,
                 'MAKE_LAT_XSPECTRUM':      0,
                 'MAKE_BKGE_XSPECTRUM':     0,
                 'MAKELLE':                 0,
                 'COMPOSITELC':             0,
                 'MAKE_LIKE':               0,
                 'EXTENDED':                0,
                 'LIKEPHA':                 0,
                 'TSMAP':                   0}
        pass    
    else:
        exit()
        pass
    
    for t in tasks: General+=' %s=%d' %(t,tasks[t])
    QUEUE='xxl'
    
    subJob0  = 'submitJob.py -f %s -exe computeAll2 -q %s -r %s' %(FILTER,QUEUE,General)
    test     = 'gtgrb.py grbname=%s -nox -go -exe computeAll2 %s' % (GRBTEST,General)
    if BA:
        for x in LATBA: General+=' %s=%s' %(x,LATBA[x])
        subJob0  = 'submitJob.py -exe computeAll2 -q %s -r %s' %(QUEUE,General)
        test     = 'gtgrb.py -nox -go -exe computeAll2 %s' % (General)
        pass
    
    if TEST:
        if EXECUTE: os.system(test)
        else: print test
        pass
    else:
        if EXECUTE: 
            os.system(subJob0)        
            os.system('bjobs -P gtgrb')
        else:
            print subJob0
            pass
        pass
    pass

                                                                                                   
