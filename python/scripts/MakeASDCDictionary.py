#!/usr/bin/env python
import astropy.io.fits as pyfits
import pprint
pp = pprint.PrettyPrinter(indent=4)

import GTGRB.genutils

##################################################
GBM_trigcat_file  = pyfits.open('GBM_trigcat.fits')
GBM_trigcat  = GBM_trigcat_file['FERMIGTRIG'].data

NAME = GBM_trigcat.field('NAME')
RA   = GBM_trigcat.field('RA')
DEC  = GBM_trigcat.field('DEC')
ERR  = GBM_trigcat.field('ERROR_RADIUS')


N_GBM_trigcat = len(NAME)

GBM_trigcat_Dictionary={}
for i in range(N_GBM_trigcat):
    name = NAME[i].strip().replace('GRB','')
    ra   = RA[i]
    dec  = DEC[i]
    err  = ERR[i]
    GBM_trigcat_Dictionary[name]={'RA':ra, 'DEC':dec, 'ERR':err}
    pass
#print GBM_trigcat_Dictionary
##################################################
ASDC_file    = pyfits.open('fermi-gbm-grb.fits')
ASDCs_table  = ASDC_file[1].data

GBMtrigger = ASDCs_table.field('GBMtrigger')
GBMMET     = ASDCs_table.field('MET')
best_RA    = ASDCs_table.field('ra_best')
best_dec   = ASDCs_table.field('dec_best')
error      = ASDCs_table.field('error')
GBM_T90    = ASDCs_table.field('GBM_T90')
redshift   = ASDCs_table.field('Z')

N_asdc_bursts = len(GBMtrigger)

ASDCBursts={}
for i in range(N_asdc_bursts):
    name='ASDC%09d' % int(GBMtrigger[i])
    met = GBMMET[i]
    ra  = best_RA[i]
    dec = best_dec[i]
    err = error[i]
    t90 = GBM_T90[i]    
    if t90<=0: t90=100
    z   = max(0,float(redshift[i]))
    ASDCBursts[name]={'GRBTRIGGERDATE':met,'RA':ra, 'DEC':dec, 'ERR':err, 'GRBT05':0,'GRBT90':t90,'REDSHIFT':z}
    pass
##################################################

duration_file    = file('GBMCatalog.txt','r')

GBMCatalogBursts = {}
lines=duration_file.readlines()
for l in lines:
    if '#' in l: continue
    vars    = l.split()
    
    burst    = vars[0].strip().replace('bn','')
    t90	     = float(vars[1].strip())
    t90_err  = float(vars[2].strip())
    t90start = float(vars[3].strip())
    t50      = float(vars[4].strip())
    t50_err  = float(vars[5].strip())
    t50start = float(vars[6].strip())
    
    GBMCatalogBursts[burst]={}
    GBMCatalogBursts[burst]['t90']      = t90
    GBMCatalogBursts[burst]['t90_err']  = t90_err
    GBMCatalogBursts[burst]['t90start'] = t90start
    GBMCatalogBursts[burst]['t50']      = t50
    GBMCatalogBursts[burst]['t50_err']  = t50_err
    GBMCatalogBursts[burst]['t50start'] = t50start
    pass

def GetFullName(met): return genutils.met2date(met,'GRBNAME')

duration_updated=0
position_updated=0

for name in sorted(ASDCBursts.keys()):
    duration_cat_name=name.replace('ASDC','')
    position_cat_name=name.replace('ASDC','')
    #print duration_cat_name, position_cat_name
    if duration_cat_name in GBMCatalogBursts.keys():
        ASDCBursts[name]['GRBT05']=GBMCatalogBursts[duration_cat_name]['t90start']
        ASDCBursts[name]['GRBT90']=GBMCatalogBursts[duration_cat_name]['t90']
        duration_updated+=1        
        pass
    
    if position_cat_name in GBM_trigcat_Dictionary.keys():
        
        oldRA  = ASDCBursts[name]['RA']
        oldDec = ASDCBursts[name]['DEC']
        oldERR = ASDCBursts[name]['ERR']
        
        newRA  = GBM_trigcat_Dictionary[position_cat_name]['RA']
        newDec = GBM_trigcat_Dictionary[position_cat_name]['DEC']
        newERR = max(1e-4,GBM_trigcat_Dictionary[position_cat_name]['ERR'])
        
        Separation = GTGRB.genutils.angsep(oldRA,oldDec,newRA,newDec)
        
        if newERR > ASDCBursts[name]['ERR']+1 or Separation>0.01: print '$$$ %s - Ra,Dec,Err=(%.1f,%.1f,%.1e), newRa,newDec,newERR=(%.1f,%.1f,%.1e) - %.2f' % (name,
                                                                                                                                                        oldRA,
                                                                                                                                                        oldDec,
                                                                                                                                                        oldERR,
                                                                                                                                                        newRA,
                                                                                                                                                        newDec,
                                                                                                                                                        newERR,
                                                                                                                                                        Separation)        
        ASDCBursts[name]['RA']  = newRA
        ASDCBursts[name]['DEC'] = newDec
        ASDCBursts[name]['ERR'] = newERR
        position_updated+=1        
        pass
    pass

print 'Number of bursts in the ASDC table....: %d' % N_asdc_bursts
print 'Number of bursts in the LOCATION Catalog...: %d' % len(GBM_trigcat_Dictionary.keys())
print 'Number of bursts in the DURATION Catalog...: %d' % len(GBMCatalogBursts.keys())

print 'Number of LOCATIONS updated..............: %d' % position_updated
print 'Number of DURATIONS updated..............: %d' % duration_updated
print '##################################################'
print 'ASDCs= ',pp.pprint(ASDCBursts)
print '##################################################'

        
