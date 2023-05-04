#author: Giacomo Vianello (giacomov@slac.stanford.edu)

#This file contains the definitions of the models to be used by Autofit for the automatic fitting


#This define the known models with all the parameters and names
models                         = {}
sufToFancy                     = {}

allModels                      = {}
allSufToFancy                  = {}

###### AD-HOC definitions of models
adHocDefinitions               = ["mdefine logParabola (E/piv)^(-a - b*LOG(E/piv))",
                                  "mdefine asymLogP (E/E0)^(-a - b*LOG(1+(E/E0)))",
                                  "mdefine logParabolaEp 10.0^(-beta*(LOG(E/ep))^2)/E^2",
                                  "mdefine sbpl ((E/piv)^((alpha+beta)/2.0))*( (exp(log(E/E0)/delta)+exp(-log(E/E0)/delta))/(exp(log(piv/E0)/delta)+exp(-log(piv/E0)/delta))  )^((beta-alpha)/2.0*delta*ln(10))"]

class xspecModelParameter(object):
  def __init__(self,modelName,modelSuffix,paramName,fancyName):
    self.modelName             = modelName
    self.modelSuffix           = modelSuffix
    self.paramName             = paramName
    self.fancyName             = fancyName
  pass
  
  def getUglyName(self):
    return "%s%s_%s" % (self.modelSuffix,self.modelName,self.paramName)
  pass
  
  def getFancyName(self):
    return self.fancyName
  pass
###


class xspecModel(object):
  def __init__(self, name, fancyName, suffix, adHocDefinition=""):
    import re,os
    self.initExpression        = []
    self.name                  = name
    self.fancyName             = fancyName
    self.suffix                = suffix
    
    #This is a name which can be used as namefile (something like "grbm_T_pegpwrlw_P_bbody")
    self.modelFilename         = name
    
    #Look if there are table models here
    m                          = re.search('(.*)([m|a]table\{.*\})(.*)',name)
    if(m!=None):
      #Yes
      #Get the name of the table
      tablePath                = re.search('{(.+)}',m.group()).groups()[0]
      tableName                = os.path.basename(tablePath).split(".")[0]
      self.modelFilename       = ''.join([m.groups()[0],tableName,m.groups()[2]])
    pass
    
    self.modelFilename         = self.modelFilename.replace('+','_P_')
    self.modelFilename         = self.modelFilename.replace('-','_M_')
    self.modelFilename         = self.modelFilename.replace('*','_T_')
    self.modelFilename         = self.modelFilename.replace('/','_D_')
    self.modelFilename         = self.modelFilename.replace('{','-')
    self.modelFilename         = self.modelFilename.replace('}','-')
    self.modelFilename         = self.modelFilename.replace('.','_')
    
    self.parameters            = {}
    self.parList               = []
    self.nParameters           = 0
    
    if(adHocDefinition!=""):
      #This model has an ad hoc definition (to be used with mdefine in xspec)
      self.hasAdHocDefinition  = True
      self.adHocDefinition     = adHocDefinition
    else:
      self.hasAdHocDefinition  = False
      self.adHocDefinition     = adHocDefinition
    pass
    
    self.stepparString         = None
  pass
  
  def addInitExpression(self,initExpression):
    #This is to add more than one init expression: Autofit will try to fit
    #the model starting from each of the init expressions, and then will 
    #take the best fit between them: this is to soften the problem of the dependency
    #from the initial parameters
    self.initExpression.append(initExpression)
  pass
  
  def setStepparString(self,stepparString):
    #This string provides the limit and the number of steps for the steppar command,
    #which is used to achieve some global minimization capability
    self.stepparString         = stepparString
  pass
  
  def addParameter(self, componentName, paramName, fancyName):
    tp                         = xspecModelParameter(componentName,self.suffix,paramName,fancyName)
    self.parameters[tp.getUglyName()] = tp
    self.parList.append(tp)
    self.nParameters          += 1
  pass
  
###

