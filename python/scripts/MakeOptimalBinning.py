#!/usr/bin/env python
import astropy.io.fits as pyfits
import os

def _findFirst(mylist, elem):
    for i,l in enumerate(mylist):
        if l > elem:
            return i
        pass
    return len(mylist)

def _getNumberOfEvents(mylist,t0,t1):
    return _findFirst(mylist, t1) - _findFirst(mylist, t0)


def EqualNumberOfEvents(lat, EvtPerBin,Expo,duration=0):
    fileName = lat.evt_file
    
    print 'MakeOptimalBinning::EqualNumberOfEvents - Compute the binning for %s events in each bin' % EvtPerBin
    print 'MakeOptimalBinning::EqualNumberOfEvent  - Input file name: %s ' % fileName
    print 'MakeOptimalBinning:: EqualNumberOfEvent - Duration: %s ' % duration    
    hdulist = pyfits.open(fileName)
    tbdata  = hdulist[1].data
    time    = sorted(tbdata.field('TIME'))            
    gti     = hdulist[2].data
    

    
    print 'MakeOptimalBinning:: EqualNumberOfEvent - Expo: %s ' % Expo
    print 'MakeOptimalBinning:: Number of GTIs: %s ' % len(gti)    
    print 'MakeOptimalBinning:: Time from %s to %s' % (min(time)-lat.GRB.Ttrigger,max(time)-lat.GRB.Ttrigger)
    
    bins0 = []
    bins1 = []
    nEvts = []
    addDuration=True
    for ti in range(len(gti)):
        gt0 = gti.field('START')[ti]
        gt1 = gti.field('STOP')[ti]
        
        igt0 = _findFirst(time,gt0)
        igt1 = _findFirst(time,gt1)-1
        itt  = _findFirst(time,duration + lat.GRB.Ttrigger)-1
        #print itt,time[itt]-lat.GRB.Ttrigger
        print '---- MakeOptimalBinning::Working on GTI:%s - %s ' % (gt0-lat.GRB.Ttrigger,gt1-lat.GRB.Ttrigger)
        
        time_gti = time[igt0:igt1]
        N = len(time_gti)        
        if N==0:
            print 'No events in this GTI'
            continue

        i = 0
        EvtPerBin0 = int(EvtPerBin)
        bins0.append(time_gti[i] - lat.GRB.Ttrigger)        
        c=1
        while (c==1):
            if duration > 0 and (i + EvtPerBin0) > itt and addDuration:
                bins1.append(duration)
                nEvts.append(_getNumberOfEvents(time,lat.GRB.Ttrigger+bins0[-1],lat.GRB.Ttrigger+bins1[-1]))
                bins0.append(duration)

                i = _findFirst(time,duration + lat.GRB.Ttrigger)
                addDuration=False
            else:
                i = i + EvtPerBin0            
                if i < N:
                    bins1.append(time_gti[i] - lat.GRB.Ttrigger)
                    nEvts.append(_getNumberOfEvents(time,lat.GRB.Ttrigger+bins0[-1],lat.GRB.Ttrigger+bins1[-1]))
                    bins0.append(time_gti[i] - lat.GRB.Ttrigger)
                    if duration>0:
                        EvtPerBin0 = int(EvtPerBin*max(1,pow((time_gti[i] - lat.GRB.Ttrigger)/duration,Expo)))
                        pass
                    pass
                else:
                    if i <= EvtPerBin0:
                        bins1.append(time_gti[-1] - lat.GRB.Ttrigger)
                        nEvts.append(_getNumberOfEvents(time,lat.GRB.Ttrigger+bins0[-1],lat.GRB.Ttrigger+bins1[-1]))
                    else:
                        bins1[-1]  = time_gti[-1] - lat.GRB.Ttrigger
                        bins0.pop()                    
                        nEvts[-1]  =_getNumberOfEvents(time,lat.GRB.Ttrigger+bins0[-1],lat.GRB.Ttrigger+bins1[-1])
                        pass
                    c=0
                    pass
                pass
            pass
        pass

    Nfinal = len(bins0)
    i=0
    while i<Nfinal:
        if nEvts[i]<EvtPerBin and i>1:
            bins1[i-1] = bins1[i]
            nEvts[i-1] += nEvts[i] 
            bins0.pop(i)
            bins1.pop(i)
            nEvts.pop(i)
            Nfinal-=1
            pass
        i+=1
        pass
    
    print 'MakeOptimalBinning::EqualNumberOfEvents - Final Number of Time bins : ', len(bins0)
    print '--------------------------------------------------'        
    print '       TSTART   **      TSTOP   **    NEVTS'
    for i in range(len(bins0)):
        print '%15.2f %15.2f  %10d' %(bins0[i],bins1[i],nEvts[i])
        pass
    print '--------------------------------------------------'    
    return bins0,bins1

