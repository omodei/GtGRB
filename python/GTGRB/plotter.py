#!/usr/bin/env python
import sys
import numpy
import array

import pywcs

import math
import astropy.io.fits as pyfits
import os

import genutils
import latutils
from GtBurst import IRFS

import ROOT


#check for matplotlib
HASPYLAB = True
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
SMALL_SIZE = 15
MEDIUM_SIZE = 15
BIGGER_SIZE = 35
plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

cpool                         = [ '#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928','#8e8e8d']

def generateColorMap(ft1):
    reprocVer            = str(ft1[0].header['PROC_VER'])
    #Translate from bitmask to color    
    #Get all IRFS for this reprocessing
    irfs                      = map(lambda x:IRFS.IRFS[x],IRFS.PROCS[reprocVer])
    #Order by evclass
    irfs                      = sorted(irfs,key=lambda x:x.evclass)
    IRFToColor           = IRFS.CaseInsensitiveDict()
    for i,ir in enumerate(irfs):
        #print("%s (%s) -> %s" %(ir.name,ir.evclass,cpool[i]))
        IRFToColor[ir.shortname] = cpool[i]
        pass
    return IRFToColor,reprocVer

def mapEventClassesColors(IRFToColor,reprocVer,classes):
    return map(lambda x:IRFToColor[IRFS.fromEvclassToIRF(reprocVer,x)],classes)



def plotCMAP(lat,size=30,nbins=70,drawopt='cont0z',dlat=10,dlon=10,dlatlab=10,dlonlab=10,energyw=False):
    """
    plot a CountMap for an FT1 file, with the location of the burst as the center of the plot, and the spherical RA,DEC axes drawn
    inputs are:
    lat : the LAT.LAT object
    size : the radius of the ROI, used for histogram boundaries
    nbins : number of bins on histogram axes
    drawopt : ROOT displayy option
    dlat, dlatlab : step of the Latitude axes and labels, respectively
    dlon, dlonlab : step of the Longitude axes and labels, respectively
    """
    file0=lat.evt_file
    if not os.path.exists(lat.evt_file):
        file0=lat.FilenameFT1
    ra0=lat.GRB.ra
    dec0=lat.GRB.dec
    title='GRB'+lat.GRB.Name
    #########################
    # Adjustable parameters #
    #########################
    
##    # angular radius from (ra0,dec0) we want to look at
##    size=30 
##    # time window we want to look at
##    (start,end)=(Ttrig-T90,Ttrig+3.*T90) 
##    # bin size
##    binsize=size/70.
##    # drawing option to plot the count map: col,cont0/1/2/3/4/5,lego/1/2, surf/1/2 ('z' to show the color palette)
##    drawopt='cont0z' 
    
##    dlat=10 # angular interval between each latitude lines (int type)
##    dlon=dlat # angular interval between each longitude lines (int type)
##    dlatlab=dlat #angular interval between each latitude label (multiple of dlat)
##    dlonlab=dlatlab  #angular interval between each longitude label (multiple of dlon)
    
    ##########################
    # read data in fits file #
    ##########################
    
    hdulist=pyfits.open(file0)
    dat=hdulist['EVENTS'].data
    
    RA=dat.field('RA')
    DEC=dat.field('DEC')
    ENERGY=dat.field('ENERGY')

    
##    RA=[]
##    DEC=[]
##    TIME=dat.field('time')
##    for i in range(len(TIME)):
##       t=TIME[i]
##       if start<t<end:
##          RA.append(dat.field('ra')[i])
##          DEC.append(dat.field('dec')[i])
    
    ##############################
    # Rotating coordinate system #
    ##############################
    
    Phi=[]
    Theta=[]
    for i in range(len(RA)):
        (phi, theta) = genutils.getNativeCoordinate( (RA[i], DEC[i]), (ra0,dec0))
        Phi.append(-phi)
        Theta.append(theta)

    hdulist.close()
    
    ###################################
    # Filling data in a 2-D histogram #
    ###################################
    if energyw:  
        histo_name='CountMap_ENE'
        canvas_name='cmap_energy'
        title='LAT Count Map weighted by the log10(Energy)'
    else: 
        histo_name='CountMap'
        canvas_name='cmap_counts'
        title='LAT Count Map'
        pass
    
    h=ROOT.TH2F(histo_name,title,nbins,ra0-size,ra0+size,nbins,dec0-size,dec0+size )
    
    for i in range(len(RA)):
        if(energyw):  h.Fill(Phi[i]+ra0,Theta[i]+dec0,math.log10(ENERGY[i]))
        else:         h.Fill(Phi[i]+ra0,Theta[i]+dec0)
        pass
    ############
    # Plotting #
    ############
    
    c0 = ROOT.TCanvas(canvas_name, title, 280, 210, 700, 500 )
    
    #ROOT.gStyle.SetPalette(1)
    
    h.Draw(drawopt)
    ROOT.SetOwnership(c0,False)
    ROOT.SetOwnership(h,False)

    # Remove ticks, labels on x/y axis
    h.SetTickLength(0,'x')
    h.SetTickLength(0,'y')
    h.SetLabelSize(0,'x')
    h.SetLabelSize(0,'y')
    # Romove stat box
    ROOT.gStyle.SetOptStat(0)

    #####################################
    # Draw longitude and latitude lines #
    #####################################
    
    lat0=int(math.floor(dec0/dlat)*dlat) # 1st latitude below ra0 (multiple of dlat)
    lon0=int(math.floor(ra0/dlon)*dlon) # 1st longitude below dec0 (multiple of dlon)
    if dec0==0:
        sign=+1
    else:
        sign=dec0/math.fabs(dec0)
        pass
    
    tg=[]
    for dy in range(-80,90,dlat):
       tg.append(ROOT.TGraph())
       num = 0
       for dx in range(lon0-180,lon0+180+10,10):
          (phi, theta) = genutils.getNativeCoordinate( (dx, dy), (ra0,dec0) )
          if math.fabs(phi)< 1.5*size and math.fabs(theta)<1.5*size: # to prevent edge effects when latitude lines are drawn
             tg[-1].SetPoint( num, phi+ra0, theta+dec0 )
             num+=1
       if num==0: tg.pop()
    
    for dx in range(0,360,dlon):
      tg.append(ROOT.TGraph())
      num = 0
      for dy in range(lat0-90,lat0+90+10,10):
        (phi, theta) = genutils.getNativeCoordinate( (dx, dy), (ra0,dec0) )
        if math.fabs(phi)<1.5*size and math.fabs(theta)<1.5*size:
           tg[-1].SetPoint( num, -phi+ra0, theta+dec0 )
           num+=1
      if num==0: tg.pop()
      
    for i in range(len(tg)):
       tg[i].SetLineStyle(3)
       tg[i].Draw( "sameC" )
       ROOT.SetOwnership(tg[i],False)

    ################################################
    # Draw labels for latitude and longitude lines #
    ################################################
    
    Latlab=[]
    Lonlab=[]
    
    for lati in range(max(-80,int(lat0/dlatlab)*dlatlab-(int(size/dlatlab)+1)*dlatlab),min(90,int(lat0/dlatlab)*dlatlab+(int(size/dlatlab)+1)*dlatlab),dlatlab):
       (x,y)=genutils.getNativeCoordinate((ra0-0.75*size,lati-1),(ra0,dec0))
       if math.fabs(y)<size*0.95:
          Latlab.append(ROOT.TText(-x+ra0,y+dec0,'%i'%lati))
    
    for lon in range(int(lon0/dlonlab)*dlonlab-(int(size/dlonlab)+1)*dlonlab,int(lon0/dlonlab)*dlonlab+(int(size/dlonlab)+1)*dlonlab,dlonlab):
       (x,y)=genutils.getNativeCoordinate((lon-1.5,dec0-sign*0.75*size),(ra0,dec0))
       if math.fabs(x)<size:
          Lonlab.append(ROOT.TText(-x+ra0,y+dec0,'%i'%(sign*(sign*lon)%360)))
    
    for i in range(len(Latlab)):
       Latlab[i].SetTextColor(15)
       Latlab[i].SetTextSize(0.04)
       Latlab[i].Draw()
       ROOT.SetOwnership(Latlab[i],False)
    for i in range(len(Lonlab)):
       Lonlab[i].SetTextColor(15)
       Lonlab[i].SetTextSize(0.04)
       Lonlab[i].Draw()
       ROOT.SetOwnership(Lonlab[i],False)
    
    h.Draw('same'+drawopt)
    
    ############################
    # Draw cross at (ra0,dec0) #
    ############################
    if lat.GRB.LocalizationError<=0:
        dc=size/50.        
        cross1=ROOT.TLine(ra0-dc,dec0,ra0+dc,dec0)
        cross1.Draw()        
        cross2=ROOT.TLine(ra0,dec0-dc,ra0,dec0+dc)
        cross2.Draw()
        ROOT.SetOwnership(cross1,False)
        ROOT.SetOwnership(cross2,False)
    else:        
        error_circle=ROOT.TEllipse(ra0,dec0,lat.GRB.LocalizationError)
        error_circle.Draw()
        error_circle.SetFillStyle(0)
        error_circle.SetLineStyle(3)
        ROOT.SetOwnership(error_circle,False)
        pass
    # Draw Ttext box with ra&dec of best position estimate
    #text1=ROOT.TText(-150,85,'RA=48.1')
    #text2=ROOT.TText(-150,75,'DEC=-11.7')
    #text1.Draw()
    #text2.Draw()
    
    c0.Update()
    if energyw:  outfile=lat.mp_outFile.replace('_map.fits','_map_E.png')
    else: outfile=lat.mp_outFile.replace('_map.fits','_map.png')

    c0.Print(outfile)
    #c0.Print(outfile.replace('.png','.eps'))
    return c0


