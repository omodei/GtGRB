from xml.dom.minidom import parse, parseString
import os
from collections import OrderedDict
 
class parseXML(object):
  def __init__(self,xmlFile):
    self.xmlFile              = xmlFile
    self.dom                  = parse(xmlFile)
    self.fill()
  pass
    
  def fill(self):
    self.parameters           = []
    self.doms                 = []
    for par in self.dom.getElementsByTagName("parameter"):
      self.doms.append(par)
      thisParameter           = OrderedDict()
      thisParameter['Source Name']          = self._getAttribute(par.parentNode.parentNode,'name')
      thisParameter['Name']                 = self._getAttribute(par,'name')
      thisParameter['Value']                = self._getAttribute(par,'value')
      thisParameter['Error']                = self._getAttribute(par,'error')
      thisParameter['Min']                  = self._getAttribute(par,'min')
      thisParameter['Max']                  = self._getAttribute(par,'max')
      thisParameter['Scale']                = self._getAttribute(par,'scale')
      thisParameter['Free']                 = self._getAttribute(par,'free')
      thisParameter['Source Type']          = self._getAttribute(par.parentNode.parentNode,'type')
      thisParameter['Feature']              = par.parentNode.localName #either Spectrum or SpatialModel
      thisParameter['Feature Type']         = self._getAttribute(par.parentNode,'type')
      thisParameter['Feature File']         = self._getAttribute(par.parentNode,'file')
      if(thisParameter['Feature File']!=''):
        thisParameter['Feature File']       = "[..]/%s" % os.path.basename(thisParameter['Feature File'])
      pass

      self.parameters.append(thisParameter)
  pass
  
  def _getAttribute(self,element,key):
    try:
      value                   = element.attributes[key].value
    except:
      value                   = ""
    return value
  pass
  
  def setAttribute(self,parameter,attributeName,newValue):
    #Find the right parameter to change
    par                       = filter(lambda x:x['Source Name']==parameter[0] and
                                                x['Source Type']==parameter[8] and
                                                x['Feature']==parameter[9] and
                                                x['Feature Type']==parameter[10] and
                                                x['Name']==parameter[1],self.parameters)[0]
    parID                     = self.parameters.index(par)
    self.doms[parID].setAttribute(attributeName.lower(),newValue)
    self.fill()
  pass
  
  def save(self):
    f                         = open(self.xmlFile,"w+")
    self.dom.writexml(f)
    f.close()
pass
