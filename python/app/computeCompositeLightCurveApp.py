#!/usr/bin/env python
from gtgrb import *
from glob import glob
import sys,os

def Go(base,opts):
    mode='go'
    if base[-1]=='/': base=base[:-1]
    print '***************************************************'
    print ' MAKE THE COMPOSITE LIGHT CURVE IN %s' %base
    print '***************************************************'
    mydict=ListToDict(opts)
    
    OUTDIR=base[:base.rfind('/')]
    os.environ['OUTDIR']=OUTDIR
    remake = False
    ResultsFileName=glob('%s/results*txt'%base)[0]
    ResultsFileName = ReadResults(ResultsFileName=ResultsFileName)
    
    if ResultsFileName is None:
        remake = True
        return 0
    os.system('rm %s/*_CompoLC.txt' % base)

    SetGRB()

    if not remake and 'REMAKE' in mydict:
        REMAKE = mydict['REMAKE']
        if 'true' in REMAKE.lower(): remake = True
        elif 'false' in REMAKE.lower(): remake = False
        else:
            print 'REMAKE should be either "True" or "False". Current value is: %s ' % REMAKE
            pass
        pass
    
    if remake:
        print 'Regenerating some quantities...'
        PlotAngularSeparation(mode=mode)
        # GetGBMFiles()
        MakeGBMLightCurves(mode=mode)
        # GetLLE() # This will get the data.
        # #################################################
        # This is from TSRAT to TSTOP, saving the output in _ROI_E directory    
        # MakeSelectEnergyDependentROI(mode=mode) # This provides the events
        # #################################################
        print 'SELECT...'
        MakeSelect(mode=mode,use_in_composite=1,plot=0) # This provides the events
        Print()
        pass
    GetLLE() # This will get the data.
    #Print() # Save all in the results
    # try:
    #    mydict['DT']=results['LLE_DetBin']
    # except:
    #    pass
    # Print()
    # MakeGBMLightCurves(mode=mode) # This provide the GBM curves
    MakeCompositeLightCurve(**mydict) # combine the LC to make a beautiful plot
    os.system('rm %s/jobTag.txt' % base)
    #Done() # Save and exit
    pass



if __name__=='__main__':       
    print 'You can use this script to remake the composite LC plot.'
    print ' You have to enter the path to the GRB you want to process'
    print ' computeCompositeLightCurve.py DATA/.../ var=val'
    print '***************************************************'
    import ROOT

    options=[]    
    if len(sys.argv) > 0:
        baseDir  = sys.argv[1]
        for a in sys.argv:
            if '=' in   a: options.append(a)
            elif a=='-nox':
                os.environ['ROOTISBATCH']='Y'
                #os.environ['DISPLAY']='/dev/null'
                ROOT.gROOT.SetBatch(True)
                pass
            pass
        
        outDirs=sorted(glob(baseDir))
        for baseDir in outDirs:
            if os.path.isdir(baseDir): Go(baseDir,options)
            pass
        pass
    pass
