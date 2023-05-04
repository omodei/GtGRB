#! /usr/bin/env python
import cx_Oracle
from datetime import datetime
import os,sys
from GTGRB import genutils
debug =True
'''
_dbtables={'LightCurves':'LightCurves', \
 'FlareEvents':'FlareEvents',\
 'PointSources':'PointSources',\
 'EnergyBands':'EnergyBands',\
 'LatSourceCatalog':'LatSourceCatalog',\
 'DiffuseSources':'DiffuseSources',\
 'TimeIntervals':'TimeIntervals',\
 'Rois':'Rois',\
 'SourceMonitoringConfig':'SourceMonitoringConfig',\
 'Frequencies':'Frequencies',\
 'FlareTestTypes':'FlareTestTypes',\
 'FlareTypes':'FlareTypes',\
 'Flare_COUNTERPART':'Flare_COUNTERPART',\
 'SpectrumTypes':'SpectrumTypes',\
 'SourceTypes':'SourceTypes',\
 'GCNnotices':'GCNnotices',\
 'GRB_Email_List':'GRB_Email_List',\
 'GRB_ASP_Config':'GRB_ASP_Config',\
 'GRBAfterglow':'GRBAfterglow',\
 'GRB':'GRB',\
 'Healpix':'Healpix',\
 'FlareAdvocateResults':'FlareAdvocateResults',\
 'CounterPartCatalog':'CounterPartCatalog'}

'''

def _validator(grb,errMin=0):
	'''
	=======================================
	GRB_ID  =  237693852
	HEALPIX_ID  =  None
	GCN_NAME  =  GRB080714A
	GBM_GRB_ID  =  None
	LAT_GRB_ID  =  None
	LAT_ALERT_TIME  =  237693852
	LAT_RA  =  47.069
	LAT_DEC  =  14.795
	ERROR_RADIUS  =  1.16
	LAT_FIRST_TIME  =  237693852
	LAT_LAST_TIME  =  237693852
	HARDNESS_RATIO  =  0
	GCAT_FLAG  =  0
	PEAK_FLUX  =  None
	PEAK_FLUX_ERROR  =  None
	PEAK_FLUX_TIME  =  None
	FLUENCE_30  =  1.62450403389e-13
	FLUENCE_30_ERROR  =  4.09002041371e-09
	FLUENCE_100  =  1.62353384347e-13
	FLUENCE_100_ERROR  =  4.08757776133e-09
	FLUENCE_1GEV  =  1.6176502728e-13
	FLUENCE_1GEV_ERROR  =  4.07276467153e-09
	FLUENCE_10GEV  =  1.56760870147e-13
	FLUENCE_10GEV_ERROR  =  3.94677480386e-09
	ASP_PROCESSING_LEVEL  =  2
	INITIAL_LAT_RA  =  47.069
	INITIAL_LAT_DEC  =  14.795
	INITIAL_ERROR_RADIUS  =  1.16
	FLUX  =  4.34651229939e-14
	FLUX_ERROR  =  1.09432316954e-09
	IS_UPPER_LIMIT  =  1
	PHOTON_INDEX  =  -1.0050666102
	PHOTON_INDEX_ERROR  =  0.142269990724
	TS_VALUE  =  -6.31029095643e-09
	GCN_NOTICE_FILE  =  /nfs/farm/g/glast/u52/ASP/GCN_Archive/GLAST/237693853
	ASP_GCN_NOTICE_DRAFT  =  /afs/slac/g/glast/ground/links/data/ASP/Results/GRB/237693852/GRB080714A_Notice.txt
	FT1_FILE  =  /nfs/farm/g/glast/u52/ASP/LEO/GRB/237693852/GRB080714A_LAT_3.fits
	LIGHTCURVEFILE  =  None
	SPECTRUMFILE  =  /nfs/farm/g/glast/u52/ASP/LEO/GRB/237693852/GRB080714A_grb_spec.fits
	XML_FILE  =  /nfs/farm/g/glast/u52/ASP/LEO/GRB/237693852/GRB080714A_model.xml
	TS_MAP  =  None
	ADVOCATE  =  None
	ADVOCATE_REPORT_URL  =  None
	=======================================
	'''
	isValid=True

	if(grb['GBM_GRB_ID'] is None):
		grb['GBM_GRB_ID'] = 'NONE'
		pass

	if(grb['LAT_GRB_ID'] is None):
		grb['LAT_GRB_ID'] = 'NONE'
		pass
	
	if(grb['PEAK_FLUX'] is None):
		grb['PEAK_FLUX'] = -1	
		pass
	if(grb['PEAK_FLUX_ERROR'] is None):
		grb['PEAK_FLUX_ERROR'] = -1	
		pass
	if(grb['PEAK_FLUX_TIME'] is None):
		grb['PEAK_FLUX_TIME'] = -1	
		pass
	if(grb['FLUENCE_30'] is None):
		#isValid=False
		isValid=True
		pass
	if(int(grb['GRB_ID']<236563200.0)): # only after july
		isValid=False
		pass
	if(grb['GCN_NAME'] is None): # only after july
		isValid=False
		pass
	if(grb['INITIAL_LAT_RA'] is None or grb['INITIAL_LAT_DEC'] is None or grb['INITIAL_ERROR_RADIUS'] is None): isValid=False
	
	if errMin>0 and grb['INITIAL_ERROR_RADIUS']>errMin:  isValid=False
		
	return isValid

