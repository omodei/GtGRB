#!/usr/bin/env python
import os,sys,glob
import makeLLE

import utils
import astropy.io.fits as pyfits
_interactive=0
ORBIT_PERIOD = 5733.0672
LOCATION_TCATFILE='GBM_TriggerCatalog/heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/202*/bn*/current/glg_tcat_all_*.fit'


class GRB:
    def __init__(self,fileName):
        self.fileName=fileName
        self.version = int(self.fileName.split('_v')[-1].replace('.fit',''))
        self.CLASS,self.OBJECT,self.RA_OBJ,self.DEC_OBJ,self.ERR_RAD,self.TRIGTIME,self.LOC_SRC=makeLLE.ParseTrigCatFile(fileName)
        self.TriggerName = fileName.split('glg_tcat_all_')[1].split('_')[0].replace('*.fit','').replace('bn','')
        self.simple_filename=fileName[fileName.rfind('/')+1:]
        #print fileName
        pass
    def getTupla(self):
        return self.TriggerName,self.CLASS,self.OBJECT,self.RA_OBJ,self.DEC_OBJ,self.ERR_RAD,self.TRIGTIME,self.LOC_SRC
    def getDate(self):
        dt=utils.computeDate(self.TRIGTIME)
        return dt.isoformat()
    pass

class GBMTRIGCAT:
    def __init__(self,path=LOCATION_TCATFILE):
        print 'Looking for tcat file here:',path
        fileList = sorted(glob.glob(path))
        Ntotal=len(fileList)
        print '... found total of %d files...' %(Ntotal)
        self.GRBDictionary={}
        for fileName in fileList:
            g=GRB(fileName)
            #print g.TriggerName,g.CLASS,g.fileName,g.version
            if g.TriggerName in self.GRBDictionary.keys():
                if g.version > self.GRBDictionary[g.TriggerName].version:# or (g.ERR_RAD < self.GRBDictionary[gA.OBJECT].ERR_RAD):  
                    self.GRBDictionary[g.TriggerName]=g
                    pass
                pass
            else:
                self.GRBDictionary[g.TriggerName]=g
                pass
            #print 'Using...:',g.fileName
            pass
        self.keys=self.GRBDictionary.keys()
        pass

    def Get(self, grb=None): 
        if grb==None: return self.GRBDictionary    
        myGRBDictionary={}
        for k in self.keys: 
            if grb in k: myGRBDictionary[k]=self.GRBDictionary[k]
        return myGRBDictionary
    
def help():
    print 'Code written by nicola.omodei@slac.stanford.edu'
    print 'options:'
    print '   -drm build the DRM (provided a MC has been run) '
    print '   -pha  build the PHA and FT1 LLE file '
    print '   -mc  create the configuration file for the Monte Carlo generation  '
    print '   -gtgrb  analyize using GRBAnalysis-scons'
    print '   -f <EXPRESSION> filter the GRBtrigctalog'
    print '   -real execute per real the job  '
    pass


def readResults(results_file_name):
    lines=file(results_file_name).readlines()
    myDictionary={}
    for l in lines:
        if '#' in l: continue
        p,v=l.split('=')
        p=p.strip()
        v=v.strip()
        try: v=float(v)
        except: pass
        myDictionary[p]=v
        pass
    return myDictionary


