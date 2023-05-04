import collections
import guiParameters
import textwrap
import os
import textwrap

def convertToInteger(string):
  #In python, int('2.0') gives an error, while int(float('2.0')) is ok
  return int(float(string))
pass

def _findInDictionary(dictionary,key):
    #Case insensitive search in a dictionary or GtApp class
    for k,v in dictionary.iteritems():
      if(key.lower()==k.lower()):
        return k, v
      pass
    pass
    #key not found
    return None, None
pass

def handleBooleans(value,symbols=[True,False]):
  '''
    Transform a given input boolean value (yes, no, 1, 0, true, false, True, False) 
    in the corresponding value in the requested type. The default is what is understood
    by the FTOOLS (pfiles syntax)
    
    For example: handleBooleans('yes',[True,False]) will return True.
                 handleBooleans(0,['yes','no']) will return 'no'
                 handleBooleans(True,[1,0]) will return 1
                 handleBooleans(True,['pippo','pluto'] will return 'pippo'
  '''
  true                        = symbols[0]
  false                       = symbols[1]
  
  if(isinstance(value,str)):
    if(value.lower()=='yes' or value.lower()=='y' or  value.lower()=='1' or  value.lower()=='1.0' or value.lower()=='true'):
      return true
    elif(value.lower()=='no' or value.lower()=='n' or value.lower()=='0' or  value.lower()=='0.0' or value.lower()=='false'):
      return false
    else:
      raise RuntimeError("handleBooleans(): unrecognized input value")
  elif(isinstance(value,bool)):
    if(value==True):
      return true
    elif(value==False):
      return false
  elif(isinstance(value,int)):
    if(value==1):
      return true
    elif(value==0):
      return false
  elif(isinstance(value,float)):
    if(abs(value - 1.0) < 1E-3):
      return true
    elif(abs(value - 0.0) < 1E-3):
      return false
pass

def handleNone(value,none):
  if(isinstance(value,str)):
    if(value.lower()=='none'):
      return none
    elif(value.lower()==''):
      return none
    else:
      return value
  elif(value==None):
    return none
  else:
    return value
pass

def stringToListOfReals(value,delimiter=","):
  try:
    outlist                     = map(lambda x:float(x),str(value).replace(" ","").replace("\n","").replace("]","").replace("[","").split(delimiter))
  except:
    raise ValueError("Could not convert %s to a list of real numbers" %(value))
  pass
  return outlist
pass

def stringToListOfStrings(value,delimiter=","):
  try:
    outlist                     = map(lambda x:str(x),str(value).replace(" ","").replace("\n","").replace("]","").replace("[","").split(delimiter))
  except:
    raise ValueError("Could not convert %s to a list of strings" %(value))
  pass
  return outlist
pass

#Some definitions
MANDATORY                     = 'mandatory'
OPTIONAL                      = 'optional'
HIDDEN                        = 'hidden'
GUIONLY                       = 'guionly'

#None values
NONESTRING                    = ''
NONEINTEGER                   = 9999999999
NONEBOOLEAN                   = 3
NONEREAL                      = -9.9999999

#Parameter types (based on pfiles syntax)
#"The type is the data type: either b for boolean, 
#i for integer, r for real, or s for string."
#Each type is a tuple with the pfile syntax, a description of the type, a constructor/converter
#capable of transforming a string in the desired type, and a None value, which is used for the parameter
#when it is left empty by the user
INPUTFILE                     = ('s','input file',str,NONESTRING)
OUTPUTFILE                    = ('s','output file',str,NONESTRING)
INTEGER                       = ('i','integer number',convertToInteger,NONEINTEGER)
BOOLEAN                       = ('b','boolean',handleBooleans,NONEBOOLEAN)
REAL                          = ('r','real number',float,NONEREAL)
STRING                        = ('s','string',str,NONESTRING)
LISTOFREALS                   = ('r','list of real numbers',stringToListOfReals,NONEREAL)
LISTOFSTRINGS                 = ('s','list of strings',stringToListOfStrings,NONESTRING)
PYTHONONLY                    = 00000

class UserError(RuntimeError):
   def __init__(self, message):
      RuntimeError(message)
      self.message = message
pass