def addModel(xspecExpression,fancyName,suffix,initExpression,parToPrint,adHocDefinition=""):  
  '''
    addModel(xspecExpression,fancyName,suffix,initExpression,parToPrint[adHocDefinition])
    
    Parameters:
      xspecExpression            The expression you would use in Xspec to define the model
                                 (example: "abs(grbm+powerlaw)")
      fancyName                  A name which will be used in the tables (like "Band model")
      suffix                     The suffix which will be used in the FITS tables for this model.
                                 IT MUST END WITH "_" (example: "B_")
      initExpression             The expression to init the parameters of the model. Parameters
                                 are divided by a "&" character. For example, this is the init expression
                                 for a model with 3 parameters:
                                 Example: "-1 & -2 0.1 -10 -10 10 10 & 1.0"
      parToPrint                 A list of the parameters to print in the summary tables, with the component
                                 they belong to, their name (as in Xspec), and a fancy name to use when printing.
                                 For example, suppose we are adding a model like this: "pegprlw+pegpwrlw" (two power laws).
                                 Suppose we are interested in printing just the two photon indexes. Then:
                                 ["pegpwrlw,PhoIndex,Photon index 1","pegprlw1,PhoIndex,Photon Index 2"]                           
      adHocDefinition            This string will be passed to a "mdefine" command in Xspec. You can
                                 use it if the model you want to use is not contained in Xspec. For
                                 example, you can define and use a polynomial model like this:
                                 addModel("polynomial3","Polynomial of degree 3","Poly_","a*E+b*E^2+c*E^3")
                                                                                        
  '''
  global models
  global sufToFancy
  global allSufToFancy
  global allModels
    
  thisModel                   = xspecModel(xspecExpression,fancyName,suffix,adHocDefinition)
  try:
    for init in initExpression:
      if(len(init)==1):
        #I am probably iterating a string
        raise ValueError("")
      pass
      thisModel.addInitExpression(init)
    pass
  except:
    #Assume the user gave us just one init expression
    thisModel.addInitExpression(initExpression)
  pass
  
  for string in parToPrint:
    par                       = string.split(",")
    thisModel.addParameter(par[0],par[1],par[2])
  pass
  
  models[thisModel.fancyName] = thisModel
  sufToFancy[thisModel.suffix]= thisModel.fancyName
  
  allModels[thisModel.fancyName] = thisModel
  allSufToFancy[thisModel.suffix]= thisModel.fancyName
pass

def useModels(modelsToUse):
  global models
  global sufToFancy
  global allSufToFancy
  global allModels
  
  suffixList                   = modelsToUse.split(',')
  newModels                    = {}  
  newSufToFancy                = {}  
  
  for suffix in suffixList:
    try:
      suffix                   = suffix.strip("_")+"_"
      fancyName                = allSufToFancy[suffix]
      newModels[fancyName]     = allModels[fancyName]
      newSufToFancy[suffix]    = fancyName 
    except:
      print("Model suffix %s is unknown" %(suffix.strip("_")))
    pass
  pass
  
  models                       = newModels
  sufToFancy                   = newSufToFancy  
pass

def listModels():
  global allSufToFancy
  
  print("\nKnown models (use listActiveModels() to see the currently active models):\n")
  print("%-30s %-20s" %("Model name","Suffix"))
  print("---------------------------------------------")
  for suffix in sorted(allSufToFancy, key=allSufToFancy.get):     
    fancyName                 = allSufToFancy[suffix]
    print("%-30s %-20s" %(fancyName,suffix.strip("_")))
  pass
pass

def listActiveModels():
  global sufToFancy
  print("\nActive models:\n")
  print("%-30s %-20s" %("Model name","Suffix"))
  print("---------------------------------------------")
  for suffix in sorted(sufToFancy, key=sufToFancy.get):     
    fancyName                 = sufToFancy[suffix]    
    print("%-30s %-20s" %(fancyName,suffix.strip("_")))
  pass  
pass

def suffixToFancyName(suffix):
  return allSufToFancy[suffix]
pass

#Band model
Band                           = xspecModel('grbm', 'Band', 'B_')
alphaInitValues                = [-0.5,-1]
betaInitValues                 = [-2,-2.5]
e0InitValues                   = [50,200,500,1000]
for a in alphaInitValues:
  for b in betaInitValues:
    for e0 in e0InitValues:
      Band.addInitExpression("& %s & %s 0.1 -10 -9 -0.01 -0.01 & %s 10 5 10 1e5 1e5 & 0.1" %(a,b,e0))
    pass
  pass
