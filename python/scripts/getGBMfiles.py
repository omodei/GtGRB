#!/usr/bin/env python
import os,sys,glob,pyfits
from GTGRB.genutils import runShellCommand

ftp_base_path='ftp://legacy.gsfc.nasa.gov/fermi/data/gbm/bursts'
ftp_base_path='ftp://legacy.gsfc.nasa.gov/fermi/data/gbm/triggers'
gbmdir = os.path.join(os.environ['INDIR'],'GBM')

def getGBMfiles(GRBNAME,dataType=['tte','rsp','tcat']):

    yr=2000+int(GRBNAME[:2])
    DirectoryName='%s/%s/bn%s/current'%(ftp_base_path,yr,GRBNAME)

    outputDir='%s/%s' %(gbmdir,GRBNAME)
    #runShellCommand('mkdir %s'%outputDir)
    for type in dataType:
        cmd='wget -nv -c %s/*%s* -N -P %s'%(DirectoryName,type,outputDir)
        print cmd
        runShellCommand(cmd)
        pass
    pass

def getTriggerDetectors(GRBNAME):
    basename='%s/%s/*tcat*' %(gbmdir,GRBNAME)
    try:
        tcat   = glob.glob(basename)[-1]
    except:
        return None
    
    detlist=['n0','n1','n2','n3','n4','n5','n6','n7','n8','n9','na','nb']
    newdetlist=[]
    newdet =''
    if os.path.exists(tcat):
        print 'tcat filename: %s' % tcat            
        fitsfile= pyfits.open(tcat)
        mask    = fitsfile[0].header['DET_MASK']
        print mask
        pos=0
        while pos<12:
            if mask[pos]=='1':
                newdetlist.append(detlist[pos])
                pass
            pos=pos+1
            pass
        pass
    else:
        newdetlist=detlist
        pass
    newdetlist.append('b0')
    newdetlist.append('b1')
    for de in newdetlist:
        newdet = newdet+'%s,'% de
        pass
    newdet=newdet[:-1]
    return newdet



if __name__=='__main__':

    try:
        defa=grb_name
    except:
        defa=''
        pass
    
    name=raw_input(' NAME OF THE GRB (YYMMDDFFF)= %s ' %defa)
    if len(name)==9:
        GRBNAME=name        
    else:
        GRBNAME=defa
        pass

    if(len(GRBNAME)==9):
        getGBMfiles(GRBNAME)
    else:
        print 'incorrect file name'
        
