#!/usr/bin/env python
import scripts.GRBs as grbs
from GTGRB.genutils import runShellScript
import os,sys
import ROOT
from array import array

vars  =[('GRBNAME','GRB%10s'),
        ('GRBTRIGGERDATE','%10s'),
        ('GRBDATE','%10s'),
        ('GRBT90','%.5s'),
        ('RA','%10s'),
        ('DEC','%10s'),
        ('THETA','%.1f'),
        #('T00_B','%.2f'),
        #('T00_U','%.2f'),
        ('T05','%.2f'),
        #('T100_B','%.2f'),
        #('T100_U','%.2f'),
        ('T95','%.2f'),
        #('T05_key','%.2f'),
        #('T95_key','%.2f'),    
        #('T05_prob','%.2f'),
        #('T95_prob','%.2f'),
        #('T90_prob','%.2f'),
        ('TSMAP_RAMAX','%.3f'),
        ('TSMAP_DECMAX','%.3f'),
        ('TSMAP_ERR68','%.3f'),
        ('TSMAP_ERR90','%.3f'),
        ('TSMAP_ERR95','%.3f'),
        ('TS_EG_v02','%.1f'),
        ('TS_GRB','%.1f'),
        ('NobsTot','%d'),
        #('N23_EG_v02','%.1f'),
        #('N34_EG_v02','%.1f'),
        #('N23_GRB','%.1f'),
        #('N34_GRB','%.1f'),
        #('FirstEventTime_ROI_E','%.4f'),
        ('EnergyMax_Energy_T_ROI_E','%.1f'),
        ('EnergyMax_Time_T_ROI_E','%.4f'),
        ('PeakFlux','%.2e +/\- %.2e'),
        ('PeakFlux_Time','%.2e +/\- %.2e'),
        ('FLUENCE_ENE','%.2e +/\- %.2e'),
        ('FLUX','%.2e +/\- %.2e'),
        ('FLUX_ENE','%.2e +/\- %.2e'),
        ('GRBindex','%.2e +/\- %.2e'),
        #('like_timeBins','%s'),
        ('PROB_EMAX','%s'),
        ('PROB_FIRST','%s'),
        ('PROB_LAST','%s'),        
        ('AG_F0','%.2e +/\- %.2e'),
        ('AG_IN','%.2e +/\- %.2e')
        ]


#formats=['GRB%10s','%10s','%10s','%.5s','%10s','%10s','%.1f',
#         '%.2f','%.2f','%.2f','%.2f','%.2f','%.2f',
#         '%.2f','%.2f',
#         '%.2f','%.2f','%.2f',
#         '%.3f','%.3f','%.3f','%.3f','%.3f',
#         '%.1f','%.1f',
#         '%i','%.1f','%.1f','%.1f','%.1f',
#         '%.4f','%.1f','%.4f',
#         '%.2e +/\- %.2e','%.2e +/\- %.2e',
#         '%.2e +/\- %.2e',
#         '%.2e +/\- %.2e','%.2e +/\- %.2e','%.3f +/\- %.3f','%s']


tvars=['GRBNAME','GRBTRIGGERDATE','GRBT05','GRBT95','RA','DEC','THETA','ZENITH','GBMT90',
       'T00_B','T00_U','T05','T100_B','T100_U','T95',
       'T05_key','T95_key',
       'T05_prob','T95_prob','T90_prob',
       'TSMAP_RAMAX','TSMAP_DECMAX','TSMAP_ERR68','TSMAP_ERR90','TSMAP_ERR95',
       'TS_EG_v02','TS_GRB',
       'NobsTot','N23_EG_v02','N34_EG_v02','N23_GRB','N34_GRB',
       'FirstEventTime_ROI_E','EnergyMax_Energy_T_ROI_E','EnergyMax_Time_T_ROI_E',
       'FLUX','FLUX_ERR','PeakFlux','PeakFlux_ERR','PeakFlux_Time','PeakFlux_Time_ERR','GRBindex','GRBindex_ERR',
       'FLUX_ENE','FLUX_ENE_ERR','FLUENCE_ENE','FLUENCE_ENE_ERR',
       'TS_BB','GRBindex_BB','GRBindex_BB_ERR','FLUX_BB','FLUX_BB_ERR','FLUX_ENE_BB','FLUX_ENE_BB_ERR','FLUENCE_BB_ENE','FLUENCE_BB_ENE_ERR',
       'PROB_EMAX_E','PROB_EMAX_T','PROB_EMAX_P1','PROB_EMAX_P2',
       'PROB_FIRST_E','PROB_FIRST_T','PROB_FIRST_P1','PROB_FIRST_P2',
       'PROB_LAST_E','PROB_LAST_T','PROB_LAST_P1','PROB_LAST_P2',
       'AG_F0','AG_IN','AG_F0_ERR','AG_IN_ERR'
       ]


