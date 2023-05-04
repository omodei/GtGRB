#!/usr/bin/env python
import scripts.GRBs as grbs
import os,sys
import ROOT
from array import array
from scripts.GCNNumbers import GCNNumbers
from scripts.GRBDictionary import GRBs as GRBInTheDictionary

debug=0

minTS  = 20.0
minLLE = 4.75
nmin   = 0

vars  =[('GRBNAME','GRB%10s'),
        ('GRBTRIGGERDATE','%.3f'),
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
        
        ('LIKE_BKGE_TS_EG_v02','%.1f'),
        ('LIKE_BKGE_TS_GRB','%.1f'),
        ('LIKE_BKGE_NobsTot','%d'),
        ('LIKE_BKGE_FLUENCE_ENE','%.2e +/\- %.2e'),
        ('LIKE_BKGE_FLUX','%.2e +/\- %.2e'),
        ('LIKE_BKGE_FLUX_ENE','%.2e +/\- %.2e'),
        ('LIKE_BKGE_GRBindex','%.2e +/\- %.2e'),
        #('LIKE_BKGE_N23_EG_v02','%.1f'),
        #('LIKE_BKGE_N34_EG_v02','%.1f'),
        #('LIKE_BKGE_N23_GRB','%.1f'),
        #('LIKE_BKGE_N34_GRB','%.1f'),
        #('FirstEventTime_ROI_E','%.4f'),
        ('EnergyMax_Energy_T_ROI_E','%.1f'),
        ('EnergyMax_Time_T_ROI_E','%.4f'),        
        ('PeakFlux','%.2e +/\- %.2e'),
        ('PeakFlux_Time','%.2e +/\- %.2e'),
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


##################################################
# THIS PARSE ONE FILE
##################################################

def readOneFile(filename,silent=1):
    fin   = file(filename)    
    lines = fin.readlines()
    pars  = {}
    #print '--------------------------------------------------------'
    for line in lines:
        if line.find('#')!= 0:
            pp=line.split('=')
            var_n = pp[0].strip()
            var_v = pp[1].strip()
            
            ulindex = -2.25
            try:
                ulindex = float(pars['GRBindex'])
            except:
                pass
            # print var_n, var_v, 'UL_FLUX_BA_%.2f' % ulindex
            if var_n ==('UL_FLUX_BA_%.2f' % ulindex):
                var_n = 'FLUX'
                pars['FLUX']     = var_v
                pars['FLUX_ERR'] = '0.0'                
            elif var_n==('UL_EnFLUX_BA_%.2f' % ulindex):
                pars['FLUX_ENE']=var_v
                pars['FLUX_ENE_ERR'] ='0.0'
            else:
                pars[var_n]=var_v
                pass
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

##################################################
# This save the table in the root tree
##################################################

if __name__=='__main__':
    help=''' ---------------------------------------------------
    This program convert the output from gtgrb into a root tree.
    Written by Nicola Omodei: nicola.omodei@slac.stanford.edu
    Usage:
    ./app/MakeTree.py OUTPUTDIR FILTER
    OUTPUTDIR: is the path to the base of the output directory. This program
    expects to find files under OUTPUTDIR/GRBNAME/results_GRBNAME.txt

    FILTER: can be a string to select only GRB in the database that contains that string.
     ---------------------------------------------------
    '''
    import glob
    grbout_dir      = sys.argv[1]
    try:
        filter= sys.argv[2]
    except:
        filter = None
        pass
    
    decorate_base   = 'http://glast-ground.slac.stanford.edu/Decorator/Decorate/users/omodei/GRBanalysis/%s' % grbout_dir
    if filter is None:
        grbs_d1=[]
    else:
        grbs_d1 = grbs.getGRBs(filter)
        pass
    
    if len(grbs_d1)==0:
        filelist = glob.glob('%s/*' % grbout_dir)
        # print filelist        
        for ifile in filelist:
            if os.path.isdir(ifile): grbs_d1.append(ifile[ifile.rfind('/')+1:])
            pass
        pass
    grbs_d1=sorted(grbs_d1)
    table = {}    
    print 'SELECTED GRBS: ', len(grbs_d1)
    grbs_a=[]
    
    
    #print '#GRB GRBNAME GRBTRIGGERDATE GBMT90 BKGET05 BKGET95'
    NumberLLDetected=0
    NumberLLDetected2=0
    NumberLikelihood=0
    NumberInTheFoV=0
    NumberGRB=0
    NumberGRBDetected=0
    for i,g in enumerate(grbs_d1):        
        file_name='%s/%s/results_%s.txt' % (grbout_dir,grbs.GetFullName(g),grbs.GetFullName(g))
        if not os.path.exists(file_name):
            print ' === File not found! === '
            continue
        
        if debug:
            entry = readOneFile(file_name,i)            
            pass
        if 1==1:#try:
            entry = readOneFile(file_name,i)        
            entry['GRBDATE'] = entry['GRBDATE'][:21]
            if 'LLE_DetMaxSign' in entry.keys(): entry['LLEDETECTED']  = int(float(entry['LLE_DetMaxSign'])>minLLE)
            else: entry['LLEDETECTED']   = 0
            if 'LLENSIG' in entry.keys(): entry['LLEDETECTED2']  = int(float(entry['LLENSIG'])>minLLE)
            else: entry['LLEDETECTED2']  = 0
            
            max_ts = -1
            
            detected_ag_like =0
            detected_gbm_like=0

            LIKE_GBM_TS_GRB = 0
            LIKE_GBM_NobsTot= 0
            LIKE_AG_TS_GRB  = 0
            LIKE_AG_NobsTot =0
            
            if 'LIKE_GBM_TS_GRB' in entry.keys():
                LIKE_GBM_TS_GRB = float(entry['LIKE_GBM_TS_GRB'])
                LIKE_GBM_NobsTot= int(float(entry['LIKE_GBM_NobsTot']))
                if LIKE_GBM_TS_GRB>minTS and LIKE_GBM_NobsTot>nmin : detected_gbm_like=1
                pass

            if 'LIKE_AG_TS_GRB' in entry.keys():
                LIKE_AG_TS_GRB = float(entry['LIKE_AG_TS_GRB'])
                LIKE_AG_NobsTot= int(float(entry['LIKE_AG_NobsTot']))
                if LIKE_AG_TS_GRB>minTS and LIKE_AG_NobsTot>nmin : detected_ag_like=0#1
                pass
            
            for mylike in ('LIKE_GBM_TS_GRB','LIKE_BKGE_TS_GRB','LIKE_JOINT_TS_GRB','LIKE_AG_TS_GRB','LIKE_EXT_TS_GRB'):
                if mylike in entry.keys(): max_ts = max(float(entry[mylike]),max_ts)
                pass
            
            if max_ts > -1: entry['LIKEDETECTED'] = int(max_ts>minTS)
            else: entry['LIKEDETECTED'] = 0
            
            if max_ts > 0: entry['LIKEDETECTED_MAXTS'] = max_ts
            else: entry['LIKEDETECTED_MAXTS'] = 0

            NumberGRB+=1
            if entry['LLEDETECTED'] ==1 :  NumberLLDetected+=1
            if entry['LLEDETECTED2'] ==1 : NumberLLDetected2+=1
            
            if 'THETA' in entry.keys():
                if float(entry['THETA'])<70: NumberInTheFoV+=1
                pass
            
            if entry['LIKEDETECTED']==1: NumberLikelihood+=1
            # DETECTION CONDITION:
            
            
            
            
            if (float(entry['THETA'])<90) and ((detected_gbm_like or detected_ag_like) or (entry['LLEDETECTED'] and entry['LLEDETECTED2'])):
                NumberGRBDetected+=1
                pass
            
            table[g]=entry
            grbs_a.append(g)
            # print grbs.GetFullName(g)
            # --------------------------------------------------
            # safe checks:
            for x in ('LLEt05','LLEt95','LLE_DetMaxSign','LLENSIG'):
                if not x in entry.keys(): entry[x]=0
            # --------------------------------------------------
            
            if float(entry['LLEt05']) < -1000:
                entry['LLEt05']=0
                entry['LLEt05loerr']=0
                entry['LLEt05hierr']=0
                pass
            if float(entry['LLEt95']) < -1000:
                entry['LLEt95']=0
                entry['LLEt95loerr']=0
                entry['LLEt95hierr']=0
                pass
            pass
        else: #except:
            print 'GRB %s not found!' % g
            pass
        #try:
        # print g, grbs.GetFullName(g), float(entry['GRBTRIGGERDATE']),float(entry['GBMT90']),float(entry['BKGET05']),float(entry['BKGET95'])

        print '**************************************************'
        print g, grbs.GetFullName(g), float(entry['THETA']),float(entry['LLE_DetMaxSign']),float(entry['LLENSIG']),LIKE_GBM_TS_GRB,LIKE_GBM_NobsTot,LIKE_AG_TS_GRB,LIKE_AG_NobsTot
        print '**************************************************'
        #except:
        #    pass
        pass
    print '--------------------------------------------------'
    print ' TOTAL NUMBER OF GRB READ ................... %d' % NumberGRB
    print ' TOTAL NUMBER OF GRB LLE  (LLE_DetMaxSign)... %d' % NumberLLDetected
    print ' TOTAL NUMBER OF GRB LLE2 (LLENSIGM)......... %d' % NumberLLDetected2
    print ' TOTAL NUMBER OF GRB LIKE.................... %d' % NumberLikelihood
    print ' TOTAL NUMBER OF GRB THETA < 70 deg.......... %d' % NumberInTheFoV
    print ' TOTAL NUMBER OF GRB DETECTED................ %d' % NumberGRBDetected
    print '--------------------------------------------------'
    
    makeTXT=False
    if makeTXT:
        print 'VARIABLES IN THE TXT FILE:'
        for v in vars:
            print '|| %s ||     |' % v[0]
            pass
        print '--------------------------------------------------'
        # #################################################
        # print '--------------------------------------------------'
        # print 'VARIABLES IN THE TXT FILE (LaTeX):'
        # for v in vars:        
        #     print ' ${%s}$ & \\\ ' % v[0].replace('_','}_{')
        #     pass
        # print '--------------------------------------------------'
        # #################################################
        output_file_name= '%s/grbs_summary_file.txt' % grbout_dir
        fout = file(output_file_name,'w')
        # #################################################
        txt=''
        for v in vars:
            txt=txt+'|| %10s\t' % v[0]
            pass
        fout.write(txt+'|| \n')
        
        
        for g in grbs_a:
            txt=''
            grb_name=grbs.GetFullName(g)
            print '--------------------------------------------------'
            print grb_name
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
                    entry= table[g][v[0]]
                except:
                    entry='0.0'
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
        pass
    # #################################################
    # SAVE THE ROOT TREE
    # New loop for saving the GRBs into the tree
    string_variables=['GRBNAME','GRBDATE','GCNNAME','like_model','IRFS','DETLIST']
    double_variables=['GRBMET','GRBTRIGGERDATE']
    string_lenght   = 30

    if grbout_dir[-1]=='/':grbout_dir = grbout_dir[:-1]
    out_file_name = '%s.root' % grbout_dir[grbout_dir.rfind('/')+1:]
    print '##################################################'
    print out_file_name
    print '##################################################'

    output_file_root= '%s/%s' % (grbout_dir,out_file_name)
    rootf     = ROOT.TFile(output_file_root,'RECREATE')
    tree      = ROOT.TTree('GRBCatalog','GRBCatalog')
    
    arrays={}
    tvars=[]
    for g in grbs_a:
        for k in table[g].keys():
            if k not in tvars:
                tvars.append(k)
                pass
            pass
        pass
    tvars = sorted(tvars) #table[g].keys())
    
    for v in tvars:
        if v in string_variables:
            arrays[v]=array('c',string_lenght*'.'+'\0')
            tree.Branch(v,arrays[v],'%s/C' % v)
        elif v in double_variables:
            arrays[v]=array('d',[0.0])
            tree.Branch(v,arrays[v],'%s/D' % v)
        else:
            arrays[v]=array('f',[0.0])
            tree.Branch(v,arrays[v],'%s/F' % v)
            pass
        pass
    # #################################################
    
    for g in grbs_a:
        grb_name=grbs.GetFullName(g)        
        for v in tvars:
            if v in string_variables:
                for j in range(string_lenght): # tbdata.formats[na]):fields[na][i]):
                    try:
                        arrays[v][j] = table[g][v][j]
                    except:
                        arrays[v][j] = ' '
                        pass
                    pass
                pass
            else:
                try:
                    tentry = float(table[g][v])
                except:
                    tentry=0.0
                    pass
                arrays[v][0]=tentry
                pass
            pass
        tree.Fill()
        pass
    #tree.Scan('PROB_EMAX_T:PROB_FIRST_T:PROB_LAST_T:GRBindex:GRBindex_ERR')
    print '--------------------------------------------------'
    print 'VARIABLES IN THE ROOT TREE:'
    for v in sorted(tvars):
        print 'GRBCatalog.%s' % v
        pass
    print '--------------------------------------------------'    
    print ' --> ROOT file saved in:  %s' %output_file_root
    if makeTXT:
        print ' --> TXT  file saved in:  %s' %output_file_name
        pass
    print '--------------------------------------------------'    

    tree.Write()
    rootf.Close() 

    ##################################################
    def InterpretString(g,var):
        #for v in tvars:
        #    var.replace(v,"g['%s']" % v)        
        operators=['+','-','*','/']
        txt=''
        for o in operators:
            if o in var:
                var1 = var.split(o)[0]
                var2 = var.split(o)[1]
                if var1 not in table[g].keys() or var2 not in table[g].keys():
                    return 0
                
                val1 = eval("table['%s']['%s']" % (g,var1.strip()))
                val2 = eval("table['%s']['%s']" % (g,var2.strip()))
                val  = eval('%s%s%s' % (val1,o,val2))
                if debug:
                    print '888888 ===> ', val1,val2,val
                    pass
                return val
            pass
        if var not in table[g].keys():
            return 0
        txt="table['%s']['%s']" % (g,var)
        val = eval(txt)
        if debug:
            print '&&&&&&&&&&& %s &&&   %s &&&&&&&&&&&&&&' % (txt,val)
            pass        
        try: val=float(val)
        except: pass
        return val
    ##################################################
    
    def MakeTable(table,grbs_a,header_variable_format,caption='',label='',multipleraws=None,onlyDetected=False):
        number_of_colums = len(header_variable_format)
        caption=caption.replace('\b','\\b')
        
        print '% ------------------------------------------------------------------------------ '
        print '\\clearpage'
        print '\\thispagestyle{empty}'
        print '\\clearpage'
        print '\\begin{center}'
        print '\\begin{deluxetable}{l'+'r'*(number_of_colums-1)+'}'
        print '\\tabletypesize{\\tiny}'
        print '\\tablecolumns{%d}' % number_of_colums
        print '\\tablewidth{0pt}'
        print '\\tablecaption{%s\label{%s}}' % (caption,label)
        txt= '\\tablehead{'
        for i in range(number_of_colums-1):
            txt += '\\colhead{%s} & ' %(header_variable_format[i][0])
            pass
        txt += '\\colhead{%s} \\\ ' %(header_variable_format[-1][0])
        print txt
        txt=''
        for i in range(number_of_colums-1):
            txt += '\\colhead{%s} & ' %(header_variable_format[i][1])
            pass
        txt += '\\colhead{%s}} ' %(header_variable_format[-1][1])
        print txt
        print '\\startdata'
        
        '''
        print '------------------------------------------------------------------------------'
        print '\\clearpage'
        print '\\thispagestyle{empty}'
        print '\\begin{center}'
        print '\\begin{table}[h!]\\tiny'
        print '\\begin{tabular}{l'+'|r'*(number_of_colums-1)+'}'
        
        print  '\hline'
        txt=''
        for i in range(number_of_colums-1):
            txt += (header_variable_format[i][0]+' & ')
            pass
        txt += header_variable_format[-1][0] + ' \\\ '        
        print txt
        txt=''
        for i in range(number_of_colums-1):
            txt += (header_variable_format[i][1]+' & ')
            pass
        txt += header_variable_format[-1][1] + ' \\\ '
        print txt
        print '\hline'
        '''
        
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        def WriteOneRaw(number_of_colums, header_variable_format):
            txt=''
            #debug=0

            all0 = 0
            
            try:       detected = (InterpretString(g,'LIKEDETECTED') or InterpretString(g,'LLEDETECTED'))
            except:    detected=1
            
            
            for i in range(number_of_colums):
                skip = 0
                scale = float(header_variable_format[i][4])
                replace0 = '-'
                if '@' in header_variable_format[i][2]:
                    replace0 = '0' 
                    pass
                if '$' in header_variable_format[i][2]:
                    skip = 1
                    pass

                ulprint=True
                
                variable_name = header_variable_format[i][2].replace('@','')
                variable_name = variable_name.replace('$','')
                if '!' in header_variable_format[i][2]:
                    ulprint = False
                    variable_name = variable_name.replace('!','')
                    pass
                
                if debug: print 'variable_name=' , variable_name
                if variable_name=='XXX':
                    value     = g#rbs.GetFullName(g)
                    value_err = 0
                    value_err1 = 0
                    pass
                
                cut = 1
                if '&' in header_variable_format[i][2]:
                    cut           = int(InterpretString(g,header_variable_format[i][2].split('&')[1]))
                    variable_name = header_variable_format[i][2].split('&')[0]
                    pass
                
                if variable_name=='GCN':
                    gcnname=InterpretString(g,'GCNNAME')
                    
                    if gcnname in GCNNumbers.keys():
                        value=GCNNumbers[gcnname][0]
                    else:
                        value=''
                        pass
                elif 'GRBindex' in variable_name:
                    p1=variable_name.split(',')[0].strip()
                    p2=variable_name.split(',')[1].strip()
                    p3=None
                    p4=p1.replace('_GRBindex','_FLUX_ERR')
                    value     = InterpretString(g,p1) # table[g][p1]
                    value_err = InterpretString(g,p2) # table[g][p2]
                    ts        = InterpretString(g,p4)
                    if ts==0 or cut==0:
                        value=0
                        value_err = 0
                        pass
                    pass
                    
                elif 'max(' in variable_name:
                    variable_name.replace('max(','')
                    variable_name.replace(')','')                    
                    vars=variable_name.split(',')
                    value=0
                    for p1 in vars: value=max(value,InterpretString(g,p1))                    
                    pass
                elif ',' in variable_name:
                    p1=variable_name.split(',')[0].strip()
                    p2=variable_name.split(',')[1].strip()
                    try:
                        p3=variable_name.split(',')[2].strip()
                    except:
                        p3=None
                        pass
                    
                    #try:
                    value     = InterpretString(g,p1) # table[g][p1]
                    value_err = InterpretString(g,p2) # table[g][p2]
                    if cut==0:
                        value=0
                        value_err=0
                        pass
                    if p3:
                        value_err1 = InterpretString(g,p3) # table[g][p3]
                        if cut==0: value_err1=0
                        pass
                    pass
                else:                    
                    try:
                        value     = table[g][variable_name]
                        value_err = 0.0
                        value_err1= 0.0
                    except:
                        value     = 0.0
                        value_err = 0.0
                        value_err1= 0.0
                        pass
                    if cut==0:
                        value     = 0.0
                        value_err = 0.0
                        value_err1= 0.0
                        pass                    
                    pass
                if skip==1 and float(value)==0 and value_err==0 and value_err1==0: all0=1

                if onlyDetected and detected==0: all0=1

                # #################################################
                if 1==0: print variable_name, value, value_err, value_err1, skip,all0                                    
                # #################################################
                closeout=' & '                
                if i==number_of_colums-1:
                    closeout=' \\\ '
                    pass

                format=header_variable_format[i][3]
                if format =='':
                    txt+= variable_name+ closeout
                elif 'pm' in format:
                    if debug:
                        print '--->', variable_name, float(value)/scale,' **', float(value_err)/scale, format
                        pass            
                    if float(value)/scale == 0.0 and float(value_err)/scale == 0.0:
                        txt += (replace0 +closeout)
                    elif float(value_err)/scale == 0.0:
                        ulformat = format.split('\pm')[0]
                        if ulprint: txt += ('$<' + ulformat % (float(value)/scale) + closeout)
                        else: txt += ('$' + ulformat % (float(value)/scale) + closeout)
                    else:
                        txt += ((format % (float(value)/scale,float(value_err)/scale))+closeout)
                        pass
                    pass
                elif '(' in format:
                    if debug:
                        print '--->', variable_name, float(value)/scale,' **', float(value_err)/scale, format
                        pass            
                    txt += ((format % (value,value_err))+closeout)
                    pass
                elif '+' in format:
                    if debug:
                        print '--->',float(value)/scale,float(value_err)/scale,float(value_err1)/scale
                        pass
                    
                    if float(value) == 0.0 and float(value_err) == 0.0 and float(value_err1)==0.0 :
                        txt += (replace0 +closeout)
                        
                    elif float(value_err)/scale == 0.0 and float(value_err1)==0.0:
                        ulformat = format.split('$')[0]
                        txt += ('$>' + ulformat % (float(value)/scale) + '$' + closeout)
                    else:
                        txt += ((format % (float(value)/scale,float(value_err)/scale,float(value_err1)/scale))+closeout)
                        pass
                    pass
                elif '--' in format:
                    if debug:
                        print '--->',float(value)/scale,float(value_err)/scale
                        pass
                    
                    if float(value) == 0.0 and float(value_err) == 0.0:
                        txt += (replace0 +closeout)
                    else:
                        txt += ((format % (float(value)/scale,float(value_err)/scale))+closeout)
                        pass
                    pass
                elif 'o' in format:
                    degrees = float(value)
                    arcmin  = degrees*60.
                    arcsec  = arcmin*60.
                    
                    if arcmin<0.1:
                        format=format.replace('o',"''$^{XXX}$")
                        value=arcsec
                    elif degrees<0.1:
                        format=format.replace('o',"'$^{XXX}$")
                        value=arcmin
                    else:
                        value=degrees
                        format=format.replace('o',"$^{oXXX}$")
                        pass
                    gcn_name = InterpretString(g,'GCNNAME')
                    if gcn_name in GRBInTheDictionary.keys():
                        if 'LOCINSTRUMENT' in GRBInTheDictionary[gcn_name].keys():
                            LOCINSTRUMENT = GRBInTheDictionary[gcn_name]['LOCINSTRUMENT']
                            if LOCINSTRUMENT=='LAT': format=format.replace('XXX',"\gamma")
                            if LOCINSTRUMENT=='GBM': format=format.replace('XXX',"\dagger")
                            if LOCINSTRUMENT=='LAT??': format=format.replace('XXX',"???")
                            if LOCINSTRUMENT=='SWIFT': format=format.replace('XXX',"\star")
                            if LOCINSTRUMENT=='XRT': format=format.replace('XXX',"\star")
                            pass
                    
                    if debug:
                        print '--->',variable_name,float(value)/scale
                        pass
                    if (float(value)/scale) == 0.0:
                        txt += (replace0 +closeout)
                    else:
                        txt += ((format % (float(value)/scale))+closeout)
                        pass
                    pass
                elif 's' in format:
                    if debug:
                        print '--->',variable_name,value
                        pass
                    txt += ((format % value) + closeout)                    
                    pass
                elif 'f' in format:
                    toAdd=''
                    if debug:
                        print '--->',variable_name,value
                        pass
                    try:
                        #print (float(value)) == 0.0
                        if (float(value)) == 0.0:
                            toAdd= (replace0 +closeout)
                        else:
                            toAdd= ((format % (float(value)/scale))+closeout)
                            pass
                        pass
                    except:
                        toAdd= ((format % value) + closeout)                    
                        pass
                    #print toAdd
                    try:
                        if float(toAdd.replace(closeout,'').strip()) == 0: toAdd=toAdd.replace('-0.00','0.00')
                        pass
                    except:
                        pass
                    txt+=toAdd
                    pass
                else:
                    if (float(value)/scale) == 0.0:
                        txt += (replace0 +closeout)
                    else:
                        txt += ((format % (float(value)/scale))+closeout)
                        pass
                    pass
                pass

            if all0==1: txt=None
            return txt
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        for g in sorted(grbs_a):
            hline=False
            txt = WriteOneRaw(number_of_colums, header_variable_format)
            if txt is not None:
                print txt
                hline = True
                pass
            if multipleraws is not None:
                for another_raw in multipleraws:
                    txt= WriteOneRaw(number_of_colums, another_raw)
                    if txt is not None: print txt
                    pass
                if hline:
                    print '\\hline'
                    hline=False
                pass
            pass
        
        
        print '\enddata'
        print '\\tablenotetext{a}{File used: %s }' % (grbout_dir.split('/')[-1])
        print '\\end{deluxetable}'
        print '\\end{center}'
        
        '''
        print '\end{tabular}'
        print '\caption{{\\bf %s} %s}' % (grbout_dir.split('/')[-1],caption)
        print '\label{%s}' %label
        print '\end{table}'
        print '\end{center}'
        '''
        print '\n'
        pass

    # TABLE 0 GRB General Informations:
    header_variable_format =[(' ',' ','GCNNAME',' %10s ',1),
                             #('YYMMDDFFF',' ','GRBNAME',' %09d ',1),
                             ('DATE',' ','GRBDATE',' %21s ',1),
                             ('GBM Trigger Time','(MET)','GRBMET','%16s',1),
                             #('GBM T$_{05}$','s ','@GBMT05','%5.2f',1),
                             #('GBM T$_{90}$','s ','GBMT90','%5.2f',1),
                             ('R.A.','Deg., J2000','RA',' %9s ',1),
                             ('Dec.','Deg., J2000','DEC',' %9s ',1),
                             ('$\\theta$','Deg.','THETA',' %.1f ',1),                             
                             #('$\zeta$','\de','ZENITH',' %.1f ',1),                             
                             ('Loc. Err.','','ERR','%.2fo',1),
                             ('Like.','','@LIKEDETECTED','%d',1),
                             ('LLE','','@LLEDETECTED','%d',1),
                             #('LLE Significance','$\sigma$ ','LLE_DetMaxSign','%.1f',1)
                             ('Redshift','','REDSHIFT','%.2f',1),
                             ('LAT GCN Number','','GCN','%s',1)
                             ]
    caption='Need to recheck this!. Fermi LAT GRBs in the catalog, from August 2008 to August 2010. Localization errors from: $^{\gamma}$Fermi-LAT, $^{\dagger}$Fermi-GBM, $^{\star}$Swift-XRT/Swift-UVOT. Redshift determination from: $^{a}$ GROND, $^{b}$ Gemini-S, $^{c}$ VLT, $^{d}$ Gemini-N'
    label  ='tab_GRBs' 
    MakeTable(table,grbs_a,header_variable_format,caption,label)
    
    # TABLE 1 DURATION:
    header_variable_format =[(' GRB NAME',' ','GCNNAME','%s',1),
                             #('GBM T$_{05}$','s ','@GBMT05','%.2f',1),
                             #('GBM T$_{95}$','s ','!@GBMT95,GRBT90_ERR','%.2f $\pm$ %.2f',1),
                             ('LAT T$_{05}$','s ','BKGET05,BKGET05-BKGET05L,BKGET05U-BKGET05&LIKEDETECTED','%.2f$_{-%.2f}^{+%.2f}$',1),
                             ('LAT T$_{95}$','s ','BKGET95,BKGET95-BKGET95L,BKGET95U-BKGET95&LIKEDETECTED','%.2f$_{-%.2f}^{+%.2f}$',1),
                             ('LLE T$_{05}$','s ','LLEt05,LLEt05loerr,LLEt05hierr&LLEDETECTED','%.2f$_{-%.2f}^{+%.2f}$',1),                           
                             ('LLE T$_{95}$','s ','LLEt95,LLEt95loerr,LLEt95hierr&LLEDETECTED','%.2f$_{-%.2f}^{+%.2f}$',1),
                             ('Max TS','','LIKEDETECTED_MAXTS','%.1f',1),
                             ('LLE Significance','$\sigma$, Post Trials','LLE_DetPTSigma','%.1f',1),
                             
                             #('LLE Significance 2','$\sigma$ ','LLENSIG','%.1f',1)
                             #('Null Hyp. Prob.','(Post Trials)','@LLE_DetNullHypPTP','%.2e',1)
                             #('Total Significance',' $\sigma$ ','LLEtotalSignificance','%.2f',1)                             
                             ]
    caption='Comparison between duration estimators, for Fermi LAT GRB from August 2008 to August 2011'
    label  ='tab_durations' 
    MakeTable(table,grbs_a,header_variable_format,caption,label,onlyDetected=True)

    # TABLE 1.5 LOCALIZATION:

    header_variable_format =[('GRB NAME',' ','GCNNAME',' %10s ',1),
                             #('R.A.','Deg., J2000','RA',' %9s ',1),
                             #('Dec.','Deg., J2000','DEC',' %9s ',1),
                             #('R.A.(gtfingsrc)','(\de, J2000)','FindSrc_RA1',' %.2f ',1),
                             #('Dec.(gtfingsrc)','(\de, J2000)','FindSrc_DEC1',' %.2f ',1),
                             #('Err.(gtfingsrc)','(\de)','FindSrc_ERR',' %.2f ',1),
                             ('R.A.(gttsmap)','Deg., J2000','TSMAP_RAMAX',' %.2f ',1),
                             ('Dec.(gttsmap)','Deg., J2000','TSMAP_DECMAX',' %.2f ',1),                             
                             ('68\\% (gttsmap)','Deg.','TSMAP_ERR68',' %.2f ',1),                             
                             ('90\\% (gttsmap)','Deg.','TSMAP_ERR90',' %.2f ',1),                             
                             ('95\\% (gttsmap)','Deg.','TSMAP_ERR95',' %.2f ',1),
                             ('TS Max Value (gttsmap)','Deg.','TSMAP_MAX',' %.1f ',1)
                             ]
    caption='Localization estimation for LAT GRBs.'
    label  ='tab_localizations' 
    MakeTable(table,grbs_a,header_variable_format,caption,label,onlyDetected=True)

    
    # TABLE 2 FLUXES, FLUENCES, and INDEXES :    
    header_variable_format =[(' GRB NAME',' ','GCNNAME','%s',1),
                             ('Trans. Ev.','in the ROI','NumberOfEvents100MeV_T_ROI','%d',1),
                             ('Trans. Ev.','in 95\% PSF','NumberOfEvents100MeV_T_ROI_E','%d',1),
                             ('Trans. Ev.','used in likelihood','LIKE_BKGE_NobsTot','%d',1),                             
                             ('Trans. Ev.','Predicted','LIKE_BKGE_Ntot_GRB','%.2f',1),
                             ('Test Statistic','(TS)','LIKE_BKGE_TS_GRB','%.2f',1),
                             ('Spectral Index',' ','LIKE_BKGE_GRBindex,LIKE_BKGE_GRBindex_ERR','%.2f $\pm$ %.2f',1),
                             ('Flux',' ph/cm$^2$/s ($\\times 10^{-5}$)','LIKE_BKGE_FLUX,LIKE_BKGE_FLUX_ERR','%.2f $\pm$ %.2f',1e-5),
                             ('Fluence','erg/cm$^2$ ($\\times 10^{-5}$)','LIKE_BKGE_FLUENCE_ENE,LIKE_BKGE_FLUENCE_ENE_ERR','%.2f $\pm$ %.2f',1e-5),
                             ('E$\\rm_{ISO}$','erg ($\\times 10^{52}$)','LIKE_BKGE_EISO52,LIKE_BKGE_EISO52_ERR','%.1f $\pm$ %.1f',1)
                             ]
    
    caption='Likelihood analysis'
    label  ='tab_likelihoods' 
    #MakeTable(table,grbs_a,header_variable_format,caption,label)

    
    # TABLE 2.5 FLUXES, FLUENCES, and INDEXES In different Bands of time:    
    header_variable_format =[(' GRB NAME',' ','GCNNAME','%s',1),
                             ('Interval (t$_{0}$-t$_{1}$)','s','$@LIKE_GBM_T0,LIKE_GBM_T1',' GBM (%5.1f--%5.1f)',1),
                             #('t$_{1}$','S','@LIKE_GBM_T1','%.1f',1),                                                          
                             ('Trans. Ev.','in the ROI','@LIKE_GBM_NobsTot','%d',1),
                             ('Trans. Ev.','Predicted','LIKE_GBM_Ntot_GRB','%.2f',1),
                             ('Test Statistic','(TS)','LIKE_GBM_TS_GRB','%.2f',1),
                             ('Spectral Index',' ','LIKE_GBM_GRBindex,LIKE_GBM_GRBindex_ERR','%.2f $\pm$ %.2f',1),
                             ('Flux','cm$^{-2}$ s$^{-1}$ ($\\times 10^{-5}$)','LIKE_GBM_FLUX,LIKE_GBM_FLUX_ERR','%.2f $\pm$ %.2f',1e-5),
                             ('Fluence','erg cm$^{-2}$ ($\\times 10^{-5}$)','LIKE_GBM_FLUENCE_ENE,LIKE_GBM_FLUENCE_ENE_ERR','%.2f $\pm$ %.2f',1e-5),
                             ('E$\\rm_{ISO}$','erg ($\\times 10^{52}$)','LIKE_GBM_EISO52,LIKE_GBM_EISO52_ERR','%.1f $\pm$ %.1f',1)]
    
    multiple_raws           =([(' GRB NAME',' ','','',1),
                               ('Interval (t$_{0}$-t$_{1}$)','S','$@LIKE_BKGE_T0,LIKE_BKGE_T1',' LAT (%5.1f--%5.1f)',1),
                               #('t$_{0}$','S','@LIKE_BKGE_T0','%.1f',1),
                               #('t$_{1}$','S','@LIKE_BKGE_T1','%.1f',1),
                               ('Trans. Ev.','in the ROI','@LIKE_BKGE_NobsTot','%d',1),
                               ('Trans. Ev.','Predicted','LIKE_BKGE_Ntot_GRB','%.2f',1),
                               ('Test Statistic','(TS)','LIKE_BKGE_TS_GRB','%.2f',1),
                               ('Spectral Index',' ','LIKE_BKGE_GRBindex,LIKE_BKGE_GRBindex_ERR','%.2f $\pm$ %.2f',1),
                               ('Flux',' ph/cm$^2$/s ($\\times 10^{-5}$)','LIKE_BKGE_FLUX,LIKE_BKGE_FLUX_ERR','%.2f $\pm$ %.2f',1e-5),
                               ('Fluence','erg/cm$^2$ ($\\times 10^{-5}$)','LIKE_BKGE_FLUENCE_ENE,LIKE_BKGE_FLUENCE_ENE_ERR','%.2f $\pm$ %.2f',1e-5),
                               ('E$\\rm_{ISO}$','erg ($\\times 10^{52}$)','LIKE_BKGE_EISO52,LIKE_BKGE_EISO52_ERR','%.1f $\pm$ %.1f',1)],
                              
                              [(' GRB NAME',' ','','',1),
                               ('Interval (t$_{0}$-t$_{1}$)','S','$@LIKE_PRE_T0,LIKE_PRE_T1',' PRE (%5.1f--%5.1f)',1),
                               #('Trans. Ev.','in the ROI','NumberOfEvents100MeV_T_ROI','%d',1),
                               #('Trans. Ev.','in 95\% PSF','NumberOfEvents100MeV_T_ROI_E','%d',1),
                               #('t$_{0}$','S','@LIKE_PRE_T0','%.1f',1),
                               #('t$_{1}$','S','@LIKE_PRE_T1','%.1f',1),                             
                               ('Trans. Ev.','in the ROI','@LIKE_PRE_NobsTot','%d',1),
                               ('Trans. Ev.','Predicted','LIKE_PRE_Ntot_GRB','%.2f',1),
                               ('Test Statistic','(TS)','LIKE_PRE_TS_GRB','%.2f',1),
                               ('Spectral Index',' ','LIKE_PRE_GRBindex,LIKE_PRE_GRBindex_ERR','%.2f $\pm$ %.2f',1),
                               ('Flux',' ph/cm$^2$/s ($\\times 10^{-5}$)','LIKE_PRE_FLUX,LIKE_PRE_FLUX_ERR','%.2f $\pm$ %.2f',1e-5),
                               ('Fluence','erg/cm$^2$ ($\\times 10^{-5}$)','LIKE_PRE_FLUENCE_ENE,LIKE_PRE_FLUENCE_ENE_ERR','%.2f $\pm$ %.2f',1e-5),
                               ('E$\\rm_{ISO}$','erg ($\\times 10^{52}$)','LIKE_PRE_EISO52,LIKE_PRE_EISO52_ERR','%.1f $\pm$ %.1f',1)],

                              [(' GRB NAME',' ','','',1),
                               ('Interval (t$_{0}$-t$_{1}$)','S','$@LIKE_JOINT_T0,LIKE_JOINT_T1',' JOINT (%5.1f--%5.1f)',1),
                               #('t$_{0}$','S','@LIKE_JOINT_T0','%.1f',1),
                               #('t$_{1}$','S','@LIKE_JOINT_T1','%.1f',1),
                               ('Trans. Ev.','in the ROI','@LIKE_JOINT_NobsTot','%d',1),
                               ('Trans. Ev.','Predicted','LIKE_JOINT_Ntot_GRB','%.2f',1),
                               ('Test Statistic','(TS)','LIKE_JOINT_TS_GRB','%.2f',1),
                               ('Spectral Index',' ','LIKE_JOINT_GRBindex,LIKE_JOINT_GRBindex_ERR','%.2f $\pm$ %.2f',1),
                               ('Flux',' ph/cm$^2$/s ($\\times 10^{-5}$)','LIKE_JOINT_FLUX,LIKE_JOINT_FLUX_ERR','%.2f $\pm$ %.2f',1e-5),
                               ('Fluence','erg/cm$^2$ ($\\times 10^{-5}$)','LIKE_JOINT_FLUENCE_ENE,LIKE_JOINT_FLUENCE_ENE_ERR','%.2f $\pm$ %.2f',1e-5),
                               ('E$\\rm_{ISO}$','erg ($\\times 10^{52}$)','LIKE_JOINT_EISO52,LIKE_JOINT_EISO52_ERR','%.1f $\pm$ %.1f',1)],                              

                              [(' GRB NAME',' ','','',1),
                               ('Interval (t$_{0}$-t$_{1}$)','S','$@LIKE_EXT_T0,LIKE_EXT_T1',' EXT (%5.1f--%5.1f)',1),
                               #('t$_{0}$','S','@LIKE_EXT_T0','%.1f',1),
                               #('t$_{1}$','S','@LIKE_EXT_T1','%.1f',1),                           
                               ('Trans. Ev.','in the ROI','@LIKE_EXT_NobsTot','%d',1),
                               ('Trans. Ev.','Predicted','LIKE_EXT_Ntot_GRB','%.2f',1),
                               ('Test Statistic','(TS)','LIKE_EXT_TS_GRB','%.2f',1),
                               ('Spectral Index',' ','LIKE_EXT_GRBindex,LIKE_EXT_GRBindex_ERR','%.2f $\pm$ %.2f',1),
                               ('Flux',' ph/cm$^2$/s ($\\times 10^{-5}$)','LIKE_EXT_FLUX,LIKE_EXT_FLUX_ERR','%.2f $\pm$ %.2f',1e-5),
                               ('Fluence','erg/cm$^2$ ($\\times 10^{-5}$)','LIKE_EXT_FLUENCE_ENE,LIKE_EXT_FLUENCE_ENE_ERR','%.2f $\pm$ %.2f',1e-5),
                               ('E$\\rm_{ISO}$','erg ($\\times 10^{52}$)','LIKE_EXT_EISO52,LIKE_EXT_EISO52_ERR','%.1f $\pm$ %.1f',1)],

                              [(' GRB NAME',' ','','',1),
                               ('Interval (t$_{0}$-t$_{1}$)','S','$@LIKE_AG_T0,LIKE_AG_T1',' AG (%5.1f--%5.1f)',1),
                               #('t$_{0}$','S','@LIKE_AG_T0','%.1f',1),
                               #('t$_{1}$','S','@LIKE_AG_T1','%.1f',1),                           
                               ('Trans. Ev.','in the ROI','@LIKE_AG_NobsTot','%d',1),
                               ('Trans. Ev.','Predicted','LIKE_AG_Ntot_GRB','%.2f',1),
                               ('Test Statistic','(TS)','LIKE_AG_TS_GRB','%.2f',1),
                               ('Spectral Index',' ','LIKE_AG_GRBindex,LIKE_AG_GRBindex_ERR','%.2f $\pm$ %.2f',1),
                               ('Flux',' ph/cm$^2$/s ($\\times 10^{-5}$)','LIKE_AG_FLUX,LIKE_AG_FLUX_ERR','%.2f $\pm$ %.2f',1e-5),
                               ('Fluence','erg/cm$^2$ ($\\times 10^{-5}$)','LIKE_AG_FLUENCE_ENE,LIKE_AG_FLUENCE_ENE_ERR','%.2f $\pm$ %.2f',1e-5),
                               ('E$\\rm_{ISO}$','erg ($\\times 10^{52}$)','LIKE_AG_EISO52,LIKE_AG_EISO52_ERR','%.1f $\pm$ %.1f',1)])
    
    
    caption='Likelihood analysis'
    label  ='tab_likelihoods' 
    MakeTable(table,grbs_a,header_variable_format,caption,label,multiple_raws)

    
    # TABLE 3. PROBABILITY EMAX
    #header_variable_format =[(' GRB NAME',' ','GCNNAME','%s',1),
    #                         ('Energy','(GeV)','PROB_EMAX_E','%.2f',1000),
    #                         ('Arrival time','(sec)','PROB_EMAX_T','%.4f',1),
    #                         ('Probability 1 ','','PROB_EMAX_P1','%.3f',1),
    #                         ('Probability 2','','PROB_EMAX_P2','%.3f',1)]

    #caption='Highest energy event for for Fermi LAT GRB from August 2008 to August 2011'
    #label  ='energymax' 
    #MakeTable(table,grbs_a,header_variable_format,caption,label)
    
    # TABLE 3. PROBABILITY EMAX
    header_variable_format =[(' GRB NAME',' ','GCNNAME','%s',1),
                             ('Number of events','(P$>$0.9)','LIKE_BKGE_gtsrcprob_Nthr','%d',1),
                             ('Energy','(GeV)','$LIKE_BKGE_gtsrcprob_Emax','%.2f',1000),
                             ('Arrival time','(sec)','LIKE_BKGE_gtsrcprob_Tmax','%.2f',1),
                             ('Probability ','','LIKE_BKGE_gtsrcprob_Pmax','%.3f',1)
                             ]

    caption='Highest energy event for for Fermi LAT GRB from August 2008 to August 2011. BKGE Duration'
    label  ='tab_energymax_bkge' 
    MakeTable(table,grbs_a,header_variable_format,caption,label)



    header_variable_format =[(' GRB NAME',' ','GCNNAME','%s',1),
                             ('Number of events','(P$>$0.9)','LIKE_GBM_gtsrcprob_Nthr','%d',1),
                             ('Energy','(GeV)','$LIKE_GBM_gtsrcprob_Emax','%.2f',1000),
                             ('Arrival time','(sec)','LIKE_GBM_gtsrcprob_Tmax','%.2f',1),
                             ('Probability ','','LIKE_GBM_gtsrcprob_Pmax','%.4f',1)]
    
    caption='Highest energy event for for Fermi LAT GRB from August 2008 to August 2011. GBM Duration.'
    label  ='tab_energymax_gbm' 
    MakeTable(table,grbs_a,header_variable_format,caption,label)
    

    header_variable_format =[(' GRB NAME',' ','GCNNAME','%s',1),
                             ('Number of events','(P$>$0.9)','LIKE_EXT_gtsrcprob_Nthr','%d',1),
                             ('Energy','(GeV)','$LIKE_EXT_gtsrcprob_Emax','%.2f',1000),
                             ('Arrival time','(sec)','LIKE_EXT_gtsrcprob_Tmax','%.2f',1),
                             ('Probability ','','LIKE_EXT_gtsrcprob_Pmax','%.3f',1)
                             ]

    caption='Highest energy event for for Fermi LAT GRB from August 2008 to August 2011. EXT Duration'
    label  ='tab_energymax_ext' 
    MakeTable(table,grbs_a,header_variable_format,caption,label)


    header_variable_format =[(' GRB NAME',' ','GCNNAME','%s',1),
                             ('Number of events','(P$>$0.9)','gtsrcprob_ExtendedEmission_NTH','%d',1),
                             ('Energy','(GeV)','gtsrcprob_ExtendedEmission_MAXE','%.2f',1000),
                             ('Arrival time','(sec)','gtsrcprob_ExtendedEmission_MAXE_T','%.2f',1),
                             ('Probability ','','gtsrcprob_ExtendedEmission_MAXE_P','%.3f',1)
                             ]

    caption='Highest energy event for for Fermi LAT GRB from August 2008 to August 2011. The probability has been estimated using gtsrcprob in different time bin.'
    label  ='tab_energymax_all' 
    MakeTable(table,grbs_a,header_variable_format,caption,label)



    # TABLE 3. PROBABILITY FIRST EVENT
    #header_variable_format =[(' GRB NAME',' ','GCNNAME','%s',1),
    #                         ('Energy','(GeV)','PROB_FIRST_E','%.2f',1000),
    #                         ('Arrival time','(sec)','PROB_FIRST_T','%.4f',1),
    #                         ('Probability 1 ',' ','PROB_FIRST_P1','%.3f',1),
    #                         ('Probability 2',' ','PROB_FIRST_P2','%.3f',1)]
    #caption='First event after the time of the trigger'
    #label  ='firstevent' 
    #MakeTable(table,grbs_a,header_variable_format,caption,label)

    # TABLE 3. PROBABILITY LAST EVENT
    #header_variable_format =[(' GRB NAME',' ','GCNNAME','%s',1),
    #                         ('Energy','(GeV)','PROB_LAST_E','%.2f',1000),
    #                         ('Arrival time','(sec)','PROB_LAST_T','%.4f',1),
    #                         ('Probability 1 ',' ','PROB_LAST_P1','%.3f',1),
    #                         ('Probability 2',' ','PROB_LAST_P2','%.3f',1)]
    #caption='Last event after the trigger'
    #label  ='lastevent' 
    #MakeTable(table,grbs_a,header_variable_format,caption,label)

    # TABLE PEAK FLUX
    header_variable_format =[(' GRB NAME',' ','GCNNAME','%s',1),
                             ('Peak Flux','cm$^{-2}$ s$^{-1}$ ($\\times 10^{-5}$)','$PeakFlux,PeakFlux_ERR','%.2f $\pm$ %.2f',1e-5),
                             ('PeakFlux Time','(sec)','PeakFlux_Time,PeakFlux_Time_ERR ','%.2f $\pm$ %.2f',1),
                             ('Decay Index',' ','AG_IN,AG_IN_ERR','%.2f $\pm$ %.2f',1),
                             ('Extended Emission Duration',' s ($\\times 10^{3}$)','AG_DUR,AG_DUR_ERR','%.1f $\pm$ %.1f',1e3)]
    caption='Temporally extended high energy emission'
    label  ='tab_extended' 
    MakeTable(table,grbs_a,header_variable_format,caption,label)



    # Summary Table:
    #header_variable_format =[('GRB NAME',' ','GCNNAME','%s',1),
    #                         ('Theta','Deg.','THETA','%.1f',1.0),
    #                         ('LLE Sig.','','LLENSIG','%.1f',1.0),
    #                         ('LLE Sig.','','LLE_DetMaxSign','%.1f',1.0),
    #                         ('Test Statistic','','@max(LIKE_GBM_TS_GRB,LIKE_BKGE_TS_GRB,LIKE_PRE_TS_GRB,LIKE_JOINT_TS_GRB,LIKE_AG_TS_GRB,LIKE_EXT_TS_GRB)','%d',1.0),
    #                         ('N Pred. Events $>$ 100MeV','(LAT duration)','LIKE_BKGE_Ntot_GRB','%d',1),
    #                         #('N Events',' GBM','LIKE_GBM_Ntot_GRB','%d',1),                             
    #                         ('LAT T$_{05}$','(s) ','BKGET05,BKGET05-BKGET05L,BKGET05U-BKGET05','%.2f$_{-%.2f}^{+%.2f}$',1),
    #                         ('LAT T$_{95}$','(s) ','BKGET95,BKGET95-BKGET95L,BKGET95U-BKGET95','%.2f$_{-%.2f}^{+%.2f}$',1),
    #                         ('GBM T90','(s)','GBMT90','%.2f',1.0),
    #                         #('Extra comp','(ks)','AG_DUR','%.1f',1000.0),
    #                         ('Energy Max','GeV','PROB_EMAX_E','%.1f',1.0e3),
    #                         ('Redshift','','REDSHIFT','%10s',1)]
    #
    #caption='Temporal extended high energy emission'
    #label  ='tab_summary'
    #MakeTable(table,grbs_a,header_variable_format,caption,label)


    # TABLE 0 GRB Summary Detection Table Informations:
    header_variable_format =[(' ',' ','GCNNAME',' %10s ',1),
                             ('YYMMDDFFF',' ','GRBNAME',' %09d ',1),
                             ('DATE',' ','GRBDATE',' %21s ',1),
                             ('GBM Trigger Time','(MET)','GRBMET','%16s',1),
                             ('GBM T$_{05}$','s ','@GBMT05','%5.2f',1),
                             ('GBM T$_{90}$','s ','@GBMT90','%5.2f',1),
                             ('R.A.','Deg., J2000','RA',' %.3f ',1),
                             ('Dec.','Deg., J2000','DEC',' %.3f ',1),
                             ('$\\theta$','Deg.','THETA',' %.1f ',1),                             
                             ('$\zeta$','\de','ZENITH',' %.1f ',1),                             
                             ('Like Detected','','@LIKEDETECTED','%d',1),
                             ('LLE DetMaxSign','','@LLEDETECTED,LLE_DetMaxSign','%d (%.1f)',1),
                             ('LLENSIG','','@LLEDETECTED2,LLENSIG','%d (%.1f)',1)
                             ]
    caption='Summary Detection Table.'
    label  ='tab_summary_detection' 
    MakeTable(table,grbs_a,header_variable_format,caption,label)
    
    ##################################################
    print '---- Code for Spectral Analysis:'
    import numpy as num
    from pyfits import Column, HDUList, PrimaryHDU, new_table


    a_gcn_names = []
    a_gbmt05    = []
    a_gbmt95    = []
    a_bkget05   = []
    a_bkget95   = []
    
    '''
    if 'BKGET95' in table[g]:
        txt='params={'
        for g in grbs_a:
            txt+='\t\'%s\':[%7.3f,%7.3f,%7.3f,%7.3f],\n' %(table[g]['GCNNAME'],
                                                           float(table[g]['GBMT05']),
                                                           float(table[g]['BKGET05']),
                                                           float(table[g]['GBMT95']),
                                                           float(table[g]['BKGET95']))
            a_gcn_names.append(table[g]['GCNNAME'])
            a_gbmt05.append(float(table[g]['GBMT05'])) 
            a_gbmt95.append(float(table[g]['GBMT95']) )
            a_bkget05.append(float(table[g]['BKGET05']))
            a_bkget95.append(float(table[g]['BKGET95']))            
            pass
        print txt,'}'
        pass
    '''
    C_gcn_names      = Column(name="gcn_names", format="10A", array=num.array(a_gcn_names))
    C_gbmt05         = Column(name="GBMT05",    format="F",   array=num.array(a_gbmt05),unit='s')
    C_gbmt95         = Column(name="GBMT95",    format="F",   array=num.array(a_gbmt95),unit='s')
    C_bkget05        = Column(name="BKGET05",   format="F",   array=num.array(a_bkget05),unit='s')
    C_bkget95        = Column(name="BKGET95",   format="F",   array=num.array(a_bkget95),unit='s')

    columns = [C_gcn_names,C_gbmt05,C_gbmt95,C_bkget05,C_bkget95]
    prim    = PrimaryHDU()

    import time
    ttupla=time.gmtime()
    yyyy=ttupla[0]
    mm=ttupla[1]
    dd=ttupla[2]
    hh=ttupla[3]
    mi=ttupla[4]
    se=ttupla[5]
    
    fileName = grbout_dir+'/SpectralIntervals.fits'
    
    timeString='%i-%02i-%02iT%02i:%02i:%06.3f' % (yyyy,mm,dd,hh,mi,se)
    prim.header.update('DATE',timeString,comment='Date file was made in YYYY-MM-DD')
    prim.header.update('FILENAME',fileName,comment='File name')
    prim.header.update('GRBOUTDI',grbout_dir,comment='Input Catalog File')
    prim.header.update('TELESCOP','FERMI',comment='Name of the mission')
    prim.header.update('INSTRUME','LAT',comment='Name of instrument generating data')
    prim.header.update('OBSERVER','MICHELSON',comment='Instrument PI')
    prim.header.update('CREATOR','GRBAnalysis',comment='Software creating file')
    
    
    output  = HDUList()
    
    output.append(prim)
    output.append(new_table(columns))
    output[1].name = 'SPECRAL_INTERVALS'
    ext1hdr=output[1]
    ext1hdr.header.update('DATE',timeString,comment='Date file was made in YYYY-MM-DD')
    ext1hdr.header.update('FILENAME',fileName,comment='File name')
    ext1hdr.header.update('GRBOUTDI',grbout_dir,comment='Input Catalog File')
    ext1hdr.header.update('TELESCOP','FERMI',comment='Name of the mission')
    ext1hdr.header.update('INSTRUME','LAT',comment='Name of instrument generating data')
    ext1hdr.header.update('OBSERVER','MICHELSON',comment='Instrument PI')
    ext1hdr.header.update('CREATOR','GRBAnalysis',comment='Software creating file')
    output.verify()
    output.writeto(fileName, clobber=True)
    
    print '---- Code for LLE generation:'
    txt='GRBs={'
    for g in grbs_a:
        txt+='\t\'%s\':[%7.3f,%17.6f,%7.3f,%7.3f, %.1f,%.1f,%.1f,%.1f,%.1f],\n' %(table[g]['GCNNAME'],
                                                                                  float(table[g]['GBMT95']),
                                                                                  float(table[g]['GRBMET']),
                                                                                  float(table[g]['RA']),
                                                                                  float(table[g]['DEC']),0.0,1.0,-1.0,100,80)
        pass
    print txt,'}'
    
    
    print '---- Code for GRB Dictionary:'
    txt='GRBs={'
    for g in grbs_a:
        #if float(table[g]['TSMAP_ERR68'])<float(table[g]['ERR']):
        #    newra  = float(table[g]['TSMAP_RAMAX'])
        #    newdec = float(table[g]['TSMAP_DECMAX'])
        
        txt+=""" '%s\':{'RA':%.2f,
        'DEC': %.4f,
                 'ERR': %.4f,
                 'GRBT05': %.2f,
                 'GRBT90': %.2f,
                 'GRBTRIGGERDATE': %.4f,
                 'REDSHIFT': %.3f},\n""" %(table[g]['GCNNAME'],
                                           float(table[g]['RA']),
                                           float(table[g]['DEC']),
                                           float(table[g]['ERR']),
                                           float(table[g]['GBMT05']),
                                           float(table[g]['GBMT95']),
                                           float(table[g]['GRBMET']),
                                           float(table[g]['REDSHIFT']))
        pass
    print txt,'}'
    
    print '---- Code for BKGE Dictionary:'
    txt='BKGE = {'
    for g in grbs_a:
        txt+="'%s\':{\'BKGET05\':%.2f,\'BKGET05L\':%.2f,\'BKGET05U\':%.2f," %(table[g]['GCNNAME'],
                                                                              float(table[g]['BKGET05']),
                                                                              float(table[g]['BKGET05L']),
                                                                              float(table[g]['BKGET05U']))
        
        txt+="\'BKGET90\':%.2f,\'BKGET90L\':%.2f,\'BKGET90U\':%.2f," % (float(table[g]['BKGET90']),
                                                                        float(table[g]['BKGET90L']),
                                                                        float(table[g]['BKGET90U']))
        
        
        txt+="\'BKGET95\':%.2f,\'BKGET95L\':%.2f,\'BKGET95U\':%.2f},\n\t" % (float(table[g]['BKGET95']),
                                                                             float(table[g]['BKGET95L']),
                                                                             float(table[g]['BKGET95U']))
        pass
    print txt[:-1],'}'
    pass