def plotLC(det,vline=None):
    lightc = det.lc_outFile

    lightc_png=det.lc_outFile.replace('_lc.fits','_lc.png')
    #lightc_eps=det.lc_outFile.replace('_lc.fits','_lc.eps')

    if not os.path.exists(det.lc_outFile):
        print det.lc_outFile, ' file not found!'
    else:
        print 'plotting lightcurve from ' + lightc
    
        lc=pyfits.open(lightc)
        dat=lc['RATE'].data
        time = dat.field('TIME')
        counts = dat.field('COUNTS')
        lc.close()
        
        start = det.GRB.Ttrigger
        
        binsizes = dat.field('TIMEDEL')
        tstarts = map(lambda x:(x[0]-float(x[1])/2.0)-start,zip(time,binsizes))
        tstops = map(lambda x:x[0]+x[1],zip(tstarts,binsizes))
        bins = list(tstarts)
        bins.append(tstops[-1])
                
        dt = time[1]-time[0]
        name ='can_%s_lc' % det.detector_name
        title='%s' % det.detector_name
        
        title = 'GRB' + det.GRB.Name + ' ' + det.detector_name +' lightcurve'

        lcurve = ROOT.TH1D(title,title,len(tstarts),numpy.array(bins))
        lcurve.Sumw2()
        
        for i,c in enumerate(counts):
            lcurve.SetBinContent(i+1,c)
        
        xtitle = 'Time - %s' % start
        ytitle = 'Counts/(%.2f s)' % dt
        lcurve.SetXTitle(xtitle)
        lcurve.SetYTitle(ytitle)
        
        lcurve.SetTitle(title)
        lcurve.GetXaxis().CenterTitle()
        lcurve.GetYaxis().CenterTitle()

        c0 = ROOT.TCanvas (name,title, 0, 0, 800, 600)
        ROOT.SetOwnership(c0,False)
        ROOT.SetOwnership(lcurve,False)
        ROOT.gStyle.SetOptStat(0)

        
        lcurve.Draw("HIST")    # Do this before drawing graphs
        ROOT.gPad.SetLeftMargin(0.15)
        lcurve.GetYaxis().SetTitleOffset(1.4)
        #        lcurve.SetMarkerStyle(23)
        #        lcurve.SetMarkerColor(ROOT.kRed);
        #lcurve.SetMarkerStyle(20)
        #lcurve.SetFillColor(ROOT.kGray)
        #lcurve.SetLineColor(ROOT.kBlue)        
        #lcurve.Draw('E1')
        
        
        #if(vline is not None):
        #ymax=Hist.GetMaximum();
        
        #tline=ROOT.TLine(0,0,0,ymax)
        #tline.SetLineColor(ROOT.kRed)
        #tline.SetLineStyle(2)
        #tline.Draw()
        c0.Update()
        c0.Print(lightc_png)
        #c0.Print(lightc_eps)
        print 'lc, done'
        return lightc_png,c0

def plotLC_FT1(det,dt):
    ft1_file = det.evt_file
    if not os.path.exists(ft1_file):
        print ft1_file, ' file not found!'
    else:
        print 'plotting lightcurve from ' + ft1_file
        ft1=pyfits.open(ft1_file)
        dat = ft1['EVENTS'].data
        time = dat.field('TIME')
        ft1.close()

        start = det.GRB.TStart
        stop = det.GRB.TStop
        if time[0]>start :
            start = time[0]
        if time[len(time)-1]<stop :
            stop = time[len(time)-1]

        nbins = int((stop-start)/dt)
        title = 'GRB' + det.GRB.Name + ' ' + det.detector_name +' lightcurve'
        h=ROOT.TH1F(title,title,nbins,-dt,stop-start+dt)
            
        for i in range(len(time)):
            if start<time[i]<stop:
                h.Fill(time[i]-start)
                
        c0 = ROOT.TCanvas ('c0', 'lightcurve', 0, 0, 500, 300)
        ROOT.SetOwnership(c0,False)
        ROOT.SetOwnership(h,False)
        ROOT.gStyle.SetOptStat(0)
        
        h.SetXTitle('TIME - MET ' + str(start))
        h.SetYTitle('COUNTS/' + str(dt)+ 'SEC') 
        h.GetXaxis().CenterTitle()
        h.Draw()    # Do this before drawing graphs
        
        c0.Update()

def plotList(list,label,nbins,drawopt=''):
    c0 = ROOT.TCanvas ('c0', label, 0, 0, 500, 300)
    ROOT.SetOwnership(c0,False)
    h=ROOT.TH1F('list','',nbins,0.9*min(list),1.1*max(list) )
    ROOT.SetOwnership(h,False)
    for i in range(len(list)):
        h.Fill(list[i])
    h.Draw(drawopt)
    h.GetXaxis().CenterTitle()
    return h

def plot_confreg_xs(lat,model):
    file = lat.GRB.out_dir+'/LAT_fit_'+model+'.dat'
    if os.path.exists(file):
        ROOT.gROOT.LoadMacro("$IPYTHONDIR/GTGRB/ConfRegion.C+")
        ROOT.ConfRegion(file)
    else:
        print 'file ' + file + ' does not exist\n'

