#! /usr/bin/env python
from GTGRB import XSPEC, LAT, GBM, GRB
import sys
import os
import glob

def GBM_spectrum(grb=None,tstart=0,tstop=100,x='no'):
    # create an XSPEC script
    # all necessary information can be found in grb
    spectrumfilename = grb.out_dir+'/GBM_fit.ps'
    if(x=='yes'):
        spectrumfilename = 'X'
        pass
    scriptname = grb.out_dir+'/GBM_fit.xcm'
    outputfile = grb.out_dir+'/GBM_fit.dat'
    print "XSPEC input and output files: ",spectrumfilename,scriptname,outputfile
    
    Detectors=[]
    PHAfiles={}
    RSPfiles={}
    BAKfiles={}

    ############  GBM  ########
    closer_detectors=grb.GBMdetectors

    for gbm_det in closer_detectors:
        
        gbm=GBM.GBM(grb=grb,detector_name=gbm_det)
        gbm.make_time_select(tstart,tstop)
        gbm.make_bkg()
        gbm.make_rsp()
        gbm.make_pha1()
        
        Detectors.append(gbm_det)
        PHAfiles[gbm_det] = gbm.sp_outFile
        RSPfiles[gbm_det]  = gbm.rsp_File
        BAKfiles[gbm_det]  = gbm.back_File
        

    XSPEC.MakeScript(PHAfiles,
                     RSPfiles,
                     BAKfiles,
                     Detectors,
                     area = False,
                     model = 'grbm',
                     statistics = 'chi',
                     script = scriptname,
                     outfile = outputfile,
                     CalcFlux = False,
                     deltafit=0,
                     SpectrumFileName = spectrumfilename
                     )
    
    # perform the fit
    XSPEC.Fit(scriptname)
    os.system('gv '+spectrumfilename+' &')
    print "Results saved in %s"%outputfile
    return spectrumfilename
    
def LAT_spectrum(grb=None, lat=None,x='no'):
    #    g=GRB.GRB(grb_name)
    #    l=LAT.LAT(g)
    
    # all necessary information can be found in grb
    scriptname = grb.out_dir+'/LAT_fit.xcm'
    outputfile = grb.out_dir+'/LAT_fit.dat'
    spectrumfilename = grb.out_dir+'/LAT_fit.ps'
    if(x=='yes'):
        spectrumfilename = 'X'
        pass



    Detectors=[]
    PHAfiles={}
    RSPfiles={}
    BAKfiles={}

    if not os.path.exists(lat.evt_file):
        lat.make_select()
    if not os.path.exists(lat.sp_outFile):
        lat.make_pha1()
    if not os.path.exists(lat.rsp_File):
        lat.make_rsp()
    Detectors=['LAT']
    PHAfiles['LAT'] = lat.sp_outFile
    RSPfiles['LAT'] = lat.rsp_File
    BAKfiles['LAT'] = ''

    XSPEC.MakeScript(PHAfiles,
                     RSPfiles,
                     BAKfiles,
                     Detectors,
                     area = False,
                     model = 'pow',
                     statistics = 'cstat',
                     script = scriptname,
                     outfile = outputfile,
                     CalcFlux = False,
                     deltafit=0,
                     SpectrumFileName=spectrumfilename)
    
    XSPEC.Fit(scriptname)
    return spectrumfilename

def JOINT_spectrum(grb=None,lat=None,tstart=0,tstop=0,x='no'):
    # g=GRB.GRB(grb_name)
    
    # all necessary information can be found in grb
    scriptname = grb.out_dir+'/Joint_fit.xcm'
    outputfile = grb.out_dir+'/Joint_fit.dat'
    spectrumfilename = grb.out_dir+'/Joint_fit.ps'
    if(x=='yes'):
        spectrumfilename = 'X'
        pass
    Detectors=[]
    PHAfiles={}
    RSPfiles={}
    BAKfiles={}

    
    ############  GBM  ########
    
    closer_detectors=grb.GBMdetectors
    

    for gbm_det in closer_detectors:
        gbm=GBM.GBM(grb=grb,detector_name=gbm_det)
        gbm.make_time_select(tstart,tstop)
        gbm.make_bkg()
        gbm.make_rsp()
        gbm.make_pha1()

        gbm.make_bkg()
        Detectors.append(gbm_det)
        PHAfiles[gbm_det] = gbm.sp_outFile
        RSPfiles[gbm_det]  = gbm.rsp_File
        BAKfiles[gbm_det]  = gbm.back_File
        
    ############  LAT  ########
    #   l=LAT.LAT(g)

    Detectors.append('LAT')
    if not os.path.exists(lat.evt_file):
        lat.make_select()
    if not os.path.exists(lat.sp_outFile):
        lat.make_pha1()
    if not os.path.exists(lat.rsp_File):
        lat.make_rsp()
    PHAfiles['LAT'] = lat.sp_outFile
    RSPfiles['LAT'] = lat.rsp_File
    BAKfiles['LAT'] = ''

    XSPEC.MakeScript(PHAfiles,
                     RSPfiles,
                     BAKfiles,
                     Detectors,
                     area = False,
                     model = 'grbm',
                     statistics = 'cstat',
                     script = scriptname,
                     outfile = outputfile,
                     CalcFlux = False,
                     deltafit=0,
                     SpectrumFileName = spectrumfilename
                     )
    
    # perform the fit
    XSPEC.Fit(scriptname)
    return spectrumfilename

if __name__ == "__main__":

    grb=GRB.GRB(sys.argv[1])
    start=grb.TStart-5.
    stop=grb.TStart+105.
    
    detector_name=sys.argv[2]
    if (detector_name=='LAT'):
        lat=LAT.LAT(grb=grb)
        try:
            lat.SetResponseFunction(sys.argv[3])
        except IndexError:
            print 'Using default IRFS: ',lat._ResponseFunction
        spectrum = LAT_spectrum(grb=grb, lat=lat)
        print 'XSPEC LAT analysis, done!'
    elif (detector_name=='GBM'):
        spectrum = GBM_spectrum(grb=grb,tstart=start,tstop=stop)
        print 'XSPEC GBM analysis, done!' 
    elif (detector_name=='ALL'):
        lat=LAT.LAT(grb=grb)
        try:
            lat._ResponseFunction=sys.argv[3]
        except IndexError:
            print 'Using default IRFS: ',lat._ResponseFunction
        spectrum = JOINT_spectrum(grb=grb,lat=lat,tstart=start,tstop=stop)
        print ' XSPEC JOINT analysis, done!'
    else:
        print 'makeXSPEC.py <GRBname> <LAT|GBM|ALL>'
    os.system('gv '+spectrum+ '&')