def SplitForGTI(lat, bins,**kwargs):
    MinimumSize = 0
    fileName = lat.evt_file
    T0       = lat.GRB.Ttrigger
    chatter = 0
    for key in kwargs.keys():
        if   key.upper()=="FILENAME": fileName            = kwargs[key]
        elif key.upper()=="MINIMUMSIZE"   : MinimumSize   = kwargs[key]
        elif key.upper()=="CHATTER": chatter=kwargs[key]        
        pass
    if chatter > 0:
        print 'MakeOptimalBinning::SplitForGTI'
        print 'MakeOptimalBinning::SplitForGTI - Input file name: %s ' % fileName
        if chatter > 1:
            print 'INPUT BINS: '
            print bins
            pass
        pass
    hdulist = pyfits.open(fileName)
    gti     =  hdulist[2].data
    if chatter > 0:
        print 'MakeOptimalBinning::SplitForGTI - Number of GTIs: %s ' % len(gti)    
        pass
    bins0 = []
    bins1 = []
    # print 'input bins:', bins
    for ti in range(len(gti)):
        gt0 = gti.field('START')[ti]
        gt1 = gti.field('STOP')[ti]
        if chatter > 0:
            print ' MakeOptimalBinning::SplitForGTI - Working on GTI:%.3f - %.3f ' % (gt0-T0,gt1-T0)
            pass
        if bins[-1] > gt0-T0 and bins[0] < gt1-T0:
            tt0 = max(gt0-T0,bins[0])
            tt1 = min(gt1-T0,bins[-1])
            bins0.append(tt0)
            bins1.append(tt1)
            
            for b in bins:
                if b>tt0 and b<tt1 and b > bins0[-1] + MinimumSize:
                    bins0.append(b)
                    bins1.append(b)
                    pass
                pass
            pass
        pass
    
    bins0.sort()
    bins1.sort()
    if chatter > 0:
        print ' MakeOptimalBinning::EqualNumberOfEvents - Final Number of Time bins : ', len(bins0)
        print ' MakeOptimalBinning::TSTART ** TSTOP '
        for i in range(len(bins0)):
            print '%15.2f %15.2f' %(bins0[i],bins1[i])
            pass
        pass
    
    return bins0,bins1

def BayesianBlocks(lat,prior=1):
    import BayesianBlocks_python as BB
    import numpy as num
    import ROOT
    
    fileName = lat.evt_file    
    print ' MakeOptimalBinning::BayesianBlocks Methods from:'
    print ' MakeOptimalBinning::BayesianBlocks - Input file name: %s ' % fileName
    
    hdulist = pyfits.open(fileName)
    tbdata  = hdulist[1].data
    time    = sorted(tbdata.field('TIME'))
    # duration=lat.GRB.Duration
    gti     =  hdulist[2].data
    # print 'MakeOptimalBinning::EqualNumberOfEvent - GRB Duration: %s ' % duration
    print 'MakeOptimalBinning::Number of GTIs: %s ' % len(gti)
    print 'UNBINNED BB METHOD'
    
    
    tmin     = time[0]-lat.GRB.Ttrigger
    tmax     = time[-1]-lat.GRB.Ttrigger
    N        = max(100,int(tmax-tmin))
    histo    = ROOT.TH1D('LCBB','LCBB',N,tmin,tmax)
    contents = num.zeros(N)
    sizes    = num.zeros(N)
    nevents  = len(time)
    events   = num.zeros(nevents)
    for i,t in enumerate(time):
        histo.Fill(t-lat.GRB.Ttrigger)
        events[i]=(t-lat.GRB.Ttrigger)
        pass
    for i in range(N):
        contents[i] = histo.GetBinContent(i+1)
        sizes[i]    = histo.GetBinWidth(i+1)
        pass
    
    # BINNED
    #   bb = BB.BayesianBlocks(contents,sizes,0.0) 
    
    # UNBINNED:
    bb = BB.BayesianBlocks(events)

    xx, yy = bb.globalOpt(ncp_prior=prior)
    ymax=max(yy)
    print xx
    print yy
    ngr=len(xx)
    bins=[]
    bins.append(xx[0])
    for i in range(1,ngr):
        if xx[i]>xx[i-1]: bins.append(xx[i])  
        pass
    # ##################################################    
    # GRAPHICAL OUTPUT:
    cbb = ROOT.TCanvas( 'cbb', 'cbb', 100, 100, 500, 500 )
    gr=ROOT.TGraph()
    for i in range(ngr):
        if ymax>0: gr.SetPoint(i,xx[i],yy[i]/ymax)
        else:      gr.SetPoint(i,xx[i],0.0)
        pass
    histomax=histo.GetMaximum()
    if histomax>0: histo.Scale(1./histomax)
    else:
        histo.Scale(0.0)
        print 'MekeOptimalBinning::ERROR ymax == 0'
        pass
    histo.Draw()
    gr.SetLineColor(ROOT.kBlue)
    gr.SetLineWidth(2)
    gr.Draw('lp')
    cbb.Update()
    output_canvas_name = lat.out_dir+'/'+lat.grb_name+'_BB.png'        
    cbb.Print(output_canvas_name)
    # ##################################################
    return SplitForGTI(lat, bins,chatter=1)