def plot_confreg(lat,e1,e2,e0,norm,gam,Vnn,Vgg,Vgn,factor):
    N = 100
    stepsize = (math.log10(e2) - math.log10(e1))/(N/2-1)

    ret = ROOT.TPolyLine(N+1)

    #factor = 3. # 3 sigma error
    
    gamma = -1.*gam

    fmin = norm * math.pow(e2/e0,-1*gamma)
    fmax = norm * math.pow(e1/e0,-1*gamma)

    for i in range(N/2):
        lE = math.log10(e1) + i*stepsize
        E = math.pow(10.,lE)
        flux = norm * math.pow(E/e0,-1*gamma)
        err = factor*flux*math.sqrt(Vnn/math.pow(norm,2)+math.pow(math.log(E/e0),2.)*Vgg-2.*math.log(E/e0)/norm*Vgn)
        lE = math.log10(E)
        if flux-err > 0:
            lflow = math.log10(flux-err)
        else:
            lflow = math.log10(fmin)-1.
        lfup = math.log10(flux+err)

        ret.SetPoint(i,lE,lflow)
        ret.SetPoint(N-1-i,lE,lfup)
        if i == 0:
            ret.SetPoint(N,lE,lflow)

    ret.SetFillColor(8)
    #ret.SetLineColor(8)


    xlow=math.log10(e1)-1.
    xup=math.log10(e2)+1.
    yup=math.log10(fmax)+1.
    ylow=math.log10(fmin)-1.

    title='GRB' + lat.grb_name + ' confidence region'
    
    h2=ROOT.TH2F(title,title+";log10(E[MeV]);log10(flux[cm^{-2}s^{-1}MeV^{-1}])",100,xlow,xup,100,ylow,yup)
            
    c0 = ROOT.TCanvas ('c0', 'Confidence Region', 0, 0, 500, 500)
    ROOT.SetOwnership(c0,False)
    ROOT.SetOwnership(h2,False)
    ROOT.SetOwnership(ret,False)
    #ROOT.gStyle.SetOptStat(0)
    
    h2.GetXaxis().CenterTitle()
    h2.Draw()    # Do this before drawing graphs

    ret.Draw('f')

    #c0.GetLogx()
    #c0.GetLogy()
    
    c0.Update()

    #pass

def plotLC_PYLAB(det,
                 lcfile='file_lc.fits',
                 evtfile=None,
                 T0=0):
    if not HASPYLAB:
        print 'MATPLOTLIB NOT INSTALLED'
        return
    if lcfile == '' : lcfile=det.lc_outFile
    fin=pyfits.open(lcfile)    
    rates   = fin[1].data
    TIME    = rates.field('TIME')-T0
    TIMEDEL = rates.field('TIMEDEL')
    ERROR   = rates.field('ERROR')
    COUNTS  = rates.field('COUNTS')
    X=TIME#+TIMEDEL/2.
    DX=TIMEDEL
    Y=COUNTS
    DY=ERROR
    
    fig = plt.figure(figsize=(15,15),facecolor='w')
    plt.subplots_adjust(left=0.1, right=0.75, top=0.9, bottom=0.1)
    ax=fig.add_subplot(1,1,1)

    ax.bar(X[COUNTS>0], Y[COUNTS>0], DX[COUNTS>0], color='r', alpha=0.75, yerr=DY[COUNTS>0])
    if T0>0: ax.plot([0,0],[0,max(COUNTS)+max(ERROR)],'k--',color='red')
    plt.xlabel('Time since T0 (s)')
    plt.ylabel('Counts')
    plt.ylim([0,max(COUNTS)+max(ERROR)+1])
    if evtfile is not None:
        ax2 = ax.twinx()
        ft1 = pyfits.open(evtfile)
        events=ft1['EVENTS'].data
        IRFToColor,reprocVer=generateColorMap(ft1)
        #header=table.header    
        #TIME=numpy.array(data['TIME'])-T0
        #ENERGY=numpy.array(data['ENERGY'])
        
        plt.scatter(events.field("TIME")-T0,
                    events.field("ENERGY"),s=20,c=mapEventClassesColors(IRFToColor,reprocVer,classes=events.field("EVENT_CLASS")),
                    picker=0,lw=0)
        if len(events.field("TIME"))<50:
            for t,e in zip(events.field("TIME"),events.field("ENERGY")): print t,t-T0,e
        # Put the legend on top of the figure
        for k,v in IRFToColor.iteritems():
            plt.scatter([0],[0],s=20,lw=0,label=k,c=v)
            pass
        legend=plt.legend(bbox_to_anchor=(1.05, 1), loc=2)
        #legend = plt.legend(scatterpoints=1,
        #                    ncol=2,labelspacing=0.05,
        #                    loc='upper center',
        #                    bbox_to_anchor=(0.3,1.20),
        #                    fancybox=True,)
        
        ltext                     = legend.get_texts()
        plt.setp(ltext, fontsize='small') 
        legend.get_title().set_fontsize('x-small')
        #self.figure.canvas.draw()

        plt.ylabel('Energy [MeV]',size=15)
        plt.yscale('log')
        ax.yaxis.grid(True)
        #ax.xaxis.grid(xgrid)    
        pass
    
    savedfile=lcfile.replace('.fits','.png')
    print 'saving to %s'%savedfile
    plt.savefig(savedfile)
    return

def plotCMAP_PYLAB(lat,map='map.fits',center=None):
    if HASPYLAB:
        print 'lll'
        if map == '' : map=lat.mp_outFile
        map_fit=pyfits.open(map)
        plt.figure()

        nx=map_fit[0].header['NAXIS1']
        ny=map_fit[0].header['NAXIS2']
        x0=map_fit[0].header['CRVAL1']
        y0=map_fit[0].header['CRVAL2']
        dx=map_fit[0].header['CDELT1']
        dy=map_fit[0].header['CDELT2']
        
        print x0+nx/2.*dx,x0-nx/2.*dx,y0-ny/2.*dy,y0+ny/2.*dy
        
        ra=float(center[0])
        dec=float(center[1])
        plt.figure()
        plt.imshow(map_fit[0].data,interpolation='nearest',extent=(x0+nx/2.*dx,x0-nx/2.*dx,y0-ny/2.*dy,y0+ny/2.*dy))
        if center is not None:
            ra=float(center[0])
            dec=float(center[1])
            plt.plot([ra],[dec],'y+',ms=15)
            pass
        plt.colorbar()
        
        #plt.autumn() #	set the default colormap to autumn
        #plt.bone() #	set the default colormap to bone
        #plt.cool() #	set the default colormap to cool
        #plt.copper() #	set the default colormap to copper
        #plt.flag() #	set the default colormap to flag
        #plt.gray() #	set the default colormap to gray
        #plt.hot() #	set the default colormap to hot
        #plt.hsv() #	set the default colormap to hsv
        #plt.jet() #	set the default colormap to jet
        #plt.pink() #	set the default colormap to pink
        #plt.prism() #	set the default colormap to prism
        #plt.spring() #	set the default colormap to spring
        #plt.summer() #	set the default colormap to summer
        #plt.winter() #	set the default colormap to winter
        plt.spectral() #	set the default colormap to spectral
        plt.savefig(map.replace('.fits','.png'))
        # plt.show()
        
        pass
    pass

def oplot_errors(x, y, yerr):
    for xx, yy, err in zip(x, y, yerr):
        if err == yy == 1:
            err = 0.999 # workaround for plotting bug in plt for ylog plots
            pass
        plt.plot([xx, xx], [yy-err, yy+err], 'k-')
    pass

