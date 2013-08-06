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

import sys
sys.path.append('Dependencies')
import Pmw
import string

class functional_pmw_counter(Pmw.Counter):
    def __init__(self, a, b, c, d, e, f, g):
        Pmw.Counter.__init__(self, a, labelpos = b, label_text = c, entryfield_value = d, entryfield_validate = e, datatype = f, increment = g)
        self.parent_frame        = a
        self.labelpos            = b
        self.label_text          = c
        self.entryfield_value    = d
        self.entryfield_validate = e
        self.datatype            = f
        self.increment           = g
        self.function = self.empty_function
        self.enabled = 1
        self.active = 0
    def disable(self):
        self.component('entryfield').component('entry').config(state='disabled')
        self.enabled = 0
    def enable(self):
        self.component('entryfield').component('entry').config(state='normal')
        self.enabled = 1
    def empty_function(self):
        pass
    def update_function(self, new_function):
        self.function = new_function
    def _countUp(self, event):
        # override for disable control and attaching the increment/decrement to the filename
        self.active=1
        if self.enabled:
            Pmw.Counter._countUp(self, event)
    def _countDown(self, event):
        self.active=1
        if self.enabled:
            Pmw.Counter._countDown(self, event)
    def _stopCounting(self, event):
        Pmw.Counter._stopCounting(self, event)
        if self.active==1:
            t = self.component('entryfield').getvalue()
            if self.entryfield_validate['validator'] == 'time':
                t_tokens = string.split(t, ':')
                a = string.atoi(t_tokens[0])*60*60
                b = string.atoi(t_tokens[1])*60
                c = string.atoi(t_tokens[2])
                seconds = float(a + b + c)
                self.function(seconds)
            elif self.entryfield_validate['validator'] == 'integer':
                self.function()
            self.active=0
