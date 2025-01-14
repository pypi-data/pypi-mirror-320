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
 * @file SrcPhraseLenFeat.h
 *
 * @brief Declares the SrcPhraseLenFeat template class. This class
 * implements a source phrase length feature.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "phrase_models/BasePhraseModel.h"
#include "stack_dec/BasePbTransModelFeature.h"
#include "stack_dec/PhrScoreInfo.h"

//--------------- Constants ------------------------------------------

//--------------- Classes --------------------------------------------

//--------------- SrcPhraseLenFeat class

/**
 * @brief The SrcPhraseLenFeat template class is a base class for
 * implementing a word penalty feature.
 */

template <class SCORE_INFO>
class SrcPhraseLenFeat : public BasePbTransModelFeature<SCORE_INFO>
{
public:
  typedef typename BasePbTransModelFeature<SCORE_INFO>::HypScoreInfo HypScoreInfo;

  // Constructor
  SrcPhraseLenFeat();

  // Feature information
  std::string getFeatType(void);

  // Scoring functions
  HypScoreInfo extensionScore(const std::vector<std::string>& srcSent, const HypScoreInfo& predHypScrInf,
                              const PhrHypDataStr& predHypDataStr, const PhrHypDataStr& newHypDataStr, float weight,
                              Score& unweightedScore);
  Score scorePhrasePairUnweighted(const std::vector<std::string>& srcPhrase, const std::vector<std::string>& trgPhrase);

  // Functions related to model pointers
  void link_pm(BasePhraseModel* _invPbModelPtr);

protected:
  BasePhraseModel* invPbModelPtr;

  Score srcPhraseLenScore(unsigned int k, const SourceSegmentation& srcSegm, unsigned int srcLen,
                          unsigned int lastTrgSegmLen);
};

//--------------- SrcPhraseLenFeat class functions
//

template <class SCORE_INFO>
SrcPhraseLenFeat<SCORE_INFO>::SrcPhraseLenFeat()
{
  invPbModelPtr = NULL;
}

//---------------------------------
template <class SCORE_INFO>
std::string SrcPhraseLenFeat<SCORE_INFO>::getFeatType(void)
{
  return "SrcPhraseLenFeat";
}

//---------------------------------
template <class SCORE_INFO>
Score SrcPhraseLenFeat<SCORE_INFO>::scorePhrasePairUnweighted(const std::vector<std::string>& /*srcPhrase*/,
                                                              const std::vector<std::string>& /*trgPhrase*/)
{
  return 0;
}

//---------------------------------
template <class SCORE_INFO>
void SrcPhraseLenFeat<SCORE_INFO>::link_pm(BasePhraseModel* _invPbModelPtr)
{
  invPbModelPtr = _invPbModelPtr;
}

//---------------------------------------
template <class SCORE_INFO>
Score SrcPhraseLenFeat<SCORE_INFO>::srcPhraseLenScore(unsigned int k, const SourceSegmentation& srcSegm,
                                                      unsigned int srcLen, unsigned int lastTrgSegmLen)
{
  return (double)invPbModelPtr->trgSegmLenLgProb(k, srcSegm, srcLen, lastTrgSegmLen);
}

