#!/usr/bin/env python
import os, sys, math
import astropy.io.fits as pyfits
import glob
from GTGRB import *
from GTGRB.genutils import runShellCommand
from LikelihoodState import LikelihoodState
import LikelihoodProfileFit          
import numpy as np  

_switch_irf = 100000.0
MeV2erg     = 1.60217646e-6
NumberOfDOF = 2
StepSize    = 1
ExpCutOffModelUsed=["ExpCutoff","Index","P1"]
#ExpCutOffModelUsed=["PLSuperExpCutoff","Index1","Cutoff"]
CL=float(os.getenv('ULCL', 0.95))
'''freeParValues = []
>>> for sourcename in like.sourceNames():
>>>    for element in like.freePars(sourcename):
>>>       freeParValues.append(element.getValue())
>>>
>>> g_index = freeParValues.index(like.freePars('4FGL J1555.7+1111')[1].getValue())
>>> cov_gg = like.covariance[g_index][g_index]
'''


def getCovariance(like):
    cov = like.covariance
    N   = len(cov)
    par_cov={}
    
    #freePars=[]
    i=0
    for sourcename in like.sourceNames():
        for element in like.freePars(sourcename):
            if 'GRB' in sourcename:
                x=[]
                n = element.getName()
                v = element.getValue()
                e = element.error()
                s = element.getScale()  
                x.append(n)
                x.append(v)
                x.append(e)
                x.append(s)
                print i,n,v,e,s,'|',
                for j in range(N):
                    x.append(cov[i][j])
                    print cov[i][j],            
                    pass
                print ''
                par_cov[i]=x
                pass
            i+=1
            pass
        pass
    print par_cov
    return par_cov


def _findFirst(mylist, elem):
    ''' This method return the position of the first element
    of the list after elem'''
    for i,l in enumerate(mylist):
        if l > elem:
            return i
        pass
    return len(mylist)-1


def _median(a):
    ''' Compute the median of a list of numbers '''
    n=len(a)
    
    if n==0: median =0
    elif (n % 2)==0: median = (a[n/2]+a[n/2-1])/2
    else: median=(a[(n+1)/2-1])
    print ' compute the median - n= %d, median=%f' %(n,median)
    return median

def removeFiles(files):
    for f in files:
        print '-- Removing: %s' % f
        runShellCommand('rm -rf %s' % f)
        pass
    pass
    
def sourceInXml(xmlfile,src):
    print '...checking src %s in file %s...'  %(src,xmlfile)
    for l in file(xmlfile,'r').readlines():
        if src in l.strip():            
            return True
        pass
    print '...not found.'
    return False


def MakeXMLModel(lat, src_filePath, bkg_filePath, like_model,t1=0,t2=0,chatter=2,AppendSourceList="",grb_model="PowerLaw2"):
    irfs = lat._ResponseFunction
    if chatter>1: print 'MakeXMLModel : %s' % like_model
    diffuseModel=False
    latutils.CreateSource_XML(src_filePath)    
    like_model_comps=like_model.split("+") #tokenize    
    for i in range(0,len(like_model_comps)): #convert to UL
	like_model_comps[i]=like_model_comps[i].upper()
        pass
    
    resetMinimumTs=False
    if len(like_model_comps)==1: resetMinimumTs=True
    
    #check if all passed model are ok
    accepted_model_comps=['PREFIT','GRB','GRBEXP','GRBEBL','SRC','ISO','TEM','GAL','GAL0','BKGE_GAL_GAMMAS','BKGE_CR_EGAL','BKGE_TOTAL','2FGL']
    for amodel in like_model_comps:
	if(amodel.find("SRC")>=0):
            continue
        if not amodel in accepted_model_comps:
	    print "Model component '%s' is not recognized. Please use the following models %s" %(amodel,accepted_model_comps)
	    return "error"
        pass

    if 'PREFIT' in like_model_comps:
        latutils.SetFromTemplate_XML(xmlFileName=src_filePath,template=bkg_filePath,fixed=True)
        latutils.write_xmlModel(model=grb_model,xmlFileName=src_filePath,ra=lat.GRB.ra,dec=lat.GRB.dec,Integral=1e-5, Index=-2.2)
        latutils.Close_XML(src_filePath)
        diffuseModel=True
        return diffuseModel,resetMinimumTs
    
    if 'GRB' in like_model_comps:
        if grb_model=="PowerLaw2":
            result=latutils.write_xmlModel(model="PowerLaw2",xmlFileName=src_filePath,ra=lat.GRB.ra,dec=lat.GRB.dec,Integral=1e-5, Index=-2.2)
        else: 
            result=latutils.write_xmlModel(model=grb_model,xmlFileName=src_filePath,ra=lat.GRB.ra,dec=lat.GRB.dec)
        if result=="error": return "error"
        pass
    elif 'GRBEXP' in like_model_comps:
        EXPO_MODEL=os.getenv('EXPO_MODEL','SUN')
        print 'EXPO_MODEL=',EXPO_MODEL
        if EXPO_MODEL=='SUN':
            Index          = 0.0
            Index_free     = 1
            Ebreak         = 0.1
            Ebreak_free    = 0
            P1             = 300.0
            P1_free        = 1
            P2             = 0.0
            P2_free        = 0 
            P3             = 0.0
            P3_free        = 0
        elif EXPO_MODEL=='SNALP':
            Index          = 2.3
            Index_free     = 0
            Ebreak         = 0.1
            Ebreak_free    = 0
            P1             = 30.0
            P1_free        = 0
            P2             = 0.0
            P2_free        = 0 
            P3             = 0.0
            P3_free        = 0
            pass
        
        result=latutils.write_xmlModel(model=ExpCutOffModelUsed[0],
                                       xmlFileName=src_filePath,
                                       ra=lat.GRB.ra,dec=lat.GRB.dec,
                                       Index            = Index,
                                       Index_free       = Index_free,
                                       Ebreak           = Ebreak,
                                       Ebreak_free      = Ebreak_free,
                                       P1               = P1,
                                       P1_free          = P1_free,
                                       P2               = P2,
                                       P2_free          = P2_free,  
                                       P3               = P3,
                                       P3_free          = P3_free)
        
        
        
        if result=="error": return "error"        
        pass
    elif 'GRBEBL' in like_model_comps:
        result=latutils.write_xmlModel(model="EblAtten::PowerLaw2",
                                       xmlFileName=src_filePath,
                                       ra=lat.GRB.ra,dec=lat.GRB.dec,
                                       Integral=1e-5, Index=-2.2,redshift=lat.GRB.redshift)
        if result=="error": return "error"
        pass
    
    # This ADD A SOURCE with a powerlaw index of -2.24    
    if like_model.find("SRC")>=0:  
        #This will be a list like [['ra','dec','index'],['ra','dec','index']...] depending on the number of sources
        tokenLists = map(lambda x:x.split('(')[1].split(')')[0].split(','),like_model.split('SRC')[1:])                  
        src_idx  = -2.14
        src_flux = 2.7e-6
        free=1
        for i,sourceTokens in enumerate(tokenLists):
            src_ra    = float(sourceTokens[0])
            src_dec   = float(sourceTokens[1])
            try:
                src_idx   = float(sourceTokens[2])
                free=0
            except:                pass
            try:
                src_flux = float(sourceTokens[3])
                free=0
            except: pass
            
            latutils.write_xmlModel(model="PowerLaw2",xmlFileName=src_filePath,name="SRC%s" %i, 
                                    ra=src_ra,dec=src_dec,
                                    Integral=src_flux, Index=src_idx,
                                    LowerLimit=100.,UpperLimit=100000.,free=free)
            pass
        pass

    
    if 'ISO' in like_model_comps:
        latutils.Add_IsoPower_XML(xmlFileName=src_filePath)
        diffuseModel=True
        pass
    
    if 'TEM' in like_model_comps:
        isoTemplate_string='ISODIFFUSE'
        isoTemplate = os.environ[isoTemplate_string]
        latutils.Add_IsoTemplate_XML(xmlFileName=src_filePath,template=isoTemplate,vary=10,pmean=1)
        diffuseModel=True
        pass
    
    if 'GAL0' in like_model_comps:
        galTemplate = os.environ['GALDIFFUSE']
        #if 'P7' in irfs: galTemplate = os.environ['GALDIFFUSE_P7']
        latutils.Add_GalacticDiffuseComponent_XML(xmlFileName=src_filePath, template=galTemplate,free=0)
        diffuseModel=True
        pass
    elif 'GAL' in like_model_comps:
        galTemplate = os.environ['GALDIFFUSE']
        #if 'P7' in irfs: galTemplate = os.environ['GALDIFFUSE_P7']
        latutils.Add_GalacticDiffuseComponent_XML(xmlFileName=src_filePath, template=galTemplate,free=1)
        diffuseModel=True
        pass
    
    #if 'BKGE_MAP_CR_EGAL' in like_model_comps:
    #    if "BKGE_CR_EGAL" in like_model_comps:
    #       print "Do not use BKGE_MAP_CR_EGAL and BKGE_CR_EGAL together"
    #       return "error"
    #    UseBKGE=True
    #    bkge_map_filename=BKGE_Tools.MakeGtLikeMap(lat,start=t1,stop=t2,AddResidual=False,chatter=1)
    #    latutils.Add_GalacticDiffuseComponent_XML(xmlFileName=src_filePath, template=bkge_map_filename,ModelName="BKGE_MAP_CR_EGAL")
    #    diffuseModel=True
    #    pass

    UseBKGE=False
    if 'BKGE_GAL_GAMMAS' in like_model_comps or 'BKGE_CR_EGAL' in like_model_comps or 'BKGE_TOTAL' in like_model_comps:
	UseBKGE=True
	#some cross checks first
        if 'BKGE_TOTAL' in like_model_comps:
	    if 'GAL' in like_model_comps or 'ISO' in like_model_comps or 'SRC' in like_model_comps:
	        print "BKGE_TOTAL should be used by itself!"
		return "error"
	    pass
        if ('BKGE_CR_EGAL' in like_model_comps or 'BKGE_GAL_GAMMAS' in like_model_comps) and "DIFFUSE" in lat._ResponseFunction.upper():
	    print "Do not use BKGE_CR_EGAL or BKGE_GAL_GAMMAS models with the diffuse class. Use just BKGE_TOTAL."
	    return "error"
        
        if ('BKGE_TOTAL' not in like_model_comps) and ('BKGE_CR_EGAL' not in like_model_comps) and ('BKGE_GAL_GAMMAS' not in like_model_comps) :
	    print "Use BKGE_TOTAL, BKGE_CR_EGAL, or BKGE_GAL_GAMMAS for the bkge-provided template. Just BKGE is deprecated"
	    return "error"
        ##################################################
        # THIS CALL THE BACKGROUND ESTIMATOR
        import BKGE_interface
        BKGE_interface.setResponseFunction(lat._ResponseFunction)
        try:    bkge_chatter=int(os.environ['BKGE_CHATTER'])
        except: bkge_chatter=3

        BKGE_interface.MakeGtLikeTemplate(start=t1, stop=t2,
                                          grb_trigger_time=lat.GRB.Ttrigger,
                                          RA=lat.GRB.ra, DEC=lat.GRB.dec,
                                          FT1=lat.FilenameFT1,
                                          FT2=lat.FilenameFT2,
                                          OUTPUT_DIR=lat.out_dir,
                                          chatter= bkge_chatter,
                                          ROI_Radius=lat.radius,
                                          GRB_NAME=lat.GRB.Name)
            
            #BKGE_Tools.MakeGtLikeTemplate(lat,start=t1,stop=t2)        
        ##################################################
	if 'BKGE_TOTAL' in like_model_comps:
	    model_bkg  = lat.out_dir+'/Bkg_Estimates/%.2f_%.2f/%s_gtlike_%s_TOTAL.txt' %(t1,t2,lat._ResponseFunction,lat.GRB.Name)
	    BKGE_Model="BKGE_TOTAL"
            latutils.Add_IsoTemplate_XML(xmlFileName = src_filePath,
                                         template = model_bkg,component_name=BKGE_Model)
            pass
        if 'BKGE_GAL_GAMMAS' in like_model_comps:
	    model_bkg  = lat.out_dir+'/Bkg_Estimates/%.2f_%.2f/%s_gtlike_%s_GALGAMMAS.txt' %(t1,t2,lat._ResponseFunction,lat.GRB.Name)
	    BKGE_Model="BKGE_GAL_GAMMAS"
            latutils.Add_IsoTemplate_XML(xmlFileName = src_filePath,
                                     template = model_bkg,component_name=BKGE_Model)
            pass
        if 'BKGE_CR_EGAL' in like_model_comps:
            model_bkg  = lat.out_dir+'/Bkg_Estimates/%.2f_%.2f/%s_gtlike_%s_CR_EGAL.txt' %(t1,t2,lat._ResponseFunction,lat.GRB.Name)
            BKGE_Model="BKGE_CR_EGAL"
            latutils.Add_IsoTemplate_XML(xmlFileName = src_filePath,
                                         template = model_bkg,component_name=BKGE_Model)
            pass
        diffuseModel=True
        pass
    
    if '2FGL' in like_model_comps:
        awfulTrickName            = os.path.join(os.path.dirname(src_filePath),'fgl_pointSources.xml')    
        #from scripts import make2FGLxml
        from scripts import make3FGLxml
        FERMISOURCECATALOG=os.environ['FERMISOURCECATALOG']    
        print 'ADDING THE 3FGL POINT SOURCES FROM: %s' % FERMISOURCECATALOG        
        mymodel=make3FGLxml.srcList(FERMISOURCECATALOG,lat.evt_file,awfulTrickName)
        mymodel.makeModel(radLim=0.001,psForce=True,sigFree=4.0,Exposure=t2-t1)
        if(os.path.exists(awfulTrickName)):
            AppendSourceList        = awfulTrickName
            print("\nAdding point sources from %s file..." %(awfulTrickName))
            pass
        if AppendSourceList!="":
            source_list=open(AppendSourceList,"r")
            sources=filter(lambda x:x.find("<?xml")<0 and x.find('source_library')<0,source_list.readlines())
            xml_file=open(src_filePath,"a")
            xml_file.writelines(sources)
            xml_file.close()
            source_list.close()
            pass
        pass
    
    latutils.Close_XML(src_filePath)
        
    if chatter>1: 
	print '----------------------------------------------------------------------------'
	print ' -- Likelihood Model: %s ' % like_model
	print ' -- Model XML file  : %s ' % src_filePath
	if diffuseModel: print ' -- The diffuse response will be computed.'
	print '----------------------------------------------------------------------------'
        pass
    if UseBKGE:        
	return  diffuseModel,0
    else: 
	return diffuseModel,resetMinimumTs
    pass


