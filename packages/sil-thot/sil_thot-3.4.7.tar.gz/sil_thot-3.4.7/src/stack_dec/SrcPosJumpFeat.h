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
 * @file SrcPosJumpFeat.h
 *
 * @brief Declares the SrcPosJumpFeat template class. This class
 * implements a reordering feature.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "phrase_models/BasePhraseModel.h"
#include "stack_dec/BasePbTransModelFeature.h"
#include "stack_dec/PhrScoreInfo.h"

//--------------- Constants ------------------------------------------

//--------------- Classes --------------------------------------------

//--------------- SrcPosJumpFeat class

/**
 * @brief The SrcPosJumpFeat template class is a base class for
 * implementing a reordering feature.
 */

template <class SCORE_INFO>
class SrcPosJumpFeat : public BasePbTransModelFeature<SCORE_INFO>
{
public:
  typedef typename BasePbTransModelFeature<SCORE_INFO>::HypScoreInfo HypScoreInfo;

  // Constructor
  SrcPosJumpFeat();

  // Feature information
  std::string getFeatType(void);

  // Scoring functions
  HypScoreInfo extensionScore(const std::vector<std::string>& srcSent, const HypScoreInfo& predHypScrInf,
                              const PhrHypDataStr& predHypDataStr, const PhrHypDataStr& newHypDataStr, float weight,
                              Score& unweightedScore);
  Score scorePhrasePairUnweighted(const std::vector<std::string>& srcPhrase, const std::vector<std::string>& trgPhrase);

  // Heuristic related functions
  Score calcHeurScore(const std::vector<std::pair<PositionIndex, PositionIndex>>& gaps,
                      PositionIndex lastSrcPosCovered) const;

  // Functions related to model pointers
  void link_pm(BasePhraseModel* _invPbModelPtr);

protected:
  BasePhraseModel* invPbModelPtr;

  Score srcJumpScore(unsigned int offset) const;
  std::vector<unsigned int> min_jumps(const std::vector<std::pair<PositionIndex, PositionIndex>>& gaps,
                                      PositionIndex lastSrcPosCovered) const;
};

//--------------- SrcPosJumpFeat class functions
//

template <class SCORE_INFO>
SrcPosJumpFeat<SCORE_INFO>::SrcPosJumpFeat()
{
  invPbModelPtr = NULL;
}

//---------------------------------
template <class SCORE_INFO>
std::string SrcPosJumpFeat<SCORE_INFO>::getFeatType(void)
{
  return "SrcPosJumpFeat";
}

//---------------------------------
template <class SCORE_INFO>
Score SrcPosJumpFeat<SCORE_INFO>::scorePhrasePairUnweighted(const std::vector<std::string>& /*srcPhrase*/,
                                                            const std::vector<std::string>& /*trgPhrase*/)
{
  return 0;
}

//---------------------------------
template <class SCORE_INFO>
Score SrcPosJumpFeat<SCORE_INFO>::calcHeurScore(const std::vector<std::pair<PositionIndex, PositionIndex>>& gaps,
                                                PositionIndex lastSrcPosCovered) const
{
  Score result = 0;
  std::vector<unsigned int> jumps = min_jumps(gaps, lastSrcPosCovered);
  for (unsigned int k = 0; k < jumps.size(); ++k)
    result += srcJumpScore(jumps[k]);
  return result;
}

//---------------------------------
template <class SCORE_INFO>
void SrcPosJumpFeat<SCORE_INFO>::link_pm(BasePhraseModel* _invPbModelPtr)
{
  invPbModelPtr = _invPbModelPtr;
}

//---------------------------------------
template <class SCORE_INFO>
Score SrcPosJumpFeat<SCORE_INFO>::srcJumpScore(unsigned int offset) const
{
  return (double)this->invPbModelPtr->trgCutsLgProb(offset);
}

//---------------------------------
template <class SCORE_INFO>
std::vector<unsigned int> SrcPosJumpFeat<SCORE_INFO>::min_jumps(
    const std::vector<std::pair<PositionIndex, PositionIndex>>& gaps, PositionIndex lastSrcPosCovered) const
{
  std::vector<unsigned int> result;
  PositionIndex j = lastSrcPosCovered;
  for (unsigned int k = 0; k < gaps.size(); ++k)
  {
    if (j > gaps[k].first)
      result.push_back(j - gaps[k].first);
    else
      result.push_back(gaps[k].first - j);

    j = gaps[k].second;
  }

  return result;
}

