import astropy.io.fits as pyfits
import ROOT
import sys,os
import math
import numpy

import genutils
from genutils import runShellCommand

def AppendEventProbability(fitsFileName,probFileName=None):
    verbose=0
    new_fitsFile   = fitsFileName.replace('.fits','_p.fits')
    new_fitsFile_2 = fitsFileName.replace('.fits','_p2.fits')
    for x in (new_fitsFile,new_fitsFile_2):     runShellCommand('rm -f %s' %x)
    
    #infile,s,a,"DATA/120229-FULL-GRB/110709642/_ROI/110709642_LAT_ROI_-20.00_300.00.fits[EVENTS]",,,"Name of FITS file and [ext#]"
    #outfile,s,a,"ss.fits",,,"Name of output FITS file"
    #clname,s,a,"SRC_PROBABILITY",,,"Resultant column name"
    #expr,s,a,"0",,,"Arithmetic expression"
    #anull,s,h,,,,"Null string for ASCII table columns"
    #inull,i,h,0,,,"Null value for integer column (0=no nulls)"
    #copycol,b,h,yes,,,"Copy all columns in table"
    #histkw,b,h,yes,,,"Print a history keyword"
    #copyall,b,h,yes,,,"Copy all other extensions?"
    #rowrange,s,h,"-",,,"Row ranges to operate on"
    #tform,s,h,,,,"TFORM value for output column"
    #clobber,b,h,no,,,"Overwrite existing output file?"
    #mode,s,h,"ql",,,""
    
    runShellCommand('fcalc infile=%s[EVENTS] expr=0.0 clname=SRC_PROBABILITY outfile=%s' % (fitsFileName,new_fitsFile))
    fitsFile = pyfits.open(new_fitsFile)

    events   = fitsFile['EVENTS']
    N=events.header['NAXIS2']
    EVENT_ID = events.data.field('EVENT_ID')    
    RUN_ID   = events.data.field('RUN_ID')
    TIME     = events.data.field('TIME')

    if probFileName is not None:    
        probFile          = pyfits.open(probFileName)
        events_p          = probFile['EVENTS']
        EVENT_ID_p        = events_p.data.field('EVENT_ID')
        RUN_ID_p          = events_p.data.field('RUN_ID')
        SRC_PROBABILITY_p = events_p.data.field('GRB') #SRC_PROBABILITY')
        N_p               = events_p.header['NAXIS2']
    else:
        SRC_PROBABILITY_p = None
        pass
    
    SRC_PROBABILITY = events.data.field('SRC_PROBABILITY')
    
    x = 0
    for i in range(N):
        x = 0
        lookup = 1
        SRC_PROBABILITY[i] = 0.0
        if SRC_PROBABILITY_p is not None:
            while (lookup and x < N_p):
                #print EVENT_ID[i],EVENT_ID_p[x],RUN_ID[i],RUN_ID_p[x], EVENT_ID[i] == EVENT_ID_p[x],RUN_ID[i]==RUN_ID_p[x],SRC_PROBABILITY_p[x]
                if EVENT_ID[i] == EVENT_ID_p[x] and RUN_ID[i]==RUN_ID_p[x]:
                    SRC_PROBABILITY[i] = SRC_PROBABILITY_p[x]
                    lookup=0
                    pass
                x+=1
                pass
            pass
        else:
            SRC_PROBABILITY[i]=0.0
            pass
        if verbose: print '-->', x,i, EVENT_ID[i],RUN_ID[i],TIME[i],SRC_PROBABILITY[i]
        pass
    fitsFile.writeto(new_fitsFile_2)
    runShellCommand('mv %s %s' %(new_fitsFile_2,fitsFileName))
    runShellCommand('rm -f %s' % new_fitsFile)
    if verbose: print fitsFileName,' -> wrote'
    return fitsFileName


def GetEventClass(ClassName):
    ''' THIS ASSUMES:
    0 = TRANSEINT
    1 = SOURCE
    2 = DIFFUSE
    3 = CLEAN
    4 = S3 (ONLY PASS7)
    FOR BOTH PASS6 and PASS7
    '''
    def a2b(X):
        N=len(X)
        y=0
        for i,x in enumerate(X):
            y+=x*2**(N-i-1)
            pass
        return int(y)

    def p6(X): return X
    def p7(X):
        ultraClean = (X>>4 & 0x1)
        Clean      = (X>>3 & 0x1)*((X>>4 & 0x1)==False)
        Source     = (X>>2 & 0x1)*((X>>3 & 0x1)==False)*((X>>4 & 0x1)==False)
        Transient  = (X>>0 & 0x1)*((X>>2 & 0x1)==False)*((X>>3 & 0x1)==False)*((X>>4 & 0x1)==False)
        return     Transient + Source*2 + Clean*3 + ultraClean*4
    def p8(X):
        X=a2b(X)
        ultraClean = (X>>9 & 0x1)
        Clean      = (X>>8 & 0x1)*((X>>9 & 0x1)==False)
        Source     = (X>>7 & 0x1)*((X>>8 & 0x1)==False)*((X>>9 & 0x1)==False)
        Transient  = (X>>6 & 0x1)*((X>>7 & 0x1)==False)*((X>>8 & 0x1)==False)*((X>>9 & 0x1)==False)
        return     Transient + Source*2 + Clean*3 + ultraClean*4
    
    pippo = numpy.zeros(len(ClassName),dtype=numpy.int)
    if numpy.isscalar(ClassName[0]):
        if max(ClassName)>10: 
            for i,X in enumerate(ClassName): pippo[i]=p7(X)
        else:
            for i,X in enumerate(ClassName): pippo[i]=p6(X)
    else:
        for i,X in enumerate(ClassName):     pippo[i]=p8(X)
        pass
    return pippo
    

def getNumberOfEvents(fileName):
    nevts = 0
    try:
        print '...opening', fileName
        hdulist = pyfits.open(fileName)
        nevts   = hdulist['EVENTS'].header['NAXIS2']
    except:
        nevts   = 0
        pass    
    return nevts


def computeEflux(f0,index,emin=100, emax=10000):
    #print 'index= %s '
    if index==-2:
        index=-2.000001
    elif index==-1:
        index = -1.000001
        pass
    
    ef0=f0*(1.+index)/(2+index)*(pow(emax,index+2)-pow(emin,index+2))/(pow(emax,index+1)-pow(emin,index+1))
    print 'index= %s , <E>= %s' %(index,ef0/f0)
    return ef0#*MeV2erg