def MakeFullLikelihood(lat, bkg_filePath, like_model, t1, t2, results, ts_min, 
                       prefix='LIKE', FIXING=1,gtsrcprob=1, mode='ql',chatter=2,
                       **kwargs):
    #Region which will be used for the computation of the exposure map (must be greater than the ROI)
    expomapradius             = lat.radius+10.0 
    for key in kwargs.keys():
        if    key.lower()=="expomapradius":         expomapradius       = float(kwargs[key])
        
    ts_min = float(ts_min)
    ##################################################
    # 1) DEFINING SOME USEFUL VARIABLES:
    ##################################################
    overwrite=False            
    if mode=='go':
        overwrite=True
        pass
    
    evt_file              = '%s/%s_events_%s_%.3f_%.3f.fits' %(lat.out_dir,lat.GRB.Name,prefix,t1,t2)
    EXP_CUBE_SRC          = '%s/%s_ltcube_%s_%.3f_%.3f.fits' %(lat.out_dir,lat.GRB.Name,prefix,t1,t2)
    EXP_MAP_SRC           = '%s/%s_expmap_%s_%.3f_%.3f.fits' %(lat.out_dir,lat.GRB.Name,prefix,t1,t2)
    src_filePath          = '%s/%s_model_%s_%.3f_%.3f.xml'   %(lat.out_dir,lat.GRB.Name,prefix,t1,t2)
    count_spectra         = '%s/%s_counts_%s_%.3f_%.3f.fits' %(lat.out_dir,lat.GRB.Name,prefix,t1,t2)
    gtsrc_probabilities   = '%s/%s_gtsrcprob_%s_%.3f_%.3f.fits' %(lat.out_dir,lat.GRB.Name,prefix,t1,t2)
    
    ##################################################
    if chatter>1:
        print '=============================================================================================='        
        DeltaT = t2-t1
        print ' MakeFullLikelihood: [%s]: Fitting between: %.2f, and %.2f (%.3f)' %(prefix, t1,t2,DeltaT)
        
    # #################################################
    # This set the time selection just to the region of the burst:
    #t01       = lat.GRB.TStart
    #t02       = lat.GRB.TStop
    #evt_file0 = lat.evt_file
    
    lat.evt_file = evt_file
    lat.setTmin(lat.GRB.Ttrigger + t1)
    lat.setTmax(lat.GRB.Ttrigger + t2)
    nevents = lat.make_select()
    
    if nevents == 0:  return 0
    ##################################################
    # 2) Building the model:                  #
    ##################################################
    # This create the XML file
    resetMinimumTs=False
    result = MakeXMLModel(lat, src_filePath, bkg_filePath, like_model,t1,t2)
    if result == "error":
        print 'Error from XML model...'
        return None
    
    if 'BKGE' in like_model:	diffuseModel,bkge_comp_stat_err = result
    else:                       diffuseModel,resetMinimumTs = result        
    
    if(diffuseModel):
        #try:
        if(not EXP_CUBE_SRC=='none'):
            lat.make_expCube(outfile=EXP_CUBE_SRC, overwrite = overwrite)
            pass
        lat.make_expMap(expcube=EXP_CUBE_SRC,outfile=EXP_MAP_SRC,overwrite = overwrite,srcrad=expomapradius)
        lat.make_gtdiffrsp(srcmdl=src_filePath)
        #except:
        #    print '===================================================================================================='
        #    print '===== Expcube, Expmap, or diffresp failed...                                                   ====='
        #    print '===================================================================================================='
        #    return None
        pass
    # #################################################
    #try:
    like    = lat.pyLike(model=src_filePath,expmap=EXP_MAP_SRC,expcube=EXP_CUBE_SRC,fixing=FIXING)
    #try:
    try: use_prior    = int(os.environ['GTGRB_USE_PRIOR'])
    except: use_prior = 1
    print 'use_prior=',use_prior
    if "BKGE_CR_EGAL" in like_model: #constrain the BKGE normalization by applying a Gaussian prior
        bkge_sys_err=0.15
        #find index of BKGE component
        for idx in range(len(like.model.srcNames)): 
            if like.model.srcNames[idx]=='BKGE_CR_EGAL' :
                like[idx].addGaussianPrior(1,bkge_sys_err)
                print "Constrained BKGE_CR_EGAL component's normalization using a %f width gaussian" % bkge_sys_err
                pass
            pass
        pass
    if "TEM" in like_model and use_prior: #constrain the TEM normalization by applying a Gaussian prior #CMMENTED ON JAN 19 2016                
        for idx in range(len(like.model.srcNames)):
            print idx,like.model.srcNames[idx]
            if 'EG' in like.model.srcNames[idx]:
                like[idx].addGaussianPrior(1.0,1.0)
                print 'Added a gaussian prior to the %s component!' % like.model.srcNames[idx]
                break
            pass
        pass
    
    try:
        logLike = like.fit(covar=True)
    except:
        print '===================================================================================================='
        print ' LIKELIHOOD FIT RETURN AN ERROR. POSSIBLE CAUSE ARE : N EVENTS < NDOF'
        print '===================================================================================================='
        return None
    like.writeXml(xmlFile=src_filePath)
    par_cov  = getCovariance(like)
    results['%s_par_cov' % prefix]=str(par_cov) # this can be read with from ast import literal_eval, d=literal_eval(par_cov) 
    print dir(like)
    try: 
        Exposure = lat.make_exposure(xmlFile=src_filePath)    
        print ' ==> EXPOSURE = ',Exposure,' cm^2 s'    
    except:
        print ' ==> ERROR IN CALCULATING THE EXPOSURE!!! <=='
        Exposure = 0
        pass
    NobsTot = like.nobs.sum()    
    try: like.writeCountsSpectra(count_spectra)
    except: print '%%%%%%%%%%%%%%%%%%% FAILED TO WRITE THE COUNT SPETCRUM !! %%%%%%%%%%%%%%%%%%%%'
    if chatter>1: print like.model    
    
    results['%s_src_filePath' % prefix]   = src_filePath
    results['%s_evt_file'     % prefix]   = evt_file
    results['%s_expmap'       % prefix]   = EXP_MAP_SRC
    results['%s_expcube'      % prefix]   = EXP_CUBE_SRC
    results['%s_logLike'      % prefix]   = logLike
    results['%s_NobsTot'      % prefix]   = NobsTot
    results['%s_count_spectra'% prefix]   = count_spectra

    sourceNames = like.sourceNames()
    for srcN in sourceNames:
        Ts      = like.Ts(srcN,reoptimize=False)
        #emin = max(100.  ,float(results['EMIN']))
        #emax = min(10000.,float(results['EMAX']))
        emin = float(results['FEMIN'])
        emax = float(results['FEMAX'])
        
        try:    Npred_100_1000   = like[srcN].src.Npred(100,1000)
        except: Npred_100_1000   = 0
        
        try:  Npred_1000_10000   = like[srcN].src.Npred(1000,10000)
        except: Npred_1000_10000 = 0
        
        try: Npred_Emin_Emax     = like[srcN].src.Npred(emin,emax)
        except: Npred_Emin_Emax  = -1
        if chatter>1 and (srcN[0] != '_' or Ts > 9):
            print 'TS                        (%s)     = %.2f' % (srcN,Ts)
            print 'N Predicted [100 MeV -  1 GeV] from %s = %s ' % (srcN,Npred_100_1000) 
            print 'N Predicted [1 GeV   - 10 GeV] from %s = %s ' % (srcN, Npred_1000_10000)         
            print 'N Predicted [%s - %s MeV] from %s = %s ' % (emin,emax,srcN,Npred_Emin_Emax)
            print '..................................................'
            pass
        if srcN[0] != '_':
            results['%s_TS_%s' % (prefix,srcN)]  = Ts
            results['%s_N23_%s'% (prefix,srcN)]  = Npred_100_1000
            results['%s_N34_%s'% (prefix,srcN)]  = Npred_1000_10000
            results['%s_Ntot_%s'% (prefix,srcN)] = Npred_Emin_Emax
            pass
        pass
    if chatter>1:
        print ' N Observed (%s - %s) MeV  = %i ' % (float(results['EMIN']),float(results['EMAX']),NobsTot)
        print ' logLikelihood             = %s ' % (logLike)
        pass
    
    if 'GRBEXP' in like_model:
        index     = like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[1]).getValue()
        index_err = like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[1]).error()
        cutoff    = like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[2]).getValue()
        cutoff_err= like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[2]).error()
        pass
    else:
        index     = like['GRB'].src.spectrum().parameter('Index').getValue()
        index_err = like['GRB'].src.spectrum().parameter('Index').error()
        cutoff    = 0
        cutoff_err= 0
        pass
    # Get the value of the normalization of the isotropic background:
    if 'TEM' in like_model: results['%s_NORM_EG'% (prefix)]=like['EG_v02'].src.spectrum().parameter('Normalization').getValue()
    
    try:
        like.plot()
        like.plotSource('GRB','red')
        like.residualPlot.canvas.Print('%s/%s_residualPlot.png' % (lat.out_dir,prefix))
        like.spectralPlot.canvas.Print('%s/%s_spectralPlot.png' % (lat.out_dir,prefix))
    except:
        print 'Failed to plot the likelihood results'
        pass
    
    results['%s_GRBindex' % prefix]     = index
    results['%s_GRBindex_ERR' % prefix] = index_err    
    results['%s_GRBcutoff' % prefix]     = cutoff
    results['%s_GRBcutoff_ERR' % prefix] = cutoff_err
    
    if gtsrcprob: # and like.Ts('GRB') > ts_min:
        if chatter>1: print ' COMPUTING THE EVENT PROBABILITY WITH GTSRCPROB:'
        out_file_srcprob = lat.gt_run_gtsrcprob(like=like)
        runShellCommand('mv %s %s' % (out_file_srcprob,gtsrc_probabilities))
        # NEW CODE TO MAKE THE ROOT FIILE OF SELECTED EVENTS ONLY
        #latutils.convert(gtsrc_probabilities,GRBMET=lat.GRB.Ttrigger,GRBRA=lat.GRB.ra,GRBDEC=lat.GRB.dec)
        # END OF NEW CODE
        results['%s_gtsrcprob' % prefix] = gtsrc_probabilities        
        if chatter>1: print 'OUTPUT: ',gtsrc_probabilities        
        myres = latutils.EventWithMaxEne(gtsrc_probabilities,t0=lat.GRB.Ttrigger,minene=0,minprob=0.9)
        results['%s_gtsrcprob_Emax' % prefix]   = myres['gtsrcprob_Emax']
        results['%s_gtsrcprob_Tmax' % prefix]   = myres['gtsrcprob_Tmax']
        results['%s_gtsrcprob_Pmax' % prefix]   = myres['gtsrcprob_Pmax']
        results['%s_gtsrcprob_Nthr' % prefix]   = myres['gtsrcprob_Nthr']
        results['%s_gtsrcprob_Tfirst' % prefix] = myres['gtsrcprob_Tfirst']
        results['%s_gtsrcprob_Tlast' % prefix]  = myres['gtsrcprob_Tlast']
        pass

    if chatter>1: print '=============================================================================================='
    
    e0  = float(results['FEMIN'])
    e1  = float(results['FEMAX'])
    z   = float(results['REDSHIFT'])
    
    ze0 = 100.0/(1.+z)  # 100 MeV RF
    ze1 = 1.0e+4/(1.+z)  # 10 GeV RF
    
    if like.Ts('GRB',reoptimize=False) > ts_min or resetMinimumTs:
        # COMPUTE THE FLUXES
        E01  = like.energyFlux('GRB',e0,e1)
        eE01 = like.energyFluxError('GRB',e0,e1)
        F01  = like.flux('GRB',e0,e1)
        eF01 = like.fluxError('GRB',e0,e1)
        FL01  = F01  * DeltaT # (Photon fluence)
        eFL01 = eF01 * DeltaT # (Photon fluence err)

        zE01  = E01
        zeE01 = eE01
        zF01  = F01
        zeF01 = eF01
        
        if chatter>1:
            print ' Flux (%f,%f) = %lf +/- %lf (MeV/cm^2/s), %.2e +/- %.2e (erg/cm^2/s) ' %(e0,e1,E01,eE01,E01*MeV2erg,eE01*MeV2erg)
            print ' Flux (%f,%f) = %lf +/- %lf  (ph/cm^2/s)' %(e0,e1,F01,eF01)
            pass

        if z>0:
            try:
                zE01  = like.energyFlux('GRB',ze0,ze1)
                zeE01 = like.energyFluxError('GRB',ze0,ze1)
                zF01  = like.flux('GRB',ze0,ze1)
                zeF01 = like.fluxError('GRB',ze0,ze1)
            except:
                zE01  = 0
                zeE01 = 0
                zF01  = 0
                zeF01 = 0
                pass
            if chatter>1:
                print ' Flux (%f,%f) Rest Frame = %lf +/- %lf (MeV/cm^2/s), %.2e +/- %.2e (erg/cm^2/s) ' %(ze0,ze1,zE01,zeE01,zE01*MeV2erg,zeE01*MeV2erg)
                print ' Flux (%f,%f) Rest Frame = %lf +/- %lf  (ph/cm^2/s)' %(ze0,ze1,zF01,zeF01)
                pass
            pass
        pass
    
    else: #CALCULATE UPPER LIMIT:
        import UpperLimits
        EXPO_MODEL=os.getenv('EXPO_MODEL','SUN')
        print 'EXPO_MODEL=',EXPO_MODEL
        if EXPO_MODEL=='SUN':
            index          = 0.0
            cutoff         = 300.0
        elif EXPO_MODEL=='SNALP':
            index          = 2.3
            cutoff         = 30.0
            pass
        if 'ULINDEX'  in results.keys(): index   = float(results['ULINDEX'])
        if 'ULCUTOFF' in results.keys(): cutoff  = float(results['ULCUTOFF'])
        
        index_err  = 0.0
        cutoff_err = 0.0
        print like_model
        if chatter>1: print 'COMPUTING UL (%d%% CL) => INDEX FIXED TO..... %s' % (CL*100,index)
        if 'GRBEXP' in like_model:
            if chatter>1: print '                       => CUT-OFF FIXED TO... %s ' % cutoff
            if chatter>1: print '                       => INDEX FIXED TO... %s ' % index
            like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[1]).setValue(index)
            like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[1]).setFree(0)
            like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[2]).setValue(cutoff)
            like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[2]).setFree(0)
            Normalization_name='Prefactor'
        else:
            if chatter>1: print '                       => INDEX FIXED TO... %s ' % index
            like['GRB'].src.spectrum().parameter('Index').setValue(index)
            like['GRB'].src.spectrum().parameter('Index').setFree(0)
            Normalization_name='Integral'
            pass 
        logLike0 = like.fit()       
        # profile the likelihood.
        #print 'Profilining the likelihood function... starting with logLike0=',logLike0
        #import scipy as sp
        #saved_state = LikelihoodState(like)
        #Normalization=like['GRB'].src.spectrum().parameter(Normalization_name).getValue()
        #print like.model 
        #print dir(like['GRB'].src.spectrum().parameter(Normalization_name).getBounds())
        #(Normalization_min,Normalization_max)=like['GRB'].src.spectrum().parameter(Normalization_name).getBounds()
        #logC=sp.logspace(sp.log10(Normalization_min),sp.log10(Normalization_max),50)
        #logL=[]
        #like['GRB'].src.spectrum().parameter(Normalization_name).setFree(0)
        #for C in logC:
        #    like['GRB'].src.spectrum().parameter(Normalization_name).setValue(C)
        #    LL   = logLike0-like.fit(covar=True,verbosity=0)#, renorm=True)
        #    E01  = like.energyFlux('GRB',e0,e1)
        #    F01  = like.flux('GRB',e0,e1)
        #    logL.append(LL)
        #    print C,logLike0,LL,e0,e1,F01,E01
        #    pass        
        #like['GRB'].src.spectrum().parameter(Normalization_name).setValue(Normalization)
        #like['GRB'].src.spectrum().parameter(Normalization_name).setFree(1)            
        #saved_state.restore()
        print '--------------------------------------------------'
        print like.model 
        print '--------------------------------------------------'
        ul = UpperLimits.UpperLimits(like)                
        try:
            ul_prof, ul_par = ul['GRB'].compute(emin=results['FEMIN'], emax=results['FEMAX'],delta=2.71/2.)
            ul_bayes, integral = ul['GRB'].bayesianUL(emin=float(results['FEMIN']), emax=float(results['FEMAX']),cl=CL)            
            # ul_prof_e =latutils.computeEflux(ul_prof,index,emin=results['FEMIN'], emax=results['FEMAX'])
            ul_bayes_e = latutils.computeEflux(ul_bayes,index,emin=float(results['FEMIN']), emax=float(results['FEMAX']))
            print 'ul_prof, ul_par=',ul_prof, ul_par
            #print ul['GRB'].bayesianUL_integral
        except:
            ul_bayes_e = 0
            ul_bayes   = 0                         
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print '         Error computing the UL...'
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            pass
        
        try:
            # ul_prof_z, ul_par = ul['GRB'].compute(emin=ze0, emax=ze1,delta=2.71/2.)            
            ul_bayes_z, integral = ul['GRB'].bayesianUL(emin=ze0, emax=ze1,cl=CL)
            # ul_prof_e =latutils.computeEflux(ul_prof,index,emin=ze0, emax=ze1)
            ul_bayes_e_z = latutils.computeEflux(ul_bayes,index,emin=ze0, emax=ze1)
        except:
            ul_bayes_e_z = 0
            ul_bayes_z   = 0
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print '         Error computing the UL...'
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            pass
        
        E01  = ul_bayes_e
        eE01 = 0.0
        F01  = ul_bayes
        eF01 = 0.0
        FL01  = ul_bayes  * DeltaT # (Photon fluence)
        eFL01 = 0.0

        zE01  = ul_bayes_e_z
        zeE01 = 0.0 
        zF01  = ul_bayes_z
        zeF01 = 0.0

        
        if chatter>1:
            print ' Flux (%f,%f) < %.2e  (MeV/cm^2/s), %.2e (erg/cm^2/s) [UL %d%% CL] ' %(e0,e1,E01,E01*MeV2erg,100*CL)
            print ' Flux (%f,%f) < %.2e  (ph/cm^2/s) [UL %d%% CL]' %(e0,e1,F01,100*CL)
            print ' Flux (%f,%f) < %.2e  (MeV/cm^2/s), %.2e (erg/cm^2/s) [UL %d%% CL] ' %(ze0,ze1,zE01,zE01*MeV2erg,100*CL)
            print ' Flux (%f,%f) < %.2e  (ph/cm^2/s) [UL %d%% CL]' %(ze0,ze1,zF01,100*CL)                        
            pass
        del ul
        pass
    
    #if F01>0:  eDeltaT = (eFL01*F01 + FL01*eF01)/(F01*F01)
    #else:      eDeltaT = 0

    #if chatter>1: print ' FLUX DeltaT: %.3f +/- %.3f ' % (DeltaT,eDeltaT)
    
    results['%s_FLUX_NRG_MIN' % prefix]     = e0
    results['%s_FLUX_NRG_MAX' % prefix]     = e1  
    results['%s_FLUX' % prefix]             = F01
    results['%s_FLUX_ERR' % prefix]         = eF01                   # ph/cm^2/s
    results['%s_FLUX_ENE' % prefix]         = E01*MeV2erg            # erg/cm^2/s
    results['%s_FLUX_ENE_ERR' % prefix]     = eE01*MeV2erg           # erg/cm^2/s
    results['%s_FLUENCE_ENE' % prefix]      = E01*MeV2erg * DeltaT   # erg/cm^2
    results['%s_FLUENCE_ENE_ERR' % prefix]  = eE01*MeV2erg * DeltaT  # erg/cm^2

    results['%s_FLUX_RF_NRG_MIN' % prefix]     = ze0
    results['%s_FLUX_RF_NRG_MAX' % prefix]     = ze1  
    results['%s_FLUX_RF' % prefix]             = zF01
    results['%s_FLUX_RF_ERR' % prefix]         = zeF01                   # ph/cm^2/s
    results['%s_FLUX_RF_ENE' % prefix]         = zE01*MeV2erg            # erg/cm^2/s
    results['%s_FLUX_RF_ENE_ERR' % prefix]     = zeE01*MeV2erg           # erg/cm^2/s
    results['%s_FLUENCE_RF_ENE' % prefix]      = zE01*MeV2erg * DeltaT   # erg/cm^2
    results['%s_FLUENCE_RF_ENE_ERR' % prefix]  = zeE01*MeV2erg * DeltaT  # erg/cm^2
    
    results['%s_T0'      % prefix]          = t1
    results['%s_T1'      % prefix]          = t2
    results['%s_EXPOSURE' % prefix]         = Exposure  # sec
    
    LD = float(results['LUMINOSITY_DISTANCE']) # this must be in cm!!
    if LD>0:
        redshift = float(results['REDSHIFT'])
        Area                    = 4.0*math.pi*pow(LD,2.0) # cm^2
        results['%s_EISO52' % prefix]         = float(results['%s_FLUENCE_ENE' % prefix])     * Area /1.0e52/(1.0+redshift) # erg
        results['%s_EISO52_ERR' % prefix]     = float(results['%s_FLUENCE_ENE_ERR' % prefix]) * Area /1.0e52/(1.0+redshift) # erg        
        results['%s_EISO52_RF' % prefix]         = float(results['%s_FLUENCE_RF_ENE' % prefix])     * Area /1.0e52/(1.0+redshift) # erg
        results['%s_EISO52_RF_ERR' % prefix]     = float(results['%s_FLUENCE_RF_ENE_ERR' % prefix]) * Area /1.0e52/(1.0+redshift) # erg
        
        if chatter>1:
            if float(results['%s_EISO52_ERR' % prefix])>0 :
                print ' Eiso (z=%.3f) = (%lf +/- %lf) x 10^52 ergs' %(float(results['REDSHIFT']),
                                                                      float(results['%s_EISO52' % prefix]),
                                                                      float(results['%s_EISO52_ERR' % prefix]))
            else:
                print ' Eiso (z=%.3f) < (%lf) x 10^52 ergs' %(float(results['REDSHIFT']),
                                                              float(results['%s_EISO52' % prefix]))
                pass
            pass
        pass
    if chatter>1: print '--------------------------------------------------'
    return like


