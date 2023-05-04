import sys
import os
import ROOT 
import numpy
import astropy.io.fits as pyfits
from GTGRB import xspecModels
from genutils import runShellCommand

class graphData(object):
  def __init__(self,xvariable,yvariable,xErrM,xErrP,yErrM,yErrP,
                    logX=False,logY=False,title='',xtitle='',ytitle='',
                    xmin=None,xmax=None,ymin=None,ymax=None):
    self.x                     = xvariable
    self.y                     = yvariable
    self.xErrM                 = xErrM
    self.xErrP                 = xErrP
    self.yErrM                 = yErrM
    self.yErrP                 = yErrP
    self.logX                  = logX
    self.logY                  = logY
    self.title                 = title
    self.xtitle                = xtitle
    self.ytitle                = ytitle
    
    #Get maximum and minimum for x and y axes
    if(xmin!=None):
      self.xmin                = xmin
    else:
      self.xmin                = min(self.x)
    if(xmax!=None):
      self.xmax                = xmax
    else:
      self.xmax                = max(self.x)
    if(ymin!=None):
      self.ymin                = ymin
    else:
      self.ymin                = min(self.y)
    if(ymax!=None):
      self.ymax                = ymax
    else:  
      self.ymax                = max(self.y)
    
    #Define my color paletter    
    #number                     = 2
    #red                        = numpy.array([1.0,0.0])
    #green                      = numpy.array([0.0,1.0])
    #blue                       = numpy.array([0.0,1.0])
    #stops                      = numpy.array([0.0,1.0])
    #self.startIndex            = ROOT.TColor.CreateGradientColorTable(number,stops,red,green,blue,
    #                                                                  len(self.x))
    #Produce a graph for every point
    self.graphs                = []
    for i in range(len(self.x)):
      if(self.x[i] < self.xmin or self.x[i] > self.xmax 
         or self.y[i] < self.ymin or self.y[i] > self.ymax):
         self.graphs.append(ROOT.TGraphAsymmErrors())
         #Add no points!
         continue
      pass   
      self.graphs.append(ROOT.TGraphAsymmErrors())
      #Insert the fake points to get always the same axis range
      self.graphs[-1].SetPoint(0,self.xmin,self.ymin)
      self.graphs[-1].SetPointError(0,0.0,0.0,0.0,0.0)
      self.graphs[-1].SetPoint(1,self.xmax,self.ymax)
      self.graphs[-1].SetPointError(1,0.0,0.0,0.0,0.0)
      self.graphs[-1].SetPoint(2,self.x[i],self.y[i])
      if(self.xErrM[i]==0 and self.xErrP[i]==0 and self.yErrM[i]==0 and self.yErrP[i]==0):
        #No errors, set the marker
        self.graphs[-1].SetMarkerStyle(7)
      else:  
        self.graphs[-1].SetPointError(2,self.xErrM[i],self.xErrP[i],
                                        self.yErrM[i],self.yErrP[i])                                       
      self.graphs[-1].GetXaxis().SetTitle(xtitle)
      self.graphs[-1].GetXaxis().CenterTitle()
      self.graphs[-1].GetYaxis().SetTitle(ytitle)
      self.graphs[-1].GetYaxis().CenterTitle()
      self.graphs[-1].SetTitle(title)                                     
    pass
  pass
                   
###

class interval(object):
  def __init__(self,start,stop,color):
    self.start                 = start
    self.stop                  = stop
    self.color                 = color
  pass
  
  def contains(self,time):
    if(time>=self.start and time<=self.stop):
      return True
    else:
      return False
    pass
  pass        
###

