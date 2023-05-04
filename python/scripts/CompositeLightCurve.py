#!/usr/bin/env python

import sys, os, glob
from GTGRB.genutils import runShellCommand

_base=os.environ['OUTDIR']

def readResults(results):
    fin=file(results,'r')
    lines=fin.readlines()
    xxx={}
    for l in lines:
        if '#' not in l:
            par = l.split('=')[0].strip()
            val = l.split('=')[1].strip()
            xxx[par]=val
            pass
        pass
    return xxx

def updateResults(results):
    return 
    

def SetupFiles(grbname,data_arr):
    files = []
    for data in data_arr:
        filepath = glob.glob('%s/%s/%s*.root'%(_base,grbname,data))
        if len(filepath)>0:
            files+=filepath
        else:
            filepath=glob.glob('%s/%s/%s*_%s*.root'%(_base,grbname,grbname,data))
            if len(filepath)>0:
                files+=filepath
                pass
            pass
        pass    
    return files
    
def AddVerticalLine(xxx,var,col):
    val = -666
    try:
        val = float(xxx[var])
    except:
        pass
    print ' | Adding a vertical line %10s at %10.2f |' %(var,val)
    
    return (val,col)

    
def makeCompositeLightCurve(grbname,
                            DT=0.0,
                            BKGSUB=0,
                            XMIN=0,
                            XMAX=0,
                            TMIN=-20,
                            TMAX=300, # Total window                            
                            NAIDETLIST=['n'],
                            BGODETLIST=['b'],
                            YMAX={},
                            YMIN={},
                            LAT1=0,
                            LAT2=0,
                            LAT3=0,
                            LAT4=0):
    
    results=os.path.join(_base,grbname,'results_%s.txt'%grbname)
    if os.path.exists(results):
        xxx           = readResults(results)
    else:
        print 'Use Print() to dump %s first.'%results
        return
    
    t0            = float(xxx['GRBTRIGGERDATE'])
            
    (gbm_t05,col_gbm_t05)       = AddVerticalLine(xxx,'GBMT05','g')    
    (gbm_t95,col_gbm_t95)       = AddVerticalLine(xxx,'GBMT95','g')
    gbm_t90       = gbm_t95 - gbm_t05
    
    (bkge_t05,col_bkge_t05)      = AddVerticalLine(xxx,'BKGET05','b')
    (bkge_t95,col_bkge_t95)      = AddVerticalLine(xxx,'BKGET95','b')
    
    bkge_t90      = bkge_t95 - bkge_t05

    duration      = gbm_t90

    
    print '***************************************************'
    print 'SET DURATION: %s (GBM=%.1f BKGE=%.1f )                     ' % (duration, gbm_t90, bkge_t90)
    print '***************************************************'
    
    
    #duration      = max(duration,bkge_t95)
    # else:
    # duration=gbm_t90
    # pass
    
    ra            = float(xxx['RA'])
    dec           = float(xxx['DEC'])
    try:
        n_evt         = float(xxx['NumberOfEvents_T_ROI_E'])
    except:
        n_evt         = 0
        pass
    
    nais          = SetupFiles(grbname,NAIDETLIST)
    bgos          = SetupFiles(grbname,BGODETLIST)

    ######################
    # TRY THE NEW SKEMA:
    LAT=[]
    if 'use_in_composite' in xxx.keys():
        selected_lat_file=xxx['use_in_composite']
        if os.path.exists(selected_lat_file): LAT.append(selected_lat_file)
        pass
    
    if len(LAT)==0: LAT           = SetupFiles(grbname,['_ROI/*_LAT_ROI'])
    
    '''
    LAT           = SetupFiles(grbname,['gtsrcprob_extended'])
    
    if len(LAT)==0: LAT           = SetupFiles(grbname,['*_gtsrcprob_LIKE_BKGE'])
    if len(LAT)==0: LAT           = SetupFiles(grbname,['*_gtsrcprob_LIKE_GBM'])
    if len(LAT)==0: LAT           = SetupFiles(grbname,['_ROI_E/*_LAT_ROI_E'])
    if len(LAT)==0: LAT           = SetupFiles(grbname,['_ROI/*_LAT_ROI'])
    if len(LAT)==0: LAT           = SetupFiles(grbname,['*_LAT_ROI'])
    '''
    
    MERIT    = SetupFiles(grbname,['lle_events'])
    LLEDETDUR     = glob.glob('%s/%s/GRB%s_LLEdetdur.root'%(_base,grbname,grbname))
    #if len(LLEDETDUR)>0: MERIT=''
    print '--------------------------------------------------'
    print 'MERIT: %s ' % MERIT
    print 'LLEDETDUR: %s ' % LLEDETDUR
    n_evt=0
    if len(LAT)>0:
        import ROOT
        TF=ROOT.TFile(LAT[0],'OPEN')
        TT=TF.Get("Events")
        n_evt = TT.GetEntries("TIME>%s && TIME<%s" %(t0+XMIN,t0+XMAX))
        TF.Close()
        pass
    
    if n_evt>0: print 'LAT:%s (%d between %f-%f)' % (LAT[0],n_evt,XMIN,XMAX)
    else:
        print ' NO LAT EVENTS SELECTED BETWEEN %f-%f' % (XMIN,XMAX)        
        LAT=[]
        pass
    print '--------------------------------------------------'
    #print LAT1,LAT2,LAT3,LAT4
    splitNaI=1
    panels=0
    if len(nais)>0 :
        panels+=1
        if splitNaI: panels+=1
        pass
    if len(bgos)>0 :
        panels+=1
        pass
    if len(LAT)>0  :
        panels+=1
        pass
    if len(MERIT)>0 or len(LLEDETDUR)>0:
        panels+=1
        pass

    for l in (LAT1,LAT2,LAT3,LAT4):
        if l>0:  panels+=1
        pass
    
    
    if DT==0:
        if n_evt>100:
            if duration<5:            
                DT = 0.01
            elif duration > 100:
                DT = 0.25
            else:
                DT = 0.1
                pass
            pass
        else:
            if duration<5:            
                DT = 0.1
            elif duration > 100:
                DT = 0.5
            else:
                DT = 0.25
                pass
            pass
        pass
    elif DT<0:
        DT = duration/220.
        pass
    
    
    labels=[]
    labeltypes=[]
    #labels.append(duration)
    #for vtx in [AddVerticalLine(xxx,'LIKE_AG_gtsrcprob_Tmax'),gbm_t05,gbm_t95,bkge_t05,bkge_t95]:
    #    if vtx > XMIN and vtx < XMAX: labels.append(vtx)
    #    pass

    
    print '====> XMIN,XMAX:',XMIN,XMAX
    for (vtx,col) in [AddVerticalLine(xxx,'LIKE_GBM_gtsrcprob_Tmax','m'),
                      AddVerticalLine(xxx,'gtsrcprob_ExtendedEmission_MAXE_T','b'),
                      AddVerticalLine(xxx,'GBMT05','g'),    
                      AddVerticalLine(xxx,'GBMT95','g')]:        
        if vtx > XMIN and vtx < XMAX:
            labels.append(vtx)
            labeltypes.append(col)
            pass
        pass
    #print 'LABELS:',labels
    #print ' TYPES:',labeltypes
    
    if (duration < 6.):
        xmin = -1
        xmax = 10.
    elif (duration < 60.): 
        xmin = -10.
        xmax = 100.
    else:
        xmin = -20.
        xmax = 200.
        pass
    
    if XMAX>XMIN:
        xmax = XMAX
        xmin = XMIN
        pass
    
    tmin = TMIN
    tmax = TMAX
    
    #xmin = max(-20.,-duration/2.)
    #xmax = 2.0*duration

    #import pdb;pdb.set_trace()
    panel=1
    
    txt="""
# #################################################
# Configuration file for making nice composite light curves
# Nicola Omodei: nicola.omodei@gmail.com
# #################################################
T0  :=  %s

LABELS     := %s
LABELTYPE  := %s
DT         := %s 
TMIN       := %s
TMAX       := %s
XMIN       := %s
XMAX       := %s
GRBTMIN    := 0
GRBTMAX    := %s
##################################################
PANELS := %s
##################################################
""" %(t0,labels,labeltypes,DT, tmin,tmax,xmin,xmax,duration,panels)
    NaI1=3
    NaI2=15
    NaI3=81

    if len(nais)>0 and splitNaI:
        txt=txt+"""
        FILES%(panel)s   := %(nais)s
        LABEL%(panel)s   := GRB%(grbname)s \\n NaI (8 keV -- 20 keV)
        CUT%(panel)s     := PHA > %(NaI1)d  && PHA < %(NaI2)d
        INSERT%(panel)s  := 0
        BKGSUB%(panel)s  := %(BKGSUB)i
        TREE%(panel)s    := Events
        TIME%(panel)s    := TIME
        COUNTS%(panel)s  := PHA
        """ % locals()
        if 'YMAX%d'%panel in YMAX.keys(): txt+='YMAX%d := %f \n' % (panel,float(YMAX['YMAX%d' % panel]))
        if 'YMIN%d'%panel in YMIN.keys(): txt+='YMIN%d := %f \n' % (panel,float(YMIN['YMIN%d' % panel]))
        panel+=1
        
        txt=txt+"""
        FILES%(panel)s   := %(nais)s
        LABEL%(panel)s   := GRB%(grbname)s \\n NaI (20 keV -- 250 keV)
        CUT%(panel)s     := PHA > %(NaI2)d  && PHA < %(NaI3)d
        INSERT%(panel)s  := 0
        BKGSUB%(panel)s  := %(BKGSUB)i
        TREE%(panel)s    := Events
        TIME%(panel)s    := TIME
        COUNTS%(panel)s  := PHA
        """ % locals()
        if 'YMAX%d'%panel in YMAX.keys(): txt+='YMAX%d := %f \n' % (panel,float(YMAX['YMAX%d' % panel]))
        if 'YMIN%d'%panel in YMIN.keys(): txt+='YMIN%d := %f \n' % (panel,float(YMIN['YMIN%d' % panel]))
        panel+=1
        pass
            

    if len(nais)>0 and not splitNaI:
        txt=txt+"""
        FILES%(panel)s   := %(nais)s
        LABEL%(panel)s   := GRB%(grbname)s \\n NaI (7 keV -- 250 keV)
        CUT%(panel)s     := PHA > %(NaI1)d  && PHA < %(NaI3)d     
        INSERT%(panel)s  := 0
        BKGSUB%(panel)s  := %(BKGSUB)i
        TREE%(panel)s    := Events
        TIME%(panel)s    := TIME
        COUNTS%(panel)s  := PHA
        """ % locals()
        if 'YMAX%d'%panel in YMAX.keys(): txt+='YMAX%d := %f \n' % (panel,float(YMAX['YMAX%d' % panel]))
        if 'YMIN%d'%panel in YMIN.keys(): txt+='YMIN%d := %f \n' % (panel,float(YMIN['YMIN%d' % panel]))
        panel+=1
        pass
    
    if len(bgos)>0:
        txt=txt+"""
        ##################################################
        FILES%(panel)s   := %(bgos)s
        LABEL%(panel)s   := BGO (200 keV -- 5 MeV)
        CUT%(panel)s     := PHA > 2  && PHA < 67
        INSERT%(panel)s  := 0
        BKGSUB%(panel)s  := %(BKGSUB)i
        TREE%(panel)s    := Events
        TIME%(panel)s    := TIME
        COUNTS%(panel)s  := PHA
        """ % locals()
        if 'YMAX%d'%panel in YMAX.keys(): txt+='YMAX%d := %f \n' % (panel,float(YMAX['YMAX%d' % panel]))
        if 'YMIN%d'%panel in YMIN.keys(): txt+='YMIN%d := %f \n' % (panel,float(YMIN['YMIN%d' % panel]))
        panel+=1
        pass
    if len(MERIT)>0:
        txt=txt+"""
        ##################################################
        FILES%(panel)s   := %(MERIT)s
        LABEL%(panel)s   := LATLLE > 10 MeV
        CUT%(panel)s     := (selection==1 || selection==3) && EvtEnergyCorr>10
        INSERT%(panel)s  := 0
        BKGSUB%(panel)s  := %(BKGSUB)i
        TREE%(panel)s    := LLETuple
        TIME%(panel)s    := EvtElapsedTime
        COUNTS%(panel)s  := EvtEnergyCorr
        """ % locals()
        if 'YMAX%d'%panel in YMAX.keys(): txt+='YMAX%d := %f \n' % (panel,float(YMAX['YMAX%d' % panel]))
        if 'YMIN%d'%panel in YMIN.keys(): txt+='YMIN%d := %f \n' % (panel,float(YMIN['YMIN%d' % panel]))
        panel+=1
        pass
    for l in (LAT1,LAT2,LAT3,LAT4):
        if l>0:
            txt=txt+"""
            ##################################################
            FILES%(panel)s   := %(LAT)s
            LABEL%(panel)s   := LAT
            CUT%(panel)s     := ENERGY>%(l)f
            INSERT%(panel)s  := 0
            BKGSUB%(panel)s  := 0
            TREE%(panel)s    := Events
            TIME%(panel)s    := TIME
            COUNTS%(panel)s  := ENERGY
            """ % locals()
            if 'YMAX%d'%panel in YMAX.keys(): txt+='YMAX%d := %f \n' % (panel,float(YMAX['YMAX%d' % panel]))
            if 'YMIN%d'%panel in YMIN.keys(): txt+='YMIN%d := %f \n' % (panel,float(YMIN['YMIN%d' % panel]))
            panel+=1
            pass        
        pass
    if len(LAT)>0:
        txt=txt+"""
        ##################################################
        FILES%(panel)s   := %(LAT)s
        LABEL%(panel)s   := LAT
        CUT%(panel)s     := 100
        INSERT%(panel)s  := 0
        BKGSUB%(panel)s  := 0
        TREE%(panel)s    := Events
        TIME%(panel)s    := TIME
        COUNTS%(panel)s  := ENERGY
        EVENTS%(panel)s  := 1        
        """ % locals()
        if 'YMAX%d'%panel in YMAX.keys(): txt+='YMAX%d := %f \n' % (panel,float(YMAX['YMAX%d' % panel]))
        if 'YMIN%d'%panel in YMIN.keys(): txt+='YMIN%d := %f \n' % (panel,float(YMIN['YMIN%d' % panel]))
        pass        
    print txt
    return txt

