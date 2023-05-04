from Detector import Detector
from GRB import *

import glob
import astropy.io.fits as pyfits
import gtrmfit
from genutils import runShellCommand

class GBM(Detector):
    def __init__(self,detector_name,grb):
        Detector.__init__(self,detector_name=detector_name,grb=grb)
        Detector.IN_Directory=grb.gbmdir
        Detector.OUT_Directory=grb.out_dir
        self.GRB = grb
        
        ##OVERRIDS DEFAULT NAMES:
        # OVERRIDES FILE NAMES
        #pre=['/GLG_TTE_','BN','_V02.FIT']
        pre=['/glg_tte_','_bn','_v*.fit']
        import glob
        
        def getFile(path):
            #print path            
            try:
                f=glob.glob(path)[-1]
            except:
                f=None
                pass
            return f
                
        self.FilenameFT1 = getFile(Detector.IN_Directory+pre[0]+detector_name+pre[1]+self.grb_name+pre[2])
        self.evt_file    = Detector.OUT_Directory+'/'+self.grb_name+'_'+detector_name+'_select.fits'
        self.tte_File    = getFile(Detector.IN_Directory+'/glg_tte_'+detector_name+pre[1]+self.grb_name+'_v*.fit')
        self.rsp_File    = getFile(Detector.IN_Directory+'/glg_cspec_'+detector_name+pre[1]+self.grb_name+'_v*.rsp')
        self.rsp2_File   = getFile(Detector.IN_Directory+'/glg_cspec_'+detector_name+pre[1]+self.grb_name+'_v*.rsp2')
        self.cspec_File  = getFile(Detector.IN_Directory+'/glg_cspec_'+detector_name+pre[1]+self.grb_name+'_v*.pha')
        self.back_File   = Detector.IN_Directory+pre[0]+detector_name+pre[1]+self.grb_name+'_back.fits'
        
        self.FilenameFT2='none'
        
        ##self.selected_evt_File=Detector.OUT_Directory+'/'+self.grb_name+'_'+detector_name+'_select.fits'
        #print '.... GBM files .... :'
        #print self.evt_file
        #print self.tte_File
        #print self.rsp_File
        #print self.rsp2_File
        #print self.cspec_File                
        #print self.back_File
        pass
        
    def SetROIFromGBM(self):
        print self.evt_file
        fitsfile = pyfits.open(self.evt_file)
        
        self.GRB.ra = fitsfile[0].header['RA_OBJ']
        self.GRB.dec = fitsfile[0].header['DEC_OBJ']
        
        self.GRB.TStart   = fitsfile[0].header['TSTART']
        self.GRB.TStop    = fitsfile[0].header['TSTOP']
        self.GRB.Ttrigger = fitsfile[0].header['TRIGTIME']
        pass
    def make_pha1(self,**kwargs):
        #print '--------------------------------------------------'
        #print 'Make PHA1 FILE: ',self.detector_name
        #print '--------------------------------------------------'
        from GtApp import GtApp
        gtbin = GtApp('gtbin')
        gtbin['algorithm']='PHA1'
        gtbin['evfile']  = self.evt_file
        gtbin['scfile']  = self.FilenameFT2
        gtbin['outfile'] = self.sp_outFile        
        gtbin.run()

    def make_rsp(self):
        print 'Generating response matrix... ',self.detector_name
        if(not os.path.exists(self.rsp_File)):
            print self.rsp_File,' file not found!'
            
            
    def make_bkg(self):
        print 'Generating background... ',self.detector_name
        if(not os.path.exists(self.back_File)):
            print self.back_File,' file not found!'
            pass
        pass
    
    def make_time_select(self,tstart,tstop):
        #print '--------------------------------------------------'
        #print ' Selecting events on detector ' + self.detector_name + '...'
        #print ' TSTART = %.2f TSTOP = %2f (seconds since the trigger) ' % (tstart-self.GRB.Ttrigger,tstop-self.GRB.Ttrigger)
        #print '--------------------------------------------------'
        #print ' Creating file ' + self.evt_file
        command = 'fselect \"' + self.FilenameFT1 + '[2]\" ' + self.evt_file + ' \"TIME > ' + str(tstart) + ' && TIME < ' + str(tstop) + '\" clobber=yes'        
        print command
        runShellCommand(command)
        pass
    
    def modify_cspec_rmfit(self):
        gtrmfit.cspecrmfit(self)
        pass
    
    def getClosest(self):
        return self.GRB.GBMdetectors

    
    def saveEvents2Root(self):
        time = self.GRB.Ttrigger
        #print 'Now making a root tree with the selected events...'
        fileName=self.evt_file
        #print '...opening', fileName
        hdulist = pyfits.open(fileName)
        #hdulist.info()
        tbdata = hdulist['EVENTS'].data

        Time=tbdata.field('time')
        Pha=tbdata.field('pha')
        n=len(Time)
        #print 'Find %d events...' % n
        import ROOT
        from array import array
        root_name=    fileName.replace('.fit','.root')
        if root_name[-1]=='s':
            root_name=root_name.replace('.roots','.root')
            pass
        rootf=ROOT.TFile(root_name,'RECREATE')

        tree=ROOT.TTree('Events','Events');
        #print 'imported root!'
        TIME  =  array('d',[0]) 
        PHA =  array('i',[0]) 
        
        tree.Branch('TIME',TIME,'TIME/D')
        tree.Branch('PHA',PHA,'PHA/I')
        for i in range(n):
            TIME[0]=Time[i]
            PHA[0] =Pha[i]
            if(i<10):
                #print TIME[0],TIME[0]-time,PHA[0]
                pass
            tree.Fill()
            pass
        tree.Write()
        rootf.Close()
        pass

    
    

