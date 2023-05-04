import ROOT
from math import sqrt
import matplotlib.pyplot as plt

class upperLimit(object):
  def __init__(self,x,ex,y,ey,m,color,marker):
    sigma                     = 2.0
    upArrow                   = (y+sigma*ey)
    downArrow                 = upArrow-0.8*upArrow
    self.arrow                = ROOT.TArrow(x,upArrow,x,downArrow,0.01,"|>")
    self.arrow.SetLineColor(color)
    self.arrow.SetFillColor(color)
    self.line                 = ROOT.TLine(x-ex,upArrow,x+ex,upArrow)
    self.line.SetLineColor(color)
    
    self.upMargin             = upArrow+0.1*upArrow
    self.downMargin           = downArrow-0.1*downArrow
    
    self.marker               = ROOT.TMarker(x,upArrow,marker)
    self.marker.SetMarkerColor(color)
  pass
  
  def Draw(self):
    #Convert from physical system to pad system
    self.arrow.Draw()
    self.line.Draw()
    self.marker.Draw()
  pass
  
  def GetN(self):
    return 1
###

def _divideDatasets(filename):
  data                     = open(filename)
  
  #Parse QDP files   
  dataRows                 = []
  thisData                 = []
  for row in data:
    #Skip comments and commands
    if(row.find("READ")>=0 or row.find("@")>=0 or row.find("!")>=0):
      continue 
    else:
      if(row.find("NO")>=0):
        #End of this dataset
        dataRows.append(thisData)
        thisData           = []
        continue
      else:
        thisData.append(row)
        continue
      pass
    pass
  pass
  #Add the last dataset
  dataRows.append(thisData)
        
  data.close()
  return dataRows
pass

