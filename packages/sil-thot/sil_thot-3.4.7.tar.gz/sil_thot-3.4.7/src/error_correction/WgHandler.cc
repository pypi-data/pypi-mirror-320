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
 * @file WgHandler.cc
 *
 * @brief Definitions file for WgHandler.h
 */

//--------------- Include files --------------------------------------

#include "error_correction/WgHandler.h"

//--------------- WgHandler class function definitions

//---------------------------------------
WgHandler::WgHandler(void)
{
}

//---------------------------------------
bool WgHandler::load(const char* filename, int verbose /*=0*/)
{
  AwkInputStream awk;

  if (awk.open(filename) == THOT_ERROR)
  {
    if (verbose)
      std::cerr << "Error while opening word graph handler file: " << filename << "\n";
    return THOT_ERROR;
  }
  else
  {
    if (verbose)
      std::cerr << "Reading word graph handler file: " << filename << "\n";

    // Clear word graph
    clear();
    // Read file entries
    while (awk.getln())
    {
      if (awk.NF >= 3)
      {
        std::vector<std::string> strVec;
        for (unsigned int i = 1; i < awk.NF - 1; ++i)
        {
          strVec.push_back(awk.dollar(i));
        }
        WgInfo wgi = awk.dollar(awk.NF);
        sentToWgInfoMap[strVec] = wgi;
      }
    }
    return THOT_OK;
  }
}

//---------------------------------------
std::string WgHandler::pathAssociatedToSentence(const std::vector<std::string>& strVec, bool& found) const
{
  found = false;
  SentToWgInfoMap::const_iterator citer;

  citer = sentToWgInfoMap.find(strVec);
  if (citer == sentToWgInfoMap.end())
  {
    std::string result;
    return result;
  }
  else
  {
    found = true;
    return citer->second;
  }
}

//---------------------------------------
bool WgHandler::empty(void) const
{
  return size() == 0;
}

//---------------------------------------
size_t WgHandler::size(void) const
{
  return sentToWgInfoMap.size();
}

//---------------------------------------
bool WgHandler::print(const char* filename) const
{
  std::ofstream outS;

  outS.open(filename, std::ios::trunc);
  if (!outS)
  {
    std::cerr << "Error while printing sentence to word graph path info." << std::endl;
    return THOT_ERROR;
  }
  else
  {
    print(outS);
    outS.close();
    return THOT_OK;
  }
}

//---------------------------------------
void WgHandler::print(std::ostream& outS) const
{
  for (SentToWgInfoMap::const_iterator citer = sentToWgInfoMap.begin(); citer != sentToWgInfoMap.end(); ++citer)
  {
    for (unsigned int i = 0; i < citer->first.size(); ++i)
    {
      outS << citer->first[i] << " ";
    }
    outS << "||| " << citer->second << std::endl;
  }
}

//---------------------------------------
void WgHandler::clear(void)
{
  sentToWgInfoMap.clear();
}

//---------------------------------------
WgHandler::~WgHandler()
{
}
