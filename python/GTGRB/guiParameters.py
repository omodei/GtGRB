from Tkinter import *
import tkFont
from tkSimpleDialog import askfloat
from tkFileDialog import askopenfilename
from tkFileDialog import askdirectory
from tkMessageBox import showerror, showinfo 
from ttk import *

import os,time, collections, sys

#Font definitions
LABELFONT                     = ("Times", 12, "bold")
NORMALFONT                    = ("Times", 12)
COMMENTFONT                   = ("Times", 12)

def getParameters(command,printPar=True,master=None):
  g                           = Getter(command,master)
  d                           = g.get()
  if(printPar and d!=None):
    print("Selected configuration:\n")
    cmdline                   = []
    for key,val in d.iteritems():
      print("%-40s = %s" %(key.upper(),val))
      if(val!=''):
        try:
          cmdline.append("%s=%s" %(key,float(val)))
        except:
          cmdline.append("%s='%s'" %(key,val))
    print("\nYou can obtain the same by running:\n")
    print("%s(%s)\n" %(command.name,",".join(cmdline)))
    sys.stdout.flush()
  pass
  return d
pass

class Getter(object):
  def __init__(self,command,master=None):
    if(master==None):
      self.root                 = Tk()
    else:
      self.root                 = Toplevel(master)
      self.root.transient(master)
      try:
        self.root.grab_set()
      except:
        pass
    pass
    
    #self.root.geometry("900x700+0+0")
    self.root.title(command.name)
    
    mainFrame                 = Frame(self.root)
    self.style                = Style()
    self.style.theme_use(self.style.theme_names()[0])
    mainFrame.pack(side=TOP,expand=True,fill=BOTH)
    
    #Parameters
    self.entries              = collections.OrderedDict()
    for parname, parameter in command.definedParameters.iteritems():
      if(parameter.isHidden()):
        continue
      if(parameter.possibleValues!=[]):
        #Combo box
        self.entries[parname] = EntryPoint(mainFrame,
        				   labeltext=parameter.parname,
        				   helptext=parameter.description,
        				   possiblevalues=parameter.possibleValues,
					   initvalue=parameter.getValue(display=True),
					   mandatory=(parameter.kind=='mandatory'))
      else: 
        print("%s -> %s" %(parameter.parname,parameter.getValue(display=True)))
        self.entries[parname] = EntryPoint(mainFrame,
                                           labeltext=parameter.parname,
                                           helptext=parameter.description,
                                           initvalue=parameter.getValue(display=True),
					   mandatory=(parameter.kind=='mandatory'))				  
    pass
    
    #Text
    textLabel                 = Label(mainFrame)
    textLabel['text']         = "\n\nParameters denoted by '*' are mandatory, the others are optional."
    textLabel.pack(side=TOP,expand=True,fill=X)
    
    #Buttons
    okButton                  = Button(mainFrame,
                                 text="Ok",
                                 command=self.saveParameters)
    okButton.pack(side=TOP,expand=True,fill=X)
    cancelButton              = Button(mainFrame,
                                 text="Cancel",
                                 command=self.cancel)
    cancelButton.pack(side=TOP,expand=True,fill=X)
    
    #Center the window
    self.root.update_idletasks()
    xp = (self.root.winfo_screenwidth() / 2) - (self.root.winfo_width() / 2)
    yp = (self.root.winfo_screenheight() / 2) - (self.root.winfo_height() / 2)
    self.root.geometry('{0}x{1}+{2}+{3}'.format(self.root.winfo_width(), self.root.winfo_height(),
                                                                        xp, yp))
    self.root.protocol("WM_DELETE_WINDOW", self.cancel)
    
    self.root.mainloop()
  pass
  
  def cancel(self):
    self.root.quit()
    self.root.destroy()
    self.outDict              = None
  
  def saveParameters(self):
    #Build the dictionary
    outDict                   = collections.OrderedDict()
    for parname,entry in self.entries.iteritems():
      outDict[parname]        = entry.get().replace("\n",'')
    pass
    self.root.quit()
    self.root.destroy()
    self.outDict              = outDict
  def get(self):
    return self.outDict 