if __name__=='__main__':
    print '*--------------------------------------------------------------------*' 
    print '| Create configuration file for Pretty Light Curve generation       |'
    print '| options are :                                                      |'
    print '|      -txt: Create the configuration files                          |'
    print '|      -exe: submit jobs to the pipeline                             |'
    print '| You can also individually run the LC using runLC.py LC_myBurst.txt |'
    print '| Comments, Questions, Suggestions: nicola.omodei@slac.stanford.edu  |'    
    print '*--------------------------------------------------------------------*'

    
    grbname='';dt=1;bksub=0;xmin=-100;xmax=500;tmin=-20;tmax=300;nai=['n'];bgo=['b'];
    make_txt = 0
    make_exe = 1
    lat1 =0
    lat2 =0
    lat3 =0
    lat4 =0
    
    YMIN={}
    YMAX={}

    for key,value in enumerate(sys.argv):
        if value.lower() == 'grbname': grbname = sys.argv[key+1]
        elif value.lower() == 'dt':    dt      = float(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'bksub': bksub   = int(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'xmin':  xmin    = float(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'xmax':  xmax    = float(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'tmin':  tmin    = float(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'tmax':  tmax    = float(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymin1':  YMIN['YMIN1'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymax1':  YMAX['YMAX1'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymin2':  YMIN['YMIN2'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymax2':  YMAX['YMAX2'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymin3':  YMIN['YMIN3'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymax3':  YMAX['YMAX3'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymin4':  YMIN['YMIN4'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymax4':  YMAX['YMAX4'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymin5':  YMIN['YMIN5'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymax5':  YMAX['YMAX5'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymin6':  YMIN['YMIN6'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymax6':  YMAX['YMAX6'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymin7':  YMIN['YMIN7'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymax7':  YMAX['YMAX7'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymin8':  YMIN['YMIN8'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'ymax8':  YMAX['YMAX8'] = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'nai':   nai     = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'bgo':   bgo     = eval(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'txt':   make_txt     = int(sys.argv[key+1])
        elif value.lower() == 'exe':   make_exe     = int(sys.argv[key+1])
        elif value.lower() == 'lat1':  lat1=float(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'lat2':  lat2=float(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'lat3':  lat3=float(sys.argv[key+1]); make_txt=1
        elif value.lower() == 'lat4':  lat4=float(sys.argv[key+1]); make_txt=1
        
        else: print 'value %s not recognize. Ignored.' % key
        pass
    if grbname=='': ' *** You must provide a valid GRB name! *** '
    
    foutn = 'LC_%s.txt'% (grbname)

    if make_txt:
        fout=file(foutn,'w')
        txt = makeCompositeLightCurve(grbname,
                                      DT=dt,
                                      BKGSUB=bksub,
                                      XMIN=xmin,
                                      XMAX=xmax,
                                      TMIN=tmin,
                                      TMAX=tmax, # Total window                            
                                      NAIDETLIST=nai,
                                      BGODETLIST=bgo,
                                      YMAX=YMAX,
                                      YMIN=YMIN,
                                      LAT1=lat1,
                                      LAT2=lat2,
                                      LAT3=lat3,
                                      LAT4=lat4)
        fout.write(txt)
        fout.close()
        
        pass
    if make_exe:
        runShellCommand('$COMPOSITELC_DIR/runLC.py %s' % foutn)
        pass
    
    
