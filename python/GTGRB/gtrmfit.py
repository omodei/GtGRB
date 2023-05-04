#! /usr/bin/env python
'''
This file is needed to convert standard pha2 file into rmfit file format.
questions: nicola.omodei@gmail.com
Nicola Omodei, for the Fermi LAT Collaboration
'''

import glob
import astropy.io.fits as pyfits
import os

def pha2rmfit(filename, trigtime):
    # filename = lat.pha2_outFile
    hdus     = pyfits.open(filename)

    primary  = hdus[0]
    spectrum = hdus[1]
    ebounds  = hdus[2]
    gti      = hdus[3]

    primary_hdr  = primary.header
    spectrum_hdr = spectrum.header
    ebounds_hdr  = ebounds.header
    gti_hdr      = gti.header

    TSTART =  gti_hdr['TSTART']
    TSTOP  =  gti_hdr['TSTOP']
    if(trigtime==0):
        trigtime=TSTART
        pass
    primary_hdr.update('FILETYPE','PHAII')
    primary_hdr.update('TRIGTIME',trigtime)
    primary_hdr.update('INSTRUME','LAT')
    primary_hdr.update('DETNAM','LAT')
    spectrum_hdr.update('TSTART',trigtime,after='DATE-END')
    
    spectrum_hdr.update('TTYPE1','TIME')
    spectrum_hdr.update('TUNIT1','s')
    spectrum_hdr.update('TZERO1',trigtime,after='TFORM1')
    
    spectrum_hdr.update('TTYPE2','ENDTIME')
    spectrum_hdr.update('TUNIT2','s')
    spectrum_hdr.update('TZERO2',trigtime,after='TFORM2')
    
    spectrum_hdr.update('BACKFILE','none')
    spectrum_hdr.update('CORRFILE','none')
    spectrum_hdr.update('RESPFILE','none')
    spectrum_hdr.update('ANCRFILE','none')
    spectrum_hdr.update('POISSERR',True)
    spectrum_tbl = spectrum.data
    spectrum_col = spectrum.columns
    
    sp_time    =  spectrum_tbl.field('TIME')
    sp_endtime =  spectrum_tbl.field('ENDTIME')
    sp_spnum   =  spectrum_tbl.field(2) # ('SPEC_NUM')

    #sp_endtime = sp_time + sp_endtime
    
    for i in range(spectrum_hdr['NAXIS2']):
        spectrum_tbl.field('TIME')[i]=sp_time[i]-trigtime
        spectrum_tbl.field('ENDTIME')[i]=spectrum_tbl.field('TIME')[i]+sp_endtime[i]-trigtime
        pass
    newfilename=filename.replace('.pha','_v1.pha')
    oldfilename=filename.replace('.pha','_v0.pha')
    
    hdus.writeto(newfilename,clobber=True)
    os.system('mv '+filename+' '+oldfilename)
    os.system('mv '+newfilename+' '+filename)
    print ' PHA2 File name saved in : %s' % filename
    pass

def cspecrmfit(gbm):
    file=gbm.cspec_file
    hdus = pyfits.open(file)

    spectrum = hdus[2]

    spectrum_hdr = spectrum.header

    spectrum_hdr.update('TTYPE5','TIME')
    spectrum_hdr.update('TUNIT5','s')
    spectrum_hdr.update('TTYPE6','ENDTIME')
    spectrum_hdr.update('TUNIT6','s')

    spectrum_tbl = spectrum.data
    #sp_time    =  spectrum_tbl.field('TIME')
    #sp_endtime =  spectrum_tbl.field('ENDTIME')

    #newfilename=file.replace('.','_p2.')
    newfilename=gbm.OUT_Directory+'/GLG_CSPEC_'+gbm.detector_name+'_BN'+gbm.grb_name+'_V02_p2.FIT'
    print 'new file : %s' % newfilename
    hdus.writeto(newfilename,clobber=True)
    
    pyfits.update(newfilename,spectrum_tbl,spectrum_hdr,2)
    pass

if __name__=='__main__':
    import sys
    fileName    = sys.argv[1]
    trigtime    = float(sys.argv[2])
    pha2rmfit(fileName, trigtime)
    
