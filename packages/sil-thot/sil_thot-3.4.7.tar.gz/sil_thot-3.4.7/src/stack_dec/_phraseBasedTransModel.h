/*
thot package for statistical machine translation
Copyright (C) 2013 Daniel Ortiz-Mart\'inez and SIL International

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

#pragma once

#include "nlp_common/Prob.h"
#include "nlp_common/ins_op_pair.h"
#include "stack_dec/BasePbTransModel.h"
#include "stack_dec/LangModelInfo.h"
#include "stack_dec/NbestTransCacheData.h"
#include "stack_dec/PbTransModelInputVars.h"
#include "stack_dec/PhraseModelInfo.h"
#include "stack_dec/PhrasePairCacheTable.h"
#include "stack_dec/ScoreCompDefs.h"
#include "stack_dec/SourceSegmentation.h"

#include <math.h>
#include <memory>
#include <set>

#define NO_HEURISTIC 0
#define LOCAL_T_HEURISTIC 4
#define LOCAL_TD_HEURISTIC 6
#define MODEL_IDLE_STATE 1
#define MODEL_TRANS_STATE 2
#define MODEL_TRANSREF_STATE 3
#define MODEL_TRANSVER_STATE 4
#define MODEL_TRANSPREFIX_STATE 5

/**
 * @brief The _phraseBasedTransModel class is a predecessor of the
 * BasePbTransModel class.
 */
template <class HYPOTHESIS>
class _phraseBasedTransModel : public BasePbTransModel<HYPOTHESIS>
{
public:
  typedef typename BasePbTransModel<HYPOTHESIS>::Hypothesis Hypothesis;
  typedef typename BasePbTransModel<HYPOTHESIS>::HypScoreInfo HypScoreInfo;
  typedef typename BasePbTransModel<HYPOTHESIS>::HypDataType HypDataType;

  // Constructor
  _phraseBasedTransModel();

  // Link language model information
  void setLangModelInfo(LangModelInfo* lmInfo);
  LangModelInfo* getLangModelInfo();

  // Link phrase model information
  void setPhraseModelInfo(PhraseModelInfo* pmlInfo);
  PhraseModelInfo* getPhraseModelInfo();

  // Init language and alignment models
  virtual bool loadLangModel(const char* prefixFileName, int verbose = 0);
  virtual bool loadAligModel(const char* prefixFileName, int verbose = 0);

  // Print models
  virtual bool printLangModel(std::string printPrefix);
  virtual bool printAligModel(std::string printPrefix);

  void clear();

  // Actions to be executed before the translation
  void pre_trans_actions(std::string srcsent);
  void pre_trans_actions_ref(std::string srcsent, std::string refsent);
  void pre_trans_actions_ver(std::string srcsent, std::string refsent);
  void pre_trans_actions_prefix(std::string srcsent, std::string prefix);

  // Function to obtain current source sentence (it may differ from
  // that provided when calling pre_trans_actions since information
  // about translation constraints is removed)
  std::string getCurrentSrcSent();

  // Word prediction functions
  void addSentenceToWordPred(std::vector<std::string> strVec, int verbose = 0);
  std::pair<Count, std::string> getBestSuffix(std::string input);
  std::pair<Count, std::string> getBestSuffixGivenHist(std::vector<std::string> hist, std::string input);

  ////// Hypotheses-related functions

  // Expansion-related functions
  void expand(const Hypothesis& hyp, std::vector<Hypothesis>& hypVec, std::vector<std::vector<Score>>& scrCompVec);
  void expand_ref(const Hypothesis& hyp, std::vector<Hypothesis>& hypVec, std::vector<std::vector<Score>>& scrCompVec);
  void expand_ver(const Hypothesis& hyp, std::vector<Hypothesis>& hypVec, std::vector<std::vector<Score>>& scrCompVec);
  void expand_prefix(const Hypothesis& hyp, std::vector<Hypothesis>& hypVec,
                     std::vector<std::vector<Score>>& scrCompVec);

  // Heuristic-related functions
  void setHeuristic(unsigned int _heuristicId);
  unsigned int getHeuristic() const;
  void addHeuristicToHyp(Hypothesis& hyp);
  void subtractHeuristicToHyp(Hypothesis& hyp);

  // Printing functions and data conversion
  void printHyp(const Hypothesis& hyp, std::ostream& outS, int verbose = false);
  std::vector<std::string> getTransInPlainTextVec(const Hypothesis& hyp) const;
  std::vector<std::string> getTransInPlainTextVec(const Hypothesis& hyp, std::set<PositionIndex>& unknownWords) const;

  // Model weights functions
  void getUnweightedComps(const std::vector<Score>& scrComps, std::vector<Score>& unweightedScrComps);
  Score getScoreForHyp(const Hypothesis& hyp);
  std::vector<Score> scoreCompsForHyp(const Hypothesis& hyp);

  // Specific phrase-based functions
  void extendHypData(PositionIndex srcLeft, PositionIndex srcRight, const std::vector<std::string>& trgPhrase,
                     HypDataType& hypd);

  // Destructor
  ~_phraseBasedTransModel();

protected:
  typedef std::map<std::pair<std::vector<WordIndex>, std::vector<WordIndex>>, std::vector<Score>> PhrasePairVecScore;

  // Data structure to store input variables
  PbTransModelInputVars pbtmInputVars;

  // Language model members
  std::shared_ptr<LangModelInfo> langModelInfo;

  // Phrase model members
  std::shared_ptr<PhraseModelInfo> phraseModelInfo;

  // Members useful for caching data
  PhrasePairVecScore cachedDirectPhrScoreVecs;
  PhrasePairVecScore cachedInversePhrScoreVecs;

  // Data used to cache n-best translation scores
  NbestTransCacheData nbTransCacheData;

  // Set of unseen words
  std::set<std::string> unseenWordsSet;

  // Mapping between phrase and language model vocabularies
  std::map<WordIndex, WordIndex> tmToLmVocMap;

  // Heuristic function to be used
  unsigned int heuristicId;
  // Heuristic probability vector
  std::vector<std::vector<Score>> heuristicScoreVec;
  // Additional data structures to store information about heuristics
  std::vector<LgProb> refHeurLmLgProb;
  std::vector<LgProb> prefHeurLmLgProb;

  // Variable to store state of the translation model
  unsigned int state;

  // Training-related data members
  std::vector<std::vector<std::string>> wordPredSentVec;

  // Protected functions

  // Functions related to class initialization
  void instantiateWeightVectors();

  // Word prediction functions
  void incrAddSentenceToWordPred(std::vector<std::string> strVec, int verbose = 0);
  void minibatchAddSentenceToWordPred(std::vector<std::string> strVec, int verbose = 0);
  void batchAddSentenceToWordPred(std::vector<std::string> strVec, int verbose = 0);

  ////// Hypotheses-related functions

  // Expansion-related functions
  void extract_gaps(const Hypothesis& hyp, std::vector<std::pair<PositionIndex, PositionIndex>>& gaps);
  void extract_gaps(const Bitset<MAX_SENTENCE_LENGTH_ALLOWED>& hypKey,
                    std::vector<std::pair<PositionIndex, PositionIndex>>& gaps);
  unsigned int get_num_gaps(const Bitset<MAX_SENTENCE_LENGTH_ALLOWED>& hypKey);

  // Specific phrase-based functions
  virtual void extendHypDataIdx(PositionIndex srcLeft, PositionIndex srcRight,
                                const std::vector<WordIndex>& trgPhraseIdx, HypDataType& hypd) = 0;

  virtual bool getHypDataVecForGap(const Hypothesis& hyp, PositionIndex srcLeft, PositionIndex srcRight,
                                   std::vector<HypDataType>& hypDataTypeVec, float N);
  // Get N-best translations for a subphrase of the source sentence
  // to be translated .  If N is between 0 and 1 then N represents a
  // threshold.
  virtual bool getHypDataVecForGapRef(const Hypothesis& hyp, PositionIndex srcLeft, PositionIndex srcRight,
                                      std::vector<HypDataType>& hypDataTypeVec, float N);
  // This function is identical to the previous function but is to
  // be used when the translation process is conducted by a given
  // reference sentence
  virtual bool getHypDataVecForGapVer(const Hypothesis& hyp, PositionIndex srcLeft, PositionIndex srcRight,
                                      std::vector<HypDataType>& hypDataTypeVec, float N);
  // This function is identical to the previous function but is to
  // be used when the translation process is performed to verify the
  // coverage of the model given a reference sentence
  virtual bool getHypDataVecForGapPref(const Hypothesis& hyp, PositionIndex srcLeft, PositionIndex srcRight,
                                       std::vector<HypDataType>& hypDataTypeVec, float N);
  // This function is identical to the previous function but is to
  // be used when the translation process is conducted by a given
  // prefix

  virtual bool getTransForHypUncovGap(const Hypothesis& hyp, PositionIndex srcLeft, PositionIndex srcRight,
                                      NbestTableNode<PhraseTransTableNodeData>& nbt, float N);
  // Get N-best translations for a subphrase of the source sentence
  // to be translated .  If N is between 0 and 1 then N represents a
  // threshold.  The result of the search is cached in the data
  // member cPhrNbestTransTable
  virtual bool getTransForHypUncovGapRef(const Hypothesis& hyp, PositionIndex srcLeft, PositionIndex srcRight,
                                         NbestTableNode<PhraseTransTableNodeData>& nbt, float N);
  // This function is identical to the previous function but is to
  // be used when the translation process is conducted by a given
  // reference sentence
  virtual bool getTransForHypUncovGapVer(const Hypothesis& hyp, PositionIndex srcLeft, PositionIndex srcRight,
                                         NbestTableNode<PhraseTransTableNodeData>& nbt, float N);
  // This function is identical to the previous function but is to
  // be used when the translation process is performed to verify the
  // coverage of the model given a reference sentence
  virtual bool getTransForHypUncovGapPref(const Hypothesis& hyp, PositionIndex srcLeft, PositionIndex srcRight,
                                          NbestTableNode<PhraseTransTableNodeData>& nbt, float N);
  // This function is identical to the previous function but is to
  // be used when the translation process is conducted by a given
  // prefix

  // Functions for translating with references or prefixes
  virtual bool hypDataTransIsPrefixOfTargetRef(const HypDataType& hypd, bool& equal) const = 0;
  void transUncovGapPrefNoGen(const Hypothesis& hyp, PositionIndex srcLeft, PositionIndex srcRight,
                              NbestTableNode<PhraseTransTableNodeData>& nbt);
  void genListOfTransLongerThanPref(std::vector<WordIndex> s_, unsigned int ntrgSize,
                                    NbestTableNode<PhraseTransTableNodeData>& nbt);
  bool trgWordVecIsPrefix(const std::vector<WordIndex>& wiVec1, bool lastWiVec1WordIsComplete,
                          const std::string& lastWiVec1Word, const std::vector<WordIndex>& wiVec2, bool& equal);
  // returns true if target word vector wiVec1 is a prefix of wiVec2

  PositionIndex getLastSrcPosCovered(const Hypothesis& hyp);
  // Get the index of last source position which was covered
  virtual PositionIndex getLastSrcPosCoveredHypData(const HypDataType& hypd) = 0;
  // The same as the previous function, but given an object of
  // HypDataType

  // Language model scoring functions
  Score wordPenaltyScore(unsigned int tlen);
  Score sumWordPenaltyScore(unsigned int tlen);
  Score nbestLmScoringFunc(const std::vector<WordIndex>& target);
  Score getNgramScoreGivenState(const std::vector<WordIndex>& target, LM_State& state);
  Score getScoreEndGivenState(LM_State& state);
  LgProb getSentenceLgProb(const std::vector<WordIndex>& target, int verbose = 0);

  // Phrase model scoring functions
  Score phrScore_s_t_(const std::vector<WordIndex>& s_, const std::vector<WordIndex>& t_);
  // obtains the logarithm of pstWeight*ps_t_
  std::vector<Score> phrScoreVec_s_t_(const std::vector<WordIndex>& s_, const std::vector<WordIndex>& t_);
  // the same as phrScore_s_t_ but returns a score vector for each model
  Score phrScore_t_s_(const std::vector<WordIndex>& s_, const std::vector<WordIndex>& t_);
  // obtains the logarithm of ptsWeight*pt_s_
  std::vector<Score> phrScoreVec_t_s_(const std::vector<WordIndex>& s_, const std::vector<WordIndex>& t_);
  // the same as phrScore_t_s_ but returns a score vector for each model
  Score srcJumpScore(unsigned int offset);
  // obtains score for source jump
  Score srcSegmLenScore(unsigned int k, const SourceSegmentation& srcSegm, unsigned int srcLen,
                        unsigned int lastTrgSegmLen);
  // obtains the log-probability for the length of the k'th source
  // segment
  Score trgSegmLenScore(unsigned int x_k, unsigned int x_km1, unsigned int trgLen);
  // obtains the log-probability for the length of a target segment

  // Functions to generate translation lists
  bool getTransForInvPbModel(const std::vector<WordIndex>& s_, std::set<std::vector<WordIndex>>& transSet);
  virtual bool getNbestTransFor_s_(std::vector<WordIndex> s_, NbestTableNode<PhraseTransTableNodeData>& nbt, float N);
  // Get N-best translations for a given source phrase s_.
  // If N is between 0 and 1 then N represents a threshold

