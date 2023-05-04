from GRB import GRB
import astropy.io.fits as pyfits
import plotter
import math
import ROOT

class Detector:
    def __init__(self,detector_name,grb):
        self.detector_name=detector_name
        self.GRB=grb
        self.grb_name = grb.Name
        self.out_dir  = grb.out_dir
        
        self.evt_file=0
        self.FilenameFT2='none'
        
        self.lc_outFile=self.out_dir+'/'+self.grb_name+'_'+self.detector_name+'_lc.fits'
        self.sp_outFile=self.out_dir+'/'+self.grb_name+'_'+self.detector_name+'.pha'
        self.mp_outFile=self.out_dir+'/'+self.grb_name+'_'+self.detector_name+'_map.fits'
        
        self.rsp_File=self.out_dir+'/'+self.grb_name+'_'+self.detector_name+'.rsp'
        self.back_File=''
        self.TimeBinWidth=1.0
        pass
    
    def make_LightCurve(self,dt = 0,evt=''):
        if dt<=0:
            dt = self.TimeBinWidth
            pass        
        self.TimeBinWidth=dt
        
        if evt == '':
            evt = self.evt_file
            lc = self.lc_outFile
            ev = pyfits.open(evt)
            dat = ev['EVENTS'].data
            time = dat.field('TIME')
            start = min(time)
            stop  = max(time)
            start = self.GRB.TStart
            stop = self.GRB.TStop

            #print '===> ', start, stop, stop-start
        else:
            evt = self.out_dir + '/' + evt
            start = self.GRB.TStart
            stop = self.GRB.TStop
            pass
        
        dt = min((stop-start)/5.0,dt)

        from GtApp import GtApp
        print 'Making lightCurve for detector:',self.detector_name,' from ',start,' to ',stop, 'dt =',dt 
        gtbin = GtApp('gtbin')
        
        gtbin['algorithm']='LC'
        
        gtbin['evfile']=evt
        gtbin['scfile']=self.FilenameFT2
        gtbin['outfile']=self.lc_outFile
        
        gtbin['tbinalg']='LIN'
        
        gtbin['tstart'] = start
        gtbin['tstop']  = stop
        gtbin['dtime']  = dt
        gtbin.run()
        pass
    
    def make_ComputeDuration(self,ext=''):
        evt   = self.evt_file
        ev    = pyfits.open(evt)
        dat   = ev['EVENTS'].data
        time  = sorted(dat.field('TIME'))
        start = self.GRB.TStart
        stop  = self.GRB.TStop
        nevt  = len(time)
        
        ###################################################################
        # STANDARD TYPE T90:
        print ' ===> 1) COMPUTE DURATION FITTING THE BACKGROUND '
        #1 Make an histogram:
        T0 = min(time) - self.GRB.Ttrigger
        T1 = T0/4.
        T3 = max(time) - self.GRB.Ttrigger        
        T2 = self.GRB.Duration  + 1./4.* (T3 - self.GRB.Duration) # positive                 

        #T0 = time[0] - self.GRB.Ttrigger
        #T1 = 0.0
        #T2 = self.GRB.Duration # + 1./4.* (T3 - self.GRB.Duration) # positive                 
        #T3 = time[-1] - self.GRB.Ttrigger        
        ###################################################################
        
        print "T0: %s T1: %s T2: %s T3: %s" % (T0,T1,T2,T3)
        
        HistoName          ='Duration1_%s' % self.detector_name+ext
        output_canvas_name = self.out_dir+'/'+self.grb_name+'_'+self.detector_name+'_T90.png'
        
        c1 = ROOT.TCanvas( 'c1', 'c1', 500, 800 )
        c1.Divide(1,2)
        c1.cd(1)
        
        Nent  = max(10,int(T3 - T0))        
        h     = ROOT.TH1D(HistoName,HistoName,Nent,T0,T3)        
        h.SetLineColor(2)
        h.SetMarkerColor(2)
        for t in time:
            h.Fill(t-self.GRB.Ttrigger)
            pass
        
        errs=[None]*Nent
        for i in range(Nent):
            v = h.GetBinContent(i+1)
            t = h.GetBinCenter(i+1)
            errs[i]=math.sqrt(v)
            if t >= T1 and t < T2:
                h.SetBinError(i+1,1e6*v)
            else:
                h.SetBinError(i+1,math.sqrt(v))
                pass
            pass
        
        fName='BKG'
        BkgFunctions=[None]*4
        prob=[None]*4        
        maxprob=0
        imax   =0

        for i in range(4):
            BkgFunctions[i] =ROOT.TF1(fName, 'pol%d'%i,T0,T3)
            h.Fit(BkgFunctions[i],'NE')
            prob[i]=BkgFunctions[i].GetProb()
            if prob[i]>maxprob:
                maxprob=prob[i]
                imax=i
                pass
            pass
        print 'Selected fit if %s order (prob: %s)' % (imax,maxprob)
        BkgFunction = BkgFunctions[imax]
        
        for i in range(Nent):
            v = h.GetBinContent(i+1)
            t = h.GetBinCenter(i+1)
            y = BkgFunction.Eval(t)
            ey = math.sqrt(max(0.0,BkgFunction.Eval(t)))
            if v>y:
                h.SetBinContent(i+1,v-y)            
                h.SetBinError(i+1,math.sqrt(errs[i]*errs[i]+ ey*ey))
            else:
                h.SetBinContent(i+1,0)
                h.SetBinError(i+1,0)
                pass
            pass
        h.Draw('E1')
        l1=ROOT.TLine(T0,0,T0,h.GetMaximum())
        l2=ROOT.TLine(T3,0,T3,h.GetMaximum())
        l3=ROOT.TLine(T1,0,T1,h.GetMaximum())
        l4=ROOT.TLine(T2,0,T2,h.GetMaximum())
        
        l1.SetLineColor(ROOT.kGreen)
        l2.SetLineColor(ROOT.kGreen)
        l3.SetLineColor(ROOT.kGreen)
        l4.SetLineColor(ROOT.kGreen)
        l3.SetLineStyle(2)
        l4.SetLineStyle(2)
        l1.Draw()
        l2.Draw()
        l3.Draw()
        l4.Draw()

        c1.cd(2)
                    
        HistoName          ='Integral1_%s' % self.detector_name+ext

        iy=[None]*Nent
        ix=[None]*Nent
        iy[0]=0.0
        ix[0]=h.GetBinCenter(1)
        for i in range(Nent-1):
            ix[i+1] = h.GetBinCenter(i+2)
            if ix[i+1] > T1 and ix[i+1] < T2:
                INCR    = 1.0*h.GetBinContent(i+2)
            else:
                INCR    = 0.0
                pass
            iy[i+1] = INCR+iy[i]
            pass
        
        maxIntegral = iy[-1]

        grt90 = ROOT.TGraph(Nent)
        newHisto = ROOT.TH1D(HistoName,HistoName,Nent,T0,T3)
        grt90.SetMarkerStyle(20)
        grt90.SetMarkerColor(ROOT.kBlue)
        
        for i in range(Nent):
            if maxIntegral>0:
                grt90.SetPoint(i,ix[i],iy[i]/maxIntegral)
                newHisto.SetBinContent(i+1,iy[i]/maxIntegral)
            else:
                grt90.SetPoint(i,ix[i],0.0)
                newHisto.SetBinContent(i+1,0.0)
                pass
            pass
        ##################################################
        npts=100000
        t05=T0
        t95=T3
        for i in range(npts):
            t = T0 + (T3-T0)*(1.0*i/(npts-1))
            yt=grt90.Eval(t)
            if yt>=0.05 and t05 == T0:
                t05=t
                pass
            if yt>=0.95 and t95 == T3:
                t95=t
                pass
            pass
        print ' == COMPUTED DURATION (1): T05= %s T95= %s, T90= %s' % (t05,t95,t95-t05)        
        ##################################################        
        newHisto.Draw()
        grt90.Draw('p')
        ##################################################
        htl05 = ROOT.TLine(T0,0.05,t05,0.05)
        htl95 = ROOT.TLine(T0,0.95,t95,0.95)
        vtl05 = ROOT.TLine(t05,0.0,t05,0.05)
        vtl95 = ROOT.TLine(t95,0.0,t95,0.95)
        htl05.SetLineStyle(3)
        htl95.SetLineStyle(3)
        vtl05.SetLineStyle(3)
        vtl95.SetLineStyle(3)
        htl05.Draw()
        htl95.Draw()
        vtl05.Draw()
        vtl95.Draw()
        
        c1.Update()
        c1.Print(output_canvas_name)
        ##################################################
        # Byasian block analysis
        #from scripts import BayesianBlocks as BB
        import BayesianBlocks_python as BB
        import numpy as num
        c2 = ROOT.TCanvas( 'c2', 'c2', 100, 100, 500, 500 )
        Nent  = max(10,int(T3 - T0))        
        histo = ROOT.TH1D('LCBB','LCBB',Nent,T0,T3)        
        contents=num.zeros(Nent)
        sizes   =num.zeros(Nent)

        events=[]
        
        for t in time:
            histo.Fill(t-self.GRB.Ttrigger)
            events.append(t-self.GRB.Ttrigger)
            pass
        
        for i in range(Nent):
            contents[i] = histo.GetBinContent(i+1)
            sizes[i]    = histo.GetBinWidth(i+1)
            pass
        ncp_prior=2
        print 'Computing BINNED Bayesian Blocks... ncp_prior=%s' %ncp_prior
        # Binned
        bb = BB.BayesianBlocks(contents,sizes,T0)
        xx, yy = bb.globalOpt(ncp_prior=ncp_prior)        
        ymax=max(yy)
        print xx
        print yy
        ngr=len(xx)
        gr=ROOT.TGraph()
        for i in range(ngr):
            gr.SetPoint(i,xx[i],yy[i]/ymax)
            pass
        
        print 'Computing UNBINNED Bayesian Blocks... ncp_prior=%s' %ncp_prior
        
        # Unbinned
        bb1 = BB.BayesianBlocks(events)
        xx1, yy1 = bb1.globalOpt(ncp_prior=ncp_prior)        
        ymax1=max(yy1)
        print xx1
        print yy1
        ngr1=len(xx1)        
        gr1=ROOT.TGraph()
        for i in range(ngr1):
            gr1.SetPoint(i,xx1[i],yy1[i]/ymax1)
            pass
        if len(xx)==2:
            bt0   = xx[0]
            bt100 = xx[1]
        else:
            bt0   = xx[1]
            bt100 = xx[-2]
            pass
        
        if len(xx1)==2:
            ut0    = xx1[0]
            ut100  = xx1[1]
        else:
            ut0    = xx1[1]
            ut100  = xx1[-2]
            pass
        ##################################################
        print '   BINNED: T0= %s T100= %s T100-T0= %s ' % (bt0,bt100,bt100-bt0)
        print ' UNBINNED: T0= %s T100= %s T100-T0= %s ' % (ut0,ut100,ut100-ut0)
        ##################################################
        histomax=histo.GetMaximum()
        histo.Scale(1./histomax)
        histo.DrawCopy()
        gr.SetLineColor(ROOT.kBlue)
        gr.SetLineWidth(2)
        gr.SetLineStyle(3)
        gr.SetMarkerColor(ROOT.kBlue)
        gr.SetMarkerStyle(20)

        gr1.SetLineColor(ROOT.kGreen)
        gr1.SetLineWidth(2)
        gr1.SetLineStyle(3)
        gr1.SetMarkerColor(ROOT.kGreen)        
        gr1.SetMarkerStyle(20)

        histomax=histo.GetMaximum()
        histo.Scale(1./histomax)
        histo.DrawCopy()

        gr.Draw('lp')
        gr1.Draw('lp')
        c2.Update()
        output_canvas_name = self.out_dir+'/'+self.grb_name+'_'+self.detector_name+'_BB.png'        
        c2.Print(output_canvas_name)
        results={}
        results['T05']    = t05
        results['T95']    = t95
        results['T00_U']  = ut0
        results['T100_U'] = ut100
        results['T00_B']  = bt0
        results['T100_B'] = bt100        
        return results

    
    def save_LightCurve_ROOT(self,ext=''):
        from array import array
        hdulist=pyfits.open(self.lc_outFile)
        #hdulist.info()
        rate    = hdulist['RATE'].data
        time    = rate.field('TIME')
        timedel = rate.field('TIMEDEL')
        counts  = rate.field('COUNTS')

        x       = array('d',time)
        x.append(time[-1]+timedel[-1])
        Nx= len(x)        
        HistoName='LightCurve_'+self.detector_name+ext
        h= ROOT.TH1D(HistoName,HistoName,Nx-1,x)
        i=0
        COUNTS=0
        for i in range(Nx-1): # count in counts:
            COUNTS+=counts[i]
            h.SetBinContent(i+1,counts[i])
            i=i+1
            pass
        print ' NUMBER OF '+self.detector_name+' COUNTS: ',COUNTS
        
        if 1==0:
            h=self.subtractBackground(h)
            nameCanvas='LightCurve_%s_BKG' % self.detector_name
            nameFile  ='LightCurve_%s.png' % self.detector_name
            nameFile1 = self.lc_outFile.replace('.fits','_bkg.png')
            
            cc=ROOT.TCanvas(nameCanvas,nameCanvas,400,400)
            h.Draw()
            cc.Update()
            cc.Print(nameFile1)
            pass
        
        h.SetMinimum(0)
        h.SetFillColor(2)
        self.GRB.ROOTFile.cd()
        h.Write()        
        print 'Saved histogram in ',self.GRB.ROOTFileName
        pass
    
    def subtractBackground(self,h):
        HistoName=h.GetName()
        h.Sumw2()
        i=0
        COUNTS=0
        T0  =0.0
        err=[]
        counts=[]
        maxt=h.GetXaxis().GetXmax()
        mint=h.GetXaxis().GetXmax()
        Nent=h.GetXaxis().GetNbins()
        T100=maxt-60
        if T100<0:
            return 0
        
        for i in range(Nent): # count in counts:
            counts.append(h.GetBinCenter(i+1))
            err.append(h.GetBinError(i+1))
            t=h.GetBinCenter(i+1)            
            if t>=T0 and t<T100:                
                h.SetBinError(i+1,1e6*counts[i])
                # else:
                #    h.SetBinError(i+1,math.sqrt(counts[i]))
                pass
            
            i=i+1
            pass
        fName=HistoName+'BKG'
        BkgFunction =ROOT.TF1(fName, 'pol3',mint,maxt)
        BkgFunction.SetLineWidth(1)
        BkgFunction.SetLineColor(ROOT.kCyan)        
        h.Fit(BkgFunction,'')
        
        for i in range(Nent): # count in counts:
            h.SetBinError(i+1,err[i])
            pass
        
        ##################################################
        print 'Subtracting background for %s...' % h.GetName()
        COUNTS=0
        for i in range(Nent):
            ledge = h.GetBinLowEdge(i+1)
            t = h.GetBinCenter(i+1)
            w = h.GetBinWidth(i+1)            
            redge = ledge + w
            obs = h.GetBinContent(i+1)
            obsErr = h.GetBinError(i+1)
            exp    = BkgFunction.Eval(t)
            try:
                expErr = math.sqrt(exp)
            except:
                expErr = 0
                pass
            value = obs - exp            
            COUNTS+=value            
            error = math.sqrt(obsErr**2 + expErr**2)
            h.SetBinContent(i+1, value)
            h.SetBinError(i+1,error)
            pass
        print "Counts for the background subtracted LC %s" % COUNTS
        return h
    
    def plotLC(self):
        vline=None
        if(self.GRB.Ttrigger>0):
            vline=self.GRB.Ttrigger
            pass
        return plotter.plotLC(self,vline)
    

    def plotLC_PYLAB(self):
        print 'plot lc with pylab, input:',self.lc_outFile
        plotter.plotLC_PYLAB(self,self.lc_outFile,self.evt_file,self.GRB.Ttrigger)

    
    def plotLC_FT1(self,dt=0.1):
        plotter.plotLC_FT1(self,dt)
        pass
