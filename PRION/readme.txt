SPADE readme

version 1.2.1

Downloads pdb files and applications. PIPPI works for lots more proteins. Removed equations.py and global_functions.py, moved SelectionMemory to MolecularSystem file. Miscellaneous UI adjustments.


version 1.1

This version has been updated to use Python 2.5, as distributed in the Enthought Python distribution, with their new numpy dependency (as opposed to the old Numeric library). There are a couple of new features in RAVE.py, including a ruler feature to the highlight selection, and a minimap of the max plot from all spectra embedded in the horizontal scrollbar.


Version 1.0

There are currently three main applications. To run them, first install Enthought's free Python version, which includes several necessary and awesome packages. Visit http://www.enthought.com/products/epd.php.

SPADE.py -- Structural Proteomics Application Development Environment

RAVE.py -- Reactivity Analysis and structure Validation Environment

MolecularViewer.py 


To run, simply double click the file. 

Note that you can open multiple molecular viewers at one time, unlike some structural proteomics packages...

SPADE currently hosts applications including a phylogenetic tree editor and a molecular dynamics playback and study tool. These files are located in the /Applications directory. A wide variety of tools have been written for reuse, and are available in the /Tools directory. Documentation is available from the /Documentation directory. Demonstration projects are not included in the initial release but will be released in parallel as I get a chance to organize them.

To run SPADE, first download a structure file from http://www.rcsb.org. Create a new folder with the protein's name in the /Systems directory and move a protein structure file (.pdb) into that new directory. Double click SPADE, then click on the protein's name as it appears in the middle of the control panel. Click the "O" button to visualize the protein in a molecular viewer. Then click one of the applications at the top of the control panel to launch that application on the protein. More thorough documentation will ensue as I finish my thesis, but for now, a presentation on SPADE is available in the /Documentation directory.

RAVE is currently a stand-alone program that offers a wide variety of tools to support emperical modeling through mass-spectrometry-based chemical probing experiments. It will eventually be integrated into SPADE as the code for each stabilizes. Documentation on RAVE is available from the /Documentation directory.

Documentation on the SPADE MolecularViewer is also available there.
