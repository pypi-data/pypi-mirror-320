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
 * @file LangModelFeat.cc
 *
 * @brief Definitions file for LangModelFeat.h
 */

//--------------- Include files --------------------------------------

#include "stack_dec/LangModelFeat.h"

//--------------- LangModelFeat class functions

template <>
LangModelFeat<PhrScoreInfo>::HypScoreInfo LangModelFeat<PhrScoreInfo>::nullHypScore(const HypScoreInfo& predHypScrInf,
                                                                                    float /*weight*/,
                                                                                    Score& unweightedScore)
{
  unweightedScore = 0;

  // Obtain language model state for null hypothesis
  HypScoreInfo hypScrInf = predHypScrInf;
  lModelPtr->getStateForBeginOfSentence(hypScrInf.lmHist);

  return hypScrInf;
}

//---------------
template <>
LangModelFeat<PhrScoreInfo>::HypScoreInfo LangModelFeat<PhrScoreInfo>::extensionScore(
    const std::vector<std::string>& srcSent, const HypScoreInfo& predHypScrInf, const PhrHypDataStr& predHypDataStr,
    const PhrHypDataStr& newHypDataStr, float weight, Score& unweightedScore)
{
  // Obtain score for hypothesis extension
  HypScoreInfo hypScrInf = predHypScrInf;
  unweightedScore = 0;

  // Obtain current partial translation
  std::vector<std::string> currPartialTrans;
  obtainCurrPartialTrans(predHypDataStr, currPartialTrans);

  // Initialize state
  LM_State state;
  lModelPtr->getStateForBeginOfSentence(state);
  addWordSeqToStateStr(currPartialTrans, state);

  for (unsigned int i = predHypDataStr.sourceSegmentation.size(); i < newHypDataStr.sourceSegmentation.size(); ++i)
  {
    // Initialize variables
    unsigned int trgLeft;
    unsigned int trgRight = newHypDataStr.targetSegmentCuts[i];
    if (i == 0)
      trgLeft = 1;
    else
      trgLeft = newHypDataStr.targetSegmentCuts[i - 1] + 1;
    std::vector<std::string> trgPhrase;
    for (unsigned int k = trgLeft; k <= trgRight; ++k)
      trgPhrase.push_back(newHypDataStr.ntarget[k]);

    // Update score
    Score iterScore = getNgramScoreGivenState(trgPhrase, state);
    unweightedScore += iterScore;
    hypScrInf.score += weight * iterScore;
  }

  // Check if new hypothesis is complete
  if (numberOfSrcWordsCovered(newHypDataStr) == srcSent.size())
  {
    // Obtain score contribution for complete hypothesis
    Score scrCompl = getEosScoreGivenState(state);
    unweightedScore += scrCompl;
    hypScrInf.score += weight * scrCompl;

    // Add end of sentence to current translation
    currPartialTrans.push_back(EOS_STR);
  }

  // Set language model history for hypothesis
  hypScrInf.lmHist = state;

  return hypScrInf;
}
