/*
thot package for statistical machine translation
Copyright (C) 2013 Daniel Ortiz-Mart\'inez

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program; If not, see <http://www.gnu.org/licenses/>.
*/

/**
 * @file anjm1ip_anjiMatrix.cc
 *
 * @brief Definitions file for anjm1ip_anjiMatrix.h
 */

//--------------- Include files --------------------------------------

#include "sw_models/anjm1ip_anjiMatrix.h"

#include "nlp_common/AwkInputStream.h"
#include "nlp_common/ErrorDefs.h"
#include "nlp_common/MathDefs.h"

#include <fstream>
#include <iostream>

//--------------- Global variables -----------------------------------

//--------------- Function declarations

//--------------- Classes --------------------------------------------

//--------------- anjm1ip_anjiMatrix class function definitions

//-------------------------
anjm1ip_anjiMatrix::anjm1ip_anjiMatrix(void)
{
  anjm1ip_anji_maxnsize = UNRESTRICTED_ANJM1IP_ANJI_SIZE;
  anjm1ip_anji_pointer = 0;
}

//-------------------------
bool anjm1ip_anjiMatrix::init_nth_entry(unsigned int n, PositionIndex nslen, PositionIndex tlen, unsigned int& mapped_n)
{
  if (anjm1ip_anji_maxnsize > 0)
  {
    // Obtain value of mapped_n
    map_n_in_matrix(n, mapped_n);

    // Check if it is required to grow in the dimension of n
    if (anjm1ip_anji.size() <= mapped_n)
    {
      anjm1ip_anji.resize(mapped_n + 1);
    }

    // Check if entry has enough room
    if (resizeIsRequired(mapped_n, nslen, tlen))
    {
      anjm1ip_anji[mapped_n].clear();

      // Initialize data structure for entry
      std::vector<float> floatVec(nslen + 1, INVALID_ANJM1IP_ANJI_VAL);
      std::vector<std::vector<float>> floatVecVec(nslen + 1, floatVec);
      anjm1ip_anji[mapped_n].resize(tlen + 1, floatVecVec);
    }

    return THOT_OK;
  }
  else
    return THOT_ERROR;
}

//-------------------------
bool anjm1ip_anjiMatrix::resizeIsRequired(unsigned int mapped_n, PositionIndex nslen, PositionIndex tlen)
{
  if (anjm1ip_anji.size() <= mapped_n)
    return true;

  if (anjm1ip_anji[mapped_n].size() <= tlen)
    return true;

  if (anjm1ip_anji[mapped_n][0].size() <= nslen)
    return true;

  if (anjm1ip_anji[mapped_n][0][0].size() <= nslen)
    return true;

  return false;
}

//-------------------------
bool anjm1ip_anjiMatrix::reset_entries(void)
{
  if (anjm1ip_anji_maxnsize > 0)
  {
    // Reset values
    for (unsigned int n = 0; n < anjm1ip_anji.size(); ++n)
    {
      for (unsigned int j = 0; j < anjm1ip_anji[n].size(); ++j)
      {
        for (unsigned int i = 0; i < anjm1ip_anji[n][j].size(); ++i)
        {
          std::fill(anjm1ip_anji[n][j][i].begin(), anjm1ip_anji[n][j][i].end(), (float)INVALID_ANJM1IP_ANJI_VAL);
        }
      }
    }

    return THOT_OK;
  }
  else
    return THOT_ERROR;
}

//-------------------------
void anjm1ip_anjiMatrix::set_maxnsize(unsigned int _anjm1ip_anji_maxnsize)
{
  clear();
  anjm1ip_anji_maxnsize = _anjm1ip_anji_maxnsize;
}

//-------------------------
unsigned int anjm1ip_anjiMatrix::get_maxnsize(void)
{
  return anjm1ip_anji_maxnsize;
}

//-------------------------
unsigned int anjm1ip_anjiMatrix::n_size(void)
{
  return anjm1ip_anji.size();
}

//-------------------------
unsigned int anjm1ip_anjiMatrix::nj_size(unsigned int n)
{
  return anjm1ip_anji[n].size();
}

//-------------------------
unsigned int anjm1ip_anjiMatrix::nji_size(unsigned int n, unsigned int j)
{
  return anjm1ip_anji[n][j].size();
}

//-------------------------
unsigned int anjm1ip_anjiMatrix::njiip_size(unsigned int n, unsigned int j, unsigned int i)
{
  return anjm1ip_anji[n][j][i].size();
}

