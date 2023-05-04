from GTGRB import *
from scripts.GRBDictionary import *

# GRBs.update(GBMs)
#GRBs.update(ARRs)
#GRBs.update(ASDCs)


'''
from scripts.GBMGCN import GBMs
GRBs.update(GBMs)

try:
    from parse_xml import GRBs as GRBs_slac
    grbs_slac = GRBs_slac('/u/gl/jchiang/users/GRB/GBM_bursts/GRBs.xml')
    
    for g in sorted(grbs_slac.keys()):
        name = g
        met  = grbs_slac[g].GRB_MET
        ra   = grbs_slac[g].GRB_RA
        dec  = grbs_slac[g].GRB_DEC
        try:
            t90  = grbs_slac[g].GRB_T90
        except:
            t90  = 50
            pass
        err  = grbs_slac[g].GRB_ERROR
        
        GRBs['GCN'+g]=[met,ra,dec,t90,err]
        pass
except:
        print 'WARNING: list of GRBs from slac cannot be read, probably because you are not on a SLAC machine.'
        pass
pass
'''


def GetFullName(grb_name):
    try:
        grb=GRBs[grb_name]
        met=grb['GRBTRIGGERDATE']
        return genutils.met2date(met,'GRBNAME')
    except:
        return grb_name
    pass

def GetDate(grb_name):
    try:
        grb=GRBs[grb_name]
        met=grb['GRBTRIGGERDATE']
        return genutils.met2date(met,'date')
    except:
        return grb_name
    pass

def PrintGRBs(filter='None'):
    latex = True
    grbs  = []

    print '---     LIST OF AVAILABLE GRB ---------------------------------------------------------------------'
    if latex:
        print '\hline'
        print ' NAME & GRBYYMMDDFFF & GRB DATE & R.A.$ Dec & GBM T$_{05}$ & GBM T$_{90}$ & Loc. Err. & Redshift \\\ '
        print '\hline'
        
        for grb in sorted(GRBs.keys()):
            if filter in grb or filter is 'None':
                grbs.append(grb)
                if GRBs[grb]['REDSHIFT']>0:
                    print '%12s & ' % grb,'GRB%s &' % GetFullName(grb),'%s &' % GetDate(grb),'%16.4f & %9.3f & %9.3f & %7s & %7s & %7s & %9.3f\\\ ' % (
                        GRBs[grb]['GRBTRIGGERDATE'],GRBs[grb]['RA'],GRBs[grb]['DEC'],GRBs[grb]['GRBT05'],GRBs[grb]['GRBT90'],GRBs[grb]['ERR'],GRBs[grb]['REDSHIFT'])
                else:
                    print '%12s & ' % grb,'GRB%s &' % GetFullName(grb),'%s &' % GetDate(grb),'%16.4f & %9.3f & %9.3f & %7s & %7s & %7s &  \\\ ' % (
                        GRBs[grb]['GRBTRIGGERDATE'],GRBs[grb]['RA'],GRBs[grb]['DEC'],GRBs[grb]['GRBT05'],GRBs[grb]['GRBT90'],GRBs[grb]['ERR'])
                    pass
                pass
            pass
        pass
    else:                
        print '  *GRB_NAME* GRB%s'%'YYMMDDFFF DATE_TIME_TRIGGER\t\t%16s %9s %9s %7s %7s %9' % ('Trigger_MET','ra','dec','Dur','Loc. Err.')
        print '----------------------------------------------------------------------------------------------------'
        print ' NAME & GRBYYMMDDFFF & GRB DATE & R.A.$ Dec & GBM T$_{05}$ & GBM T$_{90}$ & Loc. Err. & Redshift '        
        for grb in sorted(GRBs.keys()):
            if filter in grb or filter is None:
                grbs.append(grb)
                if GRBs[grb]['REDSHIFT']>0:
                    print '%12s  ' % grb,'GRB%s ' % GetFullName(grb),'%s ' % GetDate(grb),'%16.4f  %9.3f  %9.3f  %7s  %7s  %7s  %9.3f ' % (
                        GRBs[grb]['GRBTRIGGERDATE'],GRBs[grb]['RA'],GRBs[grb]['DEC'],GRBs[grb]['GRBT05'],GRBs[grb]['GRBT90'],GRBs[grb]['ERR'],GRBs[grb]['REDSHIFT'])
                else:
                    print '%12s  ' % grb,'GRB%s ' % GetFullName(grb),'%s ' % GetDate(grb),'%16.4f  %9.3f  %9.3f  %7s  %7s  %7s  ' % (
                        GRBs[grb]['GRBTRIGGERDATE'],GRBs[grb]['RA'],GRBs[grb]['DEC'],GRBs[grb]['GRBT05'],GRBs[grb]['GRBT90'],GRBs[grb]['ERR'])
                    pass
                pass
            pass
        pass
    print '----------------------------------------------------------------------------------------------------'
    print ' SCANNED: %d SELECED: %s' % (len(GRBs.keys()), len(grbs))
    return grbs
