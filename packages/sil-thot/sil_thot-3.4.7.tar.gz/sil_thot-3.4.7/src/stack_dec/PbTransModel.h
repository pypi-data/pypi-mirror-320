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
 * @file PbTransModel.h
 *
 * @brief Declares the PbTransModel class.  This class is a
 * succesor of the _pbTransModel class.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "stack_dec/PhrHypDataStr.h"
#include "stack_dec/PhraseBasedTmHypRec.h"
#include "stack_dec/_pbTransModel.h"

//--------------- Constants ------------------------------------------

//--------------- Classes --------------------------------------------

//--------------- PbTransModel class

/**
 * @brief The PbTransModel class is a predecessor of the
 * _pbTransModel class.
 */

template <class EQCLASS_FUNC>
class PbTransModel : public _pbTransModel<PhraseBasedTmHypRec<EQCLASS_FUNC>>
{
public:
  typedef typename _pbTransModel<PhraseBasedTmHypRec<EQCLASS_FUNC>>::Hypothesis Hypothesis;
  typedef typename _pbTransModel<PhraseBasedTmHypRec<EQCLASS_FUNC>>::HypScoreInfo HypScoreInfo;
  typedef typename _pbTransModel<PhraseBasedTmHypRec<EQCLASS_FUNC>>::HypDataType HypDataType;

  // Constructor
  PbTransModel();

  // Virtual object copy
  BaseSmtModel<PhraseBasedTmHypRec<EQCLASS_FUNC>>* clone(void);

  // Misc. operations with hypotheses
  HypDataType nullHypothesisHypData(void);
  bool obtainPredecessorHypData(HypDataType& hypd);
  bool isCompleteHypData(const HypDataType& hypd) const;

  // Destructor
  ~PbTransModel();

protected:
  // Misc. operations with hypothesis
  Score nullHypothesisScrComps(Hypothesis& nullHyp, std::vector<Score>& scoreComponents);
  unsigned int numberOfUncoveredSrcWordsHypData(const HypDataType& hypd) const;

  // Scoring functions
  Score incrScore(const Hypothesis& pred_hyp, const HypDataType& new_hypd, Hypothesis& new_hyp,
                  std::vector<Score>& scoreComponents);

  // Specific phrase-based functions
  void extendHypDataIdx(PositionIndex srcLeft, PositionIndex srcRight, const std::vector<WordIndex>& trgPhraseIdx,
                        HypDataType& hypd);

  // Functions for translating with references or prefixes
  bool hypDataTransIsPrefixOfTargetRef(const HypDataType& hypd, bool& equal) const;

  // Heuristic related functions
  PositionIndex getLastSrcPosCoveredHypData(const HypDataType& hypd);

  // Auxiliary functions
  PhrHypDataStr phypd_to_phypdstr(const PhrHypData phypd);
};

//--------------- PbTransModel class functions
//

template <class EQCLASS_FUNC>
PbTransModel<EQCLASS_FUNC>::PbTransModel(void) : _pbTransModel<PhraseBasedTmHypRec<EQCLASS_FUNC>>()
{
}

//---------------------------------
template <class EQCLASS_FUNC>
BaseSmtModel<PhraseBasedTmHypRec<EQCLASS_FUNC>>* PbTransModel<EQCLASS_FUNC>::clone(void)
{
  // Create clone
  return new PbTransModel<EQCLASS_FUNC>(*this);
}

