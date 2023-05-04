TMIN=239414400
TMAX=258422400 # March 11th,2009

GRBTRIGGERDATE = TMIN
OFFSET=0.0
EXPOSURE=TMAX-TMIN # 86400
RA=128.8272
DEC=-45.1762
ROI = 10.0
EMIN= 50.
EMAX= 300000.0
LTMIN=0.0
LTMAX=1.0

name='Vela'
IRFS           = 'P6_V3_DIFFUSE'

FT1            = '/nfs/farm/g/glast/u31/dpaneque/M421_AllData_v3/AllMonthsMerged/FT_FILES/ft1.fits'
FT2            = '/nfs/farm/g/glast/u31/dpaneque/M421_AllData_v3/AllMonthsMerged/FT_FILES/ft2.fits'

index=None

print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
##################################################

grb=GRB.GRB(name)
grb_trigger=GRBTRIGGERDATE
grb.Ttrigger=grb_trigger

lat=LAT.LAT(grb=grb,ft1=FT1,ft2=FT2)

ft1=lat.FilenameFT1
ft2=lat.FilenameFT2

print ft1
print ft2

grb.CreateROOTFile()

#emin,emax=lat.GetEMaxMin()
#tmin,tmax=lat.GetTMaxMin()
#dmin=genutils.met2date(tmin,'fff')
#dmax=genutils.met2date(tmax,'fff')

#d_grb_trigger=genutils.met2date(grb_trigger,'fff')

#print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
#print '           In file:       '
#print ' TMIN: ',tmin,'(',dmin[0].isoformat(),')'
#print ' TMAX: ',tmax,'(',dmax[0].isoformat(),')'
#print ' Emin: ',emin
#print ' Emax: ',emax
#print ' GRB Trigger time: ',grb_trigger,'(',d_grb_trigger[0].isoformat(),')'
#print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'

tstart= grb_trigger + OFFSET
tstop = tstart     + EXPOSURE

lat.setEmin(EMIN)
lat.setEmax(EMAX)

lat.setTmin(tstart)
lat.setTmax(tstop)

lat.setRa(RA)
lat.setDec(DEC)    
lat.setROI(ROI)

lat.SetResponseFunction(IRFS)

lat.print_parameters()
# select data #
zmax=105.0
evclsmin=0

a=raw_input('make select? [y/N]')
if (a.upper()=='Y'):
    lat.fselect(expr='CTBCLASSLEVEL>2')
    lat.make_select(zmax=zmax,evclsmin=0)#evclsmin)
    lat.make_gtmktime()
    lat.SaveEvents2Root()
    pass
a=raw_input('make skymap? [y/N]')
if (a.upper()=='Y'):
    binsz=float(raw_input('Bin size (degrees):'))
    print ROI/binsz
    lat.make_skymap(nxpix=int(ROI/binsz), nypix=int(ROI/binsz), binsz=binsz)
    lat.plotCMAP(drawopt="colz")
    ds9= '~/ds9 -width 300 -height 300 %s -smooth yes -smooth radius 3 -cmap Cool -zoom to fit' % (lat.mp_outFile) #,RA,DEC)
    print ds9
    try:
        os.system(ds9)
    except:
        'cannot execute %s ' % ds9
        pass
    pass

a='y'#raw_input('make expCube? [y/N]')
if (a.upper()=='Y'):
    lat.make_expCube()

#a=raw_input('make expMap? [y/N]')
if (a.upper()=='Y'):    
    lat.make_expMap()

#a=raw_input('make diffrsp? [y/N]')
if (a.upper()=='Y'):    
    lat.make_gtdiffrsp()

    
a=raw_input('compute LAT spectrum (PYLIKE)? [y/N]')
if (a.upper()=='Y'):
    
    like,my_obs=lat.pyLike()
    print 'TS (GRB)=', like.Ts('GRB')
    lat.plotSpectrum_ROOT()
    pass

##################################################
    