def make_PHA_RSP_BKG(lat,nfit,t1,t2,outDir,like_res):
    tt      = lat.GRB.Ttrigger
    xt1     = t1-tt
    xt2     = t2-tt
    
    evt_file = like_res['evt_file']
    EXP_CUBE = like_res['EXP_CUBE']
    EXP_MAP  = like_res['EXP_MAP']
    src_model= like_res['src_model']
    allok=1
    for x in [evt_file,EXP_CUBE,EXP_MAP,src_model]:
        if not os.path.exists(x):
            print ' file %s does not exist!!!! ' % x
            allok=0
            pass
        pass
    if allok:
        pha_file ='%s/events_%06d_%.3f_%.3f.pha' %(outDir,nfit,xt1,xt2)
        rsp_file ='%s/response_%06d_%.3f_%.3f.rsp' %(outDir,nfit,xt1,xt2)
        bkg_file ='%s/background_%06d_%.3f_%.3f.pha' %(outDir,nfit,xt1,xt2)
        like_res['pha_file'] = pha_file
        like_res['rsp_file'] = rsp_file
        like_res['bkg_file'] = bkg_file
        
        
        lat.make_pha1(evfile =evt_file,outfile=pha_file,enumbins=10)
        lat.make_rsp(specfile=pha_file,outfile=rsp_file)
        latutils.CreatePHA_BKG_fromLikelihood(pha_file,
                                              bkg_file,
                                              lat.FilenameFT2,
                                              EXP_CUBE,
                                              EXP_MAP,
                                              lat._ResponseFunction,
                                              src_model,
                                              target='GRB')
        
        # THIS IS TO SAVE SOME SPACE:
        removeFiles([EXP_CUBE,EXP_MAP])
        pass
    pass


    