def readQDP(uniqueID,exposure,**kwargs):    
  filetype                    = "spectrum"
  nuFnuUnits                  = "keV"
  for key in kwargs:
    if  (key.lower()=="filename"):              filename = kwargs[key]
    elif(key.lower()=="type")    :              filetype = kwargs[key]
    elif(key.lower()=="nufnuunits")    :        nuFnuUnits = kwargs[key]
  pass
  
  #Read all QDP files and get all the lines in lists: each element of a list contains a list with
  #all rows pertaining to that dataset
  if(filetype=="spectrum" or filetype=="residuals" or filetype=="nuFnu"):
    if(filetype=="spectrum"):
      dataSets                = _divideDatasets(filename[0])
      modelSets               = _divideDatasets(filename[1])                    
    elif(filetype=="residuals"):
      dataSets                = _divideDatasets(filename)
      #This is just to avoid chaning the following loop:
      modelSets               = dataSets
    elif(filetype=="nuFnu"):      
      modelSets               = _divideDatasets(filename)
      dataSets                = map(lambda x:[],modelSets)
    pass

    datasets                  = []
    models                    = []
    ULs                       = []
    minX                      = 1E20
    maxX                      = -1
    minY                      = 1E20
    maxY                      = -1  
        
    for thisData,thisModelData,currentColor in zip(dataSets,modelSets,range(1,len(modelSets)+1)):
    
      if(currentColor>=5):
        #This is to avoid using Yellow (=5) as color on a white background (!)
        currentColor         += 1
      
      #Open a new graph for this dataset
      datasets.append(ROOT.TGraphErrors())

      #Set the colors
      datasets[-1].SetLineColor(currentColor)
      datasets[-1].SetFillColor(0)
      datasets[-1].SetMarkerStyle(currentColor+2)
      datasets[-1].SetMarkerColor(currentColor)      
      
      #add the data to the graph
      #NOTE that this loop won't be executed if filetype=="nuFnu", since thisData is empty in that case
      nPoints                 = 0
      nULs                    = 0
      for thisGraphNpoints,row in enumerate(thisData):
        
        thisLineData          = row.split()      
        x                     = float(thisLineData[0])
        ex                    = float(thisLineData[1])
        y                     = float(thisLineData[2])       
        ey                    = float(thisLineData[3])
        b                     = float(thisLineData[4])
        be                    = float(thisLineData[5])
        m                     = float(thisLineData[6])
        
        if(y<5E-10):
          y                   = 5E-10                
        
        #Update the error bar using model variance
        #Background counts
        bb                      = b*exposure*2.0*ex
        #Model counts
        mm                      = m*exposure*2.0*ex
        
        #Gehrels kludge
        if(bb+mm < 10):
          err                   = 1+sqrt(bb+mm+0.75)
        else:
          #Model weighting
          err                   = sqrt(bb+mm+pow(be*exposure*2.0*ex,2.0))
        pass
        
        #Error on the rate
        ey                      = max(err/exposure/2.0/ex,ey)
        
        if(filetype=="residuals"):
          #Residuals      
          y                     = ((y-m))/(ey)
          ey                    = 1  
          m                     = 0
        pass
        
        #Check if I need to plot Upper Limits
        if(y-ey < 0 and filetype=="spectrum"):
          #This is an UL
          ULs.append(upperLimit(x,ex,y,ey,m,currentColor,currentColor+2))     
          nULs                  += 1
          #Update the maximums, for the range of the Y axis 
          if(ULs[-1].upMargin>maxY):   maxY = ULs[-1].upMargin
          if(ULs[-1].downMargin<minY): minY = ULs[-1].downMargin      
        else:
          #This is a regular point    
          datasets[-1].SetPoint(nPoints,x,y)
          datasets[-1].SetPointError(nPoints,ex,ey)
          nPoints                  += 1
          
          #Update the maximums, for the range of the Y axis
          if(y-ey<minY):       minY = y-ey-0.1*ey      
          if(y+2*ey>maxY):     maxY = y+2*ey             
        pass
        
        #Update the maximums, for the range of the X axis 
        if(x-ex<minX):           minX = max(x-ex,5E-10)
        if(x+ex>maxX):           maxX = x+ex
        
        if(m<minY):              minY = m 
      pass #End of loop on data points            
      
      if(filetype=="spectrum" or filetype=="nuFnu"):
        #Open a new graph for the corresponding model
        models.append(ROOT.TGraph())      
        #Set the colors
        models[-1].SetLineColor(currentColor)
        models[-1].SetFillColor(0)
        models[-1].SetMarkerStyle(currentColor+2)
        models[-1].SetMarkerColor(currentColor)       
        
        for thisGraphNpoints,row in enumerate(thisModelData):
          thisLineData          = row.split()
          x                     = float(thisLineData[0])
          ex                    = float(thisLineData[1])
          m                     = float(thisLineData[2])
          if(filetype=="nuFnu" and nuFnuUnits =="erg"):
            #Convert from keV/s to erg
            m                  *= (1.60217646E-9*exposure)     
          models[-1].SetPoint(thisGraphNpoints,x,m)
          
          #Update maximum and minimum for nuFnu
          if(filetype=="nuFnu"):
            if(x-ex<minX):           minX = max(x-ex-0.1*ex,1E-5)
            if(x+ex>maxX):           maxX = x+ex+0.1*ex
            if(m<minY):              minY = m
            if(m>maxY):              maxY = m
          pass  
        pass
      pass
      
      if(filetype=="nuFnu"):
        #Just one nuFnu, and no model plot needed,
        #no need to continue
        break
      pass
          
    pass #end of loop on data sets
  else:
    raise ValueError("Filetype not known! Possible values are nuFnu, spectrum or residuals.")     
  pass  

  graphObjects                = {}
  graphObjects['canvas']      = ROOT.TCanvas("Spectra %s" %(uniqueID),"Spectra",10,40,1024,768)
  graphObjects['pad']         = ROOT.TPad("pad1 %s" %(uniqueID),"This is pad1",0.02,0.02,0.99,0.99,0)
  graphObjects['pad'].SetLogx()
  if(filetype!="residuals"):    
    graphObjects['pad'].SetLogy()
  pass
  graphObjects['pad'].Draw()
  graphObjects['pad'].cd()
  if(filetype!="residuals"):
    #Guarantee that we don't have negative points (since we will use logarithmic Y axis)
    minY                      = max(minY,5E-10)
    maxY                      = maxY*2
  graphObjects['frame'] = graphObjects['pad'].DrawFrame(max(minX-0.5*minX,5E-10),minY,maxX,maxY)
  
  if(filetype=="spectrum"):
    graphObjects['frame'].GetXaxis().SetTitle("Energy (keV)")
    graphObjects['frame'].GetXaxis().CenterTitle()
    graphObjects['frame'].GetXaxis().SetTitleOffset(1.25)
    graphObjects['frame'].GetYaxis().SetTitle("Raw count rate (counts s^{-1} keV^{-1})")
    graphObjects['frame'].GetYaxis().CenterTitle()
    graphObjects['frame'].GetYaxis().SetTitleOffset(1.30)
    
    for d,m in zip(datasets,models):
      if(d.GetN()>0):
        d.Draw("P same 0")
      if(m.GetN()>0):
        m.Draw("L same")
    pass
    for ul in ULs:
      if(ul.GetN()>0):
        ul.Draw()
    pass
    
    return datasets, models, graphObjects, ULs
    
  elif(filetype=="residuals"):
    
    graphObjects['frame'].GetXaxis().SetTitle("Energy (keV)")
    graphObjects['frame'].GetXaxis().CenterTitle()
    graphObjects['frame'].GetXaxis().SetTitleOffset(1.25)
    graphObjects['frame'].GetYaxis().SetTitle("#chi")
    graphObjects['frame'].GetYaxis().CenterTitle()
    graphObjects['frame'].GetYaxis().SetTitleOffset(1.30)
    
    for d in datasets:
      if(d.GetN()>0):
        d.Draw("P same 0")
    pass
        
    graphObjects['zero']      = ROOT.TF1("Zero","[0]",-100,maxX*2)
    graphObjects['zero'].SetParameter(0,0)
    graphObjects['zero'].SetLineStyle(9)
    graphObjects['zero'].Draw("same")
    
    return datasets, graphObjects 
     
  elif(filetype=="nuFnu"):
    
    graphObjects['frame'].GetXaxis().SetTitle("Energy (keV)")
    graphObjects['frame'].GetXaxis().CenterTitle()
    graphObjects['frame'].GetXaxis().SetTitleOffset(1.25)
    if(nuFnuUnits=="erg"):
      graphObjects['frame'].GetYaxis().SetTitle("E^{2} dN/dE (erg cm^{-2})")
    else:
      graphObjects['frame'].GetYaxis().SetTitle("#nu F_{#nu} (ph. keV cm^{-2} s^{-1})")
    graphObjects['frame'].GetYaxis().CenterTitle()
    graphObjects['frame'].GetYaxis().SetTitleOffset(1.30)
    
    for m in models:
      if(m.GetN()>0):
        m.Draw("L same")
    pass
    return datasets, models, graphObjects, ULs
  
  pass 