class Parameter(object):
  def __init__(self,parname,description,kind=OPTIONAL,defaultValue=None,**kwargs):
    self.parname              = parname.upper()
    self.description          = description
    self.kind                 = kind    
    self.type                 = STRING
    self.extension            = "*"
    self.private              = False
    self.possibleValues       = []
    for key in kwargs.keys():
      if   key.lower()=="partype":        self.type           = kwargs[key]
      elif key.lower()=="extension":      self.extension      = kwargs[key]
      elif key.lower()=="possiblevalues": self.possibleValues = kwargs[key]
      elif key.lower()=="private"       : self.private        = kwargs[key]
    pass
    if(defaultValue==None):
      self.defaultValue       = self.type[3]
    else:
      if(self.type==BOOLEAN):
        self.defaultValue     = handleBooleans(defaultValue,self.possibleValues)
      else:
        self.defaultValue     = defaultValue
    pass
    self.setValue(defaultValue)
  
  def setValue(self,value):
    if(self.type==BOOLEAN):
      value                   = handleBooleans(value,['yes','no'])
    if(self.possibleValues!=[] and (value not in map(lambda x:x,self.possibleValues))):
      raise ValueError("Value %s is not a valid value for parameter %s. Possible values: %s" %(value,
                                                                     self.parname,",".join(self.possibleValues)))
    
    #Convert the value to the right type
    try:
      if(handleNone(value,None)==None or value==self.type[3]):
        self.value            = self.type[3]
      else:
        self.value            = self.type[2](value)
    except:
      raise RuntimeError("Could not convert %s to type '%s' for parameter %s" %(value,self.type[1],self.parname))
  pass
  
  def getValue(self,display=False):
    if(self.isNone()):
      return ''
    else:
      if(self.type==BOOLEAN and display):
        return handleBooleans(self.value,['yes','no'])
      else:
        return self.value
  pass
  
  def isMandatory(self):
    return self.kind==MANDATORY
  pass
  
  def isOptional(self):
    return (not self.isMandatory())
  
  def isHidden(self):
    return self.kind==HIDDEN
  pass
  
  def isPrivate(self):
    return self.private
  pass
  
  def isPublic(self):
    return (not self.isPrivate())
  pass
  
  def isNone(self):
    return self.value==self.type[3]
pass