def plotSpectrum_ROOT(likeFit='file_lc.fits'):
    import numarray
    if likeFit == '' :
        likeFit=det.likeFit
        pass
    
    fin=pyfits.open(likeFit)
    #plt.figure()
    
    Counts  = fin['COUNTS_SPECTRA'].data
    EBounds = fin['EBOUNDS'].data
    emin    = EBounds.field('E_MIN')
    emax    = EBounds.field('E_MAX')
    energies   = numarray.sqrt(emax*emin)
    
    xrang = [min(energies)/2., max(energies)*2]
    ymax=-1
    lines=[]
    tg=[]

    GObsCounts=ROOT.TGraphErrors()
    Gresiduals=ROOT.TGraphErrors()
    
    for name in Counts.names:
        print name
        counts=Counts.field(name)
        ymax=max(ymax,counts.max())

        if(name=='ObsCounts'):
            for i in range(len(energies)):
                GObsCounts.SetPoint(i,energies[i], counts[i])
                GObsCounts.SetPointError(i,0.0, math.sqrt(counts[i]))
                pass
            pass
        else:
            tg.append(ROOT.TGraph())
            for i in range(len(energies)):
                tg[-1].SetPoint(i,energies[i], counts[i])
                pass
            pass
        pass
    
    obscounts=Counts.field('ObsCounts')
    modelSum = numarray.zeros(len(obscounts))

    for name in Counts.names:
        print name
        if name != 'ObsCounts':
            counts=Counts.field(name)
            modelSum += counts
            pass
        pass
    GmodelSum=ROOT.TGraph()
    for i in range(len(energies)):
        GmodelSum.SetPoint(i,energies[i], modelSum[i])

    
    residuals = (obscounts - modelSum)/modelSum
    residual_errors = numarray.sqrt(obscounts)/modelSum

    for i in range(len(energies)):
        Gresiduals.SetPoint(i,energies[i], residuals[i])
        Gresiduals.SetPointError(i,0.0, residual_errors[i])
        #print residuals[i],residual_errors[i]
        pass
    # plt.xlabel('Energy (MeV)')

    #GmodelSum.GetXaxis().SetTitle('Energy (MeV)')
    #GmodelSum.GetXaxis().CenterTitle()
    
    # show
    savedfile=likeFit.replace('.fits','.png')
    print 'saving to %s'%savedfile
    c=ROOT.TCanvas('c','Spectral Fit')
    c.Divide(1,2)
    c.cd(1)
    ymax=GmodelSum.GetMaximum()+Gresiduals.GetMaximum()
    ymin=GmodelSum.GetMinimum()
    scale1=ROOT.TGraph(2)
    scale1.SetPoint(0,energies[0],-10)
    scale1.SetPoint(1,energies[-1],+10)
    scale1.GetYaxis().SetTitle('counts / bin')
    scale1.GetYaxis().CenterTitle()
    scale1.Draw('ap')
    scale1.GetXaxis().SetRangeUser(energies[0],energies[-1])
    GmodelSum.Draw('l')
    GObsCounts.Draw('E1')
    
    color=0
    for g in tg:
        g.SetLineStyle(3)
        g.SetLineColor(ROOT.kBlue+color)
        colr=color+1
        g.Draw('l')
        pass
    ROOT.gPad.SetLogx()
    ROOT.gPad.SetLogy()
    c.cd(2)
    scale=ROOT.TGraph(2)
    scale.SetPoint(0,energies[0],-10)
    scale.SetPoint(1,energies[-1],+10)
    scale.GetYaxis().SetTitle('(counts - model) / model')
    scale.GetYaxis().CenterTitle()
    scale.GetXaxis().SetTitle('Energy (MeV)')
    scale.GetXaxis().CenterTitle()
    scale.Draw('ap')
    scale.GetXaxis().SetRangeUser(energies[0],energies[-1])

    Gresiduals.Draw('E1')
    ROOT.gPad.SetLogx()
    #    ROOT.gPad.SetLogy()
    if not ROOT.gROOT.IsBatch():
        a=raw_input('press enter to continue')
        pass
    pass

def plotSpectrum_PYLAB(likeFit='file_lc.fits'):
    if not HASPYLAB:
        print 'MATPLOTLIB NOT INSTALLED'
        return
    if likeFit == '' :
        likeFit=det.likeFit
        pass
    
    fin=pyfits.open(likeFit)
    plt.figure()
    
    Counts  = fin['COUNTS_SPECTRA'].data
    EBounds = fin['EBOUNDS'].data
    emin    = EBounds.field('E_MIN')
    emax    = EBounds.field('E_MAX')
    energies   = plt.sqrt(emax*emin)
    xrang = [min(energies)/2., max(energies)*2]
    ymax=-1
    lines=[]
    
    axUpper = plt.axes((0.1, 0.3, 0.8, 0.6))
    
    for name in Counts.names:
        print name
        counts=Counts.field(name)
        ymax=max(ymax,counts.max())
        
        if(name=='ObsCounts'):

            axUpper.loglog(energies, counts, 'kD', markersize=3,label=name)
            oplot_errors(energies, counts, plt.sqrt(counts))

            #yrange = [min(counts - plt.sqrt(counts))/2, 
            #          max(counts + plt.sqrt(counts))*2]
            yrange = [0.01,max(counts + plt.sqrt(counts))*2]
        else:
            plt.plot(energies,counts,'k--',label=name)
            pass
        pass
    if yrange[0] == 0:
        yrange[0] = 0.5
        pass

    #plt.legend(Counts.names,loc='upper right')

    modelSum = plt.zeros(len(Counts.ObsCounts))
    
    for name in Counts.names:
        if name != 'ObsCounts':
            counts=Counts.field(name)
            modelSum += counts
            pass
        pass
    
    plt.plot(energies, modelSum, 'k')
    plt.axis((xrang[0], xrang[1], yrange[0], yrange[1]))
    plt.ylabel('counts / bin')
    plt.title('Counts Spectra')
    
    residuals = (Counts.ObsCounts - modelSum)/modelSum
    residual_errors = plt.sqrt(Counts.ObsCounts)/modelSum

    axLower = plt.axes((0.1, 0.1, 0.8, 0.2))
    axLower.semilogx(energies, residuals, 'kD', markersize=3)
    oplot_errors(energies, residuals, residual_errors)
    
    plt.plot([xrang[0]/10, xrang[1]*10], [0, 0], 'k--')
    plt.axis((xrang[0], xrang[1], min(residuals - residual_errors)*2, 
                max(residuals + residual_errors)*1.1))

    plt.xlabel('Energy (MeV)')
    plt.ylabel('(counts - model) / model', fontsize=6)
    # show
    savedfile=likeFit.replace('.fits','.png')
    print 'saving to %s'%savedfile
    plt.show()
    return

## Make a plot of the angle between the LAT boresight and the GRB and the Zenith and the GRB as a function of time.