pass

class EntryPoint(object):
    def __init__(self,parent,**kwargs):      
      labelText               = ''
      browser                 = False
      directory               = False
      textWidth               = 70
      initValue               = ''
      helpText                = ''
      inactive                = False
      mandatory               = True
      workdir                 = os.getcwd()
      possibleValues          = []
      for key in kwargs.keys():
        if    key.lower()=="labeltext":         labelText      = kwargs[key]
        elif  key.lower()=="browser":           browser        = bool(kwargs[key])
        elif  key.lower()=="textwidth":         textWidth      = int(kwargs[key])
        elif  key.lower()=="initvalue":         initValue      = kwargs[key]
        elif  key.lower()=="directory":         directory      = bool(kwargs[key])
        elif  key.lower()=="workdir":           workdir        = kwargs[key]
        elif  key.lower()=="inactive":          inactive       = bool(kwargs[key])
	elif  key.lower()=="mandatory":         mandatory      = bool(kwargs[key])
        elif  key.lower()=="helptext":          helpText       = kwargs[key]
        elif  key.lower()=="possiblevalues":    possibleValues = kwargs[key]
      pass
      self.parent             = parent
      self.parentWidth        = self.parent.cget('width') 
      
      self.subFrame           = Frame(self.parent,width=self.parentWidth)
      self.subFrame.pack(side=TOP,fill=BOTH,expand=True)
      #Label
      self.label              = Label(self.subFrame,width=50,wraplength=350)
      self.label['text']      = " ".join(helpText.replace("\n","").split()) #labelText
      self.label.pack(side=LEFT,expand=True,fill='x')
      
      #Variable
      self.variable           = StringVar()
      
      if(possibleValues==[]):
        #Entry
        self.variable.set(str(initValue))
        self.entry              = Entry(self.subFrame,
                                        textvariable=self.variable)
	self.entry.config(width=15)
        self.entry.pack(side=LEFT,expand=True,fill='x')        
      else:
        #Multiple choice
        self.possibleValues = possibleValues
	if(initValue==''):
	  initValue           = str(possibleValues[0])
	
        self.entry         = OptionMenu(self.subFrame, self.variable, initValue,
	                                *self.possibleValues)
	self.entry.config(width=15) 
	#apply(OptionMenu, (self.subFrame, 
        #                               self.variable) + tuple(self.possibleValues))
        self.entry.pack(side=LEFT,expand=True,fill='x')	
      pass
        
      if(inactive):
        self.entry.config(state='readonly')
      pass
      
      if(browser):
        self.browserButton    = Button(self.subFrame,text="Browse",
                                 command=lambda directory=directory: selectFile(self.parent,self.entry,directory=directory,workdir=workdir),
				       width=20)
        self.browserButton.pack(side=LEFT,fill='x',expand=True)
      elif(helpText!=''):
        if(mandatory):
          labelText            = " *   %s" %(labelText)
	else:
	  labelText            = "     %s" %(labelText)
        self.helpLabel        = Label(self.subFrame,text=labelText.upper(),width=30,anchor=W)
        self.helpLabel.pack(side=LEFT,fill='x')
      else:
        #Label
        self.spacer             = Label(self.subFrame,width=20)
        self.spacer['text']     = ''
        self.spacer.pack(side=LEFT,expand=True,fill='x')
    pass
    
    def destroy(self):
      self.entry.destroy()
      self.label.destroy()
      self.subFrame.destroy()      
      try:
        self.helpButton.destroy()
      except:
        pass
      try:
        self.browserButton.destroy()
      except:
        pass
      pass        
    pass
    
    def get(self):
      return self.variable.get()
    pass  
    
    def set(self,value):
      self.variable.set(value)
    pass
