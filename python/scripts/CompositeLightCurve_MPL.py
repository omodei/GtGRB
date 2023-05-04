#!/usr/bin/env python
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import astropy.io.fits as pyfits
import scipy as sp

def Swift_Binned(File,TRIGTIME): # TRIGTIME IS THE MET CORRESPOINDING TO THE SWIFT UTC TRIGGER - GBM TRIGGERTIME
    T   = []
    DT0 = []
    DT1 = []
    Y   = []
    DY0 = []
    DY1 = []
    for l in file(File,'r').readlines():
        values= l.split()
        #print float(values[0])+TRIGTIME, float(values[3]), values
        T.append(float(values[0])+TRIGTIME)
        DT0.append(sp.fabs(float(values[1])))
        DT1.append(sp.fabs(float(values[2])))
        Y.append(1e6*float(values[3]))
        DY0.append(1e6*sp.fabs(float(values[4])))
        DY1.append(1e6*sp.fabs(float(values[5])))
        pass
    
    return sp.array(T),sp.array(DT0),sp.array(DT1),sp.array(Y),sp.array(DY0),sp.array(DY1),

def Swift_Fits(File,TRIGTIME,DELTATRIGGER): # TRIGTIME IS THE MET CORRESPOINDING TO THE SWIFT UTC TRIGGER - GBM TRIGGERTIME
    T   = []
    DT  = []
    Y   = []
    DY  = []
    f=pyfits.open(File)
    d=f[1].data
    time = d['time']-TRIGTIME+DELTATRIGGER-17.25
    DT   = time[1:]-time[:-1]
    T    = time[:-1]+DT/2.
    #T = d['time']-TRIGTIME-17.25
    print 'size:',(d['rate'][:,1]).size
    Y = (d['RATE'][:-1,1]+d['RATE'][:-1,2])*DT
    DY = (d['ERROR'][:-1,1]+d['ERROR'][:-1,2])*DT
    #print '--------------------------------------------------'
    #for t,y in zip(T,Y): print t,y
    #print '--------------------------------------------------'
    return sp.array(T),sp.array(DT),sp.array(Y),sp.array(DY)


def GBM_EVENTS(File,Emin=0,Emax=40000,TRIGTIME=None):
    ifile=pyfits.open(File)
    table=ifile['EVENTS']
    EVENTS=table.data
    HEADER=table.header
    if TRIGTIME is None: TRIGTIME=HEADER['TRIGTIME']
    print 'GBM TRIGTIME=',TRIGTIME
    EBOUNDS=ifile['EBOUNDS'].data
    CHANNEL=EBOUNDS.field('CHANNEL')
    E_MIN=EBOUNDS.field('E_MIN')
    E_MAX=EBOUNDS.field('E_MAX') 
    if Emin<E_MIN[0]: Emin = E_MIN[0]
    if Emax>E_MAX[-1]: Emax = E_MAX[-1]

    chmin = sp.argmax(E_MAX>Emin)
    chmax = sp.argmax(E_MAX>Emax)
    EMIN = E_MIN[chmin]
    EMAX = E_MAX[chmax]
    print 'SELECTED EMIN=%s, EMAX=%s' %(EMIN,EMAX)    
    TIME=EVENTS.field('TIME')-TRIGTIME
    PHA =EVENTS.field('PHA')
    TIME=TIME[(PHA>chmin) * (PHA<chmax)]
    return TIME

def GBM_BINNED(File,Emin=0,Emax=40000,TRIGTIME=None):
    ifile=pyfits.open(File)
    print '====>',File, ifile.info()
    SPECTRUM=ifile['SPECTRUM'].data
    #print dir(SPECTRUM)
    #print SPECTRUM.names
    COUNTS=SPECTRUM.field('COUNTS')
    if TRIGTIME is None: TRIGTIME=HEADER['TRIGTIME']
    print 'GBM TRIGTIME=',TRIGTIME
    EBOUNDS=ifile['EBOUNDS'].data
    CHANNEL=EBOUNDS.field('CHANNEL')
    E_MIN=EBOUNDS.field('E_MIN')
    E_MAX=EBOUNDS.field('E_MAX') 
    chmin = sp.argmax(E_MAX>Emin)
    chmax = sp.argmax(E_MAX>Emax)
    EMIN = E_MIN[chmin]
    EMAX = E_MAX[chmax]
    print 'SELECTED EMIN=%s, EMAX=%s, (%d-%d)' %(EMIN,EMAX,chmin,chmax)    
    X=SPECTRUM.field('TIME')-TRIGTIME
    DX=SPECTRUM.field('ENDTIME')-SPECTRUM.field('TIME')
    Y=sp.sum(COUNTS[:,chmin:chmax],axis=1)/SPECTRUM.field('EXPOSURE')
    #print COUNTS.shape
    #print X.shape
    #print Y.shape

    return X,DX,Y
    
def LLE_EVENTS(File,Emin=0,Emax=1e6,TRIGTIME=None):
    table=pyfits.open(File)['EVENTS']
    data=table.data
    header=table.header
    #print header
    print 'LLE: TRIGTIME in HEADER...:',header['TRIGTIME']
    if TRIGTIME is None: TRIGTIME=header['TRIGTIME']
    TIME=sp.array(data['TIME'])-TRIGTIME
    ENERGY=sp.array(data['ENERGY'])
    
    TIME=TIME[(ENERGY>Emin) * (ENERGY<Emax)]
    return TIME

def LAT_EVENTS(File,Emin=0,Emax=1e6,TRIGTIME=0):
    table  = pyfits.open(File)['EVENTS']
    data   = table.data
    header = table.header    
    print data.names
    TIME   = sp.array(data['TIME'])-TRIGTIME
    ENERGY = sp.array(data['ENERGY'])
    try:    PROBABILITY=sp.array(data['GRB'])
    except: PROBABILITY=sp.ones(len(TIME))

    TIME        = TIME[(ENERGY>Emin) * (ENERGY<Emax)]
    PROBABILITY = PROBABILITY[(ENERGY>Emin) * (ENERGY<Emax)]
    ENERGY      = ENERGY[(ENERGY>Emin) * (ENERGY<Emax)]

    return TIME,ENERGY,PROBABILITY
    
