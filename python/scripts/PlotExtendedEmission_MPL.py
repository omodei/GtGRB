#!/usr/bin/env python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy as sp
import scipy.optimize as optimize
import math
import glob
import os

SMALL_SIZE = 20
MEDIUM_SIZE = 25
BIGGER_SIZE = 45
SPAN_COLOR='gainsboro'
SPAN_ALPHA=1.0
plt.rc('font', size=SMALL_SIZE,weight='bold')          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE,linewidth=2)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE,direction='in')    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE,direction='in')    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
plt.rcParams['ytick.right']=plt.rcParams['xtick.top']=True 
plt.rcParams['xtick.major.size']=plt.rcParams['ytick.major.size']=10
plt.rcParams['xtick.minor.size']=plt.rcParams['ytick.minor.size']=5

plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


def getProbabilities(InputFileName,likelihood_index):
    t=[]
    e=[]
    p=[]
    mydirectory=os.path.dirname(InputFileName)
    gtsrcprobfile=os.path.join(mydirectory,'gtsrcprob_%d_*.txt' % likelihood_index)
    if len(glob.glob(gtsrcprobfile))>0:
        for l in  file(glob.glob(gtsrcprobfile)[0],'r').readlines():
            if '#' in l: continue
            _t,_e,_p=l.split()
            t.append(float(_t.strip()))
            e.append(float(_e.strip()))
            p.append(float(_p.strip()))
            pass
    return sp.array(t),sp.array(e),sp.array(p)

