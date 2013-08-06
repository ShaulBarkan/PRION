from Tkinter import *
import sys
sys.path.append('./Dependencies')
import Pmw
import os

class viewer:
    def __init__(self, parent, parent_window, alias_system=None, alias_viewer=None):
        """SPADE' CodeBox has two panels, where output is presented on the left or bottom, and the right 
        or top contains a textbox where code can be simply written and evaluated, and where script files can 
        be managed. A PMW Notepad allows multiple files to be edited simultaneously.
        """
        print 'Codebox Next and Prev commands dont yet capture w/out mouse interaction'
        self.alias_system = alias_system         # used when codebox is attached to a MolecularViewer
        self.alias_viewer = alias_viewer
        self.parent = parent
        self.window = parent_window
        # controls label
        labelfont = ('times', 8)
        self.controls_label = Label(self.window, text='NEW:ctrl+N   EXECUTE:ctrl+X   SAVE:ctrl+S   CLOSE:ctrl+shift+Q   NEXT:ctrl+right arrow   PREV:ctrl+left arrow', font=labelfont)
        self.controls_label.pack(side=TOP,fill='x', expand=0, padx=0,pady=0)
        # First create the paned widget
        self.pw = Pmw.PanedWidget(self.window,orient='horizontal',
                                  hull_borderwidth = 1,
                                  hull_relief = 'sunken',
                                  hull_height=100)
        self.window.bind("<Control-x>", self.executeCurrentScript)
        self.window.bind("<Control-n>", self.addNewScript)
        self.window.bind("<Control-Shift-q>", self.closeCurrentScript)
        self.window.bind("<Control-s>", self.saveCurrentScript)
        self.window.bind("<Control-Right>", self.nextScript)
        self.window.bind("<Control-Left>", self.lastScript)
        self.output_pane  = self.pw.add('Output', min=.1,max=.9,size=.5)
        self.input_pane   = self.pw.add('Input',  min=.1,max=.9,size=.5)
        self.pw.pack(side=BOTTOM, anchor=S,expand=1,fill='both')
        # The left gets a scrolled text box
        self.output_textbox = Pmw.ScrolledText(self.output_pane, borderframe=5,text_wrap='none')
        self.output_textbox.configure(text_state='disabled')
        self.output_textbox.pack(expand=1, fill='both', padx=2, pady=2)
        # The right gets a Pmw Notebook
        self.file_notebook = Pmw.NoteBook(self.input_pane, borderwidth=1,pagemargin=2)
        self.file_notebook.pack(fill='both', expand = 1, padx = 2, pady = 2)
        self.file_pages = {}
        self.addNewScript()
        # create a default starting page
        #self.pw.setnaturalsize()
        self.pw.updatelayout()
        
    def destroy(self):
        self.controls_label.destroy()
        self.pw.destroy()

    def addNewScript(self, event=None):
        """ make a new filename of the format tmp#.mpy, where # is some value not present in the current list
         of opened mpy scripts."""
        names = self.file_notebook.pagenames()
        print names
        for i in range(0,10):
            file_name = 'tmp%d.mpy'%(i)
            if file_name not in names:
                break
        else:
            print "Too many files open (>10)\n"
        print file_name
        self.file_pages[file_name] = self.file_notebook.add(file_name)
        self.file_pages[file_name].text = Pmw.ScrolledText(self.file_pages[file_name], borderframe=5,text_wrap='none')
        self.file_pages[file_name].text.pack(fill='both', expand=1, padx=3, pady=3)

    def nextScript(self, event):
        self.file_notebook.nextpage()
        active_page = self.file_pages[self.file_notebook.getcurselection()]
        active_page.text.focus_force()
        active_page.text.tag_add(SEL, 1.0, END)

    def lastScript(self, event):
        self.file_notebook.previouspage()
        active_page = self.file_pages[self.file_notebook.getcurselection()]
        active_page.text.focus_force()
        active_page.text.tag_add(SEL, 1.0, END)

    def execute_script_callback(self, event):
        self.executeCurrentScript()

    def executeCurrentScript(self, event=None):
        """ execute the currently selected script """
        selected_title = self.file_notebook.getcurselection()
        self.saveCurrentScript()
        if self.alias_system:
            globals = {'system':self.alias_system, 'viewer':self.alias_viewer}
        else:
            globals = {'systems':self.parent.systems, 'spade':self.window, 'system_windows':self.parent.system_windows}
        locals  = {}
        exec open(os.path.join('Scripts', selected_title)).read() in globals, locals
        
    def saveCurrentScript(self, event=None):
        """ save the currently selected script """
        selected_title = self.file_notebook.getcurselection()
        text = self.file_pages[selected_title].text.get(1.0,'end')
        self.executing_file = open('Scripts/%s'%(selected_title), 'w')
        self.executing_file.writelines(text)
        self.executing_file.close()

    def closeCurrentScript(self, event=None):
        """ close the currently selected script """
        selected_title = self.file_notebook.getcurselection()
        self.file_notebook.delete(selected_title)
        
    def write(self, text):
        """ write text to the outbox of the codebox. This functions is present to override stdout. Use
        python's normal print() command instead."""
        self.output_textbox.configure(text_state='normal')
        self.output_textbox.insert(END, text)
        self.output_textbox.configure(text_state='disabled')
        self.output_textbox.see(END)
        self.output_textbox.update_idletasks()