//---------------------------------
template <class EQCLASS_FUNC>
Score PbTransModel<EQCLASS_FUNC>::nullHypothesisScrComps(Hypothesis& nullHyp, std::vector<Score>& scoreComponents)
{
  // Initialize variables
  HypScoreInfo hypScoreInfo;
  HypDataType dataType = nullHypothesisHypData();
  PhrHypDataStr dataTypeStr = phypd_to_phypdstr(dataType);

  // Init scoreInfo
  hypScoreInfo.score = 0;

  // Init scoreComponents
  scoreComponents.clear();

  // Obtain score for standard features
  for (unsigned int i = 0; i < this->standardFeaturesInfoPtr->featPtrVec.size(); ++i)
  {
    Score unweightedScore;
    hypScoreInfo = this->standardFeaturesInfoPtr->featPtrVec[i]->nullHypScore(hypScoreInfo, this->getStdFeatWeight(i),
                                                                              unweightedScore);
    scoreComponents.push_back(unweightedScore);
  }

  // Obtain score for custom features
  for (unsigned int i = 0; i < this->customFeaturesInfoPtr->featPtrVec.size(); ++i)
  {
    Score unweightedScore;
    hypScoreInfo = this->customFeaturesInfoPtr->featPtrVec[i]->nullHypScore(hypScoreInfo, this->getCustomFeatWeight(i),
                                                                            unweightedScore);
    scoreComponents.push_back(unweightedScore);
  }

  // Obtain score for on-the-fly features
  for (unsigned int i = 0; i < this->onTheFlyFeaturesInfo.featPtrVec.size(); ++i)
  {
    Score unweightedScore;
    hypScoreInfo = this->onTheFlyFeaturesInfo.featPtrVec[i]->nullHypScore(hypScoreInfo, this->getOnTheFlyFeatWeight(i),
                                                                          unweightedScore);
    scoreComponents.push_back(unweightedScore);
  }

  nullHyp.setScoreInfo(hypScoreInfo);
  nullHyp.setData(dataType);

  return hypScoreInfo.score;
}

//---------------------------------
template <class EQCLASS_FUNC>
typename PbTransModel<EQCLASS_FUNC>::HypDataType PbTransModel<EQCLASS_FUNC>::nullHypothesisHypData(void)
{
  HypDataType dataType;

  dataType.ntarget.clear();
  dataType.ntarget.push_back(NULL_WORD);
  dataType.sourceSegmentation.clear();
  dataType.targetSegmentCuts.clear();

  return dataType;
}

//---------------------------------
template <class EQCLASS_FUNC>
bool PbTransModel<EQCLASS_FUNC>::obtainPredecessorHypData(HypDataType& hypd)
{
  HypDataType predData;

  predData = hypd;
  // verify if hyp has a predecessor
  if (predData.ntarget.size() <= 1)
    return false;
  else
  {
    unsigned int i;
    unsigned int cuts;

    if (predData.targetSegmentCuts.size() == 0)
    {
      std::cerr << "Warning: hypothesis data corrupted" << std::endl;
      return false;
    }

    // get previous ntarget
    cuts = predData.targetSegmentCuts.size();
    if (cuts == 1)
    {
      i = predData.targetSegmentCuts[0];
    }
    else
    {
      i = predData.targetSegmentCuts[cuts - 1] - predData.targetSegmentCuts[cuts - 2];
    }
    while (i > 0)
    {
      predData.ntarget.pop_back();
      --i;
    }
    // get previous sourceSegmentation
    predData.sourceSegmentation.pop_back();
    // get previous targetSegmentCuts
    predData.targetSegmentCuts.pop_back();
    // set data
    hypd = predData;

    return true;
  }
}

//---------------------------------
template <class EQCLASS_FUNC>
bool PbTransModel<EQCLASS_FUNC>::isCompleteHypData(const HypDataType& hypd) const
{
  if (numberOfUncoveredSrcWordsHypData(hypd) == 0)
    return true;
  else
    return false;
}

//---------------------------------
template <class EQCLASS_FUNC>
PhrHypDataStr PbTransModel<EQCLASS_FUNC>::phypd_to_phypdstr(const PhrHypData phypd)
{
  PhrHypDataStr phypdstr;
  phypdstr.ntarget = this->trgIndexVectorToStrVector(phypd.ntarget);
  phypdstr.sourceSegmentation = phypd.sourceSegmentation;
  phypdstr.targetSegmentCuts = phypd.targetSegmentCuts;
  return phypdstr;
}