//-------------------------
void anjm1ip_anjiMatrix::set(unsigned int n, unsigned int j, unsigned int i, unsigned int ip, float f)
{
  if (anjm1ip_anji_maxnsize > 0)
  {
    unsigned int np;
    map_n_in_matrix(n, np);

    // Grow in the dimension of np if necessary
    while (anjm1ip_anji.size() <= np)
    {
      std::vector<std::vector<std::vector<float>>> ajiip;
      anjm1ip_anji.push_back(ajiip);
    }

    // Grow in the dimension of j if necessary
    while (anjm1ip_anji[np].size() <= j)
    {
      std::vector<std::vector<float>> aiip;
      anjm1ip_anji[np].push_back(aiip);
    }

    // Grow in the dimension of i if necessary
    while (anjm1ip_anji[np][j].size() <= i)
    {
      std::vector<float> aip;
      anjm1ip_anji[np][j].push_back(aip);
    }

    // Grow in the dimension of ip if necessary
    while (anjm1ip_anji[np][j][i].size() <= ip)
    {
      anjm1ip_anji[np][j][i].push_back(INVALID_ANJM1IP_ANJI_VAL);
    }

    // Set value
    anjm1ip_anji[np][j][i][ip] = f;
  }
}

//-------------------------
void anjm1ip_anjiMatrix::set_fast(unsigned int mapped_n, unsigned int j, unsigned int i, unsigned int ip, float f)
{
  if (anjm1ip_anji_maxnsize > 0)
    anjm1ip_anji[mapped_n][j][i][ip] = f;
}

//-------------------------
float anjm1ip_anjiMatrix::get(unsigned int n, unsigned int j, unsigned int i, unsigned int ip)
{
  unsigned int np;
  if (!n_is_mapped_in_matrix(n, np))
    return INVALID_ANJM1IP_ANJI_VAL;

  // Check boundaries
  if (anjm1ip_anji.size() <= np)
    return INVALID_ANJM1IP_ANJI_VAL;
  if (anjm1ip_anji[np].size() <= j)
    return INVALID_ANJM1IP_ANJI_VAL;
  if (anjm1ip_anji[np][j].size() <= i)
    return INVALID_ANJM1IP_ANJI_VAL;
  if (anjm1ip_anji[np][j][i].size() <= ip)
    return INVALID_ANJM1IP_ANJI_VAL;
  // anjm1ip_anji[np][j][i][ip] is defined
  return anjm1ip_anji[np][j][i][ip];
}

//-------------------------
float anjm1ip_anjiMatrix::get_fast(unsigned int mapped_n, unsigned int j, unsigned int i, unsigned int ip)
{
  if (anjm1ip_anji_maxnsize > 0)
    return anjm1ip_anji[mapped_n][j][i][ip];
  else
    return INVALID_ANJM1IP_ANJI_VAL;
}

//-------------------------
float anjm1ip_anjiMatrix::get_invp(unsigned int n, unsigned int j, unsigned int i, unsigned int ip)
{
  float f = get(n, j, i, ip);
  if (f == INVALID_ANJM1IP_ANJI_VAL)
    return 0;
  else
    return f;
}

//-------------------------
float anjm1ip_anjiMatrix::get_invp_fast(unsigned int mapped_n, unsigned int j, unsigned int i, unsigned int ip)
{
  float f = get_fast(mapped_n, j, i, ip);
  if (f == INVALID_ANJM1IP_ANJI_VAL)
    return 0;
  else
    return f;
}

//-------------------------
float anjm1ip_anjiMatrix::get_invlogp(unsigned int n, unsigned int j, unsigned int i, unsigned int ip)
{
  float f = get(n, j, i, ip);
  if (f == INVALID_ANJM1IP_ANJI_VAL)
    return SMALL_LG_NUM;
  else
    return f;
}

//-------------------------
float anjm1ip_anjiMatrix::get_invlogp_fast(unsigned int mapped_n, unsigned int j, unsigned int i, unsigned int ip)
{
  float f = get_fast(mapped_n, j, i, ip);
  if (f == INVALID_ANJM1IP_ANJI_VAL)
    return SMALL_LG_NUM;
  else
    return f;
}

//-------------------------
bool anjm1ip_anjiMatrix::n_is_mapped_in_matrix(unsigned int n, unsigned int& np)
{
  if (anjm1ip_anji_maxnsize == UNRESTRICTED_ANJM1IP_ANJI_SIZE)
  {
    // Size of anji is not restricted
    if (n < anjm1ip_anji.size())
    {
      np = n;
      return true;
    }
    else
      return false;
  }
  else
  {
    // Size of anjm1ip_anji is restricted
    std::pair<bool, unsigned int> pbui = read_n_to_np_vector(n);
    np = pbui.second;
    return pbui.first;
  }
}

