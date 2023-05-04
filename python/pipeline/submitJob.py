#!/usr/bin/env python
import os,sys
import datetime
import subprocess

from scripts.GRBs  import *
from GtBurst import IRFS

def checkJobs(JobName): 
    return False
#    out=subprocess.check_output('bjobs', shell=True)    
#    if JobName in out: 
#        return True
#    else: 
#        return False
    
def ParseOptions(gtgrb_option):
    dict={}
    opt_arr = gtgrb_option.split()
    for vars in opt_arr:
        vars_name = vars.split('=')[0].strip()
        vars_val  = vars.split('=')[1].strip()
        if vars_name == 'GRBNAME':
            dict[vars_name]=vars_val
        else:
            try:
                dict[vars_name]=float(vars_val)
            except:
                dict[vars_name]=vars_val            
                pass
            pass
        pass
    return dict

def getArch():
    rhversion=file('/etc/redhat-release','r').readlines()
    return int(rhversion[0].split('release')[1].split('.')[0])

def submitJob(INFILE='computeAll2',
              QUEUE='xlong',
              LOGFILE='',
              ONLYROLLBACK=False,
              gtgrb_option=''):
    queues=['short','medium','long','xlong','xxl']
    wtime={'short':'00:59',
           'medium':'06:00',
           'long':'12:00',
           'xlong':'24:00',
           'xxl':'120:00'
           }
    PIPELINE = 0
    try:
        CLEANUP  = int(os.environ['CLEANUP'])
    except:
        CLEANUP  = 1
        pass

    try:
        UCLEANUP  = int(os.environ['UCLEANUP'])
    except:
        UCLEANUP  = 0
        pass

    if CLEANUP==0: print 'submitJob.py :: CLEANUP disabled. All the files will be copy back!'
    TEST     = 0
    OS_VERS=getArch()
    if QUEUE in queues:       PIPELINE=1
    if QUEUE.upper()=='TEST': PIPELINE=-1

    print '##################################################'
    print '### submitJob : PIPELINE=%d,ONLYROLLBACK=%s,QUEUE=%s' %(PIPELINE,ONLYROLLBACK,QUEUE)
    print '### gtgrb options: %s ' % gtgrb_option 
    print '##################################################'    
    print 'Running the job from: %s' % INFILE
    
    inDir     = os.environ['INDIR']   #  DATA/FITS
    outDir    = os.environ['OUTDIR']  #  This is the final location
    logsDir   = os.environ['LOGS']    #  This are where the log files are stored
    old_base  = os.environ['BASEDIR'] #  This is where the job is executed locally
    try: jobpre=os.environ['JOBPRE']
    except: jobpre=''

    print 'Setting of the local variables'
    print 'inDir=',inDir
    print 'outDir=',outDir
    print 'logsDir=',logsDir
    print 'old_base=',old_base
    
    extension=outDir[outDir.rfind('/')+1:]
    
    parsed_options = ParseOptions(gtgrb_option)    
    jobSubmitted     = 0
    jobSubmittedTrue = 0

    #1 Case 1. No mame is provided. REQUIRED: RA, DEC, MET, DURATION, one run.
    if 'GRBNAME' in parsed_options.keys():
        fullName=parsed_options['GRBNAME']
        print 'Seeting name to GRBNAME:', fullName
    else:
        grb_trigger  = parsed_options['GRBTRIGGERDATE']
        grb_date,fff = genutils.met2date(grb_trigger,'fff')
        yy           = grb_date.year
        mm           = grb_date.month
        dd           = grb_date.day
        fullName     = '%02i%02i%02i%03i' %(yy-2000,mm,dd,fff)            
        pass
    jobName      = jobpre+fullName
    
    # Check if the job already run, or is running or failed:

    fullOutDir   = '%s/%s' % (outDir,fullName) 
    results_file = '%s/results_%s.txt'%(fullOutDir,fullName)
    jobTagName   = '%s/jobTag.txt' % (fullOutDir)

    jobTagExists        = os.path.exists(jobTagName)
    results_file_exists = os.path.exists(results_file)
    
    execute_job  = True
    
    if ONLYROLLBACK and not jobTagExists and results_file_exists:  execute_job = False
    if PIPELINE==1 and checkJobs(jobName): execute_job = False
    if execute_job==False:
        print "Job %s will not be executed" % jobName
        return
    # Preparing the local disk:
    if not TEST:
        os.system('rm -rf %s' % fullOutDir)
        os.system('mkdir -pv %s' % fullOutDir)
        pass

    if PIPELINE==1:
        os.environ['PIPELINE']='YES'
        now=datetime.datetime.now()
        RANDOM = '%i%i%i%i%i%i%i' %(now.year,now.month,now.day,now.hour,now.minute,now.second,now.microsecond)
        # Setting the stage
        stage      = '/scratch/gtgrb_%s_%s' %(RANDOM,jobName) #RANDOM)
        stage_in   = '%s/IN'  %(stage)
        stage_out  = '%s/OUT' %(stage)
        pfiles     = '%s/pfiles' %(stage)
        
        os.environ['INDIR']      = stage_in
        os.environ['OUTDIR']     = stage_out    
        os.environ['GRBNAME']    = fullName
        os.environ['PFILES']     = pfiles
        os.environ['BASEDIR']    = stage
        os.environ['LLEPIPELINE']= '%s/LLE' % stage
        #if(LOGFILE==''):   log        = '%s/%s_%s.log' % (logsDir,fullName,extension)
        if(LOGFILE==''):   log        = '%s_%s_%s.log' % (stage,fullName,extension)
        else:              log        = LOGFILE
        #if not TEST: os.system('rm -rf %s' % log)        
        # cp -r $BASEDIR/gtgrb_data/Bkg_Estimator/ stage_in/.    
        # os.environ['PYTHONPATH']
        # os.environ['ROOTISBATCH']
        cmd0=     "echo GTGRB_DIR=$GTGRB_DIR; "
        cmd0=cmd0+"echo PFILES=$PFILES; "
        cmd0=cmd0+"echo BASEDIR=$BASEDIR; "
        cmd0=cmd0+"echo INST_DIR=$INST_DIR; "
        cmd0=cmd0+"mkdir -pv $BASEDIR/gtgrb_data; mkdir -pv $BASEDIR/GTGRB; mkdir -pv $PFILES; mkdir -pv $LLEPIPELINE/src/macros; mkdir -pv $INDIR/GBM; mkdir -pv $OUTDIR/EXTRAFILES; " % locals()
        cmd0=cmd0+"cp -r %(old_base)s/gtgrb_data/Bkg_Estimator $BASEDIR/gtgrb_data; ls -al $BASEDIR; ls -al $BASEDIR/gtgrb_data; ls -al $BASEDIR/gtgrb_data/Bkg_Estimator; " % locals()
        cmd0=cmd0+"cp -r %(old_base)s/gtgrb_data/GBMtoolsDumps $BASEDIR/gtgrb_data; ls -al $BASEDIR; ls -al $BASEDIR/gtgrb_data; ls -al $BASEDIR/gtgrb_data/GBMtoolsDumps; " % locals()
        cmd0=cmd0+"cp -r $GTGRB_DIR/syspfiles/* $PFILES/.; cp ${INST_DIR}/syspfiles/* $PFILES/.; cp ${HEADAS}/syspfiles/* $PFILES/.; "
        cmd0=cmd0+"cp -r ${INST_DIR}/data/caldb %(stage_in)s/.; " % locals() # copies the system caldb
        cmd0=cmd0+"cp -r /afs/slac/g/glast/groups/canda/irfs/p8_merit/P8R3_V2/CALDB/* %(stage_in)s/caldb/.; " % locals() # copies the new p8r3
        cmd0=cmd0+"export CALDB=%(stage_in)s/caldb; " % locals() # <-- set the environment to avoid afs excessive load

        # COPY FT1 and FT2 files:
        if 'FT1' in parsed_options.keys():
            newFT1='$BASEDIR/FT1.fits'
            oldFT1=parsed_options['FT1']                
            parsed_options['FT1']=newFT1
            cmd0=cmd0+"cp -r %(oldFT1)s %(newFT1)s; " % locals()
            print oldFT1,'->',newFT1
            pass
        # COPY FT1 and FT2 files:
        if 'FT2' in parsed_options.keys():
            newFT2='$BASEDIR/FT2.fits'
            oldFT2=parsed_options['FT2']                
            parsed_options['FT2']=newFT2
            cmd0=cmd0+"cp -r %(oldFT2)s %(newFT2)s; " % locals()
            print oldFT2,'->',newFT2
            pass
        # Copy the diffuse model:
        DIFFUSEMODELS_PATH=os.path.expandvars(os.path.expanduser(os.environ['DIFFUSEMODELS_PATH']))
        # ResponseFunction=os.environ['IRFS']
        #ResponseFunction=parsed_options['IRFS']
        #print 'ResponseFunction:',ResponseFunction
        
        Models2Copy=[]
        
        def CopyDiffuseModels(ResponseFunction):
            myIRF = IRFS.IRFS[ResponseFunction]            
            a=myIRF.isotropicTemplate.split(',')
            a.reverse()
            for x in a:
                ISODIFFUSE=DIFFUSEMODELS_PATH+'/'+ x.replace(' ','')
                if os.path.exists(ISODIFFUSE):
                    if ISODIFFUSE not in Models2Copy: 
                        Models2Copy.append(ISODIFFUSE)
                        pass
                    break
                pass
            a=myIRF.galacticTemplate.split(',')
            a.reverse()
            for x in a:
                GALDIFFUSE=DIFFUSEMODELS_PATH+'/'+ x.replace(' ','')
                if os.path.exists(GALDIFFUSE):
                    if GALDIFFUSE not in Models2Copy: 
                        Models2Copy.append(GALDIFFUSE)
                        pass
                    break
                pass
            pass
        for irfs in IRFS.IRFS.keys(): CopyDiffuseModels(irfs)
        for myModel in Models2Copy:
            cmd0=cmd0+"cp -r %(myModel)s $OUTDIR/EXTRAFILES/.; " % locals()
            print ' ==> Model to copy: %s' % myModel
            pass
        #print cmd0
        #exit()
        
        os.environ['DIFFUSEMODELS_PATH']='%s/EXTRAFILES' % os.environ['OUTDIR']
        # COPY THE FERMI SOURCE CATALOG:
        FERMISOURCECATALOG = os.environ['FERMISOURCECATALOG']
        cmd0=cmd0+" cp %s  $OUTDIR/EXTRAFILES/.; " % FERMISOURCECATALOG
        os.environ['FERMISOURCECATALOG']='%s/EXTRAFILES/%s' % (os.environ['OUTDIR'],FERMISOURCECATALOG.split('/')[-1])

        # cmd0=cmd0+"cp %(old_base)s/GTGRB/*.xcm $BASEDIR/GTGRB/.; " % locals() # THIS NEEDS TO BE CHECKED
        cmd0=cmd0+"cp $LLE_DIR/src/macros/*.C $LLEPIPELINE/src/macros/.; " 
        if os.path.exists('%(inDir)s/GBM/%(fullName)s' % locals()): cmd0=cmd0+"cp -r %(inDir)s/GBM/%(fullName)s %(stage_in)s/GBM/.; " % locals()            
        cmd0=cmd0+"cd %(stage)s; " % locals()
        # #################################################
        # EXECUTE THE JOB:
        # #################################################
        
        opts='-nox -go -exe %(INFILE)s' % locals()
        for k in parsed_options.keys():
            if 'like_model' in k: opts+=' %s=\\"%s\\"' %(k,parsed_options[k])
            else: opts+=' %s=%s' %(k,parsed_options[k])
            pass
        
        # cmd0=cmd0+"%(old_base)s/app/gtgrb.py %(opts)s ; " % locals()
        # THIS IS THE RIGHT ONE:
        cmd0=cmd0+"gtgrb.py %(opts)s ; " % locals()
        # REMOVING THE UNNECESSARY FILES
        if CLEANUP:
            cmd0=cmd0+"rm -rf %(stage_out)s/%(fullName)s/*expmap*.fits; " % locals()
            cmd0=cmd0+"rm -rf %(stage_out)s/%(fullName)s/*ltcube*.fits; " % locals()
            cmd0=cmd0+"rm -rf %(stage_out)s/%(fullName)s/*MKT.fits; " % locals()
            cmd0=cmd0+"rm -rf %(stage_out)s/%(fullName)s/*select.fits; " % locals()
            cmd0=cmd0+"rm -rf %(stage_out)s/%(fullName)s/lle_events*; " % locals()
            cmd0=cmd0+"rm -rf %(stage_out)s/%(fullName)s/*LLEdetdur.root; " % locals()
            #cmd0=cmd0+"rm -rf %(stage_out)s/%(fullName)s/Bkg_Estimates/*/*.fits; " % locals()
            #cmd0=cmd0+"rm -rf %(stage_out)s/%(fullName)s/Bkg_Estimates/*/*.root; " % locals()
            cmd0=cmd0+"rm -rf %(stage_out)s/%(fullName)s/Bkg_Estimates; " % locals()
            cmd0=cmd0+"rm -rf %(stage_out)s/%(fullName)s/tmp; " % locals()
            cmd0=cmd0+"rm -rf %(stage_out)s/%(fullName)s/*/*expmap*.fits; " % locals()
            cmd0=cmd0+"rm -rf %(stage_out)s/%(fullName)s/*/*ltcube*.fits; " % locals()
            cmd0=cmd0+"rm -rf %(stage_out)s/%(fullName)s/*/MKT.fits; " % locals()
            pass
        else: # I WANT TO KEEP THE FT1 and FT2 files
            cmd0=cmd0+"cp -r %(stage_in)s/LAT/*.fits %(fullOutDir)s/.; " % locals()
            pass
        cmd0=cmd0+"rm -rf %(stage_out)s/EXTRAFILES; " % locals()
        # COPY LLE FILES
        if UCLEANUP: # this saves ONLY the results.txt file
            # COPY OUTPUT
            cmd0=cmd0+"cp  %(stage_out)s/%(fullName)s/results_%(fullName)s.txt %(fullOutDir)s/.; " % locals()            
            cmd0=cmd0+"cp  %(stage_out)s/%(fullName)s/jobTag.txt %(fullOutDir)s/.; " % locals()            
        else:
            # COPY THE LLE FILES:
            if os.path.exists("%(stage_in)s/LAT/%(fullName)s_LLE; " % locals()): 
                cmd0=cmd0+"cp -r %(stage_in)s/LAT/%(fullName)s_LLE %(inDir)s/LAT/.; " % locals()            
                pass
            # COPY OUTPUT
            cmd0=cmd0+"cp -r %(stage_out)s/%(fullName)s %(outDir)s/.; " % locals()
            pass        
        # #################################################
        # COPY THE LOGS
        cmd0=cmd0+"cp %(log)s %(fullOutDir)s/.; " % locals()
        # #################################################
        # MAKE A SYMBOLIC LINK
        #cmd0=cmd0+"ln -s %(log)s %(fullOutDir)s/.; " % locals()
        # #################################################
        # REMOVE LOGS & SCRATCH
        cmd0=cmd0+"rm %(log)s " % locals()
        cmd0=cmd0+"rm -rf %(stage)s " % locals()
        # #################################################
        if getArch()==5: ARCH='rhel50'
        elif getArch()==6: ARCH='rhel60'
        
        #cmd_pipe = 'bsub -R "select[%s] rusage[mem=3000]" -P gtgrb -J %s -o %s -q %s "%s"' %(ARCH,jobName,log,QUEUE,cmd0)
        
        cmd_pipe = 'bsub -R %s -R "scratch > 100" -P gtgrb -J %s -o %s -W %s "%s"' %(ARCH,jobName,log,wtime[QUEUE],cmd0)
        #cmd_pipe = 'bsub -R "dole || kiso || bullet || fell || hequ" -P gtgrb -J %s -o %s -W %s "%s"' %(jobName,log,wtime[QUEUE],cmd0)
        #cmd_pipe = 'bsub -m "fell0190 bullet0100 hequ0160 hequ0161 hequ0167" -P gtgrb -J %s -o %s -q %s "%s"' %(jobName,log,QUEUE,cmd0)
        print '**************************  SUBMITTING RUN %s ************************** ' % (jobName)
        print cmd_pipe
        if not TEST: os.system(cmd_pipe)
        pass
    else:
        print '**************************  EXECUTING RUN %s ************************** ' % (jobName)
        cmd_nopipe = "gtgrb.py %(opts)s ; " % locals()
        print cmd_nopipe
        if not TEST: os.system(cmd_nopipe)
        pass
    print '----------------------------------------------------------------------------------------------------'
    return
    

