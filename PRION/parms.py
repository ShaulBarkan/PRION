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

import os
import pickle
import string


peakrec_fraction = 2
home_dir = '.'

parms_dat = os.path.join(home_dir, 'parms.dat')

def get(query_parm=None):
    execfile(parms_dat, globals())
    if query_parm == None:
        return parms_list.keys()
    else:
        return parms_list[query_parm]

def set(query_parm, value):
    parms_file = open(parms_dat, 'r')
    lines = parms_file.readlines()
    for lind in range(len(lines)):
        line = string.strip(lines[lind])
        if query_parm in line:         # if already present, modify, else, append at the end
            lines[lind:lind+1] = '    \'%s\':%s,\n'%(query_parm, repr(value))
            break
    else:
        lineslen = len(lines)
        lines[lineslen-1:lineslen-1] = '    \'%s\':%s,\n'%(query_parm, repr(value))
    parms_file.close()
    parms_file = open(parms_dat, 'w')
    parms_file.writelines(lines)
    parms_file.close()

def what():
    execfile(parms_dat, globals())
    print parms_list.keys()
    