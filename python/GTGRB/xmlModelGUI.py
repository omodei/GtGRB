from Tkinter import *
import tkFont
import tkMessageBox 
import ttk
from GTGRB import guiParameters
from GTGRB.commandDefiner import *
import parseXML
import os, shutil
from tkSimpleDialog import askfloat

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

class xmlModelGUI(object):
    def __init__(self,xmlModelFile,root=None):
        if(root==None):
          self.root = Tk()
          self.root.maxsize(1024,768)
          self.root.wm_title("Likelihood model %s" %(os.path.basename(xmlModelFile)))
          self.root.wm_iconname("Likelihood model")
        else:
          self.root = root
        #Make a copy of the xml, which will be modified, and it will be copied back
        #overwritting the input file only at the very end
        self.workingCopy = "__xmlTempModel.xml"
        shutil.copyfile(xmlModelFile,self.workingCopy)
        self.xmlModel = parseXML.parseXML(self.workingCopy)
        self.xmlModelFile = xmlModelFile
        self.columns = self.xmlModel.parameters[0].keys()
        self.tree = None
        self._setup_widgets()
        self.notSaved = False
        #Center the window
        self.root.update_idletasks()
        xp = (self.root.winfo_screenwidth() / 2) - (self.root.winfo_width() / 2)
        yp = (self.root.winfo_screenheight() / 2) - (self.root.winfo_height() / 2)
        self.root.geometry('{0}x{1}+{2}+{3}'.format(self.root.winfo_width(), self.root.winfo_height(),
                                                                        xp, yp))
        self.root.protocol("WM_DELETE_WINDOW", self.done)
        self.root.mainloop()

    def _setup_widgets(self):
        msg = ttk.Label(wraplength="4i", justify="left", anchor="n",
            padding=(5, 2, 10, 5),
            text=("Double click on a parameter to change it."))
        msg.pack(side=TOP,fill='x',expand=True)

        self.container = ttk.Frame(self.root)
        self.container.pack(side=TOP,fill=BOTH, expand=True)

        self._setup_tree()
        self.buttonFrame = ttk.Frame(self.root)
        self.buttonFrame.pack(side=TOP,fill=BOTH,expand=True)
        self.button = Button(self.buttonFrame,text="Done",command=self.done,height=1)
        self.button.pack(side=LEFT,expand=True,fill=BOTH)
        self.button2 = Button(self.buttonFrame,text="Save",command=self.save,height=1)
        self.button2.pack(side=LEFT,expand=True,fill=BOTH)
        self.spacer = Button(self.root,text='    ',height=1,state=DISABLED)
        self.spacer.pack(side=TOP,expand=True,fill=BOTH)        
    pass
    
    def done(self):
      if(self.notSaved):
        if tkMessageBox.askyesno("WARNING!", "You have modified the template but you did not save. Do you really want to exit loosing your changes?"):
          self.root.quit()
          self.root.destroy()
          try:
            os.remove(self.workingCopy)
          except:
            pass
          return
        else:
          return
        pass
      pass
      self.root.quit()
      self.root.destroy()
      try:
        os.remove(self.workingCopy)
      except:
        pass
    pass
    
    def save(self):
      #Copy back the working copy on the input file
      shutil.copyfile(self.workingCopy,self.xmlModelFile)
      self.notSaved = False
      tkMessageBox.showinfo("saved!","Likelihood model saved!")
    pass
    
    def _setup_tree(self):
        if(self.tree!=None):
          self.tree.destroy()
        # XXX Sounds like a good support class would be one for constructing
        #     a treeview with scrollbars.
        self.tree = ttk.Treeview(self.container,columns=self.columns, show="headings")
        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=self.container)
        vsb.grid(column=1, row=0, sticky='ns', in_=self.container)
        hsb.grid(column=0, row=1, sticky='ew', in_=self.container)

        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.data = self.xmlModel.parameters
        for col in self.columns:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))
            # XXX tkFont.Font().measure expected args are incorrect according
            #     to the Tk docs
            self.tree.column(col, width=tkFont.Font().measure(col.title()))
        self.items = []    
        for item in self.data:
            self.items.append(self.tree.insert('', 'end', values=item.values()))

            # adjust columns lenghts if necessary
            for indx, val in enumerate(item.values()):
                ilen = tkFont.Font().measure(val)
                if self.tree.column(self.columns[indx], width=None) < ilen:
                    self.tree.column(self.columns[indx], width=ilen)
        self.tree.bind("<Double-1>", self.OnDoubleClick)
    pass
    
    def OnDoubleClick(self,event):
        item = self.tree.selection()[0]
        par  = self.tree.item(item,"values")

        cmd = Command("Parameter","Change parameter %s" %(par[1]),"0","")
        cmd.addParameter("value","Value",MANDATORY,float(par[2]),partype=REAL)
        cmd.addParameter("min","Minimum value",MANDATORY,float(par[4]),partype=REAL)
        cmd.addParameter("max","Maximum value",MANDATORY,float(par[5]),partype=REAL)
        cmd.addParameter("scale","Scale",MANDATORY,float(par[6]),partype=REAL)
        cmd.addParameter("free","Free to vary?",BOOLEAN,int(par[7]),partype=BOOLEAN,possibleValues=['yes','no'])
        pars = guiParameters.getParameters(cmd,False,self.root)
        if(pars==None):
          return
        else:  
          for k,v in pars.iteritems():
            v                   = str(v)
            if(v=='no'):
              v                 = '0'
            elif(v=='yes'):
              v                 = '1'
            pass
            self.xmlModel.setAttribute(par,k,v)
            self.xmlModel.save()
          pass
          #Reflect the change in the GUI
          self._setup_tree()
          self.notSaved = True
        pass
    pass  
        
def main():
    root = Tk()
    root.maxsize(1024,768)
    xmlModelFile = "100724029_model_LIKE_MY_0.000_300.000.xml"
    root.wm_title("Likelihood model %s" %(os.path.basename(xmlModelFile)))
    root.wm_iconname("Likelihood model")
    app = xmlModelGUI(xmlModelFile,root)
    root.mainloop()

if __name__ == "__main__":
    main()
