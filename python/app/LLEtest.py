from synthBurst import *

import os
import sys

pd = ListToDict(sys.argv)

Set(**pd)
sys.stdout.flush()
sys.stderr.flush()

os.system('echo \n \n \n')
print("Current Directory:")
sys.stdout.flush()
os.system('pwd')
#os.system('ls *')
print ("\n \n I received this parameters: \n")
print (pd)
print('\n \n \n')
sys.stdout.flush()

sb = synthBurst(float(pd['A']),float(pd['tau1']),float(pd['tau2']),-600,600,float(pd['back']),float(pd['trig']))
t90=sb.getT90()
print("\n\n\n T90 is %s \n\n\n" %(t90))

lat[0].out_dir+="/A%sT1_%sT2_%s" % (pd['A'],pd['tau1'],pd['tau2'])
try:
  os.mkdir(lat[0].out_dir)
except:
  pass
pass

MakeLLELightCurves(task='detection',synthetic=sb)
MakeLLELightCurves(task='duration',synthetic=sb)


