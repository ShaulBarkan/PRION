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

import math
pKs = {'A': [2.4,  9.9],
       'C': [1.9, 10.8,   8.3],
       'D': [2.0,  9.9,   3.9],
       'E': [2.1,  9.5,   4.1],
       'F': [2.2,  9.2],
       'G': [2.4, 9.8],
       'H': [1.8,  9.2,   6.0],
       'I': [2.3,  9.8],
       'K': [2.2,  9.2,  10.8],
       'L': [2.3,  9.7],
       'M': [2.1,  9.3],
       'N': [2.1,  8.8],
       'P': [2.0, 10.6],
       'Q': [2.2,  9.1],
       'R': [1.8,  9.0,  12.5],
       'S': [2.2,  9.2,  13.0],
       'T': [2.1,  9.1,  13.0],
       'V': [2.2,  9.7],
       'W': [2.4,  9.4],
       'Y': [2.2,  9.1,  10.1]}

def calculate_charge_from_sequence(sequence, pH=7.0):
    charge = 0.0
    for res in sequence:
        if res == 'D':
            if pH > pKs['D'][2]:
                charge -= 1.0
        elif res == 'E':
            if pH > pKs['E'][2]:
                charge -= 1.0
        elif res == 'K':
            if pH < pKs['K'][2]:
                charge += 1.0
        elif res == 'R':
            if pH < pKs['R'][2]:
                charge += 1.0
        elif res == 'H':
            if pH < pKs['H'][2]:
                charge += 1.0
    return charge

def calculate_pI_from_sequence(sequence):
    charge = calculate_charge_from_sequence(sequence)
    counts = {'D':0,'E':0,
              'K':0,'R':0,'H':0}
    for res in sequence:
        if res in counts.keys():
            counts[res] += 1
    my_pks = []
    my_pks.append(pKs[sequence[0]][1])
    my_pks.append(pKs[sequence[-1]][0])
    for res in sequence:
        if res in counts.keys():
            my_pks.append(pKs[res][2])
    my_pks.sort()
    pk1_index = int(math.floor(len(my_pks)/2.0)+charge)-1
    if pk1_index >= len(my_pks)-1:
        PI = my_pks[-1]
    elif pk1_index <= 0:
        PI = my_pks[0]
    else:
        PI = (my_pks[pk1_index] + my_pks[pk1_index+1])/2.0
    return PI
        
                