pass    
Band.addParameter("grbm","alpha","alpha")
Band.addParameter("grbm","beta","beta")
Band.addParameter("grbm","tem","E0")
Band.setStepparString("na & -3 -1.9 30 & na & na ")
models[Band.fancyName]         = Band
sufToFancy[Band.suffix]        = Band.fancyName

#Smoothly broken power law (Ryde 1998, http://arxiv.org/abs/astro-ph/9811462)
SBPL                             = xspecModel('sbpl','Smoothly Broken PL.', 'S_')
SBPL.addInitExpression('& 500 -1 & -1.5 0.1 -10 -10 10 10 & -2.5 0.1 -10 -9 -0.01 -0.01 & 500 5 5 10 1e7 1e7 & 0.1 0.001 1E-8 1E-6 500 1000 & 1')
SBPL.addParameter("sbpl","alpha","alpha")
SBPL.addParameter("sbpl","beta","beta")
SBPL.addParameter("sbpl","E0","Break energy")
SBPL.addParameter("sbpl","delta","Transition width")
models[SBPL.fancyName]         = SBPL
sufToFancy[SBPL.suffix]        = SBPL.fancyName

#Smoothly broken power law + power law
SBPLPL                           = xspecModel('sbpl+pegpwrlw','SBPL+PL', 'SP_')
SBPLPL.addInitExpression('& 500 -1 & -1.0 0.1 -10 -10 10 10 & -2.0 0.1 -10 -9 -0.01 -0.01 & 500 5 5 10 1e7 1e7 & 0.1 0.001 1E-8 1E-6 500 1000 & 1 &  2.5 0.1 0.01 0.01 9 10 & 1e3 -1 & 1e6 -1 & 50000')
SBPLPL.addParameter("sbpl","alpha","alpha")
SBPLPL.addParameter("sbpl","beta","beta")
SBPLPL.addParameter("sbpl","E0","Break energy")
SBPLPL.addParameter("sbpl","delta","Transition width")
SBPLPL.addParameter("pegpwrlw","PhoIndex","Ph. index")
models[SBPLPL.fancyName]       = SBPLPL
sufToFancy[SBPLPL.suffix]      = SBPLPL.fancyName

#Comptonized model
Comptonized                    = xspecModel("pegpwrlw*highecut","Comptonized", "C_")
alphaInitValues                = [0,0.5,1,1.5]
e0InitValues                   = [50,200,500,1000]
for a in alphaInitValues:
  for e0 in e0InitValues:
    Comptonized.addInitExpression("& %s & 1e2 -1 & 1e2 -1 & 4000 & 0 -1 0 0 1 1 & %s 10 5 10 1e7 1e7" %(a,e0))    
  pass
pass  
Comptonized.addParameter("pegpwrlw","PhoIndex","Ph. index")
Comptonized.addParameter("highecut","foldE","Cutoff en.")
models[Comptonized.fancyName]  = Comptonized
sufToFancy[Comptonized.suffix] = Comptonized.fancyName

Powerlaw                       = xspecModel("pegpwrlw","Power law","P_")
Powerlaw.addInitExpression("& 2.5 & 1e4 -1 & 1e5 -1 & 1")
Powerlaw.addParameter("pegpwrlw","PhoIndex","Ph. index")
models[Powerlaw.fancyName]     = Powerlaw
sufToFancy[Powerlaw.suffix]    = Powerlaw.fancyName

#Powerlaw with constant photon index
PowerlawFixed                  = xspecModel("cons*pegpwrlw","Power law/cons. Ph.index","PF_")
PowerlawFixed.addInitExpression("& 1 -1 & 2.5 -1 & 1e5 -1 & 1e6 -1 & 1")
PowerlawFixed.addParameter("pegpwrlw","PhoIndex","Ph. index")
models[PowerlawFixed.fancyName]= PowerlawFixed
sufToFancy[PowerlawFixed.suffix]    = PowerlawFixed.fancyName


