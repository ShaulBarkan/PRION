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
import os
sys.path.append(os.getcwd())
from MolecularComponents.classMolecule import Molecule
from MolecularComponents.classPoint import Point
import string

class Nucleotide(Molecule):
    def __init__(self, PDBlines, parent, atoms):
        Molecule.__init__(self, PDBlines)
        self.parent = parent
        self.atoms = atoms
        for atom in atoms:
            atom.parent = self
        line = PDBlines[0]
        self.res_type1  = string.strip(line[17:20])
        self.res_number = string.atoi(line[23:26])

        self.is_Nterm = 0
        self.is_Cterm = 0
        self.has_central_pt = 0    
        self.atoms_dict = {}
        for atom in self.atoms:
            self.atoms_dict[atom.atom_type] = atom
            if atom.atom_type[:2] == 'C3':
                self.central_pt = Point(atom.x, atom.y, atom.z)
                self.central_atom = atom
                self.x=atom.x
                self.y=atom.y
                self.z=atom.z
                self.has_central_pt = 1
        self.is_Nterm = 0
        self.is_Cterm = 0
        self.vtk_arg_list = {}
        

        trace_args = {'color':[0.1,0.1,1.0],
                      'opacity':1.0}
        self.vtk_arg_list['trace'] = trace_args
        self.visible = 0
        self.transparent = 0

