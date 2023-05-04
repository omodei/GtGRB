#!/bin/env python
import sys
import ROOT

class pExtendedLikePlotter(object):

    ''' Class to plot output from the extended emission
    likelihood analysis
    '''
    
    def __init__(self, InputFileName, ts_min=16, xscale='log'):
        self.InputFileName=InputFileName
        self.Xscale=xscale
        self.TS_Min=ts_min
        self.readLikeFile(self.InputFileName)
        if self.t0[0]<=0:
            self.Xscale=='lin'
        if self.t0[0]>0:
            self.fixListsZeros()
        self.Arrows=[]
        self.setupGraphs()
        ## @brief Usef to check if getFluxMaximum() has been run
        #
        self.pflux_max = 0
       
    def readLikeFile(self, InputFileName):
        ''' Reads a txt file with the results of the likelihood extended
        emission analysis
        '''
        print 'Read input file ',InputFileName
        lines=file(InputFileName,'r').readlines()
        
        self.t0=[]
        self.t1=[]
        self.tm=[]
        self.ts=[]
        self.NobsTot =[]
        self.NobsTotE=[]
        self.nph_100 =[]
        self.nph_1000=[]
        
        self.index=[]
        self.eindex=[]
        self.flux =[]
        self.eflux =[]
        self.Ns=0
        self.eneflux =[]
        self.eeneflux =[]
        
        for line in lines:
            print line
            if '#' in line:
                pass
            else:
                par=line.split()
                self.t0.append(float(par[1]))
                self.t1.append(float(par[2]))
                self.tm.append(float(par[3]))            
                self.ts.append(float(par[6]))
                self.NobsTot.append(float(par[7])/(self.t1[-1]-self.t0[-1]))
                self.NobsTotE.append(ROOT.TMath.Sqrt(float(par[7]))/(self.t1[-1]-self.t0[-1]))
                self.nph_100.append(float(par[8])/(self.t1[-1]-self.t0[-1]))
                self.nph_1000.append(float(par[9])/(self.t1[-1]-self.t0[-1]))
                
                self.index.append(float(par[10]))
                self.eindex.append(float(par[11]))
                self.flux.append(float(par[12]))
                self.eflux.append(float(par[13]))
                
                self.eneflux.append(float(par[14]))
                self.eeneflux.append(float(par[15]))
                
                self.Ns=self.Ns+1

        return self.t0, self.t1, self.tm, self.ts, self.NobsTot,\
               self.NobsTotE, self.nph_100, self.nph_1000,\
               self.index, self.eindex, self.flux, self.eflux,\
               self.Ns, self.eneflux, self.eeneflux

    ## @brief Dumpt data table in a tex file
    #  paper formatted
    #
    def dumpTexTable(self):
        tex='\\begin{table}[htbp] \n'
	tex+='\\centering \n'
	tex+='\\begin{tabular}{lcc} \n'
	tex+='\\hline\\hline \n'
	
        tex+='Time & Energy & Photon Flux above 100 MeV \\\  \n'
	tex+='Bins (s) & Index  & (ph cm$^{-2}$s$^{-1}$)\\\ \hline \n'
	for i in range(1,len(self.flux)):
	    if self.flux[i]<1e-5:
	        line='(%s) %.2f--%.2f & $%.2f\pm%.2f$ & $%.2f\pm%.2f\,10^{-6}$ \\\ \n'%\
	          (i, self.t0[i], self.t1[i], self.index[i], self.eindex[i], self.flux[i]*1e6, self.eflux[i]*1e6)
	    elif self.flux[i]<1e-4:
	        line='(%s) %.2f--%.2f & $%.2f\pm%.2f$ & $%.2f\pm%.2f\,10^{-5}$ \\\ \n'%\
	          (i, self.t0[i], self.t1[i], self.index[i], self.eindex[i], self.flux[i]*1e5, self.eflux[i]*1e5)
	    elif self.flux[i]<1e-3:
	        line='(%s) %.2f--%.2f & $%.2f\pm%.2f$ & $%.2f\pm%.2f\,10^{-4}$ \\\ \n'%\
	          (i, self.t0[i], self.t1[i], self.index[i], self.eindex[i], self.flux[i]*1e4, self.eflux[i]*1e4)
	    else:
	        line='(%s) %.2f--%.2f & $%.2f\pm%.2f$ & $%.2f\pm%.2f\,10^{-3}$ \\\ \n'%\
	          (i, self.t0[i], self.t1[i], self.index[i], self.eindex[i], self.flux[i]*1e3, self.eflux[i]*1e3)		  

	    tex+=line
	tex+='\\hline \n \\end{tabular} \n'
	tex+='\\caption{LAT Time resolved spectroscopy} \n'
	tex+='\\label{Tab:LATExt} \n'
	tex+='\\end{table} \n'
        return tex

    def fixListsZeros(self):
        print 'Fix lists zeroes'
        self.t0.insert(0,self.t0[0]/10)
        self.t1.insert(0,self.t0[1])
        self.tm.insert(0,(self.t0[1]+self.t0[0])/2.)
        self.ts.insert(0,0)
        self.NobsTot.insert(0,0)
        self.NobsTotE.insert(0,0)
        self.nph_100.insert(0,0)
        self.nph_1000.insert(0,0)
        self.index.insert(0,0)
        self.eindex.insert(0,0)
        self.flux.insert(0,0)
        self.eflux.insert(0,0)
        self.eneflux.insert(0,0)
        self.eeneflux.insert(0,0)
        self.Ns=self.Ns+1

    def setupGraphs(self):
        print 'Setup all graphs'
        self.setupFluxGraphs()
        self.setupIndexGraphs()
        self.setupTSGraphs()
        self.setupNPredGraphs()

    def setupFluxGraphs(self):
        print 'Setup Flux graphs'
        self.fmin=999999
        self.fmax=0
        for f in self.flux:
            if f>0:
                self.fmin=min(self.fmin,f)
                self.fmax=max(self.fmax,f)
                
        self.ymax = 1.1*(max(self.flux)+max(self.eflux))
        self.ymin = 0.25*self.fmin
        self.ymax = 1e-1
        self.ymin = 1e-7
       
        # Fake graph for plot scales
        self.gFluxFake = ROOT.TGraph(2)
        self.gFluxFake.SetTitle('Flux')
        self.gFluxFake.SetName('flux0')
        self.gFluxFake.SetPoint(0,self.t0[0], self.ymax)
        self.gFluxFake.SetPoint(1,self.t1[-1],self.ymin)
        self.gFluxFake.SetLineColor(ROOT.kWhite)
        self.gFluxFake.SetMarkerColor(ROOT.kWhite)
      

        # Flux with median time bins
        self.gFluxMedian = ROOT.TGraphAsymmErrors(self.Ns)
        self.gFluxMedian.SetName('gFluxMedian')
        self.gFluxMedian.SetTitle('Flux')
        self.gFluxMedian.SetMarkerStyle(20)
        self.gFluxMedian.SetMarkerSize(0.5)
        self.gFluxMedian.SetMarkerColor(ROOT.kBlack)
        self.gFluxMedian.SetLineColor(ROOT.kBlack)

        # Upper Limits
        self.gFluxUL = ROOT.TGraphAsymmErrors(self.Ns)
        self.gFluxUL.SetName('flux1UL')
        self.gFluxUL.SetLineWidth(2)
        

        # Flux To Fit (with fake points for upper limits)
        self.gFluxToFit = ROOT.TGraphAsymmErrors(self.Ns)
        self.gFluxToFit.SetName('gFluxToFit')
        self.gFluxToFit.SetMarkerStyle(20)
        self.gFluxToFit.SetMarkerSize(0.5)
        self.gFluxToFit.SetMarkerColor(ROOT.kWhite)
        self.gFluxToFit.SetLineColor(ROOT.kWhite)

        # Cumulative flux graph
        self.gCumulativeFlux = ROOT.TGraphErrors(self.Ns)
        self.gCumulativeFlux.SetLineColor(ROOT.kRed)
        self.gCumulativeFlux.SetLineWidth(2)
        self.gCumulativeFlux.SetName('Cumulative Flux')
        self.gCumulativeFlux.SetTitle('Cumulative Flux')

        # Cumulative Extra graph
        self.NBinsExtra=1000
        self.gCumulativeExtra = ROOT.TGraph(self.NBinsExtra)
        self.gCumulativeExtra.SetLineColor(ROOT.kBlue)
 
        return self.gFluxMedian, self.gFluxUL, self.gFluxToFit

    def setupIndexGraphs(self):
        print 'Setup Index graphs'
        # Fake Graph for Spectral Index
        self.gIndexFake = ROOT.TGraph(2)
        self.gIndexFake.SetTitle('Spectral Index')
        self.gIndexFake.SetName('SpectralIndex')
        self.gIndexFake.SetPoint(0,self.t0[0], -4.0)
        self.gIndexFake.SetPoint(1,self.t1[-1],-1.0)
        if min(self.index)-max(self.eindex) < -4:
            self.gIndexFake.SetPoint(0,self.t0[0], -8.0)

        # Spectral index graph
        self.gIndex = ROOT.TGraphAsymmErrors(self.Ns)
        self.gIndex.SetName('SpectralIndex_1')       
        self.gIndex.SetLineWidth(2)
        self.gIndex.SetMarkerStyle(20)
        self.gIndex.SetMarkerSize(0.5)

        # Upper limits
        self.gIndexUL = ROOT.TGraphAsymmErrors(self.Ns)
        self.gIndexUL.SetName('SprectralIndex_UL1')
        self.gIndexUL.SetLineWidth(2)

        return self.gIndex, self.gIndexUL


    def setupTSGraphs(self):
        print 'Setup TS graphs'
        # TS Fake graph
        self.gTSFake = ROOT.TGraph(2)
        self.gTSFake.SetTitle('Test Statistic')
        self.gTSFake.SetName('TS0')
        self.gTSFake.SetPoint(0,self.t0[0], 1.0)
        self.gTSFake.SetPoint(1,self.t1[-1],1.2*max(self.ts))
        # TS TGraph
        self.gTS  = ROOT.TGraphAsymmErrors(self.Ns)
        self.gTS.SetName('TS1')
        self.gTS.SetLineWidth(2)
        self.gTS.SetLineColor(ROOT.kRed)
        # TS Upper Limit TGraph
        self.gTSUL = ROOT.TGraphAsymmErrors(self.Ns)
        self.gTSUL.SetName('TS1UL')
        self.gTSUL.SetLineWidth(2)
        return self.gTS, self.gTSUL


    ## @brief Setup graph for number of events prediction
    #  for different energy thresholds
    #
    def setupNPredGraphs(self):
        print 'Setup NPred graphs'
        # Fake graph
        self.gNPredFake = ROOT.TGraph(2)
        self.gNPredFake.SetTitle('GRB Observed Rate')
        self.gNPredFake.SetName('gNPred0')
        self.gNPredFake.SetPoint(0,self.t0[0], 0.0)
        self.gNPredFake.SetPoint(1,self.t1[-1],1.1*(max(self.NobsTot)+max(self.NobsTotE)))
        # NPred TGraph Black All
        self.gNPredAll  = ROOT.TGraphAsymmErrors(self.Ns)
        self.gNPredAll.SetName('gNPredAll')
        self.gNPredAll.SetLineWidth(2)        
        self.gNPredAll.SetLineColor(ROOT.kBlack)

        # NPred TGraph Blue >100 MeV
        self.gNPred100MeV  = ROOT.TGraphAsymmErrors(self.Ns)
        self.gNPred100MeV.SetName('gNPred100MeV')
        self.gNPred100MeV.SetLineWidth(2)        
        self.gNPred100MeV.SetLineColor(ROOT.kBlue)

        # NPred TGraph Red >1 GeV
        self.gNPred1GeV  = ROOT.TGraphAsymmErrors(self.Ns)
        self.gNPred1GeV.SetName('gNpred1GeV')
        self.gNPred1GeV.SetLineWidth(2)        
        self.gNPred1GeV.SetLineColor(ROOT.kRed)
        return self.gNPredAll, self.gNPred100MeV, self.gNPred1GeV

    def fillFluxGraphs(self):
        print 'Fill flux graphs'
        for i in range(self.Ns):
            if self.ts[i]>self.TS_Min:
                self.gFluxMedian.SetPoint(i,self.tm[i],self.flux[i])
                self.gFluxMedian.SetPointError(i,\
                     self.tm[i]-self.t0[i], self.t1[i]-self.tm[i],\
                     self.eflux[i], self.eflux[i])
               
                self.gFluxToFit.SetPoint(i,self.tm[i],self.flux[i])
                self.gFluxToFit.SetPointError(i,\
                     self.tm[i]-self.t0[i], self.t1[i]-self.tm[i],\
                     self.eflux[i], self.eflux[i])
            else:
                self.gFluxUL.SetPoint(i, self.tm[i], self.flux[i])
                self.gFluxUL.SetPointError(i,self.tm[i]-self.t0[i],\
                                           self.t1[i]-self.tm[i],0,0)
            
                self.gFluxToFit.SetPoint(i,self.tm[i],self.flux[i]/1.65)
                self.gFluxToFit.SetPointError(i,self.tm[i]-self.t0[i],self.t1[i]-self.tm[i],\
                                              self.flux[i]/1.65,self.flux[i]/1.65)

                arrow = ROOT.TArrow(self.tm[i],self.flux[i],self.tm[i],\
                                    self.flux[i]/2,0.005,'|>')
                arrow.SetLineWidth(2)
                if self.flux[i]>0: self.Arrows.append(arrow)

        return self.gFluxMedian, self.gFluxToFit, self.gFluxUL, self.Arrows

    def fillIndexGraphs(self):
        print 'Fill index graphs'
        for i in range(self.Ns):
            if self.ts[i]>self.TS_Min:
                self.gIndex.SetPoint(i, self.tm[i], self.index[i])
                self.gIndex.SetPointError(i,\
                     self.tm[i]-self.t0[i], self.t1[i]-self.tm[i],\
                     self.eindex[i], self.eindex[i])
            else:
                self.gIndexUL.SetPoint(i, self.tm[i], self.index[i])
                self.gIndexUL.SetPointError(i,\
                     self.tm[i]-self.t0[i], self.t1[i]-self.tm[i],\
                     self.eindex[i], self.eindex[i])
        return self.gIndex, self.gIndexUL

    ## @brief Fill the TS graphs from the list
    #
    def fillTSGraphs(self):
        print 'Fill TS graphs'
        for i in range(self.Ns):
             if self.ts[i]>self.TS_Min:
                 self.gTS.SetPoint(i,self.tm[i],self.ts[i])
                 self.gTS.SetPointError(i,\
                     self.tm[i]-self.t0[i], self.t1[i]-self.tm[i],0,0)
             else:
                 self.gTSUL.SetPoint(i,self.tm[i],self.ts[i])
                 self.gTSUL.SetPointError(i,self.tm[i]-self.t0[i], self.t1[i]-self.tm[i],0,0)
        return self.gTS,self.gTSUL 


    ## @brief Fill the graphs for the prediction of number of events from the list
    #
    def fillNPredGraphs(self):
        print 'Fill NPred graphs'
        for i in range(self.Ns):
            self.gNPredAll.SetPoint(i, self.tm[i], max(0,self.NobsTot[i]))
            self.gNPredAll.SetPointError(i,\
                           self.tm[i]-self.t0[i], self.t1[i]-self.tm[i],\
                           self.NobsTotE[i], self.NobsTotE[i])

            self.gNPred100MeV.SetPoint(i,self.tm[i], max(0,self.nph_100[i]))
            self.gNPred100MeV.SetPointError(i,\
                            self.tm[i]-self.t0[i], self.t1[i]-self.tm[i], 0., 0.)

            self.gNPred1GeV.SetPoint(i, self.tm[i], max(0,self.nph_1000[i]))
            self.gNPred1GeV.SetPointError(i,\
                            self.tm[i]-self.t0[i], self.t1[i]-self.tm[i], 0., 0.)
            
        return self.gNPredAll, self.gNPred100MeV, self.gNPred1GeV

    ## @brief Fill the cumulative flux graphs from the list
    #
    def fillCumulativeFlux(self):
        print 'Fill Cumulative Flux graph and compute flux T90'
        self.cum_y        = [None]*(self.Ns)
        self.cum_ey       = [None]*(self.Ns)
        self.xi           = [None]*(self.Ns)    
        self.exi          = [None]*(self.Ns)
        self.xsum         = 0
        self.yim1         = 0
        self.eyim1        = 0

        # COMPUTE THE T90 USING THE FLUX
        self.ngoodpoints  = 0
        self.firstgood    = 1e6 
        for i in range(self.Ns):
            self.xi[i]    = (self.t1[i]+self.t0[i])/2
            self.exi[i]   = (self.t1[i]-self.t0[i])/2
            
            if self.ts[i]>self.TS_Min:
                self.firstgood = min(self.xi[i],self.firstgood)
                self.xsum     += self.exi[i]
                self.ngoodpoints = self.ngoodpoints + 1
                self.yim1        += (self.flux[i] * self.exi[i]) # ph/cm^2
                self.eyim1       += (self.eflux[i]* self.exi[i]) # ph/cm^2

            self.cum_y[i]  = self.yim1
            self.cum_ey[i] = self.eyim1
   
        if self.ngoodpoints<10:
            self.yim1 =0
            self.eyim1=0        
            print ' ngoodpoints=%d, COMPUTE THE T90 USING THE\
                    EXPECTED NUMBER OF EVENTS' %  self.ngoodpoints
            for i in range(self.Ns):
                self.yim1       = self.yim1 + self.nph_100[i]
                self.eyim1      = self.eyim1 + ROOT.TMath.Sqrt(self.nph_100[i])
                self.cum_y[i]   = self.yim1
                self.cum_ey[i]  = self.eyim1
            if self.yim1<1:
                print '*** WARNING: THE EXPECTED NUMBER OF EVENTS\
                      FROM THE SOURCE IS %.2f *** ' % self.yim1
    
        for i in range(self.Ns):
            if self.yim1>0:
                self.gCumulativeFlux.SetPoint(i,self.xi[i],self.cum_y[i]/self.yim1)
                self.gCumulativeFlux.SetPointError(i,self.exi[i],0)
            else:
                self.gCumulativeFlux.SetPoint(i,self.xxi[i],0)            

        # COMPUTE THE T90 FLUX
        self.t05=0
        self.t95=0
        self.first = self.xi[0]
        self.last  = self.xi[-1]
        for i in range(self.NBinsExtra):
            #print last,first,NBIN
            if self.first>0:
                tt = self.first*ROOT.TMath.Power(self.last/self.first,\
                                              i*1.0/(self.NBinsExtra-1.))
            else:
                tt = self.first + (self.last-self.first)*i/(self.NBinsExtra-1.)
        
            y  = self.gCumulativeFlux.Eval(tt)
            self.gCumulativeExtra.SetPoint(i,tt,y)

            if y < 0.05:
                self.t05=tt
            if y < 0.95:
                self.t95=tt
        self.t90=self.t95-self.t05
        
        return self.gCumulativeFlux, self.gCumulativeExtra

    def getFluenceAndDuration(self):
        print 'Running get Fluence and Duration'
        self.npoints = 0
        last_good_t = 0
        self.duration_min = 1e9
        self.duration_max = 0
    
        self.fluence_before  = 0
        self.efluence_before = 0
        self.fluence_after   = 0
        self.efluence_after  = 0
        
        self.enefluence_before  = 0
        self.eenefluence_before = 0
        self.enefluence_after   = 0
        self.eenefluence_after  = 0
        self.time_before     = 0
        self.time_after      = 0
        for i,t in enumerate(self.t1):        
            #this includes the max flux in the fit, and excludes upperlimits
            if self.ts[i]>self.TS_Min: 
                self.duration_min = min(self.duration_min,self.t0[i])
                self.duration_max = max(self.duration_max,self.t1[i])
                #this includes the max fluence in the fit, and excludes upperlimits
                if t > self.time_pflux_max:            
                    self.time_after += self.exi[i]                
                    self.npoints = self.npoints+1
                    last_good_t = t
                
                    self.fluence_after += self.flux[i]        * self.exi[i]
                    self.efluence_after += self.eflux[i]      * self.exi[i]
                    self.enefluence_after += self.eneflux[i]  * self.exi[i]
                    self.eenefluence_after += self.eeneflux[i]* self.exi[i]
                else:
                    self.time_before += self.exi[i]
                    self.fluence_before += self.flux[i]        * self.exi[i]
                    self.efluence_before += self.eflux[i]      * self.exi[i]
                    self.enefluence_before += self.eneflux[i]  * self.exi[i]
                    self.eenefluence_before += self.eeneflux[i]* self.exi[i]
        return 1


    def printDuration(self):
        # Check that we have all the information needed
        if self.pflux_max == 0:            
            self.fillGraphs()
        print '--------------------------------------------------'
        print '***** PROMPT DELAY    (T05)........: %.2f' %(self.t05)
        print '***** PROMPT END      (T95)........: %.2f' %(self.t95)
        print '***** PROMPT DURATION (T90)........: %.2f' %(self.t90)
        print '***** FIRST BIN WITH TS>%d..........: %.2f'\
              %(self.TS_Min,self.duration_min)
        print '***** LAST  BIN WITH TS>%d..........: %.2f'\
              %(self.TS_Min,self.duration_max)

        return 1 


    def fillGraphs(self):
        print 'Fill all graphs'
        self.getFluxMaximum()
        self.fillTSGraphs()
        self.fillIndexGraphs()
        self.fillCumulativeFlux()
        self.getFluenceAndDuration()
        self.printDuration()
        self.fillFluxGraphs()
        self.fillNPredGraphs()
      
    def plotFlux(self, gPad=None, simple=False):
        print 'Plot fluxes'
        if gPad is None:
            self.cFlux=ROOT.TCanvas("FluxCan", "Flux Canvas",30,50,550,550)
            self.fluxPad=ROOT.TPad("FluxPad","",0,0,1,1)
            self.fluxPad.Draw()
            self.fluxPad.cd()
        else:
            gPad.cd()
        if self.Xscale=='log':
            ROOT.gPad.SetLogx()
        if simple:            
            self.gFluxMedian.Draw("AP")
            self.gFluxMedian.GetYaxis().SetTitle('Flux [ph/cm^2/s]')
            self.gFluxMedian.GetXaxis().SetTitle('Time-Trigger [s]')
            self.gFluxMedian.GetYaxis().CenterTitle()
            self.gFluxMedian.GetXaxis().CenterTitle()
            self.gFluxMedian.GetXaxis().SetTitleOffset(1.2)
            self.gFluxMedian.GetYaxis().SetTitleOffset(1.4)
            self.gFluxMedian.GetXaxis().SetRangeUser(-0.1*self.t95,self.t95/3.)
        else:
            ROOT.gPad.SetLogy(1)
            self.gFluxFake.Draw("AP")
            self.gFluxFake.GetYaxis().SetTitle('Flux [ph/cm^2/s]')
            self.gFluxFake.GetXaxis().SetTitle('Time-Trigger [s]')
            self.gFluxFake.GetYaxis().CenterTitle()
            self.gFluxFake.GetXaxis().CenterTitle()
            self.gFluxFake.GetXaxis().SetTitleOffset(1.2)
            self.gFluxFake.GetYaxis().SetTitleOffset(1.4)
       
            self.gFluxToFit.Draw("P")
            self.gFluxMedian.Draw("P")
            self.gFluxUL.Draw("P")

            for a in self.Arrows:
                a.Draw()


    def plotIndex(self, gPad=None):
        print 'Plot indices'
        if gPad is None:
            self.cIndex=ROOT.TCanvas("IndexCan", "Index Canvas",600,50,550,550)
            self.cIndex.cd()
        else:
            gPad.cd()
        if self.Xscale=='log':
            ROOT.gPad.SetLogx()
        self.gIndexFake.Draw("AP")
        self.gIndexFake.GetYaxis().SetTitle('Spectral Index')
        self.gIndexFake.GetXaxis().SetTitle('Time-Trigger [s]')
        self.gIndex.Draw("P")
        self.gIndexUL.Draw("P")
        self.gIndexFake.GetXaxis().CenterTitle()
        self.gIndexFake.GetYaxis().CenterTitle()


    def plotFluxAndIndex(self):
        # Set Style
        ROOT.gStyle.SetPadTickY(0)
        kIndexColor=ROOT.kBlack
        # Open new Canvas
        self.cFluxIndex=ROOT.TCanvas("FluxIndexCan",\
                             "Flux and IndexCanvas",30,50,850,650)
        self.fluxPad=ROOT.TPad("FluxPad","",0,0,1,1)
        self.fluxPad.Draw()
        self.fluxPad.cd()
        self.fillGraphs()
        self.gFluxFake.SetPoint(0,1,1e-7)
        self.gFluxFake.SetTitle("")
        self.plotFlux(self.fluxPad)
        self.fitAfterglow(self.fluxPad)
        self.FitTxt[2].SetY(1e-4)
        self.FitTxt[2].Draw()
        self.cFluxIndex.Update()
        # create a transparent pad drawn on top of the main pad
        self.cFluxIndex.cd()
        self.overlay = ROOT.TPad("overlay","",0,0,1,1)
        self.overlay.SetFillStyle(4000)
        self.overlay.SetFillColor(0)
        self.overlay.SetFrameFillStyle(4000)
        self.overlay.Draw()
        self.overlay.cd()
        # Draw transparent frame in the pad
        xmin=self.gFluxFake.GetXaxis().GetXmin()
        xmax=self.gFluxFake.GetXaxis().GetXmax()
        ymin=self.gIndexFake.GetYaxis().GetXmin()-1.8
        ymax=self.gIndexFake.GetYaxis().GetXmax()-0.4
        self.hframe = self.overlay.DrawFrame(xmin,ymin,xmax,ymax)
        self.hframe.GetXaxis().SetLabelOffset(99)
        self.hframe.GetYaxis().SetLabelOffset(99)
        self.hframe.GetXaxis().SetTickLength(0.0)
        self.hframe.GetYaxis().SetTickLength(0.0)
        # Draw Index
        self.gOvrIndex=self.gIndex.Clone("gOvrIndex")
        self.gOvrIndex.SetLineWidth(1)
        self.gOvrIndex.SetMarkerStyle(26)
        self.gOvrIndex.SetMarkerSize(1)
        self.gOvrIndex.SetMarkerColor(kIndexColor)
        self.gOvrIndex.SetLineColor(kIndexColor)        
        self.gOvrIndex.Draw("P")
        # Draw IndexUL
        self.gOvrIndexUL=self.gIndexUL.Clone("gOvrIndexUL")
        self.gOvrIndexUL.SetLineWidth(1)
        self.gOvrIndexUL.SetMarkerColor(kIndexColor)
        self.gOvrIndexUL.SetMarkerStyle(26)
        self.gOvrIndexUL.SetMarkerSize(1)
        self.gOvrIndexUL.SetLineColor(kIndexColor)        
        self.gOvrIndexUL.Draw("P")        

        #Draw an axis on the right side
        self.IndexAxis = ROOT.TGaxis(xmax,ymin,xmax,\
                                     ymax,ymin,ymax,510,"+L")
        self.IndexAxis.SetLineColor(kIndexColor)
        self.IndexAxis.SetLabelColor(kIndexColor)
        self.IndexAxis.SetLabelSize(0.032)
        self.IndexAxis.SetTitle("Spectral Index")
        self.IndexAxis.CenterTitle()        
        self.IndexAxis.Draw()
        # Set Log X
        self.overlay.SetLogx(1)
        ROOT.gStyle.SetPadTickY(0)

        # Legend
        self.LegendFluxIndex=ROOT.TLegend(0.2,0.15,0.5,0.3)
        self.LegendFluxIndex.AddEntry(self.gFluxMedian, "Flux (left)","lep")
        self.LegendFluxIndex.AddEntry(self.gOvrIndex, "Spectral Index (right)","lep")
        self.LegendFluxIndex.SetFillColor(0)
        self.LegendFluxIndex.SetBorderSize(2)
        self.LegendFluxIndex.Draw()

    def plotTS(self, gPad=None):
        print 'Plot TS'
        if gPad is None:
            self.cTS=ROOT.TCanvas("TSCan", "TS Canvas",30,550,550,450)
            self.cTS.cd()
        else:
            gPad.cd()
        if self.Xscale=='log':
            ROOT.gPad.SetLogx()

        self.gTSFake.Draw('ap')
        self.gTS.Draw('p')
        self.gTSUL.Draw('p')

        ROOT.gPad.SetLogy()
        self.gTSFake.GetYaxis().SetTitle('TS')
        self.gTSFake.GetXaxis().SetTitle('Time-Trigger [s]')
        self.gTSFake.GetYaxis().CenterTitle()
        self.gTSFake.GetXaxis().CenterTitle()
        self.gTSFake.GetXaxis().SetTitleOffset(1.2)
        self.gTSFake.GetYaxis().SetTitleOffset(1.4)
        
        self.TSLine=ROOT.TLine(self.t0[0],self.TS_Min,self.t1[-1],self.TS_Min)
        self.TSLine.SetLineStyle(3)
        self.TSLine.SetLineColor(ROOT.kBlue)
        self.TSLine.Draw()
        

    ## @brief Plot the graphs with the number of predicted counts
    #  for the GRB
    # 
    def plotNPred(self, gPad=None):
        print 'Plot N predicted'
        if gPad is None:
            self.cNPred=ROOT.TCanvas("NPredCan", "NPred Canvas",600,50,550,550)
            self.cNPred.cd()
        else:
            gPad.cd()
        if self.Xscale=='log':
            ROOT.gPad.SetLogx()
        ROOT.gPad.SetLogy(1)
        self.gNPredFake.Draw("AP")
        self.gNPredFake.GetYaxis().SetTitle('Rate of Events [Hz]')
        self.gNPredFake.GetXaxis().SetTitle('Time-Trigger [s]')
        self.gNPredAll.Draw("P")
        self.gNPred100MeV.Draw("P")
        self.gNPred1GeV.Draw("P")

        # Add legend
        self.NPredLegend=ROOT.TLegend(0.6,0.9,0.95,1.0)
        self.NPredLegend.AddEntry(self.gNPredAll,"N observed",'l')
        self.NPredLegend.AddEntry(self.gNPred100MeV,"N GRB > 100 MeV",'l')
        self.NPredLegend.AddEntry(self.gNPred1GeV,"N GRB > 1 GeV",'l')
        self.NPredLegend.SetFillStyle(0)
        self.NPredLegend.Draw()


    def plotCumulativeFlux(self, gPad=None):
        print 'Plot cumulative flux'
        if gPad is None:
            self.cCumul=ROOT.TCanvas("CumulativeFluxCan",\
                                     "Cumulative Flux Canvas",600,630,550,500)
            self.cCumul.cd()
        else:
            gPad.cd()
        if self.Xscale=='log':
            ROOT.gPad.SetLogx()
        self.gCumulativeFlux.Draw("APL")
        self.gCumulativeExtra.Draw("PL")
        self.gCumulativeFlux.GetHistogram().GetXaxis().SetTitle('Time-Trigger [s]')
        self.gCumulativeFlux.GetHistogram().GetYaxis().SetTitle('Cumulative Flux')
        self.gCumulativeFlux.GetHistogram().GetYaxis().CenterTitle()
        self.gCumulativeFlux.GetHistogram().GetXaxis().CenterTitle()
        self.gCumulativeFlux.GetXaxis().SetTitleOffset(1.2)
        self.gCumulativeFlux.GetYaxis().SetTitleOffset(1.4)

        # Add Lines and Text
        self.CumulLine=[]
        self.CumulLine.append(ROOT.TLine(self.t0[0],0.05,self.t05,0.05))
        self.CumulLine.append(ROOT.TLine(self.t0[0],0.95,self.t95,0.95))
        self.CumulLine.append(ROOT.TLine(self.t05,0,self.t05,0.05))
        self.CumulLine.append(ROOT.TLine(self.t95,0,self.t95,0.95))
        for l in self.CumulLine:
            l.SetLineStyle(3)
            l.Draw()
        self.t90lattxt = ROOT.TLatex(self.t05,1.05,'T_{05}=%.1f, T_{95}=%.1f, T_{90}=%.1f'\
                             %(self.t05, self.t95, self.t90))
        self.t90lattxt.SetTextSize(0.03)
        self.t90lattxt.Draw()
 
    def getFluxMaximum(self):
        print 'Get Flux maximum'
        self.pflux_nbins = 0
        self.pflux_max = 0
        self.epflux_max = 0
        self.time_pflux_max = 0
        self.etime_pflux_max_low = 0
        self.etime_pflux_max_high = 0
  
        for i in range(self.Ns):
            if self.flux[i] > self.pflux_max and self.ts[i]>self.TS_Min:
                self.pflux_max       = self.flux[i]
                self.epflux_max      = self.eflux[i]
                self.time_pflux_max  = self.tm[i]
                self.etime_pflux_max_low = self.tm[i]-self.t0[i]
                self.etime_pflux_max_high= self.t1[i]-self.tm[i]
                self.pflux_nbins    += 1
        return self.time_pflux_max, self.etime_pflux_max_low, self.etime_pflux_max_high

    def fitAfterglow(self, agPad):        
        # Check that we have all the information needed
        if self.pflux_max == 0:            
            self.fillGraphs()
        print 'Fit Afterglow'
        # Fit parameters
        p0   = 0
        ep0  = 0
        p1   = 0
        ep1  = 0
        t06  = 0
        dt06 = 0

        # Filled at the end
        self.AfterglowIndex=0
        self.AfterglowIndexError=0
        self.AfterglowFlux=0
        self.AfterglowFluxError=0
        
        # Define fit functions, 2 of them...
        self.fun   = ROOT.TF1('f1','[0]*(x**(-[1]))')
        self.fund  = ROOT.TF1('f1d','[0]*(x**(-[1]))')
        self.fun.SetParameters(0.01,1.5)
        self.fun.SetParLimits(0,1e-6,10.0)
        self.fun.SetParLimits(1,0.1,4.0)        
        self.fun.SetLineWidth(2)
        self.fun.SetLineStyle(1)
        self.fun.SetLineColor(ROOT.kGray)    
        self.fund.SetLineWidth(2)
        self.fund.SetLineColor(ROOT.kGreen)
        self.fund.SetLineColor(ROOT.kGray)    

        #this includes upperlimits in the fit
        last_good_t = 0
        for i,t in enumerate(self.t1):        
            if t > self.time_pflux_max:
                last_good_t = t

        if self.npoints > 1 and self.first>0:
            xaxis   = self.gFluxToFit.GetX()
            N       = self.gFluxToFit.GetN()
            x1 = self.time_pflux_max
            x2 = last_good_t
            print 'fitting between %.3f and %.3f using %d points'\
                  %(x1,x2,self.npoints)
            self.fitPtr=self.gFluxToFit.Fit(self.fun,"EMS",'',x1,x2)            
            p0=self.fun.GetParameter(0)
            ep0=self.fun.GetParError(0)
            p1=self.fun.GetParameter(1)
            ep1=self.fun.GetParError(1)

            # Fit
            ii=2
            while p0!=p0 or p1!=p1 or ep1!=ep1 or ep0!=ep0 and N-ii>0:
                try:
                    x2 = xaxis[N-ii]
                    self.fun.SetParameters(1.0,1.5)
                    print '--------------------------------------------------'
                    print ' =====> fitting between %.3f and %.3f ' %(x1,x2)
                    self.fitPtr=self.gFluxToFit.Fit(self.fun,"EMS",'',x1,x2)
                    p0=self.fun.GetParameter(0)
                    ep0=self.fun.GetParError(0)
                    p1=self.fun.GetParameter(1)
                    ep1=self.fun.GetParError(1)
                except:                
                    pass
                ii+=1            
            
            self.fund.SetParameters(p0,p1)
            self.fund.SetRange(self.time_pflux_max,self.t1[-1])
            self.fund.Draw("same")

            try:
                xlat  = ROOT.TMath.Power(10.,ROOT.TMath.Log10(self.t1[0]*\
                                            ROOT.TMath.Power(self.t1[-1]/self.t1[0],6./10.)))
                ylat0 = ROOT.TMath.Power(10.,ROOT.TMath.Log10(self.ymin *\
                                            ROOT.TMath.Power(self.ymax/self.ymin,3./10.)))
                ylat1 = ROOT.TMath.Power(10.,ROOT.TMath.Log10(self.ymin *\
                                            ROOT.TMath.Power(self.ymax/self.ymin,2./10.)))
                ylat2 = ROOT.TMath.Power(10.,ROOT.TMath.Log10(self.ymin *\
                                            ROOT.TMath.Power(self.ymax/self.ymin,9./10.)))
                try:
                    if p1>0 and p0>0:
                        t06      = ROOT.TMath.Power(1e6*p0,1./p1)
                        dt06_dp1 = ROOT.TMath.Power(1e6*p0,1./p1) *\
                                             ROOT.TMath.Log(1e6*p0) * (-1/(p1*p1))
                        dt06_dp0 = ROOT.TMath.Power(1e6,1./p1) *\
                                             ROOT.TMath.Power(p0,1./p1-1.)/p1
                        # p0 and p1 are highly correlated so
                        dt06     = ROOT.TMath.Sqrt(ROOT.TMath.Power(dt06_dp0 * ep0,2) +\
                                             ROOT.TMath.Power(dt06_dp1*ep1,2)+\
                                             2*ep0*ep1*dt06_dp0*dt06_dp1)
                        t06_l    = t06-dt06
                        t06_u    = t06+dt06
                except:
                    t06   = 0
                    dt06  = 0
                    t06_l = 0
                    t06_u = 0

                # Se members
                self.t06=t06
                self.dt06=dt06
                self.t06_l=t06_l
                self.t06_u=t06_u
                # Get Fit results
                print '--------------------------------------------------'
                print 'Fit details'
                self.fitPtr.Print("V")
                print '--------------------------------------------------'
                print '**** Afterglow Fit Results. Fit if the Flux in time interval (%.3f,%.3f)'\
                      % (self.t90,last_good_t)
                print '*** F(t)=F0 t^(-a) [ph/cm^2/s]'
                print ' F0 = (%.4f +/- %.4f) with dF0/F0=%.1f %%' %(p0,ep0,ep0/p0*100)
                print ' a  = (%.4f +/- %.4f) with da/a=%.1f %%' %(p1,ep1,ep1/p1*100)
                print ' Ttime @ F=10-6      = %.3f +/- %.3f, tmin= %.3f, tmax=%.3f' %\
                      (t06,dt06,t06_l, t06_u)
                print '--------------------------------------------------'
                sys.stdout.flush()
                self.FitTxt=[]
                self.FitTxt.append(ROOT.TLatex(xlat,ylat0,"F(t) = F_{0} t^{-#alpha}"))
                self.FitTxt.append(ROOT.TLatex(xlat,ylat1,"F_{0}= %.3f \pm %.3f (ph/cm^{2}/s)"\
                                               %(p0,ep0)))
                self.FitTxt.append(ROOT.TLatex(xlat,ylat2,"#alpha= %.2f \pm %.2f " %(p1,ep1)))
                agPad.cd()
                for txt in self.FitTxt:
                    txt.SetTextSize(0.03)
                # Draw only the last one
                self.FitTxt[2].Draw()
                ROOT.gPad.Update()
                self.AfterglowIndex=p1
                self.AfterglowIndexError=ep1
                self.AfterglowFlux=p0
                self.AfterglowFluxError=ep0
            except:
                print ' Afterglow decay will not be computed'

        return self.AfterglowIndex,self.AfterglowIndexError

    def compareTo(self, other):
        other.plotFullCanvas('1')
        self.plotFullCanvas('2')
        # TS pad
        self.FullCanvas.cd(1)
        self.gTS.SetLineColor(1)
        self.gTSUL.SetLineColor(1)
        other.gTS.Draw('P')
        other.gTSUL.Draw('P')
        self.FullCanvas.cd(2)        
        other.gFluxMedian.Draw('P')
        other.gFluxUL.Draw('P')
        other.gFluxMedian.SetLineColor(2)
        other.gFluxUL.SetLineColor(2)
        self.FullCanvas.cd(3)
        other.gIndex.Draw('P')
        other.gIndexUL.Draw('P')
        other.gIndex.SetLineColor(2)
        other.gIndexUL.SetLineColor(2)
        

    def plotFullCanvas(self, tag=''):
        self.fillGraphs()
        self.FullCanvas=ROOT.TCanvas("ExtendedCanvas_%s"%tag,\
                                     "Extended Emission Canvas %s"%tag,30,50,1250,750)
        self.FullCanvas.Divide(3,2)
        # TS
        self.FullCanvas.cd(1)
        self.plotTS(ROOT.gPad)
        # Flux
        self.FullCanvas.cd(2)
        self.plotFlux(ROOT.gPad)
        self.fitAfterglow(ROOT.gPad)
        # Index
        self.FullCanvas.cd(3)
        self.plotIndex(ROOT.gPad)
        # Flux 
        self.FullCanvas.cd(4)
        self.plotFlux(ROOT.gPad, simple=True)
        # Event rate
        self.FullCanvas.cd(5)
        self.plotNPred(ROOT.gPad)        
        # Cumulative flux
        self.FullCanvas.cd(6)
        self.plotCumulativeFlux(ROOT.gPad)
        # Update canvas
        self.FullCanvas.cd()
        self.FullCanvas.Update()
        # Save Canvas
        self.saveCanvas()
        # Save dictionnary
        return self.saveResults()
        
    def runAll(self):
        print 'Do everything'
        self.fillGraphs()
        self.plotFlux()
        self.plotIndex()
        self.plotCumulativeFlux()
        self.fitAfterglow(self.cFlux)
        self.plotTS()
        self.plotNPred()

    def saveCanvas(self):
        # Save sub-pads
        for i in range(6):
            self.FullCanvas.cd(i+1)
            ROOT.gPad.Update()
            ROOT.gPad.Print(self.InputFileName.replace('.txt','_%d.png' %(i+1)))
        # Save full canvas
        self.FullCanvas.cd()
        file_out=self.InputFileName.replace('.txt','.png')
        self.FullCanvas.Print(file_out)
        file_out=self.InputFileName.replace('.txt','.C')
        self.FullCanvas.Print(file_out)
        file_out=self.InputFileName.replace('.txt','.root')
        self.FullCanvas.SaveAs(file_out)

    def saveResults(self):
        # Create an empty dictionnary
        results={}            
        # Found a dictionnary now fill it
        results['LIKE_DURMIN'] = self.duration_min
        results['LIKE_DURMAX'] = self.duration_max
        results['PeakFlux']          = self.pflux_max       # ph/cm^2/s
        results['PeakFlux_ERR']      = self.epflux_max      # ph/cm^2/s
        results['PeakFlux_Time']     = self.time_pflux_max  # s
        results['PeakFlux_Time_Low'] = self.etime_pflux_max_low # s
        results['PeakFlux_Time_High']= self.etime_pflux_max_high # s
        # Fluence
        results['TimeBeforePeakFlux']       = self.time_before
        results['FluenceBeforePeakFlux']    = self.fluence_before  # ph/cm^2
        results['FluenceBeforePeakFlux_ERR']= self.efluence_before # ph/cm^2
        results['FluenceAfterPeakFlux']     = self.fluence_after    # ph/cm^2
        results['FluenceAfterPeakFlux_ERR'] = self.efluence_after   # ph/cm^2
        
        results['TimeAfterPeakFlux']           = self.time_after    
        results['EneFluenceBeforePeakFlux']    = self.enefluence_before  # MeV/cm^2
        results['EneFluenceBeforePeakFlux_ERR']= self.eenefluence_before # MeV/cm^2
        results['EneFluenceAfterPeakFlux']     = self.enefluence_after    # MeV/cm^2
        results['EneFluenceAfterPeakFlux_ERR'] = self.eenefluence_after   # MeV/cm^2
        
        results['T05_L']      = self.t05
        results['T95_L']      = self.t95
        results['AG_F0']      = self.fun.GetParameter(0)
        results['AG_F0_ERR']  = self.fun.GetParError(0)
        results['AG_IN']      = self.fun.GetParameter(1)
        results['AG_IN_ERR']  = self.fun.GetParError(1)
        results['AG_DUR']     = self.t06
        results['AG_DUR_ERRL']= self.t06_l
        results['AG_DUR_ERRU']= self.t06_u
        # Return dictionnary
        self.results=results
        return self.results

       

if __name__ == "__main__":
    BASEDIR='/gpfs/gpfsddn/glast/users/johan/GRB'
    plotter=pExtendedLikePlotter('%s/GRB110731A/like_110731465_P7V6Trans_BKE_GAL0.txt'\
                                 %BASEDIR)
    #plotter.runAll()
    #plotter.plotFullCanvas()
    plotter.plotFluxAndIndex()
    