#Band+Powerlaw
BandPowerlaw                   = xspecModel("grbm+pegpwrlw","Band + power law","BP_")
alphaInitValues                = [0,-0.5,-1]
betaInitValues                 = [-2,-2.5]
e0InitValues                   = [50,200,500,1000]
for a in alphaInitValues:
  for b in betaInitValues:
    for e0 in e0InitValues:
      BandPowerlaw.addInitExpression("& %s & %s 0.1 -10 -9 -0.01 -0.01 & %s 10 5 10 1e5 1e5 & 0.01 & 2.2 & 1e4 -1 & 1e4 -1 & 10" %(a,b,e0))
    pass
  pass
pass 
BandPowerlaw.addParameter("grbm","alpha","alpha")
BandPowerlaw.addParameter("grbm","beta","beta")
BandPowerlaw.addParameter("grbm","tem","E0")                                            
BandPowerlaw.addParameter("pegpwrlw","PhoIndex","Ph. index (pow.)")
models[BandPowerlaw.fancyName] = BandPowerlaw
sufToFancy[BandPowerlaw.suffix]    = BandPowerlaw.fancyName

#Band+Comptonized
BandCompt                   = xspecModel("grbm+pegpwrlw*highecut","Band + Compt.","BC_")
alphaInitValues                = [0,-0.5,-1]
betaInitValues                 = [-2]
e0InitValues                   = [50,200,500,1000]
cutoffInitValues               = [5e4,1e6]
for a in alphaInitValues:
  for b in betaInitValues:
    for e0 in e0InitValues:
      for c in cutoffInitValues:
        BandCompt.addInitExpression("& %s & %s 0.1 -10 -9 -0.01 -0.01 & %s 10 5 10 1e5 1e5 & 0.01 & 2 & 1e4 -1 & 1e4 -1 & 10 & 0 -1 0 0 1 1 & %s 1e3 10 10 1e9 1e9" %(a,b,e0,c))
      pass
    pass
  pass
pass 
BandCompt.addParameter("grbm","alpha","alpha")
BandCompt.addParameter("grbm","beta","beta")
BandCompt.addParameter("grbm","tem","E0")                                            
BandCompt.addParameter("pegpwrlw","PhoIndex","Ph. index (pow.)")
BandCompt.addParameter("highecut","foldE","Cutoff en.")
models[BandCompt.fancyName] = BandCompt
sufToFancy[BandCompt.suffix]    = BandCompt.fancyName

#Band + black body
BandBBody                      = xspecModel("grbm+bbody","Band + black body","BBk_")
alphaInitValues                = [-0.25,-1]
betaInitValues                 = [-2,-2.5]
e0InitValues                   = [100,500,1000]
TInitValues                    = [15,60,100]
for a in alphaInitValues:
  for b in betaInitValues:
    for e0 in e0InitValues:
      for T in TInitValues:
        BandBBody.addInitExpression("& %s & %s 0.1 -10 -9 -0.01 -0.01 & %s 10 5 10 1e5 1e5 & 0.01 & %s 1.0 0.1 0.1 1000 1000 & 1.0" %(a,b,e0,T))
      pass
    pass
  pass
pass
BandBBody.addParameter("grbm","alpha","alpha")
BandBBody.addParameter("grbm","beta","beta")
BandBBody.addParameter("grbm","tem","E0")
BandBBody.addParameter("bbody","kT","T")
models[BandBBody.fancyName]    = BandBBody
sufToFancy[BandBBody.suffix]    = BandBBody.fancyName

#Comptonized+ Black body model
ComptonizedBBody               = xspecModel("pegpwrlw*highecut+bbody","Compt. + black body", "CB_")
alphaInitValues                = [0,0.5,1,1.5]
e0InitValues                   = [50,200,500,1000]
TInitValues                    = [15,60,100]
for a in alphaInitValues:
  for e0 in e0InitValues:
    for T in TInitValues:
      ComptonizedBBody.addInitExpression("& %s & 1e2 -1 & 1e2 -1 & 4000 & 0 -1 0 0 1 1 & %s 10 5 10 1e7 1e7 & %s 1.0 0.1 0.1 1000 1000 & 1.0" %(a,e0,T))    
    pass
  pass