#Latex1={'GRBNAME':'%s',
#        'T05B':'%.2f'
#        'T05U':'%.2f'
#        'T05':'%.2f'
#        'T90B':'%.2f'
#        'T90B':'%.2f'
#        'T90B':'%.2f'
#        }

grbout_dir_0    = 'DATA/GRBOUT'
# grbout_dir     = 'DATA/GRBOUT_PF_100811_GBMT90'
grbout_dir      = 'DATA/GRBOUT_PF_100915_BKGET90'
# grbout_dir     = 'DATA/GRBOUT_BKGE_100901_BKGET90'

decorate_base   = 'http://glast-ground.slac.stanford.edu/Decorator/Decorate/users/omodei/GRBanalysis/%s' % grbout_dir

grbs_list = grbs.getGRBs()
#grbs_list = grbs.getARRs()
#grbs_list = grbs.getULs()

grb_dir='%s/%s' 

grbs_d1 = grbs_list #sorted(grbs.GRBs.keys())

if not os.path.exists(grbout_dir):
    runShellScript('mkdir %s' % grbout_dir)
    pass

for g in grbs_d1:    
    gdir_new = grb_dir %(grbout_dir,grbs.GetFullName(g))
    
    if not os.path.exists(gdir_new):
        gdir_old = grb_dir %(grbout_dir_0,grbs.GetFullName(g))  
        print 'copying/moving the %s directory...' % gdir_old
        cmd='cp -r %s %s' %(gdir_old,gdir_new)
        cmd='mv %s %s' %(gdir_old,gdir_new)
        print cmd
        runShellScript(cmd)
        pass
    else:
        print 'file %s not copied/moved...directory already there...' % g
    pass
# elif v=='FLUX' and a[0]==0.0:
#    FLUX' in v:
#    if 'UL_EnFLUX_BA_-2.2##            
#                pprint
            #                ,'FLUX_ENE'




def readOneFile(filename,silent=1):
    fin   = file(filename)    
    lines = fin.readlines()
    pars  = {}
    for line in lines:
        if line.find('#')!= 0:
            pp=line.split('=')
            var_n=pp[0].strip()
            var_v=pp[1].strip()
            if var_n=='UL_FLUX_BA_-2.2':
                var_n='FLUX'
                var_v='(%s,%s)' % (var_v,0.0)
                pass
            elif var_n=='UL_EnFLUX_BA_-2.2':
                var_n='FLUX_ENE'
                var_v='(%s,%s)' % (var_v,0.0)
                pass
            pars[var_n]=var_v
            pass
        pass
    if silent==0:
        print ' =================================================== '
        print ' ====          VARIABLES IN THE DICTIONARY      ==== '
        for k in sorted(pars.keys()):
            print k
            pass
        pass
    return pars


