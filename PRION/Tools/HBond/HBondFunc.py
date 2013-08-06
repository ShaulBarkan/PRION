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

import re
import string

"""
 Read the protonation information from the data file
"""
def read_protonation_info (protonFile):
    protonsInfo = []
    # Read the protonation information from the data file
    fproton = open (protonFile,"r")
    comment_pat = re.compile ("^#")
    # Format of a protonation line is:
    # AA Name,D,DD1,DD2,DDD1,DDD2,Hybridization,Bonds,D-H distance,Angles
    for line in fproton:
        line = string.strip (line)
        if (not comment_pat.search (line) and line != ''):
            fields=string.split (line,",")
            protonInfo={}
            protonInfo['aminoAcidName']=fields[0]
            protonInfo['atomName']=fields[1]
            protonInfo['DD1Name']=fields[2]
            protonInfo['DD2Name']=fields[3]
            protonInfo['DDD1Name']=fields[4]
            protonInfo['DDD2Name']=fields[5]
            protonInfo['hyb']=fields[6]
            protonInfo['bonds']=fields[7]
            protonInfo['D-H']=string.atof(fields[8])
            protonInfo['angles']=fields[9]
            protonsInfo.append (protonInfo)
    fproton.close()

    return protonsInfo

"""
 Find the proton information for a given atom and residue
"""
def find_proton_info (res_type,atom,protonsInfo):
    for protonInfo in protonsInfo:
        atom_type = atom.atom_type
        if (protonInfo['atomName'] == atom_type and
            (res_type == protonInfo['aminoAcidName'] or protonInfo['aminoAcidName'] == '*')):
            return protonInfo
    return None

"""
 Find the donor information for a given atom
"""
def find_donor_info (res_type,atom,donorsInfo):
    for donorInfo in donorsInfo:
        if (donorInfo['atomName'] == atom.atom_type and
            (res_type == donorInfo['aminoAcidName'] or donorInfo['aminoAcidName'] == '*')):
            return donorInfo
    return None

"""
 Read donor information
"""
def read_donor_info (donorFile):
    donorsInfo = []
    fdonor = open (donorFile,"r")
    comment_pat = re.compile ("^#")
    # Format of a donor line is:
    # AA Donor Name, Donor Atom Name
    for line in fdonor:
        line = string.strip (line)
        if (not comment_pat.search (line) and line != ''):
            fields=string.split (line,",")
            donorInfo={}
            donorInfo['aminoAcidName']=fields[0]
            donorInfo['atomName']=fields[1]
            donorsInfo.append (donorInfo)
    fdonor.close()
    return donorsInfo


"""
 Find the acceptor information for a given atom
"""
def find_acc_info (res_type,atom,accsInfo):
    for accInfo in accsInfo:
        if (accInfo['atomName'] == atom.atom_type and
            (res_type == accInfo['aminoAcidName'] or accInfo['aminoAcidName'] == '*')):
            return accInfo
    return None

"""
 Read the acceptor information
"""
def read_acc_info (accFile):
    accsInfo = []
    facc = open (accFile,"r")
    comment_pat = re.compile ("^#")
    # Format of a acceptor line is:
    # Amino Acid Name, A, AA
    for line in facc:
        line = string.strip (line)
        if (not comment_pat.search (line) and line != ''):
            fields=string.split (line,",")
            accInfo={}
            accInfo['aminoAcidName']=fields[0]
            accInfo['atomName']=fields[1]
            accInfo['AAName']=fields[2]
            accsInfo.append (accInfo)
    facc.close()
    return accsInfo