pass  
ComptonizedBBody.addParameter("pegpwrlw","PhoIndex","Ph. index")
ComptonizedBBody.addParameter("highecut","foldE","Cutoff en.")
ComptonizedBBody.addParameter("bbody","kT","T")
models[ComptonizedBBody.fancyName]  = ComptonizedBBody
sufToFancy[ComptonizedBBody.suffix] = ComptonizedBBody.fancyName


#Band with high energy cutoff
BandHighEcut                   = xspecModel("grbm*highecut","Band with hi en. cutoff","BHec_")
alphaInitValues                = [-0.5,-1]
betaInitValues                 = [-2,-2.5]
e0InitValues                   = [100,500,1000]
cutoffInitValues               = [5e3,5e4,5e5]
for a in alphaInitValues:
  for b in betaInitValues:
    for e0 in e0InitValues:
      for c in cutoffInitValues:
        BandHighEcut.addInitExpression("& %s & %s 0.1 -10 -9 -0.01 -0.01 & %s 10 5 10 1e5 1e5 & 0.1 & 0 -1 0 0 1 1 & %s 5e2 100 100 1e9 1e9" %(a,b,e0,c))
      pass
    pass
  pass
pass    
BandHighEcut.addParameter("grbm","alpha","alpha")
BandHighEcut.addParameter("grbm","beta","beta")
BandHighEcut.addParameter("grbm","tem","E0")
BandHighEcut.addParameter("highecut","foldE","Cutoff en.")
models[BandHighEcut.fancyName] = BandHighEcut
sufToFancy[BandHighEcut.suffix]    = BandHighEcut.fancyName


#logParabola
LogParabola                    = xspecModel("logParabola","Log. parabola","Logp_")
aInitValues                    = [1.0,2.0,3.0]
bInitValues                    = [0.1,0.5,1.0]  
for a in aInitValues:
  for b in bInitValues:
    LogParabola.addInitExpression("& 1e3 -1 & %s 0.01 0.0001 0.001 5 10 & %s 0.1 0.1 0.1 10 10 & 0.1" %(a,b))
  pass
pass    
LogParabola.addParameter("logParabola","a","Form fact. a")
LogParabola.addParameter("logParabola","b","Form fact. b")
models[LogParabola.fancyName]  = LogParabola
sufToFancy[LogParabola.suffix]    = LogParabola.fancyName

#logParabola+LogParabola
LogPLogP                    = xspecModel("logParabola+logParabola","Log. par.+Log par.","LpLp_")
aInitValues                    = [1.0,2.5]
bInitValues                    = [0.1,0.5,1.0]  
for a in aInitValues:
  for b in bInitValues:
    for aa in aInitValues:
      for bb in bInitValues:
        LogPLogP.addInitExpression("& 1e3 -1 & %s 0.01 0.0001 0.001 5 10 & %s 0.1 0.1 0.1 10 10 & 0.1 & 1e3 -1 & %s 0.01 0.0001 0.001 5 10 & %s 0.1 0.1 0.1 10 10 & 0.1" %(a,b,aa,bb))
      pass
    pass
  pass
pass 
LogPLogP.addParameter("logParabola","a","Form fact. a (1)")
LogPLogP.addParameter("logParabola","b","Form fact. b (1)")
LogPLogP.addParameter("logParabola1","a","Form fact. a (2)")
LogPLogP.addParameter("logParabola1","b","Form fact. b (2)")
models[LogPLogP.fancyName]  = LogPLogP
sufToFancy[LogPLogP.suffix]    = LogPLogP.fancyName

#Redefine the two log parabolas using the formula with Ep
LogParabolaEp                    = xspecModel("logParabolaEp","Log. parabola Ep","LogpEp_")
aInitValues                     = [0.1,0.5,1.0]
EpInitValues                    = [100,300,700,1000,5000,1e4]  
for a in aInitValues:
  for e in EpInitValues:
    LogParabolaEp.addInitExpression("& %s 0.01 0.0001 0.001 5 10 & %s 10 1.0 1.0 1e9 1e9 & 0.1" %(a,e))
  pass