def GetFirstTimeAfter(fileName,METTime,evcls=0):
    hdulist = pyfits.open(fileName)
    tbdata = hdulist[1].data
    time=tbdata.field('TIME')
    energy=tbdata.field('ENERGY')
    evt={}
    i=0
    for t in time:
        evt[t]=energy[i]
        i=i+1
        pass
    i=0
    ttime=sorted(time)
    if ttime[-1]<METTime:
        print 'Returning last entry in th file: %s' % ttime[-1]
        return ttime[-1]
    
    for t in ttime:
        if t-METTime<0:
            i=i+1
        else:
            break
        pass
    t0=ttime[i]
    print "First event after trigger: Time= %s, Energy= %s, DT= %s "%(t0,evt[t0],t0-METTime)
    return t0-METTime
    
def convert(fileName,GRBMET=0,GRBRA=0,GRBDEC=0):
    obj=[]
    print '...opening', fileName
    hdulist = pyfits.open(fileName)
    hdulist.info()
    tbdata = hdulist[1].data

    time=tbdata.field('TIME')
    energy=tbdata.field('ENERGY')
    ra =tbdata.field('RA')
    dec=tbdata.field('DEC')
    l=tbdata.field('L')
    b=tbdata.field('B')
    theta=tbdata.field('THETA')
    phi=tbdata.field('PHI')
    zenith_angle=tbdata.field('ZENITH_ANGLE')
    earth_azimuth_angle = tbdata.field('EARTH_AZIMUTH_ANGLE')
    event_class         = GetEventClass(tbdata.field('EVENT_CLASS'))
    conversion_type     = tbdata.field('CONVERSION_TYPE')
    include_probability=0
    if 'GRB' in tbdata.names:
        src_probability    = tbdata.field('GRB')
        include_probability= 1
        print 'will include probabilities from GRB'
    elif 'SRC_PROBABILITY' in tbdata.names:
        src_probability    = tbdata.field('SRC_PROBABILITY')
        include_probability= 1
        print 'will include probabilities from SRC_PROBABILITY'
    else:
        src_probability = None
        include_probability=0
        pass
    
    n=len(time)
    print 'Find %d events...' % n
    import ROOT
    from array import array
    #    mc_src_id=[] #tbdata.field('mc_src_id')
    #    for i in range(n):
    #        mc_src_id.append(0)
    root_name=    fileName.replace('.fit','.root')
    if root_name[-1]=='s':
        root_name=root_name.replace('.roots','.root')
        pass
    rootf=ROOT.TFile(root_name,'RECREATE')
    asciif   =root_name.replace('.root','.txt')
    evtcanvas=root_name.replace('.root','evt.png')
    
    tree=ROOT.TTree('Events','Events');
    TIME  =  array('d',[0]) 
    ENERGY =  array('f',[0]) 

    RA    =  array('f',[0])
    DEC    =  array('f',[0])
    
    L    =  array('f',[0])
    B    =  array('f',[0])
    THETA=  array('f',[0])
    PHI  =  array('f',[0])
    ZENITH_ANGLE =  array('f',[0])
    EARTH_AZIMUTH_ANGLE =  array('f',[0])
    #    MC_SRC_ID  =  array('i',[0])
    EVENT_CLASS  =  array('i',[0])
    CONVERSION_TYPE = array('i',[0])
    SRC_PROBABILITY     = array('f',[0])
    #tree.Branch('MC_SRC_ID',MC_SRC_ID,'MC_SRC_ID/I')
    tree.Branch('EVENT_CLASS',EVENT_CLASS,'EVENT_CLASS/I')
    tree.Branch('TIME',TIME,'TIME/D')
    tree.Branch('ENERGY',ENERGY,'ENERGY/F')
    tree.Branch('RA',RA,'RA/F')
    tree.Branch('DEC',DEC,'DEC/F')
    tree.Branch('L',L,'L/F')
    tree.Branch('B',B,'B/F')
    tree.Branch('THETA',THETA,'THETA/F')
    tree.Branch('PHI',PHI,'PHI/F')
    tree.Branch('ZENITH_ANGLE',ZENITH_ANGLE,'ZENITH_ANGLE/F')
    tree.Branch('EARTH_AZIMUTH_ANGLE',EARTH_AZIMUTH_ANGLE,'EARTH_AZIMUTH_ANGLE/F')
    tree.Branch('CONVERSION_TYPE',CONVERSION_TYPE,'CONVERSION_TYPE/I')
    if include_probability: tree.Branch('SRC_PROBABILITY',SRC_PROBABILITY,'SRC_PROBABILITY/F')
    time_max=max(time)
    time_min=min(time)
    energy_max=max(energy)    
    print 'TIME MIN,MAX = %.3f, %.3f ' %(time_min,time_max)
    TMAX,EMAX,RAMAX,DECMAX=0,0,0,0

    myevt={}

    gT=ROOT.TGraph()
    gT.SetName('gT')

    gS=ROOT.TGraph()
    gS.SetName('gS')

    gD=ROOT.TGraph()
    gD.SetName('gD')
    
    gC=ROOT.TGraph()
    gC.SetName('gC')

    gTSD=ROOT.TGraph()
    gTSD.SetName('gTSD')

    obj.append(gT)
    obj.append(gS)
    obj.append(gD)
    obj.append(gC)
    obj.append(gTSD)
    
    gT.SetMarkerColor(ROOT.kBlack)
    gS.SetMarkerColor(ROOT.kBlue)
    gD.SetMarkerColor(ROOT.kRed)
    gC.SetMarkerColor(ROOT.kCyan)    
    gTSD.SetMarkerColor(ROOT.kGreen)
    gT.SetMarkerStyle(20)
    gS.SetMarkerStyle(20)
    gD.SetMarkerStyle(20)
    gC.SetMarkerStyle(20)    
    gTSD.SetMarkerStyle(20)
    
    for i in range(n):
        TIME[0]=time[i]
        myevt[time[i]-GRBMET]=[energy[i],ra[i],dec[i],event_class[i],conversion_type[i]]
        if(energy[i]==energy_max):
            TMAX=time[i]-GRBMET
            EMAX=energy_max
            RAMAX=ra[i]
            DECMAX=dec[i]
            CONVERSION_TYPEMAX=conversion_type[i]
            pass
        ENERGY[0]=energy[i] 
        RA[0]=ra[i]
        DEC[0]=dec[i]
        if(l[i]>180.0):
            L[0]=l[i]-360.0
        else:
            L[0]=l[i]
            pass
        B[0]=b[i]
        THETA[0]=theta[i]
        PHI[0]=phi[i]
        ZENITH_ANGLE[0]=zenith_angle[i]
        EARTH_AZIMUTH_ANGLE[0]=earth_azimuth_angle[i]
        
        #        MC_SRC_ID[0]=mc_src_id[i]
        EVENT_CLASS[0]=event_class[i]
        CONVERSION_TYPE[0]=conversion_type[i]
        if include_probability: SRC_PROBABILITY[0] = src_probability[i]
        tree.Fill()
        pass

    print ' --- EVENT WITH THE MAX ENERGY: -------'
    print 'T: %15.4f\t E: %10.0f\t RA: %10.4f\t DEC: %10.4f'%(TMAX,EMAX,RAMAX,DECMAX)
    print 'CONVERSION_TYPE: %s (0=F, 1=B)' % CONVERSION_TYPEMAX
    print '---------------------------------------'
    ##################################################
    NMAX=10
    print 'Now printing the first %s events:' % NMAX
    fout=file(asciif,'w')
    txt='# %13s\t%10s\t%10s\t%10s\t%10s\t%5s\t%10s' %('TIME','ENERGY','RA','DEC','ANGSEP','CLASS','CONVERSION_TYPE')
    print txt
    fout.write('%s\n' % txt)
    if GRBMET>0:
        fout.write('# TRIGGERTIME=%.4f \n'%(GRBMET))
        pass
    
    keys=sorted(myevt.keys())

    i=0

    NEVT100MEV=0
    NEVT1GEV  =0
    NEVT10GEV  =0
    NDIFF=0
    NTRAN=0
    NSOUR=0
    NCLEA=0    
    NTOT =0

    for t in keys:
        evt=myevt[t]
        ##################################################
        gTSD.SetPoint(NTOT,t,evt[0])
        NTOT=NTOT+1
        if evt[3]==1:
            gT.SetPoint(NTRAN,t,evt[0])
            NTRAN=NTRAN+1
            pass
        if evt[3]==2:
            gS.SetPoint(NSOUR,t,evt[0])
            NSOUR=NSOUR+1
            pass
        if evt[3]==3:
            gD.SetPoint(NDIFF,t,evt[0])
            NDIFF=NDIFF+1
            pass
        if evt[3]==4:
            gC.SetPoint(NCLEA,t,evt[0])
            NCLEA=NCLEA+1
            pass