def makeOneLikelihood(lat,
                      nfit,
                      like_model,
                      results,
                      t1,
                      t2,
                      outDir,                      
                      computeUL = True,
                      switch_irf= False,
                      ts_min    = 25):
    ts_min = float(ts_min)    
    e0     = float(results['FEMIN'])                                                                                                                                                                                  
    e1     = float(results['FEMAX']) 

    tt      = lat.GRB.Ttrigger
    xt1     = t1-tt
    xt2     = t2-tt
    try: use_prior    = int(os.environ['GTGRB_USE_PRIOR'])
    except: use_prior = 1
    print 'use_prior=',use_prior    
    evt_file ='%s/events_%06d_%.4f_%.4f.fits'%(outDir,nfit,xt1,xt2)
    EXP_CUBE ='%s/ltcube_%06d_%.4f_%.4f.fits'%(outDir,nfit,xt1,xt2)
    EXP_MAP  ='%s/expmap_%06d_%.4f_%.4f.fits'%(outDir,nfit,xt1,xt2)
    src_model='%s/model_%06d_%.4f_%.4f.xml' %(outDir,nfit,xt1,xt2)

    filesAll=[evt_file,EXP_CUBE,EXP_MAP]
    filesFew=[EXP_CUBE,EXP_MAP]
    
    bkg_filePath = '%s/bkg_model.xml'   % lat.out_dir
    
    
    # NOTICE THAT src_model is an output and bkg_filePath is an input. t1, and t2 are MET
    
    #runShellCommand('cp %s %s' %(srcmodel,src_model))
    
    
    evt_file0    = lat.evt_file    
    lat.evt_file = evt_file
    
    lat.setTmin(t1)
    lat.setTmax(t2)
    irf0=lat._ResponseFunction
    like_model_used = like_model
    if switch_irf:        
        new_irfs=lat._ResponseFunction
        if t2-t1>100: 
            new_irfs='P8_TRANSIENT010E'
            like_model_used = like_model.replace('BKGE_CR_EGAL','TEM')
            pass
        if t2-t1>1000: 
            new_irfs='P8_SOURCE'
            like_model_used = like_model.replace('BKGE_CR_EGAL','TEM')
            pass
        lat.SetResponseFunction(new_irfs)
        pass
    '''
    if t2-t1 > _switch_irf and 'TRANSIENT' in irf0 and switch_irf: #and 'BKGE' not in src_model:    
        print '-- T2-T1 (%.3f) > %.3f => DIFFUSE WILL BE USED' %(t2-t1,_switch_irf)
        irfs=irf0.replace('TRANSIENT','DIFFUSE')
        lat.SetResponseFunction(irfs)
        like_model_used = like_model.replace('BKGE','TEM')
        print '---- Previous : ',irf0
        print '---- Current  : ',irfs
        pass
    '''
    resetMinimumTs=False

    lat.print_parameters()
    nevents = lat.make_select()
    result  = MakeXMLModel(lat, src_model, bkg_filePath, like_model_used, (t1-tt),(t2-tt))

    if result == "error":
        print "Error returned from MakeXMLModel.."
        return None,None
    
    if 'BKGE' in like_model_used:	diffuseModel,bkge_comp_stat_err = result
    else:                       diffuseModel,resetMinimumTs = result    
    
    print '===================================================================================================='
    print '===== MakeOneLikelihood Fit. Number of events between %.3f and %.3f is: %d  (ts_min=%.1f)  ====' %((t1-tt),(t2-tt),nevents,ts_min)
    print '===================================================================================================='
    if nevents==0:
        lat.evt_file         = evt_file0
        lat.SetResponseFunction(irf0)
        removeFiles(filesAll)
        return 0,None
    try:
        lat.make_expCube(outfile=EXP_CUBE)
        lat.make_expMap(expcube=EXP_CUBE,outfile=EXP_MAP)
        lat.make_gtdiffrsp(srcmdl=src_model)
    except:
        print '===================================================================================================='
        print '===== Expcube, Expmap, or diffresp failed...                                                   ====='
        print '===================================================================================================='
        lat.evt_file         = evt_file0
        lat.SetResponseFunction(irf0)
        removeFiles(filesAll)
        return None,None

    try:    
        like    = lat.pyLike(model=src_model,expmap=EXP_MAP,expcube=EXP_CUBE)        
        if "BKGE" in like_model_used: #constrain the BKGE normalization by applying a Gaussian prior
            bkge_sys_err=0.15
            # find index of BKGE component
            for idx in range(len(like.model.srcNames)): 
                if 'BKGE' in like.model.srcNames[idx]:
                    like[idx].addGaussianPrior(1,bkge_sys_err)
                    print 'Add gaussian prior to the BKGE model'
                    break
                pass
            pass
        if "TEM" in like_model_used and use_prior: #constrain the TEM normalization by applying a Gaussian prior #CMMENTED ON JAN 19 2016                
            for idx in range(len(like.model.srcNames)):
                print idx,like.model.srcNames[idx]
                if 'EG' in like.model.srcNames[idx]:
                    like[idx].addGaussianPrior(1.0,1.0)
                    print 'Added a gaussian prior to the %s component!' % like.model.srcNames[idx]
                    break
                pass
            pass
        pass
    except:
        print '===================================================================================================='
        print '===== pyLike failed...                                                                         ====='
        print '===================================================================================================='
        lat.evt_file         = evt_file0
        lat.SetResponseFunction(irf0)
        removeFiles(filesAll)        
        return None,None
    
    try:
        logLike = like.fit(covar=True)                
        print '--------------------------------------------------'
        print like
        print '--------------------------------------------------'
    except:
        print '===================================================================================================='
        print '===== Likelihood fit did not converge.                                                         ====='
        print '===================================================================================================='
        lat.evt_file         = evt_file0
        lat.SetResponseFunction(irf0)
        removeFiles(filesAll)
        return None,None
        
    print like.model    
    NobsTot = like.nobs.sum()
    emin = max(100.,  lat.Emin)
    emax = min(10000.,lat.Emax)
    #emin = float(results['FEMIN'])                                                                                                                                                                                  
    #emax = float(results['FEMAX']) 
    print '****************************************************************************************************'
    print 'log(Likelihood): %s' % logLike    
    for ss in like.sourceNames():
        try: npred_emin_emax    = like[ss].src.Npred(emin,emax)
        except: npred_emin_emax = 0
        print '******** SOURCE: %10s, Ts= %10.2f, Npred(%.3e,%.3e)/Nobs= %5.1f/%3d' %(ss,like.Ts(ss,reoptimize=False),emin,emax,npred_emin_emax,NobsTot)
        pass
    print '****************************************************************************************************'
    Ts           = like.Ts('GRB',reoptimize=False)    
    spec         = like['GRB'].spectrum()
    if 'GRBEXP' in like_model_used:
        index     = like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[1]).getValue()
        index_err = like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[1]).error()
        cutoff    = like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[2]).getValue()
        cutoff_err= like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[2]).error()
    else:
        index     = like['GRB'].src.spectrum().parameter('Index').getValue()
        index_err = like['GRB'].src.spectrum().parameter('Index').error()
        cutoff    = 0
        cutoff_err= 0
        pass
    
    try: Np_100MeV    = like['GRB'].src.Npred(100,emax)
    except: Np_100MeV = 0
    try: Np_1GeV      = like['GRB'].src.Npred(1000,emax)
    except: Np_1GeV   = 0
    try: Np_GRB       = like['GRB'].src.Npred(emin,emax)
    except: Np_GRB    = 0
    
    E01 = 0    
    E01 = 0
    eE01 = 0
    F01 = 0
    eF01 = 0

    if (Ts > ts_min and Np_GRB>1) or resetMinimumTs:
        try:
            like.plot()
            for srcN in like.sourceNames():
                if 'GRB' in srcN:
                    like.plotSource(srcN,'red')
                elif 'EG' in srcN or 'BKGE' in srcN:
                    like.plotSource(srcN,'green')
                elif 'GAL' in srcN:
                    like.plotSource(srcN,'blue')
                    pass
                pass
            like.residualPlot.canvas.Update()
            like.spectralPlot.canvas.Update()
            like.residualPlot.canvas.Print('%s/residualPlot_%06d_%.4f_%.4f.png' % (outDir,nfit,xt1,xt2))
            like.spectralPlot.canvas.Print('%s/spectralPlot_%06d_%.4f_%.4f.png' % (outDir,nfit,xt1,xt2))
        except:
            print 'Failed to plot the likelihood...'
            pass
            
        like.writeXml(xmlFile=src_model)
        
        E01  = like.energyFlux('GRB',e0,e1)
        eE01 = like.energyFluxError('GRB',e0,e1)
        F01  = like.flux('GRB',e0,e1)
        eF01 = like.fluxError('GRB',e0,e1)
        
        print ' Flux (%f,%f) = %lf +/- %lf (MeV/cm^2/s)' %(e0,e1,E01,eE01)
        print ' Flux (%f,%f) = %lf +/- %lf  (ph/cm^2/s)' %(e0,e1,F01,eF01)
        print ' Npredicted >100MeV: %.1f' % Np_100MeV 
        print ' Npredicted >  1GeV: %.1f' % Np_1GeV
    elif computeUL:        
        import UpperLimits
        try:     index = float(results['ULINDEX'])
        except:  index  = -2.0
        try:     cutoff= float(results['ULCUTOFF'])
        except:  cutoff = 300.0
        index_err  = 0.0
        cutoff_err = 0.0
        print like_model_used
        print 'Computing UL... Fixing the index to %s' % index        
        if 'GRBEXP' in like_model_used:
            print '... and the cut off to: %s ' % cutoff            
            like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[1]).setValue(index)
            like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[1]).setFree(0)
            like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[2]).setValue(cutoff)
            like['GRB'].src.spectrum().parameter(ExpCutOffModelUsed[2]).setFree(0)
        else:
            like['GRB'].src.spectrum().parameter('Index').setValue(index)
            like['GRB'].src.spectrum().parameter('Index').setFree(0)
            pass
        
        like.fit()
        
        # like.plot()
        # for srcN in like.sourceNames():
        #    if 'GRB' in srcN:
        #        like.plotSource(srcN,'red')
        #    elif 'EG' in srcN or 'BKGE' in srcN:
        #        like.plotSource(srcN,'green')
        #    elif 'GAL' in srcN:
        #        like.plotSource(srcN,'blue')
        #        pass
        #    pass
        # like.residualPlot.canvas.Print('%s/residualPlot_%06d_%.4f_%.4f.png' % (outDir,nfit,xt1,xt2))
        # like.spectralPlot.canvas.Print('%s/spectralPlot_%06d_%.4f_%.4f.png' % (outDir,nfit,xt1,xt2))
        # like.writeXml(xmlFile=src_model)
        
        ul=UpperLimits.UpperLimits(like)
	ul_bayes_e = 0
        ul_bayes   = 0                
        try:
            # ul_prof, ul_par = ul['GRB'].compute(emin=e0, emax=e1,delta=2.71/2.)
            ul_bayes, integral = ul['GRB'].bayesianUL(emin=e0, emax=e1,cl=CL)
            ul_bayes_e = latutils.computeEflux(ul_bayes,index,emin=float(results['FEMIN']), emax=float(results['FEMAX']))
        except:
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print 'Error computing the UL...'
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            return None,None
        E01  = ul_bayes_e
        F01  = ul_bayes
        eE01 = 0
        eF01 = 0
        print ' Flux (%f,%f) < %.2e  (MeV/cm^2/s), %.2e (erg/cm^2/s) [UL %d%% CL] ' %(e0,e1,E01,E01*MeV2erg,100*CL)
        print ' Flux (%f,%f) < %.2e  (ph/cm^2/s) [UL %d%% CL]' %(e0,e1,F01,100*CL)
        del ul
        pass
    
    # for f in (EXP_CUBE,EXP_MAP): runShellCommand('rm -rf %s' % f)
    #del like
    lat.evt_file         = evt_file0
    lat.SetResponseFunction(irf0)
    
    ##################################################
    # SAVE THE RESULTS IN A DICTIONARY               #
    ##################################################
    
    like_results={}

    like_results['evt_file']=evt_file
    like_results['EXP_CUBE']=EXP_CUBE
    like_results['EXP_MAP']= EXP_MAP
    like_results['src_model']=src_model
    
    like_results['e0']       =e0
    like_results['e1']       =e1
    like_results['Ts']       =Ts
    like_results['index']    =index
    like_results['index_err'] =index_err
    if cutoff>0:
        like_results['cutoff']    =index
        like_results['cutoff_err'] =index_err
        pass
    like_results['F01']      = F01
    like_results['eF01']     = eF01
    like_results['E01']      = E01
    like_results['eE01']     = eE01
    like_results['NobsTot']  = NobsTot
    like_results['Np_100MeV']= Np_100MeV
    like_results['Np_1GeV']  = Np_1GeV    
    like_results['Np_GRB']   = Np_GRB    
    
    # removeFiles(filesFew)
    return like_results,like



