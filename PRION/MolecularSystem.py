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

# python imports
import sys
import os
import re
import parms
import pickle
import copy
import math
import random
import string
# internal imports
sys.path.append(os.getcwd())
from MolecularComponents.classAtom            import Atom
from MolecularComponents.classMolecule        import Molecule
from MolecularComponents.classWater           import Water
from MolecularComponents.classLigand          import Ligand
from MolecularComponents.classAminoAcid       import AminoAcid
from MolecularComponents.classNucleotide      import Nucleotide
from MolecularComponents.classPolymer         import Polymer
from MolecularComponents.classProtein         import Protein
from MolecularComponents.classNucleotideChain import NucleotideChain
from MolecularComponents.classPoint           import Point
from MolecularComponents.classFutamuraHash    import FutamuraHash
import MolecularComponents.MathFunc
verbose = 0
#sys.path.append('./Tools/Aligner')
#import SequenceAligner

# SystemMemory objects are located and described at the bottom of this file

class System:
    def __init__(self, file_name):
        """ initialize a system object from a pdb or sms file """
        self.__module__ = "System"
        self.filename = file_name
        if file_name:
            tokens = string.split(file_name, '.')
            self.load(file_name, tokens[-1])

    def get_filename(self):
        return self.filename

    def select(self):
        self.selected = 1
        
    def deselect(self):
        self.deselected = 1
        
    def load(self, filename, type_arg):
        self.filename = filename
        self.x_table = None
        self.selected = 1
        self.visible  = 1
        type = string.upper(type_arg)
        if type == 'SPS':
            self.load_system(filename)
        elif type in ['PDB', 'ENT']:
            self.load_pdb(filename, 1)
        else:
            print 'did not recognize the file type as .pdb, .ent, or .sps'
        self.vtk_arg_list = {}
        hbond_args   = {'visualize':0,
                        'currently_on':0,
                        'representation':'lines',
                        'width':0.4,
                        'sides':5,
                        'specular':0.1,
                        'specular_power':10}
        self.vtk_arg_list['hbonds']  = hbond_args

    def load_pdb(self, filename, silent=0):
        if not silent:
            print "Opening pdb file %s\n"%(os.path.split(filename)[1])
        """ parse a pdb file and load it as a system object."""
        self.filename = filename
        self.selected = 1
        self.ProteinList         = []
        self.NucleotideChainList = []
        self.LigandList          = []
        self.WaterList           = []
        self.HeaderLines         = []
        self.HBonds              = []
        self.header             = ''
        self.resolution          = None
        # open the file
        if len(filename) == 0:
            return
        PDBfile = open(filename, 'r')
        # separate atoms, HETATMS, and other
        ATOMlines   = []
        HETATMlines = []
        ANISlines   = []        # anisotropy cards are ignored
        otherlines  = []
        while 1:
            line = PDBfile.readline()
            if not line: 
                break
            # should be able to tell from the first 4 characters of each line
            if line[0:4] == 'ATOM':
                if line[16:17] == ' ' or line[16:17] == 'A':
                    ATOMlines.append(line)
            elif line[0:4] == 'HETA':
                if line[16:17] == ' ' or line[16:17] == 'A':
                    HETATMlines.append(line)
            elif line[0:4] == 'ANIS':
                ANISlines.append(line)
            elif line[0:4] == 'REMA':
                self.HeaderLines.append(line)
                if "RESOLUTION" in line:
                    tokens = string.split(line)
                    for i in range(len(tokens)):
                        token = tokens[i]
                        if 'RESOLUTION' in token:
                            try:
                                float(tokens[i+1])
                            except:
                                pass
                            else:
                                self.resolution = float(tokens[i+1])
            elif line[0:4] in ['TER ','MAST','CONE','END ']:
                pass
            else:
                self.HeaderLines.append(line)
        for line in self.HeaderLines:
            if line[0:4] == 'HEAD':
                self.header = string.strip(line[6:])
                
        if verbose:
            print "%d atoms" % len(ATOMlines)
            print "%d hetero atoms" % len(HETATMlines)
            print "%d header lines" % len(otherlines)

        # next make a list of lines for the amino acids and nucleotides
        AATypes = parms.get('AATypes')
        NUCTypes = ['A','G','C','T','U']
        WATTypes = parms.get('WATTypes')
        AAlines = []
        NUClines = []
        WATlines = []
        OTHlines = []
        for line in ATOMlines:
            if line[17:20] in AATypes:
                AAlines.append(line)
            elif string.strip(line[17:20]) in NUCTypes:
                NUClines.append(line)
            elif line[17:18] in NUCTypes and line[19:20] == " ":
                NUClines.append(line)
            elif line[17:20] in WATTypes:
                WATlines.append(line)
            else:
                OTHlines.append(line)
        for line in HETATMlines:
            if line[17:20] in WATTypes:
                WATlines.append(line)
            else:
                OTHlines.append(line)

        # now separate the chains
        # first collect the chain names for AAlines
        if len(AAlines) > 0:
            proteinchainlist = []
            for line in AAlines:
                if line[21:22] in proteinchainlist:
                    pass
                else:
                    proteinchainlist.append(line[21:22])
            # and create a list for each
            separatedlists = []
            for chainname in proteinchainlist:
                newlist = []
                for line in AAlines:
                    if chainname == line[21:22]:
                        newlist.append(line)
                separatedlists.append(newlist)
            # now create all of the Protein objects
            for slist in separatedlists:
                newprotein = Protein(slist, self)
                self.ProteinList.append(newprotein)

        # next make a list of all nucleotide lines
        # and create all of the NucleotideChain objects
        if len(NUClines) > 0:
            NUCchainlist = []
            for line in NUClines:
                if line[21:22]in NUCchainlist:
                    pass
                else:
                    NUCchainlist.append(line[21:22])
            if verbose:
                if len(NUCchainlist) == 1:
                    print "1 nucleotide chain loading"
                else:
                    print "%d nucleotide chains loading" % len(NUCchainlist)
            # and create a list for each
            separatedlists = []
            for chainname in NUCchainlist:
                newlist = []
                for line in NUClines:
                    if chainname == line[21:22]:
                        newlist.append(line)
                separatedlists.append(newlist)
            # now create all of the Nucleotide chain objects
            for slist in separatedlists:
                newnucchain = NucleotideChain(slist, self)
                self.NucleotideChainList.append(newnucchain)

        # now make a list of all other molecule types
        # and create all of the ligand Molecule objects
        # pass through the list, collecting by residue number
        if len(OTHlines) > 0:
            last_rez_num = None
            current_molecule = []
            for line in OTHlines:
                current_rez_num = string.atoi(line[23:26])
                if current_rez_num == last_rez_num:
                    current_molecule.append(line)
                else:
                    if len(current_molecule)>0:
                        new_molecule = Ligand(current_molecule, self)
                        self.LigandList.append(new_molecule)
                    current_molecule = []
                    current_molecule.append(line)
                last_rez_num = current_rez_num
            new_molecule = Ligand(current_molecule, self)
            self.LigandList.append(new_molecule)

            mol_names = []
            for mol in self.LigandList:
                mol_names.append(mol.res_type)
            if verbose:
                if len(self.LigandList) == 1:
                    print "1 ligand molecule %s" % (mol_names)
                else:
                    print "%d ligand molecules %s" % (len(self.LigandList), mol_names)

        # once ligands have been read in, then process the water list
        # so that they can be numbered sequentially
        if len(WATlines) > 0:
            last_rez_num = None
            current_molecule = []
            for line in WATlines:
                current_rez_num = line[23:26]
                if current_rez_num == last_rez_num:
                    current_molecule.append(line)
                else:
                    if len(current_molecule)>0:
                        new_molecule = Water(current_molecule)
                        self.WaterList.append(new_molecule)
                    current_molecule = []
                    current_molecule.append(line)
                last_rez_num = current_rez_num
            if len(current_molecule) > 0:
                new_molecule = Water(current_molecule)
                self.WaterList.append(new_molecule)
            if verbose:
                if len(self.WaterList) == 1:
                     print "1 water molecule"
                else:
                    print "%d water molecules" % (len(self.WaterList))
        PDBfile.close()
        self._supplementary_initialization(silent)

    def _supplementary_initialization(self, silent=0):
        """ Completes initialization by rebuilding the redundant object from stored data.
            Data is never duplicated, only pointers.
        """
        self.MoleculeList        = []
        self.SmallMoleculeList   = []
        self.PolymerList         = []
        self.PolymerDict         = {}
        self.ProteinDict         = {}
        self.NucleotideChainDict = {}
        self.LigandDict          = {}
        self.WaterDict           = {}
        # now create dictionaries out of the lists
        for pchain in self.ProteinList:
            self.ProteinDict[pchain.key] = pchain
        for nchain in self.NucleotideChainList:
            self.NucleotideChainDict[nchain.key] = nchain
        for lig in self.LigandList:
            self.LigandDict[lig.key] = lig
        for wat in self.WaterList:
            self.WaterDict[wat.key] = wat

        # these can be uncommented to remove water functionality (some of which may not be finished)
        #self.WaterList = []
        #self.WaterDict = {}

        # count the atoms first, for a printout and to set 
        items = [self.ProteinList, self.NucleotideChainList, self.LigandList, self.WaterList]
        count = 0
        for item in items:
            for mol in item:
                count = count + len(mol.atoms)
        self.atom_count = count
        # set up the MoleculeList
        items = [self.ProteinList, self.NucleotideChainList, self.LigandList]
        count = 0
        for item in items:
            for mol in item:
                self.MoleculeList.append(mol)
        # use MoleculeList to create atom_dict features for all molecules
        for mol in self.MoleculeList:
            mol.atom_dict = {}
            for atom in mol.atoms:
                mol.atom_dict[atom.atom_number] = atom
        # set up the SmallMoleculeList
        items = [self.LigandList, self.WaterList]
        count = 0
        for item in items:
            for mol in item:
                self.SmallMoleculeList.append(mol)
        # set up PolymerList and PolymerDict
        items = [self.ProteinList, self.NucleotideChainList]
        count = 0
        for item in items:
            for mol in item:
                self.PolymerList.append(mol)
                self.PolymerDict[mol.chain_name] = mol
        # create b_factor features
        self.normalize_b_factors()
        self.log_b_factors()
        reslen = 0
        for chain in self.PolymerList:
            reslen += len(chain.residues)
        if not silent:
            print 'loaded %s atoms and %s residues in %d polymers, %d ligands, %d waters'%(self.atom_count, reslen, len(self.PolymerList), len(self.LigandList), len(self.WaterList))
                
    def add_protein(self, prot):
        self.ProteinList.append(prot)
        self.PolymerList.append(prot)
        self.ProteinDict[prot.chain_name] = prot
        self.PolymerDict[prot.chain_name] = prot
        self.MoleculeList.append(prot)
        
    def get_resolution(self):
        return self.resolution

    def renumber_atoms(self):
        atom_number = 1
        for pchain in self.ProteinList:
            for atom in pchain.atoms:
                atom.atom_number = atom_number
                atom_number += 1
        for nchain in self.NucleotideChainList:
            for atom in nchain.atoms:
                atom.atom_number = atom_number
                atom_number += 1
        for lig in self.LigandList:
            for atom in lig.atoms:
                atom.atom_number = atom_number
                atom_number += 1
        for wat in self.WaterList:
            for atom in wat.atoms:
                atom.atom_number = atom_number
                atom_number += 1

    def create_hydrogen(self, chain_name, res_number, atom_name, coordinates_list, redo=0):
        """ used by Tool Protonate
            currently only confirmed to work for protein chains. res_number could potentially
            be filled with a ligand's res_type to uniquely identify the molecule, and
            distinguish from a polymer. nomenclature should be checked for nucleotides,
            ligands, and waters. Renumbers atoms at the end 
        """
        # the nomenclature may need to be adjusted to account for hydrogens
        # that extend the length of the main chain. For example, the terminal 
        # three hydrogens of lysine should probably be named HH1, HH2, and HH3,
        # as opposed to being named after the terminal lysine
        #
        # response: this is not the case. The standard is that hydrogens are named after
        # the heavy atoms they are attached to.
        #
        atom_place = atom_name[1:]
        if (len(atom_place) > 0):
            regx = re.compile (atom_place)
        else:
            regx = re.compile ("^\d*$")
        hyd_present = 1
        target_chain = self.PolymerDict[chain_name]
        target_res = target_chain.residues_dict['%s'%(res_number)] 
        for atom in target_res.atoms:
            if atom.atom_type[0] == 'H':
                if regx.match(atom.atom_type[1:]):
                    hyd_present += 1

        if hyd_present == 2:
            for atom in target_res.atoms:
                if atom.atom_type[0] == 'H':
                    if regx.match(atom.atom_type[1:]):
                        atom.atom_type += '1'
         
        atom_number = 0
        if hyd_present >= 2:
            atom_type   = 'H' + atom_place + '%s'%(hyd_present)
        else:
            atom_type   = 'H' + atom_place
        res_type    = target_res.res_type
        x,y,z = coordinates_list[0], coordinates_list[1], coordinates_list[2]
        new_atom = Atom(target_chain.residues_dict['%s'%(res_number)],\
                        "ATOM %6s%5s %3s %1s%4s %11.3f %7.3f %7.3f%26s\n"\
                        %(atom_number,atom_type,res_type,chain_name,res_number,x,y,z, " "))
        new_atom.data['parent_molecule'] = target_res
        # can just insert into the residue's dictionary
        target_res.atoms_dict[new_atom.atom_type] = new_atom
        # find the correct heavy atom and append after any hydrogens that follow it.
        found_the_heavy_atom = 0
        counter = 0
        for atom in target_res.atoms:
            if not found_the_heavy_atom:
                if regx.match(atom.atom_type[1:]):
                    found_the_heavy_atom = 1
                    counter += 1
                    continue
            else:
                if atom.atom_type[0] == 'H':
                    counter += 1
                    continue
                else:
                    target_res.atoms[counter:counter] = [new_atom]
                    break
        else:
            target_res.atoms.append(new_atom)
        # now that the residue is changed, rebuild the atoms list for the
        # polymer or molecule
        target_chain.atoms = []
        for res in target_chain.residues:
            for atom in res.atoms:
                target_chain.atoms.append(atom)
        # polymers have no atoms_dict, but ligands will. insert code here
        self.renumber_atoms()
        return new_atom

    def create_hbonds (self,availAcceptors=None,availDonors=None,strict=True):
        """
         Create all of the hydrogen bonds. Right now it only handles protein atoms.
         Sets member 'HBonds':
             {'accAtom', 'donorAtom', 'hydAtom', 'HBondInfo'}
         Parameters: strict=>False... ignore angle requirements
        """
        # Get all of the available acceptors and donors
        avAccs = []
        avDonors = []
        if (availAcceptors != None):
            avAccs = availAcceptors
        if (availDonors != None):
            avDonors = availDonors

        if (availAcceptors == None or availDonors == None):
            for protein in self.ProteinList:
                protein.protonate ("./Tools/HBond/protonate.dat")
                if (availAcceptors == None):
                    avAccs[len(avAccs):]=protein.get_avail_acceptors ("./Tools/HBond/acceptors.dat")
                if (availDonors == None):
                    avDonors[len(avDonors):]=protein.get_avail_donors ("./Tools/HBond/donors.dat")

        # Initialize all of the hydrogen bond arrays to empty
        self.HBonds=[]
        for acceptor in avAccs:
            acceptor['accAtom'].Acc_HBonds=[]
        for donor in avDonors:
            donor['donorAtom'].Donor_HBonds=[]
    
        # Enumerate all of the acceptor/donor pairs that could hydrogen bond
        
        da_pairs_present = []
        for acceptor in avAccs:
            for donor in avDonors:
                # Cannot hbond to yourself
                if (donor['donorAtom'] == acceptor['accAtom']):
                    continue
                pair1 = '%s_%s'%(acceptor['accAtom'].atom_number, donor['donorAtom'].atom_number)
                pair2 = '%s_%s'%(donor['donorAtom'].atom_number, acceptor['accAtom'].atom_number)
                for hydAtom in donor['hydAtoms']:
                    if hydAtom.dist(acceptor['accAtom']) > 3.0:
                        continue
                    if (pair1 in da_pairs_present or pair2 in da_pairs_present):
                        continue
                    HBondInfo = self.measure_hbond(acceptor,donor,hydAtom)
                    if (self.is_valid_hbond (HBondInfo,strict)):
                        HBondInfo['strength'] = self.calculate_block_function_strength(HBondInfo)
                        da_pairs_present.append(pair1)
                        da_pairs_present.append(pair2)
                        hbond = {'accAtom': acceptor['accAtom'], 'donorAtom': donor['donorAtom'],
                                 'hydAtom': hydAtom, 'HBondInfo': HBondInfo,
                                 'vtk_arg_list':{'color':[1.0,0.0,1.0]}}
                        acceptor['accAtom'].Acc_HBonds.append(hbond)
                        donor['donorAtom'].Donor_HBonds.append(hbond)
                        self.HBonds.append (hbond)

        print 'located %s hbonds'%(len(self.HBonds))

    def calculate_block_function_strength(self, HBondInfo):
        # calculate strengths
        # the following energy approximation is a simplified version of the block functions
        # used in ChemScore
        # see http://www.ccdc.cam.ac.uk/support/documentation/gold/3_1/doc/portable_html/gold_portable-3-083.html
        r_ideal       = 1.85
        delta_r_ideal = 0.25
        delta_r_max   = 0.85

        a_ideal       = 180
        delta_a_ideal = 30
        delta_a_max   = 80

        b_ideal       = 180
        delta_b_ideal = 70
        delta_b_max   = 80

        r = HBondInfo['dist_H_A']
        d_r = float(abs(r-r_ideal))
        if d_r > delta_r_max:
            t1 = 0.0
        elif d_r > delta_r_ideal:
            t1 = (delta_r_max - d_r)/delta_r_max
        else:
            t1 = 1.0
        a = HBondInfo['angle_D_H_A']
        d_a = float(abs(a_ideal-a))
        if d_a > delta_a_max:
            t2 = 0.0
        elif d_a > delta_a_ideal:
            t2 = (delta_a_max - d_a)/delta_a_max
        else:
            t2 = 1.0
        b = HBondInfo['angle_H_A_AA']
        d_b = float(abs(b_ideal-b))
        if d_b > delta_b_max:
            t3 = 0.0
        elif d_b > delta_b_max:
            t3 = (delta_b_max - d_b)/delta_b_max
        else:
            t3 = 1.0
        return t1*t2*t3
        
    def measure_hbond (self,acc,donor,hydAtom):
        """
         Measures the possible hbond between the acceptor and donor.
        """
        donorAtom=donor['donorAtom']
        accAtom=acc['accAtom']
        AAAtom=acc['AAAtom']
        Dv=MolecularComponents.MathFunc.r_[donorAtom.x,donorAtom.y,donorAtom.z]
        Hv=MolecularComponents.MathFunc.r_[hydAtom.x,hydAtom.y,hydAtom.z]
        Av=MolecularComponents.MathFunc.r_[accAtom.x,accAtom.y,accAtom.z]
        # There is no AAAtom for water molecules
        if (AAAtom == None and accAtom.res_type in ("HOH")):
            AAv=None
        else:
            AAv=MolecularComponents.MathFunc.r_[AAAtom.x,AAAtom.y,AAAtom.z]
        HBondInfo={}
        HBondInfo['dist_D_A']= MolecularComponents.MathFunc.distance (Dv,Av)
        HBondInfo['dist_H_A'] = MolecularComponents.MathFunc.distance (Hv,Av)
        HBondInfo['angle_D_H_A'] = MolecularComponents.MathFunc.angle (Dv,Hv,Av)
        if (AAv != None):
            # print Dv[0],Dv[1],Dv[2],Av[0],Av[1],Av[2]
            HBondInfo['angle_D_A_AA'] = MolecularComponents.MathFunc.angle (Dv,Av,AAv)
            HBondInfo['angle_H_A_AA'] = MolecularComponents.MathFunc.angle (Hv,Av,AAv)
        else:
            HBondInfo['angle_D_A_AA'] = 'Water'
            HBondInfo['angle_H_A_AA'] = 'Water'

            
        return HBondInfo

    def is_valid_hbond (self,HBondInfo,strict=True):
        """
            If strict == False then the angle criteria is ignored
        """
        self.maxDist_D_A = 3.9
        self.maxDist_H_A = 2.6        #orig 2.5
        self.minDist_D_A = 2.9
        self.minDist_H_A = 1.3        #orig 1.4
        self.minAngle_D_H_A = 100.0   #orig 90
        self.minAngle_D_A_AA = 100.0  #orig 90
        self.minAngle_H_A_AA = 100.0  #orig 90
        
        if (HBondInfo['dist_D_A'] > self.maxDist_D_A or HBondInfo['dist_D_A'] < self.minDist_D_A):
            return False
        if (HBondInfo['dist_H_A'] > self.maxDist_H_A or HBondInfo['dist_H_A'] < self.minDist_H_A):
            return False
        
        if (HBondInfo['angle_D_H_A'] < self.minAngle_D_H_A and strict == True):
            return False 
        if (HBondInfo['angle_D_A_AA'] < self.minAngle_D_A_AA and strict == True):
            return False
        if (HBondInfo['angle_H_A_AA'] < self.minAngle_H_A_AA and strict == True):
            return False
        return True

    def print_hbonds (self,output=None):
        f = sys.stdout
        if (output != None):
            f = open (output,"w")
      
        f.write("%6s|%8s|%8s|%10s|%8s|%8s|%11s|%12s|%12s\n"\
                %('Acc AA','Acc Atom','Donor AA','Donor Atom','Dist D-A',
                  'Dist H-A','Angle D-H-A','Angle D-A-AA','Angle H-A-AA'))
        for HBond in self.HBonds:
            accAtom=HBond['accAtom']
            donorAtom=HBond['donorAtom']
            HBondInfo=HBond['HBondInfo']
            f.write("%6s|%8s|%8s|%10s|%8.2f|%8.2f|%11.2f"\
                    %(accAtom.res_type,accAtom.atom_type,donorAtom.res_type,donorAtom.atom_type,
                      HBondInfo['dist_D_A'],HBondInfo['dist_H_A'],HBondInfo['angle_D_H_A']))
            if (HBondInfo['angle_D_A_AA'] == 'Water'):
                f.write("|%12s|%12s\n"\
                        %(HBondInfo['angle_D_A_AA'],HBondInfo['angle_H_A_AA']))
            else:
                f.write("|%12.2f|%12.2f\n"\
                        %(HBondInfo['angle_D_A_AA'],HBondInfo['angle_H_A_AA']))

        
    def select(self):
        """ select all of the objects in this molecular system """
        for pchain in self.ProteinList:
            pchain.select()
        for nchain in self.NucleotideChainList:
            nchain.select()
        for lig in self.LigandList:
            lig.select()
        for wat in self.WaterList:
            wat.select()
            
    def deselect(self):
        """ deselect all of the objects in this molecular system """
        for pchain in self.ProteinList:
            pchain.deselect()
        for nchain in self.NucleotideChainList:
            nchain.deselect()
        for lig in self.LigandList:
            lig.deselect()
        for wat in self.WaterList:
            wat.deselect()
               
    def save_pdb(self, filename="tmp.pdb"):
        """ write out the structure to the given file name, in pdb-style """
        if verbose:
            print "currently only printing the protein atom lines"
        pdb_file = open(filename, 'w')
        pdb_file.writelines(self.HeaderLines)
        for pchain in self.ProteinList:
            pdb_file.writelines(pchain.get_pdb_lines())
        for nchain in self.NucleotideChainList:
            pdb_file.writelines(nchain.get_pdb_lines())
        for lig in self.LigandList:
            pdb_file.writelines(lig.get_pdb_lines())
        for wat in self.WaterList:
            pdb_file.writelines(wat.get_pdb_lines())
        pdb_file.close()
                
    def save_system(self, filename="tmp.sps"):
        # discards any intersection tables (x_table) because they're vtk based 
        for mol in self.MoleculeList:
            try:
                mol.x_table
            except AttributeError:
                pass
            else:
                mol.x_table = None
        # space-saving feature; reducing gets rid of atom features that
        # can be rebuilt directly from the pdb lines. rebuild later for continued use. this saves 
        # maybe a fifth of the space, probably more for larger systems. more to be done
        for mol in self.MoleculeList:
            for atom in mol.atoms:
                atom.reduce_for_storage()
        
        save_dict = {}
        try:
            self.filename
        except AttributeError:
            self.filename = filename
        else:
            save_dict['filename'] = self.filename
        save_dict['selected'] = self.selected
        save_dict['ProteinList'] = self.ProteinList
        save_dict['NucleotideChainList'] = self.NucleotideChainList
        save_dict['LigandList'] = self.LigandList
        save_dict['WaterList'] = self.WaterList
        save_dict['HeaderLines'] = self.HeaderLines
        save_dict['header'] = self.header

        # save the file    
        if len(filename) == 0:
            return
        sys_file = open(filename, 'wb')
        pickle.dump(save_dict, sys_file, 2)
        sys_file.close()
        # rebuild
        for mol in self.MoleculeList:
            for atom in mol.atoms:
                atom.rebuild_from_storage()
                
    def load_system(self, filename):
        self.filename = filename
        print 'opening %s'%(os.path.split(filename)[1])
        new_file = open(filename, 'rb')
        save_dict = pickle.load(new_file)
        self.filename = save_dict['filename']
        self.selected = save_dict['selected']
        self.ProteinList = save_dict['ProteinList']
        self.NucleotideChainList = save_dict['NucleotideChainList']
        self.LigandList = save_dict['LigandList']
        self.WaterList = save_dict['WaterList']
        self.HeaderLines = save_dict['HeaderLines']
        self.header = save_dict['header']
        for molset in [self.ProteinList, self.NucleotideChainList, self.LigandList, self.WaterList]:
            for mol in molset:
                for atom in mol.atoms:
                    atom.rebuild_from_storage()
        self._supplementary_initialization()
        
    def get_filename_by_extension(self, ext=None, chain_name = 'None'):
        """ use the pdb's filename to produce a filename of type ext  It figures out whether
            to add a '.' chain_name is a unique identifier to tag on to the filename, i.e.
            molecule.key. if ext is None, just returns the directory.
        """
        af = self.filename
        index = af.rfind('.')
        slash = af.rfind(os.sep)
        if( index == -1 or index < slash ):
            index = len( af )
        if ext == None:
            i = af[0:index].rfind(os.sep)
            return af[0:i]
        
        if chain_name == 'None':
            if ext[0] == ".":
                df = af[0:index] + ext
            else:
                df = af[0:index] + "." + ext
        else:
            if ext[0] == ".":
                df = af[0:index] + chain_name + ext
            else:
                df = af[0:index] + chain_name + "." + ext
            
        return df

    def translate_filename_to_DOS_8_3_format(self, filename):
        """ Assumes working on Windows. clustalw doesn't seem to like opening files in normal
        format when a directory in the path has a space in it. Change the format to 8.3 format,
        where each filename has at most 8 chars in the filename (using ~1 format)."""
        # first make sure its windows
        if 'indows' not in sys.platform:
            return filename
        filename = os.path.abspath(filename)
        components = string.split(filename, '\\')
        out = ""
        for i in range(len(components)):
            stuff = string.split(components[i], ' ')
            components[i] = string.join(stuff, '')
        for i in range(len(components)-1):
            if len(components[i]) > 8:
                components[i] = components[i][:6] + '~1'
            out = out + components[i] + '\\'
        x = string.rfind(components[-1],'.')
        if x == -1 or x<8:
            new_string = components[-1]
        else:       # if there's a dot and the base is > 8 characters
            new_string = components[-1][:6] + '~1' + components[-1][x:]
        out = out + new_string
        return out


    def get_bounds(self):
        x = 0.0
        y = 0.0
        z = 0.0
        count = 0
        for items in [self.ProteinList, self.NucleotideChainList, self.LigandList]:
            for mol in items:
                for atom in mol.atoms:
                    x = x + atom.x
                    y = y + atom.y
                    z = z + atom.z
                    count = count + 1
                    
        center_x = x / float(count)
        center_y = y / float(count)
        center_z = z / float(count)
        
        min_x = max_x = center_x
        min_y = max_y = center_y
        min_z = max_z = center_z
        
        for items in [self.ProteinList, self.NucleotideChainList, self.LigandList]:
            for mol in items:
                for atom in mol.atoms:
                    if atom.x >= max_x:
                        max_x = atom.x
                    if atom.x < min_x:
                        min_x = atom.x
                    if atom.y >= max_y:
                        max_y = atom.y
                    if atom.y < min_y:
                        min_y = atom.y
                    if atom.z >= max_z:
                        max_z = atom.z
                    if atom.z < min_z:
                        min_z = atom.z
        return [min_x,max_x,min_y,max_y,min_z,max_z]
    
    def normalize_b_factors(self):
        max_b = 0.0
        min_b = 1000.0
        print 'normalizing b factors'
        if self.MoleculeList[0].atoms[0].b_factor != None:
            for mol in self.MoleculeList:
                for atom in mol.atoms:
                    if atom.b_factor < min_b:
                        min_b = atom.b_factor
                    if atom.b_factor > max_b:
                        max_b = atom.b_factor
            print 'b_factor range %s %s'%(min_b, max_b)
            if max_b != 0.0:
                for mol in self.MoleculeList:
                    for atom in mol.atoms:
                        if atom.b_factor < (0.5*max_b):
                            atom.features['b_factor'] = 0.0
                        else:
                            atom.features['b_factor'] =(atom.b_factor-(0.5*max_b)) / (max_b-(0.5*max_b))
    
    def log_b_factors(self):
        max_b = 0.0
        min_b = 1000.0
        print 'log of b factors'
        if self.MoleculeList[0].atoms[0].b_factor != None:
            for mol in self.MoleculeList:
                for atom in mol.atoms:
                    if atom.b_factor == 0.0:
                        atom.b_factor = 0.01
                    atom.features['b_factor'] = math.log(atom.b_factor)

    def calculate_system_asa(self, solvent_radius, point_count, forced_rewrite=1, verbose=1):
        """ based on a function in classProtein """
        filename = self.get_filename_by_extension('.bsa')
        create_new = 0
        if forced_rewrite:
            print 'forced rewrite'
            create_new = 1
        else:
            try:
                asa_file = open(filename)
                print 'opening %s'%(filename)
            except IOError:
                create_new = 1
                print 'creating new'
        if create_new:
            sphere_res = 15
            if self.x_table == None:
                self.build_futamura_intersection_table(solvent_radius)
            x_table = self.x_table
            for pchain in self.ProteinList:
                # create spheres for each atom
                for res in pchain.residues:
                    total_points = 0
                    total_side   = 0
                    intra_inaccessible = 0
                    side_intra         = 0
                    side_inter         = 0
                    for atom in res.atoms:
                        radius = solvent_radius + atom.radius
                        radius_sq = radius**2
                        intrachain_tally = 0
                        # figure out which ones to keep
                        for i in range(point_count):
                            # build the point
                            angle = random.random() * 2 * 3.141592654
                            z = (random.random() * 2 * radius) - radius
                            z_sq = z**2;
                            x_store = math.sqrt(radius_sq - z_sq) * math.cos(angle) + atom.x
                            y_store = math.sqrt(radius_sq - z_sq) * math.sin(angle) + atom.y
                            z_store = z + atom.z
                            externally_broken = 0
                            # see if the point is blocked by any other atoms
                            for second_atom in x_table['%s'%(atom.atom_number)]:
                                if math.sqrt(pow(x_store-second_atom[0],2) + pow(y_store-second_atom[1],2) + pow(z_store-second_atom[2],2)) <= second_atom[3]: # second_atom[3] is rad+solv_rad
                                    # if the point is within range of a second atom,
                                    # dont count it if its blocked by a covalent bond
                                    if atom.atom_type == 'C' and second_atom[6] == 'N' and second_atom[4]-atom.res_number==1:
                                        break
                                    elif atom.atom_type == 'N' and second_atom[6] == 'C' and atom.res_number-second_atom[4]==1:
                                        break
                                    elif second_atom[4] == res.res_number and second_atom[5] == res.chain_name:
                                        break
                                    else:
                                        # not a covalent with next or last or current residues
                                        externally_broken = 1
                            else:
                                # now considering only points not blocked by covalent bonds
                                if externally_broken:   # is blocked by something
                                    total_points += 1
                                    intra_inaccessible += 1
                                    if atom.atom_type not in ['N', 'C', 'O']:
                                        total_side += 1
                                        side_intra += 1
                                else:                   # not blocked by anything
                                    total_points += 1
                                    if atom.atom_type not in ['N', 'C', 'O']:
                                        total_side += 1
                    
                    total_points = total_points + 0.0
                    total_side   = total_side   + 0.0
                    res.features['system_asa'] = (total_points-intra_inaccessible) / (total_points)
                    res.features['system_sidechain_asa'] = (total_side-side_intra) / (total_side)
                    if verbose:
                        print 'res %s%s - %5.2f accessible, %5.2f sidechain'%(res.res_number, res.res_type, res.features['system_asa'], res.features['system_sidechain_asa'])
                
            asa_file = open(filename, 'w')
            for pchain in self.ProteinList:
                for rex in range(len(pchain.residues)):
                    asa_file.write("%s %5.3f %5.3f\n"%(pchain.residues[rex].res_number, pchain.residues[rex].features['system_asa'], pchain.residues[rex].features['system_sidechain_asa']))
            asa_file.close()
        else:           # else read the contacts_file to fill the contact_list
            for pchain in self.ProteinList:
                for rex in range(len(pchain.residues)):
                    buffer = asa_file.readline()
                    if len(buffer) == 0:
                        break
                    tokens = string.split(buffer)
                    pchain.residue_dict[string.atoi(tokens[0])].features['system_asa'] = string.atof(tokens[1])
                    pchain.residue_dict[string.atoi(tokens[0])].features['system_sidechain_asa'] = string.atof(tokens[2])
            asa_file.close()

    def calculate_differential_system_asa(self, solvent_radius, point_count, forced_rewrite=0):
        self.calculate_system_asa(solvent_radius, point_count, forced_rewrite)
        for pchain in self.ProteinList:
            pchain.assign_asa(solvent_radius, point_count, forced_rewrite)
        if self.x_table == None:
            self.build_futamura_intersection_table(solvent_radius)
        # for chain _ include _ as interface and exclude _ from background
        specs = {'Systems/1a2k/1a2k.pdb':{'A':[['D'], ['B']],
                                          'B':[['C','E'], ['A']]},
                 'Systems/1aa1/1aa1.pdb':{'S':[['L','B'], ['C']],
                                          'B':[['S','C'], ['L']]},
                 'Systems/1acm/1acm.pdb':{'A':[['B'],[]],
                                          'B':[['A'],['D']]},
                 'Systems/1agr/1agr.pdb':{'A':[['C'],['B']],
                                          'C':[['A'],[]]},
                 'Systems/1aip/1aip.pdb':{'A':[['C','D'],[]],
                                          'C':[['A','B'],['D']]},
                 'Systems/1cb7/1cb7.pdb':{'A':[['B'],[]],
                                          'B':[['A'],['D']]},
                 'Systems/1cd9/1cd9.pdb':{'A':[['B','D'],[]],
                                          'B':[['C','A'],[]],
                                          'C':[['B','D'],[]],
                                          'D':[['C','A'],[]]},
                 'Systems/1cqi/1cqi.pdb':{'A':[['B','E'],[]],
                                          'B':[['A'],['D','E']]},
                 'Systems/1dkg/1dkg.pdb':{'A':[['D'],['B']],
                                          'D':[['A'],[]]},
                 'Systems/1efu/1efu.pdb':{'A':[['B','D'],['C']],
                                          'B':[['A','C'],['D']]},
                 'Systems/1ewy/1ewy.pdb':{'A':[['C'],['B']],
                                          'B':[['C'],['A']],
                                          'C':[['A','B'],[]]},
                 'Systems/1fin/1fin.pdb':{'A':[['B'],['D']],
                                          'A':[['D'],['B']],
                                          'B':[['A'],['C']],
                                          'B':[['C'],['A']]},
                 'Systems/1gg2/1gg2.pdb':{'A':[['B'],[]],
                                          'B':[['A','G'],[]],
                                          'G':[['B'],[]]},
                 'Systems/1h1l/1h1l.pdb':{'A':[['B','D'],[]],
                                          'B':[['A','C'],['D']]},
                 'Systems/1hwg/1hwg.pdb':{'A':[['B','C'],[]],
                                          'B':[['A'],['C']],
                                          'C':[['A'],['B']]},
                 'Systems/1i7q/1i7q.pdb':{'A':[['B'],['C','D']],
                                          'B':[['A','C'],[]]},
                 'Systems/1ib1/1ib1.pdb':{'A':[['E','F'],['B']],
                                          'E':[['A','B'],['F']]},
                 'Systems/1nhe/1nhe.pdb':{},
                 
                 }
        
                                          

        for pchain in self.ProteinList:
            for res in pchain.residues:
                dif = res.features['asa'] - res.features['system_asa'] 
                res.features['differential_asa'] = dif

                if dif > 0.05:
                    res.features['binary_dif_asa'] = -1
                    closest_chain = None
                    closest_distance = 1000
                    for atom in res.atoms:
                        for intersection in self.x_table['%s'%(atom.atom_number)]:
                            if intersection[5] != atom.chain_name:
                                if intersection[7] < closest_distance:
                                    closest_distance = intersection[7]
                                    closest_chain = intersection[5]
                    res.data['chain_dif_asa'] = closest_chain
                else:
                    res.features['binary_dif_asa'] = 0
                    res.data['chain_dif_asa'] = 0
                
                dif = res.features['sidechain_asa'] - res.features['system_sidechain_asa'] 
                res.features['differential_sidechain_asa'] = dif
                
                if dif > 0.05:
                    res.features['binary_dif_sidechain_asa'] = -1
                    closest_chain = None
                    closest_distance = 1000
                    for atom in res.atoms:
                        for intersection in self.x_table['%s'%(atom.atom_number)]:
                            if intersection[5] != atom.chain_name:
                                if intersection[7] < closest_distance:
                                    closest_distance = intersection[7]
                                    closest_chain = intersection[5]
                    res.data['chain_dif_sidechain_asa'] = closest_chain
                else:
                    res.features['binary_dif_sidechain_asa'] = 0
                    res.data['chain_dif_sidechain_asa'] = 0
            print

        asa_style = 'asa'
        for pchain in self.ProteinList:
            total_sum = 0.0
            rui = 0.0
            for res in pchain.residues:
                if res.features['binary_dif_'+asa_style] == -1:  # include -- see calculate_differential_system_asa
                    if asa_style == 'sidechain_asa':
                        rui += res.features['differential_asa'] *  res.data['exposed_area']
                    elif asa_style == 'asa':
                        rui += res.features['differential_sidechain_asa'] *  res.data['exposed_sidechain_area']
                    #print '%s%s %s, '%(res.res_type1, res.res_number, res.features['normalized_0D_conservation'])
            print '\n%5.2f angstroms under interface %s'%(rui, pchain.chain_name)
        
    def calculate_interface_significance(self, asa_style):
        # assumes calculate_differential_system_asa has been called
        outfile = open('./interface_results.txt', 'a')
        for pchain in self.ProteinList:
            line = '\ntesting chain %s pdb %s'%(pchain.chain_name, self.filename)
            print line
            outfile.write(line+'\n')
            total_sum = 0.0
            rui = 0.0
            conservation_present = 0
            for res in pchain.residues:
                if res.features['binary_dif_'+asa_style] == -1:  # include -- see calculate_differential_system_asa
                    if asa_style == 'sidechain_asa':
                        rui += res.features['differential_asa'] *  res.data['exposed_area']
                    elif asa_style == 'asa':
                        rui += res.features['differential_sidechain_asa'] *  res.data['exposed_sidechain_area']
                    try:
                        res.features['normalized_0D_conservation']
                    except KeyError:
                        line = '%s%s, '%(res.res_type1, res.res_number)
                    else:
                        line = '%s%s %s, '%(res.res_type1, res.res_number, res.features['normalized_0D_conservation'])
                        conservation_present=1
                    print line
                    outfile.write(line+'\n')

            line = '%5.2f angstroms under interface %s'%(rui, pchain.chain_name)
            print line
            outfile.write(line+'\n')
            
            if not conservation_present:
                print 'conservation analysis requires the conservation module'
                outfile.close()
                return

            tokens = ['normalized_0D_conservation', 'normalized_noactsit_0D_conservation', 'normalized_1D_conservation', 'normalized_3D_conservation', 'normalized_ms3D_conservation', 'normalized_noactsit_ms3D_conservation', 'normalized_nobadloop_ms3D_conservation']
            for token in tokens:
                # calculate the average score over the interface
                wins = 0
                times = 10000
                sum, count = 0.0, 0.0
                residues = []                   # speedup prefilter -- collect solvent exposed residues
                for res in pchain.residues:
                    if res.features[asa_style] >= 0.05 and res.features[token] != -1:
                        residues.append(res)
                        if res.features['binary_dif_'+asa_style] == -1:  # include -- see calculate_differential_system_asa
                            sum += res.features[token]
                            count += 1.0
                        
                if count > 0:
                    average = sum / count
                else:
                    print 'no residues in the interface'
                    continue

                monitor = []
                for res in residues:
                    monitor.append(0)
                    
                for i in range(times):
                    sum = 0.0
                    count2 = 0
                    for i in range(len(residues)):
                        monitor[i] = 0
                    while count2 < count:
                        r = random.randint(0,len(residues)-1)
                        if monitor[r]:
                            continue
                        monitor[r] = 1
                        sum += residues[r].features[token]
                        count2 += 1
                    if average >= sum/count2:
                        wins += 1
                line = 'chain %s %s (%s residues - %s) wins %4.1f percent of the time'%(pchain.chain_name, token, int(count), average, 100.0*wins/float(times))
                print line
                outfile.write(line+'\n')
                total_sum += 100.0*wins/float(times)
            print 'chain %s interface averages %s over the methods'%(pchain.chain_name, total_sum/5.0)
        outfile.close()
        
    def build_futamura_intersection_table(self, solvent_radius, include_ligands=0, include_waters=0):        
        outside_barrier = 4.0
        grid_spacing = 4*solvent_radius
        # make a fake molecule that holds all atoms from the system
        class FakeMolecule:
            def __init__(self, atoms):
                self.atoms = atoms
                self.atom_dict = {}
                centroid = [0.0,0.0,0.0]
                for atom in atoms:
                    self.atom_dict[atom.atom_number] = atom
                    centroid[0] += atom.x
                    centroid[1] += atom.y
                    centroid[2] += atom.z
                centroid[0] /= float(len(atoms))
                centroid[1] /= float(len(atoms))
                centroid[2] /= float(len(atoms))
                self.centroid = Point(centroid[0], centroid[1], centroid[2])
        atomlist = []
        for pchain in self.ProteinList:
            for atom in pchain.atoms:
                atomlist.append(atom)

        if include_ligands:
            for ligand in self.LigandList:
                for atom in ligand.atoms:
                    atomlist.append(atom)

        if include_waters:
            for water in self.WaterList:
                for atom in water.atoms:
                    atomlist.append(atom)
                
        fakemol = FakeMolecule(atomlist)
        grid = FutamuraHash(fakemol, outside_barrier, grid_spacing)
        T = grid.T
        block_assignments = grid.atom_block_assignments
        print 'locating intersections'
        # now locate the intersections
        x_table = {}
        for atom in fakemol.atoms:
            x_table['%s'%(atom.atom_number)] = []
            r1 = solvent_radius + atom.radius
            block = block_assignments['%s'%(atom.atom_number)]
            key_tokens = string.split(block)
            keys = [string.atoi(key_tokens[0]), string.atoi(key_tokens[1]), string.atoi(key_tokens[2])]
            # put 'this' block first, so that intersection table accesses search here first
            for second_atom in T[block]:
                if atom != second_atom:
                    r2 = solvent_radius + second_atom.radius
                    if atom.dist(second_atom) <= r1+r2:
                        x_table['%s'%(atom.atom_number)].append([second_atom.x,second_atom.y,second_atom.z, r2, second_atom.res_number, second_atom.chain_name, second_atom.atom_type, atom.dist(second_atom), second_atom.atom_number])
            
            start_array = [0,0,0]
            end_array   = [0,0,0]
            # figure out starts and ends
            counts = [grid.volume_count_x, grid.volume_count_y, grid.volume_count_z]
            for ind in [0,1,2]:
                if keys[ind] == 0:
                    start_array[ind] = 0
                    end_array[ind]   = 2
                elif keys[ind] == counts[ind] - 1:
                    start_array[ind] = keys[ind]-1
                    end_array[ind]   = keys[ind]+1
                else:
                    start_array[ind] = keys[ind]-1
                    end_array[ind]   = keys[ind]+2

            for i in range(start_array[0], end_array[0]):
                for j in range(start_array[1], end_array[1]):
                    for k in range(start_array[2], end_array[2]):
                        key2 = '%s %s %s'%(i,j,k)
                        if key2 == block:
                            continue            # did this one earlier
                        if key2 in T.keys():
                            for second_atom in T[key2]:
                                if atom != second_atom:
                                    r2 = solvent_radius + second_atom.radius
                                    if atom.dist(second_atom) <= r1+r2:
                                        x_table['%s'%(atom.atom_number)].append([second_atom.x,second_atom.y,second_atom.z, r2, second_atom.res_number, second_atom.chain_name, second_atom.atom_type, atom.dist(second_atom), second_atom.atom_number])
        self.x_table = x_table

    def remove_noninterfacial_waters(self, max_distance=3.0):
        if self.x_table == None:
            self.build_futamura_intersection_table(max_distance, 1, 1)
        prot_atom_nums = []
        for pchain in self.ProteinList:
            prot_atom_nums.append([])
            for res in pchain.residues:
                for atom in res.atoms:
                    prot_atom_nums[-1].append('%s'%(atom.atom_number))

        lig_atom_nums = []
        for ligand in self.LigandList:
            if ligand not in self.WaterList:
                lig_atom_nums.append([])
                for atom in ligand.atoms:
                    lig_atom_nums[-1].append('%s'%(atom.atom_number))

        mol_count = len(self.ProteinList) + len(self.LigandList)
        seen_in   = []
        for i in range(mol_count):
            seen_in.append(0)

        print '%s waters before'%(len(self.WaterList))
        keep_list = []
        for water in self.WaterList:
            keep_list.append(1)
        for i in range(len(self.WaterList)):
            for j in range(mol_count):
                seen_in[j] = 0
            water = self.WaterList[i]
            for atom in water.atoms:
                for second_atom in self.x_table['%s'%(atom.atom_number)]:
                    molnum = 0
                    for list in prot_atom_nums:
                        if '%s'%(second_atom[8]) in list:
                            dist = math.sqrt(pow(atom.x-second_atom[0],2) + pow(atom.y-second_atom[1],2) + pow(atom.z-second_atom[2],2))
                            if dist <= max_distance:
                                seen_in[molnum] = 1
                        molnum += 1
                    for list in lig_atom_nums:
                        if '%s'%(second_atom[8]) in list:
                            dist = math.sqrt(pow(atom.x-second_atom[0],2) + pow(atom.y-second_atom[1],2) + pow(atom.z-second_atom[2],2))
                            if dist <= max_distance:
                                seen_in[molnum] = 1
                        molnum += 1
            presence_count = 0
            for j in range(mol_count):
                if seen_in[j]:
                    presence_count += 1
            if presence_count < 2:
                keep_list[i] = 0

        keep_waters = []
        for i in range(len(self.WaterList)):
            if keep_list[i]:
                keep_waters.append(self.WaterList[i])

        self.WaterList = copy.deepcopy(keep_waters)
        print '%s waters after'%(len(self.WaterList))
        self._supplementary_initialization()
        self.x_table = None

    """
    def remove_redundant_chains(self, min_pid=.99, min_length=50):
        if len(self.ProteinList) < 2:
            return
        aligner = SequenceAligner.SequenceAligner(0, 'local', [2, 0.5])
        keep_list = []
        for p in self.ProteinList:
            keep_list.append(1)
        for i in range(len(self.ProteinList)-1):
            aligner.clear_template()
            aligner.add_template(self.ProteinList[i])
            for j in range(i+1, len(self.ProteinList)):
                aligner.clear_target()
                aligner.add_target(self.ProteinList[j])
                pid, length = aligner.get_pid_and_length()
                if pid > min_pid and length > min_length:
                    keep_list[j] = 0

        new_protein_list = []
        for i in range(len(keep_list)):
            if keep_list[i]:
                new_protein_list.append(self.ProteinList[i])

        self.ProteinList = copy.deepcopy(new_protein_list)
        self._supplementary_initialization()
        self.x_table = None
    """