  // Functions to score n-best translations lists
  virtual Score nbestTransScore(const std::vector<WordIndex>& s_, const std::vector<WordIndex>& t_) = 0;
  virtual Score nbestTransScoreLast(const std::vector<WordIndex>& s_, const std::vector<WordIndex>& t_) = 0;
  // Cached functions to score n-best translations lists
  Score nbestTransScoreCached(const std::vector<WordIndex>& s_, const std::vector<WordIndex>& t_);
  Score nbestTransScoreLastCached(const std::vector<WordIndex>& s_, const std::vector<WordIndex>& t_);

  // Functions related to pre_trans_actions
  virtual void clearTempVars(void);
  bool lastCharIsBlank(std::string str);
  void verifyDictCoverageForSentence(std::vector<std::string>& sentenceVec,
                                     int maxSrcPhraseLength = MAX_SENTENCE_LENGTH_ALLOWED);
  // Verifies dictionary coverage for the sentence to translate.  It
  // is possible to impose an additional constraint consisting of a
  // maximum length for the source phrases.
  void manageUnseenSrcWord(std::string srcw);
  bool unseenSrcWord(std::string srcw);
  bool unseenSrcWordGivenPosition(unsigned int srcPos);
  Score unkWordScoreHeur(void);
  void initHeuristic(unsigned int maxSrcPhraseLength);
  // Initialize heuristic for the sentence to be translated

  // Functions related to getTransInPlainTextVec
  std::vector<std::string> getTransInPlainTextVecTs(const Hypothesis& hyp, std::set<PositionIndex>& unknownWords) const;
  std::vector<std::string> getTransInPlainTextVecTps(const Hypothesis& hyp,
                                                     std::set<PositionIndex>& unknownWords) const;
  std::vector<std::string> getTransInPlainTextVecTrs(const Hypothesis& hyp,
                                                     std::set<PositionIndex>& unknownWords) const;
  std::vector<std::string> getTransInPlainTextVecTvs(const Hypothesis& hyp,
                                                     std::set<PositionIndex>& unknownWords) const;

  // Heuristic related functions
  virtual Score calcHeuristicScore(const Hypothesis& hyp);
  void initHeuristicLocalt(int maxSrcPhraseLength);
  Score heurLmScoreLt(std::vector<WordIndex>& t_);
  Score heurLmScoreLtNoAdmiss(std::vector<WordIndex>& t_);
  Score calcRefLmHeurScore(const Hypothesis& hyp);
  Score calcPrefLmHeurScore(const Hypothesis& hyp);
  Score heuristicLocalt(const Hypothesis& hyp);
  void initHeuristicLocaltd(int maxSrcPhraseLength);
  Score heuristicLocaltd(const Hypothesis& hyp);
  std::vector<unsigned int> min_jumps(const std::vector<std::pair<PositionIndex, PositionIndex>>& gaps,
                                      PositionIndex lastSrcPosCovered) const;

  // Vocabulary functions
  WordIndex stringToSrcWordIndex(std::string s) const;
  std::string wordIndexToSrcString(WordIndex w) const;
  std::vector<std::string> srcIndexVectorToStrVector(std::vector<WordIndex> srcidxVec) const;
  std::vector<WordIndex> strVectorToSrcIndexVector(std::vector<std::string> srcStrVec) const;
  WordIndex stringToTrgWordIndex(std::string s) const;
  std::string wordIndexToTrgString(WordIndex w) const;
  std::vector<std::string> trgIndexVectorToStrVector(std::vector<WordIndex> trgidxVec) const;
  std::vector<WordIndex> strVectorToTrgIndexVector(std::vector<std::string> trgStrVec) const;
  std::string phraseToStr(const std::vector<WordIndex>& phr) const;
  std::vector<std::string> phraseToStrVec(const std::vector<WordIndex>& phr) const;
  WordIndex tmVocabToLmVocab(WordIndex w);
  void initTmToLmVocabMap(void);
};

