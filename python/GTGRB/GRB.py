import datetime
import os, glob
import astropy.io.fits as pyfits
import genutils,ROOT

from GTGRB.genutils import runShellCommand

## @brief Class containing GRB parameters
## 
class GRB:
## Constructor
## @param grb_name=None the name of the GRB
## @param gbm=None the instance of the GBM object
## @param lat=None the instance of the LAT object
#  The class instance.

    def __init__(self, grb_trigger, grb_name=None, gbm=None, lat=None, chatter=1):	
        import GBM
        self.Name     = 'UNDEFINED'
        self.Date     = ''
        self.Ttrigger = grb_trigger
        grb_date,fff=genutils.met2date(grb_trigger,'fff')
        self.Date    = grb_date
        if grb_name is None or grb_name == '':
            yy=grb_date.year
            mm=grb_date.month
            dd=grb_date.day            
            self.Name    ='%02i%02i%02i%03i' %(yy-2000,mm,dd,fff)
        else:
            self.Name= grb_name
            pass
        
        self.TStart   = 0
        self.TStop    = 0
        self.T05      = 0
        self.T90      = 0
        self.T95      = 0
	self.chatter  = chatter
        self.ra=999.
        self.dec=999.
        self.LocalizationError=1.0
        #        self.Ttrigger = -1.
        self.GBMdetectors=[]        
                
        #self.GBM = self.SetGBM(gbm)
        #self.LAT = self.SetLAT(lat)

        self.latdir  = os.path.join(os.environ['INDIR'],'LAT')
        self.gbmdir  = os.path.join(os.environ['INDIR'],'GBM/%s' % self.Name)
        self.out_dir = os.path.join(os.environ['OUTDIR'], self.Name)

        runShellCommand('mkdir -p %s' % self.latdir)
        runShellCommand('mkdir -p %s' % self.gbmdir)
        runShellCommand('mkdir -p %s' % self.out_dir)        
        self.xml_file_name=os.path.join(self.out_dir,self.Name+'.xml')
        if self.chatter>0: print 'OUTPUT DIRECTORY: %s' % self.out_dir
        pass
    
    '''
    def SetGRB(self, grb_name=None):
    if grb_name is None :
    return
    grb_name=grb_name.strip('GRB')
    if(len(grb_name)!=9):
    print ' GRB NAME ',grb_name,
    self.Name = grb_name
    return
    
    self.Name = grb_name
    fd=grb_name[0:2]+"-"+grb_name[2:4]+"-"+grb_name[4:6] 
    sod=float(grb_name[6:9])*86.4
    self.Ttrigger=genutils.date2met(fd,sod)
    print "Trigger according to GRB name : ",self.Ttrigger   
    
    '''
    def SetGBM(self, gbm=None) :
        #if gbm is None and self.Name=='UNDEFINED': return
        if gbm == 'query' :
            print 'Database query not implemented yet.'
            return
        self.gbmdir = os.path.join(os.environ['INDIR'],'GBM','GRB'+self.Name)
        if not os.path.exists(gbmdir):
            print 'GBM Directory not found ', gbmdir
            return
        print 'INPUT GBM DIRECTORY: %s' % gbmdir 
        self.gbmdir = gbmdir

    def SetLAT(self, lat=None) :
        latdir = os.path.join(os.environ['INDIR'],'LAT')
        self.latdir  = latdir
        pass
    
    ## @brief This Create a ROOT File saving histograms.
    ## The name of the file is be self.out_dir+'/'+self.Name+'.root'
    #
    def CreateROOTFile(self):
        #print 'Creating root file...'
        self.ROOTFileName = self.out_dir+'/'+self.Name+'.root'
        self.ROOTFile     = ROOT.TFile(self.ROOTFileName,'RECREATE')
        if self.chatter>0: print 'Open %s ' % self.ROOTFileName
        pass
    
    ## @brief Save an object into the ROOT file.
    ## 
    #
    def WriteToROOTFile(self,object):
        #print 'Creating root file...'
        self.ROOTFile.cd()
        object.Write()
        if self.chatter>0: print 'Object %s saved into %s ' % (object.GetName(),self.ROOTFileName)
        pass
    

    
    ## @brief This Close the created ROOT file.
    ## The name of the file is self.out_dir+'/'+self.Name+'.root'
    # The file is left open to add object during the processing. It must be closed at the end.
    def CloseROOTFile(self):
        print 'Closing root file...'
        self.ROOTFile.Close()
        pass
    
    def InitGRBModel(self):
        print 'Init GRB model...', self.ra,self.dec 
        xmlFile=open(self.xml_file_name,'w')
        xmlFile.write('''<?xml version="1.0" ?>
        <source_library title="source library">
        <source name="GRB" type="PointSource">
        <!-- point source units are cm^-2 s^-1 MeV^-1 -->
        <spectrum type="PowerLaw">
        <parameter free="1" max="100000.0" min="0.000001" name="Prefactor" scale="1e-06" value="1"/>
        <parameter free="1" max="-1.0" min="-5." name="Index" scale="1.0" value="-2.1"/>
        <parameter free="0" max="2000.0" min="30.0" name="Scale" scale="1.0" value="100.0"/>
        </spectrum>
        <spatialModel type="SkyDirFunction">
        ''')
        xmlFile.write('       <parameter free="0" max="360.0" min="-360.0" name="RA" scale="1.0" value="'+str(self.ra)+'"/>\n')
        xmlFile.write('       <parameter free="0" max="90.0" min="-90.0" name="DEC" scale="1.0" value="'+str(self.dec)+'"/>\n')
        xmlFile.write('       </spatialModel>\n')
        xmlFile.write('       </source>\n')
        xmlFile.write('</source_library>\n')
        return self.xml_file_name
    
    
    def MakeXMLFileLikelihood(self):
        filePath=self.xml_file_name
        import latutils
        latutils.CreateSource_XML(filePath)        
        latutils.Add_IsoPower_XML(filePath) #Add_DiffuseComponents_XML(filePath)
        latutils.write_xmlModel(xmlFileName='GRBmodel.xml',ra=self.ra,dec=self.dec,Integral=1e-5,Index=-2.0)
        latutils.Close_XML(filePath)
        pass
    

if __name__ == "__main__":
    print 'done'
