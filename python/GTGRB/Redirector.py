#This is a trick to redirect the output sent to cout (for example, by
#C++ libraries) and the produced images to the ipython Notebook
#giacomov@slac.stanford.edu

import threading, time, sys, os, fcntl
import glob, datetime
from gtgrb import *

import matplotlib
matplotlib.rcParams['figure.dpi'] = 150
matplotlib.rcParams['figure.figsize'] = [25,12.5]
import matplotlib.pyplot as plt
plt.ion()

__all__ = ['start_redirect', 'stop_redirect','get_figures','show_figure']

class FigureGetter(object):
  def __init__(self):
    #Save current time
    self.date                 = datetime.datetime.now().timetuple()
  pass
  
  def get_figures(self,debug=False):
    #Print all the figures generated since the last print
    #get the output directory
    try:
      outdir                  = os.path.join(os.environ['OUTDIR'],'%09i' %(float(results['GRBNAME'])))
    except:
      outdir                  = os.path.abspath(".")
    
    #Now show on the stdout all the .png files which have been produced
    #since the last figure I shown    
    imageList                 = []
    for root, subFolders, files in os.walk(outdir):
      for f in files:
        if(f.split(".")[-1]=="png"):
          imageList.append(os.path.join(outdir,root,f))
        pass
      pass
    pass
    
    if(debug):
      print("Current reference date:")
      print self.date
      print("Images considered:")
      for im in imageList:
        print("%s %s" %(im,time.localtime(os.path.getmtime(im))))
    pass
    #Select all the images newer than the last time I printed images
    to_show                   = filter(lambda x:time.localtime(os.path.getmtime(x)) > self.date,imageList)
    if(len(to_show)==0):
      print("No new images to show!")
    else:
      to_show.sort(key=lambda x:os.stat(x).st_mtime)
      for im in to_show:
        self.showFigure(im)
      pass
      self.date                 = time.localtime(os.path.getmtime(to_show[-1]))
    pass
  pass
    
  def showFigure(self,imagePath):
    img                     = plt.imread(imagePath)
    print("File %s:" %(imagePath))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.xaxis.set_ticklabels([None])
    ax.yaxis.set_ticklabels([None])
    ax.xaxis.set_ticks([None])
    ax.yaxis.set_ticks([None])
    plt.imshow(img)
    plt.show()
  pass
pass  
  

# A thread that will redirect the c++ stdout and stderr to the ipython notebook
class T(threading.Thread):

  def __init__(self):
    threading.Thread.__init__(self)
    
    self.go_on                = False
        
    # copy the c++ stdout handler for later
    self.oldhandle            = os.dup(1)
    self.oldhandleStdErr      = os.dup(2)
    
    #Save current time
    self.date                 = datetime.datetime.now().timetuple()  
    # create a pipe and glue the c++ stdout to its write end
    # make the read end non-blocking
    self.piper, self.pipew    = os.pipe()
    os.dup2(self.pipew, 1)
    os.close(self.pipew)
    fcntl.fcntl(self.piper,fcntl.F_SETFL,os.O_NONBLOCK)
    
    #Repeat the same thing for Stderr
    self.pipererr, self.pipewerr = os.pipe()
    os.dup2(self.pipewerr, 2)
    os.close(self.pipewerr)
    fcntl.fcntl(self.pipererr,fcntl.F_SETFL,os.O_NONBLOCK)
    
  def stop(self):
    return
    # when we want to stop the thread put back the c++ stdout where it was
    # clear the pipe
    os.dup2(self.oldhandle, 1)
    os.close(self.piper)
    #same for stderr
    os.dup2(self.oldhandleStdErr, 2)
    os.close(self.pipererr)
    self.go_on                = False
      
  def run(self):
    while self.go_on:
      #self.get_figures()
      # give the system 2.0 seconds to fill up the pipe
      time.sleep(2.0)
      try:
        # read out the pipe and write it to the screen
        # if the pipe was empty it return an error (hence the try-except)
        sys.stdout.write(os.read(self.piper, 50000))
        sys.stdout.flush()
      except:
        pass
      #same thing for stderr
      try:
        # read out the pipe and write it to the screen
        # if the pipe was empty it return an error (hence the try-except)
        sys.stderr.write(os.read(self.pipererr, 50000))
        sys.stderr.flush()
      except:
        pass      
    pass
    return

# flag to know if the thread was started
started                       = False

figureGetter                  = FigureGetter()

# start the redirection
def start_redirect():
  global started
  global a
  if started:
    print "Already redirected c++ output"
  else:
    started                   = True
    print "Redirecting c++ stdout and stderr to python..."
    # start a new redirection thread
    a                         = T()
    a.start()
pass

# stop the redirection
def stop_redirect():
  global started
  global a
  if started:
    started                   = False
    a.stop()
pass

#Collect figures
def get_figures(debug=False):
  global figureGetter
  figureGetter.get_figures(debug)
pass

#Show a particular figure
def show_figure(path):
  '''
  Show a figure in the Notebook. Usage:
  
  show_figure(path)
  
  where path is the absolute path.
  '''  
  global figureGetter
  figureGetter.showFigure(os.path.abspath(os.path.expandvars(os.path.expanduser(path))))
pass