pass

class ListBoxChoice(object):
    def __init__(self, title=None, message=None, list=[],predefinedChoice=None):
        self.value = None
        self.list = list[:]     
        self.root = Tk()
        self.style                = Style()
        self.style.theme_use(self.style.theme_names()[0])
        self.root.bind("<Return>", self._choose)
        self.root.bind("<Escape>", self._cancel)

        if title:
            self.root.title(title)

        if message:
            Label(self.root, text=message).pack(padx=5, pady=5)

        listFrame = Frame(self.root)
        listFrame.pack(side=TOP, padx=5, pady=5)
        height                = min(len(self.list),20)
        self.listBox = Listbox(listFrame, selectmode=EXTENDED,
                               width=max(map(lambda x:len(x),self.list)),height=height,font=("TkFixedFont",10))
        
        self.listBox.pack(side=LEFT, fill=BOTH)
        scrollBar = Scrollbar(listFrame,orient=VERTICAL)
        scrollBar.pack(side=RIGHT, fill=BOTH)
        scrollBar.config(command=self.listBox.yview)
        self.listBox.config(yscrollcommand=scrollBar.set)
        for item in self.list:
            self.listBox.insert(END, item)

        buttonFrame = Frame(self.root)
        buttonFrame.pack(side=BOTTOM)

        chooseButton = Button(buttonFrame, text="Choose", command=self._choose)
        chooseButton.pack(side=LEFT,fill=BOTH)

        cancelButton = Button(buttonFrame, text="Cancel", command=self._cancel)
        cancelButton.pack(side=RIGHT,fill=BOTH)
        
        #Center the window
        self.root.update_idletasks()
        xp = (self.root.winfo_screenwidth() / 2) - (self.root.winfo_width() / 2)
        yp = (self.root.winfo_screenheight() / 2) - (self.root.winfo_height() / 2)
        self.root.geometry('{0}x{1}+{2}+{3}'.format(self.root.winfo_width(), self.root.winfo_height(),
                                                                        xp, yp))
        self.root.protocol("WM_DELETE_WINDOW", self._cancel)
        #Highlight the pre-defined choices
        if(predefinedChoice!=None):
          for i in predefinedChoice:
            self.listBox.selection_set(i)
          pass
        pass
        self.root.mainloop()
        
    def _choose(self, event=None):
        try:
            sels = self.listBox.curselection()
            values = []
            for sel in sels:
              values.append(self.list[int(sel)])
            pass
            self.value = values  
        except IndexError:
            self.value = None
        self.root.quit()
        self.root.destroy()

    def _cancel(self, event=None):
        self.value = None
        self.root.quit()
        self.root.destroy()
        
    def returnValue(self):
        return self.value

pass


def sortby(tree, col, descending):
    """Sort tree contents when a column is clicked on."""
    # grab values to sort
    data = [(tree.set(child, col), child) for child in tree.get_children('')]

    # reorder data
    data.sort(reverse=descending)
    for indx, item in enumerate(data):
        tree.move(item[1], '', indx)

    # switch the heading so that it will sort in the opposite direction
    tree.heading(col,
        command=lambda col=col: sortby(tree, col, int(not descending)))