""" SystemMemory quickly traverses a MolecularSystem object and records System data into a tree that
    is the same shape as the MolecularSystem object itself. restore_system() can then be used to traverse
    and restore the data. System memory objects inherity from base class SystemMemory. To specify the
    data to collect, implement the _get_data() and _set_data() functions, as demonstrated in several
    class objects below.
"""

class SystemMemory:
    def __init__(self, system):
        # constructs self.data by calling _get_data on every component including the system
        self.system = system
        self.data = {'system':{}, 'prots':{}, 'nuccs':{}, 'ligs':{}, 'wats':{}}
        self.data['system'] = {'hbonds':{}}
        self.data['system'] = copy.deepcopy(self._get_data(system))
        for pchain in system.ProteinList:
            self.data['prots'][pchain.key] = {'atoms':{},'residues':{},'molecule':'None'}
            for atom in pchain.atoms:
                self.data['prots'][pchain.key]['atoms'][atom.atom_number] = copy.deepcopy(self._get_data(atom))
            for res in pchain.residues:
                self.data['prots'][pchain.key]['residues'][res.res_number] = copy.deepcopy(self._get_data(res))
            self.data['prots'][pchain.key]['molecule'] = copy.deepcopy(self._get_data(pchain))
        for nchain in system.NucleotideChainList:
            self.data['nuccs'][nchain.key] = {'atoms':{},'residues':{},'molecule':'None'}
            for atom in nchain.atoms:
                self.data['nuccs'][nchain.key]['atoms'][atom.atom_number] = copy.deepcopy(self._get_data(atom))
            for res in nchain.residues:
                self.data['nuccs'][nchain.key]['residues'][res.res_number] = copy.deepcopy(self._get_data(res))
            self.data['nuccs'][nchain.key]['molecule'] = copy.deepcopy(self._get_data(nchain))
        for lig in system.LigandList:
            self.data['ligs'][lig.key] = {'atoms':{},'molecule':'None'}
            for atom in lig.atoms:
                self.data['ligs'][lig.key]['atoms'][atom.atom_number] = copy.deepcopy(self._get_data(atom))
            self.data['ligs'][lig.key]['molecule'] = copy.deepcopy(self._get_data(lig))
        for wat in system.WaterList:
            self.data['wats'][wat.key] = {'atoms':{},'molecule':'None'}
            for atom in wat.atoms:
                self.data['wats'][wat.key]['atoms'][atom.atom_number] = copy.deepcopy(self._get_data(atom))
            self.data['wats'][wat.key]['molecule'] = copy.deepcopy(self._get_data(wat))
    def restore_system(self):
        self._set_data(self.system, copy.deepcopy(self.data['system']))
        for pchain in self.system.ProteinList:
            for atom in pchain.atoms:
                self._set_data(atom, copy.deepcopy(self.data['prots'][pchain.key]['atoms'][atom.atom_number]))
            for res in pchain.residues:
                self._set_data(res, copy.deepcopy(self.data['prots'][pchain.key]['residues'][res.res_number]))
            self._set_data(pchain, copy.deepcopy(self.data['prots'][pchain.key]['molecule']))
        for nchain in self.system.NucleotideChainList:
            for atom in nchain.atoms:
                self._set_data(atom, copy.deepcopy(self.data['nuccs'][nchain.key]['atoms'][atom.atom_number]))
            for res in nchain.residues:
                self._set_data(res, copy.deepcopy(self.data['nuccs'][nchain.key]['residues'][res.res_number]))
            self._set_data(nchain, copy.deepcopy(self.data['nuccs'][nchain.key]['molecule']))
        for lig in self.system.LigandList:
            for atom in lig.atoms:
                self._set_data(atom, copy.deepcopy(self.data['ligs'][lig.key]['atoms'][atom.atom_number]))
            self._set_data(lig, copy.deepcopy(self.data['ligs'][lig.key]['molecule']))
        for wat in self.system.WaterList:
            for atom in wat.atoms:
                self._set_data(atom, copy.deepcopy(self.data['wats'][wat.key]['atoms'][atom.atom_number]))
            self._set_data(wat, copy.deepcopy(self.data['wats'][wat.key]['molecule']))
    def _get_data(self, item):
        pass
    def _set_data(self, item, data):
        pass
        

