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
 * @file WordPredictor.cc
 *
 * @brief Definitions file for WordPredictor.h
 */

//--------------- Include files --------------------------------------

#include "incr_models/WordPredictor.h"

//--------------- WordPredictor class functions
//

//---------------------------------------
WordPredictor::WordPredictor()
{
  numSentsToRetain = 1;
}

//---------------------------------------
bool WordPredictor::load(const char* fileName, int verbose /*=0*/)
{
  // Load file with sentences
  int ret = loadFileWithSents(fileName, verbose);
  if (ret == THOT_ERROR)
    return THOT_ERROR;

  std::string fileAddInfoName = fileName;
  fileAddInfoName = fileAddInfoName + ".addinfo";
  ret = loadFileWithAdditionalInfo(fileAddInfoName.c_str(), verbose);
  if (ret == THOT_ERROR)
    return THOT_ERROR;

  return THOT_OK;
}

//---------------------------------------
bool WordPredictor::loadFileWithSents(const char* fileName, int verbose)
{
  AwkInputStream fileStream;

  // Open files
  if (fileStream.open(fileName) == THOT_ERROR)
  {
    if (verbose)
      std::cerr << "WordPredictor: Error while loading file with sentences " << fileName << std::endl;
    return THOT_ERROR;
  }
  else
  {
    if (verbose)
      std::cerr << "WordPredictor: loading file with sentences " << fileName << std::endl;

    while (fileStream.getln())
    {
      std::vector<std::string> strVec;

      for (unsigned int i = 1; i <= fileStream.NF; ++i)
      {
        strVec.push_back(fileStream.dollar(i));
      }
      addSentence(strVec);
      strVec.clear();
    }
    fileStream.close();
    return THOT_OK;
  }
}

//---------------------------------------
bool WordPredictor::loadFileWithAdditionalInfo(const char* fileName, int verbose)
{
  AwkInputStream fileStream;

  // Open files
  if (fileStream.open(fileName) == THOT_ERROR)
  {
    //    std::cerr<<"WordPredictor: file with additional info "<<fileName<<" not found. No additional info was
    //    loaded"<<std::endl;
    return THOT_OK;
  }
  else
  {
    if (verbose)
      std::cerr << "WordPredictor: loading file with additional info " << fileName << " ... ";

    if (fileStream.getln())
    {
      if (fileStream.NF == 1)
      {
        numSentsToRetain = atoi(fileStream.dollar(1).c_str());
        if (verbose)
          std::cerr << "numSentsToRetain= " << numSentsToRetain << std::endl;
        fileStream.close();
        return THOT_OK;
      }
      else
      {
        if (verbose)
          std::cerr << "anomalous file with additional info" << std::endl;
        return THOT_ERROR;
      }
    }
    else
    {
      if (verbose)
        std::cerr << "unexpected end of file with additional info" << std::endl;
      return THOT_ERROR;
    }
  }
}

//---------------------------------------
void WordPredictor::addSentence(std::vector<std::string> strVec)
{
  if (numSentsToRetain > 0)
  {
    strVecVec.push_back(strVec);
    if (strVecVec.size() == numSentsToRetain)
    {
      for (unsigned int i = 0; i < strVecVec.size(); ++i)
        addSentenceAux(strVecVec[i]);
      strVecVec.clear();
    }
  }
}

//---------------------------------------
void WordPredictor::addSentenceAux(std::vector<std::string> strVec)
{
  std::vector<char> vecChar;
  std::string chain;
  Count* cPtr;

  for (unsigned int i = 0; i < strVec.size(); ++i)
  {
    chain = strVec[i];
    vecChar.clear();
    for (unsigned int j = 0; j < chain.size(); ++j)
    {
      vecChar.push_back(chain[j]);
    }
    cPtr = charTrie.find(vecChar);
    if (cPtr == NULL)
    {
      charTrie.insert(vecChar, 1);
    }
    else
    {
      *cPtr = *cPtr + (Count)1;
    }
  }
}

//---------------------------------------
void WordPredictor::getSuffixList(std::string input, SuffixList& out)
{
  Trie<char, Count>* triePtr;
  std::vector<char> charVec;

  out.clear();
  for (unsigned int i = 0; i < input.size(); ++i)
    charVec.push_back(input[i]);
  triePtr = charTrie.getState(charVec);
  if (triePtr != NULL)
  {
    Trie<char, Count>::const_iterator trieIter;
    std::string suff;
    unsigned int i;

    for (trieIter = triePtr->begin(); trieIter != triePtr->end(); ++trieIter)
    {
      suff = "";
      if ((double)trieIter->second > (double)0)
      {
        if (input.size() > 0 && trieIter->first[0] != input[input.size() - 1])
          break;
        // This checking is done to detect whether the iterator
        // finish the iteration over the words that starts with the
        // prefix input

        for (i = 1; i < trieIter->first.size(); ++i)
        {
          suff.push_back(trieIter->first[i]);
        }
        out[trieIter->second] = suff;
      }
    }
  }
}

//---------------------------------------
std::pair<Count, std::string> WordPredictor::getBestSuffix(std::string input)
{
  std::pair<Count, std::string> pcs;
  SuffixList suffixList;
  SuffixList::iterator suffListIter;

  pcs.first = 0;
  pcs.second = "";

  getSuffixList(input, suffixList);

  suffListIter = suffixList.begin();
  if (suffListIter != suffixList.end())
    pcs = *suffListIter;

  return pcs;
}

//---------------------------------------
void WordPredictor::clear(void)
{
  charTrie.clear();
  numSentsToRetain = 1;
  strVecVec.clear();
}

//---------------------------------------
WordPredictor::~WordPredictor()
{
}
