#!/usr/bin/env python
import os

if __name__=='__main__':
    from optparse import OptionParser
    usg = "\033[1;31m%prog -p par1 [...other options]\033[1;m \n"
    desc = "\033[34mThis is a sample script\033[0m \n"
    
    parser=OptionParser(description=desc,usage=usg)
    parser.add_option("-a","--all",type="string",default=None,help="List all the possible names)")
    parser.add_option("-n","--name",type="string",default=None,help="Name of the GRB. (-a GRB --all GRB to list the possible names)")
    parser.add_option("-r","--ra",type="string",default=None,help="Right Ascension")
    parser.add_option("-d","--dec",type="string",default=None,help="Declination")
    parser.add_option("-m","--met",type="string",default=None,help="Trigger Time")
    parser.add_option("-t","--duration",type="string",default=50,help="Duration of the GRB")
    parser.add_option("-o","--offset",type="string",default=0,help="Offset of the GRB")
    parser.add_option("-p","--phastart",type="string", default=0, help="Start time for the generation of the PHA/RSP file")
    parser.add_option("-P", "--phastop", type="string", default=0, help="Stop time for the generation of the PHA/RSP file")
    parser.add_option("-l","--liketstart",type="string", default=0,help="Start time for the Likelihood analysis")
    parser.add_option("-L","--liketstop",type="string"   , default=0,help="Stop time for the Likelihood analysis")
    parser.add_option("-X","--X11",type="string"   , default='Y',help="Enable/Disable X11 forwarding [Y/n]")
    print dir(parser)
    (options,args) = parser.parse_args()
    
    filter = options.all
    name   = options.name
    met    = options.met
    ra     = options.ra
    dec    = options.dec
    dur    = options.duration
    off    = options.offset
    phastart  = options.phastart
    phastop   = options.phastop
    
    if phastop <= phastart:
        phastart = 0
        phastop  = dur
        pass
    
    
    liketstart = options.liketstart
    liketstop  = options.liketstop
    
    if liketstop <= liketstart:
        liketstart = 0
        liketstop  = dur
        pass
    
    cmd1='-go '
    if options.X11.upper() == 'N':
        cmd1+='-nox '
        pass
    
    cmd0 = None
    
    if filter!=None:
        os.system('app/gtgrb.py -l %s' % filter)
        exit()
            
    if name != None:
        cmd0 = 'grbname=%s PHAstart=%s PHAstop=%s LIKETSTART=%s LIKETSTOP=%s TSTART=-25 TSTOP=250' %(name,phastart,phastop,liketstart,liketstop) 
    else:   
        if (met==None or ra==None or dec==None):  parser.print_usage()
        else: cmd0 = 'RA=%s DEC=%s GRBTRIGGERDATE=%s GRBT05=%s GRBT90=%s PHAstart=%s PHAstop=%s LIKETSTART=%s LIKETSTOP=%s TSTART=-25 TSTOP=250' %(ra,dec,met,off,dur,phastart,phastop,liketstart,liketstop)
        pass

    if cmd0 is not None:
        os.system('app/gtgrb.py -exe app/computeAngularSeparation.py %s %s' % (cmd0,cmd1))
        os.system('app/gtgrb.py -exe app/computeLLE.py %s %s' % (cmd0,cmd1))
        os.system('app/gtgrb.py -exe app/computeSelect.py %s %s' % (cmd0,cmd1))
        os.system('app/gtgrb.py -exe app/computeSelectEnergyDependentROI.py %s %s' % (cmd0,cmd1))        
        os.system('app/gtgrb.py -exe app/computeCompositeLightCurve.py %s REMAKE=true %s' % (cmd0,cmd1))
        os.system('app/gtgrb.py -exe app/computeBKGEPHAfile.py %s %s' % (cmd0,cmd1))
        os.system('app/gtgrb.py -exe app/computeLikelihood.py %s %s' % (cmd0,cmd1))

        pass
