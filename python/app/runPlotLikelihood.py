#!/usr/bin/env python
if __name__=='__main__':
    import glob,sys,os
    in_dir=glob.glob(sys.argv[1])
    
    for i,f in enumerate(sorted(in_dir)):
        if len(glob.glob('%s/results*' % f))>0:
            cmd='computeLikelihoodPlots.py -d %s -nox -write ' %(f)
            if '-p' in sys.argv: cmd='bsub -q medium -o log_%03i.log %s ' %(i,cmd)
            print cmd                            
            if '-t' not in sys.argv: os.system(cmd)        

            pass
        pass
    pass
    