class CompositeLC():
    def __init__(self,TRIGTIME,TMIN=-22,TMAX=290,DT=1.0):
        self.TMIN = TMIN
        self.TMAX = TMAX
        self.BINS = int((self.TMAX-self.TMIN)/DT)
        # THESE ARE TTE FILES        
        self.NaIFiles1=None
        self.BGOFiles1=None
        self.LLEFiles1=None
        self.LATFiles1=None
        self.NaIFiles2=None
        self.BGOFiles2=None
        self.LLEFiles2=None
        self.LATFiles2=None
        # THESE ARE CSPEC FILES        
        self.NaIFilesB1=None
        self.BGOFilesB1=None
        self.NaIFilesB2=None
        self.BGOFilesB2=None
        
        self.NaIEmin1=None
        self.BGOEmin1=None
        self.LLEEmin1=None
        self.LATEmin1=None
        self.NaIEmin2=None
        self.BGOEmin2=None
        self.LLEEmin2=None
        self.LATEmin2=None
        self.NaIEmax1=None
        self.BGOEmax1=None
        self.LLEEmax1=None
        self.LATEmax1=None
        self.NaIEmax2=None
        self.BGOEmax2=None
        self.LLEEmax2=None
        self.LATEmax2=None
        self.Swift=None
        self.fill=True
        self.fill_color='silver'
        self.plotLATLC=False

        self.colors={'LAT1':'gray',
                     'LAT2':'r',
                     'NaI1':'c',
                     'NaI2':'lightblue',
                     'BGO1':'g',
                     'BGO2':'g',
                     'LLE1':'b',
                     'LLE2':'r'} 
        self.colors={'LAT1':'gray',
                     'LAT2':'gray',
                     'NaI1':'gray',
                     'NaI2':'gray',
                     'BGO1':'gray',
                     'BGO2':'gray',
                     'LLE1':'gray',
                     'LLE2':'gray'}
        self.colors={'LAT1':'k',
                     'LAT2':'k',
                     'NaI1':'k',
                     'NaI2':'k',
                     'BGO1':'k',
                     'BGO2':'k',
                     'LLE1':'k',
                     'LLE2':'k'}
       #self.colors={'LAT1':'cyan',
        #             'LAT2':'cyan',
        #             'NaI1':'cyan',
        #             'NaI2':'cyan',
        #             'BGO1':'cyan',
        #             'BGO2':'cyan',
        #             'LLE1':'cyan',
        #             'LLE2':'cyan'}
        
        self.TRIGTIME=TRIGTIME
        self.NP=0
        self.xlabel='Time since t$_{0}$ [s]'
        pass
    
    def SetSwift(self,Swift,Swift_TTime,Swift_Legend):
        print 'setting swift...'
        self.Swift        = Swift
        self.Swift_TTime  = Swift_TTime
        self.Swift_Legend = Swift_Legend
        #self.NP+=1
        pass
    
    def SetNaI1(self,NaIFiles,Emin,Emax):
        self.NaIFiles1 = NaIFiles
        self.NaIEmin1 = Emin
        self.NaIEmax1 = Emax
        self.NP+=1
        pass

    def SetBGO1(self,BGOFiles,Emin,Emax):
        self.BGOFiles1 = BGOFiles
        self.BGOEmin1 = Emin
        self.BGOEmax1 = Emax
        self.NP+=1
        pass
    
    def SetNaIB1(self,NaIFiles,Emin,Emax):
        self.NaIFilesB1 = NaIFiles
        self.NaIEmin1 = Emin
        self.NaIEmax1 = Emax
        self.NP+=1
        pass
    
    def SetBGOB1(self,BGOFiles,Emin,Emax):
        self.BGOFilesB1 = BGOFiles
        self.BGOEmin1 = Emin
        self.BGOEmax1 = Emax
        self.NP+=1
        pass

    def SetLLE1(self,LLEFiles,Emin,Emax):
        self.LLEFiles1 = LLEFiles
        self.LLEEmin1 = Emin
        self.LLEEmax1 = Emax
        self.NP+=1
        pass

    def SetLAT1(self,LATFiles,Emin,Emax):
        self.LATFiles1 = LATFiles
        self.LATEmin1 = Emin
        self.LATEmax1 = Emax
        self.NP+=1
        pass
    ##################################################
    def SetNaI2(self,NaIFiles,Emin,Emax):
        self.NaIFiles2 = NaIFiles
        self.NaIEmin2 = Emin
        self.NaIEmax2 = Emax
        self.NP+=1
        pass
    
    def SetBGO2(self,BGOFiles,Emin,Emax):
        self.BGOFiles2 = BGOFiles
        self.BGOEmin2 = Emin
        self.BGOEmax2 = Emax
        self.NP+=1
        pass

    def SetNaIB2(self,NaIFiles,Emin,Emax):
        self.NaIFilesB2 = NaIFiles
        self.NaIEmin2 = Emin
        self.NaIEmax2 = Emax
        self.NP+=1
        pass
    
    def SetBGOB2(self,BGOFiles,Emin,Emax):
        self.BGOFilesB2 = BGOFiles
        self.BGOEmin2 = Emin
        self.BGOEmax2 = Emax
        self.NP+=1
        pass

    def SetLLE2(self,LLEFiles,Emin,Emax):
        self.LLEFiles2 = LLEFiles
        self.LLEEmin2 = Emin
        self.LLEEmax2 = Emax
        self.NP+=1
        pass

    def SetLAT2(self,LATFiles,Emin,Emax):
        self.LATFiles2 = LATFiles
        self.LATEmin2 = Emin
        self.LATEmax2 = Emax
        self.NP+=1
        pass
       
    def SetOutput(self,output):
        self.output=output
        pass

    def Plot(self,rebin=False,vertical_lines=[]):
        def getUnits(value,ubase):
            units=['ev','keV','MeV','GeV','TeV']                        
            for idx,k in enumerate(units):
                if k==ubase: break
                pass       
            if value<1000:  return value,units[idx]
            return getUnits(value/1000,units[idx+1])
        
        def label(detector,emin,emax,ubase):
            emin,umin=getUnits(emin,ubase)
            emax,umax=getUnits(emax,ubase)
            if umin==umax:
                return '%s [%d - %d %s]' % (detector,emin,emax,umax)
            else:
                return '%s [%d %s - %d %s]' % (detector,emin,umin,emax,umax)


        if self.NP==0: return None
        TIME_BINS=sp.linspace(self.TMIN,self.TMAX,self.BINS)        
        if rebin: TIME_BINS_REBIN=sp.array(vertical_lines)
        
        figsize=(10,3*self.NP)
        #figsize=(5,9)
        #figsize=(6,14)
        fig=plt.figure(figsize=figsize,facecolor='w')
        # #################################################
        Panel=1
        ToShare=None
        # #################################################
        vlines_color='k:'
        xgrid=False
        ygrid=True
        line_0=1
        # #################################################
        # First precedence to CSPEC file, if any...
        if self.NaIFilesB1 is not None:
            log_scale=True
            print 'NaIFilesB1: found %s file' % self.NaIFilesB1
            ax=plt.subplot(self.NP,1,Panel)
            if Panel==1: ToShare=ax
            Emin,Emax=self.NaIEmin1,self.NaIEmax1
            X=sp.array([])
            Y=sp.array([])
            DX=sp.array([])
            for f in self.NaIFilesB1:
                _X,_DX,_Y=GBM_BINNED(f,Emin=Emin,Emax=Emax,TRIGTIME=self.TRIGTIME)
                X=_X
                DX=_DX
                if Y.shape[0]==0: Y=_Y
                else: Y+=_Y
                pass
            
            plt.bar(X,Y,DX,edgecolor=self.colors['NaI1'],alpha=0.75,linewidth=0,label=label('NaI',Emin,Emax,'keV'),log=log_scale,fill=self.fill)
            plt.xlim([self.TMIN,self.TMAX])
            if log_scale: ymin=0.9*Y.mean()
            else: ymin=0.9*Y.min()
            ymax=1.1*Y.max()
            plt.ylim([ymin,ymax])
            plt.legend(frameon=0)
            ax.xaxis.grid(xgrid)
            #ax.title.set_visible(False)
            #ax.xlabels.set_visible(False)
            #plt.setp(ax.get_xticklines(),visible=False)
            #plt.xticks(size=0)                
            plt.ylabel('Count rate (ph/s)',size=15)
            if log_scale: plt.yscale('log')
            if line_0: plt.plot([0,0],[ymin,ymax],'r--')
            for x in vertical_lines: plt.plot([x,x],[ymin,ymax],vlines_color)
            Panel+=1
            pass
        if self.NaIFilesB2 is not None:
            log_scale=True
            print 'NaIFilesB2: found %s file' % self.NaIFilesB2
            ax=plt.subplot(self.NP,1,Panel)
            if Panel==1: ToShare=ax
            Emin,Emax=self.NaIEmin2,self.NaIEmax2
            X=sp.array([])
            Y=sp.array([])
            DX=sp.array([])
            for f in self.NaIFilesB2:
                _X,_DX,_Y=GBM_BINNED(f,Emin=Emin,Emax=Emax,TRIGTIME=self.TRIGTIME)
                X=_X
                DX=_DX
                if Y.shape[0]==0: Y=_Y
                else: Y+=_Y
                pass
            plt.bar(X,Y,DX,edgecolor=self.colors['NaI2'],alpha=0.75,linewidth=1,label=label('NaI',Emin,Emax,'keV'),log=log_scale,fill=self.fill)
            plt.xlim([self.TMIN,self.TMAX])
            if log_scale: ymin=0.9*Y.mean()
            else: ymin=0.9*Y.min()
            ymax=1.1*Y.max()
            plt.ylim([ymin,ymax])
            plt.legend(frameon=0)
            ax.xaxis.grid(xgrid)
            #ax.title.set_visible(False)
            #ax.xlabels.set_visible(False)
            #plt.setp(ax.get_xticklines(),visible=False)
            #plt.xticks(size=0)                
            plt.ylabel('Count rate (ph/s)',size=15)
            if log_scale: plt.yscale('log')
            if line_0: plt.plot([0,0],[ymin,ymax],'r--')
            for x in vertical_lines: plt.plot([x,x],[ymin,ymax],vlines_color)
            Panel+=1
            pass
        # #################################################
        
        if 1==0:#self.NaIFiles1 is not None:
            ax=plt.subplot(self.NP,1,Panel)
            if Panel==1: ToShare=ax
            NAI_EVT=sp.array([],dtype=sp.float64)
            Emin,Emax=self.NaIEmin1,self.NaIEmax1

            for iFile in self.NaIFiles1:   NAI_EVT=sp.append(NAI_EVT,GBM_EVENTS(iFile,TRIGTIME=self.TRIGTIME,Emin=Emin,Emax=Emax))    

            hist,bin_edges=sp.histogram(NAI_EVT,TIME_BINS)
            X=bin_edges[:-1]
            DX=(bin_edges[1:]-bin_edges[:-1])
            Y=hist/DX
            plt.bar(X,Y,DX,edgecolor=self.colors['NaI1'],alpha=0.75,linewidth=0,label=label('NaI',Emin,Emax,'keV'))
            #plt.setp(ax.get_xticklines(),visible=False)
            plt.xlim([self.TMIN,self.TMAX])
            plt.ylim([0.9*Y.min(),1.1*Y.max()])
            plt.legend(frameon=0)
            ax.xaxis.grid(xgrid)
            #ax.title.set_visible(False)
            #ax.xlabels.set_visible(False)
            #plt.setp(ax.get_xticklines(),visible=False)
            #plt.xticks(size=0)                
            plt.ylabel('Count rate (ph/s)',size=15)
            if line_0: plt.plot([0,0],[0.9*Y.min(),1.1*Y.max()],'r--')
            for x in vertical_lines: plt.plot([x,x],[0.9*Y.min(),1.1*Y.max()],vlines_color)

            if rebin:
                hist,bin_edges=sp.histogram(NAI_EVT,TIME_BINS_REBIN)
                DX=(bin_edges[1:]-bin_edges[:-1])
                X=bin_edges[:-1]+DX/2.

                Y=hist/DX
                plt.bar(X,Y,DX,color=(0, 0, 0, 0.0),linewidth=1,edgecolor='k',label=None)
                pass                    

            Panel+=1
            pass
        # ##################################################
        if self.Swift is not None:
            ax=plt.subplot(self.NP,1,Panel)
            #ax2 = ax.twinx()
            #if Panel==1: ToShare=ax
            #X,DX0,DX1,Y,DY0,DY1=Swift_Binned(self.Swift,self.Swift_TTime-self.TRIGTIME)
            X,DX,Y,DY=Swift_Fits('sw00883832000b_4chan_64ms.lc',self.Swift_TTime,self.Swift_TTime-self.TRIGTIME)
            #plt.errorbar(X,Y,xerr=[DX0,DX1],yerr=[DY0,DY1],alpha=0.75,marker=None,label=self.Swift_Legend,c='k',ls='-')
            #C=Y.max()/Y2.max()
            #plt.errorbar(X,Y,xerr=[DX02,DX12],yerr=[DY02,DY12],alpha=0.75,marker=None,label=self.Swift_Legend,c='k',ls='-')
            #plt.errorbar(X,Y,xerr=[DX0,DX1],yerr=[0*DY0,0*DY1],alpha=0.75,marker=None,label=self.Swift_Legend,c='k',ls='-')
            #plt.step(X,Y,xerr=[DX0,DX1],yerr=[DY0,DY1],alpha=0.75,fmt='.',label=self.Swift_Legend,c='k')
            plt.step(X,Y,where='mid',color='k',label=self.Swift_Legend)
            if self.fill: plt.fill_between(X,Y,step='mid',color=self.fill_color)

            plt.xlim([self.TMIN,self.TMAX])
            plt.ylim([0.9*Y.min(),1.1*Y.max()])
            plt.legend(frameon=0,loc=(0.72,0.78))
            plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0),useOffset=True)
            plt.ylabel(r'Counts/detector',size=13)
            #plt.ylabel(r'Flux [$\times$10$^{-6}$ cm$^{-2}$ s$^{-1}$]',size=13)
            #ax.xaxis.grid(xgrid)
            #plt.xticks(size=0)                
            #plt.ylabel('Count rate (ph/s)',size=15)
            if line_0: plt.plot([0,0],[0.9*Y.min(),1.1*Y.max()],'r--')
            #for x in vertical_lines: plt.plot([x,x],[0.9*Y.min(),1.1*Y.max()],vlines_color)
            Panel+=1
            pass

        ##################################################
        if self.NaIFiles2 is not None:
            ax=plt.subplot(self.NP,1,Panel)
            if Panel==1: ToShare=ax
            NAI_EVT=sp.array([])
            Emin,Emax=self.NaIEmin2,self.NaIEmax2
            for iFile in self.NaIFiles2:   NAI_EVT=sp.append(NAI_EVT,GBM_EVENTS(iFile,TRIGTIME=self.TRIGTIME,Emin=Emin,Emax=Emax))
            hist,bin_edges=sp.histogram(NAI_EVT,TIME_BINS)
            X=bin_edges[:-1]
            DX=(bin_edges[1:]-bin_edges[:-1])
            Y=hist/DX
            #plt.bar(X,Y,DX,edgecolor=self.colors['NaI2'],alpha=0.75,linewidth=1,label=label('NaI',Emin,Emax,'keV'))
            plt.step(X,Y,DX,where='mid',color=self.colors['NaI2'],label=label('NaI',Emin,Emax,'keV'))
            if self.fill: plt.fill_between(X,Y,step='mid',color=self.fill_color)
            plt.xlim([self.TMIN,self.TMAX])
            plt.ylim([0.9*Y.min(),1.1*Y.max()])
            plt.legend(frameon=0)
            ax.xaxis.grid(xgrid)
            #plt.xticks(size=0)                
            plt.ylabel('Count rate [Hz]',size=15)
            if line_0: plt.plot([0,0],[0.9*Y.min(),1.1*Y.max()],'r--')
            for x in vertical_lines: plt.plot([x,x],[0.9*Y.min(),1.1*Y.max()],vlines_color)
            if rebin:
                hist,bin_edges=sp.histogram(NAI_EVT,TIME_BINS_REBIN)
                DX=(bin_edges[1:]-bin_edges[:-1])
                X=bin_edges[:-1]+DX/2.           
                Y=hist/DX
                plt.bar(X,Y,DX,color=(0, 0, 0, 0.0),linewidth=1,edgecolor='k',label=None)
                pass  
            Panel+=1
            pass
        
        # #################################################
        # First precedence to CSPEC file, if any...
        if self.BGOFilesB1 is not None:
            log_scale=True
            print 'BGOFilesB1: found %s file' % self.BGOFilesB1
            ax=plt.subplot(self.NP,1,Panel)
            if Panel==1: ToShare=ax
            Emin,Emax=self.BGOEmin1,self.BGOEmax1
            X=sp.array([])
            Y=sp.array([])
            DX=sp.array([])
            for f in self.BGOFilesB1:
                _X,_DX,_Y=GBM_BINNED(f,Emin=Emin,Emax=Emax,TRIGTIME=self.TRIGTIME)
                X=_X
                DX=_DX
                if Y.shape[0]==0: Y=_Y
                else: Y+=_Y
                pass

            plt.bar(X,Y,DX,edgecolor=self.colors['BGO1'],alpha=0.75,linewidth=1,label=label('BGO',Emin,Emax,'keV'),log=log_scale,fill=self.fill)
            plt.xlim([self.TMIN,self.TMAX])
            if log_scale: ymin=0.9*Y.mean()
            else: ymin=0.9*Y.min()
            ymax=1.1*Y.max()
            plt.ylim([ymin,ymax])
            plt.legend(frameon=0)
            ax.xaxis.grid(xgrid)
            #ax.title.set_visible(False)
            #ax.xlabels.set_visible(False)
            #plt.setp(ax.get_xticklines(),visible=False)
            #plt.xticks(size=0)                
            plt.ylabel('Count rate [Hz]',size=15)
            if log_scale: plt.yscale('log')
            if line_0: plt.plot([0,0],[ymin,ymax],'r--')
            for x in vertical_lines: plt.plot([x,x],[ymin,ymax],vlines_color)
            Panel+=1
            pass
        if self.BGOFilesB2 is not None:
            log_scale=True
            print 'BGOFilesB2: found %s file' % self.BGOFilesB2
            ax=plt.subplot(self.NP,1,Panel)
            if Panel==1: ToShare=ax
            Emin,Emax=self.BGOEmin2,self.BGOEmax2
            X=sp.array([])
            Y=sp.array([])
            DX=sp.array([])
            for f in self.BGOFilesB2:
                _X,_DX,_Y=GBM_BINNED(f,Emin=Emin,Emax=Emax,TRIGTIME=self.TRIGTIME)
                X=_X
                DX=_DX
                if Y.shape[0]==0: Y=_Y
                else: Y+=_Y
                pass
            
            plt.bar(X,Y,DX,edgecolor=self.colors['BGO2'],alpha=0.75,linewidth=1,label=label('BGO',Emin,Emax,'keV'),log=log_scale,fill=self.fill)
            plt.xlim([self.TMIN,self.TMAX])
            if log_scale: ymin=0.9*Y.mean()
            else: ymin=0.9*Y.min()
            ymax=1.1*Y.max()
            plt.ylim([ymin,ymax])
            plt.legend(frameon=0)
            ax.xaxis.grid(xgrid)
            #ax.title.set_visible(False)
            #ax.xlabels.set_visible(False)
            #plt.setp(ax.get_xticklines(),visible=False)
            #plt.xticks(size=0)                
            plt.ylabel('Count rate [Hz]',size=15)
            if log_scale: plt.yscale('log')
            if line_0: plt.plot([0,0],[ymin,ymax],'r--')
            for x in vertical_lines: plt.plot([x,x],[ymin,ymax],vlines_color)
            Panel+=1
            pass


        ##################################################
        if self.BGOFiles1 is not None:    
            if Panel==1:
                ax=plt.subplot(self.NP,1,Panel)
                ToShare=ax
            else: ax=plt.subplot(self.NP,1,Panel,sharex=ToShare)
            Emin,Emax=self.BGOEmin1,self.BGOEmax1
            BGO_EVT=sp.array([])
            for iFile in self.BGOFiles1:   BGO_EVT=sp.append(BGO_EVT,GBM_EVENTS(iFile,TRIGTIME=self.TRIGTIME,Emin=Emin,Emax=Emax))
            hist,bin_edges=sp.histogram(BGO_EVT,TIME_BINS)
            X=bin_edges[:-1]
            DX=(bin_edges[1:]-bin_edges[:-1])
            Y=hist/DX
            #plt.bar(X,Y,DX,edgecolor=self.colors['BGO1'],alpha=0.75,linewidth=1,label=label('BGO',Emin,Emax,'keV'))
            plt.step(X,Y,DX,where='mid',color=self.colors['BGO1'],label=label('BGO',Emin,Emax,'keV'))
            if self.fill: plt.fill_between(X,Y,step='mid',color=self.fill_color)

            plt.xlim([self.TMIN,self.TMAX])
            plt.ylim([0.9*Y.min(),1.1*Y.max()])
            plt.legend(frameon=0)
            ax.xaxis.grid(xgrid)
            #plt.xticks(size=0)                
            plt.ylabel('Count rate [Hz]',size=15)
            if line_0: plt.plot([0,0],[0.9*Y.min(),1.1*Y.max()],'r--')
            for x in vertical_lines: plt.plot([x,x],[0.9*Y.min(),1.1*Y.max()],vlines_color)
            if rebin:
                hist,bin_edges=sp.histogram(BGO_EVT,TIME_BINS_REBIN)
                DX=(bin_edges[1:]-bin_edges[:-1])
                X=bin_edges[:-1]+DX/2.       
                Y=hist/DX
                plt.bar(X,Y,DX,color=(0, 0, 0, 0.0),linewidth=1,edgecolor='k',label=None)
                pass  
            Panel+=1
            pass
        ##################################################
        if self.BGOFiles2 is not None:        
            if Panel==1:
                ax=plt.subplot(self.NP,1,Panel)
                ToShare=ax
            else: ax=plt.subplot(self.NP,1,Panel,sharex=ToShare)
            Emin,Emax=self.BGOEmin2,self.BGOEmax2
            BGO_EVT=sp.array([])
            for iFile in self.BGOFiles2:   BGO_EVT=BGO_EVT=sp.append(BGO_EVT,GBM_EVENTS(iFile,TRIGTIME=self.TRIGTIME,Emin=Emin,Emax=Emax))
            hist,bin_edges=sp.histogram(BGO_EVT,TIME_BINS)
            X=bin_edges[:-1]
            DX=(bin_edges[1:]-bin_edges[:-1])
            Y=hist/DX
            plt.bar(X,Y,DX,edgecolor=self.colors['BGO2'],alpha=0.75,linewidth=1,label=label('BGO',Emin,Emax,'keV'))
            plt.xlim([self.TMIN,self.TMAX])
            plt.ylim([0.9*Y.min(),1.1*Y.max()])
            plt.legend(frameon=0)
            ax.xaxis.grid(xgrid)
            #plt.xticks(size=0)                
            plt.ylabel('Count rate [Hz]',size=15)
            if line_0: plt.plot([0,0],[0.9*Y.min(),1.1*Y.max()],'r--')
            for x in vertical_lines: plt.plot([x,x],[0.9*Y.min(),1.1*Y.max()],vlines_color)
            if rebin:
                hist,bin_edges=sp.histogram(BGO_EVT,TIME_BINS_REBIN)

                DX=(bin_edges[1:]-bin_edges[:-1])
                X=bin_edges[:-1]+DX/2.       

                Y=hist/DX
                plt.bar(X,Y,DX,color=(0, 0, 0, 0.0),linewidth=1,edgecolor='k',label=None)
                pass  

            Panel+=1
            pass
        ##################################################
        if self.LLEFiles1 is not None:
            LLE_EVT=sp.array([])
            Emin,Emax=self.LLEEmin1,self.LLEEmax1
            print self.LLEFiles1
            for iFile in self.LLEFiles1:   LLE_EVT=sp.append(LLE_EVT,LLE_EVENTS(iFile,TRIGTIME=self.TRIGTIME,Emin=Emin,Emax=Emax))
            Nevents=len(LLE_EVT[(LLE_EVT>self.TMIN)*(LLE_EVT<self.TMAX)])
            if Nevents>0:
                if Panel==1:
                    ax=plt.subplot(self.NP,1,Panel)
                    ToShare=ax
                else: ax=plt.subplot(self.NP,1,Panel,sharex=ToShare)

                hist,bin_edges=sp.histogram(LLE_EVT,TIME_BINS)
                X=bin_edges[:-1]
                DX=(bin_edges[1:]-bin_edges[:-1])
                Y=hist/DX
                #plt.bar(X,Y,DX,edgecolor=self.colors['LLE1'],alpha=0.75,linewidth=1,label=label('LLE',Emin,Emax,'MeV'))
                plt.step(X,Y,DX,where='mid',color=self.colors['LLE1'],label=label('LLE',Emin,Emax,'MeV'))
                if self.fill: plt.fill_between(X,Y,step='mid',color=self.fill_color)
                plt.xlim([self.TMIN,self.TMAX])
                plt.ylim([0.9*Y.min(),1.1*Y.max()])
                plt.legend(frameon=0)
                ax.xaxis.grid(xgrid)
                #plt.xticks(size=0)                
                plt.ylabel('Count rate [Hz]',size=15)
                if line_0: plt.plot([0,0],[0.9*Y.min(),1.1*Y.max()],'r--')
                for x in vertical_lines: plt.plot([x,x],[0.9*Y.min(),1.1*Y.max()],vlines_color)
                if rebin:
                    hist,bin_edges=sp.histogram(LLE_EVT,TIME_BINS_REBIN)

                    DX=(bin_edges[1:]-bin_edges[:-1])
                    X=bin_edges[:-1]+DX/2.       
                    Y=hist/DX
                    plt.bar(X,Y,DX,color=(0, 0, 0, 0.0),linewidth=1,edgecolor='k',label=None)
                    pass  
                
                Panel+=1
                pass
            pass        
        ##################################################
        if self.LLEFiles2 is not None:
            LLE_EVT=sp.array([])
            Emin,Emax=self.LLEEmin2,self.LLEEmax2
            for iFile in self.LLEFiles2:   LLE_EVT=sp.append(LLE_EVT,LLE_EVENTS(iFile,TRIGTIME=self.TRIGTIME,Emin=Emin,Emax=Emax))
            Nevents=len(LLE_EVT[(LLE_EVT>self.TMIN)*(LLE_EVT<self.TMAX)])
            if Nevents>0:
                if Panel==1:
                    ax=plt.subplot(self.NP,1,Panel)
                    ToShare=ax
                else: ax=plt.subplot(self.NP,1,Panel,sharex=ToShare)
                hist,bin_edges=sp.histogram(LLE_EVT,TIME_BINS)
                X=bin_edges[:-1]
                DX=(bin_edges[1:]-bin_edges[:-1])
                Y=hist/DX
                plt.bar(X,Y,DX,edgecolor=self.colors['LLE2'],alpha=0.75,linewidth=1,label=label('LLE',Emin,Emax,'MeV'))

                plt.xlim([self.TMIN,self.TMAX])
                plt.ylim([0.9*Y.min(),1.1*Y.max()])
                plt.legend(frameon=0)
                ax.xaxis.grid(xgrid)
                #plt.xticks(size=0)                
                plt.ylabel('Count rate [Hz]',size=15)
                if line_0: plt.plot([0,0],[0.9*Y.min(),1.1*Y.max()],'r--')
                for x in vertical_lines: plt.plot([x,x],[0.9*Y.min(),1.1*Y.max()],vlines_color)
                if rebin:
                    hist,bin_edges=sp.histogram(LLE_EVT,TIME_BINS_REBIN)

                    DX=(bin_edges[1:]-bin_edges[:-1])
                    X=bin_edges[:-1]+DX/2.
                    Y=hist/DX
                    plt.bar(X,Y,DX,color=(0, 0, 0, 0.0),linewidth=1,edgecolor='k',label=None)
                    pass  

                Panel+=1
                pass
            pass        
        ##################################################
        if self.LATFiles1 is not None and self.plotLATLC:
            if Panel==1:
                ax=plt.subplot(self.NP,1,Panel)
                ToShare=ax
            else: ax=plt.subplot(self.NP,1,Panel,sharex=ToShare)
            LAT_EVT_T=sp.array([])
            LAT_EVT_E=sp.array([])
            LAT_EVT_P=sp.array([])

            Emin=self.LATEmin1
            Emax=self.LATEmax1
            for iFile in self.LATFiles1:                
                TIME_ENERGY=LAT_EVENTS(iFile,TRIGTIME=self.TRIGTIME,Emin=Emin,Emax=Emax)
                LAT_EVT_T=sp.append(LAT_EVT_T,TIME_ENERGY[0])
                LAT_EVT_E=sp.append(LAT_EVT_E,TIME_ENERGY[1])
                LAT_EVT_P=sp.append(LAT_EVT_P,TIME_ENERGY[2])
                pass
            Nevents=len(LAT_EVT_T[(LAT_EVT_T>self.TMIN)*(LAT_EVT_T<self.TMAX)])
            print ' LAT 1 ===>',Nevents        
            if Nevents>0:
                hist,bin_edges=sp.histogram(LAT_EVT_T,TIME_BINS)
                X=bin_edges[:-1]
                DX=(bin_edges[1:]-bin_edges[:-1])
                Y=hist/DX
                #plt.bar(X,Y,DX,edgecolor=self.colors['LAT1'],alpha=0.75,linewidth=1,label=label('LAT',Emin,Emax,'MeV'))
                plt.step(X,Y,DX,where='mid',color=self.colors['LAT1'],label=label('LAT',Emin,Emax,'MeV'))
                if self.fill: plt.fill_between(X,Y,step='mid',color=self.fill_color)
                plt.xlim([self.TMIN,self.TMAX])
                plt.ylim([0.9*Y.min(),1.1*Y.max()])
                plt.legend(frameon=0)
                ax.xaxis.grid(xgrid)
                #plt.xticks(size=0)                
                plt.ylabel('Count rate [Hz]',size=15)
                if line_0: plt.plot([0,0],[0.9*Y.min(),1.1*Y.max()],'r--')
                for x in vertical_lines: plt.plot([x,x],[0.9*Y.min(),1.1*Y.max()],vlines_color)
                if rebin:
                    hist,bin_edges=sp.histogram(LAT_EVT_T,TIME_BINS_REBIN)

                    DX=(bin_edges[1:]-bin_edges[:-1])
                    X=bin_edges[:-1]+DX/2.
                    Y=hist/DX
                    plt.bar(X,Y,DX,color=(0, 0, 0, 0.0),linewidth=1,edgecolor='k',label=None)
                    pass  
                
                Panel+=1
                pass
            pass
                
        ##################################################
        if self.LATFiles2 is not None:
            if Panel==1:
                ax=plt.subplot(self.NP,1,Panel)
                ToShare=ax
            else: ax=plt.subplot(self.NP,1,Panel,sharex=ToShare)
            LAT_EVT_T=sp.array([])
            LAT_EVT_E=sp.array([])
            LAT_EVT_P=sp.array([])
            
            Emin=self.LATEmin2
            Emax=self.LATEmax2
            for iFile in self.LATFiles2:
                TIME_ENERGY=LAT_EVENTS(iFile,TRIGTIME=self.TRIGTIME,Emin=Emin,Emax=Emax)
                LAT_EVT_T=sp.append(LAT_EVT_T,TIME_ENERGY[0])
                LAT_EVT_E=sp.append(LAT_EVT_E,TIME_ENERGY[1])
                LAT_EVT_P=sp.append(LAT_EVT_P,TIME_ENERGY[2])
                pass
            Nevents=len(LAT_EVT_T[(LAT_EVT_T>self.TMIN)*(LAT_EVT_T<self.TMAX)])
            print ' LAT 2 ===>',Nevents
            if Nevents>0:
                hist,bin_edges=sp.histogram(LAT_EVT_T,TIME_BINS)
                X=bin_edges[:-1]
                DX=(bin_edges[1:]-bin_edges[:-1])
                Y=hist/DX
                #plt.bar(X,Y,DX,edgecolor=self.colors['LAT1'],alpha=0.75,linewidth=1,label=label('LAT',Emin,Emax,'MeV'))
                plt.step(X,Y,DX,where='mid',color=self.colors['LAT1'],label=label('LAT',Emin,Emax,'MeV'))
                if self.fill: plt.fill_between(X,Y,step='mid',color=self.fill_color)
                plt.xlim([self.TMIN,self.TMAX])
                plt.ylim([0.9*Y.min(),1.1*Y.max()])
                plt.legend(frameon=0)
                ax.xaxis.grid(xgrid)
                #plt.xticks(size=0)                
                plt.ylabel('Count rate [Hz]',size=15)
                if line_0: plt.plot([0,0],[0.9*Y.min(),1.1*Y.max()],'r--')
                for x in vertical_lines: plt.plot([x,x],[0.9*Y.min(),1.1*Y.max()],vlines_color)
                if rebin:
                    hist,bin_edges=sp.histogram(LAT_EVT_T,TIME_BINS_REBIN)

                    DX=(bin_edges[1:]-bin_edges[:-1])
                    X=bin_edges[:-1]+DX/2.
                    Y=hist/DX
                    plt.bar(X,Y,DX,color=(0, 0, 0, 0.0),linewidth=1,edgecolor='k',label=None)
                    pass  
                
                Panel+=1
                pass
            pass
        plt.xlabel(self.xlabel,size=15)
        ##################################################
        if self.LATFiles1 is not None:
            if Panel==1:
                ax=plt.subplot(self.NP,1,Panel)
                ToShare=ax
            else: 
                ax=plt.subplot(self.NP,1,Panel,sharex=ToShare)
                #ax2 = ax.twinx() # Uncomment this for twing axis... and commenmyt the line above
                pass
            LAT_EVT_T=sp.array([])
            LAT_EVT_E=sp.array([])
            LAT_EVT_P=sp.array([])
            for iFile in self.LATFiles1:
                TIME_ENERGY=LAT_EVENTS(iFile,TRIGTIME=self.TRIGTIME,Emin=self.LATEmin1,Emax=self.LATEmax1)
                LAT_EVT_T=sp.append(LAT_EVT_T,TIME_ENERGY[0])
                LAT_EVT_E=sp.append(LAT_EVT_E,TIME_ENERGY[1])
                LAT_EVT_P=sp.append(LAT_EVT_P,TIME_ENERGY[2])
                pass
            Nevents=len(LAT_EVT_T[(LAT_EVT_T>self.TMIN)*(LAT_EVT_T<self.TMAX)])
            print ' ===>',Nevents
            if Nevents>0:
            ##################################################
                print len(LAT_EVT_T),len(LAT_EVT_P)
                print len(LAT_EVT_T[LAT_EVT_P>=0.9])
                #ax=plt.subplot(self.NP,1,Panel,sharex=ToShare)
                plt.plot(LAT_EVT_T[LAT_EVT_P>=0.9],LAT_EVT_E[LAT_EVT_P>=0.9],'o',mfc='r',mec='r',alpha=0.5)#,fc=(0,0,0,0))
                plt.plot(LAT_EVT_T[LAT_EVT_P<0.9],LAT_EVT_E[LAT_EVT_P<0.9],'o',mfc='w',mec='orange',alpha=0.5)#,fc=(0,0,0,0))
                
                plt.xlim([self.TMIN,self.TMAX])
                plt.ylim([self.LATEmin1,self.LATEmax1])
                plt.yscale('log')
                #plt.xticks(size=0)                
                plt.ylabel('Energy [MeV*]',size=15)
                ax.yaxis.grid(ygrid)
                ax.xaxis.grid(xgrid)

                if self.plotLATLC is False: ax.text(0.85, 0.85, label('LAT',self.LATEmin1,self.LATEmax1,'MeV'), 
                                                    horizontalalignment='center', 
                                                    verticalalignment='center', 
                                                    transform=ax.transAxes)
                if line_0: plt.plot([0,0],[self.LATEmin1,self.LATEmax1],'r--')
                #for x in vertical_lines: plt.plot([x,x],[0.9*Y.min(),1.1*Y.max()],vlines_color)
                #Panel+=1
                pass
            pass

        
        ##################################################
        plt.xlabel(self.xlabel,size=15)
        if self.NP==1: plt.subplots_adjust(hspace=0.001,bottom=0.3)
        else: plt.subplots_adjust(hspace=0.001)
        #plt.tight_layout(h_pad=0.0)
        plt.savefig(self.output)
        plt.savefig(self.output.replace(self.output.split('.')[-1],'eps'))
        plt.savefig(self.output.replace(self.output.split('.')[-1],'png'))
        
        #plt.show()
        pass
    pass