def plotAngSeparation_ROOT(time_grb,MET, AngGRBZenith, AngGRBSCZ, SAA, AngGRBSCZ_0, AngGRBZenith_0):
    obj=[]
    
    earth_ang = 105
    fov_ang   =  75
    c1        =   ROOT.TCanvas("Pointing","Pointing",800,600)
    
    obj.append(c1)
    c1.Divide(1,2)
    
    g1    = ROOT.TGraph()
    g2    = ROOT.TGraph()
    
    g1on  = ROOT.TGraph()
    g2on  = ROOT.TGraph()
    g1off = ROOT.TGraph()
    g2off = ROOT.TGraph()
    
    g3=ROOT.TGraph()

    obj.append(g1)
    obj.append(g2)
    
    obj.append(g1on)
    obj.append(g2on)
    
    obj.append(g1off)
    obj.append(g2off)
    obj.append(g3)
    
    ion = 0
    ioff= 0
    
    for i in range(len(MET)):
        g1.SetPoint(i,MET[i],AngGRBZenith[i])
        g2.SetPoint(i,MET[i],AngGRBSCZ[i])        
        g3.SetPoint(i,MET[i],SAA[i])
        
        if AngGRBZenith[i]<earth_ang and AngGRBSCZ[i] < fov_ang:
            g1on.SetPoint(ion,MET[i],AngGRBZenith[i])
            g2on.SetPoint(ion,MET[i],AngGRBSCZ[i])
            ion  += 1
        else:
            g1off.SetPoint(ioff,MET[i],AngGRBZenith[i])
            g2off.SetPoint(ioff,MET[i],AngGRBSCZ[i])
            ioff += 1
            pass

        pass

    g1.GetXaxis().SetTitle('Time since %i [sec]' % time_grb)
    g1.GetXaxis().CenterTitle()
    g1.GetYaxis().SetTitle('Angle GRB - Zenith (deg)')
    g1.GetYaxis().CenterTitle()
    
    g2.GetXaxis().SetTitle('Time since %i [sec]' % time_grb)
    g2.GetXaxis().CenterTitle()
    g2.GetYaxis().SetTitle('Angle GRB-SCZ (deg)')
    g2.GetYaxis().CenterTitle()

    l1=ROOT.TLine(MET[0],earth_ang,MET[-1],earth_ang)
    l2=ROOT.TLine(MET[0],fov_ang,MET[-1],fov_ang)
    
    obj.append(l1)
    obj.append(l2)
    g1.SetMarkerColor(ROOT.kWhite)
    g2.SetMarkerColor(ROOT.kWhite)
    
    g1on.SetMarkerColor(ROOT.kBlue)
    g2on.SetMarkerColor(ROOT.kBlue)
    
    g1off.SetMarkerColor(ROOT.kRed)
    g2off.SetMarkerColor(ROOT.kRed)
    
    g3.SetMarkerColor(ROOT.kGreen)
    g3.SetMarkerStyle(6)
    
    l1.SetLineColor(ROOT.kRed)
    l2.SetLineColor(ROOT.kRed)

    l1.SetLineStyle(2)
    l2.SetLineStyle(2)

    g1.SetMinimum(-1)
    g2.SetMinimum(-1)

    g1.SetMaximum(180)
    g2.SetMaximum(90)
    
    g1on.SetMarkerStyle(20)
    g2on.SetMarkerStyle(20)
    
    g1off.SetMarkerStyle(20)
    g2off.SetMarkerStyle(20)
    #    g3.SetLineWidth(2)
    l1.SetLineWidth(2)
    l2.SetLineWidth(2)

    c1.cd(1)
    g1.Draw('ap')
    if ion>0: g1on.Draw('p')
    if ioff>0: g1off.Draw('p')    
    g3.Draw('p')
    l1.Draw()
    
    c1.cd(2)
    g2.Draw('ap')
    g2on.Draw('p')
    g2off.Draw('p')
    g3.Draw('p')
    l2.Draw()
    c1.Update()
    #c1.Print('pointing.png')
    #c1.Print('pointing.eps')
    for o in obj: ROOT.SetOwnership(o,False)    
    #if not ROOT.gROOT.IsBatch():
    #    a=raw_input('press enter to continue')
    #    pass
    return c1

def plotAngSeparation_PYLAB(time_grb,MET, AngGRBZenith, AngGRBSCZ, SAA, AngGRBSCZ_0, AngGRBZenith_0,outfile=None,earth_ang=105,fov_ang=75):
    
    myFilter=(AngGRBSCZ<fov_ang)*(AngGRBZenith<earth_ang)
    myFilter_not=numpy.logical_not(myFilter)

    # top plot
    plt.figure(figsize=(15,15),facecolor='w')#    plt.figure()
    plt.subplot(211)
    plt.scatter(MET[myFilter], AngGRBZenith[myFilter],color='b')
    plt.scatter(MET[myFilter_not], AngGRBZenith[myFilter_not],color='r')
    
    # line at the Earth contour
    Earth=plt.plot([MET[0],MET[-1]],[earth_ang,earth_ang],'--',lw=2)
    #plt.maximum(120)
  
    plt.title('Angle of the GRB with the local zenith')
    plt.ylabel('Angle GRB - Zenith (deg)')

    dT=MET[-1]-MET[0]

    plt.xlim(MET[0]-0.1*dT,MET[-1]+0.1*dT)
    plt.ylim(max(0,min(AngGRBZenith)-10),120)
    
    #plt.legend([Earth],['Earth limb'],'upper center')
    
    # bottom plot
  
    plt.subplot(212)
    GRB_SCZ=plt.scatter(MET[myFilter], AngGRBSCZ[myFilter],color='b')
    GRB_SCZ=plt.scatter(MET[myFilter_not], AngGRBSCZ[myFilter_not],color='r')
    #GRB_SCZ=plt.scatter(MET, AngGRBSCZ)
    
    plt.title('Angle of the GRB with the LAT boresight')
    plt.xlabel('TIME-Ttrig (%i)' % time_grb)
    plt.ylabel('Angle GRB-SCZ (deg)')

    dT=MET[-1]-MET[0]
    plt.xlim(MET[0]-0.1*dT,MET[-1]+0.1*dT)
    plt.ylim(0,90)    
    fov=plt.plot([MET[0],MET[-1]],[fov_ang,fov_ang],'--',c='r', lw=2)
    plt.plot(MET,SAA,'.',c='y', lw=3)
    plt.grid(True)
    
    #    plt.subplot(313)
    #    plt.plot(MET, AngRock)
    print 'Angle with respect to the LAT SCZ: %.2f ' % (AngGRBSCZ_0)  
    print 'Angle with respect the Local Zenith :%.2f (%.2f from the Earth Limb) ' % (AngGRBZenith_0,earth_ang-AngGRBZenith_0)  

    #savedfile='GRB_location.png'
    print 'saving to %s' % outfile    
    plt.savefig(outfile)
    print 'done!'
    pass