class SelectionMemory(SystemMemory):
    def __init__(self, system):
        SystemMemory.__init__(self, system)
    def _get_data(self, item):
        return item.selected
    def _set_data(self, item, data):
        item.selected = data
    def is_molecule_selection_current(self, mol):
        key_dict = {'System':'system',
                    'MolecularComponents.classProtein':'prots',
                    'MolecularComponents.classNucleotideChain':'nuccs',
                    'MolecularComponents.classLigand':'ligs',
                    'MolecularComponents.classWater':'wats'}
        for atom in mol.atoms:
            if atom.selected != self.data[key_dict[mol.__module__]][mol.key]['atoms'][atom.atom_number]:
                return 0
        else:
            return 1

class ObjectSelectionVisitor(SystemMemory):
    def __init__(self, system):
        SystemMemory.__init__(self, system)
        self.restore_system()
    def _get_data(self, item):
        return 1
    def _set_data(self, item, data):
        item.selected = data

class AtomSelectionVisitor(SystemMemory):
    def __init__(self, system):
        SystemMemory.__init__(self, system)
        self.restore_system()
    def _get_data(self, item):
        if item.__module__ == 'MolecularComponents.classAtom':
            item.selected = 1
        else:
            item.selected = 0
    def _set_data(self, item, data):
        item.selected = data
    
