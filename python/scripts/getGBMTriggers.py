#!/usr/bin/env python
import urllib2,ssl
from GTGRB import genutils

ssl._https_verify_certificates(0)

def downloadListGRB(**kwargs):
    grb_dictionary={}
    url='https://heasarc.gsfc.nasa.gov/cgi-bin/W3Browse/w3query.pl?tablehead=name%3dBATCHRETRIEVALCATALOG%5f2%2e0+fermigbrst&Action=Query&Coordinates=%27Equatorial%3a+R%2eA%2e+Dec%27&Equinox=2000&Radius=60&NR=&GIFsize=0&Fields=&varon=trigger_name&varon=trigger_time&varon=ra&varon=dec&varon=error_radius&varon=t90&varon=t90_start&sortvar=trigger_name&ResultMax=1000000&displaymode=BatchDisplay'
    req = urllib2.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    response              = urllib2.urlopen(req,timeout=60)
    text                  = response.read()
    f                     = open("trigcat.txt",'w+')
    f.write(text)
    f.close()
    data             = map(lambda x:x.strip().split("|")[1:-1],text.split("\n")[3:-2])
    #print data
    # Convert RA, Dec from hh mm ss to decimal, and the trigger time from ISO UTC to MET
    for i in range(len(data)):
        triggerName         = data[i][0].strip()
        triggerDate         = data[i][1].strip().replace('T',' ')
        MET                 = genutils.date2met(triggerDate)
        ra                  = genutils.convHMS(data[i][2].strip().replace(' ',':')) #RA in HH:DD:MM.SSS format
        dec                 = genutils.convDMS(data[i][3].strip().replace(' ',':'))
        err                 = float(data[i][4].strip())
        try:    t90         = float(data[i][5].strip())
        except: t90         = 60.0
        try:    t05         = float(data[i][6].strip())
        except: t05         = 0.0
        # print triggerDate, MET, ra, dec, err, t90, t05
        grb_dictionary[triggerName]=[ MET, ra, dec, err, t90, t05,'GRB']
        pass
    return grb_dictionary

def downloadListTrigger(**kwargs):
    grb_dictionary={}
    url= "https://heasarc.gsfc.nasa.gov/cgi-bin/W3Browse/w3query.pl?tablehead=name%3dBATCHRETRIEVALCATALOG%5f2%2e0+fermigtrig&Action=Query&Coordinates=%27Equatorial%3a+R%2eA%2e+Dec%27&Equinox=2000&Radius=60&NR=&GIFsize=0&Fields=&varon=trigger_name&varon=trigger_time&varon=trigger_type&varon=ra&varon=dec&varon=error_radius&varon=localization_source&sortvar=trigger_name&ResultMax=1000000&displaymode=BatchDisplay"
    req = urllib2.Request(url, headers={'User-Agent':'Mozilla/5.0'})                                                                                                                                                        
    response              = urllib2.urlopen(req,timeout=60)
    text                  = response.read()
    f                     = open("trigcat.txt",'w+')
    f.write(text)
    f.close()
    data             = map(lambda x:x.strip().split("|")[1:-1],text.split("\n")[3:-2])
    #print data
    # Convert RA, Dec from hh mm ss to decimal, and the trigger time from ISO UTC to MET
    for i in range(len(data)):
        triggerName         = data[i][0].strip()
        triggerDate         = data[i][1].strip().replace('T',' ')
        MET                 = genutils.date2met(triggerDate)
        triggerType         = data[i][2].strip()        
        ra                  = genutils.convHMS(data[i][3].strip().replace(' ',':')) #RA in HH:DD:MM.SSS format
        dec                 = genutils.convDMS(data[i][4].strip().replace(' ',':'))
        err                 = float(data[i][5].strip())
        localization_source = data[i][6].strip()
        #print triggerDate, MET, ra, dec, err, triggerType, localization_source
        grb_dictionary[triggerName]=[ MET, ra, dec, err, 60, 0, triggerType]
        pass
    return grb_dictionary