if __name__=='__main__':
    table = {}
    grbs_d1 = sorted(grbs_list)#grbs_d.keys())
    grbs_a=[]
    for i,g in enumerate(grbs_d1):
        file_name='%s/%s/results_%s.txt' % (grbout_dir,grbs.GetFullName(g),grbs.GetFullName(g))
        try:        
            entry = readOneFile(file_name,i)
            entry['GRBDATE'] = grbs.GetDate(g)
            
            table[g]=entry
            grbs_a.append(g)
        except:
            print 'GRB %s not found!' % g
        pass
    print '--------------------------------------------------'
    print 'VARIABLES IN THE TXT FILE:'
    for v in vars:
        print '|| %s ||     |' % v[0]
        pass
    print '--------------------------------------------------'
    ##################################################
    print '--------------------------------------------------'
    print 'VARIABLES IN THE TXT FILE (LaTeX):'
    for v in vars:        
        print ' ${%s}$ & \\\ ' % v[0].replace('_','}_{')
        pass
    print '--------------------------------------------------'
    ##################################################
    output_file_name= '%s/grbs_summary_file.txt' % grbout_dir
    fout = file(output_file_name,'w')
    ##################################################
    txt=''
    for v in vars:
        txt=txt+'|| %10s\t' % v[0]
        pass
    fout.write(txt+'|| \n')
    

    for g in grbs_a:
        txt=''
        grb_name=grbs.GetFullName(g)
        for i,v in enumerate(vars):
            if i==0:
                txt0='[%s|%s/%s]' % (v[1],decorate_base,grb_name)
            elif v[0]=='like_timeBins':
                txt0='[%s|%s/%s/ExtendedEmission/like_%s.png]' % (v[1],decorate_base,grb_name,grb_name)
            elif v[0]=='THETA':
                txt0='[%s|%s/%s/%s_%d_%d_pointing.png]' % (v[1],decorate_base,grb_name,grb_name,float(table[g]['BEFORE']),float(table[g]['AFTER']))
            elif 'TSMAP_' in v[0]:
                txt0='[%s|%s/%s/%s_LAT_tsmap_tsmap_2.png]' % (v[1],decorate_base,grb_name,grb_name)
            elif 'TS_' in v[0]:
                txt0='[%s|%s/%s/spectralPlot.png]' % (v[1],decorate_base,grb_name)
            elif 'NobsTot' in v[0]:
                txt0='[%s|%s/%s/%s_LAT_ROIevt.png]' % (v[1],decorate_base,grb_name,grb_name)
            else:
                txt0='%s' % v[1]
                pass            
            try:
                entry= table[g][v[0]].replace('(','').replace(')','')
            except:
                entry='0,0'
                pass
            
            try:
                if v[1].find('s')>-1:
                    txt=txt+'| '+txt0 % entry +'\t'
                else:
                    a=[]
                    for t in entry.split(','):
                        a.append(float(t))
                        pass
                    txt=txt+'| '+txt0 % tuple(a)+'\t'
                    pass
                pass
            except:
                txt=txt+'| - \t'
                pass
            pass
        fout.write(txt+' | \n')        
        pass
    fout.close()
    ##################################################
    # SAVE THE ROOT TREE
    # New loop for saving the GRBs into the tree
    output_file_root= '%s/grbs_summary_file.root' % grbout_dir
    rootf     = ROOT.TFile(output_file_root,'RECREATE')
    tree      = ROOT.TTree('GRBCatalog','GRBCatalog')    
    arrays={}
    for v in tvars:
        arrays[v]=array('f',[0])
        tree.Branch(v,arrays[v],'%s/F' % v)
        pass
    ##################################################
    
    for g in grbs_a:
        grb_name=grbs.GetFullName(g)
        
        for v in tvars:
            try:
                entry= table[g][v].replace('(','').replace(')','')
            except:
                entry='0,0'
                pass
            if 'ERR' in v:
                continue
            if 'ERR' not in v and ('FLUX' in v or 'FLUENCE' in v or 'GRBindex' in v or 'PeakFlux' in v or 'AG' in v):

                v1=float(entry.split(',')[0])
                v2=float(entry.split(',')[1])
                arrays[v][0]       =v1
                arrays[v+'_ERR'][0]=v2
                print g, v,v+'_ERR',entry,v1,v2
                pass
            elif v=='PROB_EMAX_T':
                try:
                    arrays['PROB_EMAX_T'][0]       = float(table[g]['PROB_EMAX'].split(',')[0].replace('(','').replace(')',''))
                    arrays['PROB_EMAX_E'][0]       = float(table[g]['PROB_EMAX'].split(',')[1].replace('(','').replace(')',''))/1000.
                    arrays['PROB_EMAX_P1'][0]      = float(table[g]['PROB_EMAX'].split(',')[2].replace('(','').replace(')',''))
                    arrays['PROB_EMAX_P2'][0]      = float(table[g]['PROB_EMAX'].split(',')[3].replace('(','').replace(')',''))
                except:
                    arrays['PROB_EMAX_T'][0]       = 0.0
                    arrays['PROB_EMAX_E'][0]       = 0.0
                    arrays['PROB_EMAX_P1'][0]      = 0.0
                    arrays['PROB_EMAX_P2'][0]      = 0.0
                    pass
            elif v=='PROB_FIRST_T':
                try:
                    arrays['PROB_FIRST_T'][0]       = float(table[g]['PROB_FIRST'].split(',')[0].replace('(','').replace(')',''))
                    arrays['PROB_FIRST_E'][0]       = float(table[g]['PROB_FIRST'].split(',')[1].replace('(','').replace(')',''))/1000.
                    arrays['PROB_FIRST_P1'][0]      = float(table[g]['PROB_FIRST'].split(',')[2].replace('(','').replace(')',''))
                    arrays['PROB_FIRST_P2'][0]      = float(table[g]['PROB_FIRST'].split(',')[3].replace('(','').replace(')',''))
                except:
                    arrays['PROB_FIRST_T'][0]       = 0.0
                    arrays['PROB_FIRST_E'][0]       = 0.0
                    arrays['PROB_FIRST_P1'][0]      = 0.0
                    arrays['PROB_FIRST_P2'][0]      = 0.0
                    pass
            elif v=='PROB_LAST_T':
                try:
                    arrays['PROB_LAST_T'][0]       = float(table[g]['PROB_LAST'].split(',')[0].replace('(','').replace(')',''))
                    arrays['PROB_LAST_E'][0]       = float(table[g]['PROB_LAST'].split(',')[1].replace('(','').replace(')',''))/1000.
                    arrays['PROB_LAST_P1'][0]      = float(table[g]['PROB_LAST'].split(',')[2].replace('(','').replace(')',''))
                    arrays['PROB_LAST_P2'][0]      = float(table[g]['PROB_LAST'].split(',')[3].replace('(','').replace(')',''))
                except:
                    arrays['PROB_LAST_T'][0]       = 0.0
                    arrays['PROB_LAST_E'][0]       = 0.0
                    arrays['PROB_LAST_P1'][0]      = 0.0
                    arrays['PROB_LAST_P2'][0]      = 0.0
                    pass                
                pass
            else:
                try:
                    tentry=float(entry)
                except:
                    tentry=0.0
                    pass
                arrays[v][0]=tentry
                pass
            pass
        tree.Fill()
        pass
    tree.Scan('PROB_EMAX_T:PROB_FIRST_T:PROB_LAST_T:GRBindex:GRBindex_ERR')
    print '--------------------------------------------------'
    print 'VARIABLES IN THE ROOT TREE:'
    for v in tvars:
        print 'GRBCatalog.%s' % v
        pass
    print '--------------------------------------------------'    
    print ' --> ROOT file saved in:  %s' %output_file_root
    print ' --> TXT  file saved in:  %s' %output_file_name
    print '--------------------------------------------------'    

    tree.Write()
    rootf.Close() 

    ##################################################
    # GENERATION OF LATEX TABLES
    # TABLE 1 DURATION:
    print '00000'
    #print table['GRB080825C']
    
    print '\hline'
    print ' GRB & GBM T$_{90}$ & LAT T$_{05}$ & LAT T$_{95}$ & LLE T$_{05}$ & LLE T$_{95}$ \\\ '
    print '\hline'
    
    for g in grbs_a:
        grb_name=grbs.GetFullName(g)
        try:
            tGBM    = float(table[g]['GBMT90'])
        except:
            tGBM    = 0.0
            pass
        
        try:
            tLAT95  = float(table[g]['BKGET95'])                
        except:
            tLAT95 = 0.0       
            pass
        
        try:
            tLAT05  = float(table[g]['BKGET05'])
        except:
            tLAT05  = 0.0       
            pass
        try:
            tLATLLE95 = float(table[g]['LLET90'])
        except:
            tLATLLE95 = 0.0       
            pass
        
        try:
            tLATLLE05 = float(table[g]['LLET05'])
        except:
            tLATLLE05 = 0.0
            pass

        print '%s & %.2f & %.2f & %.2f & %.2f & %.2f \\\ ' %(g,tGBM,tLAT05,tLAT95,tLATLLE05, tLATLLE95)
        pass

    # TABLE 2 FLUXES, FLUENCES, and INDEXES :
    
    print '\hline'
    print ' GRB NAME & Number Of Transient Events & Predicted Number of Events & Test Statistic (TS) & Flux                           & Fluence \\\ '
    print '          & Compatible with the 95\% containment &                            &                     & ph/cm$^2$/s ($\\times 10^{-5}$) & erg/cm$^2$ ($\\times 10^{-5}$) \\\ '
    print '\hline'
    scale=1e5
    for g in grbs_a:
        grb_name=grbs.GetFullName(g)
        try:
            NumberOfEvents_T_ROI_E    = float(table[g]['NumberOfEvents_T_ROI_E'])
        except:
            NumberOfEvents_T_ROI_E    = 0
            pass
        
        try:
            Ntot_GRB  = float(table[g]['Ntot_GRB'])                
        except:
            Ntot_GRB = 0.0       
            pass
        
        try:
            TS  = float(table[g]['TS_GRB'])
        except:
            TS  = 0.0       
            pass
        try:
            FLUX     = scale* float(table[g]['FLUX'].split(',')[0].replace('(',''))
            FLUX_ERR = scale* float(table[g]['FLUX'].split(',')[1].replace(')',''))
        except:
            FLUX = 0.0       
            FLUX_ERR = 0.0       
            pass
        
        try:
            FLUENCE_ENE     = scale* float(table[g]['FLUENCE_ENE'].split(',')[0].replace('(',''))
            FLUENCE_ENE_ERR = scale* float(table[g]['FLUENCE_ENE'].split(',')[1].replace(')',''))

        except:
            FLUENCE_ENE = 0.0
            FLUENCE_ENE_ERR = 0.0
            pass

        print '%s & %d & %.1f & %.1f & %.2f $\pm$ %.2f & %.2f $\pm$ %.2f \\\ ' %(g,NumberOfEvents_T_ROI_E,Ntot_GRB,TS,FLUX,FLUX_ERR,FLUENCE_ENE,FLUENCE_ENE_ERR)
        pass
    
    
    # TABLE 3. FLUXES, FLUENCES, and INDEXES :
    print '-----------------------  Energy Max -------------------------------------'
    
    print '\hline'    
    print ' GRB NAME & Energy & Arrival time  & Probability 1 & Probability 2 \\\ '
    print '          & (GeV)  & Since T$_{0}$ & Probability 1 & Probability 2 \\\ '
    print '\hline'
    
    for g in grbs_a:
        grb_name=grbs.GetFullName(g)
        try:
            PROB_EMAX_T       = float(table[g]['PROB_EMAX'].split(',')[0].replace('(','').replace(')',''))
            PROB_EMAX_E       = float(table[g]['PROB_EMAX'].split(',')[1].replace('(','').replace(')',''))/1000.
            PROB_EMAX_P1      = float(table[g]['PROB_EMAX'].split(',')[2].replace('(','').replace(')',''))
            PROB_EMAX_P2      = float(table[g]['PROB_EMAX'].split(',')[3].replace('(','').replace(')',''))
        except:
            PROB_EMAX_E       = 0
            PROB_EMAX_T       = 0
            PROB_EMAX_P1      = 0
            PROB_EMAX_P2      = 0
            pass
        
        print '%s & %.2f & %.4f & %.3f  & %.3f \\\ ' %(g,PROB_EMAX_E, PROB_EMAX_T, PROB_EMAX_P1, PROB_EMAX_P2)
        pass

    # TABLE 3. FLUXES, FLUENCES, and INDEXES :

    print '-----------------------  First Event -------------------------------------'

    print '\hline'
    print ' GRB NAME & Energy & Arrival time  & Probability 1 & Probability 2 \\\ '
    print '          & (GeV)  & Since T$_{0}$ & Probability 1 & Probability 2 \\\ '
    print '\hline'
    
    for g in grbs_a:
        grb_name=grbs.GetFullName(g)
        try:
            PROB_FIRST_T       = float(table[g]['PROB_FIRST'].split(',')[0].replace('(','').replace(')',''))
            PROB_FIRST_E       = float(table[g]['PROB_FIRST'].split(',')[1].replace('(','').replace(')',''))/1000.
            PROB_FIRST_P1      = float(table[g]['PROB_FIRST'].split(',')[2].replace('(','').replace(')',''))
            PROB_FIRST_P2      = float(table[g]['PROB_FIRST'].split(',')[3].replace('(','').replace(')',''))
        except:
            PROB_FIRST_T       = 0
            PROB_FIRST_E       = 0
            PROB_FIRST_P1      = 0
            PROB_FIRST_P2      = 0
            pass
        print '%s & %.2f & %.4f & %.3f  & %.3f \\\ ' %(g,PROB_FIRST_E, PROB_FIRST_T, PROB_FIRST_P1, PROB_FIRST_P2)
        pass

    print '-----------------------  Last Event -------------------------------------'
    print '\hline'
    print ' GRB NAME & Energy & Arrival time  & Probability 1 & Probability 2 \\\ '
    print '          & (GeV)  & Since T$_{0}$ & Probability 1 & Probability 2 \\\ '
    print '\hline'
    for g in grbs_a:
        grb_name=grbs.GetFullName(g)
        
        try:
            PROB_LAST_T       = float(table[g]['PROB_LAST'].split(',')[0].replace('(','').replace(')',''))
            PROB_LAST_E       = float(table[g]['PROB_LAST'].split(',')[1].replace('(','').replace(')',''))/1000.
            PROB_LAST_P1      = float(table[g]['PROB_LAST'].split(',')[2].replace('(','').replace(')',''))
            PROB_LAST_P2      = float(table[g]['PROB_LAST'].split(',')[3].replace('(','').replace(')',''))
        except:
            PROB_LAST_E       = 0
            PROB_LAST_T       = 0
            PROB_LAST_P1      = 0
            PROB_LAST_P2      = 0
            pass
        print '%s & %.2f & %.4f & %.3f  & %.3f \\\ ' %(g,PROB_LAST_E, PROB_LAST_T, PROB_LAST_P1, PROB_LAST_P2)
        pass

    # TABLE PEAK FLUX
    
    print '\hline'
    print 'GRB NAME & Peak Flux & Time of the Peak Flux & decay index \\\ '
    print '\hline'

    for g in grbs_a:
        #print table[g]
        scale = 1e5
        try:
            PeakFlux     = scale* float(table[g]['PeakFlux'].split(',')[0].replace('(',''))
            PeakFlux_ERR = scale* float(table[g]['PeakFlux'].split(',')[1].replace(')',''))
        except:
            PeakFlux = 0.0
            PeakFlux_ERR = 0.0
            pass
        
        scale=1
        try:
            PeakFlux_Time     = scale* float(table[g]['PeakFlux_Time'].split(',')[0].replace('(',''))
            PeakFlux_Time_ERR = scale* float(table[g]['PeakFlux_Time'].split(',')[1].replace(')',''))
            
        except:
            PeakFlux_Time     = 0.0
            PeakFlux_Time_ERR = 0.0
            pass
        
        scale=1
        try:
            AG_IN     = scale* float(table[g]['AG_IN'].split(',')[0].replace('(',''))
            AG_IN_ERR = scale* float(table[g]['AG_IN'].split(',')[1].replace(')',''))            
        except:
            AG_IN      = 0.0
            AG_IN_ERRR = 0.0
            pass

        print '%s & %.2f $\pm$ %.2f & %.2f $\pm$ %.2f & %.2f $\pm$ %.2f \\\ ' %(g,PeakFlux,PeakFlux_ERR,PeakFlux_Time,PeakFlux_Time_ERR,AG_IN,AG_IN_ERR)
        pass