//-------------------------
void anjm1ip_anjiMatrix::map_n_in_matrix(unsigned int n, unsigned int& np)
{
  if (anjm1ip_anji_maxnsize == UNRESTRICTED_ANJM1IP_ANJI_SIZE)
  {
    // Size of anji is not restricted
    np = n;
  }
  else
  {
    // Size of anji is restricted
    if (!n_is_mapped_in_matrix(n, np))
    {
      // n is not mapped in anji

      // Assign index to n
      np = anjm1ip_anji_pointer;
      ++anjm1ip_anji_pointer;
      if (anjm1ip_anji_pointer >= anjm1ip_anji_maxnsize)
        anjm1ip_anji_pointer = 0;

      // Update info for old index
      std::pair<bool, unsigned int> pbui = read_np_to_n_vector(np);
      if (pbui.first)
      {
        // np'th entry of anji was in use

        // Update old n to np correspondence
        update_n_to_np_vector(pbui.second, std::make_pair(false, 0));
        // Clear anji entry for old index
        anjm1ip_anji[np].clear();
      }

      // Update np to n mapping
      update_np_to_n_vector(np, std::make_pair(true, n));

      // Update n to np mapping
      update_n_to_np_vector(n, std::make_pair(true, np));
    }
  }
}

//-------------------------
std::pair<bool, unsigned int> anjm1ip_anjiMatrix::read_np_to_n_vector(unsigned int np)
{
  if (np < np_to_n_vector.size())
  {
    return np_to_n_vector[np];
  }
  else
    return std::make_pair(false, 0);
}

//-------------------------
std::pair<bool, unsigned int> anjm1ip_anjiMatrix::read_n_to_np_vector(unsigned int n)
{
  if (n < n_to_np_vector.size())
  {
    return n_to_np_vector[n];
  }
  else
    return std::make_pair(false, 0);
}

//-------------------------
void anjm1ip_anjiMatrix::update_np_to_n_vector(unsigned int np, std::pair<bool, unsigned int> pbui)
{
  // grow np_to_n_vector
  while (np >= np_to_n_vector.size())
  {
    np_to_n_vector.push_back(std::make_pair(false, 0));
  }
  np_to_n_vector[np] = pbui;
}

//-------------------------
void anjm1ip_anjiMatrix::update_n_to_np_vector(unsigned int n, std::pair<bool, unsigned int> pbui)
{
  // grow n_to_np_vector
  while (n >= n_to_np_vector.size())
  {
    n_to_np_vector.push_back(std::make_pair(false, 0));
  }
  n_to_np_vector[n] = pbui;
}

//-------------------------
bool anjm1ip_anjiMatrix::load(const char* prefFileName, int verbose /*=0*/)
{
  // Clear data structures
  clear();

  // Load information from files
  bool retVal;
  std::string matrixFile = prefFileName;
  matrixFile = matrixFile + ".anjm1ip_anji";
  retVal = load_matrix_values(matrixFile.c_str(), verbose);
  if (retVal == THOT_ERROR)
    return THOT_ERROR;

  std::string maxnsizeDataFile = prefFileName;
  maxnsizeDataFile = maxnsizeDataFile + ".msinfo";
  retVal = load_maxnsize_data(maxnsizeDataFile.c_str(), verbose);
  if (retVal == THOT_ERROR)
  {
    if (verbose)
      std::cerr << "Maximum size for matrix is set to " << UNRESTRICTED_ANJM1IP_ANJI_SIZE << " (unrestricted size)."
                << std::endl;
    anjm1ip_anji_maxnsize = UNRESTRICTED_ANJM1IP_ANJI_SIZE;
  }
  return THOT_OK;
}

//-------------------------
bool anjm1ip_anjiMatrix::load_matrix_values(const char* matrixFile, int verbose)
{
  if (verbose)
    std::cerr << "Loading file with anjm1ip_anji values from " << matrixFile << std::endl;
  // Try to open file
  std::ifstream inF(matrixFile, std::ios::in | std::ios::binary);
  if (!inF)
  {
    if (verbose)
      std::cerr << "File with anjm1ip_anji values " << matrixFile << " does not exist.\n";
    return THOT_ERROR;
  }
  else
  {
    // Read register
    bool end = false;
    while (!end)
    {
      unsigned int n;
      unsigned int j;
      unsigned int i;
      unsigned int ip;
      float f;
      if (inF.read((char*)&n, sizeof(unsigned int)))
      {
        inF.read((char*)&j, sizeof(unsigned int));
        inF.read((char*)&i, sizeof(unsigned int));
        inF.read((char*)&ip, sizeof(unsigned int));
        inF.read((char*)&f, sizeof(float));
        set(n, j, i, ip, f);
      }
      else
        end = true;
    }
    return THOT_OK;
  }
}

