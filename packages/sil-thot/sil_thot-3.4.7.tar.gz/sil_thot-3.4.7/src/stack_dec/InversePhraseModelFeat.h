
#pragma once

#include "phrase_models/BasePhraseModel.h"
#include "stack_dec/BasePbTransModelFeature.h"
#include "stack_dec/PhrScoreInfo.h"
#include "sw_models/AlignmentModel.h"

#define INVERSE_PM_FEAT_DEFAULT_LAMBDA 0.01

/**
 * @brief The InversePhraseModelFeat template class implementes an
 * inverse phrase model feature.
 */
template <class SCORE_INFO>
class InversePhraseModelFeat : public BasePbTransModelFeature<SCORE_INFO>
{
public:
  typedef typename BasePbTransModelFeature<SCORE_INFO>::HypScoreInfo HypScoreInfo;

  // Constructor
  InversePhraseModelFeat();

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
  void link_swm(AlignmentModel* _invSwAligModelPtr);
  AlignmentModel* get_swmptr(void);

  // Functions related to lambda parameter
  void set_lambda(float _lambda);
  float get_lambda(void);

protected:
  BasePhraseModel* invPbModelPtr;
  AlignmentModel* invSwAligModelPtr;
  float lambda;

  Score inversePhrTransUnweightedScore(const std::vector<WordIndex>& srcPhrase,
                                       const std::vector<WordIndex>& trgPhrase);
  Score invSwLgProb(const std::vector<WordIndex>& srcPhraseWidx, const std::vector<WordIndex>& trgPhraseWidx);
  WordIndex stringToSrcWordindex(std::string word);
  std::string wordindexToSrcString(WordIndex wordIdx);
  WordIndex stringToTrgWordindex(std::string word);
  std::string wordindexToTrgString(WordIndex wordIdx);
};

//--------------- WordPenaltyFeat class functions
//

template <class SCORE_INFO>
InversePhraseModelFeat<SCORE_INFO>::InversePhraseModelFeat()
{
  this->lambda = INVERSE_PM_FEAT_DEFAULT_LAMBDA;
  invPbModelPtr = NULL;
  invSwAligModelPtr = NULL;
}

//---------------------------------
template <class SCORE_INFO>
bool InversePhraseModelFeat<SCORE_INFO>::scoringIsProcessSafe(void)
{
  if (invPbModelPtr == NULL || invSwAligModelPtr == NULL)
    return false;
  else
  {
    return invPbModelPtr->modelReadsAreProcessSafe() && invSwAligModelPtr->modelReadsAreProcessSafe();
  }
}

//---------------------------------
template <class SCORE_INFO>
std::string InversePhraseModelFeat<SCORE_INFO>::getFeatType(void)
{
  return "InversePhraseModelFeat";
}

//---------------------------------
template <class SCORE_INFO>
Score InversePhraseModelFeat<SCORE_INFO>::scorePhrasePairUnweighted(const std::vector<std::string>& srcPhrase,
                                                                    const std::vector<std::string>& trgPhrase)
{
  // Obtain WordIndex vectors
  std::vector<WordIndex> srcPhraseIdx;
  for (unsigned int i = 0; i < srcPhrase.size(); ++i)
    srcPhraseIdx.push_back(this->stringToSrcWordindex(srcPhrase[i]));

  std::vector<WordIndex> trgPhraseIdx;
  for (unsigned int i = 0; i < trgPhrase.size(); ++i)
    trgPhraseIdx.push_back(this->stringToTrgWordindex(trgPhrase[i]));

  return inversePhrTransUnweightedScore(srcPhraseIdx, trgPhraseIdx);
}

//---------------------------------
template <class SCORE_INFO>
void InversePhraseModelFeat<SCORE_INFO>::obtainTransOptions(const std::vector<std::string>& /*wordVec*/,
                                                            std::vector<std::vector<std::string>>& transOptVec)
{
  transOptVec.clear();
}

//---------------------------------
template <class SCORE_INFO>
void InversePhraseModelFeat<SCORE_INFO>::link_pm(BasePhraseModel* _invPbModelPtr)
{
  invPbModelPtr = _invPbModelPtr;
}

//---------------------------------
template <class SCORE_INFO>
BasePhraseModel* InversePhraseModelFeat<SCORE_INFO>::get_pmptr(void)
{
  return invPbModelPtr;
}

//---------------------------------
template <class SCORE_INFO>
void InversePhraseModelFeat<SCORE_INFO>::link_swm(AlignmentModel* _invSwAligModelPtr)
{
  invSwAligModelPtr = _invSwAligModelPtr;
}

//---------------------------------
template <class SCORE_INFO>
AlignmentModel* InversePhraseModelFeat<SCORE_INFO>::get_swmptr(void)
{
  return invSwAligModelPtr;
}

//---------------------------------
template <class SCORE_INFO>
void InversePhraseModelFeat<SCORE_INFO>::set_lambda(float _lambda)
{
  lambda = _lambda;
}

//---------------------------------
template <class SCORE_INFO>
float InversePhraseModelFeat<SCORE_INFO>::get_lambda(void)
{
  return lambda;
}

//---------------------------------
template <class SCORE_INFO>
Score InversePhraseModelFeat<SCORE_INFO>::inversePhrTransUnweightedScore(const std::vector<WordIndex>& srcPhrase,
                                                                         const std::vector<WordIndex>& trgPhrase)
{
  if (lambda == 1.0)
  {
    return (double)invPbModelPtr->logpt_s_(trgPhrase, srcPhrase);
  }
  else
  {
    float sum1 = log(lambda) + (float)invPbModelPtr->logpt_s_(trgPhrase, srcPhrase);
    if (sum1 <= log(PHRASE_PROB_SMOOTH))
      sum1 = FEAT_LGPROB_SMOOTH;
    float sum2 = log(1.0 - lambda) + (float)invSwLgProb(srcPhrase, trgPhrase);
    float interp = MathFuncs::lns_sumlog(sum1, sum2);
    return (double)interp;
  }
}

//---------------------------------
template <class SCORE_INFO>
Score InversePhraseModelFeat<SCORE_INFO>::invSwLgProb(const std::vector<WordIndex>& srcPhrase,
                                                      const std::vector<WordIndex>& trgPhrase)
{
  return invSwAligModelPtr->computePhraseSumLogProb(trgPhrase, srcPhrase);
}

//---------------------------------
template <class SCORE_INFO>
WordIndex InversePhraseModelFeat<SCORE_INFO>::stringToSrcWordindex(std::string word)
{
  return invPbModelPtr->stringToTrgWordIndex(word);
}

//---------------------------------
template <class SCORE_INFO>
std::string InversePhraseModelFeat<SCORE_INFO>::wordindexToSrcString(WordIndex wordIdx)
{
  return invPbModelPtr->wordIndexToTrgString(wordIdx);
}

//---------------------------------
template <class SCORE_INFO>
WordIndex InversePhraseModelFeat<SCORE_INFO>::stringToTrgWordindex(std::string word)
{
  return invPbModelPtr->stringToSrcWordIndex(word);
}

//---------------------------------
template <class SCORE_INFO>
std::string InversePhraseModelFeat<SCORE_INFO>::wordindexToTrgString(WordIndex wordIdx)
{
  return invPbModelPtr->wordIndexToSrcString(wordIdx);
}