if __name__=='__main__':
    import os,sys
    import argparse
    import glob
    desc = '''Plot a Composite Light Curve'''
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--triggertime',help='Trigger time (MET)', type=float, required=True)
    parser.add_argument('--tmin',help='min of the x-axis', type=float, required=False, default=-22)
    parser.add_argument('--tmax',help='min of the x-axis', type=float, required=False, default=290)
    parser.add_argument('--dt',  help='bin width', type=float, required=False, default=1)
    parser.add_argument('--NaIB1',help='Input NaI list of CSPEC files', type=str,   required=False, default='',nargs='+')
    parser.add_argument('--NaIB2',help='Input NaI list of CSPEC files', type=str,   required=False, default='',nargs='+')
    parser.add_argument('--BGOB1',help='Input BGO list of files',    type=str,   required=False, default='',nargs='+')
    parser.add_argument('--BGOB2',help='Input BGO list of files',    type=str,   required=False, default='',nargs='+')
    parser.add_argument('--LLE1',help='Input LLE fits file',        type=str,   required=False, default='',nargs='+')
    parser.add_argument('--LLE2',help='Input LLE fits file',        type=str,   required=False, default='',nargs='+')
    parser.add_argument('--LAT1',help='Input LLE fits file',        type=str,   required=False, default='',nargs='+')
    parser.add_argument('--LAT2',help='Input LLE fits file',        type=str,   required=False, default='',nargs='+')
    parser.add_argument('--NaI1',help='Input NaI list of files',    type=str,   required=False, default='',nargs='+')
    parser.add_argument('--NaI2',help='Input NaI list of files',    type=str,   required=False, default='',nargs='+')
    parser.add_argument('--BGO1',help='Input BGO list of files',    type=str,   required=False, default='',nargs='+')
    parser.add_argument('--BGO2',help='Input BGO list of files',    type=str,   required=False, default='',nargs='+')

    parser.add_argument('--Swift',help='Input Swift LC File',    type=str,   required=False, default=None)

    parser.add_argument('--NAI1_EBOUNDS',help='Energy Bounds for NaI (1st plot) [keV]', type=float,   required=False, default= [10, 100],nargs='+')
    parser.add_argument('--NAI2_EBOUNDS',help='Energy Bounds for NaI (2nd plot) [keV]', type=float,   required=False, default= [100, 520],nargs='+')
    parser.add_argument('--BGO1_EBOUNDS',help='Energy Bounds for BGO (1st plot) [keV]', type=float,   required=False, default= [520,1000],nargs='+')
    parser.add_argument('--BGO2_EBOUNDS',help='Energy Bounds for BGO (2nd plot) [keV]', type=float,   required=False, default= [1000,40000],nargs='+')
    parser.add_argument('--LLE1_EBOUNDS',help='Energy Bounds for LLE (1st plot) [MeV]', type=float,   required=False, default= [30, 100],nargs='+')
    parser.add_argument('--LLE2_EBOUNDS',help='Energy Bounds for LLE (2nd plot) [MeV]', type=float,   required=False, default= [100,1000],nargs='+')
    parser.add_argument('--LAT1_EBOUNDS',help='Energy Bounds for LAT (1st plot) [MeV]', type=float,   required=False, default= [30, 100],nargs='+')
    parser.add_argument('--LAT2_EBOUNDS',help='Energy Bounds for LAT (2nd plot) [MeV]', type=float,   required=False, default= [100,100000],nargs='+')

    parser.add_argument('--Swift_TTime',help='MET corresponding to the Swift Trigger time', type=float,   required=False)
    parser.add_argument('--Swift_Legend',help='TExt to display as legend', type=str,   required=False, default='Swift')


    parser.add_argument('--vlines',help='vertical lines to draw',   type=float,   required=False, default=[],nargs='+')

    parser.add_argument('--rebin',help='Rebin the LC using vlines', type=int,   required=False, default=0)
    parser.add_argument('--output',help='Name of the output plot', type=str,    required=False, default='CompositeLightcurve.png')
    
    #parser.add_argument('--tmin',help='minimum time for the x-axis', required=False, default=None)
    #parser.add_argument('--tmax',help='maximum time for the x-axis', required=False, default=None)

    #parser.add_argument('--lc',help='directory containing the LC files',
    #                    required=False, default=None)
    #parser.add_argument('--nside',help='Input HEALPIX NSIDE', type=int, required=False,default=0)
    #parser.add_argument('--xlabel',help='Label of the x axis', type=str, required=False,default="GW")
    #parser.add_argument('--ylabel',help='Label of the y axis', type=str, required=False,default="Flux [erg cm$^{-2}$ s$^{-1}$]")
    #parser.add_argument('--histo',help='Horizontal Histogram', type=int, required=False,default=1)

    args = parser.parse_args()
    TMIN      = args.tmin
    TMAX      = args.tmax
    DT        = args.dt
    NaIFilesB1 = args.NaIB1
    BGOFilesB1 = args.BGOB1
    NaIFilesB2 = args.NaIB2
    BGOFilesB2 = args.BGOB2

    LLEFiles1 = args.LLE1
    LATFiles1 = args.LAT1
    BGOFiles1 = args.BGO1
    NaIFiles1 = args.NaI1
    LLEFiles2 = args.LLE2
    LATFiles2 = args.LAT2
    BGOFiles2 = args.BGO2
    NaIFiles2 = args.NaI2
    Swift     = args.Swift
    Swift_TTime=args.Swift_TTime
    Swift_Legend=args.Swift_Legend
    GRBMET    = args.triggertime
    vertical_lines=args.vlines
    rebin     = bool(args.rebin)
    NaI1_EBOUNDS = sp.array(args.NAI1_EBOUNDS)
    NaI2_EBOUNDS = sp.array(args.NAI2_EBOUNDS) 
    BGO1_EBOUNDS = sp.array(args.BGO1_EBOUNDS)
    BGO2_EBOUNDS = sp.array(args.BGO2_EBOUNDS)
    LLE1_EBOUNDS = sp.array(args.LLE1_EBOUNDS)
    LLE2_EBOUNDS = sp.array(args.LLE2_EBOUNDS)
    LAT1_EBOUNDS = sp.array(args.LAT1_EBOUNDS)
    LAT2_EBOUNDS = sp.array(args.LAT2_EBOUNDS)
    output       = args.output

    #import scripts.CompositeLightCurve_MPL as CLC
    #LLEFiles = glob.glob('%s/%s/v%02d/gll_lle*fit' % (output_ez,grbname,LLE_VERSION))
    #LATFiles = [results['use_in_composite'].replace('.root','.fits')]
    LC=CompositeLC(GRBMET,TMIN,TMAX,DT)
    if len(NaIFilesB1)>0: LC.SetNaIB1(NaIFilesB1,NaI1_EBOUNDS[0],NaI1_EBOUNDS[1])
    if len(BGOFilesB1)>0: LC.SetBGOB1(BGOFilesB1,BGO1_EBOUNDS[0],BGO1_EBOUNDS[1])

    if len(NaIFiles1)>0: LC.SetNaI1(NaIFiles1,NaI1_EBOUNDS[0],NaI1_EBOUNDS[1])
    if len(BGOFiles1)>0: LC.SetBGO1(BGOFiles1,BGO1_EBOUNDS[0],BGO1_EBOUNDS[1])

    if len(LLEFiles1)>0: LC.SetLLE1(LLEFiles1,LLE1_EBOUNDS[0],LLE1_EBOUNDS[1])
    if len(LATFiles1)>0: LC.SetLAT1(LATFiles1,LAT1_EBOUNDS[0],LAT1_EBOUNDS[1])

    if len(NaIFilesB2)>0: LC.SetNaIB2(NaIFilesB2,NaI2_EBOUNDS[0],NaI2_EBOUNDS[1])
    if len(BGOFilesB2)>0: LC.SetBGOB2(BGOFilesB2,BGO2_EBOUNDS[0],BGO2_EBOUNDS[1])

    if len(NaIFiles2)>0: LC.SetNaI2(NaIFiles2,NaI2_EBOUNDS[0],NaI2_EBOUNDS[1])
    if len(BGOFiles2)>0: LC.SetBGO2(BGOFiles2,BGO2_EBOUNDS[0],BGO2_EBOUNDS[1])

    if len(LLEFiles2)>0: LC.SetLLE2(LLEFiles2,LLE2_EBOUNDS[0],LLE2_EBOUNDS[1])
    if len(LATFiles2)>0: LC.SetLAT2(LATFiles2,LAT2_EBOUNDS[0],LAT2_EBOUNDS[1])

    if Swift is not None: LC.SetSwift(Swift,Swift_TTime,Swift_Legend)

    LC.SetOutput(output)
    LC.Plot(rebin=rebin,vertical_lines=vertical_lines)

##################################################                                                                                                                                                                                                                     
# FINISHING UP                                                                                                                                                                                                                                                         
##################################################                                                                                                                                                                                                                     
    #Done()




#NaIFiles= ['120226871/glg_tte_n0_bn120226871_v00.fit','120226871/glg_tte_n1_bn120226871_v00.fit']
#BGOFiles= ['120226871/glg_tte_b0_bn120226871_v00.fit','120226871/glg_tte_b0_bn120226871_v00.fit']
#LLEFiles =['v01/gll_lle_bn120226871_v01.fit']
#LATFiles =['120226871_LAT_ROI_0.00_4000.00.fits']
#TRIGTIME=pyfits.open(NaIFiles[0])['EVENTS'].header['TRIGTIME']

#LC=CompositeLC(TRIGTIME)
#LC.SetNaI(NaIFiles)
#LC.SetBGO(BGOFiles)
#LC.SetLLE(LLEFiles)
#LC.SetLAT(LATFiles)
#LC.Plot()