//---------------------------------
template <class EQCLASS_FUNC>
Score PbTransModel<EQCLASS_FUNC>::incrScore(const Hypothesis& pred_hyp, const HypDataType& new_hypd,
                                            Hypothesis& new_hyp, std::vector<Score>& scoreComponents)
{
  // Initialize variables
  HypScoreInfo hypScoreInfo = pred_hyp.getScoreInfo();
  HypDataType pred_hypd = pred_hyp.getData();
  PhrHypDataStr pred_hypd_str = phypd_to_phypdstr(pred_hypd);
  PhrHypDataStr new_hypd_str = phypd_to_phypdstr(new_hypd);

  // Init scoreComponents
  scoreComponents.clear();

  // Obtain score for standard features
  for (unsigned int i = 0; i < this->standardFeaturesInfoPtr->featPtrVec.size(); ++i)
  {
    Score unweightedScore;
    hypScoreInfo = this->standardFeaturesInfoPtr->featPtrVec[i]->extensionScore(
        this->pbtmInputVars.srcSentVec, hypScoreInfo, pred_hypd_str, new_hypd_str, this->getStdFeatWeight(i),
        unweightedScore);
    scoreComponents.push_back(unweightedScore);
  }

  // Obtain score for custom features
  /* std::cerr<<"*********************** "<<this->customFeaturesInfoPtr->featPtrVec.size()<<std::endl; */
  for (unsigned int i = 0; i < this->customFeaturesInfoPtr->featPtrVec.size(); ++i)
  {
    Score unweightedScore;
    hypScoreInfo = this->customFeaturesInfoPtr->featPtrVec[i]->extensionScore(
        this->pbtmInputVars.srcSentVec, hypScoreInfo, pred_hypd_str, new_hypd_str, this->getCustomFeatWeight(i),
        unweightedScore);
    scoreComponents.push_back(unweightedScore);
  }

  // Obtain score for on-the-fly features
  for (unsigned int i = 0; i < this->onTheFlyFeaturesInfo.featPtrVec.size(); ++i)
  {
    Score unweightedScore;
    hypScoreInfo = this->onTheFlyFeaturesInfo.featPtrVec[i]->extensionScore(
        this->pbtmInputVars.srcSentVec, hypScoreInfo, pred_hypd_str, new_hypd_str, this->getOnTheFlyFeatWeight(i),
        unweightedScore);
    scoreComponents.push_back(unweightedScore);
  }

  new_hyp.setScoreInfo(hypScoreInfo);
  new_hyp.setData(new_hypd);

  return hypScoreInfo.score;
}

//---------------------------------
template <class EQCLASS_FUNC>
unsigned int PbTransModel<EQCLASS_FUNC>::numberOfUncoveredSrcWordsHypData(const HypDataType& hypd) const
{
  unsigned int n = 0;
  for (unsigned int k = 0; k < hypd.sourceSegmentation.size(); k++)
    n += hypd.sourceSegmentation[k].second - hypd.sourceSegmentation[k].first + 1;

  return (this->pbtmInputVars.srcSentVec.size() - n);
}

//---------------------------------
template <class EQCLASS_FUNC>
void PbTransModel<EQCLASS_FUNC>::extendHypDataIdx(PositionIndex srcLeft, PositionIndex srcRight,
                                                  const std::vector<WordIndex>& trgPhraseIdx, HypDataType& hypd)
{
  std::pair<PositionIndex, PositionIndex> sourceSegm;

  // Add trgPhraseIdx to the target vector
  for (unsigned int i = 0; i < trgPhraseIdx.size(); ++i)
  {
    hypd.ntarget.push_back(trgPhraseIdx[i]);
  }

  // Add source segment and target cut
  sourceSegm.first = srcLeft;
  sourceSegm.second = srcRight;
  hypd.sourceSegmentation.push_back(sourceSegm);

  hypd.targetSegmentCuts.push_back(hypd.ntarget.size() - 1);
}

//---------------------------------
template <class EQCLASS_FUNC>
bool PbTransModel<EQCLASS_FUNC>::hypDataTransIsPrefixOfTargetRef(const HypDataType& hypd, bool& equal) const
{
  PositionIndex ntrgSize = hypd.ntarget.size();
  PositionIndex nrefSentSize = this->pbtmInputVars.nrefSentIdVec.size();

  if (ntrgSize > nrefSentSize)
    return false;
  for (PositionIndex i = 1; i < ntrgSize; ++i)
  {
    if (this->pbtmInputVars.nrefSentIdVec[i] != hypd.ntarget[i])
      return false;
  }
  if (ntrgSize == nrefSentSize)
    equal = true;
  else
    equal = false;

  return true;
}

//---------------------------------
template <class EQCLASS_FUNC>
PositionIndex PbTransModel<EQCLASS_FUNC>::getLastSrcPosCoveredHypData(const HypDataType& hypd)
{
  SourceSegmentation sourceSegmentation;

  sourceSegmentation = hypd.sourceSegmentation;
  if (sourceSegmentation.size() > 0)
    return sourceSegmentation.back().second;
  else
    return 0;
}

//---------------------------------
template <class EQCLASS_FUNC>
PbTransModel<EQCLASS_FUNC>::~PbTransModel()
{
}

//-------------------------

