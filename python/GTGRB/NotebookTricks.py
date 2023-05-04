#These are functions meant to be used inside the ipython Notebook

import GtApp
import os, shelve
from IPython.core.display import HTML, display

class NotebookTricks(object):
  def __init__(self):
    pass
  pass
  
  def _makeForm(self,title,parList,hide=False):
    form                        = ""    
    if(hide):
      fieldtype                 = 'hidden'
    else:
      form                     += "\n<h3>%s</h3>" %(title)
      form                       += "\n<table border='0'>"   
      fieldtype                 = 'text'
    pass 
    
    for par in parList:
      parInPfile                = self.gtgrbApp.pars.params.get(par)
      descr                     = parInPfile[-1].strip('"')
      curValue                  = parInPfile[2].strip('"')
      if(hide):
        form                   += '\n<input type="%s" name="%s" value="%s">' %(fieldtype,par,curValue)
      else:  
        if(par=="IRFS"):
          irfs                  = "P7TRANSIENT_V6,P7SOURCE_V6,P7CLEAN_V6,P7ULTRACLEAN_V6,P6_V3_TRANSIENT".split(",")
          form                 += "\n<tr><td>%s</td><td><select id='%s'>" %(descr,par)
          for ir in irfs:
            form               += "\n<option value='%s'>%s</option>" %(ir,ir)
          pass  
          form                 += "\n</select></td></tr>"
        else:  
          form                 += '\n<tr><td>%s</td><td><input type="%s" name="%s" value="%s"></td>' %(descr,fieldtype,par,curValue)
    pass
    if(not hide):
      form                     += "\n</table>\n"
    return form
  pass
        
  pass
  
  def PromptGeneralParameters(self):
    #This read the pfile for gtgrb
    self.gtgrbApp               = GtApp.GtApp('gtgrb')
    
    grbParameters               = ['GRBTRIGGERDATE','RA','DEC','ERR','REDSHIFT',
                                   'GRBT05','GRBT90']
    analysisParameters          = ['ROI','IRFS','EMIN','EMAX','EBINS','ZMAX']
    otherParameters             = ['FT1','FT2','DETLIST','DT','BINSZ','NAIANGLE']
    
    #Prepare the subforms
    grbForm                     = self._makeForm("GRB parameters:",grbParameters)
    analysisForm                = self._makeForm("Analysis parameters:",analysisParameters)
    otherForm                   = self._makeForm("Other parameters (you don't normally need to change these):",otherParameters,True)
    
    #Put everything together
    form                        = '<FORM NAME="mainForm" ACTION="" METHOD="GET">'
    form                       += grbForm
    form                       += analysisForm
    form                       += otherForm
    form                       += '\n<INPUT TYPE="button" NAME="button" Value="Store" onClick="setParameters(this.form)">'
    form                       += "\n</FORM>"
    
    #Now write the script which transfer the values from the form to a dictionary
    script                      = '\n<script LANGUAGE="JavaScript">'
    script                     += '\nfunction setParameters(form) {'
    #script                     += '\n  form.button.value = "Working..."'
    script                     += '\n  IPython.notebook.kernel.execute("userParameters = {}");'
    allParameters               = grbParameters+analysisParameters+otherParameters
    for par in allParameters:
      if(par=="IRFS"):
        script                 += '\n  IPython.notebook.kernel.execute("userParameters[\'%s\'] = \'"+form.%s.options[form.%s.options.selectedIndex].text+"\'");' %(par,par,par)
      else:
        script                 += '\n  IPython.notebook.kernel.execute("userParameters[\'%s\'] = \'"+form.%s.value+"\'");' %(par,par)
    pass
    #script                     += '\n  IPython.notebook.kernel.execute("Set(**userParameters)");'
    #script                     += '\n  form.button.value = "Set Parameters"'
    script                     += '\n}'
    script                     += '\n</script>'
    
    return (script+form)
    
  pass
  
  def getNameAndSetPfiles(self):
    script                      = "Executed!<script language='JavaScript'>"
    script                     += '\n  if (IPython.notebook.get_notebook_name().search(/untitled/i) != -1) { '
    script                     += '\n     alert("You have to give a name different from Untitled to your notebook before continuing!'
    script                     += 'Use the Rename function in the menu File or click on the title to change it, then reset the kernel and retry");'
    script                     += '\n     throw "Unnamed notebook" ;}'
    #Now set the right pfiles directory
    script                     += '\n  IPython.notebook.kernel.execute("notebookName = \'" + IPython.notebook.get_notebook_name()+"\'");'
    script                     += '''\n  IPython.notebook.kernel.execute("os.environ['NOTEBOOK_NAME'] = notebookName");'''
    script                     += '\n  IPython.notebook.kernel.execute("import os,subprocess") ;'
    script                     += '\n  IPython.notebook.kernel.execute("newPfiles                   = \'%s/Notebooks/%s_pfiles\' %(os.environ[\'BASEDIR\'],notebookName)") ;'
    script                     += '\n  IPython.notebook.kernel.execute("import os");'
    script                     += '\n  IPython.notebook.kernel.execute("try:\\n    os.makedirs(newPfiles)\\nexcept:\\n    pass");'
    script                     += '\n  IPython.notebook.kernel.execute("os.environ[\'PFILES\'] = \'%s;%s\' % (newPfiles,os.environ[\'PFILES\'].split(\';\')[1])") ;'
    script                     += '\n</script>'
    return script
  pass
  
pass

def set_pfiles():
  tr                          = NotebookTricks()
  return HTML(tr.getNameAndSetPfiles())
pass

def load_session():
  #Now check if a session has been saved
  #Reget the name of the notebook
  notebookName                = os.environ['NOTEBOOK_NAME']
  shelfName                   = os.path.join(os.environ['BASEDIR'],'Notebooks','%s.data' %(notebookName))  
  if(os.path.exists(shelfName)):
    print("Found saved session in %s, loading it..." %(shelfName))
    shelf                       = shelve.open(shelfName,'r')
    for key in shelf:
      try:
        if(key=='results'):
          globals()['savedResults'] = shelf[key].copy()
        elif(key=='lat' or key=='grb'):
          continue
        else:
          globals()[key]         = shelf[key]
      except:
        print('Could not load %s' %(key))
      pass
      shelf.close()
      print("Session loaded!")  
  else:
    print("No saved session in %s" %(shelfName))
  pass
  display(HTML(tr.PromptGeneralParameters()))
  return
pass