if os.environ['ORACLE_HOME'] == '/usr/oracle':
	#
	# Use encoded passwords from config file.
	#
	db_config = open(os.environ['ASP_DB_CONFIG'], 'r')
	lines = db_config.readlines()
	glastgen = lines[0].strip().encode('rot13').split()
	asp_prod = lines[1].strip().encode('rot13').split()
	asp_dev = lines[2].strip().encode('rot13').split()
	rsp_dev = lines[3].strip().encode('rot13').split()
else:
	#
	# Use Oracle wallet.
	#
	glastgen = ('/@glastgenprod',)
	asp_prod = ('/@asp',)
	asp_dev = ('/@asp-dev',)
	rsp_prod = ('/@rsp',)
	rsp_dev = ('/@rsp-dev',)
	pass

asp_default=asp_prod

class GRBdbmanager:
	def __init__(self):
		connect=asp_default
		self.conn= cx_Oracle.connect(*connect)
		pass
	def close(self):
		self.conn.close()
		pass
	def getGRBs(self, grb_id='*'):
		#sql="select '1' from IS_UPPER_LIMIT order by GRB_ID ASC" 
		sql="select %s from GRB order by GRB_ID ASC" % grb_id
		print sql
		cursor=self.conn.cursor()
		res=cursor.execute(sql)
		colname=cursor.description
		tot=len(colname)
		GRBs={}
		for row in cursor:
			if debug==True: print '======================================='
			GRB={}
			for i in range(0,tot):
				field=colname[i][0]  
				#if field=='GCN_NAME':
				#	GCN_NAMEprint field,' = ',row[i]
				#	pass
				#if(row[i]=='GRB090308937'):
				if debug==True: print field,' = ',row[i]
				GRB[field]=row[i]
				#	pass
				#_PointSourcesFields[colname[i][0]][1].append(row[i])
				pass
			#print GRB['GCN_NAME'],_validator(GRB)
			if _validator(GRB): GRBs[GRB['GCN_NAME']]=GRB
			pass
		cursor.close()
		return GRBs
	
	def getGRBList(self, grb_id='*'):
		#sql="select '1' from IS_UPPER_LIMIT order by GRB_ID ASC" 
		sql="select %s from GRB order by GRB_ID ASC" % grb_id
		print sql
		cursor=self.conn.cursor()
		res=cursor.execute(sql)
		colname=cursor.description
		tot=len(colname)
		GRBs={}
		for row in cursor:
			if debug==True: print '======================================='
			GRB={}
			for i in range(0,tot):
				field=colname[i][0]  
				#if field=='GCN_NAME':
				#	GCN_NAMEprint field,' = ',row[i]
				#	pass
				#if(row[i]=='GRB090308937'):
				if debug==True: print field,' = ',row[i]
				GRB[field]=row[i]
				#	pass
				#_PointSourcesFields[colname[i][0]][1].append(row[i])
				pass
			#print GRB['GCN_NAME'],_validator(GRB)
			if _validator(GRB): GRBs[GRB['GCN_NAME']]=[GRB['GBM_GRB_ID'],GRB['GRB_ID'],GRB['LAT_RA'],GRB['LAT_DEC'],30,GRB['ERROR_RADIUS']]
			
			pass
		cursor.close()
		return GRBs