class helpGUI(object):
    def __init__(self,commands,command=None,root=None):
        if(root==None):
          root = Tk()
          root.maxsize(1024,768)
          root.wm_title("GtGRB Help")
          root.wm_iconname("GtGRB Help")
        pass
        self.root = root
        #Make a copy of the xml, which will be modified, and it will be copied back
        #overwritting the input file only at the very end
        self.columns = ["Command name","Description"]
        self.commands = commands
        self.tree = None
        self._setup_widgets()
        #Center the window
        self.root.update_idletasks()
        xp = (self.root.winfo_screenwidth() / 2) - (self.root.winfo_width() / 2)
        yp = (self.root.winfo_screenheight() / 2) - (self.root.winfo_height() / 2)
        self.root.geometry('{0}x{1}+{2}+{3}'.format(self.root.winfo_width(), self.root.winfo_height(),
                                                                        xp, yp))
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        if(command!=None):
          self.displayHelp(command)
        self.root.mainloop()
        

    def _setup_widgets(self):
        msg = Label(wraplength="4i", justify="left", anchor="n",
            padding=(5, 2, 10, 5),
            text=("Double click on a command to get a description of all its parameters"))
        msg.pack(side=TOP,fill='x',expand=True)

        self.container = Frame(self.root)
        self.container.pack(side=TOP,fill=BOTH, expand=True)
        self._setup_tree()
        self.buttonFrame = Frame(self.root)
        self.buttonFrame.pack(side=TOP,fill=BOTH,expand=True)
        self.button = Button(self.buttonFrame,text="Close",command=self.close)
        self.button.pack(side=LEFT,expand=True,fill=BOTH)
        self.spacer = Button(self.root,text='    ',state=DISABLED)
        self.spacer.pack(side=TOP,expand=True,fill=BOTH)        
    pass
    
    def close(self):
      self.root.quit()
      self.root.destroy()
    pass
    
    def _setup_tree(self):
        if(self.tree!=None):
          self.tree.destroy()
        # XXX Sounds like a good support class would be one for constructing
        #     a treeview with scrollbars.
        self.tree = Treeview(self.container,columns=self.columns, show="headings")
        vsb = Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=self.container)
        vsb.grid(column=1, row=0, sticky='ns', in_=self.container)
        hsb.grid(column=0, row=1, sticky='ew', in_=self.container)

        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.data = map(lambda x:(x.name,x.description),self.commands.values())
        for col in self.columns:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))
            # XXX tkFont.Font().measure expected args are incorrect according
            #     to the Tk docs
            self.tree.column(col, width=tkFont.Font().measure(col.title()))
        self.items = []    
        for item in self.data:
            self.items.append(self.tree.insert('', 'end', values=item))

            # adjust columns lenghts if necessary
            for indx, val in enumerate(item):
                ilen = tkFont.Font().measure(val)
                if self.tree.column(self.columns[indx], width=None) < ilen:
                    self.tree.column(self.columns[indx], width=ilen)
        self.tree.bind("<Double-1>", self.OnDoubleClick)
    pass
    
    def OnDoubleClick(self,event):
        #import pdb;pdb.set_trace()
        #item = self.tree.selection()[0]
        #print "you clicked on", self.tree.item(item,"values")[0]
        #self.tree.set(item,0,'TEST')
        item = self.tree.selection()[0]
        par  = self.tree.item(item,"values")
        self.displayHelp(par[0])
    pass
    
    def displayHelp(self,commandName):
        try:
          message = self.commands[commandName].getHelp(printHelp=False)
        except:
          raise ValueError("Command not found: %s" %(commandName))
        transient = Toplevel(self.root)
        transient.transient(self.root)
        transient.wm_title("%s help" %(commandName))
        transient.wm_iconname("%s help" %(commandName))
        frame = Frame(transient)
        frame.pack(side=TOP,fill=BOTH,expand=True)
        frame2 = Frame(transient)
        frame2.pack(side=TOP,fill=BOTH,expand=True)
        #define a new frame and put a text area in it
	text=Text(frame,height=40,width=80,background='white')
	text.insert(END, message)
        
	# put a scroll bar in the frame
	scroll=Scrollbar(frame,orient=VERTICAL)
	scroll.config(command=text.yview)
	#pack everything
	text.pack(side=LEFT,expand=True,fill=BOTH)
        text.configure(yscrollcommand=scroll.set)
	scroll.pack(side=RIGHT,fill=BOTH,expand=True)
        
        #Close button
        button = Button(frame2,text="Close",command=transient.destroy)
        button.pack(side=TOP,expand=True)
    pass  