if __name__=='__main__':
    _filter = ''
    _class  ='GRB'
    mode=[]
    forReal=0
    tree=None
    OUTDIRNAME='AUTO'
    rollback = 0
    RA_UPD, DEC_UPD = None,None
    IRFS     = 'P7TRANSIENT_V6'
    GENERATELLEFILES=False
    EMIN     = 100
    EMAX     = 100000
    NMAX     = 100
    T05      = 0.0 
    T95      = 100.0
    GRBMODEL = 'GRB'
    ZMAX     = 105
    ORBIT    = 0
    ROI      = 12
    for i,a in enumerate(sys.argv):
        if '-orbit' in a:    ORBIT=float(sys.argv[i+1])        
        elif '-f' in a:        _filter = sys.argv[i+1]        
        elif '-class' in a:    _class  = sys.argv[i+1]        
        elif '-o' in a:        OUTDIRNAME= sys.argv[i+1]        
        elif '-catalog' in a:  mode.append('catalog')
        elif '-real' in a:     mode.append('forReal')
        elif '-h' in a:        help(); exit()
        elif '-pipe' in a:     mode.append('pipe')
        elif '-irfs' in a:     IRFS=sys.argv[i+1]
        elif '-emin' in a:     EMIN=float(sys.argv[i+1])
        elif '-emax' in a:     EMAX=float(sys.argv[i+1])
        elif '-zmax' in a:     ZMAX=float(sys.argv[i+1])
        elif '-roi'  in a:     ROI=float(sys.argv[i+1])
        elif '-ra' in a:       RA_UPD  = float(sys.argv[i+1])
        elif '-dec' in a:      DEC_UPD = float(sys.argv[i+1])
        elif '-rollback' in a: rollback=1
        elif '-nmax' in a:     NMAX=int(sys.argv[i+1])
        elif '-lle' in a:      GENERATELLEFILES=True
        elif '-ebl' in a:      GRBMODEL='GRBEBL'      
        elif '-t05' in a:      T05=float(sys.argv[i+1])
        elif '-t95' in a:      T95=float(sys.argv[i+1])
        pass
    T90=T95-T05
    if 'forReal' in mode: forReal=1
    if 'P7' in IRFS:
        if 'TRANSIENT' in IRFS: os.environ['JOBPRE']='t'
        else: os.environ['JOBPRE']='s'
    else:
        if 'TRANSIENT' in IRFS: os.environ['JOBPRE']='T'
        else: os.environ['JOBPRE']='S'
        pass
    os.environ['IRFS']  =IRFS
    os.environ['JOBPRE']=IRFS
    BASEDIR = os.environ['BASEDIR']    
    OUTDIR = '%s/DATA/%s' % (BASEDIR,OUTDIRNAME)
    print 'RESULTS WILL BE STORED IN %s' % OUTDIR
    os.environ['OUTDIR'] = OUTDIR
    os.system('mkdir -p $OUTDIR')
    
    Total=0
    Filtered=0
    InTheta=0
    submitted=0
    SE=0
    DE=0
    MC=0
    NSE=0
    NDE=0
    NMC=0

    THETA_MIN=makeLLE.GetThetaMin()    
    #GBM_TC=GBMTRIGCAT(LOCATION_TCATFILE)
    #GRBDictionary=GBM_TC.Get()
    
    import gtgrb

    my_grbs     = gtgrb.GRBNames()                                                                                                                                                                                                     
    my_triggers = gtgrb.TriggerNames()                                                                                                                                                                                                 

    for objectName in sorted(my_triggers.keys()):
        if objectName in my_grbs.keys(): myObject = my_grbs[objectName]
        else:                            myObject = my_triggers[objectName]
        Total+=1
        # STEP 1: PARSE THE FILE
        #myObject=GRBDictionary[objectName]
        #TriggerName,CLASS,OBJECT,RA_OBJ,DEC_OBJ,ERR_RAD,TRIGTIME,LOC_SRC = myObject.getTupla()
        TriggerName = objectName  # bnYYMMGGFFF
        RA_OBJ      = myObject[1] 
        DEC_OBJ     = myObject[2] 
        ERR_RAD     = myObject[3] 
        TRIGTIME    = myObject[0] 
        LOC_SRC     = 'XXX'
        CLASS       = myObject[6]
        OBJECT      = '%s%s' % (CLASS,objectName.replace('bn',''))

        TRIGTIME+=(ORBIT*ORBIT_PERIOD)
        #print '------------------------- %s %s %.2f,%.2f,%.2f,%s' %(CLASS,OBJECT,RA_OBJ,DEC_OBJ,ERR_RAD,LOC_SRC)
        if _filter in OBJECT and _class in CLASS:
            if RA_UPD is not None:
                RA_OBJ  = RA_UPD
                #print '--- RA updated: %.3f' %(RA_OBJ)
                pass
            if DEC_UPD is not None:
                DEC_OBJ = DEC_UPD
                #print '--- DEC updated: %.3f' %(DEC_OBJ)
                pass
            
            Filtered+=1
            object_number=OBJECT[-9:]

            local_output_directory='%(OUTDIR)s/%(object_number)s' % locals()
            local_output_results='%(OUTDIR)s/%(object_number)s/results_%(object_number)s.txt' % locals()
            local_output_flag='%(OUTDIR)s/%(object_number)s/jobTag.txt' % locals()
            local_theta='%s/theta.txt' % local_output_directory
            
            jt_exists    = os.path.exists(local_output_flag)
            dir_exists   = os.path.exists(local_output_directory)
            res_exists   = os.path.exists(local_output_results)
            theta_exists = os.path.exists(local_theta)
            job_success  = res_exists and not jt_exists            
            remove_dir   = False
            if res_exists and job_success:
                d = readResults(local_output_results)
                if (ERR_RAD+0.5) < d['ERR']:
                    print '%s,%s==>%s,%s (%s => %s)'%(d['RA'],d['DEC'],RA_OBJ,DEC_OBJ,d['ERR'],ERR_RAD)
                    remove_dir=True
                    pass
                if RA_UPD is not None:  remove_dir=True
                if DEC_UPD is not None: remove_dir=True
                pass

            print '%s %s %s %.3f, %.2f, %.2f, %.2f [%s]' %(object_number,CLASS,OBJECT,TRIGTIME, RA_OBJ,DEC_OBJ,ERR_RAD,LOC_SRC)
            #print 'jt_exists...:',jt_exists
            #print 'dir_exists..:',dir_exists
            #print 'res_exists..:',res_exists
            #print 'theta_exists:',theta_exists
            #print 'job_success.:',job_success
            #print 'remove_dir..:',remove_dir
            print 'Submitted....: %d/%d' %(submitted,NMAX)
            run_job=True
            if job_success: run_job=False

            if GENERATELLEFILES:
                print '''# Configuration file for %(OBJECT)s
NAME                      = '%(OBJECT)s_GR200811'
DURATION                  = 50.00
MET                       = %(TRIGTIME).3f
RA                        = %(RA_OBJ).3f
DEC                       = %(DEC_OBJ).3f
''' %locals()
                continue
            ##################################################
            if 'P7' in IRFS and 'TRANSIENT' in IRFS:         bkg="%s+BKGE_CR_EGAL+GAL0+2FGL"  % GRBMODEL  
            elif 'P8' in IRFS and 'TRANSIENT100E' in IRFS:   bkg="%s+BKGE_CR_EGAL+GAL0+2FGL"  % GRBMODEL     
            else: bkg="%s+TEM+GAL0+2FGL" % GRBMODEL
            if not 'GRB' in CLASS: T90 = 3600
            ##################################################
            try:
                from GRBREDSHIFT import REDSHIFT as GRBz
                if object_number in GRBz.keys(): REDSHIFT = GRBz[object_number]            
            except:
                REDSHIFT = 0.0
                pass
            MyOptions={ "IGNORE_THETA":1,
                        "CHANGE_ZMAX":0,
                        "TSTART":T05-20, 
                        "TSTOP":T95+300,
                        "BEFORE":600,
                        "AFTER":3600,
                        "EMIN":EMIN,
                        "EMAX":EMAX,
                        "TSMIN":20,
                        "TSMIN_EXT":10,
                        "UPDATE_POS_TSMAP":1,
                        "ULINDEX":-2.00,
                        "ZMAX":ZMAX,
                        "ROI":ROI,
                        "DT":1.0,
                        "IRFS":IRFS,
                        "like_model":bkg,
                        "like_timeBins":'LOG',
                        "NLIKEBINS":48,
                        "EXTENDED_TSTART":T05+0.01,
                        "EXTENDED_TSTOP":T05+50000,
                        "MAKE_LIKE":1,
                        "MAKE_LLE":1,
                        "MAKE_TSMAP":0,
                        "LLEDT":"0.1,10",
                        "N":10,
                        "LLEDS":0,
                        "GRBTRIGGERDATE":TRIGTIME,
                        "GRBT05":T05 ,
                        "GRBT90":T90,
                        "RA":RA_OBJ,
                        "DEC":DEC_OBJ,
                        "ERR":ERR_RAD,
                        "REDSHIFT":REDSHIFT
                        }
            if forReal and run_job:
                FT2   = makeLLE.GetFT2(TRIGTIME)
                if FT2 is None:  
                    print '>>>> FT2 file not found!'
                    continue            
                if remove_dir: os.system('rm -rf %s' % local_output_directory)                
                THETA = makeLLE.GetTheta(FT2,TRIGTIME,RA_OBJ,DEC_OBJ)            
                if THETA > THETA_MIN:  InTheta+=1
                # STEP 4: Process the file with gtgrb
                pass
            processed=0
            if submitted>NMAX: break
            if run_job: processed = makeLLE.ComputeDetection(OBJECT, mode, MyOptions)                                    
            if forReal: submitted+=processed
            pass
        pass
    print '#################################################################'
    print '#                   FINAL REPORT                                #'        
    print '# TOTAL: %d; FILTERES: %d; THETA<%.1f: %d  Submitted: %d #' %(Total,Filtered,THETA_MIN, InTheta,submitted)
    print '#################################################################'
    