class spectralMovie(object):
  def __init__(self,lightcurveFileName,firstInterval=1,lastInterval=None):
    self.rootCounts            = ROOT.TFile("countsSpectra.root","READ")
    self.rootNuFnu             = ROOT.TFile("nuFnuSpectra.root","READ")
    
    self.lightCurveFile        = ROOT.TFile(lightcurveFileName,"READ")        
    self.lightCurve            = self.lightCurveFile.Get("constantSN_lc")
    self.autofit_res           = pyfits.open("autofit_res.fits")
    self.graphs                = []
    self.intervals             = []
    self.firstInterval         = firstInterval
    if(lastInterval==None):
      self.lastInterval        = len(self.autofit_res[1].data)
    else:
      self.lastInterval        = lastInterval
  pass
  
  def setColorInterval(self,start,stop,color):
    self.intervals.append(interval(start,stop,color))
  pass
  
  def getColorForThisTime(self,time):
    for interval in self.intervals:
      if(interval.contains(time)):
        return interval.color
      pass
    pass
    #if we are here, no intervals have been defined
    return ROOT.kBlack
  pass
  
  def addGraph(self,xvariable,yvariable,**kwargs):
    
    errors                     = True
    logX                       = False
    logY                       = False
    title                      = ""
    xmin                       = None
    xmax                       = None
    ymin                       = None
    ymax                       = None
    for key in kwargs.keys():
        if   key.lower()=="errors":             errors    = bool(kwargs[key])
        elif key.lower()=="logx"  :             logX      = bool(kwargs[key])
        elif key.lower()=="logy"  :             logY      = bool(kwargs[key])
        elif key.lower()=="title" :             title     = str(kwargs[key])
        elif key.lower()=="xmin"  :             xmin      = float(kwargs[key])
        elif key.lower()=="xmax"  :             xmax      = float(kwargs[key])
        elif key.lower()=="ymin"  :             ymin      = float(kwargs[key])
        elif key.lower()=="ymax"  :             ymax      = float(kwargs[key])        
    pass
    
    #Get the data for the graph
    xvector                    = numpy.array(self.autofit_res[1].data.field(xvariable))
    yvector                    = numpy.array(self.autofit_res[1].data.field(yvariable))
    if(errors):
      xvectorErrM              = numpy.array(self.autofit_res[1].data.field("%s_ErrM" % (xvariable)))*(-1)
      xvectorErrP              = numpy.array(self.autofit_res[1].data.field("%s_ErrP" % (xvariable)))
      yvectorErrM              = numpy.array(self.autofit_res[1].data.field("%s_ErrM" % (yvariable)))*(-1)
      yvectorErrP              = numpy.array(self.autofit_res[1].data.field("%s_ErrP" % (yvariable)))
    else:
      #set all errors to zero
      xvectorErrM              = xvector-xvector
      xvectorErrP              = xvector-xvector
      yvectorErrM              = xvector-xvector
      yvectorErrP              = xvector-xvector
    pass  
    
    #Get fancy names for the variables
    try:      
      xModelSuffix               = xvariable.split("_")[0]+"_"
      xModelFancyName            = xspecModels.suffixToFancyName(xModelSuffix)
      xFancyName                 = xspecModels.allModels[xModelFancyName].parameters[xvariable].fancyName
    except:
      xFancyName                 = xvariable
    pass
      
    try: 
      yModelSuffix               = yvariable.split("_")[0]+"_"
      yModelFancyName            = xspecModels.suffixToFancyName(yModelSuffix)
      yFancyName                 = xspecModels.allModels[yModelFancyName].parameters[yvariable].fancyName
    except:
      yFancyName                 = yvariable
    pass
      
    nPoints                    = len(xvector)
    
    if(xmin==None):
      xmin                     = min(xvector[self.firstInterval-1:self.lastInterval])
      idx                      = list(xvector[self.firstInterval-1:self.lastInterval]).index(xmin)
      xmin                    -= xvectorErrM[self.firstInterval-1:self.lastInterval][idx]
    if(xmax==None):
      xmax                     = max(xvector[self.firstInterval-1:self.lastInterval])
      idx                      = list(xvector[self.firstInterval-1:self.lastInterval]).index(xmax)
      xmax                    += xvectorErrP[self.firstInterval-1:self.lastInterval][idx]
    if(ymin==None):
      ymin                     = min(yvector[self.firstInterval-1:self.lastInterval])
      idx                      = list(yvector[self.firstInterval-1:self.lastInterval]).index(ymin)
      ymin                    -= yvectorErrM[self.firstInterval-1:self.lastInterval][idx]
    if(ymax==None):
      ymax                     = max(yvector[self.firstInterval-1:self.lastInterval])
      idx                      = list(yvector[self.firstInterval-1:self.lastInterval]).index(ymax)
      ymax                    += yvectorErrM[self.firstInterval-1:self.lastInterval][idx]
    print("X range: %s - %s , Y range: %s - %s" %(xmin,xmax,ymin,ymax))
    #Build the TGraph
    self.graphs.append(graphData(xvector,yvector,xvectorErrM,xvectorErrP,yvectorErrM,yvectorErrP,
                                 logX,logY,title,xFancyName,yFancyName,xmin,xmax,ymin,ymax))
  
  pass
  
  def makeMovie(self, filename,modelFancyName,frameDuration=50):
    #Loop over the time intervals
    intID                      = self.firstInterval
    
    ROOT.gROOT.SetStyle("Plain")
    
    try:
      runShellCommand("rm -rf spectralMovie")
      os.mkdir("spectralMovie")
    except:
      pass
    pass
      
    print("Writing frames...")
    try:
      os.remove(filename)
    except:
      pass
    pass    
    
    #Adjust the light curve
    self.lightCurve.GetXaxis().SetTitle("Time since trigger (s)")
    self.lightCurve.GetXaxis().CenterTitle()
    self.lightCurve.GetYaxis().SetTitle("Flux (ph. s^{-1})")
    self.lightCurve.GetYaxis().CenterTitle()
    boxes                      = []
    colors                     = [ROOT.kCyan,ROOT.kGreen,ROOT.kBlue,ROOT.kYellow,ROOT.kYellow,ROOT.kYellow,ROOT.kBlue]
    colorIndex                 = -1
    downFlux                   = False
    while(intID<=self.lastInterval):      
      if(self.lightCurve.GetBinContent(intID)<11000):
        if(downFlux==False):
          print("Switching to gray")
        thisColor            = ROOT.kGray
        downFlux             = True
      else:          
        if(downFlux):                        
          colorIndex          += 1
          print("Switching to color %s" %(colorIndex))
          downFlux             = False
        pass
        thisColor            = colors[colorIndex] 
      pass
      try:
        countsCanvas           = self.rootCounts.Get("%s_%i_%s" %(modelFancyName,intID,"counts"))        
        countsPad              = countsCanvas.GetPrimitive("pad1")        
        gr                     = countsPad.GetPrimitive("hframe").GetXaxis().SetRangeUser(10,1e7)
        gr                     = countsPad.GetPrimitive("hframe").GetYaxis().SetRangeUser(1E-6,1000.0)
        
        resPad                 = countsCanvas.GetPrimitive("pad2")
        gr                     = resPad.GetPrimitive("hframe").GetXaxis().SetRangeUser(10,1e7)
        gr                     = resPad.GetPrimitive("hframe").GetYaxis().SetRangeUser(-5.0,5.0)
        
        nuFnuCanvas            = self.rootNuFnu.Get("%s_%i_%s" %(modelFancyName,intID,"nuFnu"))
        nuFnuPad               = nuFnuCanvas.GetPrimitive("pad1")
        gr                     = nuFnuPad.GetPrimitive("hframe").GetXaxis().SetRangeUser(10,1e7)
        gr                     = nuFnuPad.GetPrimitive("hframe").GetYaxis().SetRangeUser(1E-1,1E4)
        
        thisCanvas             = ROOT.TCanvas()
        thisCanvas.Clear()
        thisCanvas.Draw()
        thisCanvas.SetWindowSize(1024,768)
        thisCanvas.SetCanvasSize(1024,768)        
        thisCanvas.Divide(2,1)
        
        #Plot the light curve, with the current bin in evidence
        leftPad                = thisCanvas.cd(1)
        leftPad.Divide(1,3)
        leftPad.cd(1)
        self.lightCurve.Draw()

        lowEdge                = self.lightCurve.GetBinLowEdge(intID)
        center                 = self.lightCurve.GetBinCenter(intID)
        hiEdge                 = self.lightCurve.GetBinLowEdge(intID)+self.lightCurve.GetBinWidth(intID)

        #Change the color for the graph corresponding to this point
        #thisColor              = self.getColorForThisTime(intID)
        
        boxes.append(ROOT.TBox(lowEdge,self.lightCurve.GetMinimum(),hiEdge,self.lightCurve.GetBinContent(intID)))        
        boxes[-1].SetFillColor(thisColor)
        boxes[-1].SetFillStyle(3004)
        boxes[-1].SetLineColor(thisColor)
        #Draw all boxes from the beginning to now
        for box in boxes:
          box.Draw("same")
        pass                 
        
        #plot the spectrum
        subpad                 = leftPad.cd(2)
        subpad.cd()
        countsPad.SetPad(0.02,0.30,0.99,0.99)
        resPad.SetPad(0.02,0.02,0.99,0.30)       
        ROOT.gStyle.SetPadBorderMode(0)
        ROOT.gStyle.SetFrameBorderMode(0)        
        countsPad.SetBottomMargin(0.005)
        #Reset symbols to a single pixel (symbols are too large for this multi-panel plot)
        for thisPrim in countsPad.GetListOfPrimitives():
          try:
            thisPrim.SetMarkerStyle(1)
          except:
            pass
        for thisPrim in resPad.GetListOfPrimitives():
          try:
            thisPrim.SetMarkerStyle(1)
          except:
            pass
              
        countsPad.Draw()
        resPad.SetTopMargin(0.005)
        resPad.SetBottomMargin(0.3)    
        resPad.Draw()        
        
        #plot the nuFnu
        leftPad.cd(3)
        nuFnuPad.Draw()
        
        #Plot the graphs
        rightPad               = thisCanvas.cd(2)        
        rightPad.Divide(1,len(self.graphs))                

        for i,gr in enumerate(self.graphs):
          gr.graphs[intID-1].SetMarkerColor(thisColor)
          gr.graphs[intID-1].SetLineColor(thisColor)
          gr.graphs[intID-1].SetFillColor(0)
        
          thisPad              = rightPad.cd(i+1)
          if(gr.logX):
            thisPad.SetLogx()
          if(gr.logY):
            thisPad.SetLogy()
          frame                = thisPad.DrawFrame(gr.xmin,gr.ymin,gr.xmax,gr.ymax)
          frame.GetXaxis().SetTitle(gr.xtitle)
          frame.GetXaxis().CenterTitle()
          frame.GetXaxis().SetMoreLogLabels()
          frame.GetYaxis().SetTitle(gr.ytitle)
          frame.GetYaxis().CenterTitle()
          frame.GetYaxis().SetMoreLogLabels()
          frame.SetTitle(gr.title)
          #Draws all the points from the first one to the current one
          for j in range(self.firstInterval-1,intID):
            if(gr.graphs[j].GetN()<1):
              continue
            else:  
              gr.graphs[j].Draw("P same")
          pass 
        pass

        #Save this frame
        thisCanvas.Update()
        thisCanvas.Print("spectralMovie/frame%.5i_%s" %(intID,filename));
        sys.stderr.write("%i " %(intID))
        
        intID                 += 1
      except:
        print("Skipping frame %s" %(intID))
        intID                 += 1
    pass
    print("Generating the movie merging the frames...")
    runShellCommand("convert -delay %s -loop 1 spectralMovie/frame*.gif %s" %(frameDuration,filename))
    print("Done")
  pass
  
  def __del__(self):
    self.rootCounts.Close()
    self.rootNuFnu.Close()
    self.lightCurveFile.Close()
    self.autofit_res.close()
  pass
###
