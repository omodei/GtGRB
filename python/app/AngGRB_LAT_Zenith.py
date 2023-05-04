#!/usr/bin/env python

'''
This script will take as input:
- GRB ra
- GRB dec
- Trigger time
- FT2 file

It will output 2 plots:
- the GRB angle with respect to the local zenith of the earth at the postion of
the spacecraft between tstart and tend
- the GRB angle with respect to the LAT pointing direction between tstart and tend

The angle of your "favorite earth limb" can be specified via the variable earth_ang.

If you do not want to sepecify the GRB trigger time and have these plots in function of MET time, set the variable ttrig_opt to False.
'''

import sys
import math
#import astropy.io.fits as pyfits
#import pylab
from GTGRB import *


def plotSeparation(ra_grb,dec_grb,time_grb,ft2file):
  MET, AngGRBZenith, AngGRBSCZ, SAA, AngGRBSCZ_0, AngGRBZenith_0 = latutils.AngSeparation(ra_grb,dec_grb,time_grb,ft2file)  
  c1 = plotter.plotAngSeparation_ROOT(time_grb, MET, AngGRBZenith, AngGRBSCZ, SAA, AngGRBSCZ_0, AngGRBZenith_0)
  pass

def getTheta(ra_grb,dec_grb,time_grb,ft2file):
  return float(latutils.GetTheta(ra_grb,dec_grb,time_grb,ft2file))


def getZenith(ra_grb,dec_grb,time_grb,ft2file):
  return float(latutils.GetZenith(ra_grb,dec_grb,time_grb,ft2file,0))
               
def getMcIlWain(time_grb,ft2file):
  (McIlWain_L,McIlWain_B) = latutils.GetMcIlWain(time_grb,ft2file,0)
  return  (McIlWain_L,McIlWain_B) 


if __name__=='__main__':
  print 'running...'
  plot=0
  for (i,a) in enumerate(sys.argv):
    if a=='-ra': ra_grb=float(sys.argv[i+1])
    if a=='-dec': dec_grb=float(sys.argv[i+1])
    if a=='-t': Ttrig=float(sys.argv[i+1])
    if a=='-ft2': ft2file=sys.argv[i+1]
    if a=='-p': plot=1
    pass
  print 50*'-'
  print 'Theta: %.2f' % getTheta(ra_grb,dec_grb,Ttrig,ft2file)
  print 'Zenith: %.2f' % getZenith(ra_grb,dec_grb,Ttrig,ft2file)
  print 'McIlWain L,B: (%.2f,%.2f)' % getMcIlWain(Ttrig,ft2file)
  print 50*'-'
  if plot:plotSeparation(ra_grb,dec_grb,Ttrig,ft2file)
  

