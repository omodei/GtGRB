#!/usr/bin/env python
import os,sys

def help():
    print ' -o <...>: OUTDIR'
    print ' -g <...>: myGRB'
    print ' -q <...>: queue'
    print ' -b : background subtraction'
    print ' -h : help()'
    exit()
    pass

OUTDIR=os.environ['OUTDIR']
myGRB='GRB'
queue=None
BK=0
REMAKE='False'
for i,a in enumerate(sys.argv):
    if   a=='-o': OUTDIR=sys.argv[i+1]
    elif a=='-g': myGRB=sys.argv[i+1]
    elif a=='-q': queue=sys.argv[i+1]
    elif a=='-h': help()
    elif a=='-b': BK=1
    elif a=='-r': REMAKE='True'
    pass
os.environ['OUTDIR']=OUTDIR
#from scripts.GBMGCN import GBMs
from scripts.GRBs  import *

ALL_GRBs  = GRBs
all_grbs  = sorted(ALL_GRBs.keys())




LC_Options = {'GRB080825C':'DT=0.1  XMIN=-5   XMAX=35 ',
              'GRB080916C':'DT=0.25 XMIN=-5   XMAX=105 DETLIST=\'n3,n4,b0\' NAIANGLE=180',
              'GRB081006' :'DT=0.1  XMIN=-10  XMAX=20 YMIN1=410 YMIN2=310 YMAX1=690 YMAX2=490',
              'GRB081024B':'DT=0.05 XMIN=-1   XMAX=4 YMIN1=120 YMAX1=300 YMIN2=45 YMAX2=115  ',
              'GRB081207': 'DT=10.0 XMIN=-100 XMAX=300 ',
              'GRB081215' :'DT=0.05 XMIN=-1   XMAX=20 ',
              'GRB081224' :'DT=0.1  XMIN=-5   XMAX=52 ',              
              'GRB090217' :'DT=0.1  XMIN=-5   XMAX=50 YMIN3=-0.5 ',              
              'GRB090227' :'DT=.5   XMIN=-10  XMAX=60 ',              
              'GRB090227B':'DT=0.01 XMIN=-1   XMAX=1.5 ',              
              'GRB090323' :'DT=0.5  XMIN=-10  XMAX=200 ',              
              'GRB090328' :'DT=0.5  XMIN=-10  XMAX=300 ',              
              #'GRB090429D':'DT=0.1 XMIN=-20  XMAX=100 ',              
              'GRB090510' :'DT=0.01 XMIN=-0.5 XMAX=6.0 ',
              'GRB090531B':'DT=0.05 XMIN=-5   XMAX=10 ',              
              'GRB090626' :'DT=0.25 XMIN=-10  XMAX=100 ',              
              'GRB090902B':'DT=0.25 XMIN=-10  XMAX=100 ',              
              'GRB090926' :'DT=0.25 XMIN=-10  XMAX=100 ',                            
              'GRB091003' :'DT=0.1  XMIN=-20  XMAX=100 ',              
              'GRB091031' :'DT=0.5  XMIN=-20  XMAX=100 ',              
              'GRB100116A':'DT=0.5  XMIN=-20  XMAX=130 ',              
              'GRB100225A':'DT=0.5  XMIN=-20  XMAX=100 ',              
              'GRB100325A':'DT=0.5  XMIN=-20  XMAX=80  DETLIST=\'n0,n3,n6,b0\' NAIANGLE=180',              
              'GRB100414A':'DT=0.5  XMIN=-5   XMAX=100  DETLIST=\'n9\' NAIANGLE=180',              
              'GRB100707A':'DT=0.25 XMIN=-20  XMAX=60  ',              
              'GRB100724B':'DT=0.25 XMIN=-20  XMAX=170 ',              
              'GRB100728A':'DT=0.75 XMIN=-20  XMAX=300 ',
              'GRB100826A':'DT=1.0  XMIN=-20  XMAX=260 ',
              'GRB101014A':'DT=1.0  XMIN=-20  XMAX=500 ',              
              'GRB101123A':'DT=0.5  XMIN=-20  XMAX=200 ',              
              'GRB110120A':'DT=0.5  XMIN=-20  XMAX=200 ',              
              'GRB110328B':'DT=0.5  XMIN=-20  XMAX=200 ',              
              'GRB110428A':'DT=0.1  XMIN=-5  XMAX=30 ',                            
              'GRB110529A':'DT=0.01 XMIN=-1   XMAX=3 ',
              'GRB110625A':'DT=0.1  XMIN=-20  XMAX=100 ',
              'GRB110721A':'DT=0.05 XMIN=-3   XMAX=35  ',
              'GRB110731A':'DT=0.05 XMIN=-5   XMAX=20  '
              } 

array=[]
for grb in all_grbs:
    if myGRB in grb: array.append(grb)
    pass

IRFS="P6_V3_TRANSIENT"

for g in array:
    #if 'GRB' in g :
    options=''
    if g in LC_Options.keys(): options = LC_Options[g]
    options=options+' BK=%s REMAKE=%s ' %(BK,REMAKE)
    options=options+' IRFS=%s' % (IRFS)    
    print options
    cmd='gtgrb.py grbname=%s -go -exe computeCompositeLightCurve FT1="" FT2="" %s' %(g,options)
    if queue in ['medium','short','long','xlong','xxl']: cmd = 'bsub -q medium -o logfiles/%s_compositeLC.log %s -nox ' % (g,cmd)
    elif queue in ['nox']:  cmd='gtgrb.py grbname=%s -nox -go -exe computeCompositeLightCurve FT1="" FT2="" %s' %(g,options)
    #cmd='submitJob.py -q medium grbname=%s -exe computeCompositeLightCurve FT1="" FT2="" %s' %(g,LC_Options[g])
    print '--------------------------------------------------'
    print cmd
    os.system(cmd)
    print '--------------------------------------------------'
    
    pass

        