pass    
LogParabolaEp.addParameter("logParabolaEp","beta","Curvature")
LogParabolaEp.addParameter("logParabolaEp","ep","Peak energy")
LogParabolaEp.addParameter("logParabolaEp","norm","Sp")
models[LogParabolaEp.fancyName]  = LogParabolaEp
sufToFancy[LogParabolaEp.suffix]    = LogParabolaEp.fancyName

#logParabola+LogParabola
LogpEpLogpEp                    = xspecModel("logParabolaEp+logParabolaEp","Log. par.Ep+Log par.Ep","LpEpLpEp_")
aInitValues                     = [0.5,1.0]
EpInitValues                    = [100,1000,1e4]  
for a in aInitValues:
  for e in EpInitValues:
    for aa in aInitValues:
      for ee in EpInitValues:
        LogpEpLogpEp.addInitExpression("& %s 0.01 0.0001 0.001 5 10 & %s 10 1.0 1.0 1e9 1e9 & 0.1 & %s 0.01 0.0001 0.001 5 10 & %s 10 10.0 10.0 1e9 1e9 & 0.1" %(a,e,aa,ee))
      pass
    pass
  pass
pass
LogpEpLogpEp.addParameter("logParabolaEp","beta","Curvature (1)")
LogpEpLogpEp.addParameter("logParabolaEp","ep","Peak energy (1)")
LogpEpLogpEp.addParameter("logParabolaEp","norm","Sp (1)")
LogpEpLogpEp.addParameter("logParabolaEp1","beta","Curvature (2)")
LogpEpLogpEp.addParameter("logParabolaEp1","ep","Peak energy (2)")
LogpEpLogpEp.addParameter("logParabolaEp1","norm","Sp (2)")
models[LogpEpLogpEp.fancyName]  = LogpEpLogpEp
sufToFancy[LogpEpLogpEp.suffix]    = LogpEpLogpEp.fancyName

#Asymmetric log parabola
AsymLogParabola                    = xspecModel("asymLogP","Asymm. log. Parab.","ALogP_")
AsymLogParabola.addInitExpression("& 1000.0 5.0 5.0 5.0 1e9 1e9 & 1.5 & 2 & 0.01")
AsymLogParabola.addParameter("asymLogP","E0","Roll off energy")
AsymLogParabola.addParameter("asymLogP","a","Low-energy ph. index")
AsymLogParabola.addParameter("asymLogP","b","Curvature")
AsymLogParabola.addParameter("asymLogP","norm","Norm")
models[AsymLogParabola.fancyName]  = AsymLogParabola
sufToFancy[AsymLogParabola.suffix]    = AsymLogParabola.fancyName

  
#Comptonized + powerlaw
ComptPowerlaw                  = xspecModel("pegpwrlw*highecut+pegpwrlw","Comptonized + power law", "CP_")
alphaInitValues                = [0,-0.5,-1,-1.5]
e0InitValues                   = [50,200,500,1000]
for a in alphaInitValues:
  for e0 in e0InitValues:
    ComptPowerlaw.addInitExpression("& %s & 1e2 -1 & 1e2 -1 & 0.1 & 0 -1 0 0 1 1 & %s 10 5 10 1e5 1e5 &  2.2 & 1e4 -1 & 1e4 -1 & 10" %(a,e0))
  pass
pass 
ComptPowerlaw.addParameter("pegpwrlw","PhoIndex","Ph. index (compt.)")
ComptPowerlaw.addParameter("highecut","foldE","Cutoff en. (compt.)")
ComptPowerlaw.addParameter("pegpwrlw1","PhoIndex","Ph. index (pow.)")
models[ComptPowerlaw.fancyName] = ComptPowerlaw
sufToFancy[ComptPowerlaw.suffix]    = ComptPowerlaw.fancyName