class QuickRenderVisitor(SystemMemory):
    def __init__(self, system):
        SystemMemory.__init__(self, system)
        self.restore_system()
    def _get_data(self, item):
        return 1
    def _set_data(self, item, data):
        if item.__module__ == 'System':
            item.vtk_arg_list['hbonds']['selected'] = 1
            item.vtk_arg_list['hbonds']['representation'] = 'line'
        if item.__module__ in ['MolecularComponents.classProtein', 'MolecularComponents.classNucleotideChain']:
            item.vtk_arg_list['trace']['selected'] = 1
            item.vtk_arg_list['trace']['representation'] = 'line'
            item.vtk_arg_list['volume']['selected'] = 0
            item.vtk_arg_list['atoms']['selected'] = 0
        if item.__module__ == "MolecularComponents.classLigand":
            item.vtk_arg_list['volume']['selected'] = 0
            item.vtk_arg_list['atoms']['selected'] = 1
            item.vtk_arg_list['atoms']['representation'] = 'wireframe'
        if item.__module__ == "MolecularComponents.ClassWater":
            item.vtk_arg_list['volume']['selected'] = 0
            item.vtk_arg_list['atoms']['selected'] = 0
        if item.__module__ == "MolecularComponents.classAtom":
            if item.parent.__module__ in ['MolecularComponents.classAminoAcid', 'MolecularComponents.classNucleotide']:
                item.vtk_arg_list['atoms']['color'] = item.parent.parent.default_chain_color
                item.vtk_arg_list['atoms']['opacity'] = 1.0
            else:
                item.vtk_arg_list['atoms']['color'] = [0.8,0.8,0.8]
                item.vtk_arg_list['atoms']['opacity'] = 1.0
        if item.__module__ in ["MolecularComponents.classAminoAcid", "MolecularComponents.classNucleotide"]:
            item.vtk_arg_list['trace']['color'] = item.parent.default_chain_color