def PlotExtendedEmission(InputFileName,inputResults,xscale='log',ts_min=10,fit=2,
                         xmax=None,xmin=None,useGBM=True,
                         fluxmax = 1e-1,fluxmin = 1e-7,
                         fit_xmin=None,fit_xmax=None,include_ul=True):
    print '--------------- PlotExtendedEmission -------------------- '
    print '- InputFileName...:',InputFileName
    print '- xscale..........:',xscale
    print '- xmin............:',xmin
    print '- xmax............:',xmax
    print '- ts_min..........:',ts_min
    print '- fit.............:',fit
    print '-  fit_xmin.......:', fit_xmin
    print '-  fit_xmax.......:', fit_xmax    
    print '-----------------------------------------------------------'

    if xmin is None: xmin=1e-2
    
    if 'GBMT95' in inputResults.keys():  GBMT95=inputResults['GBMT95']
    else: GBMT95=0.0
    
    if 'GRBNAME' in inputResults.keys():  GRBNAME=inputResults['GRBNAME']
    else: GRBNAME=InputFileName.split('_')[-1].split('.')[0]
    if 'GCNNAME' in inputResults.keys():  GCNNAME=inputResults['GCNNAME']
    else: GCNNAME=GRBNAME
    try: GCNNAME='%06d' % GCNNAME
    except:  pass
    results={}
    InputFile=file(InputFileName,'r')
    lines = InputFile.readlines()
    
    t0=[]
    t1=[]
    tm=[]
    ts=[]
    NoUL=[]
    NobsTot =[]
    nph_100 =[]
    nph_1000=[]
    index=[]
    eindex=[]
    flux =[]
    eflux =[]
    eneflux =[]
    eeneflux =[]
    toFit=[]
    toFit_err=[]
    Ns=0
    consecutive_ul=0#first_ul=True
    like_durmin_l = 1e6
    like_durmax_l = -like_durmin_l
    like_durmin_u = 1e6
    like_durmax_u = -like_durmin_u

    like_prob_prob=sp.array([])
    like_prob_time=sp.array([])
    like_prob_ener=sp.array([])
    for line in lines:
        print line
        if '#' in line: continue
        par=line.split()
        if xmax is not None and float(par[2])>xmax: continue
        likelihood_index=int(par[0])
        like_t,like_e,like_p=getProbabilities(InputFileName,likelihood_index)
        like_prob_time=sp.append(like_prob_time,like_t)
        like_prob_ener=sp.append(like_prob_ener,like_e)
        like_prob_prob=sp.append(like_prob_prob,like_p)
        
        t0.append(float(par[1]))
        t1.append(float(par[2]))
        tm.append(float(par[3]))            
        ts.append(max(0.1,float(par[6])))
        NobsTot.append(float(par[7]))
        nph_100.append(float(par[8]))
        nph_1000.append(float(par[9]))
        
        index.append(float(par[10]))
        eindex.append(float(par[11]))
        flux.append(float(par[12]))
        eflux.append(float(par[13]))
        
        eneflux.append(float(par[14]))
        eeneflux.append(float(par[15]))
        
        if eflux[-1]>0: # this is a point, not an UL
            if fit_xmax is not None: tnofit=fit_xmax
            else:                    tnofit=1e-4
            if fit_xmax is not None and t0[-1]>fit_xmax:
                NoUL.append(0)
            elif consecutive_ul>1 and sp.sum(NoUL)>0 and t0[-1]>tnofit: # and fit_xmax is None:#first_ul==False and tm[-1]>1e5: 
                NoUL.append(0) # this is to avoid cases when the point is late in time with UL before.
            else: 
                NoUL.append(1)
                consecutive_ul     = 0
                like_durmin_u      = round(min(like_durmin_u,t0[-1]),2)
                like_durmax_l      = round(max(like_durmax_l,t1[-1]),2)
                try: like_durmin_l = round(min(like_durmin_l,t1[-2]),2)
                except: pass
                pass
            
            toFit.append(flux[-1])
            toFit_err.append(eflux[-1])
        else: # this is an upper limitxs            
            consecutive_ul+=1
            if fit_xmax is not None and t0[-1]>fit_xmax:
                NoUL.append(0)
            elif consecutive_ul<2 and include_ul and sp.sum(NoUL)>0:# and fit_xmax is None:# and t0[-1]<fit_xmax: 
                NoUL.append(1)
                like_durmin_l=round(min(like_durmin_l,t1[-1]),2)
                like_durmax_u=round(max(like_durmax_u,t0[-1]),2)
            else: 
                NoUL.append(0)
                pass
            toFit.append(flux[-1]/1.65)
            toFit_err.append(flux[-1]/1.65)
            pass
        #print "DEBUG:",tm[-1], eflux[-1], NoUL[-1], consecutive_ul
        Ns=Ns+1
        pass

    like_durmin_l=round(min(like_durmin_l,like_durmin_u),2)
    like_durmax_u=round(max(like_durmax_l,like_durmax_u),2)
    #print like_durmin_l,like_durmin_u,like_durmax_l,like_durmax_u

    if Ns==0:  return results
    
    if t0[0]<=0: xscale=='lin'
    #if t0[0]>0:        
    #    t0.insert(0,xmin)
    #    t1.insert(0,t0[1])
    #    tm.insert(0,(t0[1]+t0[0])/2.)
    #    ts.insert(0,0)
    #    NobsTot.insert(0,0)
    #    nph_100.insert(0,0)
    #    nph_1000.insert(0,0)
    #    index.insert(0,0)
    #    eindex.insert(0,0)
    #    flux.insert(0,0)
    #    eflux.insert(0,0)
    #    eneflux.insert(0,0)
    #    eeneflux.insert(0,0)
    #    NoUL.insert(0,0)
    #    Ns=Ns+1
    #    pass
    
    t0=sp.array(t0)
    t1=sp.array(t1)
    tm=sp.array(tm)
    ts=sp.array(ts)
    NoUL=sp.array(NoUL)
    NobsTot =sp.array(NobsTot)
    nph_100 =sp.array(nph_100)
    nph_1000=sp.array(nph_1000)
    index=sp.array(index)
    eindex=sp.array(eindex)
    flux =sp.array(flux)
    eflux =sp.array(eflux)
    eneflux =sp.array(eneflux)
    eeneflux =sp.array(eeneflux)
    toFit =sp.array(toFit)
    toFit_err =sp.array(toFit_err)
    
    tlower=tm-t0
    tupper=t1-tm
    delta_t=t1-t0

    myfilter=(eflux>0)
    myfilter_UL=(eflux==0)

    # #################################################
    # Some definitions
    # #################################################
    nfine_steps=1000
    xmin=0.5*t0[0]
    xmax=2*t1[-1]    
    #xmin=0.01
    #xmax=1e5
    bar=0.5
    #plt.xlim([1,2e4])
    peak_flux_idx = 0
    peak_flux     = 0
    peak_flux_err = 0
    peak_flux_time= 0 
    peak_flux_time_err=0.0
    if myfilter.sum()>0:
        peak_flux_idx = flux[myfilter].argmax()
        peak_flux     = flux[myfilter][peak_flux_idx]
        peak_flux_err = eflux[myfilter][peak_flux_idx]
        peak_flux_time= tm[myfilter][peak_flux_idx]
        peak_flux_time_err= t1[myfilter][peak_flux_idx]-t0[myfilter][peak_flux_idx]
        pass
    print 'Generating the figure...'
    # #################################################      
    fig = plt.figure(figsize=(23,15),facecolor='w')
    fig.suptitle('GRB %s' % GRBNAME, fontsize=14, fontweight='bold')
    print 'Adding subplots...'
    ax1 = fig.add_subplot(2,3,1)
    ax1.set_title('GRB %s' % GCNNAME)

    # #################################################      
    #### FIRST PLOT: TS
    # #################################################  
    if myfilter.sum()>0:
        color='red'
        plt.errorbar(tm[myfilter],ts[myfilter],
                     xerr=[tlower[myfilter],tupper[myfilter]],
                     #yerr=[0,0],
                     ls='None',marker='None',mfc=color,mec=color,ecolor=color,lw=2,zorder=10)
    
    if myfilter_UL.sum()>0:
        color='k'
        plt.errorbar(tm[myfilter_UL],ts[myfilter_UL],
                     xerr=[tlower[myfilter_UL],tupper[myfilter_UL]],
                     #yerr=[0,0],
                     ls='None',marker='None',mfc=color,mec=color,ecolor=color,lw=2,zorder=10)
        pass
    plt.plot([xmin,xmax],[ts_min,ts_min],'b--',zorder=1)
    plt.yscale('log')
    if xscale=='log': plt.xscale('log')
    plt.ylabel('Test Statistics (TS)')
    plt.xlabel('T-T$_{0}$ [s]' )
    plt.ylim([0.9*ts.min(),10*ts.max()])        
    plt.xlim([xmin,xmax])
    for i in range(Ns-1):
        if  t0[i+1]!=t1[i]:  plt.axvspan(t0[i+1], t1[i], color=SPAN_COLOR, alpha=SPAN_ALPHA, lw=0,zorder=1)
        pass
    # #################################################      
    #### Second PLOT: Flux
    # #################################################  
    ax2 = fig.add_subplot(2,3,2)
    ax2.set_title('GRB %s' % GCNNAME)
    if myfilter.sum()>0:
        color='b'
        plt.errorbar(tm[myfilter],flux[myfilter],
                     xerr=[tlower[myfilter],tupper[myfilter]],
                     yerr=[eflux[myfilter],eflux[myfilter]],
                     ls='None',marker='None',mfc=color,mec=color,ecolor=color,lw=2,zorder=10)
        pass
    if myfilter_UL.sum()>0:
        color='k'
        plt.errorbar(tm[myfilter_UL],flux[myfilter_UL],
                     xerr=[tlower[myfilter_UL],tupper[myfilter_UL]],
                     yerr=[bar*flux[myfilter_UL],0.0*flux[myfilter_UL]],uplims=True,
                     ls='None',marker='None',mfc=color,mec=color,ecolor=color,lw=2,zorder=10)
        
        pass
    for i in range(Ns-1):
        if  t0[i+1]!=t1[i]:  plt.axvspan(t0[i+1], t1[i], color=SPAN_COLOR, alpha=SPAN_ALPHA, lw=0,zorder=1)
        pass

    plt.yscale('log')
    if xscale=='log': plt.xscale('log')
    plt.ylabel('Flux [ph cm$^{-2}$ s$^{-1}$]')
    plt.xlabel('T-T$_{0}$ [s]')
    plt.ylim([fluxmin,fluxmax])
    plt.xlim([xmin,xmax])
    if GBMT95>0: plt.plot([GBMT95,GBMT95],[fluxmin,fluxmax],'k--',zorder=1)
    ### SIMPLE FIT WITH A STRAIGHT LINE:
    N=0
    N_err=0
    alpha     = 0
    alpha_err = 0
    N2=0
    N2_err=0
    x0=0
    x0_err=0
    a1=0
    a1_err=0
    a2=0
    a2_err=0
    reduced_chi_squared1=999
    reduced_chi_squared2=999
    def Rad_UISM(a):
        return -(1.0+7./2.*a)/6-1.
            
    def Rad_Pair(a):
        return -(-1.0+7./2.*a)/4-1.

    def Adiabatic(a):
        return -(0.5+a)*2./3.-1.

    if useGBM: xmin_tofit=max(peak_flux_time,GBMT95)
    else:      xmin_tofit=peak_flux_time
    xmax_tofit=xmax

    if fit_xmin is not None: xmin_tofit=fit_xmin
    if fit_xmax is not None: xmax_tofit=fit_xmax

    tofit_filter=sp.logical_and(sp.logical_and((tm>=xmin_tofit),(tm<=xmax_tofit)),NoUL)
    #print tofit_filter
    #print tm
    print 'Fit range: %s -- %s (%d points)' %(xmin_tofit,xmax_tofit,tofit_filter.sum())    

    if tofit_filter.sum()>2 and fit>0:
        def decay(x, N, a):
            return N-a*x#sp.power(x,a)

        x  = sp.log10(tm[tofit_filter])
        xl=  sp.log10(tm[tofit_filter]-tlower[tofit_filter])
        xu=  sp.log10(tm[tofit_filter]+tupper[tofit_filter])

        y  = sp.log10(toFit[tofit_filter])
        dy = sp.log10(toFit_err[tofit_filter])
        p0 = (1.,1.)
        def errorfun(p,x,y,dy):
            fx=decay(x, p[0], p[1])
            return ((fx-y)/dy)
        p0=[sp.log10(flux.max()),1.5]
    
        pfit, pcov = optimize.curve_fit(decay, x, y, sigma=dy, p0=p0)
        print 'plotting range %f -- %f' % (sp.power(10,xl[0]),sp.power(10,xu[-1]))
        
        #pfit, pcov, infodict, errmsg, success   = optimize.leastsq(func=errorfun, x0=p0, args=(x,y,dy),full_output=True)
        #if (len(y) > len(p0)) and pcov is not None:
        #    s_sq = (errorfun(pfit, x, y, dy)**2).sum()/(len(y)-len(p0))
        #    pcov = pcov * s_sq
        #else:
        #    pcov = inf
        #    pass
        #print pfit, pcov

        N         = pfit[0]
        N_err     = pcov[0,0]**0.5
        alpha     = pfit[1]
        alpha_err = pcov[1,1]**0.5
        print 'Simple Power Law:'
        print "N =", N, "+/-", N_err
        print "a =", alpha, "+/-", alpha_err
        chi_squared = sp.sum(((decay(x, *pfit)-y)/dy)**2)
        dof         = len(x)-len(pfit)
        reduced_chi_squared1 = (chi_squared)/(1.0*dof)
        print 'CHI SQUARE=%.3f/%d %.2e' %(chi_squared,dof,reduced_chi_squared1)
        xfine = sp.linspace(xl[0],xu[-1],nfine_steps)  # define values to plot the function for
        plt.plot(sp.power(10,xfine), sp.power(10,decay(xfine, *pfit)), 'r',lw=2,zorder=11)
        #plt.errorbar(sp.power(10,x),sp.power(10,y),yerr=sp.power(10,dy))
        gamma_rad_up = Rad_UISM(alpha+alpha_err)
        gamma_rad_lo = Rad_UISM(alpha-alpha_err)
        gamma_rad2_up = Rad_Pair(alpha+alpha_err)
        gamma_rad2_lo = Rad_Pair(alpha-alpha_err)
        gamma_adi_up = Adiabatic(alpha+alpha_err)
        gamma_adi_lo = Adiabatic(alpha-alpha_err)
        try: plt.text(0.52, 0.92, r' $\alpha=%.2f\pm%.2f$' %(alpha,alpha_err), fontsize=18,transform=ax2.transAxes,zorder=12)
        except: pass
        pass

    if tofit_filter.sum()>4 and fit>1:
        def decay2(x, x0, N2, a1, a2):
            return N2-(x<x0)*a1*(x-x0)-(x>=x0)*a2*(x-x0)
        
        def errorfun2(p,x,y,dy):
            x0=p[0]
            N2=p[1]
            a1=p[2]
            a2=p[3]
            penalization=0
            #if x0>10 or x0<3: penalization+=1000                        
            #if a1>1.1 or a1<0.9: penalization+=1000                                    
            fx=decay2(x, *p)
            chi=((fx-y)/dy)+penalization            
            print 'errorfun2:',x0,N2,a1,a2,chi.sum()
            return chi

        x  = sp.log10(tm[tofit_filter])
        y  = sp.log10(toFit[tofit_filter])
        dy = sp.log10(toFit_err[tofit_filter])
        #p0 = [sp.log10(peak_flux_time), N, 2.0, 1.5]
        x_0 = 0.5*(x[0]+x[-1])
        x_1 = min(x[1],x_0-1.0)
        x_2 = max(x[-2],x_0+1.0)
        p0 = [x_0, N, alpha, alpha]
        print 'Broken PL, x0,x1,x2:',x_0,x_1,x_2
        

        pfit, pcov = optimize.curve_fit(decay2, x, y, sigma=dy, p0=p0, bounds=([x_1,-sp.inf,0,0],[x_2,sp.inf,5.0,5.0])) #bounds=([x[0],x[1]],[-sp.inf,sp.inf],[.0,5.0]))#   
        print 'pfit2=',pfit
        print 'pcov2=',pcov
        #import iminuit
        #import probfit
        #try:
        if sp.fabs(pcov[0,0])<10. and sp.fabs(pcov[1,1])<10. and sp.fabs(pcov[2,2])<10. and sp.fabs(pcov[3,3])<10.:
            x0     = pfit[0]
            x0_err = pcov[0,0]**0.5
            N2     = pfit[1]
            N2_err = pcov[1,1]**0.5
            a1     = pfit[2]
            a1_err = pcov[2,2]**0.5
            a2     = pfit[3]
            a2_err = pcov[3,3]**0.5
            print "X0=", x0,"+/-", x0_err
            print "N2=", N2, "+/-", N2_err
            print "a1 =", a1, "+/-", a1_err
            print "a2 =", a2, "+/-", a2_err
            chi_squared = sp.sum(((decay2(x, *pfit)-y)/dy)**2)
            dof         = len(x)-len(pfit)
            reduced_chi_squared2 = (chi_squared)/(1.0*dof)
            print 'CHI SQUARE=%.3f/%d %.2e' %(chi_squared,dof,reduced_chi_squared2)
            xfine = sp.linspace(x[0],x[-1],nfine_steps)  # define values to plot the function for
            plt.plot(sp.power(10,xfine), sp.power(10,decay2(xfine, *pfit)), 'g', lw=2,zorder=11)
            
                # plt.errorbar(sp.power(10,x),sp.power(10,y),yerr=sp.power(10,dy))
            try:   plt.text(0.52, 0.85, r' $\alpha_{1}=%.2f\pm%.2f$' %(a1,a1_err), fontsize=18,transform=ax2.transAxes,zorder=12)
            except: pass
            if (reduced_chi_squared2<reduced_chi_squared1):
                try: plt.text(0.52, 0.8, r'*$\alpha_{2}=%.2f\pm%.2f$' %(a2,a2_err), fontsize=18,transform=ax2.transAxes,zorder=12)
                except: pass
                gamma_rad_up = Rad_UISM(a2+a2_err)
                gamma_rad_lo = Rad_UISM(a2-a2_err)
                gamma_rad2_up = Rad_Pair(a2+a2_err)
                gamma_rad2_lo = Rad_Pair(a2-a2_err)
                gamma_adi_up = Adiabatic(a2+a2_err)
                gamma_adi_lo = Adiabatic(a2-a2_err)
            else:
                try: plt.text(0.52, 0.8, r' $\alpha_{2}=%.2f\pm%.2f$' %(a2,a2_err), fontsize=18,transform=ax2.transAxes,zorder=12)
                except: pass
                pass
            pass
        else:
            print 'Parameters of the it not constrained!'
            # except:
            #            pass
            pass
        pass
    # #################################################
    #### Third PLOT: index
    # #################################################
    ax3    =  fig.add_subplot(2,3,3)
    ax3.set_title('GRB %s' % GCNNAME)
    plt.subplots_adjust(bottom=0.1,hspace=0.3)
    if (myfilter.sum()>0):
        color='k'
        plt.errorbar(tm[myfilter],index[myfilter],
                     xerr=[tlower[myfilter],tupper[myfilter]],
                     yerr=[eindex[myfilter],eindex[myfilter]],
                     ls='None',marker='None',mfc=color,mec=color,ecolor=color,lw=2,zorder=10)
        pass
    if myfilter_UL.sum()>0:
        color='r'
        plt.errorbar(tm[myfilter_UL],index[myfilter_UL],
                     xerr=[tlower[myfilter_UL],tupper[myfilter_UL]],
                     yerr=[0.0*index[myfilter_UL],0.0*index[myfilter_UL]],
                     ls='None',marker='None',mfc=color,mec=color,ecolor=color,lw=2,zorder=10)
        
        pass
    if tofit_filter.sum()>2:
        try:
            print gamma_rad_up-gamma_rad_lo,t1[myfilter][-1]-t0[myfilter][0]
            rect = plt.Rectangle((t0[myfilter][0], gamma_rad_lo), t1[myfilter][-1]-t0[myfilter][0],gamma_rad_up-gamma_rad_lo , facecolor="r", alpha=0.2,edgecolor="r",zorder=5)
            plt.gca().add_patch(rect)
            rect = plt.Rectangle((t0[myfilter][0], gamma_rad2_lo), t1[myfilter][-1]-t0[myfilter][0],gamma_rad2_up-gamma_rad2_lo , facecolor="b", alpha=0.2,edgecolor="b",zorder=5)
            plt.gca().add_patch(rect)
            rect = plt.Rectangle((t0[myfilter][0], gamma_adi_lo), t1[myfilter][-1]-t0[myfilter][0],gamma_adi_up-gamma_adi_lo , facecolor="g", alpha=0.2,edgecolor='g',zorder=5)
            plt.gca().add_patch(rect)
            
            plt.text(0.6, 0.95, 'Rad. ISO', color='r', fontsize=20,transform=ax3.transAxes)
            plt.text(0.6, 0.9, 'Rad. Pair', color='b', fontsize=20,transform=ax3.transAxes)
            plt.text(0.6, 0.85, 'Adiabatic', color='g', fontsize=20,transform=ax3.transAxes)
        except: pass
    	pass	
    #plt.yscale('log')
    if xscale=='log': plt.xscale('log')
    plt.ylabel('photon index')
    plt.xlabel('T-T$_{0}$ [s]')
    plt.ylim([-5,0])        
    plt.xlim([xmin,xmax])
    for i in range(Ns-1):
        if  t0[i+1]!=t1[i]:  plt.axvspan(t0[i+1], t1[i], color=SPAN_COLOR, alpha=SPAN_ALPHA, lw=0,zorder=1)
        pass
    # #################################################
    #### Fourth PLOT: Number of events
    # #################################################
    ax4 = fig.add_subplot(2,3,4)
    ax4.set_title('GRB %s' % GCNNAME)
    color='k'
    plt.errorbar(tm,NobsTot/delta_t,
                 xerr=[tlower,tupper],
                 ls='None',marker='None',mfc=color,mec=color,ecolor=color,lw=2,label='Obs.')
    color='b'
    plt.errorbar(tm,nph_100/delta_t,
                 xerr=[tlower,tupper],
                 ls='None',marker='None',mfc=color,mec=color,ecolor=color,lw=2,label='Pred. >100 MeV')
    color='r'
    plt.errorbar(tm,nph_1000/delta_t,
                 xerr=[tlower,tupper],
                 ls='None',marker='None',mfc=color,mec=color,ecolor=color,lw=2,label='Pred. >1 GeV')

    plt.yscale('log')
    if xscale=='log': plt.xscale('log')
    plt.ylabel('Rate of Events [Hz]')
    plt.xlabel('T-T$_{0}$ [s]')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)
    for i in range(Ns-1):
        if  t0[i+1]!=t1[i]:  plt.axvspan(t0[i+1], t1[i], color=SPAN_COLOR, alpha=SPAN_ALPHA, lw=0)
        pass
    plt.xlim([xmin,xmax])
    # #################################################
    #### Fourth PLOT: Number of events
    # #################################################

    ##color='k'
    #plt.errorbar(tm[NobsTot>0],delta_t[NobsTot>0]/NobsTot[NobsTot>0],
    #             xerr=[tlower[NobsTot>0],tupper[NobsTot>0]],
    #             c=color,
    #             #ls='None',
    #             marker='None',mfc=color,mec=color,ecolor=color,lw=2,label='Obs.')
    #color='b'
    #plt.errorbar(tm[nph_100>0],delta_t[nph_100>0]/nph_100[nph_100>0],
    #             xerr=[tlower[nph_100>0],tupper[nph_100>0]],
    #             c=color,
    #             #ls='None',
    #             marker='None',mfc=color,mec=color,ecolor=color,lw=2,label='Pred. >100 MeV')
    #color='r'
    #plt.errorbar(tm[nph_1000>0],delta_t[nph_1000>0]/nph_1000[nph_1000>0],
    #             xerr=[tlower[nph_1000>0],tupper[nph_1000>0]],
    #             c=color,
    #             #ls='None',
    #             marker='None',mfc=color,mec=color,ecolor=color,lw=2,label='Pred. >1 GeV')#

    #plt.yscale('log')
    #if xscale=='log': plt.xscale('log')
    #plt.ylabel('1/Rate [s]')
    #plt.xlabel('T-T$_{0}$')
    #plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)
    # #################################################
    # #################################################
    #### Fourth PLOT: Culative Number of events
    # #################################################
    from scipy.interpolate import interp1d

    ax5 = fig.add_subplot(2,3,5)
    ax5.set_title('GRB %s' % GCNNAME)
    cumulative_obs   = sp.zeros(Ns+1)
    cumulative_p100  = sp.zeros(Ns+1)
    cumulative_p1000 = sp.zeros(Ns+1)
    cumulative_flu   = sp.zeros(Ns+1)
    cumulative_x     = sp.zeros(Ns+1)
    
    for i in range(Ns):
        if eflux[i]>0 and NoUL[i]==1:
            cumulative_obs[i+1]  = cumulative_obs[i]  + NobsTot[i]
            cumulative_p100[i+1] = cumulative_p100[i] + nph_100[i]
            cumulative_p1000[i+1]= cumulative_p1000[i]+ nph_1000[i]
            cumulative_flu[i+1]  = cumulative_flu[i] + flux[i]*delta_t[i] # This is a fluence
        else:
            cumulative_obs[i+1]  = cumulative_obs[i]
            cumulative_p100[i+1] = cumulative_p100[i]
            cumulative_p1000[i+1]= cumulative_p1000[i]
            cumulative_flu[i+1]  = cumulative_flu[i]
            pass
        cumulative_x[i]      = t0[i]
        pass
    cumulative_x[Ns]     = t1[Ns-1]
    print 'CUMULATIVE:',
    CumulativeNevt  = cumulative_obs[-1]
    CumulativeN100  = cumulative_p100[-1]
    CumulativeN1000 = cumulative_p1000[-1]
    CumulativeFlux  = cumulative_flu[-1]
    
    y_100  = sp.zeros(2*Ns)
    y_1000 = sp.zeros(2*Ns)
    y_flu  = sp.zeros(2*Ns)
    x_cum  = sp.zeros(2*Ns)

    for i in range(Ns):
        x_cum[2*i]   = t0[i]
        x_cum[2*i+1] = t1[i]
        y_100[2*i]   = cumulative_p100[i]
        y_100[2*i+1] = cumulative_p100[i+1]        
        y_1000[2*i]   = cumulative_p1000[i]
        y_1000[2*i+1] = cumulative_p1000[i+1]        
        y_flu[2*i]   = cumulative_flu[i]
        y_flu[2*i+1] = cumulative_flu[i+1]        
        pass
    for i in range(Ns-1):
        if  t0[i+1]!=t1[i]:  plt.axvspan(t0[i+1], t1[i], color=SPAN_COLOR, alpha=SPAN_ALPHA, lw=0)
        pass

    print 'Nobs= %d Pred (>100 MeV)=%.2f Pred (>1 GeV)=%.2f Fluence MAX=%.2f  ' %(cumulative_obs[-1], y_100[-1], y_1000[-1], y_flu[-1])

    color='b'
    p1,=plt.plot(x_cum,y_100,
                 c=color,
                 marker='None',lw=2)
    
    color='r'
    p2,=plt.plot(x_cum,y_1000,
                 c=color,
                 marker='None',lw=2)
    
    #plt.yscale('log')
    if xscale=='log': plt.xscale('log')
    plt.ylabel('Cumulative N (<T-T$_{0}$) ')
    plt.xlabel('T-T$_{0}$ [s]')

    
    uspl=interp1d(sp.log10(x_cum),y_100)
    finex=sp.linspace(sp.log10(x_cum[0]),sp.log10(x_cum[-1]),nfine_steps)

    COUNTS_95=0
    COUNTS_05=0
    C100=y_100[-1]
    C1000=y_100[-1]

    C95=0.95*C100
    C05=0.05*C100
    for x in finex:
        if uspl(x)<C05:   COUNTS_05=x
        if uspl(x)>C95:
            COUNTS_95=x
            break
        pass
    COUNTS_05=sp.power(10,COUNTS_05)
    COUNTS_95=sp.power(10,COUNTS_95)
    plt.xlim([xmin,xmax])
    # FLUENCE
    axr = ax5.twinx()
    axr.spines["right"].set_visible(True)
    
    color='g'
    p3,=axr.plot(x_cum,y_flu,
                 c=color,
                 marker='None',lw=2,label='Flu. >100 MeV')
    plt.ylabel('Cumulative Photon Fluence (<T-T$_{0}$)')
    axr.tick_params(axis='y', colors=color)

    uspl=interp1d(sp.log10(x_cum),y_flu)
    finex=sp.linspace(sp.log10(x_cum[0]),sp.log10(x_cum[-1]),nfine_steps)
    #axr.plot(sp.power(10,finex),uspl(finex),'o')
    FLUENCE_95=finex[0]
    FLUENCE_05=finex[0]
    F100=y_flu[-1]
    F95=0.95*F100
    F05=0.05*F100
    for x in finex:
        if uspl(x)<F05:   FLUENCE_05=x
        if uspl(x)>F95:
            FLUENCE_95=x
            break
        pass
    FLUENCE_05=sp.power(10,FLUENCE_05)
    FLUENCE_95=sp.power(10,FLUENCE_95)



    lines=[p1,p2,p3]
    labels=['P.>100 MeV','P.> 1GeV','Flu.>100 MeV']
    plt.legend(lines,labels,bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)



    #finey=uspl(finex)
    #ax5.plot(sp.power(10,finex),finey,'g')

    ax5.plot([COUNTS_95,xmin],[C95,C95],'b--')
    ax5.plot([COUNTS_95,COUNTS_95],[0,C95],'b--')
    #ax1.plot([COUNTS_95,COUNTS_95],[0.9*ts.min(),10*ts.max()],'b--')
    #ax2.plot([COUNTS_95,COUNTS_95],[fluxmin,fluxmax],'b--')
    
    ax5.plot([COUNTS_05,xmin],[C05,C05],'b--')
    ax5.plot([COUNTS_05,COUNTS_05],[0,C05],'b--')
    #ax1.plot([COUNTS_05,COUNTS_05],[0.9*ts.min(),10*ts.max()],'b--')
    #ax2.plot([COUNTS_05,COUNTS_05],[fluxmin,fluxmax],'b--')

    gtsrcprob_x=like_prob_time
    gtsrcprob_y=1.5e-7*sp.ones_like(gtsrcprob_x)
    #gtsrcprob_f=sp.logical_and((like_prob_prob>0.9),gtsrcprob_x>like_durmin_u,gtsrcprob_x<like_durmax_l)    
    gtsrcprob_f=(like_prob_prob>0.9)*(gtsrcprob_x>=like_durmin_u)*(gtsrcprob_x<=like_durmax_l)
    
    extended_first        = -666
    extended_last         = -666    
    extended_first_err    = -666
    extended_last_err     = -666
    extended_max_ene      = -666
    extended_max_ene_prob = -666
    extended_max_ene_time = -666
    extended_max_ene_nth  = gtsrcprob_f.sum()

    if extended_max_ene_nth>0:

        extended_first        = gtsrcprob_x[gtsrcprob_f][0]
        extended_last         = gtsrcprob_x[gtsrcprob_f][-1]        

        extended_first_err    = extended_first - like_durmin_l
        extended_last_err     = like_durmax_u  - extended_last
        extended_max_ene      = like_prob_ener[gtsrcprob_f].max()
        extended_max_ene_prob = like_prob_prob[gtsrcprob_f][like_prob_ener[gtsrcprob_f].argmax()]
        extended_max_ene_time = like_prob_time[gtsrcprob_f][like_prob_ener[gtsrcprob_f].argmax()]

        ax2.plot(gtsrcprob_x[gtsrcprob_f],gtsrcprob_y[gtsrcprob_f],'|r',zorder=10)
        ax2.plot(extended_max_ene_time,1.5e-7,'xg',zorder=11)
        pass
    if extended_max_ene_nth>1:
        extended_first_err = min(extended_first_err,(gtsrcprob_x[gtsrcprob_f][1]-extended_first))
        extended_last_err  = min(extended_last_err, (extended_last-gtsrcprob_x[gtsrcprob_f][-2]))
        pass
    
    print 'Events: n(p>0.9)..:',extended_max_ene_nth
    print ' First Event......:',extended_first,extended_first_err
    print ' Last  Event......:',extended_last,extended_last_err
    print ' First Interval...: ',like_durmin_l, like_durmin_u
    print ' Last  Interval...: ',like_durmax_l, like_durmax_u
    print 'Maximum energy....: ',extended_max_ene
    print 'Maximum energy p .: ',extended_max_ene_prob
    print 'Maximum energy t .: ',extended_max_ene_time
    for a in ax1,ax2,axr:
        a.axvline(x=extended_first,color='g',linestyle='--',zorder=2)
        a.axvline(x=extended_last,color='g',linestyle='--',zorder=2)
        pass
    
    results['EXTENDED_FIRST']  = extended_first
    results['EXTENDED_LAST']   = extended_last
    
    results['EXTENDED_MAXE']   = extended_max_ene
    results['EXTENDED_MAXE_P'] = extended_max_ene_prob
    results['EXTENDED_MAXE_T'] = extended_max_ene_time
    results['EXTENDED_MAXE_N'] = extended_max_ene_nth
    # LIKE_DURMIN is LAT T05
    # and LIKE_DURMAX is LATT95
    
    #if extended_last>extended_first:
    results['LIKE_DURMIN']     = extended_first
    results['LIKE_DURMAX']     = extended_last
    results['LIKE_DURMIN_MIN'] = extended_first - extended_first_err
    results['LIKE_DURMAX_MAX'] = extended_last  + extended_last_err
    #else:
    #    results['LIKE_DURMIN']     = like_durmin_u
    #    results['LIKE_DURMAX']     = like_durmax_l
    #    results['LIKE_DURMIN_MIN'] = like_durmin_l
    #    results['LIKE_DURMAX_MAX'] = like_durmax_u
    #    pass
    
    ax2.plot([results['LIKE_DURMIN_MIN'],results['LIKE_DURMIN']],[2e-7,2e-7],'r',lw=4,alpha=0.5,zorder=2)
    ax2.plot([results['LIKE_DURMAX'],results['LIKE_DURMAX_MAX']],[2e-7,2e-7],'r',lw=4,alpha=0.5,zorder=2)
    ax2.plot([results['LIKE_DURMIN'],results['LIKE_DURMAX']],[2e-7,2e-7],'r',lw=1,alpha=0.5,zorder=2)
        
    axr.plot([FLUENCE_95,xmax],[F95,F95],'m--')
    axr.plot([FLUENCE_95,FLUENCE_95],[0,F95],'m--')
    axr.plot([FLUENCE_05,xmax],[F05,F05],'m--')
    axr.plot([FLUENCE_05,FLUENCE_05],[0,F05],'m--')

    #ax1.plot([FLUENCE_95,FLUENCE_95],[0.9*ts.min(),10*ts.max()],'g--')
    #ax2.plot([FLUENCE_95,FLUENCE_95],[fluxmin,fluxmax],'g--')
    #ax1.plot([FLUENCE_05,FLUENCE_05],[0.9*ts.min(),10*ts.max()],'g--')
    #ax2.plot([FLUENCE_05,FLUENCE_05],[fluxmin,fluxmax],'g--')

    plt.xlim([xmin,xmax])


    ##################################################
    '''ax6 = fig.add_subplot(2,3,6)
    cumulative_obs  = CumulativeNevt - cumulative_obs 
    cumulative_p100 = CumulativeN100 - cumulative_p100
    cumulative_ts   = CumulativeTS   - cumulative_ts  

    color='k'
    p1,=plt.plot(cumulative_x,cumulative_obs,
                c=color,
                marker='None',lw=2)
    color='b'
    p2,=plt.plot(cumulative_x,cumulative_p100,
                c=color,
                marker='None',lw=2)
    

    plt.yscale('log')
    plt.ylabel('Cumulative N (>T-T$_{0}$)')
    plt.ylim([1,max(2,2*CumulativeNevt)])
    if xscale=='log': plt.xscale('log')
    plt.xlabel('T-T$_{0}$')
    #plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)

    color='r'
    axr = ax6.twinx()
    axr.spines["right"].set_visible(True)
    
    p3,=axr.plot(cumulative_x,cumulative_ts,
                c=color,lw=2)
    
    plt.yscale('log')
    plt.ylabel('Cumulative TS (>T-T$_{0}$)')
    axr.tick_params(axis='y', colors='r')
    plt.ylim([1,max(25,2*CumulativeTS)])
    lines=[p1,p2,p3]
    labels=['Obs.','Pred. >100 MeV','TS']
    plt.legend(lines,labels,bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=3, mode="expand", borderaxespad=0.)

    uspl=UnivariateSpline(sp.log10(cumulative_x[cumulative_ts>0]),sp.log10(cumulative_ts[cumulative_ts>0]),s=0,k=1)
    finex=sp.linspace(sp.log10(cumulative_x[0]),sp.log10(cumulative_x[-1]),1000)
    finey=sp.power(10,uspl(finex))
    ACCUMULATION_DUR=0
    if CumulativeTS>ts_min:
        for x in finex:
            if sp.power(10,uspl(x))<ts_min:
                x10=sp.power(10,x)
                ACCUMULATION_DUR=x10
                break
            pass
        axr.plot([ACCUMULATION_DUR,cumulative_x[-1]],[ts_min,ts_min],'m--')
        axr.plot([ACCUMULATION_DUR,ACCUMULATION_DUR],[ts_min,1],'m--')
        ax1.plot([ACCUMULATION_DUR,ACCUMULATION_DUR],[0.9*ts.min(),10*ts.max()],'m--')
        ax2.plot([ACCUMULATION_DUR,ACCUMULATION_DUR],[fluxmin,fluxmax],'m--')
        pass
     '''


    ##################################################
    print ' =========================================================================='
    print ' SUMMARY EXTENDED MISSION ANALYSIS '
    print ' EXTENDED EMISSION .....: START= %10.2f - %10.2f END = %10.2f - %10.2f ' % (results['LIKE_DURMIN_MIN'],results['LIKE_DURMIN'],results['LIKE_DURMAX'],results['LIKE_DURMAX_MAX'])
    print ' FROM COUNTS............: T05  = %10.2f T95 = %10.2f (%10.2f) ' % (COUNTS_05, COUNTS_95, COUNTS_95-COUNTS_05)
    print ' FROM FLUENCE...........: T05  = %10.2f T95 = %10.2f (%10.2f) ' % (FLUENCE_05, FLUENCE_95, FLUENCE_95-FLUENCE_05)
    print ' CUMULATIVE COUNTS  >100 MeV = %10.1f' %(C100)
    print ' CUMULATIVE COUNTS  >  1 GeV = %10.1f' %(C1000)
    print ' CUMULATIVE FLUENCE >100 MeV = %10.2e' %(F100)    
    print ' PEAK FLUX.........................: %.2e +/- %.2e' % (peak_flux,peak_flux_err)
    print ' PEAK FLUX TIME....................: %.2e +/- %.2e' % (peak_flux_time,peak_flux_time_err)
    if alpha_err>0:    print ' DECAY INDEX [ALPHA]...............: %.2f +/- %.2f' % (alpha,alpha_err)
    if a1_err>0:    print ' BPL, DECAY INDEX1 [ALPHA1]...............: %.2f +/- %.2f' % (a1,a1_err)
    if a2_err>0:    print ' BPL, DECAY INDEX2 [ALPHA2]...............: %.2f +/- %.2f' % (a2,a2_err)
    print ' =========================================================================='


    #  LATT05_L = LIKE_DURMIN_MIN
    #  LATT95_U = LIKE_DURMAX_MAX

    results['PeakFlux']          = peak_flux       # ph/cm^2/s
    results['PeakFlux_ERR']      = peak_flux_err      # ph/cm^2/s
    results['PeakFlux_Time']     = peak_flux_time  # s
    results['PeakFlux_Time_ERR'] = peak_flux_time_err # s
    # Fluence
    #results['TimeBeforePeakFlux']             = time_before
    #results['FluenceBeforePeakFlux']     = fluence_before  # ph/cm^2
    #results['FluenceBeforePeakFlux_ERR'] = efluence_before # ph/cm^2
    #results['FluenceAfterPeakFlux']     = fluence_after    # ph/cm^2
    #results['FluenceAfterPeakFlux_ERR'] = efluence_after   # ph/cm^2
    
    #results['TimeAfterPeakFlux']             = time_after    
    #results['EneFluenceBeforePeakFlux']     = enefluence_before  # MeV/cm^2
    #results['EneFluenceBeforePeakFlux_ERR'] = eenefluence_before # MeV/cm^2
    #results['EneFluenceAfterPeakFlux']     = enefluence_after    # MeV/cm^2
    #results['EneFluenceAfterPeakFlux_ERR'] = eenefluence_after   # MeV/cm^2
    
    results['T95_COUNTS']        = COUNTS_95
    results['T05_COUNTS']        = COUNTS_05
    results['T95_FLUENCE']       = FLUENCE_95
    results['T05_FLUENCE']       = FLUENCE_05
    
    results['CUM_FLUENCE']       = F100
    results['CUM_COUNTS']        = C100

    results['AG_F0']             = N
    results['AG_F0_ERR']         = N_err

    results['AG_SPL_IN1']        = alpha
    results['AG_SPL_IN1_ERR']    = alpha_err    

    #results['AG_SPL_DUR']            = spl_t06
    #results['AG_SPL_DUR_ERRL']       = spl_t06_l
    #results['AG_SPL_DUR_ERRU']       = spl_t06_u

    #results['AG_BPL_DUR']            = bpl_t06
    #results['AG_BPL_DUR_ERRL']       = bpl_t06_l
    #results['AG_BPL_DUR_ERRU']       = bpl_t06_u

    results['AG_BPL_F0']         = N2
    results['AG_BPL_F0_ERR']     = N2_err

    results['AG_BPL_TB']         = x0
    results['AG_BPL_TB_ERR']     = x0_err

    
    results['AG_BPL_IN1']       = a1
    results['AG_BPL_IN1_ERR']   = a1_err
    
    results['AG_BPL_IN2']       = a2
    results['AG_BPL_IN2_ERR']   = a2_err
    
    #results['AG_SPL_T0']        = start_SPL_fit
    #results['AG_SPL_T1']        = last_good_t
    
    #results['AG_BPL_T0']        = start_BPL_fit
    #results['AG_BPL_T1']        = last_good_t
    
    results['AG_SPL_CHI2']      = reduced_chi_squared1
    results['AG_BPL_CHI2']      = reduced_chi_squared2
    
    if reduced_chi_squared1<reduced_chi_squared2:
        results['AG_IN']             = alpha
        results['AG_IN_ERR']         = alpha_err
    else:
        results['AG_IN']             = a2
        results['AG_IN_ERR']         = a2_err
        pass
    print 'Saving figures...'
    if fit==0: fig.savefig(InputFileName.replace('.txt','_nofit.png'))
    else:          fig.savefig(InputFileName.replace('.txt','.png'))

    for (i,ax) in enumerate([ax1,ax2,ax3,ax4]):
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        if fit==0 and (i==1 or i==2): fig.savefig(InputFileName.replace('.txt','_%d_nofit.eps' % i), bbox_inches=extent.expanded(1.19, 1.23).translated(-0.48,0))
        else:                         fig.savefig(InputFileName.replace('.txt','_%d.eps' % i), bbox_inches=extent.expanded(1.19, 1.23).translated(-0.48,0))
        pass
    plt.close(fig)
    return results
    
