#!/usr/bin/env python

import os
os.environ['OUTDIR']='DATA/110501-v00-05-00_SpectralFiles'
os.system('mkdir -p $OUTDIR')
intervals={'GRB080825C':[  0.000,  3.200, 20.990, 29.900],
           'GRB080916C':[  0.000,  5.100, 62.980,215.500],
           'GRB081006':[  0.000,  0.000,  6.400,115.000],
           'GRB081024B':[  0.000,  0.100,  0.640, 22.000],
           'GRB081215':[  0.000,  0.000,  5.568,  0.000],
           'GRB081224':[  0.000, 12.000, 16.440,271.500],
           'GRB090217':[  0.000,  6.100, 33.281,170.700],
           'GRB090227B':[  0.000,  0.000,  1.280,  0.000],
           'GRB090323':[  0.000, 26.000,135.170,319.500],
           'GRB090328':[  0.000, 63.400, 61.697,785.700],
           'GRB090429D':[  0.000,  0.000,  0.640,  0.000],
           'GRB090510':[  0.000,  0.500,  0.960, 70.700],
           'GRB090531B':[  0.000,  0.000,  0.768,  0.000],
           'GRB090626':[  0.000, 40.700, 48.900,558.800],
           'GRB090902B':[  0.000,  0.000, 19.330,825.000],
           'GRB090926':[  0.000,  0.000, 13.760,225.000],
           'GRB091003':[  0.000,  5.500, 20.220,501.800],
           'GRB091031':[  0.000,  3.200, 33.920,214.800],
           'GRB100116A':[  0.000,  0.000,102.530,141.000],
           'GRB100225A':[  0.000,  0.000, 12.990,  0.000],
           'GRB100325A':[  0.000,  0.000,  7.100,  0.000],
           'GRB100414A':[  0.000, 17.700, 26.500,356.000],
           'GRB100707A':[  0.000,  0.000, 81.790,  0.000],
           'GRB100724B':[  0.000,  0.000, 87.000,  0.000],
           'GRB100728A':[  0.000,  0.000,162.900,  0.000],
           'GRB101014A':[  0.000,  0.000,450.900,  0.000],
           'GRB101123A':[  0.000,  0.000,160.000,  0.000],
           'GRB110120A':[  0.000,  0.000,100.000,  0.000]}

pipeline = 1

for k in sorted(intervals.keys()):
    inter    =  intervals[k]
    PHAStart = '[%s,%s,%s]'% (inter[0],inter[1],inter[2])
    PHAstop  = '[%s,%s,%s]'% (inter[1],inter[2],inter[3])
    params = 'FLAT_ROI=0 PHAstart=%s PHAstop=%s GBM_SPECTRA=0 BKGE=1' %(PHAStart,PHAstop)    
    cmd='./app/gtgrb.py grbname=%s -exe app/computeSpectralFiles.py -go -nox %s' %(k,params)
    pipe='./pipeline/submitJob.py -f %s -exe app/computeSpectralFiles.py -q xxl %s' %(k,params)
    if pipeline: print pipe; os.system(pipe)
    else: print cmd
    pass
