#!/usr/bin/env python

import os
from subprocess import call


As  = [30,35,40,45,50,60,70,80,100,120,150]
tau1s = [4.0,5.0,6.0,7.0]
tau2s = [4.0,5.0,6.0,7.0]
As  = [50]
tau1s = [6.0]
tau2s = [7.0]
back = 20
trig = 0

for tau1 in tau1s:
  for tau2 in tau2s:
    for A in As: 
       logfile = "logfiles/A%sT1_%sT2_%s.log" % (A,tau1,tau2)
       cmdline = "A=%s tau1=%s tau2=%s back=%s trig=%s" %(A,tau1,tau2,back,trig)
       os.system("python ./pipeline/submitJob.py -q long -exe app/LLEtest.py -l %s mode='go' GRBname='GRB090902B' GRBTRIGGERDATE=273582310.31271398 %s" % (logfile, cmdline))
       #call(["python","./pipeline/submitJob.py","-exe app/LLEtest.py -mode 'go' -q long GRBNAME='GRB090902B' "+cmdline])
    pass
  pass   
pass