def PrintResults(results,ResultsFileName):
    ''' Print the parameters currentlky in use.'''    
    ResultsFile=file(ResultsFileName,'w')
    ResultsFile.write('# Input Parameters\n')
    keys= sorted(results.keys())
    print '====> Print () =================================================='
    print '# Stored Parameters --------------------------------------------------'    
    for item in keys:
        if not 'FGL ' in item: print item,' = ', results[item]
        ResultsFile.write('%30s = %10s\n' %(item,results[item])) 
        pass
    print '# Output Results --------------------------------------------------'
    ResultsFile.close()
    print '# output written in %s ' % ResultsFileName
    print '=================================================='
    pass

if __name__=='__main__':
    #results={}#'GBMT95':10000}
    # InputFileName="/Users/omodei/Documents/DATA/ExtendedEmissions/like_090814950.txt"
    # InputFileName="/Users/omodei/Documents/DATA/ExtendedEmissions/like_100116897.txt"
    import sys
    #import gtgrb
    from gtgrb import ReadResults
    InputFileNames=sorted(glob.glob(sys.argv[1]))
    useGBM=True
    fit_xmin=None
    fit_xmax=None
    xmin=None
    xmax=None
    include_ul=True
    fit=2
    fluxmax = 1e-1
    fluxmin = 1e-7
    for i,a in enumerate(sys.argv):
        if a=='-gbm': useGBM=bool(sys.argv[i+1])
        elif a=='-xmin': xmin=float(sys.argv[i+1])
        elif a=='-xmax': xmax=float(sys.argv[i+1])
        elif a=='-fit_xmin': fit_xmin=float(sys.argv[i+1])
        elif a=='-fit_xmax': fit_xmax=float(sys.argv[i+1])
        elif a=='-flux_min': fluxmin=float(sys.argv[i+1])
        elif a=='-flux_max': fluxmax=float(sys.argv[i+1])
        elif a=='-no_ul':include_ul=False
        elif a=='-no_fit':fit=int(sys.argv[i+1])
        
        pass
    
    for InputFileName in InputFileNames:
        if '_emax.txt' in InputFileName: continue
        ResultsFileName=glob.glob(InputFileName.split('ExtendedEmission')[0]+'results_*.txt')[0]
        print InputFileName
        print ResultsFileName
        results=ReadResults(ResultsFileName=ResultsFileName,new=1)    
        new_results=PlotExtendedEmission(InputFileName=InputFileName,
                                         inputResults=results,
                                         xscale='log',
                                         ts_min=10,fit=fit,
                                         xmax=xmax,xmin=xmin,useGBM=useGBM,
                                         fluxmax = fluxmax,  fluxmin = fluxmin,
                                         fit_xmin=fit_xmin,fit_xmax=fit_xmax,include_ul=include_ul)
        for k in new_results.keys(): results[k]=new_results[k]
                
        PrintResults(results,ResultsFileName=ResultsFileName)
        plt.show()
        pass
    pass
    