#Comptonized + Comptonized
ComptCompt                     = xspecModel("pegpwrlw*highecut+pegpwrlw*highecut","Compt. + Compt.", "CC_")
alphaInitValues                = [0,-0.5,-1]
e0InitValues                   = [50,200,500,1000]
cutoffInitValues               = [5e3,5e4,1e6]
for a in alphaInitValues:
  for e0 in e0InitValues:
    for c in cutoffInitValues:
      ComptCompt.addInitExpression("& %s & 1e2 -1 & 1e2 -1 & 0.1 & 0 -1 0 0 1 1 & %s 10 5 10 1e5 1e5 & 2.2 & 1e4 -1 & 1e4 -1 & 10 & 0 -1 0 0 1 1 & %s 1e3 1e3 1e3 1e9 1e9" %(a,e0,c))
    pass
  pass
pass 
ComptCompt.addParameter("pegpwrlw","PhoIndex","Ph. index (compt.1)")
ComptCompt.addParameter("highecut","foldE","Cutoff en. (compt.1)")
ComptCompt.addParameter("pegpwrlw1","PhoIndex","Ph. index (compt.2)")
ComptCompt.addParameter("highecut1","foldE","Cutoff en. (compt.2)")
models[ComptCompt.fancyName] = ComptCompt
sufToFancy[ComptCompt.suffix]    = ComptCompt.fancyName

#logParabola+power law
LogpPowerlaw                   = xspecModel("logParabola+pegpwrlw","Log. parab. + power law","LogpP_")
LogpPowerlaw.addInitExpression("& 1e3 -1 & 1.0 0.1 0.0 0.0 10 10 & 2.0 0.1 0 0 10 10 & 1 &  2.5 0.1 0.01 0.01 9 10 & 1e4 -1 & 1e4 -1 & 1000")
LogpPowerlaw.addParameter("logParabola","a","Form fact. a")
LogpPowerlaw.addParameter("logParabola","b","Form fact. b")
LogpPowerlaw.addParameter("pegpwrlw","PhoIndex","Ph. index")
models[LogpPowerlaw.fancyName] = LogpPowerlaw
sufToFancy[LogpPowerlaw.suffix]    = LogpPowerlaw.fancyName

allModels                      = dict(models)
allSufToFancy                  = dict(sufToFancy)

#Set default models
useModels("B,BP,BC,C,CP,P")

#Further models
addModel("bknpower","broken powerlaw","BKN_","& 1 & 500.0 5 10 10 1e9 1e9 & 2 & 0.1",["bknpower,PhoIndx1,Photon index 1","bknpower,BreakE,Break energy","bknpower,PhoIndx2,Photon index 2"]) 

parList = []
parList.append("& -1 & -2 & 500.0 5 10 10 1e9 1e9 & 0.1 & 0 -1 0 0 1 1 & 3e4 1e2 500 500 1e9 1e9 & 120 1 1.0 1.0 1000 1000 & 0.1")
parList.append("& -1 & -2 & 500.0 5 10 10 1e9 1e9 & 0.1 & 0 -1 0 0 1 1 & 3e4 1e2 500 500 1e9 1e9 & 70 1 1.0 1.0 1000 1000 & 0.1")
parList.append("& -1 & -2 & 500.0 5 10 10 1e9 1e9 & 0.1 & 0 -1 0 0 1 1 & 3e4 1e2 500 500 1e9 1e9 & 30 1 1.0 1.0 1000 1000 & 0.1")
parList.append("& -1 & -2 & 300.0 5 10 10 1e9 1e9 & 0.1 & 0 -1 0 0 1 1 & 3e4 1e2 500 500 1e9 1e9 & 120 1 1.0 1.0 1000 1000 & 0.1")
parList.append("& -1 & -2 & 300.0 5 10 10 1e9 1e9 & 0.1 & 0 -1 0 0 1 1 & 3e4 1e2 500 500 1e9 1e9 & 70 1 1.0 1.0 1000 1000 & 0.1")
parList.append("& -1 & -2 & 300.0 5 10 10 1e9 1e9 & 0.1 & 0 -1 0 0 1 1 & 3e4 1e2 500 500 1e9 1e9 & 30 1 1.0 1.0 1000 1000 & 0.1")

addModel("grbm*highecut+bbody","Band with cutoff+Black Body","BHecBB_",parList,["grbm,alpha,alpha","grbm,beta,beta","grbm,tem,break energy","highecut,foldE,Fold energy","bbody,kT,kT"])