def RunExtendedEmission(lat, like_model, results, bins,
                        gtsrcprob = 1, pha=1,
                        ts_min=25, equalTS = False):
    
    like_model_comps=like_model.split("+") #tokenize
    for i in range(0,len(like_model_comps)): #convert to UL
        like_model_comps[i]=like_model_comps[i].upper()
        pass

    NumberOfParameters = 0
    if 'GAL' in like_model_comps: NumberOfParameters+=1 # norm
    if 'TEM' in like_model_comps: NumberOfParameters+=1 # norm
    if 'BKGE_GAL_GAMMAS' in like_model_comps: NumberOfParameters+=1 # norm
    if 'BKGE_CR_EGAL' in like_model_comps: NumberOfParameters+=1 # norm
    if 'BKGE_TOTAL' in like_model_comps: NumberOfParameters+=1 # norm
    if 'PREFIT' in like_model_comps: NumberOfParameters+=1 # norm index
    # 2.
    if 'GRB' in like_model_comps: NumberOfParameters+=2 # norm and spectral index
    if 'ISO' in like_model_comps: NumberOfParameters+=2 # norm and spectral index
    if 'SRC' in like_model_comps: NumberOfParameters+=2 # norm and spectral index
    
    
    irf0 = lat._ResponseFunction
    
    outDir='%s/ExtendedEmission'%(lat.out_dir)
    
    runShellCommand('mkdir %s'%outDir)
    like_results_name='%s/like_%s.txt' % (outDir,lat.GRB.Name)
    like_results=file(like_results_name,'w')
    txt='# fitNum \t start \t\t end \t\t median \t\t Emin \t Emax \t Ts \t NobsTot \t Npred_100 \t Npred_1000 \t index \t errorI \t Flux    \t\t ErrorF \t EnergyFlux \t\t ErrorEF   \t\t Fluence\n'
    like_results.write(txt)
    txt='#        \t sec   \t\t sec \t\t sec    \t\t MeV  \t MeV  \t    \t         \t           \t            \t       \t        \t ph/cm/s \t\t ph/cm/s\t MeV/cm^2/s \t\t MeV/cm^2/s\t\t MeV/cm^2\n'    
    like_results.write(txt)
    like_results.close()

    emax_name='%s/like_%s_emax.txt' % (outDir,lat.GRB.Name)
    like_results = file(emax_name,'w')
    txt= '#%6s %10s %15s %10s %10s %10s\n' %('NEVT','TIME','ENERGY','PROB','FIRST','LAST')
    like_results.write(txt)
    like_results.close()
    
    bins0 = bins[0]
    bins1 = bins[1]
    
    
    FirstBin_MET    = bins0[0] + lat.GRB.Ttrigger
    LastBin_MET     = bins1[-1]+ lat.GRB.Ttrigger
    


    lat.setTmin(FirstBin_MET)
    lat.setTmax(LastBin_MET)
    nevt = lat.make_select()
    if nevt==0: return like_results_name
        
    evt_file0 = lat.evt_file
    hdulist = pyfits.open(evt_file0)
    tbdata  = hdulist[1].data
    MET_time    = sorted(tbdata.field('TIME'))
    hdulist.close()
    print 'Selected events between %.3f and %.3f...(%.3f and %.3f): %s' %(bins0[0],bins1[-1],FirstBin_MET,LastBin_MET,len(MET_time))
    print 'Number of free parameters in the model:%d, Minimum NDOF=%d Step forward by %d events' %(NumberOfParameters, NumberOfDOF, StepSize)
    #for i in range(len(MET_time)):
    #    print '%d - %.3f ' %(i,MET_time[i]-lat.GRB.Ttrigger)
    #    pass
    
    NT = len(bins0)
    j     =  0
    index_likelihood=0
    import gtgrb
    i1=0
    i2=0
    for i in range(NT):        
        if equalTS:     
            i1 = i
            i2 = i            
            print ' (i:%d,i1:%d,i2:%d): LIKELIHOOD MODEL: %s' %(i,i1,i2,like_model)
            MinTime = bins0[i1]
            MaxTime = bins1[i2]
            MinTime_MET  = lat.GRB.Ttrigger + MinTime
            MaxTime_MET  = lat.GRB.Ttrigger + MaxTime
            first = NumberOfDOF + NumberOfParameters # This is the number of dof
           
            print '***** USING: MINIMUM NUMBER OF EVENTS= %d, NUMBER TO ADD=%d' %(first,StepSize)
            print ' ------------------------------------------------------------------------------- '
            print ' Running Likelihood analysis with constant Ts [%.4f - %.4f] ' % (MinTime, MaxTime)
            print ' ------------------------------------------------------------------------------- '
            
            evt1      = _findFirst(MET_time, MinTime_MET)            
            evt2      = min(evt1 + first,    len(MET_time)-1)            
            tBin1_MET = MET_time[evt1]-1.0e-3
            tBin2_MET = MET_time[evt2]-1.0e-3
            if tBin1_MET > MaxTime_MET: continue
            
            XTIME1    = 0
            XTIME2    = 0
            XMETTIME1 = 0
            XMETTIME2 = 0
            Ts      =   0
            index   =   0
            interrompi = 0
            continua   = 1
            while continua == 1:
                # print ' 888888888888888888888888888 Evt1: %d , Evt2: %d of (%d), tBin1: %.3f, tBin2: %.3f (%d) 888888888888888888888' % (evt1,
                #                                                                                                                         evt2,
                #                                                                                                                         len(MET_time)-1,
                #                                                                                                                         tBin1_MET - lat.GRB.Ttrigger,
                #                                                                                                                         tBin2_MET - lat.GRB.Ttrigger,
                #                                                                                                                         interrompi)
                dt = tBin2_MET - tBin1_MET
                if dt<=0 or evt1==evt2:
                    print ' End of running extended emission...'
                    break
                
                like_res,like = makeOneLikelihood(lat,j,like_model,results,
                                                  tBin1_MET,tBin2_MET,outDir,
                                                  computeUL  = True,
                                                  switch_irf = False, #don't change!
                                                  ts_min     = ts_min)
                index_likelihood=j
                
                # THESE ARE THE TIME WHEN THE LIKELIHOOD IS COMPUTED
                XMETTIME1 = tBin1_MET
                XMETTIME2 = tBin2_MET
                XTIME1    = XMETTIME1 - lat.GRB.Ttrigger
                XTIME2    = XMETTIME2 - lat.GRB.Ttrigger
                
                if like_res == 0: # This happen when there are 0 events in the interval, therefore, change interval
                    if MET_time[evt2] >= MaxTime_MET or evt2==(len(MET_time)-1): continua=0 # Used altready all the events
                    evt1  = evt2
                    evt2  = min(evt1 + first,len(MET_time)-1)                    
                    tBin1_MET = MET_time[evt1]-1.0e-3
                    tBin2_MET = min(MET_time[evt2]-1.0e-3, MaxTime_MET)                    
                    continue                
                
                if like_res is None: # If likelihood did not converge, try to extend the interval
                    if MET_time[evt2] >= MaxTime_MET or evt2==(len(MET_time)-1): continua=0 # Used altready all the events
                    evt2  = min(evt2 + StepSize,len(MET_time)-1)                    
                    tBin1_MET = MET_time[evt1]-1.0e-3
                    tBin2_MET = min(MET_time[evt2]-1.0e-3, MaxTime_MET)
                    # if MET_time[evt2]>=MaxTime_MET: continua=0
                    continue
                
                Ts        = like_res['Ts']

                if (Ts < ts_min):
                    if MET_time[evt2] >= MaxTime_MET or evt2==(len(MET_time)-1): # Used altready all the events
                        interrompi=1
                        # continue
                    
                    evt2  = min(evt2 + StepSize,len(MET_time)-1)
                    tBin2_MET = min(MaxTime_MET, MET_time[evt2]-1.0e-3)                    
                    pass
                print '***** DEBUG: Spectrum %d (%d), Ts=%.1f (ts_min=%.1f), evt1=%d, evt2=%d, [%.2f-%.2f] (continua=%d, interrompi=%d)' %(index_likelihood,i,Ts,ts_min, evt1, evt2, tBin1_MET-lat.GRB.Ttrigger, tBin2_MET-lat.GRB.Ttrigger, continua,interrompi)
                
                print 'Profiling the likelihood...'
                src_xml = like.srcModel.replace('.xml','_profile.xml')
                like.writeXml(xmlFile=src_xml)
                saved_state = LikelihoodState(like)
                from GtBurst.likelihood_profile_writer import LikelihoodProfiler
                lpw = LikelihoodProfiler(like, src_xml)
                lpw.get_likelihood_profile()
                lpw.save('%s/ExtendedEmission/profile_%06d_%.4f_%.4f' %(lat.out_dir,index_likelihood,MinTime,MaxTime))
                fig = lpw.plot()
                fig.savefig('%s/ExtendedEmission/profile_%06d_%.4f_%.4f.png' %(lat.out_dir,index_likelihood,MinTime,MaxTime))
                saved_state.restore()
                                
                if (Ts >= ts_min) or interrompi:
                    like_evtfile = like.observation.eventFiles[0]
                    print '--------------------------------------------------'
                    if pha:   make_PHA_RSP_BKG(lat,index_likelihood,tBin1_MET,tBin2_MET,outDir,like_res)
                    if gtsrcprob:# and (Ts >= ts_min):
                        print '==== COMPUTING GTSRCPROB:'
                        if os.path.exists(like_evtfile):
                            gtsrc_probabilities   = '%s/ExtendedEmission/gtsrcprob_%s_%.3f_%.3f.fits' %(lat.out_dir, index_likelihood, XTIME1,XTIME2)
                            out_file_srcprob = lat.gt_run_gtsrcprob(like=like)                    
                            runShellCommand('mv %s %s' % (out_file_srcprob,gtsrc_probabilities))                            
                            runShellCommand('rm %s' %like.observation.eventFiles[0])                            
                            if os.path.exists(gtsrc_probabilities):
                                print 'OUTPUTFILE: %s' % gtsrc_probabilities
                                myres = latutils.EventWithMaxEne(gtsrc_probabilities,t0=lat.GRB.Ttrigger,minene=0,minprob=0.9)
                                # NEW CODE TO MAKE THE ROOT FIILE OF SELECTED EVENTS ONLY
                                #latutils.convert(gtsrc_probabilities,GRBMET=lat.GRB.Ttrigger,GRBRA=lat.GRB.ra,GRBDEC=lat.GRB.dec)
                                # END OF NEW CODE
                                energy_max = myres['gtsrcprob_Emax']
                                time_max   = myres['gtsrcprob_Tmax']
                                prob_max   = myres['gtsrcprob_Pmax']
                                Nthr       = myres['gtsrcprob_Nthr']
                                first      = myres['gtsrcprob_Tfirst']
                                last       = myres['gtsrcprob_Tlast']
                                txt='%6d %10.2f %15.1f %10.3f %10.2f %10.2f \n' %(Nthr,time_max,energy_max,prob_max,first,last)
                                like_results = file(emax_name,'a') # this is to force the file to be written
                                like_results.write(txt)
                                like_results.close()
                                pass
                            pass
                        else: print '====GTSRCPROB NOT RUNNING. FILE %s NOT FOUND!' %(like_evtfile)
                        del like
                        print '--------------------------------------------------'
                        pass
                    
                    e0       = like_res['e0']
                    e1       = like_res['e1']
                    Ts       = like_res['Ts']
                    NobsTot  = like_res['NobsTot']
                    n100     = like_res['Np_100MeV']
                    n1000    = like_res['Np_1GeV']
                    index    = like_res['index']
                    index_err= like_res['index_err']
                    F01      = like_res['F01']
                    eF01     = like_res['eF01']
                    E01      = like_res['E01']
                    eE01     = like_res['eE01']

                    # --------------------------------------------------
                    it1= _findFirst(MET_time, XMETTIME1)            
                    it2= _findFirst(MET_time, XMETTIME2)                    
                    TimeArray = MET_time[it1:it2]
                    #print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
                    #print tBin1_MET,tBin2_MET,it1,it2
                    #print TimeArray
                    median    = _median(TimeArray)-lat.GRB.Ttrigger
                    # --------------------------------------------------
                    

                    txt='%i \t %f \t %f \t\t %f \t %.1f \t %.1f \t %f \t %i \t %f \t %.2f \t %.4f \t %.4f \t %.3e \t %.3e \t %.3e \t %.3e \t\t %.3e\n' % \
                         (index_likelihood,XTIME1, XTIME2, median, e0, e1, Ts, NobsTot, n100, n1000, index, index_err, F01, eF01, E01, eE01, F01*dt)
                    j+=1                
                    print txt
                    like_results = file(like_results_name,'a') # this is to force the file to be written
                    like_results.write(txt)
                    like_results.close()
                    evt1  = evt2
                    evt2  = min(evt1 + first,len(MET_time)-1)
                    tBin1_MET = MET_time[evt1]-1.0e-3
                    tBin2_MET = MET_time[evt2]-1.0e-3
                    pass
                if interrompi==1:
                    continua = 0
                    '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% BREAK!! %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
                    pass
                pass
            pass    
        else:
            # 2 Case with multiple bins, no Equal TS            
            # These are two options:
            #1. This will increment the bin size when there are too few events...            
            try:
              changeSizeWhenFew = bool(os.environ['CHANGESIZEWHENFEW'])
            except:
              changeSizeWhenFew = True
            #2. This will increment the bin size when likelihood return ts(GRB)<tsmin.
            changeSizeWhenUL  = True
            
            print '--------------------------------------------------'
            # The first iteration has i1=i2=0
            if i1>=NT or i2>=NT:
                # No more bins...
                break
            
            MinTime = bins0[i1]
            MaxTime = bins1[i2]
            MinTime_MET  = lat.GRB.Ttrigger + MinTime
            MaxTime_MET  = lat.GRB.Ttrigger + MaxTime
            
            evt1      = _findFirst(MET_time, MinTime_MET)            
            evt2      = _findFirst(MET_time, MaxTime_MET)
            print 'Spectrum # %d (%d), from %.3f, to %.3f [Number of events: %d]'%(i1,i,MinTime,MaxTime,evt2-evt1)
            if (evt2 - evt1)==0:                        like_res = 0
            elif (evt2-evt1) <= (NumberOfDOF+NumberOfParameters): like_res = None
            else:
                #######
                like_res,like = makeOneLikelihood(lat,i1,like_model,results,MinTime_MET,MaxTime_MET,outDir,computeUL = True, switch_irf=True, ts_min = ts_min)
                index_likelihood=i1
                pass
            
            if like_res == 0: # No events. Step to the next bin                
                i1 = i1+1
                i2 = i2+1                
            elif like_res is None: # Failed (but there were some events) increase the size of the bin adding the next bin:
                print  'i2+1=' , i2+1,'NT:',NT,'changeSizeWhenFew:',changeSizeWhenFew
                if i2+1 < NT:
                    if bins0[i2+1] == bins1[i2] and changeSizeWhenFew:
                        i2 = i2+1 # Increment only the Upper bound
                    else:
                        i1 = i2+1 # Increment the Lower bound
                        i2 = i2+1 # Increment the Upper bound
                        pass
                    pass
                else:
                    i1 = i2+1 # Increment the Lower bound
                    i2 = i2+1 # Increment the Upper bound                    
                    pass
                pass
            elif isinstance(like_res,dict):
                scrivi   = False
                Ts       = like_res['Ts']
                # 2 cases:
                if (Ts < ts_min): # A) ts<tsmin
                    if i2+1 < NT:
                        if bins0[i2+1] == bins1[i2] and changeSizeWhenUL:
                            i2 = i2+1 # Increment only the Upper bound
                        else:
                            i1 = i2+1 # Increment the Lower bound
                            i2 = i2+1 # Increment the Upper bound
                            scrivi = True
                            pass
                        pass
                    else:
                        i1 = i2+1 # Increment the Lower bound
                        i2 = i2+1 # Increment the Upper bound
                        scrivi = True                                                
                        pass
                    pass
                else: # B) ts>=tsmin
                    i1 = i2+1 # Increment the Lower bound
                    i2 = i2+1 # Increment the Upper bound
                    scrivi = True                                        
                    pass
                
                if scrivi:
                    print 'Profiling the likelihood...'
                    src_xml = like.srcModel.replace('.xml','_profile.xml')
                    like.writeXml(xmlFile=src_xml)
                    saved_state = LikelihoodState(like)
                    from GtBurst.likelihood_profile_writer import LikelihoodProfiler
                    lpw = LikelihoodProfiler(like, src_xml)
                    lpw.get_likelihood_profile()
                    lpw.save('%s/ExtendedEmission/profile_%06d_%.4f_%.4f' %(lat.out_dir,index_likelihood,MinTime,MaxTime))
                    fig = lpw.plot()
                    fig.savefig('%s/ExtendedEmission/profile_%06d_%.4f_%.4f.png' %(lat.out_dir,index_likelihood,MinTime,MaxTime))
                    saved_state.restore()
                    
                    like_evtfile = like.observation.eventFiles[0]
                    if pha:   make_PHA_RSP_BKG(lat,index_likelihood,MinTime_MET,MaxTime_MET,outDir,like_res)
                    if gtsrcprob and (Ts >= ts_min):
                        print '--------------------------------------------------'
                        print '==== COMPUTING GTSRCPROB:'
                        if os.path.exists(like_evtfile):
                            gtsrc_probabilities   = '%s/ExtendedEmission/gtsrcprob_%d_%.3f_%.3f.fits' %(lat.out_dir,index_likelihood,MinTime,MaxTime)
                            out_file_srcprob = lat.gt_run_gtsrcprob(like=like)                    
                            runShellCommand('mv %s %s' % (out_file_srcprob,gtsrc_probabilities))                                            
                            runShellCommand('rm %s' %like.observation.eventFiles[0])
                            # NEW CODE TO MAKE THE ROOT FIILE OF SELECTED EVENTS ONLY
                            #latutils.convert(gtsrc_probabilities,GRBMET=lat.GRB.Ttrigger,GRBRA=lat.GRB.ra,GRBDEC=lat.GRB.dec)
                            # END OF NEW CODE
                            myres = latutils.EventWithMaxEne(gtsrc_probabilities,t0=lat.GRB.Ttrigger,minene=0,minprob=0.9)
                            energy_max = myres['gtsrcprob_Emax']
                            time_max   = myres['gtsrcprob_Tmax']
                            prob_max   = myres['gtsrcprob_Pmax']
                            Nthr       = myres['gtsrcprob_Nthr']
                            first      = myres['gtsrcprob_Tfirst']
                            last       = myres['gtsrcprob_Tlast']
                            txt='%6d %10.2f %15.1f %10.3f %10.2f %10.2f \n' %(Nthr,time_max,energy_max,prob_max,first,last)
                            like_results = file(emax_name,'a') # this is to force the file to be written
                            like_results.write(txt)
                            like_results.close()
                        else:
                            print '====GTSRCPROB NOT RUNNING. FILE %s NOT FOUND!' %(like_evtfile)
                            pass
                        del like
                        pass
                    print '--------------------------------------------------'
                    e0       = like_res['e0']
                    e1       = like_res['e1']                    
                    NobsTot  = like_res['NobsTot']
                    n100     = like_res['Np_100MeV']
                    n1000    = like_res['Np_1GeV']
                    index    = like_res['index']
                    index_err= like_res['index_err']
                    F01      = like_res['F01']
                    eF01     = like_res['eF01']
                    E01      = like_res['E01']
                    eE01     = like_res['eE01']
                    # --------------------------------------------------
                    TimeArray = MET_time[evt1:evt2]
                    median    = _median(TimeArray)-lat.GRB.Ttrigger
                    # --------------------------------------------------
                    
                    txt='%i \t %f \t %f \t\t %f \t %.1f \t %.1f \t %f \t %i \t %f \t %.2f \t %.4f \t %.4f \t %.3e \t %.3e \t %.3e \t %.3e \t\t %.3e\n' % \
                         (index_likelihood,MinTime,MaxTime,median,e0,e1,Ts,NobsTot,n100,n1000,index,index_err,F01,eF01,E01,eE01,F01*(MaxTime-MinTime))
                    like_results = file(like_results_name,'a') # this is to force the file to be written
                    like_results.write(txt)
                    like_results.close()
                    pass
                pass
            else:
                print 'WARNING!!!! likelihood returned %s...  ' % like_res
                i1 = i2+1 # Increment the Lower bound
                i2 = i2+1 # Increment the Upper bound   
                pass
            pass
        pass
    print '**************************************************'
    

    profiles_dict = LikelihoodProfileFit.find_profiles(outDir)
    outroot= '%s/profile' % outDir
    t1=results['GBMT95']
    t2=bins1[-1]
    print 'calling LikelihoodProfileFit with...: tstart=%f, tstop=%s, outroot=%s' % (t1,t2, outroot)
    try:
        
        po_best_fit, bknpo_best_fit, TS = LikelihoodProfileFit.go(profiles_dict, tstart=t1, tstop=t2, outroot=outroot)    

        results['PO_TS_POW_BKN']=TS

        po_best_fit_values=po_best_fit.values

        if po_best_fit_values.shape == (2,5):
            results['PO_POW_N']    = po_best_fit_values[0][0]
            results['PO_POW_N_LE'] = po_best_fit_values[0][1]
            results['PO_POW_N_HE'] = po_best_fit_values[0][2]
            results['PO_POW_N_ERR']= po_best_fit_values[0][3]
            
            results['PO_POW_idx']    = po_best_fit_values[1][0]
            results['PO_POW_idx_LE'] = po_best_fit_values[1][1]
            results['PO_POW_idx_HE'] = po_best_fit_values[1][2]
            results['PO_POW_idx_ERR']= po_best_fit_values[1][3]
            pass
        bknpo_best_fit_values=bknpo_best_fit.values
        if bknpo_best_fit_values.shape == (4,5):
            results['PO_BKN_N']    = bknpo_best_fit_values[0][0]
            results['PO_BKN_N_LE'] = bknpo_best_fit_values[0][1]
            results['PO_BKN_N_HE'] = bknpo_best_fit_values[0][2]
            results['PO_BKN_N_ERR']= bknpo_best_fit_values[0][3]
            
            results['PO_BKN_Eb']    = bknpo_best_fit_values[1][0]
            results['PO_BKN_Eb_LE'] = bknpo_best_fit_values[1][1]
            results['PO_BKN_Eb_HE'] = bknpo_best_fit_values[1][2]
            results['PO_BKN_Eb_ERR']= bknpo_best_fit_values[1][3]
            
            results['PO_BKN_Idx1']    = bknpo_best_fit_values[2][0]
            results['PO_BKN_Idx1_LE'] = bknpo_best_fit_values[2][1]
            results['PO_BKN_Idx1_HE'] = bknpo_best_fit_values[2][2]
            results['PO_BKN_Idx1_ERR']= bknpo_best_fit_values[2][3]
            
            results['PO_BKN_Idx2']    = bknpo_best_fit_values[3][0]
            results['PO_BKN_Idx2_LE'] = bknpo_best_fit_values[3][1]
            results['PO_BKN_Idx2_HE'] = bknpo_best_fit_values[3][2]
            results['PO_BKN_Idx2_ERR']= bknpo_best_fit_values[3][3]
            pass
        
    except: 
        print 'LikelihoodProfileFit crashed...'
        pass
    lat.evt_file = evt_file0
    lat.setTmin(FirstBin_MET)
    lat.setTmax(LastBin_MET)    
    return like_results_name