template <class HYPOTHESIS>
_phraseBasedTransModel<HYPOTHESIS>::_phraseBasedTransModel(void) : BasePbTransModel<HYPOTHESIS>()
{
  // Set state info
  state = MODEL_IDLE_STATE;

  // Initially, no heuristic is used
  heuristicId = NO_HEURISTIC;
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::setLangModelInfo(LangModelInfo* lmInfo)
{
  langModelInfo.reset(lmInfo);

  // Initialize tm to lm vocab map
  initTmToLmVocabMap();
}

template <class HYPOTHESIS>
LangModelInfo* _phraseBasedTransModel<HYPOTHESIS>::getLangModelInfo()
{
  return langModelInfo.get();
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::instantiateWeightVectors()
{
  phraseModelInfo->phraseModelPars.ptsWeightVec.clear();
  phraseModelInfo->phraseModelPars.pstWeightVec.clear();

  phraseModelInfo->phraseModelPars.ptsWeightVec.push_back(DEFAULT_PTS_WEIGHT);
  phraseModelInfo->phraseModelPars.pstWeightVec.push_back(DEFAULT_PST_WEIGHT);
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::setPhraseModelInfo(PhraseModelInfo* pmInfo)
{
  phraseModelInfo.reset(pmInfo);
}

template <class HYPOTHESIS>
PhraseModelInfo* _phraseBasedTransModel<HYPOTHESIS>::getPhraseModelInfo()
{
  return phraseModelInfo.get();
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::loadLangModel(const char* prefixFileName, int verbose /*=0*/)
{
  std::string penFile;
  std::string predFile;
  int err;

  langModelInfo->langModelPars.languageModelFileName = prefixFileName;

  // Initializes language model
  if (langModelInfo->langModel->load(prefixFileName, verbose) == THOT_ERROR)
    return THOT_ERROR;

  // load WordPredictor info
  predFile = prefixFileName;
  predFile = predFile + ".wp";
  err = langModelInfo->wordPredictor.load(predFile.c_str(), verbose);
  if (err == THOT_ERROR && verbose)
  {
    std::cerr << "Warning: File for initializing the word predictor not provided!" << std::endl;
  }
  return THOT_OK;
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::loadAligModel(const char* prefixFileName, int verbose /*=0*/)
{
  // Save parameters
  phraseModelInfo->phraseModelPars.srcTrainVocabFileName = "";
  phraseModelInfo->phraseModelPars.trgTrainVocabFileName = "";
  phraseModelInfo->phraseModelPars.readTablePrefix = prefixFileName;

  // Load phrase model
  if (this->phraseModelInfo->invPhraseModel->load(prefixFileName, verbose) != 0)
    return THOT_ERROR;

  // Instantiate weight vectors for phrase model
  instantiateWeightVectors();

  return THOT_OK;
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::printLangModel(std::string printPrefix)
{
  bool retVal = langModelInfo->langModel->print(printPrefix.c_str());
  if (retVal == THOT_ERROR)
    return THOT_ERROR;

  return THOT_OK;
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::printAligModel(std::string printPrefix)
{
  bool retVal = this->phraseModelInfo->invPhraseModel->print(printPrefix.c_str());
  if (retVal == THOT_ERROR)
    return THOT_ERROR;

  return THOT_OK;
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::clear(void)
{
  this->phraseModelInfo->invPhraseModel->clear();
  langModelInfo->langModel->clear();
  langModelInfo->wpModel->clear();
  langModelInfo->wordPredictor.clear();
  // Set state info
  state = MODEL_IDLE_STATE;
}

template <class HYPOTHESIS>
PositionIndex _phraseBasedTransModel<HYPOTHESIS>::getLastSrcPosCovered(const Hypothesis& hyp)
{
  return getLastSrcPosCoveredHypData(hyp.getData());
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::wordPenaltyScore(unsigned int tlen)
{
  return langModelInfo->langModelPars.wpScaleFactor * (double)langModelInfo->wpModel->wordPenaltyScore(tlen);
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::sumWordPenaltyScore(unsigned int tlen)
{
  return langModelInfo->langModelPars.wpScaleFactor * (double)langModelInfo->wpModel->sumWordPenaltyScore(tlen);
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::nbestLmScoringFunc(const std::vector<WordIndex>& target)
{
  // Warning: this function may become a bottleneck when the list of
  // translation options is large

  PhraseCacheTable::iterator pctIter;
  pctIter = nbTransCacheData.cnbLmScores.find(target);
  if (pctIter != nbTransCacheData.cnbLmScores.end())
  {
    // Score was previously stored in the cache table
    return pctIter->second;
  }
  else
  {
    // Score is not stored in the cache table
    std::vector<WordIndex> hist;
    LM_State state;
    langModelInfo->langModel->getStateForWordSeq(hist, state);
    Score scr = getNgramScoreGivenState(target, state);
    nbTransCacheData.cnbLmScores[target] = scr;
    return scr;
  }
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::getNgramScoreGivenState(const std::vector<WordIndex>& target, LM_State& state)
{
  // Score not present in cache table
  std::vector<WordIndex> target_lm;
  Score unweighted_result = 0;

  // target_lm stores the target sentence using indices of the language model
  for (unsigned int i = 0; i < target.size(); ++i)
  {
    target_lm.push_back(tmVocabToLmVocab(target[i]));
  }

  for (unsigned int i = 0; i < target_lm.size(); ++i)
  {
#ifdef WORK_WITH_ZERO_GRAM_PROB
    Score scr = log((double)langModelInfoPtr->lModelPtr->getZeroGramProb());
#else
    Score scr = (double)langModelInfo->langModel->getNgramLgProbGivenState(target_lm[i], state);
#endif
    // Increase score
    unweighted_result += scr;
  }
  // Return result
  return langModelInfo->langModelPars.lmScaleFactor * unweighted_result;
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::getScoreEndGivenState(LM_State& state)
{
#ifdef WORK_WITH_ZERO_GRAM_PROB
  return langModelInfoPtr->langModelPars.lmScaleFactor * log((double)langModelInfoPtr->lModelPtr->getZeroGramProb());
#else
  return langModelInfo->langModelPars.lmScaleFactor * (double)langModelInfo->langModel->getLgProbEndGivenState(state);
#endif
}

template <class HYPOTHESIS>
LgProb _phraseBasedTransModel<HYPOTHESIS>::getSentenceLgProb(const std::vector<WordIndex>& target, int verbose)
{
  LgProb lmLgProb = 0;

  std::vector<WordIndex> s;
  unsigned int i;
  for (i = 0; i < target.size(); ++i)
    s.push_back(tmVocabToLmVocab(target[i]));
  lmLgProb = (double)langModelInfo->langModel->getSentenceLog10Prob(s, verbose) * M_LN10;

  return lmLgProb;
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::phrScore_s_t_(const std::vector<WordIndex>& s_,
                                                        const std::vector<WordIndex>& t_)
{
  std::vector<Score> scoreVec = phrScoreVec_s_t_(s_, t_);
  Score sum = 0;
  for (unsigned int i = 0; i < scoreVec.size(); ++i)
    sum += scoreVec[i];
  return sum;
}

template <class HYPOTHESIS>
std::vector<Score> _phraseBasedTransModel<HYPOTHESIS>::phrScoreVec_s_t_(const std::vector<WordIndex>& s_,
                                                                        const std::vector<WordIndex>& t_)
{
  // Check if score of phrase pair is stored in cache table
  PhrasePairVecScore::iterator ppctIter = cachedInversePhrScoreVecs.find(std::make_pair(s_, t_));
  if (ppctIter != cachedInversePhrScoreVecs.end())
    return ppctIter->second;
  else
  {
    // Score has not been cached previously
    std::vector<Score> scoreVec;
    Score score = this->phraseModelInfo->phraseModelPars.pstWeightVec[0]
                * (double)this->phraseModelInfo->invPhraseModel->logpt_s_(t_, s_);
    scoreVec.push_back(score);
    cachedInversePhrScoreVecs[std::make_pair(s_, t_)] = scoreVec;
    return scoreVec;
  }
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::phrScore_t_s_(const std::vector<WordIndex>& s_,
                                                        const std::vector<WordIndex>& t_)
{
  std::vector<Score> scoreVec = phrScoreVec_t_s_(s_, t_);
  Score sum = 0;
  for (unsigned int i = 0; i < scoreVec.size(); ++i)
    sum += scoreVec[i];
  return sum;
}

template <class HYPOTHESIS>
std::vector<Score> _phraseBasedTransModel<HYPOTHESIS>::phrScoreVec_t_s_(const std::vector<WordIndex>& s_,
                                                                        const std::vector<WordIndex>& t_)
{
  // Check if score of phrase pair is stored in cache table
  PhrasePairVecScore::iterator ppctIter = cachedDirectPhrScoreVecs.find(std::make_pair(s_, t_));
  if (ppctIter != cachedDirectPhrScoreVecs.end())
    return ppctIter->second;
  else
  {
    // Score has not been cached previously
    std::vector<Score> scoreVec;
    Score score = this->phraseModelInfo->phraseModelPars.ptsWeightVec[0]
                * (double)this->phraseModelInfo->invPhraseModel->logps_t_(t_, s_);
    scoreVec.push_back(score);
    cachedDirectPhrScoreVecs[std::make_pair(s_, t_)] = scoreVec;
    return scoreVec;
  }
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::srcJumpScore(unsigned int offset)
{
  return this->phraseModelInfo->phraseModelPars.srcJumpWeight
       * (double)this->phraseModelInfo->invPhraseModel->trgCutsLgProb(offset);
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::srcSegmLenScore(unsigned int k, const SourceSegmentation& srcSegm,
                                                          unsigned int srcLen, unsigned int lastTrgSegmLen)
{
  return this->phraseModelInfo->phraseModelPars.srcSegmLenWeight
       * (double)this->phraseModelInfo->invPhraseModel->trgSegmLenLgProb(k, srcSegm, srcLen, lastTrgSegmLen);
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::trgSegmLenScore(unsigned int x_k, unsigned int x_km1, unsigned int trgLen)
{
  return this->phraseModelInfo->phraseModelPars.trgSegmLenWeight
       * (double)this->phraseModelInfo->invPhraseModel->srcSegmLenLgProb(x_k, x_km1, trgLen);
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::clearTempVars(void)
{
  // Clear input information
  pbtmInputVars.clear();

  // Clear set of unseen words
  unseenWordsSet.clear();

  // Clear data structures that are used
  // for fast access.

  // Clear phrase model caching data members
  cachedDirectPhrScoreVecs.clear();
  cachedInversePhrScoreVecs.clear();

  // Clear n-best translation cache data
  nbTransCacheData.clear();

  // Init the map between TM and LM vocabularies
  initTmToLmVocabMap();

  // Clear information of the heuristic used in the translation
  heuristicScoreVec.clear();

  // Clear additional heuristic information
  refHeurLmLgProb.clear();
  prefHeurLmLgProb.clear();

  // Clear temporary variables of the language model
  langModelInfo->langModel->clearTempVars();

  // Clear temporary variables of the phrase model
  this->phraseModelInfo->invPhraseModel->clearTempVars();
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::lastCharIsBlank(std::string str)
{
  if (str.size() == 0)
    return false;
  else
  {
    if (str[str.size() - 1] == ' ')
      return true;
    else
      return false;
  }
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::verifyDictCoverageForSentence(std::vector<std::string>& sentenceVec,
                                                                       int /*maxSrcPhraseLength*/)
{
  // Manage source words without translation options
  for (unsigned int j = 0; j < sentenceVec.size(); ++j)
  {
    NbestTableNode<PhraseTransTableNodeData> ttNode;
    std::string s = sentenceVec[j];
    std::vector<WordIndex> s_;
    s_.push_back(stringToSrcWordIndex(s));
    std::set<std::vector<WordIndex>> transSet;
    getTransForInvPbModel(s_, transSet);
    if (transSet.size() == 0)
    {
      manageUnseenSrcWord(s);
    }
  }
  // Clear temporary variables of the phrase model
  this->phraseModelInfo->invPhraseModel->clearTempVars();
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::manageUnseenSrcWord(std::string srcw)
{
  // Visualize warning depending on the verbosity level
  if (this->verbosity > 0)
  {
    std::cerr << "Warning! word " << srcw << " has been marked as unseen." << std::endl;
  }
  // Add word to the set of unseen words
  unseenWordsSet.insert(srcw);
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::unseenSrcWord(std::string srcw)
{
  std::set<std::string>::iterator setIter;

  setIter = unseenWordsSet.find(srcw);
  if (setIter != unseenWordsSet.end())
    return true;
  else
    return false;
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::unseenSrcWordGivenPosition(unsigned int srcPos)
{
  return unseenSrcWord(pbtmInputVars.srcSentVec[srcPos - 1]);
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::unkWordScoreHeur(void)
{
  Score result = 0;

  // Obtain phrase scores
  std::vector<WordIndex> s_;
  std::vector<WordIndex> t_;

  // Init s_ and t_
  s_.push_back(UNK_WORD);
  t_.push_back(UNK_WORD);

  // p(t_|s_) phrase score
  result += this->phrScore_t_s_(s_, t_);

  // p(s_|t_) phrase score
  result += this->phrScore_s_t_(s_, t_);

  // Obtain lm scores
  std::vector<WordIndex> hist;
  LM_State state;
  langModelInfo->langModel->getStateForWordSeq(hist, state);
  t_.clear();
  t_.push_back(UNK_WORD);
  result += getNgramScoreGivenState(t_, state);

  // Return result
  return result;
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::initHeuristic(unsigned int maxSrcPhraseLength)
{
  switch (heuristicId)
  {
  case LOCAL_T_HEURISTIC:
    initHeuristicLocalt(maxSrcPhraseLength);
    break;
  case LOCAL_TD_HEURISTIC:
    initHeuristicLocaltd(maxSrcPhraseLength);
    break;
  }
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::initHeuristicLocalt(int maxSrcPhraseLength)
{
  std::vector<Score> row;
  NbestTableNode<PhraseTransTableNodeData> ttNode;
  NbestTableNode<PhraseTransTableNodeData>::iterator ttNodeIter;
  Score compositionProduct;
  Score bestScore_ts = 0;
  Score score_ts;
  std::vector<WordIndex> s_;

  unsigned int J = pbtmInputVars.nsrcSentIdVec.size() - 1;
  heuristicScoreVec.clear();
  // Initialize row vector
  for (unsigned int j = 0; j < J; ++j)
    row.push_back(-FLT_MAX);
  // Insert rows into t-heuristic table
  for (unsigned int j = 0; j < J; ++j)
    heuristicScoreVec.push_back(row);

  // Fill the t-heuristic table
  for (unsigned int y = 0; y < J; ++y)
  {
    for (unsigned int x = J - y - 1; x < J; ++x)
    {
      // obtain source phrase
      unsigned int segmRightMostj = y;
      unsigned int segmLeftMostj = J - x - 1;
      s_.clear();

      // obtain score for best translation
      if ((segmRightMostj - segmLeftMostj) + 1 > (unsigned int)maxSrcPhraseLength)
      {
        ttNode.clear();
      }
      else
      {
        for (unsigned int j = segmLeftMostj; j <= segmRightMostj; ++j)
          s_.push_back(pbtmInputVars.nsrcSentIdVec[j + 1]);

        // obtain translations for s_
        getNbestTransFor_s_(s_, ttNode, this->pbTransModelPars.W);
        if (ttNode.size() != 0) // Obtain best p(s_|t_)
        {
          bestScore_ts = -FLT_MAX;
          for (ttNodeIter = ttNode.begin(); ttNodeIter != ttNode.end(); ++ttNodeIter)
          {
            // Obtain phrase to phrase translation probability
            score_ts = phrScore_s_t_(s_, ttNodeIter->second) + phrScore_t_s_(s_, ttNodeIter->second);
            // Obtain language model heuristic estimation
            //            score_ts+=heurLmScoreLt(ttNodeIter->second);
            score_ts += heurLmScoreLtNoAdmiss(ttNodeIter->second);

            if (bestScore_ts < score_ts)
              bestScore_ts = score_ts;
          }
        }
      }

      // Check source phrase length
      if (x == J - y - 1)
      {
        // source phrase has only one word
        if (ttNode.size() != 0)
        {
          heuristicScoreVec[y][x] = bestScore_ts;
        }
        else
        {
          heuristicScoreVec[y][x] = unkWordScoreHeur();
        }
      }
      else
      {
        // source phrase has more than one word
        if (ttNode.size() != 0)
        {
          heuristicScoreVec[y][x] = bestScore_ts;
        }
        else
        {
          heuristicScoreVec[y][x] = -FLT_MAX;
        }
        for (unsigned int z = J - x - 1; z < y; ++z)
        {
          compositionProduct = heuristicScoreVec[z][x] + heuristicScoreVec[y][J - 2 - z];
          if (heuristicScoreVec[y][x] < compositionProduct)
          {
            heuristicScoreVec[y][x] = compositionProduct;
          }
        }
      }
    }
  }
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::heurLmScoreLt(std::vector<WordIndex>& t_)
{
  std::vector<WordIndex> lmHist;
  unsigned int i;
  LM_State lmState;
  LgProb lp = 0;

  if (t_.size() > 2)
  {
    langModelInfo->langModel->getStateForBeginOfSentence(lmState);
    langModelInfo->langModel->getNgramLgProbGivenState(tmVocabToLmVocab(t_[0]), lmState);
    langModelInfo->langModel->getNgramLgProbGivenState(tmVocabToLmVocab(t_[1]), lmState);
  }
  for (i = 2; i < t_.size(); ++i)
  {
    lp = lp + (double)langModelInfo->langModel->getNgramLgProbGivenState(tmVocabToLmVocab(t_[i]), lmState);
  }
  return lp * (double)langModelInfo->langModelPars.lmScaleFactor;
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::heurLmScoreLtNoAdmiss(std::vector<WordIndex>& t_)
{
  std::vector<WordIndex> hist;
  LM_State state;
  langModelInfo->langModel->getStateForWordSeq(hist, state);
  Score scr = getNgramScoreGivenState(t_, state);
  return scr;
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::calcRefLmHeurScore(const Hypothesis& hyp)
{
  if (refHeurLmLgProb.empty())
  {
    // Fill vector with lm components for the reference sentence
    LgProb lp = 0;
    LM_State lmState;
    langModelInfo->langModel->getStateForBeginOfSentence(lmState);

    refHeurLmLgProb.push_back(NULL_WORD);
    for (unsigned int i = 1; i < pbtmInputVars.nrefSentIdVec.size(); ++i)
    {
      lp +=
          langModelInfo->langModel->getNgramLgProbGivenState(tmVocabToLmVocab(pbtmInputVars.nrefSentIdVec[i]), lmState);
      refHeurLmLgProb.push_back(lp);
    }
  }
  // Return heuristic value
  unsigned int len = hyp.partialTransLength();
  LgProb lp = refHeurLmLgProb.back() - refHeurLmLgProb[len];

  return (double)langModelInfo->langModelPars.lmScaleFactor * (double)lp;
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::calcPrefLmHeurScore(const Hypothesis& hyp)
{
  if (prefHeurLmLgProb.empty())
  {
    // Fill vector with lm components for the reference sentence
    LgProb lp = 0;
    LM_State lmState;
    langModelInfo->langModel->getStateForBeginOfSentence(lmState);

    prefHeurLmLgProb.push_back(0);
    for (unsigned int i = 1; i < pbtmInputVars.nprefSentIdVec.size(); ++i)
    {
      lp += langModelInfo->langModel->getNgramLgProbGivenState(tmVocabToLmVocab(pbtmInputVars.nprefSentIdVec[i]),
                                                               lmState);
      prefHeurLmLgProb.push_back(lp);
    }
  }
  // Return heuristic value
  LgProb lp;
  unsigned int len = hyp.partialTransLength();
  if (len >= pbtmInputVars.nprefSentIdVec.size() - 1)
    lp = 0;
  else
  {
    lp = prefHeurLmLgProb.back() - prefHeurLmLgProb[len];
  }
  return (double)langModelInfo->langModelPars.lmScaleFactor * (double)lp;
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::heuristicLocalt(const Hypothesis& hyp)
{
  if (state == MODEL_TRANS_STATE)
  {
    LgProb result = 0;
    unsigned int J;
    std::vector<std::pair<PositionIndex, PositionIndex>> gaps;

    J = pbtmInputVars.srcSentVec.size();
    this->extract_gaps(hyp, gaps);
    for (unsigned int i = 0; i < gaps.size(); ++i)
    {
      result += heuristicScoreVec[gaps[i].second - 1][J - gaps[i].first];
    }
    return result;
  }
  else
  {
    // TO-DO
    return 0;
  }
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::initHeuristicLocaltd(int maxSrcPhraseLength)
{
  initHeuristicLocalt(maxSrcPhraseLength);
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::heuristicLocaltd(const Hypothesis& hyp)
{
  if (state == MODEL_TRANS_STATE)
  {
    Score result = 0;

    // Get local t heuristic information
    unsigned int J = pbtmInputVars.srcSentVec.size();
    std::vector<std::pair<PositionIndex, PositionIndex>> gaps;
    this->extract_gaps(hyp, gaps);
    for (unsigned int i = 0; i < gaps.size(); ++i)
    {
      result += heuristicScoreVec[gaps[i].second - 1][J - gaps[i].first];
    }

    // Distortion heuristic information
    PositionIndex lastSrcPosCovered = getLastSrcPosCovered(hyp);
    std::vector<unsigned int> jumps = min_jumps(gaps, lastSrcPosCovered);
    for (unsigned int k = 0; k < jumps.size(); ++k)
      result += srcJumpScore(jumps[k]);

    return result;
  }
  else
  {
    // TO-DO
    return 0;
  }
}

template <class HYPOTHESIS>
std::vector<unsigned int> _phraseBasedTransModel<HYPOTHESIS>::min_jumps(
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

template <class HYPOTHESIS>
WordIndex _phraseBasedTransModel<HYPOTHESIS>::stringToSrcWordIndex(std::string s) const
{
  return this->phraseModelInfo->invPhraseModel->stringToTrgWordIndex(s);
}

template <class HYPOTHESIS>
std::string _phraseBasedTransModel<HYPOTHESIS>::wordIndexToSrcString(WordIndex w) const
{
  return this->phraseModelInfo->invPhraseModel->wordIndexToTrgString(w);
}

template <class HYPOTHESIS>
std::vector<std::string> _phraseBasedTransModel<HYPOTHESIS>::srcIndexVectorToStrVector(
    std::vector<WordIndex> srcidxVec) const
{
  std::vector<std::string> vStr;
  unsigned int i;

  for (i = 0; i < srcidxVec.size(); ++i)
    vStr.push_back(wordIndexToSrcString(srcidxVec[i]));

  return vStr;
}

template <class HYPOTHESIS>
std::vector<WordIndex> _phraseBasedTransModel<HYPOTHESIS>::strVectorToSrcIndexVector(
    std::vector<std::string> srcStrVec) const
{
  std::vector<WordIndex> widxVec;
  unsigned int i;

  for (i = 0; i < srcStrVec.size(); ++i)
    widxVec.push_back(stringToSrcWordIndex(srcStrVec[i]));

  return widxVec;
}

template <class HYPOTHESIS>
WordIndex _phraseBasedTransModel<HYPOTHESIS>::stringToTrgWordIndex(std::string s) const
{
  return this->phraseModelInfo->invPhraseModel->stringToSrcWordIndex(s);
}

template <class HYPOTHESIS>
std::string _phraseBasedTransModel<HYPOTHESIS>::wordIndexToTrgString(WordIndex w) const
{
  return this->phraseModelInfo->invPhraseModel->wordIndexToSrcString(w);
}

template <class HYPOTHESIS>
std::vector<std::string> _phraseBasedTransModel<HYPOTHESIS>::trgIndexVectorToStrVector(
    std::vector<WordIndex> trgidxVec) const
{
  std::vector<std::string> vStr;
  unsigned int i;

  for (i = 0; i < trgidxVec.size(); ++i)
    vStr.push_back(wordIndexToTrgString(trgidxVec[i]));

  return vStr;
}

template <class HYPOTHESIS>
std::vector<WordIndex> _phraseBasedTransModel<HYPOTHESIS>::strVectorToTrgIndexVector(
    std::vector<std::string> trgStrVec) const
{
  std::vector<WordIndex> widxVec;
  unsigned int i;

  for (i = 0; i < trgStrVec.size(); ++i)
    widxVec.push_back(stringToTrgWordIndex(trgStrVec[i]));

  return widxVec;
}

template <class HYPOTHESIS>
std::string _phraseBasedTransModel<HYPOTHESIS>::phraseToStr(const std::vector<WordIndex>& phr) const
{
  std::string s;
  std::vector<std::string> svec;

  svec = phraseToStrVec(phr);
  for (unsigned int i = 0; i < svec.size(); ++i)
  {
    if (i == 0)
      s = svec[0];
    else
      s = s + " " + svec[i];
  }
  return s;
}

template <class HYPOTHESIS>
std::vector<std::string> _phraseBasedTransModel<HYPOTHESIS>::phraseToStrVec(const std::vector<WordIndex>& phr) const
{
  return trgIndexVectorToStrVector(phr);
}

template <class HYPOTHESIS>
WordIndex _phraseBasedTransModel<HYPOTHESIS>::tmVocabToLmVocab(WordIndex w)
{
  std::map<WordIndex, WordIndex>::const_iterator mapIter;

  mapIter = tmToLmVocMap.find(w);
  if (mapIter == tmToLmVocMap.end())
  {
    // w not found
    // Obtain string from index
    std::string s = wordIndexToTrgString(w);
    // Add string to the lm vocabulary if necessary
    if (!langModelInfo->langModel->existSymbol(s))
    {
      WordIndex nw = langModelInfo->langModel->stringToWordIndex(UNK_SYMBOL_STR);
      tmToLmVocMap[w] = nw;
      return nw;
    }
    else
    {
      // Map tm word to lm word
      WordIndex nw = langModelInfo->langModel->stringToWordIndex(s);
      tmToLmVocMap[w] = nw;
      return nw;
    }
  }
  else
  {
    // w found
    return mapIter->second;
  }
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::initTmToLmVocabMap(void)
{
  tmToLmVocMap.clear();
  tmToLmVocMap[UNK_WORD] = langModelInfo->langModel->stringToWordIndex(UNK_SYMBOL_STR);
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::pre_trans_actions(std::string srcsent)
{
  // Clear temporary variables
  clearTempVars();

  // Set state info
  state = MODEL_TRANS_STATE;

  // Store source sentence to be translated
  this->transMetadata->obtainTransConstraints(srcsent, this->verbosity);
  pbtmInputVars.srcSentVec = this->transMetadata->getSrcSentVec();

  // Verify coverage for source
  if (this->verbosity > 0)
    std::cerr << "Verify model coverage for source sentence..." << std::endl;
  verifyDictCoverageForSentence(pbtmInputVars.srcSentVec, this->pbTransModelPars.A);

  // Store source sentence as an array of WordIndex.
  // Note: this must be done after verifying the coverage for the
  // source sentence since it may contain unknown words

  // Init source sentence index vector after the coverage has been
  // verified
  pbtmInputVars.srcSentIdVec.clear();
  pbtmInputVars.nsrcSentIdVec.clear();
  pbtmInputVars.nsrcSentIdVec.push_back(NULL_WORD);
  for (unsigned int i = 0; i < pbtmInputVars.srcSentVec.size(); ++i)
  {
    WordIndex w = stringToSrcWordIndex(pbtmInputVars.srcSentVec[i]);
    pbtmInputVars.srcSentIdVec.push_back(w);
    pbtmInputVars.nsrcSentIdVec.push_back(w);
  }

  // Initialize heuristic (the source sentence must be previously
  // stored)
  if (this->verbosity > 0)
    std::cerr << "Initializing information about search heuristic..." << std::endl;
  initHeuristic(this->pbTransModelPars.A);
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::pre_trans_actions_ref(std::string srcsent, std::string refsent)
{
  // Clear temporary variables
  clearTempVars();

  // Set state info
  state = MODEL_TRANSREF_STATE;

  // Store source sentence to be translated
  pbtmInputVars.srcSentVec = StrProcUtils::stringToStringVector(srcsent);

  // Verify coverage for source
  if (this->verbosity > 0)
    std::cerr << "Verify model coverage for source sentence..." << std::endl;
  verifyDictCoverageForSentence(pbtmInputVars.srcSentVec, this->pbTransModelPars.A);

  // Init source sentence index vector after the coverage has been
  // verified
  pbtmInputVars.srcSentIdVec.clear();
  pbtmInputVars.nsrcSentIdVec.clear();
  pbtmInputVars.nsrcSentIdVec.push_back(NULL_WORD);
  for (unsigned int i = 0; i < pbtmInputVars.srcSentVec.size(); ++i)
  {
    WordIndex w = stringToSrcWordIndex(pbtmInputVars.srcSentVec[i]);
    pbtmInputVars.srcSentIdVec.push_back(w);
    pbtmInputVars.nsrcSentIdVec.push_back(w);
  }

  // Store reference sentence
  pbtmInputVars.refSentVec = StrProcUtils::stringToStringVector(refsent);

  pbtmInputVars.nrefSentIdVec.clear();
  pbtmInputVars.nrefSentIdVec.push_back(NULL_WORD);
  for (unsigned int i = 0; i < pbtmInputVars.refSentVec.size(); ++i)
  {
    WordIndex w = stringToTrgWordIndex(pbtmInputVars.refSentVec[i]);
    if (w == UNK_WORD && this->verbosity > 0)
      std::cerr << "Warning: word " << pbtmInputVars.refSentVec[i]
                << " is not contained in the phrase model vocabulary, ensure that your language model contains the "
                   "unknown-word token."
                << std::endl;
    pbtmInputVars.nrefSentIdVec.push_back(w);
  }

  // Initialize heuristic (the source sentence must be previously
  // stored)
  if (this->verbosity > 0)
    std::cerr << "Initializing information about search heuristic..." << std::endl;
  initHeuristic(this->pbTransModelPars.A);
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::pre_trans_actions_ver(std::string srcsent, std::string refsent)
{
  // Clear temporary variables
  clearTempVars();

  // Set state info
  state = MODEL_TRANSVER_STATE;

  // Store source sentence to be translated
  pbtmInputVars.srcSentVec = StrProcUtils::stringToStringVector(srcsent);

  // Verify coverage for source
  if (this->verbosity > 0)
    std::cerr << "Verify model coverage for source sentence..." << std::endl;
  verifyDictCoverageForSentence(pbtmInputVars.srcSentVec, this->pbTransModelPars.A);

  // Init source sentence index vector after the coverage has been
  // verified
  pbtmInputVars.srcSentIdVec.clear();
  pbtmInputVars.nsrcSentIdVec.clear();
  pbtmInputVars.nsrcSentIdVec.push_back(NULL_WORD);
  for (unsigned int i = 0; i < pbtmInputVars.srcSentVec.size(); ++i)
  {
    WordIndex w = stringToSrcWordIndex(pbtmInputVars.srcSentVec[i]);
    pbtmInputVars.srcSentIdVec.push_back(w);
    pbtmInputVars.nsrcSentIdVec.push_back(w);
  }

  // Store reference sentence
  pbtmInputVars.refSentVec = StrProcUtils::stringToStringVector(refsent);

  pbtmInputVars.nrefSentIdVec.clear();
  pbtmInputVars.nrefSentIdVec.push_back(NULL_WORD);
  for (unsigned int i = 0; i < pbtmInputVars.refSentVec.size(); ++i)
  {
    WordIndex w = stringToTrgWordIndex(pbtmInputVars.refSentVec[i]);
    if (w == UNK_WORD && this->verbosity > 0)
      std::cerr << "Warning: word " << pbtmInputVars.refSentVec[i]
                << " is not contained in the phrase model vocabulary, ensure that your language model contains the "
                   "unknown-word token."
                << std::endl;
    pbtmInputVars.nrefSentIdVec.push_back(w);
  }

  // Initialize heuristic (the source sentence must be previously
  // stored)
  if (this->verbosity > 0)
    std::cerr << "Initializing information about search heuristic..." << std::endl;
  initHeuristic(this->pbTransModelPars.A);
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::pre_trans_actions_prefix(std::string srcsent, std::string prefix)
{
  // Clear temporary variables
  clearTempVars();

  // Set state info
  state = MODEL_TRANSPREFIX_STATE;

  // Store source sentence to be translated
  pbtmInputVars.srcSentVec = StrProcUtils::stringToStringVector(srcsent);

  // Verify coverage for source
  if (this->verbosity > 0)
    std::cerr << "Verify model coverage for source sentence..." << std::endl;
  verifyDictCoverageForSentence(pbtmInputVars.srcSentVec, this->pbTransModelPars.A);

  // Init source sentence index vector after the coverage has been
  // verified
  pbtmInputVars.srcSentIdVec.clear();
  pbtmInputVars.nsrcSentIdVec.clear();
  pbtmInputVars.nsrcSentIdVec.push_back(NULL_WORD);
  for (unsigned int i = 0; i < pbtmInputVars.srcSentVec.size(); ++i)
  {
    WordIndex w = stringToSrcWordIndex(pbtmInputVars.srcSentVec[i]);
    pbtmInputVars.srcSentIdVec.push_back(w);
    pbtmInputVars.nsrcSentIdVec.push_back(w);
  }

  // Store prefix sentence
  if (lastCharIsBlank(prefix))
    pbtmInputVars.lastCharOfPrefIsBlank = true;
  else
    pbtmInputVars.lastCharOfPrefIsBlank = false;
  pbtmInputVars.prefSentVec = StrProcUtils::stringToStringVector(prefix);

  pbtmInputVars.nprefSentIdVec.clear();
  pbtmInputVars.nprefSentIdVec.push_back(NULL_WORD);
  for (unsigned int i = 0; i < pbtmInputVars.prefSentVec.size(); ++i)
  {
    WordIndex w = stringToTrgWordIndex(pbtmInputVars.prefSentVec[i]);
    if (w == UNK_WORD && this->verbosity > 0)
      std::cerr << "Warning: word " << pbtmInputVars.prefSentVec[i]
                << " is not contained in the phrase model vocabulary, ensure that your language model contains the "
                   "unknown-word token."
                << std::endl;
    pbtmInputVars.nprefSentIdVec.push_back(w);
  }

  // Initialize heuristic (the source sentence must be previously
  // stored)
  if (this->verbosity > 0)
    std::cerr << "Initializing information about search heuristic..." << std::endl;
  initHeuristic(this->pbTransModelPars.A);
}

template <class HYPOTHESIS>
std::string _phraseBasedTransModel<HYPOTHESIS>::getCurrentSrcSent(void)
{
  return StrProcUtils::stringVectorToString(pbtmInputVars.srcSentVec);
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::addSentenceToWordPred(std::vector<std::string> strVec, int verbose /*=0*/)
{
  switch (this->onlineTrainingPars.onlineLearningAlgorithm)
  {
  case BASIC_INCR_TRAINING:
    incrAddSentenceToWordPred(strVec, verbose);
    break;
  case MINIBATCH_TRAINING:
    minibatchAddSentenceToWordPred(strVec, verbose);
    break;
  case BATCH_RETRAINING:
    batchAddSentenceToWordPred(strVec, verbose);
    break;
  default:
    std::cerr << "Warning: requested online update of word predictor with id="
              << this->onlineTrainingPars.onlineLearningAlgorithm << " is not implemented." << std::endl;
    break;
  }
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::incrAddSentenceToWordPred(std::vector<std::string> strVec, int verbose /*=0*/)
{
  if (verbose)
    std::cerr << "Adding a new sentence to word predictor..." << std::endl;
  langModelInfo->wordPredictor.addSentence(strVec);
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::minibatchAddSentenceToWordPred(std::vector<std::string> strVec,
                                                                        int verbose /*=0*/)
{
  // Store sentence
  wordPredSentVec.push_back(strVec);

  // Check if a mini-batch has to be processed
  // (onlineTrainingPars.learnStepSize determines the size of the
  // mini-batch)
  unsigned int batchSize = (unsigned int)this->onlineTrainingPars.learnStepSize;
  if (!wordPredSentVec.empty() && (wordPredSentVec.size() % batchSize) == 0)
  {
    if (verbose)
      std::cerr << "Adding " << batchSize << " sentences to word predictor..." << std::endl;

    for (unsigned int i = 0; i < wordPredSentVec.size(); ++i)
      langModelInfo->wordPredictor.addSentence(wordPredSentVec[i]);
    wordPredSentVec.clear();
  }
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::batchAddSentenceToWordPred(std::vector<std::string> strVec, int verbose /*=0*/)
{
  // Store sentence
  wordPredSentVec.push_back(strVec);

  // Check if a mini-batch has to be processed
  // (onlineTrainingPars.learnStepSize determines the size of the
  // mini-batch)
  unsigned int batchSize = (unsigned int)this->onlineTrainingPars.learnStepSize;
  if (!wordPredSentVec.empty() && (wordPredSentVec.size() % batchSize) == 0)
  {
    if (verbose)
      std::cerr << "Adding " << batchSize << " sentences to word predictor..." << std::endl;

    for (unsigned int i = 0; i < wordPredSentVec.size(); ++i)
      langModelInfo->wordPredictor.addSentence(wordPredSentVec[i]);
    wordPredSentVec.clear();
  }
}

template <class HYPOTHESIS>
std::pair<Count, std::string> _phraseBasedTransModel<HYPOTHESIS>::getBestSuffix(std::string input)
{
  return langModelInfo->wordPredictor.getBestSuffix(input);
}

template <class HYPOTHESIS>
std::pair<Count, std::string> _phraseBasedTransModel<HYPOTHESIS>::getBestSuffixGivenHist(std::vector<std::string> hist,
                                                                                         std::string input)
{
  WordPredictor::SuffixList suffixList;
  WordPredictor::SuffixList::iterator suffixListIter;
  LgProb lp;
  LgProb maxlp = -FLT_MAX;
  std::pair<Count, std::string> bestCountSuffix;

  // Get suffix list for input
  langModelInfo->wordPredictor.getSuffixList(input, suffixList);
  if (suffixList.size() == 0)
  {
    // There are not any suffix
    return std::make_pair(0, "");
  }
  else
  {
    // There are one or more suffixes
    LM_State lmState;
    LM_State aux;

    // Initialize language model state given history
    langModelInfo->langModel->getStateForBeginOfSentence(lmState);
    for (unsigned int i = 0; i < hist.size(); ++i)
    {
      langModelInfo->langModel->getNgramLgProbGivenState(langModelInfo->langModel->stringToWordIndex(hist[i]), lmState);
    }

    // Obtain probability for each suffix given history
    for (suffixListIter = suffixList.begin(); suffixListIter != suffixList.end(); ++suffixListIter)
    {
      std::string lastw;

      aux = lmState;
      lastw = input + suffixListIter->second;
      lp = langModelInfo->langModel->getNgramLgProbGivenState(langModelInfo->langModel->stringToWordIndex(lastw), aux);
      if (maxlp < lp)
      {
        bestCountSuffix.first = suffixListIter->first;
        bestCountSuffix.second = suffixListIter->second;
        maxlp = lp;
      }
    }
    // Return best suffix
    return bestCountSuffix;
  }
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::expand(const Hypothesis& hyp, std::vector<Hypothesis>& hypVec,
                                                std::vector<std::vector<Score>>& scrCompVec)
{
  std::vector<std::pair<PositionIndex, PositionIndex>> gaps;
  std::vector<WordIndex> s_;
  Hypothesis extHyp;
  std::vector<HypDataType> hypDataVec;
  std::vector<Score> scoreComponents;

  hypVec.clear();
  scrCompVec.clear();

  // Extract gaps
  extract_gaps(hyp, gaps);
  if (this->verbosity >= 2)
  {
    std::cerr << "  gaps: " << gaps.size() << std::endl;
  }

  // Generate new hypotheses completing the gaps
  for (unsigned int k = 0; k < gaps.size(); ++k)
  {
    unsigned int gap_length = gaps[k].second - gaps[k].first + 1;
    for (unsigned int x = 0; x < gap_length; ++x)
    {
      s_.clear();
      if (x <= this->pbTransModelPars.U) // x should be lower than U, which is the maximum
                                         // number of words that can be jUmped
      {
        for (unsigned int y = x; y < gap_length; ++y)
        {
          unsigned int segmRightMostj = gaps[k].first + y;
          unsigned int segmLeftMostj = gaps[k].first + x;
          bool srcPhraseIsAffectedByConstraint =
              this->transMetadata->srcPhrAffectedByConstraint(std::make_pair(segmLeftMostj, segmRightMostj));
          // Verify that the source phrase length does not exceed
          // the limit. The limit can be exceeded when the source
          // phrase is affected by a translation constraint
          if ((segmRightMostj - segmLeftMostj) + 1 > this->pbTransModelPars.A && !srcPhraseIsAffectedByConstraint)
            break;
          // Obtain hypothesis data vector
          getHypDataVecForGap(hyp, segmLeftMostj, segmRightMostj, hypDataVec, this->pbTransModelPars.W);
          if (hypDataVec.size() != 0)
          {
            for (unsigned int i = 0; i < hypDataVec.size(); ++i)
            {
              // Create hypothesis extension
              this->incrScore(hyp, hypDataVec[i], extHyp, scoreComponents);
              // Obtain information about hypothesis extension
              SourceSegmentation srcSegm;
              std::vector<PositionIndex> trgSegmCuts;
              extHyp.getPhraseAlign(srcSegm, trgSegmCuts);
              std::vector<std::string> targetWordVec = this->getTransInPlainTextVec(extHyp);
              // Check if translation constraints are satisfied
              if (this->transMetadata->translationSatisfiesConstraints(srcSegm, trgSegmCuts, targetWordVec))
              {
                hypVec.push_back(extHyp);
                scrCompVec.push_back(scoreComponents);
              }
            }
#ifdef THOT_STATS
            this->basePbTmStats.transOptions += hypDataVec.size();
            ++this->basePbTmStats.getTransCalls;
#endif
          }
        }
      }
    }
  }
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::expand_ref(const Hypothesis& hyp, std::vector<Hypothesis>& hypVec,
                                                    std::vector<std::vector<Score>>& scrCompVec)
{
  std::vector<std::pair<PositionIndex, PositionIndex>> gaps;
  std::vector<WordIndex> s_;
  Hypothesis extHyp;
  std::vector<HypDataType> hypDataVec;
  std::vector<Score> scoreComponents;

  hypVec.clear();
  scrCompVec.clear();

  // Extract gaps
  extract_gaps(hyp, gaps);

  // Generate new hypotheses completing the gaps
  for (unsigned int k = 0; k < gaps.size(); ++k)
  {
    unsigned int gap_length = gaps[k].second - gaps[k].first + 1;
    for (unsigned int x = 0; x < gap_length; ++x)
    {
      s_.clear();
      if (x <= this->pbTransModelPars.U) // x should be lower than U, which is the maximum
                                         // number of words that can be jUmped
      {
        for (unsigned int y = x; y < gap_length; ++y)
        {
          unsigned int segmRightMostj = gaps[k].first + y;
          unsigned int segmLeftMostj = gaps[k].first + x;
          // Verify that the source phrase length does not exceed
          // the limit
          if ((segmRightMostj - segmLeftMostj) + 1 > this->pbTransModelPars.A)
            break;
          // Obtain hypothesis data vector
          getHypDataVecForGapRef(hyp, segmLeftMostj, segmRightMostj, hypDataVec, this->pbTransModelPars.W);
          if (hypDataVec.size() != 0)
          {
            for (unsigned int i = 0; i < hypDataVec.size(); ++i)
            {
              this->incrScore(hyp, hypDataVec[i], extHyp, scoreComponents);
              hypVec.push_back(extHyp);
              scrCompVec.push_back(scoreComponents);
            }
#ifdef THOT_STATS
            ++this->basePbTmStats.getTransCalls;
            this->basePbTmStats.transOptions += hypDataVec.size();
#endif
          }
        }
      }
    }
  }
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::expand_ver(const Hypothesis& hyp, std::vector<Hypothesis>& hypVec,
                                                    std::vector<std::vector<Score>>& scrCompVec)
{
  std::vector<std::pair<PositionIndex, PositionIndex>> gaps;
  std::vector<WordIndex> s_;
  Hypothesis extHyp;
  std::vector<HypDataType> hypDataVec;
  std::vector<Score> scoreComponents;

  hypVec.clear();
  scrCompVec.clear();

  // Extract gaps
  extract_gaps(hyp, gaps);

  // Generate new hypotheses completing the gaps
  for (unsigned int k = 0; k < gaps.size(); ++k)
  {
    unsigned int gap_length = gaps[k].second - gaps[k].first + 1;
    for (unsigned int x = 0; x < gap_length; ++x)
    {
      s_.clear();
      if (x <= this->pbTransModelPars.U) // x should be lower than U, which is the maximum
                                         // number of words that can be jUmped
      {
        for (unsigned int y = x; y < gap_length; ++y)
        {
          unsigned int segmRightMostj = gaps[k].first + y;
          unsigned int segmLeftMostj = gaps[k].first + x;
          // Verify that the source phrase length does not exceed
          // the limit
          if ((segmRightMostj - segmLeftMostj) + 1 > this->pbTransModelPars.A)
            break;
          // Obtain hypothesis data vector
          getHypDataVecForGapVer(hyp, segmLeftMostj, segmRightMostj, hypDataVec, this->pbTransModelPars.W);
          if (hypDataVec.size() != 0)
          {
            for (unsigned int i = 0; i < hypDataVec.size(); ++i)
            {
              this->incrScore(hyp, hypDataVec[i], extHyp, scoreComponents);
              hypVec.push_back(extHyp);
              scrCompVec.push_back(scoreComponents);
            }
#ifdef THOT_STATS
            ++this->basePbTmStats.getTransCalls;
            this->basePbTmStats.transOptions += hypDataVec.size();
#endif
          }
        }
      }
    }
  }
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::expand_prefix(const Hypothesis& hyp, std::vector<Hypothesis>& hypVec,
                                                       std::vector<std::vector<Score>>& scrCompVec)
{
  std::vector<std::pair<PositionIndex, PositionIndex>> gaps;
  std::vector<WordIndex> s_;
  Hypothesis extHyp;
  std::vector<HypDataType> hypDataVec;
  std::vector<Score> scoreComponents;

  hypVec.clear();
  scrCompVec.clear();

  // Extract gaps
  extract_gaps(hyp, gaps);

  // Generate new hypotheses completing the gaps
  for (unsigned int k = 0; k < gaps.size(); ++k)
  {
    unsigned int gap_length = gaps[k].second - gaps[k].first + 1;
    for (unsigned int x = 0; x < gap_length; ++x)
    {
      s_.clear();
      if (x <= this->pbTransModelPars.U) // x should be lower than U, which is the maximum
                                         // number of words that can be jUmped
      {
        for (unsigned int y = x; y < gap_length; ++y)
        {
          unsigned int segmRightMostj = gaps[k].first + y;
          unsigned int segmLeftMostj = gaps[k].first + x;
          // Verify that the source phrase length does not exceed
          // the limit
          if ((segmRightMostj - segmLeftMostj) + 1 > this->pbTransModelPars.A)
            break;
          // Obtain hypothesis data vector
          getHypDataVecForGapPref(hyp, segmLeftMostj, segmRightMostj, hypDataVec, this->pbTransModelPars.W);
          if (hypDataVec.size() != 0)
          {
            for (unsigned int i = 0; i < hypDataVec.size(); ++i)
            {
              this->incrScore(hyp, hypDataVec[i], extHyp, scoreComponents);
              hypVec.push_back(extHyp);
              scrCompVec.push_back(scoreComponents);
            }
#ifdef THOT_STATS
            ++this->basePbTmStats.getTransCalls;
            this->basePbTmStats.transOptions += hypDataVec.size();
#endif
          }
        }
      }
    }
  }
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::extract_gaps(const Hypothesis& hyp,
                                                      std::vector<std::pair<PositionIndex, PositionIndex>>& gaps)
{
  extract_gaps(hyp.getKey(), gaps);
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::extract_gaps(const Bitset<MAX_SENTENCE_LENGTH_ALLOWED>& hypKey,
                                                      std::vector<std::pair<PositionIndex, PositionIndex>>& gaps)
{
  // Extract all uncovered gaps
  std::pair<PositionIndex, PositionIndex> gap;
  unsigned int srcSentLen = this->numberOfUncoveredSrcWordsHypData(this->nullHypothesisHypData());
  unsigned int j;

  // Extract gaps
  gaps.clear();
  bool crossing_a_gap = false;

  for (j = 1; j <= srcSentLen; ++j)
  {
    if (crossing_a_gap == false && hypKey.test(j) == 0)
    {
      crossing_a_gap = true;
      gap.first = j;
    }

    if (crossing_a_gap == true && hypKey.test(j) == 1)
    {
      crossing_a_gap = false;
      gap.second = j - 1;
      gaps.push_back(gap);
    }
  }
  if (crossing_a_gap == true)
  {
    gap.second = j - 1;
    gaps.push_back(gap);
  }
}

template <class HYPOTHESIS>
unsigned int _phraseBasedTransModel<HYPOTHESIS>::get_num_gaps(const Bitset<MAX_SENTENCE_LENGTH_ALLOWED>& hypKey)
{
  // Count all uncovered gaps
  unsigned int result = 0;
  unsigned int j;
  bool crossing_a_gap;
  unsigned int srcSentLen;
  HypDataType nullHypData = this->nullHypothesisHypData();

  srcSentLen = this->numberOfUncoveredSrcWordsHypData(nullHypData);

  // count gaps
  crossing_a_gap = false;

  for (j = 1; j <= srcSentLen; ++j)
  {
    if (crossing_a_gap == false && hypKey.test(j) == 0)
    {
      crossing_a_gap = true;
    }

    if (crossing_a_gap == true && hypKey.test(j) == 1)
    {
      crossing_a_gap = false;
      ++result;
    }
  }
  if (crossing_a_gap == true)
  {
    ++result;
  }
  return result;
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::getHypDataVecForGap(const Hypothesis& hyp, PositionIndex srcLeft,
                                                             PositionIndex srcRight,
                                                             std::vector<HypDataType>& hypDataTypeVec, float N)
{
  NbestTableNode<PhraseTransTableNodeData> ttNode;
  NbestTableNode<PhraseTransTableNodeData>::iterator ttNodeIter;
  HypDataType hypData = hyp.getData();
  HypDataType newHypData;

  hypDataTypeVec.clear();

  // Obtain translations for gap
  getTransForHypUncovGap(hyp, srcLeft, srcRight, ttNode, N);

  if (this->verbosity >= 2)
  {
    std::cerr << "  trying to cover from src. pos. " << srcLeft << " to " << srcRight << "; ";
    std::cerr << "Filtered " << ttNode.size() << " translations" << std::endl;
  }

  // Generate hypothesis data for translations
  for (ttNodeIter = ttNode.begin(); ttNodeIter != ttNode.end(); ++ttNodeIter)
  {
    if (this->verbosity >= 3)
    {
      std::cerr << "   ";
      for (unsigned int i = srcLeft; i <= srcRight; ++i)
        std::cerr << this->pbtmInputVars.srcSentVec[i - 1] << " ";
      std::cerr << "||| ";
      for (unsigned int i = 0; i < ttNodeIter->second.size(); ++i)
        std::cerr << this->wordIndexToTrgString(ttNodeIter->second[i]) << " ";
      std::cerr << "||| " << ttNodeIter->first << std::endl;
    }

    newHypData = hypData;
    extendHypDataIdx(srcLeft, srcRight, ttNodeIter->second, newHypData);
    hypDataTypeVec.push_back(newHypData);
  }

  // Return boolean value
  if (hypDataTypeVec.empty())
    return false;
  else
    return true;
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::getHypDataVecForGapRef(const Hypothesis& hyp, PositionIndex srcLeft,
                                                                PositionIndex srcRight,
                                                                std::vector<HypDataType>& hypDataTypeVec, float N)
{
  NbestTableNode<PhraseTransTableNodeData> ttNode;
  NbestTableNode<PhraseTransTableNodeData>::iterator ttNodeIter;
  HypDataType hypData = hyp.getData();
  HypDataType newHypData;

  hypDataTypeVec.clear();

  getTransForHypUncovGapRef(hyp, srcLeft, srcRight, ttNode, N);

  if (this->verbosity >= 2)
  {
    std::cerr << "  trying to cover from src. pos. " << srcLeft << " to " << srcRight << "; ";
    std::cerr << "Filtered " << ttNode.size() << " translations" << std::endl;
  }

  for (ttNodeIter = ttNode.begin(); ttNodeIter != ttNode.end(); ++ttNodeIter)
  {
    if (this->verbosity >= 3)
    {
      std::cerr << "   ";
      for (unsigned int i = srcLeft; i <= srcRight; ++i)
        std::cerr << this->pbtmInputVars.srcSentVec[i - 1] << " ";
      std::cerr << "||| ";
      for (unsigned int i = 0; i < ttNodeIter->second.size(); ++i)
        std::cerr << this->wordIndexToTrgString(ttNodeIter->second[i]) << " ";
      std::cerr << "||| " << ttNodeIter->first << std::endl;
    }

    newHypData = hypData;
    extendHypDataIdx(srcLeft, srcRight, ttNodeIter->second, newHypData);
    bool equal;
    if (hypDataTransIsPrefixOfTargetRef(newHypData, equal))
    {
      if ((this->isCompleteHypData(newHypData) && equal) || !this->isCompleteHypData(newHypData))
        hypDataTypeVec.push_back(newHypData);
    }
  }
  if (hypDataTypeVec.empty())
    return false;
  else
    return true;
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::getHypDataVecForGapVer(const Hypothesis& hyp, PositionIndex srcLeft,
                                                                PositionIndex srcRight,
                                                                std::vector<HypDataType>& hypDataTypeVec, float N)
{
  NbestTableNode<PhraseTransTableNodeData> ttNode;
  NbestTableNode<PhraseTransTableNodeData>::iterator ttNodeIter;
  HypDataType hypData = hyp.getData();
  HypDataType newHypData;

  hypDataTypeVec.clear();

  getTransForHypUncovGapVer(hyp, srcLeft, srcRight, ttNode, N);

  if (this->verbosity >= 2)
  {
    std::cerr << "  trying to cover from src. pos. " << srcLeft << " to " << srcRight << "; ";
    std::cerr << "Filtered " << ttNode.size() << " translations" << std::endl;
  }

  for (ttNodeIter = ttNode.begin(); ttNodeIter != ttNode.end(); ++ttNodeIter)
  {
    if (this->verbosity >= 3)
    {
      std::cerr << "   ";
      for (unsigned int i = srcLeft; i <= srcRight; ++i)
        std::cerr << this->pbtmInputVars.srcSentVec[i - 1] << " ";
      std::cerr << "||| ";
      for (unsigned int i = 0; i < ttNodeIter->second.size(); ++i)
        std::cerr << this->wordIndexToTrgString(ttNodeIter->second[i]) << " ";
      std::cerr << "||| " << ttNodeIter->first << std::endl;
    }

    newHypData = hypData;
    extendHypDataIdx(srcLeft, srcRight, ttNodeIter->second, newHypData);
    bool equal;
    if (hypDataTransIsPrefixOfTargetRef(newHypData, equal))
    {
      if ((this->isCompleteHypData(newHypData) && equal) || !this->isCompleteHypData(newHypData))
        hypDataTypeVec.push_back(newHypData);
    }
  }
  if (hypDataTypeVec.empty())
    return false;
  else
    return true;
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::getHypDataVecForGapPref(const Hypothesis& hyp, PositionIndex srcLeft,
                                                                 PositionIndex srcRight,
                                                                 std::vector<HypDataType>& hypDataTypeVec, float N)
{
  NbestTableNode<PhraseTransTableNodeData> ttNode;
  NbestTableNode<PhraseTransTableNodeData>::iterator ttNodeIter;
  HypDataType hypData = hyp.getData();
  HypDataType newHypData;

  hypDataTypeVec.clear();

  getTransForHypUncovGapPref(hyp, srcLeft, srcRight, ttNode, N);

  if (this->verbosity >= 2)
  {
    std::cerr << "  trying to cover from src. pos. " << srcLeft << " to " << srcRight << "; ";
    std::cerr << "Filtered " << ttNode.size() << " translations" << std::endl;
  }

  for (ttNodeIter = ttNode.begin(); ttNodeIter != ttNode.end(); ++ttNodeIter)
  {
    if (this->verbosity >= 3)
    {
      std::cerr << "   ";
      for (unsigned int i = srcLeft; i <= srcRight; ++i)
        std::cerr << this->pbtmInputVars.srcSentVec[i - 1] << " ";
      std::cerr << "||| ";
      for (unsigned int i = 0; i < ttNodeIter->second.size(); ++i)
        std::cerr << this->wordIndexToTrgString(ttNodeIter->second[i]) << " ";
      std::cerr << "||| " << ttNodeIter->first << std::endl;
    }

    newHypData = hypData;
    extendHypDataIdx(srcLeft, srcRight, ttNodeIter->second, newHypData);
    hypDataTypeVec.push_back(newHypData);
  }
  if (hypDataTypeVec.empty())
    return false;
  else
    return true;
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::getTransForHypUncovGap(const Hypothesis& /*hyp*/, PositionIndex srcLeft,
                                                                PositionIndex srcRight,
                                                                NbestTableNode<PhraseTransTableNodeData>& nbt, float N)
{
  // Check if gap is affected by translation constraints
  if (this->transMetadata->srcPhrAffectedByConstraint(std::make_pair(srcLeft, srcRight)))
  {
    // Obtain constrained target translation for gap (if any)
    std::vector<std::string> trgWordVec = this->transMetadata->getTransForSrcPhr(std::make_pair(srcLeft, srcRight));
    if (trgWordVec.size() > 0)
    {
      // Convert string vector to WordIndex vector
      std::vector<WordIndex> trgWiVec;
      for (unsigned int i = 0; i < trgWordVec.size(); ++i)
      {
        WordIndex w = stringToTrgWordIndex(trgWordVec[i]);
        trgWiVec.push_back(w);
      }

      // Insert translation into n-best table
      nbt.clear();
      nbt.insert(0, trgWiVec);
      return true;
    }
    else
    {
      // No constrained target translation was found
      nbt.clear();
      return false;
    }
  }
  else
  {
    // The gap to be covered is not affected by translation constraints

    // Check if source phrase has only one word and this word has
    // been marked as an unseen word
    if (srcLeft == srcRight && unseenSrcWord(pbtmInputVars.srcSentVec[srcLeft - 1]))
    {
      std::vector<WordIndex> unkWordVec;
      unkWordVec.push_back(UNK_WORD);
      nbt.clear();
      nbt.insert(0, unkWordVec);
      return false;
    }
    else
    {
      // search translations for s in translation table
      NbestTableNode<PhraseTransTableNodeData>* transTableNodePtr;
      std::vector<WordIndex> s_;

      for (unsigned int i = srcLeft; i <= srcRight; ++i)
      {
        s_.push_back(pbtmInputVars.nsrcSentIdVec[i]);
      }

      transTableNodePtr = nbTransCacheData.cPhrNbestTransTable.getTranslationsForKey(std::make_pair(srcLeft, srcRight));
      if (transTableNodePtr != NULL)
      {
        // translation present in the cache translation table
        nbt = *transTableNodePtr;
        if (nbt.size() == 0)
          return false;
        else
          return true;
      }
      else
      {
        getNbestTransFor_s_(s_, nbt, N);
        nbTransCacheData.cPhrNbestTransTable.insertEntry(std::make_pair(srcLeft, srcRight), nbt);
        if (nbt.size() == 0)
          return false;
        else
          return true;
      }
    }
  }
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::getTransForHypUncovGapRef(const Hypothesis& hyp, PositionIndex srcLeft,
                                                                   PositionIndex srcRight,
                                                                   NbestTableNode<PhraseTransTableNodeData>& nbt,
                                                                   float N)
{
  std::vector<WordIndex> s_;
  std::vector<WordIndex> t_;
  std::vector<WordIndex> ntarget;

  // Obtain source phrase
  for (unsigned int i = srcLeft; i <= srcRight; ++i)
  {
    s_.push_back(pbtmInputVars.nsrcSentIdVec[i]);
  }

  // Obtain length limits for target phrase
  unsigned int minTrgSize = 0;
  if (s_.size() > this->pbTransModelPars.E)
    minTrgSize = s_.size() - this->pbTransModelPars.E;
  unsigned int maxTrgSize = s_.size() + this->pbTransModelPars.E;

  ntarget = hyp.getPartialTrans();

  nbt.clear();
  if (ntarget.size() > pbtmInputVars.nrefSentIdVec.size())
    return false;
  if (this->numberOfUncoveredSrcWords(hyp) - (srcRight - srcLeft + 1) > 0)
  {
    // This is not the last gap to be covered
    NbestTableNode<PhraseTransTableNodeData>* transTableNodePtr;
    PhrNbestTransTableRefKey pNbtRefKey;

    pNbtRefKey.srcLeft = srcLeft;
    pNbtRefKey.srcRight = srcRight;
    pNbtRefKey.ntrgSize = ntarget.size();
    // The number of gaps to be covered AFTER covering
    // s_{srcLeft}...s_{srcRight} is obtained to ensure that the
    // resulting hypotheses have at least as many gaps as reference
    // words to add
    if (this->pbTransModelPars.U == 0)
      pNbtRefKey.numGaps = 1;
    else
    {
      Bitset<MAX_SENTENCE_LENGTH_ALLOWED> key = hyp.getKey();
      for (unsigned int i = srcLeft; i <= srcRight; ++i)
        key.set(i);
      pNbtRefKey.numGaps = this->get_num_gaps(key);
    }

    // Search the required translations in the cache translation
    // table

    transTableNodePtr = nbTransCacheData.cPhrNbestTransTableRef.getTranslationsForKey(pNbtRefKey);
    if (transTableNodePtr != NULL)
    { // translations present in the cache translation table
      nbt = *transTableNodePtr;
    }
    else
    { // translations not present in the cache translation table
      for (PositionIndex i = ntarget.size(); i < pbtmInputVars.nrefSentIdVec.size() - pNbtRefKey.numGaps; ++i)
      {
        t_.push_back(pbtmInputVars.nrefSentIdVec[i]);
        if (t_.size() >= minTrgSize && t_.size() <= maxTrgSize)
        {
          Score scr = nbestTransScoreCached(s_, t_);
          nbt.insert(scr, t_);
        }
      }
      // Prune the list
      if (N >= 1)
        while (nbt.size() > (unsigned int)N)
          nbt.removeLastElement();
      else
      {
        Score bscr = nbt.getScoreOfBestElem();
        nbt.pruneGivenThreshold(bscr + (double)log(N));
      }
      // Store the list in cPhrNbestTransTableRef
      nbTransCacheData.cPhrNbestTransTableRef.insertEntry(pNbtRefKey, nbt);
    }
  }
  else
  {
    // The last gap will be covered
    for (PositionIndex i = ntarget.size(); i < pbtmInputVars.nrefSentIdVec.size(); ++i)
      t_.push_back(pbtmInputVars.nrefSentIdVec[i]);
    if (t_.size() >= minTrgSize && t_.size() <= maxTrgSize)
    {
      Score scr = nbestTransScoreCached(s_, t_);
      nbt.insert(scr, t_);
    }
  }
  if (nbt.size() == 0)
    return false;
  else
    return true;
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::getTransForHypUncovGapVer(const Hypothesis& hyp, PositionIndex srcLeft,
                                                                   PositionIndex srcRight,
                                                                   NbestTableNode<PhraseTransTableNodeData>& nbt,
                                                                   float N)
{
  return getTransForHypUncovGap(hyp, srcLeft, srcRight, nbt, N);
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::getTransForHypUncovGapPref(const Hypothesis& hyp, PositionIndex srcLeft,
                                                                    PositionIndex srcRight,
                                                                    NbestTableNode<PhraseTransTableNodeData>& nbt,
                                                                    float N)
{
  unsigned int ntrgSize = hyp.getPartialTrans().size();
  // Check if the prefix has been generated
  if (ntrgSize < pbtmInputVars.nprefSentIdVec.size())
  {
    // The prefix has not been generated
    NbestTableNode<PhraseTransTableNodeData>* transTableNodePtr;
    PhrNbestTransTablePrefKey pNbtPrefKey;

    pNbtPrefKey.srcLeft = srcLeft;
    pNbtPrefKey.srcRight = srcRight;
    pNbtPrefKey.ntrgSize = ntrgSize;
    if (this->numberOfUncoveredSrcWords(hyp) - (srcRight - srcLeft + 1) > 0)
      pNbtPrefKey.lastGap = false;
    else
      pNbtPrefKey.lastGap = true;

    // Search the required translations in the cache translation
    // table
    transTableNodePtr = nbTransCacheData.cPhrNbestTransTablePref.getTranslationsForKey(pNbtPrefKey);
    if (transTableNodePtr != NULL)
    { // translations present in the cache translation table
      nbt = *transTableNodePtr;
    }
    else
    {
      // Obtain list
      transUncovGapPrefNoGen(hyp, srcLeft, srcRight, nbt);

      // Prune the list
      if (N >= 1)
        while (nbt.size() > (unsigned int)N)
          nbt.removeLastElement();
      else
      {
        Score bscr = nbt.getScoreOfBestElem();
        nbt.pruneGivenThreshold(bscr + (double)log(N));
      }
      // Store the list in cPhrNbestTransTablePref
      nbTransCacheData.cPhrNbestTransTablePref.insertEntry(pNbtPrefKey, nbt);
    }
    if (nbt.size() == 0)
      return false;
    else
      return true;
  }
  else
  {
    // The prefix has been completely generated, the nbest list
    // is obtained as if no prefix was given
    return getTransForHypUncovGap(hyp, srcLeft, srcRight, nbt, N);
  }
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::transUncovGapPrefNoGen(const Hypothesis& hyp, PositionIndex srcLeft,
                                                                PositionIndex srcRight,
                                                                NbestTableNode<PhraseTransTableNodeData>& nbt)
{
  std::vector<WordIndex> s_;

  // Obtain source phrase
  nbt.clear();
  for (unsigned int i = srcLeft; i <= srcRight; ++i)
  {
    s_.push_back(pbtmInputVars.nsrcSentIdVec[i]);
  }
  // Obtain length limits for target phrase
  unsigned int minTrgSize = 0;
  if (s_.size() > this->pbTransModelPars.E)
    minTrgSize = s_.size() - this->pbTransModelPars.E;
  unsigned int maxTrgSize = s_.size() + this->pbTransModelPars.E;

  unsigned int ntrgSize = hyp.getPartialTrans().size();

  // Check if we are covering the last gap of the hypothesis
  if (this->numberOfUncoveredSrcWords(hyp) - (srcRight - srcLeft + 1) > 0)
  {
    // This is not the last gap to be covered.

    // Add translations with length in characters greater than the
    // prefix length.
    genListOfTransLongerThanPref(s_, ntrgSize, nbt);

    // Add translations with length lower than the prefix length.
    std::vector<WordIndex> t_;
    if (pbtmInputVars.nprefSentIdVec.size() > 1)
    {
      for (PositionIndex i = ntrgSize; i < pbtmInputVars.nprefSentIdVec.size() - 1; ++i)
      {
        t_.push_back(pbtmInputVars.nprefSentIdVec[i]);
        if (t_.size() >= minTrgSize && t_.size() <= maxTrgSize)
        {
          Score scr = nbestTransScoreCached(s_, t_);
          nbt.insert(scr, t_);
        }
      }
    }
  }
  else
  {
    // This is the last gap to be covered.

    // Add translations with length in characters greater than the
    // prefix length.
    genListOfTransLongerThanPref(s_, ntrgSize, nbt);
  }

  // Insert the remaining prefix itself in nbt
  std::vector<WordIndex> remainingPref;
  for (unsigned int i = ntrgSize; i < pbtmInputVars.nprefSentIdVec.size(); ++i)
    remainingPref.push_back(pbtmInputVars.nprefSentIdVec[i]);
  nbt.insert(nbestTransScoreLastCached(s_, remainingPref), remainingPref);
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::getTransForInvPbModel(const std::vector<WordIndex>& s_,
                                                               std::set<std::vector<WordIndex>>& transSet)
{
  // Obtain translation options vector for model
  BasePhraseModel::SrcTableNode srctn;
  bool ret = this->phraseModelInfo->invPhraseModel->getTransFor_t_(s_, srctn);

  // Create translation options data structure
  transSet.clear();
  for (BasePhraseModel::SrcTableNode::iterator iter = srctn.begin(); iter != srctn.end(); ++iter)
  {
    // Add new entry
    transSet.insert(iter->first);
  }
  return ret;
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::genListOfTransLongerThanPref(std::vector<WordIndex> s_, unsigned int ntrgSize,
                                                                      NbestTableNode<PhraseTransTableNodeData>& nbt)
{
  std::vector<WordIndex> remainingPref;

  // clear nbt
  nbt.clear();

  // Store the remaining prefix to be generated in remainingPref
  for (unsigned int i = ntrgSize; i < pbtmInputVars.nprefSentIdVec.size(); ++i)
    remainingPref.push_back(pbtmInputVars.nprefSentIdVec[i]);

  // Obtain translations for source segment s_
  std::set<std::vector<WordIndex>> transSet;
  getTransForInvPbModel(s_, transSet);
  for (std::set<std::vector<WordIndex>>::iterator transSetIter = transSet.begin(); transSetIter != transSet.end();
       ++transSetIter)
  {
    // Filter those translations whose length in words is
    // greater or equal than the remaining prefix length
    if (transSetIter->size() >= remainingPref.size())
    {
      // Filter those translations having "remainingPref"
      // as prefix
      bool equal;
      if (trgWordVecIsPrefix(remainingPref, pbtmInputVars.lastCharOfPrefIsBlank, pbtmInputVars.prefSentVec.back(),
                             *transSetIter, equal))
      {
        // Filter translations not exactly equal to "remainingPref"
        if (!equal)
        {
          Score scr = nbestTransScoreLastCached(s_, *transSetIter);
          nbt.insert(scr, *transSetIter);
        }
      }
    }
  }
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::trgWordVecIsPrefix(const std::vector<WordIndex>& wiVec1,
                                                            bool lastWiVec1WordIsComplete,
                                                            const std::string& lastWiVec1Word,
                                                            const std::vector<WordIndex>& wiVec2, bool& equal)
{
  equal = false;

  // returns true if target word vector wiVec1 is a prefix of wiVec2
  if (wiVec1.size() > wiVec2.size())
    return false;

  for (unsigned int i = 0; i < wiVec1.size(); ++i)
  {
    if (wiVec1[i] != wiVec2[i])
    {
      if (i == wiVec1.size() - 1 && !lastWiVec1WordIsComplete)
      {
        if (!StrProcUtils::isPrefix(lastWiVec1Word, wordIndexToTrgString(wiVec2[i])))
          return false;
      }
      else
        return false;
    }
  }

  if (wiVec1.size() == wiVec2.size() && lastWiVec1Word == wordIndexToTrgString(wiVec2.back()))
  {
    equal = true;
  }

  return true;
}

template <class HYPOTHESIS>
bool _phraseBasedTransModel<HYPOTHESIS>::getNbestTransFor_s_(std::vector<WordIndex> s_,
                                                             NbestTableNode<PhraseTransTableNodeData>& nbt, float N)
{
  BasePhraseModel::SrcTableNode srctn;
  BasePhraseModel::SrcTableNode::iterator srctnIter;
  bool ret;

  // Obtain the whole list of translations
  nbt.clear();
  std::set<std::vector<WordIndex>> transSet;
  ret = getTransForInvPbModel(s_, transSet);
  if (!ret)
    return false;
  else
  {
    Score scr;

    // This loop may become a bottleneck if the number of translation
    // options is high
    for (std::set<std::vector<WordIndex>>::iterator transSetIter = transSet.begin(); transSetIter != transSet.end();
         ++transSetIter)
    {
      scr = nbestTransScoreCached(s_, *transSetIter);
      nbt.insert(scr, *transSetIter);
    }
  }
  // Prune the list depending on the value of N
  // retrieve translations from table
  if (N >= 1)
    while (nbt.size() > (unsigned int)N)
      nbt.removeLastElement();
  else
  {
    Score bscr = nbt.getScoreOfBestElem();
    nbt.pruneGivenThreshold(bscr + (double)log(N));
  }
  return true;
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::nbestTransScoreCached(const std::vector<WordIndex>& s_,
                                                                const std::vector<WordIndex>& t_)
{
  PhrasePairCacheTable::iterator ppctIter;
  ppctIter = nbTransCacheData.cnbestTransScore.find(std::make_pair(s_, t_));
  if (ppctIter != nbTransCacheData.cnbestTransScore.end())
  {
    // Score was previously stored in the cache table
    return ppctIter->second;
  }
  else
  {
    // Score is not stored in the cache table
    Score scr = nbestTransScore(s_, t_);
    nbTransCacheData.cnbestTransScore[std::make_pair(s_, t_)] = scr;
    return scr;
  }
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::nbestTransScoreLastCached(const std::vector<WordIndex>& s_,
                                                                    const std::vector<WordIndex>& t_)
{
  PhrasePairCacheTable::iterator ppctIter;
  ppctIter = nbTransCacheData.cnbestTransScoreLast.find(std::make_pair(s_, t_));
  if (ppctIter != nbTransCacheData.cnbestTransScoreLast.end())
  {
    // Score was previously stored in the cache table
    return ppctIter->second;
  }
  else
  {
    // Score is not stored in the cache table
    Score scr = nbestTransScoreLast(s_, t_);
    nbTransCacheData.cnbestTransScoreLast[std::make_pair(s_, t_)] = scr;
    return scr;
  }
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::addHeuristicToHyp(Hypothesis& hyp)
{
  hyp.addHeuristic(calcHeuristicScore(hyp));
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::subtractHeuristicToHyp(Hypothesis& hyp)
{
  hyp.subtractHeuristic(calcHeuristicScore(hyp));
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::setHeuristic(unsigned int _heuristicId)
{
  heuristicId = _heuristicId;
}

template <class HYPOTHESIS>
unsigned int _phraseBasedTransModel<HYPOTHESIS>::getHeuristic() const
{
  return heuristicId;
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::calcHeuristicScore(const Hypothesis& hyp)
{
  Score score = 0;

  if (state == MODEL_TRANSREF_STATE)
  {
    // translation with reference
    score += calcRefLmHeurScore(hyp);
  }
  if (state == MODEL_TRANSPREFIX_STATE)
  {
    // translation with prefix
    score += calcPrefLmHeurScore(hyp);
  }

  switch (heuristicId)
  {
  case NO_HEURISTIC:
    break;
  case LOCAL_T_HEURISTIC:
    score += heuristicLocalt(hyp);
    break;
  case LOCAL_TD_HEURISTIC:
    score += heuristicLocaltd(hyp);
    break;
  }
  return score;
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::printHyp(const Hypothesis& hyp, std::ostream& outS, int verbose)
{
  // Obtain target string vector
  std::vector<std::string> trgStrVec = trgIndexVectorToStrVector(hyp.getPartialTrans());

  // Print score
  outS << "Score: " << hyp.getScore() << " ; ";

  // Print weights
  this->printWeights(outS);
  outS << " ; ";

  // Obtain score components
  Hypothesis auxHyp;
  std::vector<Score> scoreComponents;
  HypDataType hypDataType = hyp.getData();
  this->incrScore(this->nullHypothesis(), hypDataType, auxHyp, scoreComponents);

  // Print score components
  for (unsigned int i = 0; i < scoreComponents.size(); ++i)
    outS << scoreComponents[i] << " ";

  // Print score + heuristic
  addHeuristicToHyp(auxHyp);
  outS << "; Score+heur: " << auxHyp.getScore() << " ";

  // Print warning if the alignment is not complete
  if (!this->isComplete(hyp))
    outS << "; Incomplete_alignment!";

  // Obtain phrase alignment
  SourceSegmentation sourceSegmentation;
  std::vector<PositionIndex> targetSegmentCuts;
  std::vector<std::pair<PositionIndex, PositionIndex>> amatrix;
  this->aligMatrix(hyp, amatrix);
  this->getPhraseAlignment(amatrix, sourceSegmentation, targetSegmentCuts);

  // Print target translation
  outS << " | ";
  for (unsigned int i = 1; i < trgStrVec.size(); ++i)
    outS << trgStrVec[i] << " ";

  // Print source segmentation
  outS << "| Source Segmentation: ";
  for (unsigned int k = 0; k < sourceSegmentation.size(); k++)
  {
    std::string constrType = this->transMetadata->getConstraintTypeForSrcPhr(sourceSegmentation[k]);
    outS << "( " << sourceSegmentation[k].first << " , " << sourceSegmentation[k].second << " ; type: ";
    if (constrType.empty())
      outS << "RegularPhrTableEntry";
    else
      outS << constrType;
    outS << " ) ";
  }

  // Print target segmentation
  outS << "| Target Segmentation: ";
  for (unsigned int j = 0; j < targetSegmentCuts.size(); j++)
    outS << targetSegmentCuts[j] << " ";

  // Print hypothesis key
  outS << "| hypkey: " << hyp.getKey() << " ";

  // Print hypothesis equivalence class
  outS << "| hypEqClass: " << hyp.getEqClass() << std::endl;

  if (verbose)
  {
    unsigned int numSteps = sourceSegmentation.size() - 1;
    outS << "----------------------------------------------" << std::endl;
    outS << "Score components for previous expansion steps:" << std::endl;
    auxHyp = hyp;
    while (this->obtainPredecessor(auxHyp))
    {
      scoreComponents = scoreCompsForHyp(auxHyp);
      outS << "Step " << numSteps << " : ";
      for (unsigned int i = 0; i < scoreComponents.size(); ++i)
      {
        outS << scoreComponents[i] << " ";
      }
      outS << std::endl;
      --numSteps;
    }
    outS << "----------------------------------------------" << std::endl;
  }
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::extendHypData(PositionIndex srcLeft, PositionIndex srcRight,
                                                       const std::vector<std::string>& trgPhrase, HypDataType& hypd)
{
  std::vector<WordIndex> trgPhraseIdx;

  for (unsigned int i = 0; i < trgPhrase.size(); ++i)
    trgPhraseIdx.push_back(stringToTrgWordIndex(trgPhrase[i]));
  extendHypDataIdx(srcLeft, srcRight, trgPhraseIdx, hypd);
}

template <class HYPOTHESIS>
std::vector<std::string> _phraseBasedTransModel<HYPOTHESIS>::getTransInPlainTextVec(const Hypothesis& hyp) const
{
  std::set<PositionIndex> unknownWords;
  return getTransInPlainTextVec(hyp, unknownWords);
}

template <class HYPOTHESIS>
std::vector<std::string> _phraseBasedTransModel<HYPOTHESIS>::getTransInPlainTextVec(
    const Hypothesis& hyp, std::set<PositionIndex>& unknownWords) const
{
  unknownWords.clear();

  switch (state)
  {
  case MODEL_TRANS_STATE:
    return getTransInPlainTextVecTs(hyp, unknownWords);
  case MODEL_TRANSPREFIX_STATE:
    return getTransInPlainTextVecTps(hyp, unknownWords);
  case MODEL_TRANSREF_STATE:
    return getTransInPlainTextVecTrs(hyp, unknownWords);
  case MODEL_TRANSVER_STATE:
    return getTransInPlainTextVecTvs(hyp, unknownWords);
  default:
    std::vector<std::string> strVec;
    return strVec;
  }
}

template <class HYPOTHESIS>
std::vector<std::string> _phraseBasedTransModel<HYPOTHESIS>::getTransInPlainTextVecTs(
    const Hypothesis& hyp, std::set<PositionIndex>& unknownWords) const
{
  std::vector<WordIndex> nvwi;
  std::vector<WordIndex> vwi;

  // Obtain vector of WordIndex
  nvwi = hyp.getPartialTrans();
  for (unsigned int i = 1; i < nvwi.size(); ++i)
  {
    vwi.push_back(nvwi[i]);
  }
  // Obtain vector of strings
  std::vector<std::string> trgVecStr = trgIndexVectorToStrVector(vwi);

  // Treat unknown words contained in trgVecStr. Model is being used
  // to translate a sentence

  // Replace unknown words affected by constraints

  // Iterate over constraints
  std::set<std::pair<PositionIndex, PositionIndex>> srcPhrSet = this->transMetadata->getConstrainedSrcPhrases();
  std::set<std::pair<PositionIndex, PositionIndex>>::const_iterator const_iter;
  for (const_iter = srcPhrSet.begin(); const_iter != srcPhrSet.end(); ++const_iter)
  {
    // Obtain target translation for constraint
    std::vector<std::string> trgPhr = this->transMetadata->getTransForSrcPhr(*const_iter);

    // Find first aligned target word
    for (unsigned int i = 0; i < trgVecStr.size(); ++i)
    {
      if (hyp.areAligned(const_iter->first, i + 1))
      {
        for (unsigned int k = 0; k < trgPhr.size(); ++k)
        {
          if (trgVecStr[i + k] == UNK_WORD_STR)
            trgVecStr[i + k] = trgPhr[k];
        }
        // Replace unknown words and finish
        break;
      }
    }
  }

  // Replace unknown words not affected by constraints
  for (unsigned int i = 0; i < trgVecStr.size(); ++i)
  {
    if (trgVecStr[i] == UNK_WORD_STR)
    {
      unknownWords.insert(i);
      // Find source word aligned with unknown word
      for (unsigned int j = 0; j < pbtmInputVars.srcSentVec.size(); ++j)
      {
        if (hyp.areAligned(j + 1, i + 1))
        {
          trgVecStr[i] = pbtmInputVars.srcSentVec[j];
          break;
        }
      }
    }
  }
  return trgVecStr;
}

template <class HYPOTHESIS>
std::vector<std::string> _phraseBasedTransModel<HYPOTHESIS>::getTransInPlainTextVecTps(
    const Hypothesis& hyp, std::set<PositionIndex>& unknownWords) const
{
  std::vector<WordIndex> nvwi;
  std::vector<WordIndex> vwi;

  // Obtain vector of WordIndex
  nvwi = hyp.getPartialTrans();
  for (unsigned int i = 1; i < nvwi.size(); ++i)
  {
    vwi.push_back(nvwi[i]);
  }
  // Obtain vector of strings
  std::vector<std::string> trgVecStr = trgIndexVectorToStrVector(vwi);

  // Treat unknown words contained in trgVecStr. Model is being used
  // to translate a sentence given a prefix

  // Replace unknown words from trgVecStr
  for (unsigned int i = 0; i < trgVecStr.size(); ++i)
  {
    if (trgVecStr[i] == UNK_WORD_STR)
    {
      unknownWords.insert(i);
      if (i < pbtmInputVars.prefSentVec.size())
      {
        // Unknown word must be replaced by a prefix word
        trgVecStr[i] = pbtmInputVars.prefSentVec[i];
      }
      else
      {
        // Find source word aligned with unknown word
        for (unsigned int j = 0; j < pbtmInputVars.srcSentVec.size(); ++j)
        {
          if (hyp.areAligned(j + 1, i + 1))
          {
            trgVecStr[i] = pbtmInputVars.srcSentVec[j];
            break;
          }
        }
      }
    }
  }
  return trgVecStr;
}

template <class HYPOTHESIS>
std::vector<std::string> _phraseBasedTransModel<HYPOTHESIS>::getTransInPlainTextVecTrs(
    const Hypothesis& hyp, std::set<PositionIndex>& unknownWords) const
{
  std::vector<WordIndex> nvwi;
  std::vector<WordIndex> vwi;

  // Obtain vector of WordIndex
  nvwi = hyp.getPartialTrans();
  for (unsigned int i = 1; i < nvwi.size(); ++i)
  {
    vwi.push_back(nvwi[i]);
  }
  // Obtain vector of strings
  std::vector<std::string> trgVecStr = trgIndexVectorToStrVector(vwi);

  // Treat unknown words contained in trgVecStr. Model is being used
  // to generate a reference.
  for (unsigned int i = 0; i < trgVecStr.size(); ++i)
  {
    if (i < pbtmInputVars.refSentVec.size())
    {
      trgVecStr[i] = pbtmInputVars.refSentVec[i];
      unknownWords.insert(i);
    }
  }
  return trgVecStr;
}

template <class HYPOTHESIS>
std::vector<std::string> _phraseBasedTransModel<HYPOTHESIS>::getTransInPlainTextVecTvs(
    const Hypothesis& hyp, std::set<PositionIndex>& unknownWords) const
{
  std::vector<WordIndex> nvwi;
  std::vector<WordIndex> vwi;

  // Obtain vector of WordIndex
  nvwi = hyp.getPartialTrans();
  for (unsigned int i = 1; i < nvwi.size(); ++i)
  {
    vwi.push_back(nvwi[i]);
  }
  // Obtain vector of strings
  std::vector<std::string> trgVecStr = trgIndexVectorToStrVector(vwi);

  // Treat unknown words contained in trgVecStr. Model is being used
  // to verify model coverage
  for (unsigned int i = 0; i < trgVecStr.size(); ++i)
  {
    if (i < pbtmInputVars.refSentVec.size())
    {
      trgVecStr[i] = pbtmInputVars.refSentVec[i];
      unknownWords.insert(i);
    }
  }
  return trgVecStr;
}

template <class HYPOTHESIS>
void _phraseBasedTransModel<HYPOTHESIS>::getUnweightedComps(const std::vector<Score>& scrComps,
                                                            std::vector<Score>& unweightedScrComps)
{
  // Obtain weights
  std::vector<std::pair<std::string, float>> compWeights;
  this->getWeights(compWeights);

  // Generate unweighted component vector
  unweightedScrComps.clear();
  for (unsigned int i = 0; i < compWeights.size(); ++i)
  {
    if (compWeights[i].second != 0)
      unweightedScrComps.push_back(scrComps[i] / compWeights[i].second);
    else
      unweightedScrComps.push_back(0);
  }
}

template <class HYPOTHESIS>
std::vector<Score> _phraseBasedTransModel<HYPOTHESIS>::scoreCompsForHyp(const Hypothesis& hyp)
{
  HypDataType hypDataType;
  Hypothesis auxHyp;
  std::vector<Score> scoreComponents;

  // Obtain score components
  hypDataType = hyp.getData();
  this->incrScore(this->nullHypothesis(), hypDataType, auxHyp, scoreComponents);

  return scoreComponents;
}

template <class HYPOTHESIS>
Score _phraseBasedTransModel<HYPOTHESIS>::getScoreForHyp(const Hypothesis& hyp)
{
  return hyp.getScore();
}

template <class HYPOTHESIS>
_phraseBasedTransModel<HYPOTHESIS>::~_phraseBasedTransModel()
{
}
