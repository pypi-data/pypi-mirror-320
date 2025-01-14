#pragma once

#include "phrase_models/BasePhraseModel.h"
#include "stack_dec/BasePbTransModelFeature.h"
#include "stack_dec/PhrScoreInfo.h"
#include "sw_models/AlignmentModel.h"

#define DIRECT_PM_FEAT_DEFAULT_LAMBDA 0.01

/**
 * @brief The DirectPhraseModelFeat template class implements a direct
 * phrase model feature.
 */
template <class SCORE_INFO>
class DirectPhraseModelFeat : public BasePbTransModelFeature<SCORE_INFO>
{
public:
  typedef typename BasePbTransModelFeature<SCORE_INFO>::HypScoreInfo HypScoreInfo;

  // Constructor
  DirectPhraseModelFeat();

  // Thread/Process safety related functions
  bool scoringIsProcessSafe(void);

  // Feature information
  std::string getFeatType(void);

  // Scoring functions
  HypScoreInfo extensionScore(const std::vector<std::string>& srcSent, const HypScoreInfo& predHypScrInf,
                              const PhrHypDataStr& predHypDataStr, const PhrHypDataStr& newHypDataStr, float weight,
                              Score& unweightedScore);
  Score scorePhrasePairUnweighted(const std::vector<std::string>& srcPhrase, const std::vector<std::string>& trgPhrase);

  // Functions to obtain translation options
  void obtainTransOptions(const std::vector<std::string>& wordVec, std::vector<std::vector<std::string>>& transOptVec);

  // Functions related to model pointers
  void link_pm(BasePhraseModel* _invPbModelPtr);
  BasePhraseModel* get_pmptr(void);
  void link_swm(AlignmentModel* _swAligModelPtr);
  AlignmentModel* get_swmptr(void);

  // Functions related to lambda parameter
  void set_lambda(float _lambda);
  float get_lambda(void);

protected:
  BasePhraseModel* invPbModelPtr;
  AlignmentModel* swAligModelPtr;
  float lambda;

  Score directPhrTransUnweightedScore(const std::vector<WordIndex>& srcPhrase, const std::vector<WordIndex>& trgPhrase);
  Score swLgProb(const std::vector<WordIndex>& srcPhraseWidx, const std::vector<WordIndex>& trgPhraseWidx);
  WordIndex stringToSrcWordindex(std::string word);
  std::string wordindexToSrcString(WordIndex wordIdx);
  WordIndex stringToTrgWordindex(std::string word);
  std::string wordindexToTrgString(WordIndex wordIdx);
};

//--------------- WordPenaltyFeat class functions
//

template <class SCORE_INFO>
DirectPhraseModelFeat<SCORE_INFO>::DirectPhraseModelFeat()
{
  this->lambda = DIRECT_PM_FEAT_DEFAULT_LAMBDA;
  invPbModelPtr = NULL;
  swAligModelPtr = NULL;
}

//---------------------------------
template <class SCORE_INFO>
bool DirectPhraseModelFeat<SCORE_INFO>::scoringIsProcessSafe(void)
{
  if (invPbModelPtr == NULL || swAligModelPtr == NULL)
    return false;
  else
  {
    return invPbModelPtr->modelReadsAreProcessSafe() && swAligModelPtr->modelReadsAreProcessSafe();
  }
}

//---------------------------------
template <class SCORE_INFO>
std::string DirectPhraseModelFeat<SCORE_INFO>::getFeatType(void)
{
  return "DirectPhraseModelFeat";
}

//---------------------------------
template <class SCORE_INFO>
Score DirectPhraseModelFeat<SCORE_INFO>::scorePhrasePairUnweighted(const std::vector<std::string>& srcPhrase,
                                                                   const std::vector<std::string>& trgPhrase)
{
  // Obtain WordIndex vectors
  std::vector<WordIndex> srcPhraseIdx;
  for (unsigned int i = 0; i < srcPhrase.size(); ++i)
    srcPhraseIdx.push_back(this->stringToSrcWordindex(srcPhrase[i]));

  std::vector<WordIndex> trgPhraseIdx;
  for (unsigned int i = 0; i < trgPhrase.size(); ++i)
    trgPhraseIdx.push_back(this->stringToTrgWordindex(trgPhrase[i]));

  return directPhrTransUnweightedScore(srcPhraseIdx, trgPhraseIdx);
}

