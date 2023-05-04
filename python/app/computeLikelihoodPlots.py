#!/usr/bin/env python
# Author Nicola Omodei
##################################################
def PrintOut(out_dir,grb_name):
    ''' Print the parameters currentlky in use.'''    
    ResultsFileName='%s/results_%s.txt' % (out_dir,grb_name)
    ResultsFile=file(ResultsFileName,'w')
    ResultsFile.write('# Input Parameters\n')

    keys= sorted(results.keys())
    print '====> Print () =================================================='
    print '# Stored Parameters --------------------------------------------------'    
    for item in keys:
        print item,' = ', results[item]
        ResultsFile.write('%30s = %10s\n' %(item,results[item])) 
        pass
    print '# Output Results --------------------------------------------------'
    ResultsFile.close()
    print '# output written in %s ' % ResultsFileName
    print '=================================================='
    pass
##################################################
def Go(baseDir,xscale,write,xmin,xmax,fit,tsmin=None):
    print 'Using %s  scale' % xscale
    baseDir=baseDir.strip()
    if baseDir[-1] == '/': baseDir=baseDir[:-1]
    
    grbName = baseDir.split('/')[-1]
    print 'RUNNING GRBNAME: %s, in Directory %s' %(baseDir, grbName)
    results_fileName='%s/results_%s.txt' % (baseDir,grbName)
    like_fileName='%s/ExtendedEmission/like_%s.txt' % (baseDir,grbName)
    results= ReadResults(ResultsFileName = results_fileName, overw=1)    
    print results

    if tsmin is None:   ts_min=results['TSMIN_EXT']
    else:               ts_min=tsmin
    
    from scripts import PlotExtendedEmission
    results1 = PlotExtendedEmission.PlotExtendedEmission(like_fileName,results,xscale,ts_min=ts_min,xmin=xmin,xmax=xmax,fit=fit)
    AddResults(results1)
    # ------------------------------------------------------ #
    prob_filename ='%s/ExtendedEmission/like_%s_emax.txt' % (baseDir,grbName)
    from GTGRB import latutils
    results1=latutils.ParseProbabilityFile(prob_filename)
    AddResults(results1)
    # ------------------------------------------------------ #
    if write: PrintOut(baseDir,grbName)
    # ------------------------------------------------------ #               
    pass
##################################################



if __name__=='__main__':
    def myhelp():
        print 'You can use this script to remake likelihood plot.'
        print ' You have to enter the path to the GRB you want to process'
        print ' computeLikelihoodPlots.py DATA/.../ options'
        print 'Options are:'
        print '-d (directory: needed options)'
        print '==== optional:'
        print '-l (linear scale)'
        print '-nox (no X11 display)'
        print '-xmin <xmin>'
        print '-xmax <xmax>'
        print '-nofit (do not perform any fit)'
        print '-write (write the output)'
        pass
    
    from gtgrb import *
    from glob import glob
    import sys,os
    
    xscale='log'
    write = False
    outDirs=None
    fit=1
    xmin=None
    xmax=None
    tsmin=None
    for i,a in enumerate(sys.argv):
        if a=='-d': outDirs  = glob(sys.argv[i+1])
        if a=='-l': xscale='lin'
        if a=='-nox': ROOT.gROOT.SetBatch(True)        
        if a=='-xmin': xmin = float(sys.argv[i+1])
        if a=='-xmax': xmax = float(sys.argv[i+1])
        if a=='-nofit': fit=0
        if a=='-tsmin': tsmin=float(sys.argv[i+1])
        if a=='-write': write=True
        pass
    if outDirs is None: myhelp()
    elif len(outDirs)>0:
        for baseDir in outDirs:
            if os.path.isdir(baseDir): Go(baseDir,xscale,write,xmin=xmin,xmax=xmax,fit=fit,tsmin=tsmin)
            pass        
        pass
    else:  myhelp()
    pass