if __name__ == '__main__':
    PIPELINE     = 0
    INFILE       = 'computeAll2'
    QUEUE        = 'None'
    ONLYROLLBACK = False
    LOGFILE      = ''
    gtgrb_option = ''
    
    if len(sys.argv)==1:
        print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
        print ' WRONG ARGUMENTS, COMMAND SHOULD BE ON THE FORM:'
        print './pipeline/submitJob.py -exe app/..py -q queue '
        print 'with (in any order): '
        print '       -exe    <filepath>  : execute the <filepath> program. Look into app/compute* for some examples '
        print '       -q      Q : submit to the queue Q (short|medium|long|xlong)'
        print '       -l logfile: Use a specific log file, instead of the default one'
        print '       -r        : Execute only the job to rollback.'
        print ' \t \n'
        print 'To see the list type: gtgrb.py -l (you can add a filter, like \'GRB08\')' 
        print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'        
        sys.exit()
        pass
    
    for i,a in enumerate(sys.argv):        
        if '-p' in a:
            QUEUE='xlong'
            pass
        if '-exe' in a:            
            INFILE = sys.argv[i+1] 
            pass
        if '-q' in a:
            QUEUE=sys.argv[i+1]
            pass
        if '-l' in a:
            LOGFILE=sys.argv[i+1]
            pass
        if '-r' in a:
            ONLYROLLBACK = True
            pass
        if '=' in a:
            gtgrb_option=gtgrb_option+a+' '
            pass
        pass
    gtgrb_option = gtgrb_option.strip()
    print gtgrb_option
    submitJob(INFILE       = INFILE,
              QUEUE        = QUEUE,
              LOGFILE      = LOGFILE,
              ONLYROLLBACK = ONLYROLLBACK,
              gtgrb_option = gtgrb_option)
    print 'Done!'
    pass

    
