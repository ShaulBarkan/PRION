# Copyright (c) 2001-2008, Deacon John Sweeney
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Wright State University nor the names of its 
#       contributors may be used to endorse or promote products derived from 
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY DEACON JOHN SWEENEY ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL DEACON JOHN SWEENEY BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from Tkinter import *
import Pmw

class ScopFrame(Frame):
	def __init__(self, parent=None):
		Frame.__init__(self, bg='white')
		self.toplevel = parent
		
		self.menuBar = Pmw.MenuBar(self, hull_relief=RAISED,	hull_borderwidth=1)
		self.menuBar.pack(fill=X, expand=YES, anchor=N)
		
		self.menuBar.addmenu('Profiles', 'Search Profiles')
		self.menuBar.addmenuitem('Profiles', 'command', label='Load Profiles')
		self.menuBar.addmenuitem('Profiles', 'command', label='Edit Profiles')

		self.menuBar.addmenu('Search', 'Search Entire SCOP Database')
		self.menuBar.addmenuitem('Search', 'command', label='Search SCOP')

		self.treeWinText = Text(self, cursor="arrow")		
		self.sbar = Scrollbar(self)
		self.sbar.config(command=self.treeWinText.yview)
		self.treeWinText.config(yscrollcommand=self.sbar.set)
		self.sbar.pack(side=LEFT, fill=Y) 
		self.treeWinText.config(height=15, width=60)
		self.treeWinText.pack(side=LEFT, expand=YES, fill=BOTH)

		self.lineageBox = Text(self, relief=FLAT, cursor = "arrow")
		self.lineageBox.pack(side=TOP, anchor=N, expand=YES, fill=BOTH)
		self.lineageBox.config(height=8, width=38, state=DISABLED)
		
		self.viewButton = Button(self, text="View", state=DISABLED, height=1, command=lambda: self.toplevel.displaySelected, width=5)
		self.viewButton.pack(side=LEFT, anchor=S, padx=10)
		
		self.pack(expand=YES, fill=BOTH)
		
		
if __name__ == '__main__':
	root = Tk()
	ScopFrame().mainloop()