def Print(grb,t0):
	gcnname=grb['GCN_NAME']
	yymmddl=gcnname .split('GRB')[1]
	MET=grb['LAT_ALERT_TIME']			
	#ra=grb['LAT_RA']
	#dec=grb['LAT_DEC']
	ra=grb['INITIAL_LAT_RA']
	dec=grb['INITIAL_LAT_DEC']

	grbid=grb['GRB_ID']
	DATE=genutils.met2date(float(grbid))
	name=genutils.met2date(float(grbid),"grbname")
	#err=grb['ERROR_RADIUS']
	err=grb['INITIAL_ERROR_RADIUS']
	
	#ts_value = grb['TS_VALUE'] 
	gcn_notice_file = grb['GCN_NOTICE_FILE']		
	
	try:
		if 'FERMI' in gcn_notice_file.upper() or 'GLAST' in gcn_notice_file.upper(): gcn_notice_file='FERMI'
		elif 'SUPERAGILE' in gcn_notice_file.upper(): gcn_notice_file='SUPERAGILE'
		elif 'INTEGRAL' in gcn_notice_file.upper(): gcn_notice_file='INTEGRAL'				
		elif 'SWIFT' in gcn_notice_file.upper(): gcn_notice_file='SWIFT'
		#else : gcn_notice_file='UNKNOWN'
		pass
	except:
		gcn_notice_file='None'
		pass

	try:
		txt= '| %s | %s | %s | %s (%5.1f)| %10.3f | %10.3f | %2.3f | %s   |' %(gcnname, name, DATE,grbid, grbid-t0,ra,dec,err,gcn_notice_file)		
	except:
		txt= '| %s | %s | %s | %s (%5.1f)| %s | %s | %s | %s   |' %(gcnname, name, DATE,grbid, grbid-t0,ra,dec,err,gcn_notice_file)
		pass
	t0=grbid


	return txt,t0


if __name__=="__main__":
	import sys
	print 'Quering the database...'
	try:
		filter = sys.argv[1]
	except:
		filter = None
		pass
	print 'Filtering %s ' % filter
	d=datetime.now()
	db=GRBdbmanager()
	grbs=db.getGRBs()
	db.close()
	print '|| GCN_NAME || GRB NAME || Date || MET || Ra || Dec || Err || TS VALUE || inSAA || Angle with LAT zenith || Add Comments || B/A || ' 

	selected=[]
	for key in sorted(grbs.keys(),reverse=False):
		grb=grbs[key]
		gcnname=grb['GCN_NAME']
		if _validator(grb,errMin=5) and (filter is None or filter in gcnname): selected.append(grb)		
		pass

	t0=0	
	for g in selected:
		txt,t0 = Print(g,t0)
		print txt
	print '--------------------------------------------------'
	print 'ALL: %d, SELECTED %s ' %(len(grbs.keys()), len(selected))
	print '--------------------------------------------------'
	pass
