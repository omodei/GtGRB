from gtgrb import *
import getpass
import time

def go(lle_dir):
  remotePythonScript            = "remote_process.py"
  userName                      = "grb%s" %(time.time())
  f                             = open(remotePythonScript,'w+')
  f.write("username = '%s'" %(userName))
  f.write('''\n
import ROOT
ROOT.gROOT.SetBatch(True)
import os
import subprocess
from ROOT import std
import getpass

def find_merit_files(trigger, dt=(-100, 1000)):
    tmin = trigger + dt[0]
    tmax = trigger + dt[1]
    opt1 = '(%(tmin)i <= nMetStart && nMetStop <= %(tmax)i)' % locals()
    opt2 = '(nMetStart <= %(tmin)i && %(tmin)i <= nMetStop)' % locals()
    opt3 = '(nMetStart <= %(tmax)i && %(tmax)i <= nMetStop)' % locals()
    command_tpl = " ".join(("/afs/slac/g/glast/ground/bin/datacat find",
                            "\--filter '%s || %s || %s'",
                            "\--sort nMetStart \--group MERIT",
                            "\--site SLAC_XROOT /Data/Flight/Level1/LPA/"))
    command = command_tpl % (opt1, opt2, opt3)
    print command
    pipe = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output = pipe.stdout
    files = std.vector(std.string)()
    for item in output:
        files.push_back(std.string(item.strip()))
    return files


os.system("cd /tmp ; df -h ." )
outdir = '/tmp/%s' %(username)
os.system('mkdir -p %s' %(outdir))
lle_macropath = os.path.join('/tmp/make_LLE_histogram_dur.C')
ROOT.gROOT.LoadMacro(lle_macropath)
  \n''')
  f.write("theta = float('%s')\n" %(lat[0].getGRBTheta()))
  f.write("t90 = float('%s')\n" %(results['GBMT90']))
  f.write("trigger = float('%s')\n" %(grb[0].Ttrigger))
  f.write("ra = float('%s')\n" %(results['RA']))
  f.write("dec = float('%s')\n" %(results['DEC']))
  
  f.write('''\n
meritfiles = find_merit_files(trigger,(-1000,1000))
ROOT.make_LLE_histogram(meritfiles, outdir,trigger,ra,dec,theta,t90,True)
rootfile = "%s/lle_events.root" % outdir
  \n''')
  
  f.close()
  os.system('scp %s/src/macros/make_LLE_histogram_dur.C rhel6-64.slac.stanford.edu:/tmp/ ' %(lle_dir))
  os.system('scp %s rhel6-64.slac.stanford.edu:/tmp/ ' % remotePythonScript)
  os.system('ssh rhel6-64.slac.stanford.edu \"source /afs/slac/g/glast/groups/grb/grbVMutil/grbgrouplogin.csh > /dev/null ; python /tmp/%s\"' % remotePythonScript)
  os.system('scp rhel6-64.slac.stanford.edu:/tmp/%s/lle_events.root %s' %(userName,lat[0].out_dir))
  os.system('ssh rhel6-64.slac.stanford.edu \"rm -rf /tmp/%s\"' %(userName))