##################################################
        angSep=genutils.angsep(evt[1],evt[2],GRBRA,GRBDEC)
        txt='%15.4f\t%10.1f\t%10.4f\t%10.4f\t%10.4f\t%5d\t%5d'%(t,evt[0],evt[1],evt[2],angSep,evt[3],evt[4])        
        if(i<NMAX):
            print txt
            pass

        fout.write('%s\n'%txt)
        if t>=0:
            if evt[0]>100.0:
                NEVT100MEV=NEVT100MEV+1
                if evt[0]>1000.0:
                    NEVT1GEV=NEVT1GEV+1
                    if evt[0]>10000.0:
                        NEVT10GEV=NEVT10GEV+1
                        pass
                    pass
                pass
            pass
        i=i+1
        pass
    print '--------------------------------------------------'
    print ' Number of events T>0 Energy>100 MeV: %s          ' % NEVT100MEV
    print ' Number of events T>0 Energy>1   GeV: %s          ' % NEVT1GEV
    print ' Number of events T>0 Energy>10  GeV: %s          ' % NEVT10GEV
    print '--------------------------------------------------'
    print ' Number of Total     events: %s                   ' % (NTOT)
    print ' Number of >Transient events: %s                   ' % (NTRAN+NSOUR+NDIFF+NCLEA)
    print ' Number of >Source    events: %s                   ' % (NSOUR+NDIFF+NCLEA)
    print ' Number of >Diffuse   events: %s                   ' % (NDIFF+NCLEA)
    print ' Number of >Clean     events: %s                   ' % (NCLEA)
    print '--------------------------------------------------'

    cc=ROOT.TCanvas('EnergyTime','Energy vs Time',500,500)
    obj.append(cc)
    
    gTSD.SetMaximum(1.1*max(energy))
    gTSD.SetMinimum(0.9*min(energy))
    
    gTSD.Draw('ap')
    gTSD.GetXaxis().SetTitle('Time - %s' % GRBMET)
    gTSD.GetYaxis().SetTitle('Energy [MeV]')
    
    gTSD.GetXaxis().CenterTitle()
    gTSD.GetYaxis().CenterTitle()

    legend=ROOT.TLegend(0.8,0.9,0.99,0.99)    
    if NTRAN>0: 
        gT.Draw('p')
        legend.AddEntry(gT,"Transient",'p')
        pass
    if NSOUR>0: 
        gS.Draw('p')
        legend.AddEntry(gS,"Source",'p')    
        pass
    if NDIFF>0: 
        gD.Draw('p')
        legend.AddEntry(gD,"Diffuse",'p')
        pass
    if NCLEA>0: 
        gC.Draw('p')
        legend.AddEntry(gC,"Clean",'p')
        pass
    
    obj.append(legend)
    legend.Draw()
    cc.SetLogy()
    cc.Update()
    cc.Print(evtcanvas)
    for o in obj: ROOT.SetOwnership(o,False)
    
    fout.close()
    tree.Write()
    rootf.Close()
    
    #if not ROOT.gROOT.IsBatch():
    #    a=raw_input('enter to coninue...')
    pass

def GetGTI(ft1, time):
    hdulist = pyfits.open(ft1)
    start   = hdulist['GTI'].data.field('START')
    stop    = hdulist['GTI'].data.field('STOP')
    start.sort()
    stop.sort()
    return (start[start.searchsorted(time)-1] - time, stop[stop.searchsorted(time)]-time)


def GetTheta(ra_grb,dec_grb,MET_grb,ft2file):
    hdulist=pyfits.open(ft2file)
    SC_data=hdulist['SC_DATA'].data
    
    # SPACECRAFT:
    #ra_zenith   = SC_data.field('RA_ZENITH')
    #dec_zenith    = SC_data.field('DEC_ZENITH')

    # BORESIGHT:
    ra_scz  = SC_data.field('RA_SCZ')
    dec_scz = SC_data.field('DEC_SCZ')
    # TIME
    time  = SC_data.field('START')
    hdulist.close()
    i=0
    if max(time)<MET_grb:
        raise Exception('Error, FT2 file does not cover the MET of the GRB FT2 Time min,max= (%s,%s)' % (min(time)-MET_grb,max(time)-MET_grb))
    
    while (time[i]-MET_grb)<0:
        i=i+1
        pass
    i=i-1
    (phi,theta) = genutils.getNativeCoordinate((ra_grb,dec_grb),(ra_scz[i],dec_scz[i]))
    theta_grb   = math.degrees(genutils.getAngle(phi,theta))
    # print theta,phi
    # print 'Theta GRB = %s at time: %s' % (theta_grb,time[i]-MET_grb)
    return theta_grb

