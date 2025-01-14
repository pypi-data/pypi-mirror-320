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
 * @file FeaturesInfo.h
 *
 * @brief Class to store information about log-linear model features.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "stack_dec/BasePbTransModelFeature.h"
#include "stack_dec/DirectPhraseModelFeat.h"
#include "stack_dec/InversePhraseModelFeat.h"
#include "stack_dec/LangModelFeat.h"
#include "stack_dec/SrcPosJumpFeat.h"

#include <vector>

//--------------- FeaturesInfo struct

template <class SCORE_INFO>
struct FeaturesInfo
{
  std::vector<BasePbTransModelFeature<SCORE_INFO>*> featPtrVec;

  // Functions to get pointers to features
  std::vector<LangModelFeat<SCORE_INFO>*> getLangModelFeatPtrs(std::vector<unsigned int>& featIndexVec);
  std::vector<DirectPhraseModelFeat<SCORE_INFO>*> getDirectPhraseModelFeatPtrs(std::vector<unsigned int>& featIndexVec);
  std::vector<InversePhraseModelFeat<SCORE_INFO>*> getInversePhraseModelFeatPtrs(
      std::vector<unsigned int>& featIndexVec);
  std::vector<SrcPosJumpFeat<SCORE_INFO>*> getSrcPosJumpFeatPtrs(std::vector<unsigned int>& featIndexVec);
};

//---------------
template <class SCORE_INFO>
std::vector<LangModelFeat<SCORE_INFO>*> FeaturesInfo<SCORE_INFO>::getLangModelFeatPtrs(
    std::vector<unsigned int>& featIndexVec)
{
  featIndexVec.clear();
  std::vector<LangModelFeat<SCORE_INFO>*> lmFeatPtrVec;
  for (unsigned int i = 0; i < featPtrVec.size(); ++i)
  {
    LangModelFeat<SCORE_INFO>* lmFeatPtr = dynamic_cast<LangModelFeat<SCORE_INFO>*>(featPtrVec[i]);
    if (lmFeatPtr)
    {
      lmFeatPtrVec.push_back(lmFeatPtr);
      featIndexVec.push_back(i);
    }
  }
  return lmFeatPtrVec;
}

//---------------
template <class SCORE_INFO>
std::vector<DirectPhraseModelFeat<SCORE_INFO>*> FeaturesInfo<SCORE_INFO>::getDirectPhraseModelFeatPtrs(
    std::vector<unsigned int>& featIndexVec)
{
  featIndexVec.clear();
  std::vector<DirectPhraseModelFeat<SCORE_INFO>*> directPhraseModelFeatPtrVec;
  for (unsigned int i = 0; i < featPtrVec.size(); ++i)
  {
    DirectPhraseModelFeat<SCORE_INFO>* directPhraseModelFeatPtr =
        dynamic_cast<DirectPhraseModelFeat<SCORE_INFO>*>(featPtrVec[i]);
    if (directPhraseModelFeatPtr)
    {
      directPhraseModelFeatPtrVec.push_back(directPhraseModelFeatPtr);
      featIndexVec.push_back(i);
    }
  }
  return directPhraseModelFeatPtrVec;
}

//---------------
template <class SCORE_INFO>
std::vector<InversePhraseModelFeat<SCORE_INFO>*> FeaturesInfo<SCORE_INFO>::getInversePhraseModelFeatPtrs(
    std::vector<unsigned int>& featIndexVec)
{
  featIndexVec.clear();
  std::vector<InversePhraseModelFeat<SCORE_INFO>*> inversePhraseModelFeatPtrVec;
  for (unsigned int i = 0; i < featPtrVec.size(); ++i)
  {
    InversePhraseModelFeat<SCORE_INFO>* inversePhraseModelFeatPtr =
        dynamic_cast<InversePhraseModelFeat<SCORE_INFO>*>(featPtrVec[i]);
    if (inversePhraseModelFeatPtr)
    {
      inversePhraseModelFeatPtrVec.push_back(inversePhraseModelFeatPtr);
      featIndexVec.push_back(i);
    }
  }
  return inversePhraseModelFeatPtrVec;
}

//---------------
template <class SCORE_INFO>
std::vector<SrcPosJumpFeat<SCORE_INFO>*> FeaturesInfo<SCORE_INFO>::getSrcPosJumpFeatPtrs(
    std::vector<unsigned int>& featIndexVec)
{
  featIndexVec.clear();
  std::vector<SrcPosJumpFeat<SCORE_INFO>*> srcPosJumpFeatPtrVec;
  for (unsigned int i = 0; i < featPtrVec.size(); ++i)
  {
    SrcPosJumpFeat<SCORE_INFO>* srcPosJumpFeatPtr = dynamic_cast<SrcPosJumpFeat<SCORE_INFO>*>(featPtrVec[i]);
    if (srcPosJumpFeatPtr)
    {
      srcPosJumpFeatPtrVec.push_back(srcPosJumpFeatPtr);
      featIndexVec.push_back(i);
    }
  }
  return srcPosJumpFeatPtrVec;
}