class Command(object):
  def __init__(self,name,description,version,author):
    self.name                 = name
    self.version              = version
    self.author               = author
    self.description          = " ".join(description.replace("\n","").split())
    self.GUIdescription       = "You should not see this"
    #The definedParameters dictionary contains parameter names as keys and Parameter classes as values
    self.definedParameters    = collections.OrderedDict()
  pass
  
  def addParameter(self,*args,**kwargs):
    self.definedParameters[args[0]] = Parameter(*args,**kwargs)
  pass
  
  def getParValue(self,parname):
    return self.definedParameters[parname].getValue()
  pass
  
  def changeParName(self,oldname,newname):
    value                     = self.definedParameters[oldname]
    self.definedParameters[newname] = value
    del self.definedParameters[oldname]
  
  def setParValue(self,parname,value):
    self.definedParameters[parname].setValue(value)
  pass

  def getParameters(self,variables,dictionary=False):
    '''
    Return the parameters provided in the string variables as "par1,par2,par3..." or as a dictionary
    '''
    if(dictionary):
      toReturn          = {}
    else:
      toReturn          = []
    for varexpr in variables.split(","):
      if(varexpr.find(":")>0):
        var             = varexpr.split(":")[0]
        resultskey      = varexpr.split(":")[1]
      else:
        var             = varexpr
        resultskey      = varexpr
      pass
      key,value         = _findInDictionary(self.definedParameters,resultskey)
      if(key==None):
        raise ValueError("Parameter %s not found!" %(resultskey)) 
      if(dictionary):
        if(not self.definedParameters[key].isNone()):
          toReturn[var] = self.getParValue(key)
        pass
      else:    
        toReturn.append(self.getParValue(key))
    pass
    if(not dictionary):
      if(len(toReturn)==1):
        toReturn = toReturn[0]
    return toReturn
  pass
 
  def _getFromOneDictionary(self,key,d1,d2):
    if(d2==None):
      d2                      = {}
    pass
    k1, v1                    = _findInDictionary(d1,key)
    if k1!=None:
      return v1
    else:
      k2, v2                  = _findInDictionary(d2,key)
      if k2!=None:
        return v2
      else:
        return ''
  pass
  
  def harvestParameters(self,inputDict1,inputDict2=None,mode='query'):
    #This set the parameters for this command taking the values from (in order) the user (if mode='query'),
    #inputDict1 or inputDict2.
    #Note that if a parameter is set in inputDict1 and in inputDict2, the definition in the former take precedence and
    #the definition in the latter is overwritten.
    #At the end, all parameters are stored/updated. If inputDict2 is defined, it is updated
    #with all keywords in kwargs
    if(mode=='query'):
    
      #Ask all the parameters that are not hidden and are not already contained in inputDict1
      if(os.environ.get('GUIPARAMETERS')!=None and os.environ.get('GUIPARAMETERS')=='yes'):
        
        #Check if we have a suitable value for the parameter already set up, if yes update the value
        #so that the user will find it in the GUI
        for parname, parameter in self.definedParameters.iteritems():
          #Did the user specified it in the command line?
          k,v                   = _findInDictionary(inputDict1,parname)
          
          if(k!=None):
            #yes
            parameter.setValue(v)
          
          else:
            #no! If it is public, check if it is in dictionary 2 (most of the time =results)
            if(inputDict2!=None and parameter.isPublic()):
              
              k,v               = _findInDictionary(inputDict2,parname)
              if(k!=None):
                parameter.setValue(v)
              pass            
            pass
          pass      
        pass
        
        pars                    = guiParameters.getParameters(self,True)
        if(pars==None):
          raise UserError("\nCommand canceled")
      else:
        pars                    = collections.OrderedDict()
        for parname, parameter in self.definedParameters.iteritems():
          k,v                   = _findInDictionary(inputDict1,parname)
          if(k!=None):
            #Contained in inputDict1, do not ask for it again
            continue
          else:
            #Not contained in inputDict1, ask for it if it is not hidden
            if(parameter.isHidden()):
              continue
            else:
              #If it is public, check if it is in dictionary 2 (most of the time =results)
              if(inputDict2!=None and parameter.isPublic()):
                k,v               = _findInDictionary(inputDict2,parname)
                if(k!=None):
                  parameter.setValue(v)
                pass
              pass
              if(parameter.isNone()):
                currentValue        = ''
              else:
                currentValue        = parameter.getValue(True)
              pass
              frmt                  = " ".join(("%s: %s [%s]:" % (parname,parameter.description,currentValue)).replace("\n","").split())
              lines                 = textwrap.wrap(frmt,70-4)
              print(" * %s" %(lines[0])),
              for line in lines[1:]:
                print("\n   %s" % line),
              userinput             = raw_input()
              
              if(userinput.replace("\n","")==''):
                #Use current value (which is the default at the beginning)
                userinput           = parameter.getValue()
              pass
              
              pars[parname.upper()] = userinput
              
            pass
          pass
        pass
      pass
      #Copy what we've got from the user in the highest priority dictionary
      #(moving everything to upper case)
      for key, value in pars.iteritems():
        try:
          del inputDict1[key]
        except:
          pass
        inputDict1[key.upper()]   = value
      pass  
    pass 
    
    for parname, parameter in self.definedParameters.iteritems():
      
      value                   = self._getFromOneDictionary(parname,inputDict1,inputDict2)
      if(value==parameter.kind[3] or value==''):
        if(parameter.isMandatory()):
          raise RuntimeError("Parameter %s for command %s is mandatory, but it has not been specified!" %(parname,self.name))
        pass
        if(parameter.isOptional() or parameter.isHidden()):
          #use default values
          value               = parameter.defaultValue
      pass
      
      if(parameter.type==INPUTFILE and value!=''):
        #Verify that it exists
        abspath               = os.path.abspath(os.path.expanduser(os.path.expandvars(value)))
        if(not os.path.exists(abspath)):
          raise IOError("File %s does not exists or is not readable!" %(abspath))
        pass
      pass
      
      #Set the value finally
      parameter.setValue(value)
      
      #Update the inputDict2 dictionary with all the public parameters
      if(inputDict2!=None and parameter.isPublic()):
        try:
          del inputDict2[parname]
        except:
          pass
        inputDict2[parname.upper()] = parameter.getValue()
      pass
    pass  
  pass
  
  def getPreambolMessage(self):
    return "%s v.%s\nAuthor: %s" %(self.name,self.version,self.author)
  
  def setGUIdescription(self,description):
    self.GUIdescription       = description
  pass  
  
  def getGUIdescription(self):
    return self.GUIdescription
  
  def getHelp(self,printHelp=True):
    #Print a help message
    message                   = self.getPreambolMessage()
    message                  += "\n\n %s" %(self.description)
    message                  += "\n"
    message                  += "\nParameters:\n"
    for parname, parameter in self.definedParameters.iteritems():
      if(parameter.isMandatory()):
        description             = parameter.description
      elif(parameter.type==PYTHONONLY):
        continue
      else:
         description           = "(OPTIONAL) %s" %(parameter.description) 
      pass
      descriptionLines        = textwrap.wrap(description,40)
      message                += "\n{0:20s}: {1:40s}".format(parname, descriptionLines[0])
      for i in range(1,len(descriptionLines)):
        message              += "\n{0:20s}  {1:40s}".format(" ",descriptionLines[i])
      pass
      if(parameter.isMandatory()==False):
        message              += "\n{0:20s}  {1:40s}".format(" ","(Default: %s)" %(parameter.defaultValue))
    pass
    if(printHelp):
      print(message)
    else:
      return message
  pass
  
pass    
