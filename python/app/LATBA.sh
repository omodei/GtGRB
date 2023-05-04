#!/bin/sh 

MET=$1
GRBT05=$2 
GRBT90=$3 
RA=$4 
DEC=$5 
ERR=$6 
PHAStart=$7 
PHAStop=$8 
LikeStart=$9 
LikeStop=${10}

if [ -z "${MET}" ]; then
    echo 'You must supply a MET'
    exit 1
fi

if [ -z "${GRBT05}" ]; then
    echo 'You must supply a GRBT05'
    exit 1
fi

if [ -z "${GRBT90}" ]; then
    echo 'You must supply a GRBT90'
    exit 1
fi

if [ -z "${RA}" ]; then
    echo 'You must supply a RA'
    exit 1
fi

if [ -z "${DEC}" ]; then
    echo 'You must supply a DEC'
    exit 1
fi

if [ -z "${ERR}" ]; then
    echo 'You must supply a ERR'
    exit 1
fi

if [ -z "${PHAStart}" ]; then
    echo 'You must supply a PHAStart'
    exit 1
fi

if [ -z "${PHAStop}" ]; then
    echo 'You must supply a PHAStop'
    exit 1
fi


if [ -z "${LikeStart}" ]; then
    echo 'You must supply a LikeStart'
    exit 1
fi

if [ -z "${LikeStop}" ]; then
    echo 'You must supply a LikeStop'
    exit 1
fi

echo runCatalog.py -o $HOME/GRBWorkDir/DATA/LATBA -mode LATBA_P7_T -ba $MET $GRBT05 $GRBT90 $RA $DEC $ERR $PHAStart $PHAStop $LikeStart $LikeStop 
runCatalog.py -o $HOME/GRBWorkDir/DATA/LATBA -mode LATBA_P7_T -ba $MET $GRBT05 $GRBT90 $RA $DEC $ERR $PHAStart $PHAStop $LikeStart $LikeStop 