pass


def plot(exposure,**kwargs):
  '''
  a,b,c = plot(spectrum=[QDP file], model=[QDP file], nuFnu=[QDP file])
  '''
  ROOT.gROOT.SetStyle("Plain")
  
  mode                        = "both"
  files                       = {}
  datasetsName                = None
  nuFnuUnits                  = "keV"
  for key in kwargs:
    if  (key.lower()=="spectrum"):       files["spectrum"]  = kwargs[key]
    elif(key.lower()=="model"):          files["model"]     = kwargs[key]
    elif(key.lower()=="nufnu"):          files["nuFnu"]     = kwargs[key]
    elif(key.lower()=="datasetsname"):   datasetsName       = kwargs[key]
    elif(key.lower()=="nufnuunits"):     nuFnuUnits         = kwargs[key]
  pass
  
  if(len(files.keys())==0):
    raise ValueError("You have to specify either the 'spectrum' file or the 'nuFnu' file.")
  
  if(files.has_key("spectrum")):
    #Two panels plot
    ds, models, graphObj, uls = readQDP('spectrum',exposure, filename=[files['spectrum'],files['model']],type='spectrum',datasetsName=datasetsName)
    ds2, graphObj2            = readQDP('res', exposure, filename=files['spectrum'],type='residuals',datasetsName=datasetsName)

    graphObjects              = {}
    graphObjects['specGObj']  = graphObj
    graphObjects['resGObj']   = graphObj2
    graphObjects['canvas']    = ROOT.TCanvas("Two panels","Two panels",10,40,1024,768)
    graphObjects['pad1']      = ROOT.TPad("pad1","Spectral pad",0.02,0.30,0.99,0.99,0)
    graphObjects['pad2']      = ROOT.TPad("pad2","Residuals pad",0.02,0.02,0.99,0.30,0)
    graphObjects['pad1'].SetLogx()
    graphObjects['pad2'].SetLogx()    
    graphObjects['pad1'].SetLogy()
    
    ROOT.gStyle.SetPadBorderMode(0)
    ROOT.gStyle.SetFrameBorderMode(0)
    graphObjects['pad1'].SetBottomMargin(0.005)
    graphObjects['pad1'].Draw()
    graphObjects['pad2'].SetTopMargin(0.005)
    graphObjects['pad2'].SetBottomMargin(0.3)    
    graphObjects['pad2'].Draw()
    
    graphObjects['pad1'].cd()

    graphObjects['specGObj']['frame'].GetXaxis().SetTicks("+") 
    graphObjects['specGObj']['frame'].GetXaxis().SetLabelFont(40)   
    graphObjects['specGObj']['frame'].GetYaxis().SetTitleSize(0.05)
    graphObjects['specGObj']['frame'].GetYaxis().SetTitleOffset(0.89)
    graphObjects['specGObj']['frame'].GetYaxis().SetLabelFont(40)
    graphObjects['specGObj']['frame'].GetYaxis().SetLabelSize(0.04)    
    graphObjects['specGObj']['frame'].Draw()
    
    for d,m in zip(ds,models):
      if(d.GetN()>0):
        d.SetLineWidth(2)
        d.Draw("P same 0")
      if(m.GetN()>0):
        m.SetLineWidth(2)
        m.Draw("L same")
    pass
    
    #Now build the legend, if datasetsName is not None
    if(datasetsName!=None):
      #This is to let ROOT compute the right place for the legend...
      l                       = graphObjects['pad1'].BuildLegend()
      l.Clear()      
      for d,title in zip(ds,datasetsName):
        d.SetName(title)
        d.SetTitle(title)
        d.SetFillColor(0)
        l.AddEntry(d,title)
      pass
      l.SetTextFont(40)
      l.SetTextSize(0.04)
      l.SetShadowColor(0)
      l.SetBorderSize(0)
      l.SetFillStyle(0)
      l.SetFillColor(0)
      l.SetNColumns(2)
      l.SetMargin(0.5)
      l.SetTextAlign(12)
      l.SetX1(0.55)
      l.SetX2(0.85)
      l.Draw()
    pass
    
    for ul in uls:
      if(ul.GetN()>0):
        ul.line.SetLineWidth(2)
        ul.Draw()
    pass
        
    graphObjects['pad2'].cd()
    
    graphObjects['resGObj']['frame'].GetXaxis().SetTitleSize(0.11)
    graphObjects['resGObj']['frame'].GetXaxis().SetTitleOffset(1.25)
    graphObjects['resGObj']['frame'].GetXaxis().SetLabelFont(40)
    graphObjects['resGObj']['frame'].GetXaxis().SetLabelSize(0.10)    
    graphObjects['resGObj']['frame'].GetXaxis().SetTickLength(0.07)
    graphObjects['resGObj']['frame'].GetYaxis().SetTitleSize(0.11)
    graphObjects['resGObj']['frame'].GetYaxis().SetTitleOffset(0.38)
    graphObjects['resGObj']['frame'].GetYaxis().SetLabelOffset(0.02)
    graphObjects['resGObj']['frame'].GetYaxis().SetLabelFont(40)
    graphObjects['resGObj']['frame'].GetYaxis().SetLabelSize(0.10)
    graphObjects['resGObj']['frame'].Draw()
    for d in ds2:
      if(d.GetN()>0):
        d.SetLineWidth(2)
        d.Draw("P same")
    pass
    
    graphObjects['canvas'].Update()
    
    sList                     = [ds,models,uls]
    rList                     = [ds2]
    return sList,rList,graphObjects  
  elif(files.has_key("nuFnu")):
    #One panels plot
    ds, models, graphObj, uls = readQDP('nuFnu', exposure, filename=files['nuFnu'],type='nuFnu',nufnuunits=nuFnuUnits)
  
    graphObjects              = {}
    graphObjects['nuFnuGObj']  = graphObj
    graphObjects['canvas']    = ROOT.TCanvas("One panel","One panel",10,40,1024,768)
    graphObjects['pad1']      = ROOT.TPad("pad1","Spectral pad",0,0,1,1,0,0,0)
    graphObjects['pad1'].SetLogx()
    graphObjects['pad1'].SetLogy()

    graphObjects['pad1'].Draw()    
    graphObjects['pad1'].cd()

    graphObjects['nuFnuGObj']['frame'].GetXaxis().SetLabelFont(40)   
    graphObjects['nuFnuGObj']['frame'].GetYaxis().SetTitleSize(0.05)
    graphObjects['nuFnuGObj']['frame'].GetYaxis().SetTitleOffset(0.89)
    graphObjects['nuFnuGObj']['frame'].GetYaxis().SetLabelFont(40)
    graphObjects['nuFnuGObj']['frame'].GetYaxis().SetLabelSize(0.04)    
    graphObjects['nuFnuGObj']['frame'].Draw()
    
    for d,m in zip(ds,models):
      if(m.GetN()>0):
        m.SetLineWidth(2)
        m.Draw("L same")
    pass
    
    graphObjects['canvas'].Update()
    
    sList                     = [ds,models,uls]
    rList                     = []
    return sList,rList,graphObjects  
 
  
pass
