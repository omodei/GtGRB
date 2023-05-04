# 0) GENERAL SETUP
import os
mydict=ListToDict(sys.argv)
Set(**mydict)
# RESET THE POSITION AT THE SUN
MET = grb[0].Ttrigger
DELTA_T = float(mydict['GRBT90'])
make_tsmap=1
if 'MAKE_TSMAP' in mydict.keys():  make_tsmap=float(mydict['MAKE_TSMAP'])
if make_tsmap==0: print '==> THE TS MAP WILL NOT BE COMPUTED!'
else: print '==> THE TS MAP WILL BE COMPUTED!'
#SD=sunpos.getSunPosition(MET+DELTA_T/2.)
#RA_SUN,DEC_SUN=SD.ra(),SD.dec()

#SetVar('RA',RA_SUN)
#SetVar('DEC',DEC_SUN)

#SetGRB()

mode='go'
Print()

#print "***** MAKE FULL SKYMAP *****"
#outfile     = lat[0].evt_file.replace('_LAT_ROI.fits','_LAT_FULL.fits')
#map_outfile = lat[0].evt_file.replace('_LAT_ROI.fits','_LAT_FULL_cmap.fits')
#rad0=lat[0].radius
#zmax0=lat[0].zmax
#outfile0=lat[0].evt_file
#XREF=90 #180
#lat[0].make_select(infile=lat[0].FilenameFT1,tmin=MET,tmax=MET+DELTA_T,ra=0,dec=0,rad=180,outfile=outfile)
#lat[0].make_skymap(evfile=outfile,outfile=map_outfile,nxpix=3600,nypix=1800,binsz=0.1, coordsys='CEL', proj='AIT',rafield='RA', decfield="DEC", xref=XREF,yref=0)

#lat[0].radius   = rad0
#lat[0].zmax     = zmax0
#lat[0].evt_file = outfile0
#os.system('rm -f %s' % outfile)
#dt=1.0
#if DELTA_T>3600: dt=60.
#if DELTA_T>86400: dt=3600.
#if DELTA_T>86400*7: dt=3*3600.
#if DELTA_T>86400*14: dt=86400.

# 1) PLOT THE ANGULAR SEPARATION
try:      PlotAngularSeparation(mode=mode,before=60,after=60)
except:   print 'ERROR:: PlotAngularSeparation(mode=mode,before=60,after=60)'    

try:      PlotAngularSeparation(mode=mode,before=DELTA_T,after=DELTA_T)
except:   print 'ERROR:: PlotAngularSeparation(mode=mode,before=DELTA_T,after=DELTA_T)'


# 2) MAKE THE LLE LIGHTCURVE
#srctmin = -60   # Minimum time of the beginning of the GRB window
#srctmax = 600   # Maximum time of the beginning of the GRB window
#lctmin  = -DELTA_T   # Minimum time Window, including BKG (must be <srctmin)
#lctmax  = DELTA_T   # Maximum time Window, including BKG (must be >srctmax)
    
#try: MakeLLELightCurves(dt=10,ds=0,srctmin=srctmin,srctmax=srctmax,lctmin=lctmin,lctmax=lctmax)
#except: 'ERROR:: MakeLLELightCurves(dt=10,ds=0,srctmin=srctmin,srctmax=srctmax,lctmin=lctmin,lctmax=lctmax)'

#Print()

#GetGBMFiles()
#MakeGBMLightCurves()

# 3) SELECT THE DATA
#MakeSelect(tstart=0,tstop=60,suffix='_1min')
#MakeSelect(tstart=0,tstop=600,suffix='_10min')
#MakeSelect(tstart=0,tstop=3600,suffix='_1hour')
MakeSelect(tstart=0,tstop=DELTA_T,suffix='_DELTA_T')
Print()
# 3) MAKE THE LIKELIHOOD ANALYSIS
MakeLikelihoodAnalysis(tstart=0,tstop=DELTA_T,pha=0,tsmap=0,extended=0,prob=1,mode=mode,suffix='LIKE_MY')
Print()
if make_tsmap:
    MakeGtTsMap(like_suffix='LIKE_MY',refitting='yes',UPDATE_POS='yes')
    Print()
    if 'TSMAP_MAX' in results.keys() and results['TSMAP_MAX']>0:
        SetVar('RA',results['TSMAP_RAMAX'])
        SetVar('DEC',results['TSMAP_DECMAX'])
        SetGRB() 
        MakeLikelihoodAnalysis(tstart=0,tstop=DELTA_T,pha=0,tsmap=1,extended=0,prob=1,mode=mode,suffix='LIKE_UP')
        pass
    pass
# 4) SAVE AND EXIT
Done()