##########################

def gt_Create_UnbinnedLikelihood(lat,like_model,tstart_offset,tstop_offset,KeepFiles=False,chatter=2,Fit=True,ResultsDirPrefix=""):
    '''
	This toolkit-code creates and returns an unbinned likelihood object.
	It is meant to be used by other higher-order analyses.
	Adopted by makeOneLikelihood function.
	Documentation TBA
	Questions to vlasisva@gmail.com
    '''
    tstart_MET=tstart_offset+lat.GRB.Ttrigger
    tstop_MET =tstop_offset+lat.GRB.Ttrigger
    
    ResultsDirPrefix+="_"
    ResultsDir=lat.out_dir + "/%s%.2f_%.2f/" %(ResultsDirPrefix,tstart_offset,tstop_offset)
    
    if not os.path.isdir(ResultsDir) :
	os.mkdir(ResultsDir)
    if chatter>1: 
	gt_print("Using %s directory for work files" %ResultsDir,chatter=chatter)
    pass
    myevt_file ='%s/events_%.2f_%.2f.fits'%(ResultsDir,tstart_offset,tstop_offset)
    EXP_CUBE ='%s/ltcube_%.2f_%.2f.fits'%(ResultsDir,tstart_offset,tstop_offset)
    EXP_MAP  ='%s/expmap_%.2f_%.2f.fits'%(ResultsDir,tstart_offset,tstop_offset)
    src_model_file='%s/model_%.2f_%.2f.xml' %(ResultsDir,tstart_offset,tstop_offset)
    files={}
    files['RESULTS_DIR']  =ResultsDir
    files['EVENT_FILE']   =myevt_file
    files['EXPOSURE_CUBE_FILE']=EXP_CUBE
    files['EXPOSURE_MAP_FILE'] =EXP_MAP
    files['SOURCE_MODEL_FILE'] =src_model_file
    print chatter
    result = MakeXMLModel(lat, src_model_file, "", like_model, tstart_offset,tstop_offset,chatter=chatter)
    if result == "error": 
	gt_print("Error returned from MakeXMLModel..",chatter=chatter)
	return 
    pass
    lat.print_parameters()
    nevents = lat.make_select(outfile=myevt_file,tmin=tstart_MET,tmax=tstop_MET)

    if chatter>1:
    	gt_print("Number of events between %.3f and %.3f is: %d" %(tstart_offset,tstop_offset,nevents),chatter=chatter)
    pass

    if nevents==0:
	gt_print("No events in specified time interval..",chatter=chatter,print_border=True)
        if not KeepFiles:
            runShellCommand("rm -rf %s" %ResultsDir)
        return
    pass

    try:
        lat.make_expCube(chatter=chatter,outfile=EXP_CUBE,evfile=myevt_file)
        lat.make_expMap(chatter=chatter,expcube=EXP_CUBE,evfile=myevt_file,outfile=EXP_MAP)
        lat.make_gtdiffrsp(chatter=chatter,srcmdl=src_model_file)
    except:
        if not KeepFiles:
            runShellCommand("rm -rf %s" %ResultsDir)
        return
    pass

    try:    
	like = lat.pyLike(chatter=chatter,model=src_model_file,expmap=EXP_MAP,expcube=EXP_CUBE, infile=myevt_file)
    except:
	gt_print("Likelihood failed..",chatter=chatter,print_border=True)
    	if not KeepFiles:
    	    runShellCommand("rm -rf %s" %ResultsDir)
	return
    pass
    
    if Fit:
	try:
    	    like.fit(covar=True,verbosity=chatter-2)      
	except:
	    gt_print("Fitting likelihood failed..",chatter=chatter,print_border=True)
    	    if not KeepFiles:
		runShellCommand("rm -rf %s" %ResultsDir)
	    return like
	pass
    pass    
    like.writeXml(xmlFile=src_model_file)    
    return like,files