def PlotTS(tsmap,quick=False,markers=[]):
    '''
    Code by Frederic Piron (piron@in2p3.fr):
    - reads & plots the TS maps produced by gttsmap
    - computes equivalent error radii at different confidence levels 
    
    pywcs code part adapted from "Loading WCS information from a FITS file":
    http://stsdas.stsci.edu/astrolib/pywcs/examples.html#loading-wcs-information-from-a-fits-file
    pywcs doc can be found here:
    http://stsdas.stsci.edu/astrolib/pywcs/
    '''
    
    ############################################
    ### initializations
    ############################################
    # prepare palette for B&W plot
    nRGBs = 2
    ncont = 100
    stops = [ 0.00,  1.00 ]#100% from dark grey to white
    red   = [ 0.30,  1.00 ]
    green = [ 0.30,  1.00 ]
    blue  = [ 0.30,  1.00 ]
    stopsArray = array.array('d', stops)
    redArray   = array.array('d', red)
    greenArray = array.array('d', green)
    blueArray  = array.array('d', blue)
    mycol=ROOT.TColor
    FI=mycol.CreateGradientColorTable(nRGBs, stopsArray, redArray, greenArray, blueArray, ncont)
    colors=[]
    for i in range(ncont):
        colors.append(FI+i)
        colorArray = array.array('i', colors)
        pass
    #ROOT.gStyle.SetNumberContours(50)#uncomment this line to make image contours very smooth
    
    # ROOT style
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPalette(1)

    # pi/180
    pio180=math.pi/180.

    # create file name for final plot
    fout=tsmap.replace('.fits','.png')
    foutbw=tsmap.replace('.fits','BW.png')
    #fout_eps=tsmap.replace('.fits','.eps')
    #foutbw_eps=tsmap.replace('.fits','BW.eps')
    ############################################
    ### load the FITS hdulist, parse the WCS keywords in the primary HDU and get data
    ############################################
    print '<><><><> reading the TS map...'
    hdulist = pyfits.open(tsmap)
    mywcs=pywcs.WCS(hdulist[0].header,key=' ')
    data=hdulist[0].data

    ############################################
    ### store TS map in 2D histogram with same binning / center point
    ############################################
    nbx=mywcs.naxis1
    nby=mywcs.naxis2
    deltax=mywcs.wcs.cdelt[0]
    deltay=mywcs.wcs.cdelt[1]
    xref=mywcs.wcs.crpix[0]
    yref=mywcs.wcs.crpix[1]
    raref=mywcs.wcs.crval[0]
    decref=mywcs.wcs.crval[1]
    print '%d x %d pixellised map with %6.3f deg x %6.3f deg binning, centered at (x, y)=(%6.3f, %6.3f) or (RA, Dec)=(%7.3f, %7.3f)' %(nbx,nby,deltax,deltay,xref,yref,raref,decref)
    xmin=xref-nbx/2.
    xmax=xref+nbx/2.
    ymin=yref-nby/2.
    ymax=yref+nby/2.
    hTS=ROOT.TH2F('hTS','',nbx,xmin,xmax,nby,ymin,ymax)
    for i in range(nbx):
        for j in range(nby):
            hTS.SetBinContent(i+1,j+1,data[j][i])#bin 0 of histogram is for underflow
            pass
        pass
    ROOT.SetOwnership(hTS,False)

    canTSbw=ROOT.TCanvas('canTSbw','',0,0,600,600)
    canTS=ROOT.TCanvas('canTS','',0,600,600,600)
    ROOT.SetOwnership(canTS,False)
    ROOT.SetOwnership(canTSbw,False)
    
    canTS.cd()
    hTS.Draw('ah*colz')
    hTS.SetLabelFont(42,"xyz");
    hTS.SetLabelSize(0.02,"xyz");
    canTS.Update()

    ############################################
    ### find maximum
    ############################################
    grbi=ROOT.Long(0)
    grbj=ROOT.Long(0)
    kkk=ROOT.Long(0)
    hTS.GetMaximumBin(grbi,grbj,kkk)
    grbts=hTS.GetBinContent(grbi,grbj)
    grbx=hTS.GetXaxis().GetBinCenter(grbi)
    grby=hTS.GetYaxis().GetBinCenter(grbj)
    grbpix=numpy.array([[grbx,grby]],numpy.float_)
    grbsky=mywcs.all_pix2sky(grbpix,1)
    grbra=grbsky[0,0]
    grbdec=grbsky[0,1]
    print "Maximum TS=%7.3f in bin (%d, %d) at (x, y)=(%6.3f, %6.3f) or (RA, Dec)=(%7.3f, %7.3f)" %(grbts,grbi,grbj,grbx,grby,grbra,grbdec)

    ############################################
    ### create map of deltaTS and define its contours
    ############################################
    hDTS=ROOT.TH2F('hDTS','',nbx,xmin,xmax,nby,ymin,ymax)
    for i in range(nbx):
        for j in range(nby):
            hDTS.SetBinContent(i+1,j+1,grbts-data[j][i])
            pass
        pass
    ROOT.SetOwnership(hDTS,False)
    if quick:
        deltaTS=[ 2.30, 4.61]#delta_TS values (sorted in increasing order)
        CLprob =[   68,   90]#C.L. levels to probe
        CLdisp =[ True, True]#if false, compute error but do not display
        pass
    else:
        deltaTS=[ 2.30, 4.61,  5.99,  9.21]#delta_TS values (sorted in increasing order)
        CLprob =[   68,   90,    95,    99]#C.L. levels to probe
        CLdisp =[ True, True, False, False]#if false, compute error but do not display
        pass

    hDTS.SetContour(len(CLprob))
    for il in range(len(CLprob)):
        hDTS.SetContourLevel(il,deltaTS[il])
        pass

    ############################################
    ### retrieve the contour graphs and superimpose them on TS map with cross at maximum
    ############################################
    print '<><><><> retrieving and plotting the contour graphs...'
    canTS.cd()
    hDTS.Draw('cont list')#the list options create the list of contour graphs
    canTS.Update()
    hTS.Draw('ah*colz')
    icol=1
    grbpos=ROOT.TMarker(grbx,grby,3)
    grbpos.SetMarkerSize(1)
    grbpos.SetMarkerColor(icol)
    grbpos.Draw()    
    ROOT.SetOwnership(grbpos,False)
    canTS.Update()
    contours=ROOT.gROOT.GetListOfSpecials().FindObject("contours")
    tgcont=[]#tgraphs of C.L. contour in TS map coordinates
    CLprob2=[]#final C.L. levels (some contours might not be found)
    CLdisp2=[]
    area=[]#area of the C.L. contour in RA, Dec coordinates; will be used to compute the final error radii
    #print "Total number of contours: %d" %(contours.GetSize())
    #for il in range(contours.GetSize()):
        #LevelContList=contours.At(il)
        #LevelContNb=LevelContList.GetSize()
        #print "Contour %d has %d graph(s)" %(il,LevelContNb)

    for il in range(contours.GetSize()):
        # add an entry in tables
        area.append(0.)
        CLprob2.append(CLprob[il])
        CLdisp2.append(CLdisp[il])
        # retrieve contour list for the current confidence level
        LevelContList=contours.At(il)
        LevelContNb=LevelContList.GetSize()
        print "<><> %d percent level contour has %d graph(s)" %(CLprob[il],LevelContNb)
        # retrieve first contour
        tgcont.append(ROOT.TGraph())
        tgcont[-1]=LevelContList.First()
        # for this confidence level, look for the contour which contains the GRB position
        foundgraph=False
        for ig in range (LevelContNb):
            if (ig!=0):
                tgcont[-1]=LevelContList.After(tgcont[-1])
            np=tgcont[-1].GetN()
            xp=[]
            yp=[]
            xp=tgcont[-1].GetX()
            yp=tgcont[-1].GetY()
            print "Graph %d has %d points starting at (x, y)= (%6.3f, %6.3f)" %(ig,np,xp[0],yp[0])
            if ((xp[0]!=xp[np-1]) or (yp[0]!=yp[np-1])):
                print "%d percent contour is not closed (contained in the map): error won't be accurate" %(CLprob[il])
            j=np-1
            oddNodes=False
            for i in range(np):
                if ((yp[i]<grby and yp[j]>=grby) or (yp[j]<grby and yp[i]>=grby)):
                    if (xp[i]+(grby-yp[i])/(yp[j]-yp[i])*(xp[j]-xp[i])<grbx):
                        oddNodes=not oddNodes
                        pass
                    pass
                j=i
            if (not oddNodes):#the position does not fall within the contour
                print "Graph %d does not contain the GRB position -> ignored" %(ig)
                pass
            else:
                print "Graph %d contains the GRB position -> let's use that one (and ignore other graphs if any)" %(ig)
                foundgraph=True
                break
        # found graph: set style and draw (if in the list of contours to draw)
        if (foundgraph):
            tgcont[-1].SetLineWidth(1)
            tgcont[-1].SetLineStyle(il+1)
            if CLdisp2[-1]:
                tgcont[-1].Draw("sameL")
                ROOT.SetOwnership(tgcont[-1],False)
            pass
        else:
            print '%d percent C.L. contour was not found' %(CLprob[il])
            tgcont.pop()
            area.pop()
            CLprob2.pop()
            CLdisp2.pop()
            pass
        pass
    canTS.Update()


    # idem in B&W
    canTSbw.cd()
    hTS.Draw('ah*colz')
    grbpos.Draw()    
    for il in range(len(tgcont)):
        if CLdisp2[il]:
            tgcont[il].Draw()
        pass
    canTSbw.Update()

    if len(tgcont)==0:
        print '******** no contour was found: exiting'
        canTS.Print(fout)
        #canTS.Print(fout_eps)
        ROOT.gStyle.SetPalette(ncont,colorArray)
        canTSbw.Print(foutbw)
        #canTSbw.Print(foutbw_eps)
        ROOT.gStyle.SetPalette(1)
        return grbts,grbra,grbdec,0.,0.,0.,0.
        pass

    ############################################
    ### get boundaries of (RA,Dec) map
    ############################################
    print '<><><><> scanning the TS map to get RA and Dec boundaries...'
    raArr=[]
    decArr=[]
    if quick:
        nsubx=nbx
        nsuby=nby
        pass
    else:
        nsubx=10*nbx
        nsuby=10*nby
        pass
    for i in range(nsubx+1):
        pixx=xmin+i*(xmax-xmin)/nsubx
        for j in range(nsuby+1):
            pixy=ymin+j*(ymax-ymin)/nsuby
            pix=numpy.array([[pixx,pixy]],numpy.float_)
            sky=mywcs.all_pix2sky(pix,1)
            raArr.append(sky[0,0])
            decArr.append(sky[0,1])
            pass
        pass
    ramin=min(raArr)
    ramax=max(raArr)
    decmin=min(decArr)
    decmax=max(decArr)
    print 'TS map: RA min / max = %7.3f / %7.3f ; Dec min / max = %7.3f / %7.3f' %(ramin,ramax,decmin,decmax)

    ############################################
    ### draw (RA, Dec) lines
    ############################################
    print '<><><><> drawing the (RA, Dec) lines...'

    frac=0.2#(RA, Dec) grid with ~1/frac lines in each direction

    exp=int(math.log10(ramax-ramin))
    scale=math.pow(10.,1.-exp)
    deltara=int(frac*math.ceil(ramax-ramin)*scale)/scale
    
    exp=int(math.log10(decmax-decmin))
    scale=math.pow(10.,1.-exp)
    deltadec=int(frac*math.ceil(decmax-decmin)*scale)/scale

    print 'ramax-ramin=%f decmax-decmin=%f -> deltara=%f deltadec=%f' %(ramax-ramin,decmax-decmin,deltara,deltadec)

    tgline=[]#RA and Dec lines
    tglinelab=[]#labels for these lines

    fracin=0.05
    xminin=xmin+fracin*(xmax-xmin)
    xmaxin=xmax-fracin*(xmax-xmin)
    yminin=ymin+fracin*(ymax-ymin)
    ymaxin=ymax-fracin*(ymax-ymin)

    dec=decref-int((decref-decmin)/deltadec)*deltadec
    while dec<=decmax:
        tgline.append(ROOT.TGraph())
        num=0
        if deltax>0:
            ra=ramin
        else:
            ra=ramax
        nolabelyet=True
        while (deltax>0 and ra<=ramax) or (deltax<0 and ra>=ramin):
            sky=numpy.array([[ra,dec]],numpy.float_)
            pix=mywcs.wcs_sky2pix(sky,1)
            pixx=ROOT.Double(pix[0,0])
            pixy=ROOT.Double(pix[0,1])
            #print "(ra, dec)=(%f, %f) -> (x, y)=(%f, %f)" %(ra,dec,pixx,pixy)
            if pixx>xmin and pixx<xmax and pixy>ymin and pixy<ymax:#does the current label position fall in the map?
                tgline[-1].SetPoint(num,pixx,pixy)
                num+=1
                if nolabelyet and pixx>xminin and pixx<xmaxin and pixy>yminin and pixy<ymaxin:#no label yet and well in the map?
                    nolabelyet=False
                    tglinelab.append(ROOT.TText(pixx,pixy,'%6.2f'%dec))#Dec line label
                    pass
                pass
            if deltax>0:
                ra+=(ramax-ramin)/1000
            else:
                ra-=(ramax-ramin)/1000
                pass
            pass
        if num==0:
            tgline.pop()
            pass
        dec+=deltadec
        pass

    ra=raref-int((raref-ramin)/deltara)*deltara
    while ra<=ramax:
        tgline.append(ROOT.TGraph())
        num=0
        dec=decmin
        nolabelyet=True
        while dec<=decmax:
            sky=numpy.array([[ra,dec]],numpy.float_)
            pix=mywcs.wcs_sky2pix(sky,1)
            pixx=ROOT.Double(pix[0,0])
            pixy=ROOT.Double(pix[0,1])
            if pixx>xmin and pixx<xmax and pixy>ymin and pixy<ymax:#does the current label position fall in the map?
                tgline[-1].SetPoint(num,pixx,pixy)
                num+=1
                if nolabelyet and pixx>xminin and pixx<xmaxin and pixy>yminin and pixy<ymaxin:#no label yet and well in the map?
                    nolabelyet=False
                    tglinelab.append(ROOT.TText(pixx,pixy,'%6.2f'%ra))#RA line label
                    pass
                pass
            dec+=(decmax-decmin)/1000
            pass
        if num==0:
            tgline.pop()
            pass
        ra+=deltara
        pass

    # draw lines
    for i in range(len(tgline)):
        tgline[i].SetLineStyle(3)
        tgline[i].SetLineColor(19)
        ROOT.SetOwnership(tgline[i],False)

        canTS.cd()
        tgline[i].Draw("sameC" )
        canTS.Update()

        canTSbw.cd()
        tgline[i].Draw("sameC")
        canTSbw.Update()
        pass

    # draw labels
    for i in range(len(tglinelab)):
        tglinelab[i].SetTextColor(19)
        tglinelab[i].SetTextSize(0.02)
        ROOT.SetOwnership(tglinelab[i],False)
        
        canTS.cd()
        tglinelab[i].Draw()
        canTS.Update()

        canTSbw.cd()
        tglinelab[i].Draw("same")
        canTSbw.Update()
        pass

    ############################################
    ### compute error radii
    ############################################
    print '<><><><> computing error radii...'
    np=[]
    xp=[]
    yp=[]
    errok=[]
    for il in range(len(tgcont)):
        np.append(tgcont[il].GetN())
        xp.append(tgcont[il].GetX())
        yp.append(tgcont[il].GetY())
        if ((xp[il][0]!=xp[il][np[il]-1]) or (yp[il][0]!=yp[il][np[il]-1])):
            print "******** %d percent contour is not closed (contained in the map): error won't be accurate" %(CLprob2[il])
            errok.append(0.)
            pass
        else:
            errok.append(1.)
            pass
        pass
    # RA, Dec step is 0.5% of their range; take 1/5th of pixel size if range is too big (e.g. in RA close to the pole)
    if quick:#quick mode, assuming x=RA and Dec=y, which is ~correct only for small scales and far from the pole
        deltara=math.fabs(deltax)
        deltadec=math.fabs(deltay)
        pass
    else:
        deltara=min(0.005*(ramax-ramin),0.2*math.fabs(deltax))
        deltadec=min(0.005*(decmax-decmin),0.2*math.fabs(deltay))
        pass
    print 'Using (RA, Dec) binning of (%f, %f)' %(deltara,deltadec)

    grin=ROOT.TGraph()#plot this tgraph further below to check if areas are correctly computed, i.e. with a binning which is smaller than the size of a pixel in the map
    nin=0
    ntotiter=int((decmax-decmin)/deltadec)
    dniter=int(0.1*ntotiter)
    niter=0
    # loop over RA,Dec infinitesimal bins
    dec=decmin
    while dec<=decmax:
        niter+=1
        if niter%dniter==0:
            per=niter*100./(ntotiter*1.)
            print '%4.0f percent done...' %(per)
            pass
        ra=ramin
        while ra<=ramax:
            #print "(RA, Dec)=(%7.3f, %7.3f)" %(ra,dec)        
            # compute area for the current RA,Dec infinitesimal bin
            pixarea=deltara*math.cos(dec*pio180)*deltadec
            # get projected position in map for the current RA,Dec infinitesimal bin
            sky=numpy.array([[ra,dec]],numpy.float_)
            pix=mywcs.wcs_sky2pix(sky,1)
            pixx=ROOT.Double(pix[0,0])
            pixy=ROOT.Double(pix[0,1])
            # check if this position lies within the C.L. contours
            for il in range(len(tgcont)):
                #see http://root.cern.ch/root/htmldoc/src/TMath.h.html#vuXOW
                #// Function which returns kTRUE if point x,y lies inside the
                #// polygon defined by the np points in arrays xp and yp
                #// Note that the polygon may be open or closed.
                j=np[il]-1
                oddNodes=False
                for i in range(np[il]):
                    if ((yp[il][i]<pixy and yp[il][j]>=pixy) or (yp[il][j]<pixy and yp[il][i]>=pixy)):
                        if (xp[il][i]+(pixy-yp[il][i])/(yp[il][j]-yp[il][i])*(xp[il][j]-xp[il][i])<pixx):
                            oddNodes=not oddNodes
                            pass
                        pass
                    j=i
                if (oddNodes):#the position falls within the contour
                    #print "(RA, Dec)=(%7.3f, %7.3f) -> (x,y)=(%6.3f, %6.3f) is inside (pixarea=%f)" %(ra,dec,pixx,pixy,pixarea)
                    if (il==0):
                        grin.SetPoint(nin,pixx,pixy)
                        nin+=1
                        pass
                    # add the area of the current RA,Dec infinitesimal bin to the total area
                    area[il]+=pixarea
                    pass
                pass
            ra+=deltara
            pass
        dec+=deltadec
        pass

    grin.SetMarkerStyle(19)
    grin.SetMarkerColor(7)
    grin.SetLineColor(7)

    #canTS.cd()
    #grin.Draw("sameP")#uncomment this line to check area computation
    #ROOT.SetOwnership(grin,False)
    #canTS.Update()

    # idem in B&W
    #canTSbw.cd()
    #grin.Draw("sameP")#uncomment this line to check area computation
    #canTSbw.Update()

    err=[]
    for il in range(len(tgcont)):
        area[il]=area[il]*pio180**2.
        # final error radius is the 1/2 angle of the spherical cap with same area as the C.L. contour
        err.append(math.acos(1.-area[il]/(2.*math.pi))*180./math.pi)
        if errok[il]==1:
            print '%d percent C.L. error = %8.4f deg (area = %8.2e sr)' %(CLprob2[il],err[il],area[il])
        else:
            print '%d percent C.L. error = %8.4f deg **** not accurate **** (area = %8.2e sr)' %(CLprob2[il],err[il],area[il])
            pass
        pass

    ############################################
    ### draw error circles
    ############################################
    print '<><><><> drawing the error circles...'
    # burst direction
    cp = math.cos(grbra*pio180)
    sp = math.sin(grbra*pio180)
    ct = math.cos(grbdec*pio180)
    st = math.sin(grbdec*pio180)
    kx=ct*cp
    ky=ct*sp
    kz=st
    
    tgCcont=[]
    for il in range(len(tgcont)):
        tgCcont.append(ROOT.TGraph())
        n2=0
        # start with direction on same meridian, making an angle err[il] with dir
        if grbdec>0:
            ct = math.cos((grbdec-err[il])*pio180)
            st = math.sin((grbdec-err[il])*pio180)
            pass
        else:
            ct = math.cos((grbdec+err[il])*pio180)
            st = math.sin((grbdec+err[il])*pio180)
            pass
        vx=ct*cp
        vy=ct*sp
        vz=st
        # compute scalar product (should be equal to err[il])
        scalprod=vx*kx+vy*ky+vz*kz
        #print 'check err=%f deg scalprod=%f deg' %(err[il],math.acos(scalprod)/pio180)
        vecprodx = ky*vz-kz*vy
        vecprody = kz*vx-kx*vz
        vecprodz = kx*vy-ky*vx
        # create rotated directions around burst direction
        na=1000
        for ia in range(na+1):
            rotang=2.*math.pi*ia/na 
            crot=math.cos(rotang)
            srot=math.sin(rotang)
            # see Rodrigues' rotation formula
            # http://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula
            rvx = vx*crot + vecprodx*srot + kx*scalprod*(1.-crot)
            rvy = vy*crot + vecprody*srot + ky*scalprod*(1.-crot)
            rvz = vz*crot + vecprodz*srot + kz*scalprod*(1.-crot)
            if rvx!=0:
                rra = math.atan(rvy/rvx)/pio180
                if rvx<0:
                    rra+=180
                    pass
                if rra<0:
                    rra+=360#RA is between 0 and 360
                    pass
                pass
            else:
                rra=90
                if rvy<0:
                    rra=270
                    pass
                pass
            rdec=math.asin(rvz)/pio180
            # go back to pixel coordinates
            rsky=numpy.array([[rra,rdec]],numpy.float_)
            rpix=mywcs.wcs_sky2pix(rsky,1)
            rpixx=ROOT.Double(rpix[0,0])
            rpixy=ROOT.Double(rpix[0,1])
            #print "rotang=%f (grbra, grbdec)=(%f, %f) (ra, dec)=(%f, %f) -> (x, y)=(%f, %f)" %(rotang,grbra,grbdec,rra,rdec,rpixx,rpixy)
            tgCcont[il].SetPoint(n2,rpixx,rpixy)
            n2+=1
            pass
        tgCcont[il].SetLineColor(icol)
        tgCcont[il].SetLineWidth(2)
        tgCcont[il].SetLineStyle(il+1)
        canTS.cd()
        if CLdisp2[il]:
            tgCcont[il].Draw("sameL")
            ROOT.SetOwnership(tgCcont[il],False)
        canTS.Update()

        # idem in B&W
        canTSbw.cd()
        if CLdisp2[il]:
            tgCcont[il].Draw("sameL")
        canTSbw.Update()
        pass
    
    ############################################
    ### caption
    ############################################
    caption=ROOT.TPaveText(0.05,0.88,0.55,.98,"NDC");
    caption.SetFillColor(0);
    caption.SetBorderSize(1);
    if err[-1]>1.:
        title='Maximum TS=%5.1f at (RA, Dec)=(%6.2f, %6.2f)' %(grbts,grbra,grbdec)
    else:
        title='Maximum TS=%5.1f at (RA, Dec)=(%7.3f, %7.3f)' %(grbts,grbra,grbdec)
        pass
    caption.AddText(title);
    title='Error radius (deg)'
    first=True
    for il in range(len(tgcont)):
        if CLdisp2[il]:
            if first:
                first=False
                title+=': '
                pass
            else:
                title+=', '
                pass
            if err[-1]>1.:
                title+='%5.2f' %(err[il])
            else:
                title+='%6.3f' %(err[il])
                pass
            
            title+=' ('+str(CLprob2[il])+'%'+')'
            pass

    caption.AddText(title);    

    canTS.cd()
    caption.Draw();
    ROOT.SetOwnership(caption,False)
    canTS.Update()
    
    canTSbw.cd()
    caption.Draw()
    canTSbw.Update()

    ############################################
    ### save final plot
    ############################################
    print '<><><><> saving the image in color and in B&W...'
    canTS.Print(fout)
    #canTS.Print(fout_eps)
    ROOT.gStyle.SetPalette(ncont,colorArray)
    canTSbw.Print(foutbw)
    #canTSbw.Print(foutbw_eps)
    ROOT.gStyle.SetPalette(1)

    ############################################
    ### returned values: best position and errors
    ############################################
    try:
        err68=err[CLprob2.index(68)]
    except:
        err68=0.
    try:
        err90=err[CLprob2.index(90)]
    except:
        err90=0.
    try:
        err95=err[CLprob2.index(95)]
    except:
        err95=0.
    try:
        err99=err[CLprob2.index(99)]
    except:
        err99=0.

    print '<><><><> done!'
    
    return grbts,grbra,grbdec,err68,err90,err95,err99


if __name__=='__main__':
    import sys
    PlotTS(sys.argv[1])