//-------------------------
bool anjm1ip_anjiMatrix::load_maxnsize_data(const char* maxnsizeDataFile, int verbose)
{
  AwkInputStream awk;

  // Try to open file
  if (awk.open(maxnsizeDataFile) == THOT_ERROR)
  {
    if (verbose)
      std::cerr << "Error in file with anji maximum size data, file " << maxnsizeDataFile << " does not exist.\n";
    return THOT_ERROR;
  }
  else
  {
    // Read values
    if (verbose)
      std::cerr << "Reading matrix maximum size data from file: " << maxnsizeDataFile << std::endl;
    awk.getln();
    anjm1ip_anji_maxnsize = atoi(awk.dollar(1).c_str());
    awk.getln();
    anjm1ip_anji_pointer = atoi(awk.dollar(1).c_str());

    while (awk.getln())
    {
      if (awk.NF == 2)
      {
        unsigned int np = atoi(awk.dollar(1).c_str());
        unsigned int n = atoi(awk.dollar(2).c_str());

        update_np_to_n_vector(np, std::make_pair(true, n));
        update_n_to_np_vector(n, std::make_pair(true, np));
      }
    }
  }
  return THOT_OK;
}

//-------------------------
bool anjm1ip_anjiMatrix::print(const char* prefFileName)
{
  bool retVal;
  std::string matrixFile = prefFileName;
  matrixFile = matrixFile + ".anjm1ip_anji";
  retVal = print_matrix_values(matrixFile.c_str());
  if (retVal == THOT_ERROR)
    return THOT_ERROR;

  if (anjm1ip_anji_maxnsize != UNRESTRICTED_ANJM1IP_ANJI_SIZE)
  {
    std::string maxnsizeDataFile = prefFileName;
    maxnsizeDataFile = maxnsizeDataFile + ".msinfo";
    retVal = print_maxnsize_data(maxnsizeDataFile.c_str());
    if (retVal == THOT_ERROR)
      return THOT_ERROR;
  }

  return THOT_OK;
}

//-------------------------
bool anjm1ip_anjiMatrix::print_matrix_values(const char* matrixFile)
{
  std::ofstream outF;
  outF.open(matrixFile, std::ios::out);
  if (!outF)
  {
    std::cerr << "Error while printing anji file." << std::endl;
    return THOT_ERROR;
  }
  else
  {
    // print file with anji values
    for (unsigned int n = 0; n < anjm1ip_anji.size(); ++n)
    {
      for (unsigned int j = 0; j < anjm1ip_anji[n].size(); ++j)
      {
        for (unsigned int i = 0; i < anjm1ip_anji[n][j].size(); ++i)
        {
          for (unsigned int ip = 0; ip < anjm1ip_anji[n][j][i].size(); ++ip)
          {
            outF.write((char*)&n, sizeof(unsigned int));
            outF.write((char*)&j, sizeof(unsigned int));
            outF.write((char*)&i, sizeof(unsigned int));
            outF.write((char*)&ip, sizeof(unsigned int));
            outF.write((char*)&anjm1ip_anji[n][j][i][ip], sizeof(float));
          }
        }
      }
    }
    return THOT_OK;
  }
}

//-------------------------
bool anjm1ip_anjiMatrix::print_maxnsize_data(const char* maxnsizeDataFile)
{
  std::ofstream outF;
  outF.open(maxnsizeDataFile, std::ios::out);
  if (!outF)
  {
    std::cerr << "Error while printing file with anji maximum size data." << std::endl;
    return THOT_ERROR;
  }
  else
  {
    // Print maximum size for anji
    outF << anjm1ip_anji_maxnsize << std::endl;
    outF << anjm1ip_anji_pointer << std::endl;

    // Print np to n vector
    for (unsigned int np = 0; np < np_to_n_vector.size(); ++np)
    {
      if (np_to_n_vector[np].first)
        outF << np << " " << np_to_n_vector[np].second << std::endl;
    }
    return THOT_OK;
  }
}

//-------------------------
void anjm1ip_anjiMatrix::clear(void)
{
  anjm1ip_anji_pointer = 0;
  anjm1ip_anji.clear();
  np_to_n_vector.clear();
  n_to_np_vector.clear();
}