def GetZenith(ra_grb,dec_grb,MET_grb,ft2file,chatter=1):
    hdulist=pyfits.open(ft2file)
    SC_data=hdulist['SC_DATA'].data
    
    # SPACECRAFT:
    ra_zenith   = SC_data.field('RA_ZENITH')
    dec_zenith  = SC_data.field('DEC_ZENITH')

    # BORESIGHT:
    #ra_scz  = SC_data.field('RA_SCZ')
    #dec_scz = SC_data.field('DEC_SCZ')
    # TIME
    time  = SC_data.field('START')
    hdulist.close()
    i=0
    if max(time)<MET_grb:
        raise Exception('Error, FT2 file does not cover the MET of the GRB FT2 Time min,max= (%s,%s)' % (min(time)-MET_grb,max(time)-MET_grb))
    
    while (time[i]-MET_grb)<0:
        i=i+1
        pass
    i=i-1
    (phi,theta) = genutils.getNativeCoordinate((ra_grb,dec_grb),(ra_zenith[i],dec_zenith[i]))
    
    zenith_grb   = math.degrees(genutils.getAngle(phi,theta))
    #if chatter>0 :print 'Zenith GRB = %s at time: %s' % (zenith_grb,time[i]-MET_grb)
    return zenith_grb

def GetMcIlWain(MET_grb,ft2file,chatter=1):
    hdulist=pyfits.open(ft2file)
    SC_data     = hdulist['SC_DATA'].data    
    # McIlWain:
    L_MCILWAIN  = SC_data.field('L_MCILWAIN')
    B_MCILWAIN  = SC_data.field('B_MCILWAIN')
    # TIME
    time        = SC_data.field('START')
    
    hdulist.close()
    i=0
    if max(time)<MET_grb: raise Exception('Error, FT2 file does not cover the MET of the GRB FT2 Time min,max= (%s,%s)' % (min(time)-MET_grb,max(time)-MET_grb))

    while (time[i]-MET_grb)<0:  i=i+1

    i=i-1
    return (L_MCILWAIN[i],B_MCILWAIN[i])


def AngSeparation(ra_grb,dec_grb,time_grb,ft2file,BEFORE=3600, AFTER=3600):
    
    
    if isinstance(time_grb, float):
        T=time_grb
    else:
        try:
            T=genutils.date2met(time_grb)
        except:
            print 'Time must be in MET or UTC (for both tstart and tend) :', time_grb
            print 'usage MET: 236089711.0'
            print 'usage UTC: 2008 06 25 12 28 31'
            return
        pass
    AngGRBSCZ_0    = 0 #self.GetTheta(ra_grb,dec_grb,T,ft2file)
    AngGRBZenith_0 = 0 #self.GetZenith(ra_grb,dec_grb,T,ft2file)

    # retrive data from the FT2
    hdulist=pyfits.open(ft2file)
    
    SC_data=hdulist['SC_DATA'].data

    # SPACECRAFT:
    ra_zenith   = SC_data.field('RA_ZENITH')
    dec_zenith    = SC_data.field('DEC_ZENITH')

    # BORESIGHT:
    ra_scz  = SC_data.field('RA_SCZ')
    dec_scz = SC_data.field('DEC_SCZ')
    
    time=SC_data.field('START')
    
    inSAA = SC_data.field('IN_SAA')
    
    hdulist.close()
    
    MET=[]
    AngGRBZenith=[]
    AngGRBSCZ=[]
    SAA=[]
    #   AngRock=[]
    dtmin=100

    inSAA_0 = False
    arr_scra=[]
    arr_scdec=[]
    arr_zenra=[]
    arr_zendec=[]
    print ' in %s\n %s, %s, %s '%(ft2file,min(time)-T,max(time)-T,len(time))
    if min(time)-T > AFTER or max(time)-T < BEFORE:
        print 'The specified range is not covered by the current FT2 file...'
        AFTER  = max(time)-T
        BEFORE = T-min(time)
        print ' Setting interval for plotting: (%s,%s) ' %(-BEFORE,AFTER)
        #AFTER
        #raise Exception('The specified range is not covered by the current FT2 file')
        pass
    
    I=0
    
    for i in range(len(time)):
        #print time[i]-T
        txt='.'
        if (i%len(time)/20)==0:
            sys.stdout.write('-')
            sys.stdout.flush()
            pass
        
        if ((time[i]-T) > AFTER):
            break
        if((time[i]-T) > -BEFORE and (time[i]-T) <AFTER):
            
            (phi,theta)=genutils.getNativeCoordinate((ra_grb,dec_grb),(ra_scz[i],dec_scz[i]))
            grb_sc=math.degrees(genutils.getAngle(phi,theta))
            
            #(phi3,theta3)=genutils.getNativeCoordinate((ra_scz[i],dec_scz[i]),(ra_grb,dec_grb))
            #print phi,theta,math.degrees(genutils.getAngle(phi,theta))
            
            
            AngGRBSCZ.append(grb_sc)
            
            (phi2,theta2)=genutils.getNativeCoordinate((ra_grb,dec_grb),(ra_zenith[i],dec_zenith[i]))
            grb_zenith=math.degrees(genutils.getAngle(phi2,theta2))

            AngGRBZenith.append(grb_zenith)
            
            if(time[i]-T<0):
                I=i
                AngGRBSCZ_0    = grb_sc
                AngGRBZenith_0 = grb_zenith
                pass

            #     (phi3,theta3)=getNativeCoordinate((ra_zenith[i],dec_zenith[i]),(ra_scz[i],dec_scz[i]))
            #      AngRock.append(math.degrees(getAngle(phi3,theta3)))

            arr_scra.append(ra_scz[i])
            arr_scdec.append(dec_scz[i])
            arr_zenra.append(ra_zenith[i])
            arr_zendec.append(dec_zenith[i])
            
            MET.append(time[i]-T)
            if (inSAA[i]==False):
                SAA.append(0)
            else:
                SAA.append(140)
                pass
            pass
        pass
    
    inSAA_0 = inSAA[I]
    zen_ra_0,zen_dec_0 = ra_zenith[I],dec_zenith[I]
    sc_ra_0,sc_dec_0   =  ra_scz[I],dec_scz[I]

    print '--------------------------------------------------'
    print 'Time.............: %s (%s)' %(time[I],time[I]-T)
    print 'GRB.....(Ra, dec): (%.1f,%.1f)' %(ra_grb,dec_grb)
    print 'SC......(Ra, dec): (%.1f,%.1f)' %(sc_ra_0,sc_dec_0)
    print 'Zenith..(Ra, dec): (%.1f,%.1f)' %(zen_ra_0,zen_dec_0)
    print 'LAT IN SAA?......: ',inSAA_0
    print '*** GRB  THETA...: ', AngGRBSCZ_0
    print '*** FROM ZENIT...: ',AngGRBZenith_0
    print '--------------------------------------------------'    
    return numpy.array(MET), numpy.array(AngGRBZenith), numpy.array(AngGRBSCZ), numpy.array(SAA), AngGRBSCZ_0, AngGRBZenith_0

