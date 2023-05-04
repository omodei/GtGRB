from GTGRB import autofit

nai11 = autofit.detectorConfiguration("NAI_11")
nai11.setChanToIgnore("1-5 23-26 126-128")
nai11.setStatistic("pgstat")

nai10 = autofit.detectorConfiguration("NAI_10")
nai10.setChanToIgnore("1-5 23-26 126-128")
nai10.setStatistic("pgstat")

nai9 = autofit.detectorConfiguration("NAI_09")
nai9.setChanToIgnore("1-4 23-25 126-128")
nai9.setStatistic("pgstat")

nai8 = autofit.detectorConfiguration("NAI_08")
nai8.setChanToIgnore("1-4 22-25 126-128")
nai8.setStatistic("pgstat")

nai7 = autofit.detectorConfiguration("NAI_07")
nai7.setChanToIgnore("1-4 23-25 126-128")
nai7.setStatistic("pgstat")

nai6 = autofit.detectorConfiguration("NAI_06")
nai6.setChanToIgnore("1-3 22-24 126-128")
nai6.setStatistic("pgstat")

nai5 = autofit.detectorConfiguration("NAI_05")
nai5.setChanToIgnore("1-5 23-26 126-128")
nai5.setStatistic("pgstat")

nai4 = autofit.detectorConfiguration("NAI_04")
nai4.setChanToIgnore("1-4 23-25 126-128")
nai4.setStatistic("pgstat")

nai3 = autofit.detectorConfiguration("NAI_03")
nai3.setChanToIgnore("1-5 23-25 126-128")
nai3.setStatistic("pgstat")

nai2 = autofit.detectorConfiguration("NAI_02")
nai2.setChanToIgnore("1-4 22-25 126-128")
nai2.setStatistic("pgstat")

nai1 = autofit.detectorConfiguration("NAI_01")
nai1.setChanToIgnore("1-5 23-26 126-128")
nai1.setStatistic("pgstat")

nai0 = autofit.detectorConfiguration("NAI_00")
nai0.setChanToIgnore("1-4 22-25 126-128")
nai0.setStatistic("pgstat")

bgo0 = autofit.detectorConfiguration("BGO_00")
bgo0.setChanToIgnore("1 126-128")
bgo0.setStatistic("pgstat")

bgo1 = autofit.detectorConfiguration("BGO_01")
bgo1.setChanToIgnore("1-2 126-128")
bgo1.setStatistic("pgstat")

lat = autofit.detectorConfiguration("LAT")
lat.setChanToIgnore("**-1e6")
lat.setStatistic("pgstat")

lle = autofit.detectorConfiguration("LLE")
lle.setChanToIgnore("**-3e4 1e5-**")
lle.setStatistic("pgstat")

bat = autofit.detectorConfiguration("BAT")
bat.setChanToIgnore("**-15.0 150.0-**")
bat.setStatistic("chi")

detectors = {nai0.name:nai0,
             nai1.name:nai1,
             nai2.name:nai2,
             nai3.name:nai3,
             nai4.name:nai4,
             nai5.name:nai5,
             nai6.name:nai6,
             nai7.name:nai7,
             nai8.name:nai8,
             nai9.name:nai9,
             nai10.name:nai10,
             nai11.name:nai11,
             bgo0.name:bgo0,
             bgo1.name:bgo1,
             lat.name:lat,
             lle.name:lle,
             bat.name:bat}
weighting  = 'model'

configuration = {'detectors':detectors,'weighting': weighting}

import pickle
f = open("autofit.conf",'w')
pickle.dump(configuration,f)
f.close()
