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
from MolecularComponents.classNucleotide import Nucleotide
from MolecularComponents.classPolymer import Polymer
import parms

verbose = 1

class NucleotideChain(Polymer):
    def __init__(self, chainlines, parent):
        Polymer.__init__(self,chainlines, parent)
        # store a list element for each nucleotide in chainlines
        last_line = None
        current_residue = []
        atoms = []
        atom_cnt = 0
        for line in chainlines:
            current_line = line[25:29]
            if current_line == last_line:
                # just append to the previously created one
                current_residue.append(line)
                atoms.append(self.atoms[atom_cnt])
            else:
                # make a new amino acid and append it to residues list
                if len(current_residue)>0:
                    new_residue = Nucleotide(current_residue, self, atoms)
                    self.add_residue(new_residue)
                # reset the current list and append the new line to it
                current_residue = []
                current_residue.append(line)
                atoms = []
                atoms.append(self.atoms[atom_cnt])
            last_line = current_line
            atom_cnt = atom_cnt + 1
        # append the last one created
        new_residue = Nucleotide(current_residue, self, atoms)
        self.add_residue(new_residue)
        self.locate_termini()
        self.residues_dict = {}
        for res in self.residues:
            self.residues_dict['%s'%(res.res_number)] = res

    def res_number_to_residues_index(self, res_number):
        index = 0
        for rez in self.residues:
            if rez.res_number == res_number:
                return index
            index = index + 1
        else:
            return -1
    def get_sequence(self):
        my_sequence = ''
        for rez in self.residues:
            my_sequence = my_sequence + rez.res_type
        return my_sequence
    def print_sequence(self):
        x = self.get_sequence()
        print x
    

