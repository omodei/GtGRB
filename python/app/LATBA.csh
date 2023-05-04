#!/bin/csh

set MET $1
set GRBT05 $2 
set GRBT90 $3 
set RA $4 
set DEC $5 
set ERR $6 
set PHAStart $7 
set PHAStop $8 
set LikeStart $9 
set LikeStop ${10} 

if (${?MET} !=1) then
    echo 'You must supply a MET'
    exit 1
endif

if (${?GRBT05} !=1) then
    echo 'You must supply a GRBT05'
    exit 1
endif

if (${?GRBT90} !=1) then
    echo 'You must supply a GRBT90'
    exit 1
endif

if (${?RA} !=1) then
    echo 'You must supply a RA'
    exit 1
endif

if (${?DEC} !=1) then
    echo 'You must supply a DEC'
    exit 1
endif

if (${?ERR} !=1) then
    echo 'You must supply a ERR'
    exit 1
endif

if (${?MET} !=1) then
    echo 'You must supply a MET'
    exit 1
endif

if (${?PHAStart} !=1) then
    echo 'You must supply a PHAStart'
    exit 1
endif

if (${?PHAStop} !=1) then
    echo 'You must supply a PHAStop'
    exit 1
endif

if (${?LIkeStart} !=1) then
    echo 'You must supply a LIkeStart'
    exit 1
endif

if (${?LIkeStop} !=1) then
    echo 'You must supply a LIkeStop'
    exit 1
endif

runCatalog.py -t -o $HOME/GRBWorkDir/DATA/LATBA -mode LATBA_P7_T -ba $MET $GRBT05 $GRBT90 $RA $DEC $ERR $PHAStart $PHAStop $LikeStart $LikeStop 