//---------------------------------
template <class SCORE_INFO>
void DirectPhraseModelFeat<SCORE_INFO>::obtainTransOptions(const std::vector<std::string>& wordVec,
                                                           std::vector<std::vector<std::string>>& transOptVec)
{
  // Obtain vector of word indices
  std::vector<WordIndex> wordIdxVec;
  for (unsigned int i = 0; i < wordVec.size(); ++i)
    wordIdxVec.push_back(this->stringToSrcWordindex(wordVec[i]));

  // Obtain translation options
  BasePhraseModel::SrcTableNode srctn;
  this->invPbModelPtr->getTransFor_t_(wordIdxVec, srctn);

  // Put options in vector
  transOptVec.clear();
  for (BasePhraseModel::SrcTableNode::iterator iter = srctn.begin(); iter != srctn.end(); ++iter)
  {
    // Convert option to string vector
    std::vector<std::string> transOpt;
    for (unsigned int i = 0; i < iter->first.size(); ++i)
      transOpt.push_back(this->wordindexToTrgString(iter->first[i]));

    // Add new entry
    transOptVec.push_back(transOpt);
  }
}

//---------------------------------
template <class SCORE_INFO>
void DirectPhraseModelFeat<SCORE_INFO>::link_pm(BasePhraseModel* _invPbModelPtr)
{
  invPbModelPtr = _invPbModelPtr;
}

//---------------------------------
template <class SCORE_INFO>
BasePhraseModel* DirectPhraseModelFeat<SCORE_INFO>::get_pmptr(void)
{
  return invPbModelPtr;
}

//---------------------------------
template <class SCORE_INFO>
void DirectPhraseModelFeat<SCORE_INFO>::link_swm(AlignmentModel* _swAligModelPtr)
{
  swAligModelPtr = _swAligModelPtr;
}

//---------------------------------
template <class SCORE_INFO>
AlignmentModel* DirectPhraseModelFeat<SCORE_INFO>::get_swmptr(void)
{
  return swAligModelPtr;
}

//---------------------------------
template <class SCORE_INFO>
void DirectPhraseModelFeat<SCORE_INFO>::set_lambda(float _lambda)
{
  lambda = _lambda;
}

//---------------------------------
template <class SCORE_INFO>
float DirectPhraseModelFeat<SCORE_INFO>::get_lambda(void)
{
  return lambda;
}

//---------------------------------
template <class SCORE_INFO>
Score DirectPhraseModelFeat<SCORE_INFO>::directPhrTransUnweightedScore(const std::vector<WordIndex>& srcPhrase,
                                                                       const std::vector<WordIndex>& trgPhrase)
{
  if (lambda == 1.0)
  {
    return (double)invPbModelPtr->logps_t_(trgPhrase, srcPhrase);
  }
  else
  {
    float sum1 = log(lambda) + (float)invPbModelPtr->logps_t_(trgPhrase, srcPhrase);
    if (sum1 <= log(PHRASE_PROB_SMOOTH))
      sum1 = FEAT_LGPROB_SMOOTH;
    float sum2 = log(1.0 - lambda) + (float)swLgProb(srcPhrase, trgPhrase);
    float interp = MathFuncs::lns_sumlog(sum1, sum2);
    return (double)interp;
  }
}

//---------------------------------
template <class SCORE_INFO>
Score DirectPhraseModelFeat<SCORE_INFO>::swLgProb(const std::vector<WordIndex>& srcPhrase,
                                                  const std::vector<WordIndex>& trgPhrase)
{
  return swAligModelPtr->computeSumLogProb(srcPhrase, trgPhrase);
}

//---------------------------------
template <class SCORE_INFO>
WordIndex DirectPhraseModelFeat<SCORE_INFO>::stringToSrcWordindex(std::string word)
{
  return invPbModelPtr->stringToTrgWordIndex(word);
}

//---------------------------------
template <class SCORE_INFO>
std::string DirectPhraseModelFeat<SCORE_INFO>::wordindexToSrcString(WordIndex wordIdx)
{
  return invPbModelPtr->wordIndexToTrgString(wordIdx);
}

//---------------------------------
template <class SCORE_INFO>
WordIndex DirectPhraseModelFeat<SCORE_INFO>::stringToTrgWordindex(std::string word)
{
  return invPbModelPtr->stringToSrcWordIndex(word);
}

//---------------------------------
template <class SCORE_INFO>
std::string DirectPhraseModelFeat<SCORE_INFO>::wordindexToTrgString(WordIndex wordIdx)
{
  return invPbModelPtr->wordIndexToSrcString(wordIdx);
}