class GraphicsMemory(SystemMemory):
    def __init__(self, system):
        SystemMemory.__init__(self, system)
        self.key_dict = {'System':'system',
                         'MolecularComponents.classProtein':'prots',
                         'MolecularComponents.classNucleotideChain':'nuccs',
                         'MolecularComponents.classLigand':'ligs',
                         'MolecularComponents.classWater':'wats'}
    def _get_data(self, item):
        return item.vtk_arg_list
    def _set_data(self, item, data):
        item.vtk_arg_list = data
    def get_volume_args(self, mol):
        # specialized for Molecule surfaces
        return self.data[self.key_dict[mol.__module__]][mol.key]['molecule']
    def get_representation(self, obj, type):
        if type == 'atoms':
            self.get_atoms_representation(obj)
        elif type == 'trace':
            self.get_trace_representation(obj)
        elif type == 'volumes':
            self.get_volumes_representation(obj)
        elif type == 'hbonds':
            self.get_hbonds_representation(obj)
    def get_hbonds_representation(self, obj):
        return self.data[self.key_dict[obj.__module__]]['hbonds']['representation']
    def get_atoms_representation(self, obj):
        return self.data[self.key_dict[obj.__module__]][obj.key]['molecule']['atoms']['representation']
    def get_trace_representation(self, obj):
        return self.data[self.key_dict[obj.__module__]][obj.key]['molecule']['trace']['representation']
    def get_volumes_representation(self, obj):
        return self.data[self.key_dict[obj.__module__]][obj.key]['molecule']['volumes']['representation']