def write_xmlModel(model='PowerLaw2',xmlFileName='model.xml',ra=0.,dec=0.,chatter=1, justAppend=True, name="GRB", **kwargs):
    if (chatter>0): print "... adding %s point source %s " %(model,name)
    # Parameters default values:
    prefactor_max   = 1.0e5
    prefactor_min   = 0.01
    prefactor_scale = 1e-9
    prefactor_value = 50.0
    prefactor_free  = 1

    integral_max   = 1e6
    integral_min   = 1e-10
    integral_scale = 1e-6
    integral_value = 1.0
    integral_free  = 1

    index_max      = 0.01
    index_min      = -6.0
    index_scale    = 1.0
    index_value    = -2.0
    index_free=1

    scale_max      = 2000.0
    scale_min      = 30.0
    scale_scale    = 1.0
    scale_value    = 100.0
    scale_free     = 0

    LowerLimit_value=100    
    UpperLimit_value=100000

    index1_value = -2.5
    index1_min   = index_min
    index1_max   = index_max
    index1_free  = 1 
    index1_scale = 1 

    index2_value = -2.0
    index2_min   = index_min
    index2_max   = index_max
    index2_free  = 1
    index2_scale = 1

    break_value  = 300.0
    break_min    = 30.0
    break_max    = 300000.0
    break_free   =  1
    break_scale  =  1

    ebreak_value   = 0.1
    ebreak_min     = 0.0
    ebreak_max     = 300.0
    ebreak_free    = 0
    ebreak_scale   = 1.0

    indexco_max    = 3.0
    indexco_min    = -5.0
    indexco_scale  = 1.0
    indexco_value  = 0.0
    indexco_free   = 1

    p1_value   = 300.0
    p1_min     = 0.1
    p1_max     = 100000.0
    p1_free    = 1
    p1_scale   = 1.0

    p2_value   = 0.0
    p2_min     = 0.0
    p2_max     = 100000.0
    p2_free    = 0 
    p2_scale   = 1.0

    p3_value   = 0.0
    p3_min     = 0.0
    p3_max     = 100000.0
    p3_free    = 0
    p3_scale   = 1.0
    
    index1co_value = -1.0
    index1co_min   = -5.0
    index1co_max   = 1.0
    index1co_free  = 1 
    index1co_scale = 1.0 

    index2co_value = 1.0
    index2co_min   = -5.0
    index2co_max   =  5.0
    index2co_free  = 0
    index2co_scale = 1    

    cutoff_value   = 300.0
    cutoff_min     = 0.1
    cutoff_max     = 100000.0
    cutoff_free    = 1
    cutoff_scale   = 1.0
    # log parabola
    norm_value   = 1.0
    norm_min     = 0.001
    norm_max     = 1000.0
    norm_free    = 1
    norm_scale   = 1e-9

    alpha_value   = 1.0
    alpha_min     = 0.0
    alpha_max     = 10.0
    alpha_free    = 1
    alpha_scale   = 1.0

    beta_value   = 0.0
    beta_min     = -1.0
    beta_max     = 10.0
    beta_free    = 1
    beta_scale   = 2.0

    Eb_value   = 300.0
    Eb_min     = 20.0
    Eb_max     = 1e4
    Eb_free    = 1
    Eb_scale   = 1.0

    tau_norm_value  = 0.0
    redshift_value  = 0.0
    ebl_model_value = 5

    try: fixPL=float(os.environ['FIXPL'])
    except: fixPL=None 

    if justAppend==False:
        xmlFile=open(xmlFileName,'w')
	xmlFile.write('<?xml version="1.0" ?>\n')
        xmlFile.write('<source_library title="source library">\n')
    else:
        xmlFile=open(xmlFileName,'a')
        pass
    xmlFile.write('  <source name="%s" type="PointSource">\n' %name)
    xmlFile.write('  <!-- point source units are cm^-2 s^-1 MeV^-1 -->\n')
    xmlFile.write('  <spectrum type="' + model + '">\n')
    
    # Powerlaw :
    #-----------

    if model == 'PowerLaw':
        for key in kwargs.keys():
            if key == 'Prefactor':     prefactor_value = kwargs[key] # *scale* of Prefactor
            elif key == 'Prefactor_free':  prefactor_free      = kwargs[key]
            elif key == 'Index':       index_value     = kwargs[key]
            elif key == 'Index_free':  index_free      = kwargs[key]
            elif key == 'Scale':       scale_value     = kwargs[key]
            else: print 'parameter ' + key + ' unknown in model '+ model + ' : discarded'
            pass
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Prefactor" scale="%s" value="%s"/>\n' %(prefactor_free, prefactor_max, prefactor_min, prefactor_scale, prefactor_value))
        if fixPL is not None: index_free,index_value=0,fixPL        
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Index" scale="%s" value="%s"/>\n' %(index_free, index_max, index_min, index_scale, index_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Scale" scale="%s" value="%s"/>\n' %(scale_free,scale_max,scale_min,scale_scale,scale_value))
        pass
    # PowerLaw2 :
    #------------
    elif model == 'PowerLaw2':
        for key in kwargs.keys():
            print key, kwargs[key]
            if key == 'Integral': integral_value = kwargs[key] # *scale* of Integral
            elif key == 'Integral_free': integral_free = kwargs[key]
            elif key == 'Index': index_value = kwargs[key]
            elif key == 'Index_free': index_free = kwargs[key]
            elif key == 'LowerLimit': LowerLimit_value = kwargs[key]
            elif key == 'UpperLimit':  UpperLimit_value = kwargs[key]
            else: print 'parameter ' + key + ' unknown in model '+ model + ' : discarded'
            pass
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Integral" scale="%s" value="%s"/>\n' %(integral_free, integral_max,integral_min,integral_scale,integral_value))
        if fixPL is not None: index_free,index_value=0,fixPL        
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Index" scale="%s" value="%s"/>\n' %(index_free, index_max,index_min,index_scale,index_value))
        xmlFile.write('        <parameter free="0" max="2000.0" min="30.0" name="LowerLimit" scale="1." value="%s"/>\n' % LowerLimit_value)
        xmlFile.write('        <parameter free="0" max="500000.0" min="2000.0" name="UpperLimit" scale="1." value="%s"/>\n' % UpperLimit_value)        
        pass
    # EblAtten::PowerLaw2 :
    #-----------------
    elif model == 'EblAtten::PowerLaw2':
        for key in kwargs.keys():
            print key, kwargs[key]
            if key == 'Integral': integral_value = kwargs[key] # *scale* of Integral
            elif key == 'Integral_free': integral_free = kwargs[key]
            elif key == 'Index': index_value = kwargs[key]
            elif key == 'Index_free': index_free = kwargs[key]
            elif key == 'LowerLimit': LowerLimit_value = kwargs[key]
            elif key == 'UpperLimit':  UpperLimit_value = kwargs[key]

            elif key == 'tau_norm':  tau_norm_value = kwargs[key]
            elif key == 'redshift':  redshift_value = kwargs[key]
            elif key == 'ebl_model':  ebl_model_value = kwargs[key]
            else: print 'parameter ' + key + ' unknown in model '+ model + ' : discarded'
            pass
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Integral" scale="%s" value="%s"/>\n' %(integral_free, integral_max,integral_min,integral_scale,integral_value))
        if fixPL is not None: index_free,index_value=0,fixPL
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Index" scale="%s" value="%s"/>\n' %(index_free, index_max,index_min,index_scale,index_value))
        xmlFile.write('        <parameter free="0" max="2000.0" min="30.0" name="LowerLimit" scale="1." value="%s"/>\n' % LowerLimit_value)
        xmlFile.write('        <parameter free="0" max="500000.0" min="2000.0" name="UpperLimit" scale="1." value="%s"/>\n' % UpperLimit_value)
        xmlFile.write('        <parameter free="0" max="10.0" min="0.0" name="tau_norm" scale="1." value="%s"/>\n' % tau_norm_value)        
        xmlFile.write('        <parameter free="0" max="10.0" min="0.0" name="redshift" scale="1." value="%s"/>\n' % redshift_value)
        xmlFile.write('        <parameter free="0" max="8" min="0" name="ebl_model" scale="1" value="%s"/>\n' % ebl_model_value)

    # BrokenPowerlaw :
    #-----------------
    elif model == 'BrokenPowerLaw':
        for key in kwargs.keys():
            if key == 'Prefactor':        prefactor_value = kwargs[key] # *scale* of Prefactor
            elif key == 'Prefactor_free': prefactor_free  = kwargs[key]
            elif key == 'Index1':         index1_value    = kwargs[key]
            elif key == 'Index1_free':    index1_free     = kwargs[key]
            elif key == 'Index2':         index2_value    = kwargs[key]
            elif key == 'Index2_free':    index2_free     = kwargs[key]
            elif key == 'Break_value':    break_value     = kwargs[key]
            elif key == 'Break_free':     break_free      = kwargs[key]
            else: print 'parameter ' + key + ' unknown in model '+ model + ' : discarded'
            pass
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Prefactor" scale="%s" value="%s"/>\n' %(prefactor_free, prefactor_max, prefactor_min, prefactor_scale, prefactor_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Index1" scale="%s" value="%s"/>\n' %(index1_free, index1_max, index1_min, index1_scale, index1_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Index2" scale="%s" value="%s"/>\n' %(index2_free, index2_max, index2_min, index2_scale, index2_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="BreakValue" scale="%s" value="%s"/>\n' %(break_free, break_max, break_min, break_scale, break_value))
        pass
    # BrokenPowerlaw2 :
    #------------------
    elif model == 'BrokenPowerLaw2':
        for key in kwargs.keys():
            if key == 'Integral':        integral_value = kwargs[key] # *scale* of Prefactor
            elif key == 'Integra_free': integral_free  = kwargs[key]
            elif key == 'Index1':         index1_value    = kwargs[key]
            elif key == 'Index1_free':    index1_free     = kwargs[key]
            elif key == 'Index2':         index2_value    = kwargs[key]
            elif key == 'Index2_free':    index2_free     = kwargs[key]
            elif key == 'Break_value':    break_value     = kwargs[key]
            elif key == 'Break_free':     break_free      = kwargs[key]
            elif key == 'LowerLimit': LowerLimit_value = kwargs[key]
            elif key == 'UpperLimit':  UpperLimit_value = kwargs[key]
            else: print 'parameter ' + key + ' unknown in model '+ model + ' : discarded'
            pass
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Integral" scale="%s" value="%s"/>\n' %(integral_free, integral_max, integral_min, integral_scale, integral_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Index1" scale="%s" value="%s"/>\n' %(index1_free, index1_max, index1_min, index1_scale, index1_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Index2" scale="%s" value="%s"/>\n' %(index2_free, index2_max, index2_min, index2_scale, index2_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="BreakValue" scale="%s" value="%s"/>\n' %(break_free, break_max, break_min, break_scale, break_value))
        xmlFile.write('        <parameter free="0" max="2000.0" min="30.0" name="LowerLimit" scale="1." value="%s"/>\n' % LowerLimit_value)
        xmlFile.write('        <parameter free="0" max="500000.0" min="2000.0" name="UpperLimit" scale="1." value="%s"/>\n' % UpperLimit_value)        
        pass
    # EBL Cutoff :
    #-------------
    elif model == 'ExpCutoff':
        for key in kwargs.keys():
            if key == 'Prefactor':     prefactor_value = kwargs[key] # *scale* of Prefactor
            elif key == 'Prefactor_free':  prefactor_free      = kwargs[key]
            elif key == 'Index':       indexco_value     = kwargs[key]
            elif key == 'Index_free':  indexco_free      = kwargs[key]
            elif key == 'Scale':       scale_value     = kwargs[key]
            elif key == 'Ebreak': ebreak_value = kwargs[key] # MeV
            elif key == 'Ebreak_free': ebreak_free = kwargs[key] # MeV
            elif key == 'P1': p1_value = kwargs[key] # MeV
            elif key == 'P1_free': p1_free = kwargs[key] # MeV
            elif key == 'P2': p2_value = kwargs[key] # MeV
            elif key == 'P2_free': p2_free = kwargs[key] # MeV
            elif key == 'P3': p3_value = kwargs[key] # MeV
            elif key == 'P3_free': p3_free = kwargs[key] # MeV
            else: print 'parameter ' + key + ' unknown in model '+ model + ' : discarded'
            pass

        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Prefactor" scale="%s" value="%s"/>\n' %(prefactor_free, prefactor_max, prefactor_min, prefactor_scale, prefactor_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Index" scale="%s" value="%s"/>\n' %(indexco_free, indexco_max, indexco_min, indexco_scale, indexco_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Scale" scale="%s" value="%s"/>\n' %(scale_free, scale_max, scale_min, scale_scale, scale_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Ebreak" scale="%s" value="%s"/>\n' %(ebreak_free, ebreak_max, ebreak_min, ebreak_scale, ebreak_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="P1" scale="%s" value="%s"/>\n' %(p1_free, p1_max, p1_min, p1_scale, p1_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="P2" scale="%s" value="%s"/>\n' %(p2_free, p2_max, p2_min, p2_scale, p2_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="P3" scale="%s" value="%s"/>\n' %(p3_free, p3_max, p3_min, p3_scale, p3_value))
    # Simple Exp Cutoff :
    #--------------------
    elif model == 'PLSuperExpCutoff':
        for key in kwargs.keys():
            if key == 'Prefactor':     prefactor_value = kwargs[key] # *scale* of Prefactor
            elif key == 'Prefactor_free':  prefactor_free      = kwargs[key]
            elif key == 'Scale':          scale_value     = kwargs[key]
            elif key == 'Index1':         index1co_value    = kwargs[key]
            elif key == 'Index1_free':    index1co_free     = kwargs[key]
            elif key == 'Index2':         index2co_value    = kwargs[key]
            elif key == 'Index2_free':    index2co_free     = kwargs[key]
            elif key == 'Cutoff':       cutoff_value     = kwargs[key]
            elif key == 'Cutoff_free':  cutoff_free      = kwargs[key]
            else: print 'parameter ' + key + ' unknown in model '+ model + ' : discarded'
            pass
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Prefactor" scale="%s" value="%s"/>\n' %(prefactor_free, prefactor_max, prefactor_min, prefactor_scale, prefactor_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Scale" scale="%s" value="%s"/>\n' %(scale_free, scale_max, scale_min, scale_scale, scale_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Index1" scale="%s" value="%s"/>\n' %(index1co_free, index1co_max, index1co_min, index1co_scale, index1co_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Index2" scale="%s" value="%s"/>\n' %(index2co_free, index2co_max, index2co_min, index2co_scale, index2co_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Cutoff" scale="%s" value="%s"/>\n' %(cutoff_free, cutoff_max, cutoff_min, cutoff_scale, cutoff_value))
    elif model == 'LogParabola':
        Eb=1000
        alpha=1
        beta=0
        norm=0.01
        for key in kwargs.keys():
            if key == 'norm':    norm_value = kwargs[key] # *scale* of Prefactor
            elif key == 'norm_free':    norm_free = kwargs[key] # *scale* of Prefactor
            elif key == 'alpha': alpha_value = kwargs[key]
            elif key == 'alpha_free': alpha_free = kwargs[key]
            elif key == 'beta': beta_value = kwargs[key]
            elif key == 'beta_free': beta_free = kwargs[key]
            elif key == 'Eb': Eb_value = kwargs[key]
            elif key == 'Eb_free': Eb_free = kwargs[key]
            else: print 'parameter ' + key + ' unknown in model '+ model + ' : discarded'
            pass
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="norm" scale="%s" value="%s"/>\n' %(norm_free, norm_max, norm_min, norm_scale, norm_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="alpha" scale="%s" value="%s"/>\n' %(alpha_free, alpha_max, alpha_min, alpha_scale, alpha_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="beta" scale="%s" value="%s"/>\n' %(beta_free, beta_max, beta_min, beta_scale, beta_value))
        xmlFile.write('        <parameter free="%s" max="%s" min="%s" name="Eb" scale="%s" value="%s"/>\n' %(Eb_free, Eb_max, Eb_min, Eb_scale, Eb_value))
    else:
        print 'model ' + model + ' not available yet'
        return "error"
    
    xmlFile.write('  </spectrum>\n')

    xmlFile.write('\n')
    xmlFile.write('  <spatialModel type="SkyDirFunction">\n')
    xmlFile.write('       <parameter free="0" max="360.0" min="-360.0" name="RA" scale="1.0" value="'+str(ra)+'"/>\n')
    xmlFile.write('       <parameter free="0" max="90.0" min="-90.0" name="DEC" scale="1.0" value="'+str(dec)+'"/>\n')
    xmlFile.write('  </spatialModel>\n')
    xmlFile.write('  </source>\n')

    xmlFile.write('\n')
    if justAppend==False:
	xmlFile.write('</source_library>\n')

    xmlFile.close()
    #return self.xml_file_name

    if chatter>0 and justAppend==False:
         print 'created xml model file : ' + xmlFileName + '\n'

    pass

def CreateSource_XML(xmlFileName='model.xml', chatter=1):
    if chatter>0: print 'Creating xml file...'
    xml='''<?xml version="1.0" ?>
    <source_library title="source library">
    '''
    xmlFile     = open(xmlFileName,'w')
    xmlFile.write(xml)
    xmlFile.close()
    pass

def Close_XML(xmlFileName='model.xml',chatter=1):
    if chatter>0: print '... closing the xml file'
    xml='''
    </source_library>'''
    xmlFile     = open(xmlFileName,'a')
    xmlFile.write(xml)
    xmlFile.close()
    pass

def Add_IsoTemplate_XML(xmlFileName='model.xml',template=None, vary=1e6, pmean=1,chatter=1,component_name="EG_v02"):
    if template is None: template=os.environ['ISODIFFUSE']
    if vary==0: 
        free=0
        vary=10
    else :      
        free=1
        vary = math.fabs(vary)
        pass
    pmean = math.fabs(pmean)
    pmax = pmean*vary
    pmin = pmean/vary
    if chatter>0: 
	print '...adding the isotropic diffuse component from the template file:'
	print template
        print 'Normalization: max=%s min=%s value=%f' % (pmax, pmin, pmean)
        pass
    
    xml='''
    <source name="%s" type="DiffuseSource">
    \t <spectrum file="%s" type="FileFunction">
    \t \t <parameter free="%d" max="%s" min="%s" name="Normalization" scale="1" value="%f" />
    \t \t </spectrum>
    \t <spatialModel type="ConstantValue">
    \t \t <parameter free="0" max="1000.0" min="0.0" name="Value" scale="1.0" value="1"/>
    \t </spatialModel>
    </source>''' % (component_name,template, free, pmax, pmin,pmean)
    xmlFile     = open(xmlFileName,'a')
    xmlFile.write(xml)
    xmlFile.close()
    return xmlFileName

def Add_IsoPower_XML(xmlFileName='model.xml', flux=1.e-5, index=-2.4, chatter=1,component_name="EG_v02"):
    flux6=flux*1e6
    if chatter>0 :print '...adding the isotropic diffuse component with powerlaw spectrum...'
    xml='''
    <source name="%s" type="DiffuseSource">
    \t <spectrum type="PowerLaw2">
    \t \t <parameter free="1" max="1000" min="1e-10" name="Integral" scale="1e-06" value="%s"/>
    \t \t <parameter free="1" max="-1.0" min="-6.0" name="Index" scale="1" value="%s"/>
    \t \t <parameter free="0" max="200000" min="20" name="LowerLimit" scale="1" value="100"/>
    \t \t <parameter free="0" max="200000" min="20" name="UpperLimit" scale="1" value="200000"/>
    \t </spectrum>
    \t <spatialModel type="ConstantValue">
    \t \t <parameter free="0" max="1000.0" min="0.0" name="Value" scale="1.0" value="1"/>
    \t </spatialModel>
    </source>''' %(component_name,flux,index)
    
    xmlFile     = open(xmlFileName,'a')
    xmlFile.write(xml)
    xmlFile.close()
    return xmlFileName

def Add_GalacticDiffuseComponent_XML(xmlFileName='model.xml', template=None,chatter=1,free=1, ModelName="GAL_V02"):
    if template is None: template=os.environ['GALDIFFUSE']
    if chatter==1:
	print '...adding the galactic diffuse component...'
    xml='''
    <source name="%s" type="DiffuseSource">
    <!-- diffuse source units are cm^-2 s^-1 MeV^-1 sr^-1 -->
    \t <spectrum type="ConstantValue">
    \t \t <parameter free="%d" max="10000.0" min="0.0" name="Value" scale="1.0" value="1.0"/>
    \t </spectrum>
    \t <spatialModel file="%s" type="MapCubeFunction">
    \t \t <parameter free="0" max="1000.0" min="0.001" name="Normalization" scale="1.0" value="1.0"/>
    \t </spatialModel>
    </source>''' % (ModelName,free,template)
    xmlFile     = open(xmlFileName,'a')
    xmlFile.write(xml)
    xmlFile.close()
    return xmlFileName

def SetFromTemplate_XML(xmlFileName='model.xml',template='template.xml',fixed=False):
    templateF=open(template,'r')
    xml=templateF.readlines()
    xml1=''
    for line in xml:
        #print line,line.find('<?xml'),line.find('source_library')
        if line.find('<?xml')>=0 or line.find('source_library')>=0:
            pass
        else:
            xml1=xml1+line
            pass
        pass

    if (fixed==True):
        xml1=xml1.replace('free="1"','free="0"')
        pass

    print xml1
    xmlFile     = open(xmlFileName,'a')
    xmlFile.write(xml1)
    xmlFile.close()
    return xmlFileName

def CreatePHA_BKG_fromLikelihood(phafile,
                                 outfile,
                                 scfile,
                                 expcube,
                                 expmap,
                                 irfs,
                                 srcmdl,
                                 target='GRB'):
    from GtApp import GtApp
    gtbkg = GtApp('gtbkg')
    gtbkg['phafile'] = phafile    
    gtbkg['outfile'] = outfile
    gtbkg['scfile']  = scfile
    gtbkg['expcube'] = expcube
    gtbkg['expmap']  = expmap
    gtbkg['irfs']    = irfs
    gtbkg['srcmdl']  = srcmdl
    gtbkg['target']  = target
    gtbkg['evtype']  = 3
    gtbkg.run()
    pass


def setPoissonPHAError(InputPha):
    print 'Resetting the stat errors to sqrt(COUNTS): '
    fori     = pyfits.open(InputPha,mode='update')        
    data     = fori['SPECTRUM'].data
    counts   = data.field('COUNTS')
    for i,c in enumerate(counts): data.field('STAT_ERR')[i] = math.sqrt(c)
    fori.flush()
    pass

def EventWithMaxEne(fileName,t0=0,minene=0,minprob=0.9):
    nevts = 0
    outFileName = fileName.replace('.fits','.txt')
    try:
        print '...opening', fileName
        hdulist = pyfits.open(fileName)
        nevts   = hdulist['EVENTS'].header['NAXIS2']
    except:
        return None
    data   = hdulist['EVENTS'].data
    time   = data.field('TIME')
    energy = data.field('ENERGY')
    prob   = data.field('GRB')
    #if minprob==0 and prob.max()>0.9: minprob=0.9
    txt= '#%10s %15s %10s\n' %('TIME','ENERGY','PROB')
    energy_max      = 0
    time_max        = 0
    prob_max = 0
    N_threshold     = 0
    time_first=1e6
    time_last=0

    for i in range(nevts):
        relative_time = time[i]-t0
        txt+='%10.2f %15.1f %10.3f\n' %(relative_time,energy[i],prob[i])        
        if prob[i] > minprob:
            N_threshold += 1
            time_first = min(relative_time,time_first)
            time_last  = max(relative_time,time_last)
            if (energy[i]>minene):
                if energy[i] > energy_max:
                    energy_max = energy[i]
                    time_max   = relative_time
                    prob_max   = prob[i]
                    pass
                pass
            pass
        pass
    txt+='#--------------------------------------------------\n'
    txt+='# NUMBER OF EVENTS ABOVE THRESHOLD: %d \n' % N_threshold
    txt+='# ENERGY MAX EVENT: %.2f MeV, %.3f s, %.4f \n'%(energy_max,time_max,prob_max)
    txt+='#--------------------------------------------------\n'
    outFile=file(outFileName,'w')
    outFile.write(txt)
    outFile.close()
    myres={}
    myres['gtsrcprob_File']=outFileName
    myres['gtsrcprob_Emax']=energy_max
    myres['gtsrcprob_Tmax']=time_max
    myres['gtsrcprob_Pmax']=prob_max
    myres['gtsrcprob_Nthr']=N_threshold
    myres['gtsrcprob_Tfirst']=time_first
    myres['gtsrcprob_Tlast']=time_last
    print txt
    return myres

def ParseProbabilityFile(filename):
    f_in = file(filename,'r')
    nth=0
    maxEnergy=0
    maxEnergyTime=0
    maxEnergyProbability=0
    FIRST=1e6
    LAST=0
    for l in f_in.readlines():
        if '#' in l: continue
        vars   = l.split()
        NEVT   = int(vars[0])
        TIME   = float(vars[1])
        ENERGY = float(vars[2])
        PROB   = float(vars[3])
        FIRST  = min(FIRST,float(vars[4]))
        LAST   = max(LAST,float(vars[5]))
        nth+=NEVT
        if ENERGY > maxEnergy:
            maxEnergy            = ENERGY
            maxEnergyTime        = TIME
            maxEnergyProbability = PROB
            pass
        pass
    mydict={}
    mydict['gtsrcprob_ExtendedEmission_NTH']    = nth
    mydict['gtsrcprob_ExtendedEmission_MAXE']   = maxEnergy
    mydict['gtsrcprob_ExtendedEmission_MAXE_T'] = maxEnergyTime
    mydict['gtsrcprob_ExtendedEmission_MAXE_P'] = maxEnergyProbability
    mydict['gtsrcprob_ExtendedEmission_FIRST']  = FIRST
    mydict['gtsrcprob_ExtendedEmission_LAST']   = LAST
    return mydict