import ROOT

#Following function written by V.Vasileiou
def ConstantFluence(lat,tmin,tmax,fluence_per_bin):
    import math
    bins=[]
    lcurve_filename = "%s/%s_%.0f_%.0f_1_0_T90.root" %(lat.out_dir,lat.GRB.Name,lat.Emin,lat.Emax)
    if os.path.isfile(lcurve_filename): 
	lcurve_file = ROOT.TFile(lcurve_filename,"r")
    else:
        lcurve_filename = "%s/%s_%.0f_%.0f_0_0_T90.root" %(lat.out_dir,lat.GRB.Name,lat.Emin,lat.Emax)
        if os.path.isfile(lcurve_filename): 
	    lcurve_file = ROOT.TFile(lcurve_filename,"r")
	else:
	    print "Lightcurve file %s not found. Please run CalculateLATT90 first." %lcurve_filename
	    return bins
        pass    
    if not lcurve_file.IsOpen(): 
	print "Problem opening file %s" %lcurve_filename
	return bins
    try:
	gInt_bkg = lcurve_file.cDuration_Coarse.GetPad(1).FindObject("gIntBkg_fine")
	gInt_sig = lcurve_file.cDuration_Coarse.GetPad(1).FindObject("gIntDet_fine")
	gInt_exp = lcurve_file.cDuration_Coarse.GetPad(7).FindObject("gExposure_per_bin_fine")
        T05_T95_T90 = lcurve_file.f_MED_T05_T95_T90.GetTitle().split('_')
    except:
	print "Can't find lightcurve data in file %s" %lcurve_filename
	return bins


    T95 = float(T05_T95_T90[1])
    from ROOT import Math
    sig_binstart=0
    bkg_binstart=0

    at0=tmin 
    exp=0
    fluence=0
    flux_t0=0
    flux_t1=0
    last_flux=0
    for ip in range (0,gInt_bkg.GetN()):
        t1,sigs,bkgs,exps=ROOT.Double(0),ROOT.Double(0),ROOT.Double(0),ROOT.Double(0)
        gInt_bkg.GetPoint(ip,t1,bkgs)

	if t1<tmin: 
	    print "skip %f %f" %(t1,tmin)
	    continue #fast forward until we get to tmin
	if t1>=tmax: 
	    print "break %f %f" %(t1,tmax)
	    break  #done!
        gInt_sig.GetPoint(ip,t1,sigs)
	gInt_exp.GetPoint(ip,t1,exps)
	t1+=gInt_bkg.GetErrorXhigh(ip)
	bkg=bkgs-bkg_binstart #bkg from t0-t1
	sig=sigs-sig_binstart #sig from t0-t1
	if exps<=0: 
	    print "Negative exposure? time=%f exp=%f\n" %(t1,exp)
	    continue
	exp+=exps	      #exposure from t0-t1
	fluence_bin=(sig-bkg)/exp


	fluence+=fluence_bin
	#print "%f-%f bin %e-%e eval %f-%f start %f-%f %e %f" %(at0,t1,sig,bkg,sigs,bkgs,sig_binstart,bkg_binstart,prob,sigma) 
	if fluence>=fluence_per_bin:
	    print "New Bin t0-t1 %.1f--%.1f Sig %.1f bkg %.1f Fluence: %.3e photon/cm2" %(at0,t1,sig,bkg,fluence)
	    last_flux=fluence/(t1-at0)

	    bins.append(at0)
	    bins.append(t1)
	
	    sig_binstart=sigs
	    bkg_binstart=bkgs
	    exp=0;
	    fluence=0
	    at0=t1
    pass

    b=-1.5
    a=math.log(last_flux)-b*(math.log(t1)+math.log(at0))/2
    #print "%f-%f %f %f" %(at0,t1,a,b)
    fluence=0	
    dt=1
    while t1<tmax: #there are more GTIs not processed by the BKGE. Will use an extrapolation of the temporal power decay 
	aflux=math.exp(a+b*math.log(t1))
	fluence+=aflux*dt
	#print "fluence %e flux %e t %f" %(fluence,aflux,t1)
	if fluence>=fluence_per_bin:
            print "New Bin t0-t1 %.1f--%.1f (extrap)" %(at0,t1)
	    bins.append(at0)
    	    bins.append(t1)
	    at0=t1
	    fluence=0
	t1+=dt
    bins.append(at0)
    bins.append(t1)
    return bins
    









