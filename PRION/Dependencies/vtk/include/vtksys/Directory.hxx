/*=========================================================================

  Program:   KWSys - Kitware System Library
  Module:    $RCSfile: Directory.hxx.in,v $

  Copyright (c) Kitware, Inc., Insight Consortium.  All rights reserved.
  See Copyright.txt or http://www.kitware.com/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notices for more information.

=========================================================================*/
#ifndef vtksys_Directory_hxx
#define vtksys_Directory_hxx

#include <vtksys/Configure.h>

namespace vtksys
{

class DirectoryInternals;

/** \class Directory
 * \brief Portable directory/filename traversal.
 * 
 * Directory provides a portable way of finding the names of the files
 * in a system directory.
 *
 * Directory currently works with Windows and Unix operating systems.
 */
class vtksys_EXPORT Directory 
{
public:
  Directory();
  ~Directory();
  
  /**
   * Load the specified directory and load the names of the files
   * in that directory. 0 is returned if the directory can not be 
   * opened, 1 if it is opened.   
   */
  bool Load(const char*);
  
  /**
   * Return the number of files in the current directory.
   */
  unsigned long GetNumberOfFiles();
  
  /**
   * Return the file at the given index, the indexing is 0 based
   */
  const char* GetFile(unsigned long);
  
private:
  // Private implementation details.
  DirectoryInternals* Internal;
}; // End Class: Directory

} // namespace vtksys

#endif
