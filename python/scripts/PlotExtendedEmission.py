#!/usr/bin/env python
import ROOT,math
_includeUL=1
_startFromT90=1

def PlotExtendedEmission(InputFileName,inputResults,xscale='log',ts_min=16,fit=True,xmax=None,xmin=None):
    print '--------------- PlotExtendedEmission -------------------- '
    print '- InputFileName...:',InputFileName
    print '- xscale..........:',xscale
    print '- xmin............:',xmin
    print '- xmax............:',xmax
    print '- ts_min..........:',ts_min
    print '- fit.............:',fit
    print '-----------------------------------------------------------'

    if xmin is None: xmin=1e-2
    
    if 'GBMT95' in inputResults.keys():  GBMT95=inputResults['GBMT95']
    else: GBMT95=0.0
    #GBMT95=10
    results={}
    
    #ROOT.gROOT.Macro("$BASEDIR/GTGRB/rootlogon.C")
    InputFile=file(InputFileName,'r')
    lines = InputFile.readlines()
    
    t0=[]
    t1=[]
    tm=[]
    ts=[]
    NoUL=[]
    NobsTot =[]
    NobsTotE=[]
    nph_100 =[]
    nph_1000=[]
    
    index=[]
    eindex=[]
    flux =[]
    eflux =[]
    Ns=0
    eneflux =[]
    eeneflux =[]
    Ns=0
    
    for line in lines:
        print line
        if '#' in line: continue
        par=line.split()
        if xmax is not None and float(par[2])>xmax: continue
        t0.append(float(par[1]))
        t1.append(float(par[2]))
        tm.append(float(par[3]))            
        ts.append(float(par[6]))
        NobsTot.append(float(par[7])/(t1[-1]-t0[-1]))
        NobsTotE.append(math.sqrt(float(par[7]))/(t1[-1]-t0[-1]))
        nph_100.append(float(par[8])/(t1[-1]-t0[-1]))
        nph_1000.append(float(par[9])/(t1[-1]-t0[-1]))
        
        index.append(float(par[10]))
        eindex.append(float(par[11]))
        flux.append(float(par[12]))
        eflux.append(float(par[13]))
        
        eneflux.append(float(par[14]))
        eeneflux.append(float(par[15]))
        
        if eflux[-1]>0: NoUL.append(1)
        else: NoUL.append(0)
        
        Ns=Ns+1
        pass
    
    if Ns==0:  return results
    
    if t0[0]<=0: xscale=='lin'
    if t0[0]>0:        
        t0.insert(0,xmin)
        t1.insert(0,t0[1])
        tm.insert(0,(t0[1]+t0[0])/2.)
        ts.insert(0,0)
        NobsTot.insert(0,0)
        NobsTotE.insert(0,0)
        nph_100.insert(0,0)
        nph_1000.insert(0,0)
        index.insert(0,0)
        eindex.insert(0,0)
        flux.insert(0,0)
        eflux.insert(0,0)
        eneflux.insert(0,0)
        eeneflux.insert(0,0)
        NoUL.insert(0,0)
        Ns=Ns+1
        pass
    # #################################################
    # flux
    # #################################################  
    fmin=999999
    fmax=0
    for f in flux:
        if f>0:
            fmin=min(fmin,f)
            fmax=max(fmax,f)
            pass
        pass
    ymax = 1.1*(max(flux)+max(eflux))
    ymin = 0.25*fmin
    ymax = 1e-1
    ymin = 1e-7
    
    g0  = ROOT.TGraph(2)
    g0.SetTitle('')
    g0.SetName('flux0')
    
    g0.SetPoint(0,t0[0], ymax)
    g0.SetPoint(1,t1[-1],ymin)

    #g001  = ROOT.TGraph(2)
    #g001.SetTitle('FluxPrompt')
    #g001.SetName('promp0')    
    #g001.SetPoint(0,-10, ymax)
    #g001.SetPoint(1, 100,ymin)
    
    g1  =ROOT.TGraphAsymmErrors(Ns)
    g1.SetName('flux1')
    g1UL=ROOT.TGraphAsymmErrors(Ns)
    g1UL.SetName('flux1UL')

    gFluxToFit  =ROOT.TGraphAsymmErrors()
    gFluxToFit.SetName('gFluxToFit')
    gFluxToFit.SetMarkerStyle(20)
    gFluxToFit.SetMarkerSize(0.5)
    gFluxToFit.SetMarkerColor(ROOT.kWhite)
    gFluxToFit.SetLineColor(ROOT.kWhite)
    #g1  =ROOT.TGraphErrors(Ns)
    #g1.SetName('flux1')
    #g1UL=ROOT.TGraphErrors(Ns)
    #g1UL.SetName('flux1UL')
    
    #g1.SetLineColor(ROOT.kRed)
    g1.SetMarkerStyle(20)
    g1.SetMarkerSize(0.5)
    
    g1.SetLineWidth(2)
    g1UL.SetLineWidth(2)
    arrows=[]
    # #################################################
    # TS
    g00  = ROOT.TGraph(2)
    g00.SetTitle('')
    g00.SetName('TS0')
    g00.SetPoint(0,t0[0], 1.0)
    g00.SetPoint(1,t1[-1],1.2*max(ts))
    
    g10  =ROOT.TGraphErrors(Ns)
    g10.SetName('TS1')
    g10.SetLineWidth(2)
    g10.SetLineColor(ROOT.kRed)
    
    g10UL  =ROOT.TGraphErrors(Ns)
    g10UL.SetName('TS1UL')
    g10UL.SetLineWidth(2)

    # #################################################
    # Photon Index
    g01  = ROOT.TGraph(2)
    g01.SetTitle('')
    g01.SetName('SI')
    g01.SetPoint(0,t0[0], -4.0) #1.1*min(index))
    g01.SetPoint(1,t1[-1],-1.0) #0.9*max(index))
    if min(index)-max(eindex) < -4:
        g01.SetPoint(0,t0[0], -8.0)
    
    g11  =ROOT.TGraphErrors(Ns)
    g11.SetName('SI1')
    
    g11.SetLineWidth(2)
    g11UL  =ROOT.TGraphErrors(Ns)
    g11UL.SetLineWidth(2)
    g11UL.SetName('SIUL1')
    #g11.SetLineColor(ROOT.kRed)
    g11.SetMarkerStyle(20)
    g11.SetMarkerSize(0.5)
        

    # #################################################
    # N P H
    gnph0  = ROOT.TGraph(2)
    gnph0.SetTitle('')
    gnph0.SetPoint(0,t0[0], 0)
    gnph0.SetPoint(1,t1[-1],1.1*(max(NobsTot)+max(NobsTotE)))
    gnph1  =ROOT.TGraphErrors(Ns)
    gnph1.SetLineWidth(2)
    gnph1.SetLineColor(ROOT.kBlue)
    gnph2  =ROOT.TGraphErrors(Ns)
    gnph2.SetLineWidth(2)
    gnph2.SetLineColor(ROOT.kRed)
    gnph3  =ROOT.TGraphErrors(Ns)
    gnph3.SetLineWidth(2)

    pflux_nbins     = 0
    pflux_max       = 0
    epflux_max      = 0
    time_pflux_max  = 0
    etime_pflux_max = 0
    flux2fit_i=0

  
    for i in range(Ns):
        if flux[i] > pflux_max and NoUL[i]:
            pflux_max       = flux[i]
            epflux_max      = eflux[i]
            time_pflux_max  = (t1[i]+t0[i])/2
            etime_pflux_max = (t1[i]-t0[i])/2
            pflux_nbins    += 1
            pass
        
        gnph1.SetPoint(i,(t1[i]+t0[i])/2,max(0,nph_100[i]))
        gnph2.SetPoint(i,(t1[i]+t0[i])/2,max(0,nph_1000[i]))
        gnph3.SetPoint(i,(t1[i]+t0[i])/2,max(0,NobsTot[i]))
        gnph1.SetPointError(i,(t1[i]-t0[i])/2,0)
        gnph2.SetPointError(i,(t1[i]-t0[i])/2,0)        
        gnph3.SetPointError(i,(t1[i]-t0[i])/2,NobsTotE[i])

        # fakeF = 1e-2 *pow(max(100.0,(t1[i]+t0[i])/2),-1.0) # this is for testing purposes
        if NoUL[i]:            
            # g1.SetPoint(i,(t1[i]+t0[i])/2,flux[i])
            # g1.SetPointError(i,(t1[i]-t0[i])/2,eflux[i])
            #g10.SetPoint(i,(t1[i]+t0[i])/2,ts[i])
            #g10.SetPointError(i,(t1[i]-t0[i])/2,0)
            #g11.SetPoint(i,(t1[i]+t0[i])/2,index[i])
            #g11.SetPointError(i,(t1[i]-t0[i])/2,eindex[i])
            
            # gFluxToFit.SetPoint(i,(t1[i]+t0[i])/2,flux[i])
            # gFluxToFit.SetPointError(i,(t1[i]-t0[i])/2,eflux[i])

            g1.SetPoint(i,tm[i],flux[i])
            g1.SetPointError(i,tm[i]-t0[i],t1[i]-tm[i],eflux[i],eflux[i])
            
            g10.SetPoint(i,(t1[i]+t0[i])/2,ts[i])
            g10.SetPointError(i,(t1[i]-t0[i])/2,0)
            g11.SetPoint(i,(t1[i]+t0[i])/2,index[i])
            g11.SetPointError(i,(t1[i]-t0[i])/2,eindex[i])
            
            gFluxToFit.SetPoint(flux2fit_i,tm[i],flux[i])
            gFluxToFit.SetPointError(flux2fit_i,tm[i]-t0[i],t1[i]-tm[i],eflux[i],eflux[i])
            flux2fit_i+=1
            # Test with Fake F;
            #gFluxToFit.SetPoint(i,     (t1[i]+t0[i])/2,       fakeF) # flux[i]/1.65)
            #gFluxToFit.SetPointError(i,(t1[i]-t0[i])/2, 0.2 * fakeF) # flux[i]/1.65)
        else:
            #g1UL.SetPoint(i,(t1[i]+t0[i])/2,flux[i])
            #g1UL.SetPointError(i,(t1[i]-t0[i])/2,0)
            
            #gFluxToFit.SetPoint(i,     (t1[i]+t0[i])/2, flux[i]/1.65)
            #gFluxToFit.SetPointError(i,(t1[i]-t0[i])/2, flux[i]/1.65)
            
            g1UL.SetPoint(i,tm[i],flux[i])
            g1UL.SetPointError(i,tm[i]-t0[i],t1[i]-tm[i],0,0)
            if _includeUL:
                gFluxToFit.SetPoint(flux2fit_i,tm[i],flux[i]/1.65)
                gFluxToFit.SetPointError(flux2fit_i,tm[i]-t0[i],t1[i]-tm[i],flux[i]/1.65,flux[i]/1.65)
                flux2fit_i+=1
                pass
            arrow = ROOT.TArrow(tm[i],flux[i],tm[i],flux[i]/2,0.005,'|>')
            
            # Test with Fake F;
            #gFluxToFit.SetPoint(i,     (t1[i]+t0[i])/2, 1.5*fakeF)
            #gFluxToFit.SetPointError(i,(t1[i]-t0[i])/2, 1.5*fakeF)
            
            #arrow=ROOT.TArrow((t1[i]+t0[i])/2,flux[i],(t1[i]+t0[i])/2,flux[i]/2,0.005,'|>')
            arrow.SetLineWidth(2)
            if flux[i]>0: arrows.append(arrow)
            g10UL.SetPoint(i,(t1[i]+t0[i])/2,ts[i])
            g10UL.SetPointError(i,(t1[i]-t0[i])/2,0)
            g11UL.SetPoint(i,(t1[i]+t0[i])/2,index[i])
            g11UL.SetPointError(i,(t1[i]-t0[i])/2,eindex[i])
            pass
        pass
    # #################################################
    
    c=ROOT.TCanvas("ExtendedEmission","ExtendedEmission",1200,800)
    c.Divide(3,2)
    ##################################################
    c.cd(1)
    g00.Draw('ap')
    g10.Draw('p')
    g10UL.Draw('p')

    if xscale=='log': ROOT.gPad.SetLogx()
    ROOT.gPad.SetLogy()
    g00.GetYaxis().SetTitle('Test Statistic (TS)')
    g00.GetXaxis().SetTitle('Time-Trigger [s]')
    g00.GetYaxis().CenterTitle()
    g00.GetXaxis().CenterTitle()
    g00.GetXaxis().SetTitleOffset(1.2)
    g00.GetYaxis().SetTitleOffset(1.4)
    
    tsline=ROOT.TLine(t0[0],ts_min,t1[-1],ts_min)
    tsline.SetLineStyle(3)
    tsline.SetLineColor(ROOT.kBlue)
    tsline.Draw()
    # #################################################
    c.cd(2)
    
    g0.Draw('ap')
    #gFluxToFit.SetLineColor(5)
    gFluxToFit.Draw('p')
    g1.Draw('p')

    g1UL.Draw('p')
    if xscale=='log': ROOT.gPad.SetLogx()
    ROOT.gPad.SetLogy()
    g0.GetYaxis().SetTitle('Flux [ph cm^{-2} s^{-1}]')
    g0.GetXaxis().SetTitle('Time-Trigger [s]')
    g0.GetYaxis().CenterTitle()
    g0.GetXaxis().CenterTitle()
    g0.GetXaxis().SetTitleOffset(1.2)
    g0.GetYaxis().SetTitleOffset(1.4)
    for a in arrows:   a.Draw()
    
    # #################################################
    c.cd(3)
    g01.Draw('ap')
    g11.Draw('p')
    #g11UL.Draw('p')
    if xscale=='log': ROOT.gPad.SetLogx()
    g01.GetYaxis().SetTitle('Photon Index')
    g01.GetXaxis().SetTitle('Time-Trigger [s]')
    g01.GetYaxis().CenterTitle()
    g01.GetXaxis().CenterTitle()
    g01.GetXaxis().SetTitleOffset(1.2)
    g01.GetYaxis().SetTitleOffset(1.4)
    # #################################################
    
    c.cd(5)
    gnph0.Draw('ap')
    gnph1.Draw('p')
    gnph2.Draw('p')
    gnph3.Draw('p')
    if xscale=='log': ROOT.gPad.SetLogx()
    ROOT.gPad.SetLogy()
    gnph0.GetYaxis().SetTitle('Rate of Events [Hz]')
    gnph0.GetXaxis().SetTitle('Time-Trigger [s]')
    gnph0.GetYaxis().CenterTitle()
    gnph0.GetXaxis().CenterTitle()
    gnph0.GetXaxis().SetTitleOffset(1.2)
    gnph0.GetYaxis().SetTitleOffset(1.4)
    ROOT.gPad.Update()
    
    leg1=ROOT.TLegend(0.0,0.9,0.3,1.0)
    leg2=ROOT.TLegend(0.3,0.9,0.7,1.0)
    leg3=ROOT.TLegend(0.65,0.9,1.0,1.0)
    leg1.SetFillStyle(0)
    leg2.SetFillStyle(0)
    leg3.SetFillStyle(0)
    
    leg1.AddEntry(gnph3,"N observed",'l')
    leg2.AddEntry(gnph1,"N GRB > 100 MeV",'l')
    leg3.AddEntry(gnph2,"N GRB > 1 GeV",'l')
    leg1.Draw()    
    leg2.Draw()    
    leg3.Draw()
    
    # #################################################
    c.cd(6)
    # Plot the comulative Flux
    Cumulative  = ROOT.TGraphErrors(Ns)
    Cumulative.SetLineColor(ROOT.kRed)
    Cumulative.SetLineWidth(2)
    
    cum_y        = [None]*(Ns)
    cum_ey       = [None]*(Ns)
    xi           = [None]*(Ns)    
    exi          = [None]*(Ns)
    xsum         = 0
    yim1         = 0
    eyim1        = 0    
    
    # COMPUTE THE T90 USING THE FLUX
    ngoodpoints  = 0
    firstgood    = 1e6 
    for i in range(Ns):
        xi[i]    = (t1[i]+t0[i])/2
        exi[i]   = (t1[i]-t0[i])/2
        
        if NoUL[i]:
            firstgood = min(xi[i],firstgood)
            xsum     += exi[i]
            ngoodpoints = ngoodpoints + 1
            yim1        += (flux[i] * exi[i]) # ph/cm^2
            eyim1       += (eflux[i]* exi[i]) # ph/cm^2
            pass
        
        cum_y[i]  = yim1
        cum_ey[i] = eyim1
        pass
    
    if ngoodpoints<10:
        yim1 =0
        eyim1=0        
        print ' ngoodpoints=%d, COMPUTE THE T90 USING THE EXPECTED NUMBER OF EVENTS' %  ngoodpoints
        for i in range(Ns):
            yim1       = yim1 + nph_100[i]
            eyim1      = eyim1 + math.sqrt(nph_100[i])
            cum_y[i]   = yim1
            cum_ey[i]  = eyim1
            pass
        if yim1<1:
            print '*** WARNING: THE EXPECTED NUMBER OF EVENTS FROM THE SOURCE IS %.2f *** ' % yim1
            pass
        pass
    
    for i in range(Ns):
        if yim1>0:
            Cumulative.SetPoint(i,xi[i],cum_y[i]/yim1)
            Cumulative.SetPointError(i,exi[i],0) #cum_ey[i]/yim1 + cum_y[i]/(yim1**2)*eyim1)
        else:
            Cumulative.SetPoint(i,xi[i],0)            
            pass
        pass
    

    # COMPUTE THE T90 FLUX
    t05=0
    t95=0
    NBIN=1000
    EXTRA = ROOT.TGraph(NBIN)
    EXTRA.SetLineColor(ROOT.kBlue)
    first = xi[0]
    last  = xi[-1]
    for i in range(NBIN):
        #print last,first,NBIN
        if first>0: tt = first*math.pow(last/first,i*1.0/(NBIN-1.))
        else:  tt = first + (last-first)*i/(NBIN-1.)
        
        y  = Cumulative.Eval(tt)
        EXTRA.SetPoint(i,tt,y)

        if y < 0.05: t05=tt

        if y < 0.95: t95=tt
        pass
    t90=t95-t05
    
    # #################################################
    c.cd(2)
    npoints=0
    last_good_t  = 0
    duration_min = 1e9
    duration_max = 0
    
    fluence_before  = 0
    efluence_before = 0
    fluence_after   = 0
    efluence_after  = 0
    
    enefluence_before  = 0
    eenefluence_before = 0
    enefluence_after   = 0
    eenefluence_after  = 0
    time_before     = 0
    time_after      = 0
    for i,t in enumerate(t1):        
        if NoUL[i]: #this includes the max flux in the fit, and excludes upperlimits            
            duration_min = min(duration_min,t0[i])
            duration_max = max(duration_max,t1[i])
            
            if t > time_pflux_max: #this exclude the max fluence in the fit, and exclude upperlimits
                time_after += exi[i]
                
                npoints = npoints+1
                last_good_t = t
                
                fluence_after  += flux[i]        * exi[i]
                efluence_after += eflux[i]       * exi[i]
                enefluence_after  += eneflux[i]  * exi[i]
                eenefluence_after += eeneflux[i] * exi[i]
            else:
                time_before  += exi[i]
                fluence_before  += flux[i]        * exi[i]
                efluence_before += eflux[i]       * exi[i]
                enefluence_before  += eneflux[i]  * exi[i]
                eenefluence_before += eeneflux[i] * exi[i]
                pass
            pass
        
    
    print '--------------------------------------------------'
    print '***** PROMPT DELAY    (T05)........: %.2f' %(t05)
    print '***** PROMPT END      (T95)........: %.2f' %(t95)
    print '***** PROMPT DURATION (T90)........: %.2f' %(t90)
    print '***** FIRST BIN WITH TS>%d..........: %.2f' %(ts_min,duration_min)
    print '***** LAST  BIN WITH TS>%d..........: %.2f' %(ts_min,duration_max)

    print '--------------------------------------------------'
    p0   = 0
    ep0  = 0
    p1   = 0
    ep1  = 0

    spl_t06  = 0
    spl_t06_l= 0
    spl_t06_u= 0

    bpl_t06  = 0
    bpl_t06_l= 0
    bpl_t06_u= 0

    t06  = 0
    t06_l= 0
    t06_u= 0
    
    p01  = 0
    ep01 = 0
    p11  = 0
    ep11 = 0
    p21  = 0
    ep21 = 0
    p31  = 0
    ep31 = 0

    start_SPL_fit  = time_pflux_max
    if _startFromT90: start_SPL_fit = max(GBMT95,time_pflux_max)

    #fund.SetLineStyle(2)
    start_BPL_fit  = time_pflux_max
    
    np_SPL,np_BPL=0,0
    
    for i,t in enumerate(t1):
        if t > start_SPL_fit and NoUL[i]: np_SPL=np_SPL+1 # I want to make sure I have enough real points...
        if t > start_BPL_fit:
            if NoUL[i]: np_BPL = np_BPL+1 # I want to make sure I have enough real points...
            if _includeUL: last_good_t = t      # this includes upperlimits in the fit
            elif NoUL[i]:  last_good_t = t # this exclude  upperlimits in the fit
            pass
        pass
    

    fun   = ROOT.TF1('f1','[0]*(x)**(-[1])',start_SPL_fit ,last_good_t)
    fund  = ROOT.TF1('f1d','[0]*(x)**(-[1])',start_SPL_fit,last_good_t)
    fun2d  = ROOT.TF1('f12d','[0]*((x<[1])*(x/[1])**(-[2])+(x>[1])*(x/[1])**(-[3]))',start_BPL_fit,last_good_t)
        
    fun2d.SetParName(0,'Norm')
    fun2d.SetParName(1,'Break')
    fun2d.SetParName(2,'index1')
    fun2d.SetParName(3,'index2')
    
    fun2d.SetParameters(1.5e-4,2.0*GBMT95,2.0,1.0)
    #fun2d.Draw('same')
    #ROOT.gPad.Update()
    #fun2d.SetParLimits(0,1e-6,10.0)
    #fun2d.SetParLimits(1,start_BPL_fit,last_good_t)
    #fun2d.SetParLimits(2,0.1,4.0)
    #fun2d.SetParLimits(3,0.1,4.0)

    #fun2d.FixParameter(2,1.5)
    #fun2d.FixParameter(3,1.0)

    
    fun.SetParameters(0.01,1.5)
    fun.SetParLimits(0,1e-6,10.0)
    fun.SetParLimits(1,0.1,4.0)
    #fun.FixParameter(2,start_SPL_fit)
    
    fun.SetLineWidth(2)
    fun.SetLineStyle(1)
    #fun.SetLineColor(ROOT.kGreen)
    fun.SetLineColor(ROOT.kGray)
    
    fund.SetLineWidth(2)
    #fund.SetLineStyle(2)

    fund.SetLineColor(ROOT.kGray)
    fun2d.SetLineColor(ROOT.kGray)
    chi2_1=1000
    chi2_2=1000
    draw1=0
    draw2=0

    xlat  = pow(10.,math.log10(t1[0]* pow(t1[-1]/t1[0],6./10.)))
    ylat0 = pow(10.,math.log10(ymin * pow(ymax/ymin,3./10.)))
    ylat1 = pow(10.,math.log10(ymin * pow(ymax/ymin,2./10.)))
    ylat2 = pow(10.,math.log10(ymin * pow(ymax/ymin,9./10.)))
    print '----------------------------------------------'
    print ' Valid number of points for a SPL fit: ',np_SPL
    print ' Valid number of points for a BPL fit: ',np_BPL
    print '----------------------------------------------'
    if fit and np_SPL>2 and first>0: # I need at least 2 DOF for the SPL fit
        xaxis   = gFluxToFit.GetX()
        N       = gFluxToFit.GetN()
        print 'SPL fitting between %.3f and %.3f using %d points (GBMT95=%.3f)' %(start_SPL_fit,last_good_t,np_SPL,GBMT95)
        gFluxToFit.Fit(fun,"MN",'',start_SPL_fit,last_good_t)        
        p0=fun.GetParameter(0)
        ep0=fun.GetParError(0)
        p1=fun.GetParameter(1)
        ep1=fun.GetParError(1)

        ii=2
        while p0!=p0 or p1!=p1 or ep1!=ep1 or ep0!=ep0 and N-ii>0:
            try:
                x2 = xaxis[N-ii]
                fun.SetParameters(1.0,1.5)
                print ' =====> fitting between %.3f and %.3f ' %(start_SPL_fit,x2)
                gFluxToFit.Fit(fun,"MN",'',start_SPL_fit,x2)
                p0=fun.GetParameter(0)
                ep0=fun.GetParError(0)
                p1=fun.GetParameter(1)
                ep1=fun.GetParError(1)
            except:                
                pass
            ii+=1            
            pass
                
        try:
            chi2_1= fun.GetChisquare()/fun.GetNDF()
        except:
            chi2_1=0
            pass
        fund.SetParameters(p0,p1)        
        draw1=1
        try:        
            if p1>0 and p0>0:
                a=1e-6
                spl_t06      = ROOT.TMath.Power(p0/a,1./p1)
                dt06_dp1 = ROOT.TMath.Power(p0/a,1./p1) *\
                           ROOT.TMath.Log(p0/a) * (-1/(p1*p1))
                dt06_dp0 = ROOT.TMath.Power(1./a,1./p1) *\
                           ROOT.TMath.Power(p0,1./p1-1.)/p1
                # p0 and p1 are highly correlated so
                dt06     = ROOT.TMath.Sqrt(ROOT.TMath.Power(dt06_dp0 * ep0,2) +\
                                           ROOT.TMath.Power(dt06_dp1 * ep1,2)+\
                                           2*ep0*ep1*dt06_dp0*dt06_dp1)
                
                spl_t06_l    = max(0,spl_t06-dt06)
                spl_t06_u    = spl_t06+dt06
                pass            
            pass
        except:
            spl_t06         = 0
            spl_t06_l       = 0
            spl_t06_u       = 0
            pass
        if spl_t06 > 1.0e7:
            spl_t06         = 0
            spl_t06_l       = 0
            spl_t06_u       = 0
            pass
        
        
        print '=================================================='
        print ' AFTERGLOW FIT RESULTS'
        print '--------------------------------------------------'
        print '**** SIMPLE POWER LAW: time interval (%.3f,%.3f) -- CHI2/NDOF= %.3f' % (start_SPL_fit,last_good_t,chi2_1)
        print '*** F(t)=F0 t^(-a) [ph cm^{-2} s^{-1}]'
        print ' F0 = (%.4f +/- %.4f)' %(p0,ep0)
        print ' a  = (%.4f +/- %.4f)' %(p1,ep1)
        print ' Ttime @ F=10-6      = %.3f (%.3f--%.3f)' % (spl_t06,spl_t06_l,spl_t06_u)
        print '--------------------------------------------------'
        #tt1=ROOT.TLatex(xlat,ylat0,"F(t) = F_{0} t^{-#alpha}")
        #tt2=ROOT.TLatex(xlat,ylat1,"F_{0}= %.3f \pm %.3f (ph/cm^{2}/s)" %(p0,ep0))
        #tt3=ROOT.TLatex(xlat,ylat2,"#alpha= %.2f \pm %.2f " %(p1,ep1))

        tt1=ROOT.TLatex()
        tt2=ROOT.TLatex()
        tt3=ROOT.TLatex()

        tt1.SetTextSize(0.04)
        tt2.SetTextSize(0.04)
        tt3.SetTextSize(0.04)            
        # tt1.Draw()
        # tt2.Draw()
        #tt3.Draw()
        tt3.SetNDC(1)
        tt3.DrawLatex(0.6, 0.85, "#alpha= %.2f \pm %.2f " %(p1,ep1))
        ROOT.gPad.Update()
        # except:
        # print ' Afterglow decay will not be computed'
        # pass
        pass
    if fit and np_BPL>4 and first>0: # I need 4 DOF for the BPL fit
        ylat3 = pow(10.,math.log10(ymin * pow(ymax/ymin,8./10.)))
        ylat4 = pow(10.,math.log10(ymin * pow(ymax/ymin,7./10.)))
        ylat5 = pow(10.,math.log10(ymin * pow(ymax/ymin,6./10.)))        
        print 'BPL: fitting between %.3f and %.3f using %d points (GBMT95=%.3f)' %(start_BPL_fit,last_good_t,np_BPL,GBMT95)
        gFluxToFit.Fit(fun2d,"MN",'',start_BPL_fit,last_good_t)
        try:
            chi2_2= fun2d.GetChisquare()/fun2d.GetNDF()
        except:
            chi2_2=0
            pass
        p01=fun2d.GetParameter(0)
        ep01=fun2d.GetParError(0)
        
        p11=fun2d.GetParameter(1)
        ep11=fun2d.GetParError(1)
        
        p21=fun2d.GetParameter(2)
        ep21=fun2d.GetParError(2)
        
        p31=fun2d.GetParameter(3)
        ep31=fun2d.GetParError(3)
        
        fun2d.SetParameters(p01,p11,p21,p31)
        
        try:
            if p31>0 and p0>0:
                a=1e-6
                bpl_t06  = p11* ROOT.TMath.Power(p01/a,1./p31)
                dt06_dp1 = p11* ROOT.TMath.Power(p01/a,1./p31) *\
                           ROOT.TMath.Log(p01/a) * (-1/(p31*p31))
                dt06_dp0 = p11* ROOT.TMath.Power(1./a,1./p31) *\
                           ROOT.TMath.Power(p01,1./p31-1.)/p31
                # p0 and p1 are highly correlated so
                dt06     = ROOT.TMath.Sqrt(ROOT.TMath.Power(dt06_dp0 * ep01,2) +\
                                           ROOT.TMath.Power(dt06_dp1 * ep31,2)+\
                                           2*ep01*ep31*dt06_dp0*dt06_dp1)
                bpl_t06_l    = max(0,bpl_t06-dt06)
                bpl_t06_u    = bpl_t06+dt06
                pass
            pass
        except:
            bpl_t06         = 0
            bpl_t06_l       = 0
            bpl_t06_u       = 0
            pass
        if bpl_t06 > 1.0e7:
            bpl_t06         = 0
            bpl_t06_l       = 0
            bpl_t06_u       = 0
            pass
        
        print '--------------------------------------------------'
        print '**** BROKEN POWER LAW: time interval (%.3f,%.3f) -- CHI2/NDOF= %.3f' % (start_BPL_fit,last_good_t,chi2_2)
        print '*** F(t)= F0 (t<t0)*(t/t0)^(-a)+(t>t0)*(t/t0)^(-b)) [ph cm^{-2} s^{-1}]'
        print ' F0 = (%.2e +/- %.2ef)' %(p01,ep01)
        print ' t0 = (%.4f +/- %.4f)' %(p11,ep11)
        print ' a  = (%.4f +/- %.4f)' %(p21,ep21)
        print ' b  = (%.4f +/- %.4f)' %(p31,ep31)
        print ' Ttime @ F=10-6      = %.3f (%.3f--%.3f)' % (bpl_t06,bpl_t06_l,bpl_t06_u)
        print '--------------------------------------------------'
        tt4=ROOT.TLatex()
        tt6=ROOT.TLatex()#xlat,ylat4,"#alpha_{2}= %.2f \pm %.2f " %(p31,ep31))
        tt4.SetTextSize(0.04)
        #tt5.SetTextSize(0.04)
        tt6.SetTextSize(0.04)
        tt4.SetNDC()
        tt6.SetNDC()
        
        if p21<10 and ep21>0:
            tt4.DrawLatex(0.6,0.775,"#alpha_{1}= %.2f \pm %.2f " %(p21,ep21))
            tt6.DrawLatex(0.6,0.7,"#alpha_{2}= %.2f \pm %.2f " %(p31,ep31))            
            #tt4.Draw()
            # tt5.Draw()
            #tt6.Draw()
            draw2=1
            pass
        #line_break1 = ROOT.TLine(p11-ep11,ymin,p11-ep11,ymax) 
        #line_break2 = ROOT.TLine(p11+ep11,ymin,p11+ep11,ymax)
        #line_break1.SetLineStyle(3)
        #line_break2.SetLineStyle(3)
        #line_break1.SetLineColor(ROOT.kGray)
        #line_break2.SetLineColor(ROOT.kGray)
        #line_break1.Draw()
        #line_break2.Draw()
        pass
    
    if chi2_2 < chi2_1:
        fund.SetLineStyle(2)
        fun2d.SetLineStyle(1)
        #fun2d.SetLineColor(ROOT.kBlue)
    else:
        fund.SetLineStyle(1)
        fun2d.SetLineStyle(2)
        #fun.SetLineColor(ROOT.kBlue)
        pass

    # Only now draw the primitives
    if draw1: fund.Draw("same")
    if draw2: fun2d.Draw("same")
    gbmt95line = ROOT.TLine(GBMT95,ymin,GBMT95,ymax)
    gbmt95line.SetLineColor(ROOT.kRed)
    gbmt95line.SetLineStyle(3)
    gbmt95line.Draw()
    # #################################################
    c.cd(4)
    #g1.SetMaximum(ymax)
    #g1.SetMinimum(ymin)
    g1.GetYaxis().SetTitle('Flux [ph cm^{-2} s^{-1}]')
    g1.GetXaxis().SetTitle('Time-Trigger [s]')
    g1.GetYaxis().CenterTitle()
    g1.GetXaxis().CenterTitle()
    g1.GetXaxis().SetTitleOffset(1.2)
    g1.GetYaxis().SetTitleOffset(1.4)
    g1.GetXaxis().SetRangeUser(-0.1*t95,t95/2)
    
    g1.Draw('ap')    

    ##################################################
    c.cd(6)

    Cumulative.Draw('apl')
    
    EXTRA.Draw('pl')

    if xscale=='log': ROOT.gPad.SetLogx()
    
    t05H=ROOT.TLine(t0[0],0.05,t05,0.05)
    t95H=ROOT.TLine(t0[0],0.95,t95,0.95)
    t05V=ROOT.TLine(t05,0,t05,0.05)
    t95V=ROOT.TLine(t95,0,t95,0.95)
    t05H.SetLineStyle(3)
    t05V.SetLineStyle(3)
    t95H.SetLineStyle(3)
    t95V.SetLineStyle(3)
    t05H.Draw()
    t05V.Draw()
    t95H.Draw()
    t95V.Draw()
    t90lat = ROOT.TLatex(t05,1.05,'T_{05}=%.1f, T_{95}=%.1f, T_{90}=%.1f' %(t05,t95,t90))
    t90lat.SetTextSize(0.03)
    t90lat.Draw()
    Cumulative.GetHistogram().GetXaxis().SetTitle('Time-Trigger [s]')
    Cumulative.GetHistogram().GetYaxis().SetTitle('Cumulative Flux')
    Cumulative.GetHistogram().GetYaxis().CenterTitle()
    Cumulative.GetHistogram().GetXaxis().CenterTitle()
    Cumulative.GetXaxis().SetTitleOffset(1.2)
    Cumulative.GetYaxis().SetTitleOffset(1.4)
    c.cd()
    c.Update()
    # #################################################
    for i in range(6):
        c.cd(i+1)
        ROOT.gPad.Update()
        ROOT.gPad.Print(InputFileName.replace('.txt','_%d.png' %(i+1)))
        pass
    # #################################################
    c.cd()
    file_out=InputFileName.replace('.txt','.png')
    c.Print(file_out)
    #file_out=InputFileName.replace('.txt','.C')
    #c.Print(file_out)
    
    #if not ROOT.gROOT.IsBatch():
    #    a=raw_input('press enter to continue')
    #    pass

    results['LIKE_DURMIN'] = duration_min
    results['LIKE_DURMAX'] = duration_max
    results['PeakFlux']          = pflux_max       # ph/cm^2/s
    results['PeakFlux_ERR']      = epflux_max      # ph/cm^2/s
    results['PeakFlux_Time']     = time_pflux_max  # s
    results['PeakFlux_Time_ERR'] = etime_pflux_max # s
    # Fluence
    results['TimeBeforePeakFlux']             = time_before
    results['FluenceBeforePeakFlux']     = fluence_before  # ph/cm^2
    results['FluenceBeforePeakFlux_ERR'] = efluence_before # ph/cm^2
    results['FluenceAfterPeakFlux']     = fluence_after    # ph/cm^2
    results['FluenceAfterPeakFlux_ERR'] = efluence_after   # ph/cm^2
    
    results['TimeAfterPeakFlux']             = time_after    
    results['EneFluenceBeforePeakFlux']     = enefluence_before  # MeV/cm^2
    results['EneFluenceBeforePeakFlux_ERR'] = eenefluence_before # MeV/cm^2
    results['EneFluenceAfterPeakFlux']     = enefluence_after    # MeV/cm^2
    results['EneFluenceAfterPeakFlux_ERR'] = eenefluence_after   # MeV/cm^2
    
    results['T05_L']             = t05
    results['T95_L']             = t95
    results['AG_F0']             = p0
    results['AG_F0_ERR']         = ep0

    results['AG_SPL_IN1']       = p1
    results['AG_SPL_IN1_ERR']   = ep1    

    results['AG_SPL_DUR']            = spl_t06
    results['AG_SPL_DUR_ERRL']       = spl_t06_l
    results['AG_SPL_DUR_ERRU']       = spl_t06_u

    results['AG_BPL_DUR']            = bpl_t06
    results['AG_BPL_DUR_ERRL']       = bpl_t06_l
    results['AG_BPL_DUR_ERRU']       = bpl_t06_u

    results['AG_BPL_F0']         = p01
    results['AG_BPL_F0_ERR']     = ep01

    results['AG_BPL_TB']         = p11
    results['AG_BPL_TB_ERR']     = ep11

    
    results['AG_BPL_IN1']       = p21
    results['AG_BPL_IN1_ERR']   = ep21
    
    results['AG_BPL_IN2']       = p31
    results['AG_BPL_IN2_ERR']   = ep31
    
    results['AG_SPL_T0']        = start_SPL_fit
    results['AG_SPL_T1']        = last_good_t
    
    results['AG_BPL_T0']        = start_BPL_fit
    results['AG_BPL_T1']        = last_good_t
    
    results['AG_SPL_CHI2']      = chi2_1
    results['AG_BPL_CHI2']      = chi2_2
    
    if chi2_1<chi2_2:
        results['AG_IN']             = p1
        results['AG_IN_ERR']         = ep1
        
        results['AG_DUR']            = spl_t06
        results['AG_DUR_ERRL']       = spl_t06_l
        results['AG_DUR_ERRU']       = spl_t06_u
    else:
        results['AG_IN']             = p31
        results['AG_IN_ERR']         = ep31
        
        results['AG_DUR']            = bpl_t06
        results['AG_DUR_ERRL']       = bpl_t06_l
        results['AG_DUR_ERRU']       = bpl_t06_u        
        pass
    
    
    return results
