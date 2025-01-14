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

#include "stack_dec/SwModelInfo.h"
#include "stack_dec/_phraseBasedTransModel.h"

#include <memory>

typedef std::pair<unsigned int, unsigned int> uint_pair;

/**
 * @brief The _phrSwTransModel class is a base class for deriving
 * translation models that combine phrase based models and single-word
 * models.
 */

template <class HYPOTHESIS>
class _phrSwTransModel : public _phraseBasedTransModel<HYPOTHESIS>
{
public:
  typedef typename _phraseBasedTransModel<HYPOTHESIS>::Hypothesis Hypothesis;
  typedef typename _phraseBasedTransModel<HYPOTHESIS>::HypScoreInfo HypScoreInfo;
  typedef typename _phraseBasedTransModel<HYPOTHESIS>::HypDataType HypDataType;

  // class functions

  // Constructor
  _phrSwTransModel();

  // Link sw model information
  void setSwModelInfo(SwModelInfo* swmInfo);
  SwModelInfo* getSwModelInfo();

  // Init alignment model
  bool loadAligModel(const char* prefixFileName, int verbose = 0);

  // Print models
  bool printAligModel(std::string printPrefix);

  void clear();

  // Actions to be executed before the translation
  void pre_trans_actions(std::string srcsent);
  void pre_trans_actions_ref(std::string srcsent, std::string refsent);
  void pre_trans_actions_ver(std::string srcsent, std::string refsent);
  void pre_trans_actions_prefix(std::string srcsent, std::string prefix);

  ////// Hypotheses-related functions

  // Destructor
  ~_phrSwTransModel();

protected:
  // SwModelInfo pointer
  std::shared_ptr<SwModelInfo> swModelInfo;

  // Precalculated lgProbs
  std::vector<std::vector<Prob>> sumSentLenProbVec;
  // sumSentLenProbVec[slen][tlen] stores p(sl=slen|tl<=tlen)
  std::vector<std::vector<uint_pair>> lenRangeForGaps;

  // Cached scores
  std::vector<PhrasePairCacheTable> cSwmScoreVec;
  std::vector<PhrasePairCacheTable> cInvSwmScoreVec;

  Score invSwScore(int idx, const std::vector<WordIndex>& s_, const std::vector<WordIndex>& t_);
  Score swScore(int idx, const std::vector<WordIndex>& s_, const std::vector<WordIndex>& t_);
  LgProb swLgProb(int idx, const std::vector<WordIndex>& s_, const std::vector<WordIndex>& t_);
  LgProb invSwLgProb(int idx, const std::vector<WordIndex>& s_, const std::vector<WordIndex>& t_);

  // Sentence length scoring functions
  Score sentLenScore(unsigned int slen, unsigned int tlen);
  Score sentLenScoreForPartialHyp(Bitset<MAX_SENTENCE_LENGTH_ALLOWED> key, unsigned int curr_tlen);
  Prob sumSentLenProb(unsigned int slen, unsigned int tlen);
  // Returns p(sl=slen|tl<=tlen)
  Score sumSentLenScoreRange(unsigned int slen, uint_pair range);
  // Returns p(sl=slen|tl\in range)
  uint_pair obtainLengthRangeForGaps(const Bitset<MAX_SENTENCE_LENGTH_ALLOWED>& hypKey);
  void initLenRangeForGapsVec(int maxSrcPhraseLength);

  // Functions related to pre_trans_actions
  void clearTempVars();

  // Vocabulary-related functions
  WordIndex addSrcSymbolToAligModels(std::string s);
  WordIndex addTrgSymbolToAligModels(std::string t);
  void updateAligModelsSrcVoc(const std::vector<std::string>& sStrVec);
  void updateAligModelsTrgVoc(const std::vector<std::string>& tStrVec);

  // Helper functions to load models
  bool loadMultipleSwModelsPrefix(const char* prefixFileName, int verbose);
};

template <class HYPOTHESIS>
_phrSwTransModel<HYPOTHESIS>::_phrSwTransModel() : _phraseBasedTransModel<HYPOTHESIS>()
{
  PhrasePairCacheTable phrasePairCacheTable;
  cSwmScoreVec.push_back(phrasePairCacheTable);
  cInvSwmScoreVec.push_back(phrasePairCacheTable);
}

template <class HYPOTHESIS>
void _phrSwTransModel<HYPOTHESIS>::setSwModelInfo(SwModelInfo* swmInfo)
{
  swModelInfo.reset(swmInfo);
}

template <class HYPOTHESIS>
SwModelInfo* _phrSwTransModel<HYPOTHESIS>::getSwModelInfo()
{
  return swModelInfo.get();
}

template <class HYPOTHESIS>
bool _phrSwTransModel<HYPOTHESIS>::loadMultipleSwModelsPrefix(const char* prefixFileName, int verbose)
{
  swModelInfo->swModelPars.readTablePrefixVec.clear();
  swModelInfo->invSwModelPars.readTablePrefixVec.clear();
  cSwmScoreVec.clear();
  cInvSwmScoreVec.clear();

  // sw model (The direct model is the one with the prefix _invswm)
  std::string invReadTablePrefix = prefixFileName;
  invReadTablePrefix += "_invswm";
  swModelInfo->swModelPars.readTablePrefixVec.push_back(invReadTablePrefix);
  bool ret = swModelInfo->swAligModels[0]->load(invReadTablePrefix.c_str(), verbose);
  if (ret == THOT_ERROR)
    return THOT_ERROR;

  // Inverse sw model
  std::string readTablePrefix = prefixFileName;
  readTablePrefix += "_swm";
  swModelInfo->invSwModelPars.readTablePrefixVec.push_back(readTablePrefix);
  ret = swModelInfo->invSwAligModels[0]->load(readTablePrefix.c_str(), verbose);
  if (ret == THOT_ERROR)
    return THOT_ERROR;

  // Grow caching data structures for swms
  PhrasePairCacheTable phrasePairCacheTable;
  cSwmScoreVec.push_back(phrasePairCacheTable);
  cInvSwmScoreVec.push_back(phrasePairCacheTable);

  return THOT_OK;
}

template <class HYPOTHESIS>
bool _phrSwTransModel<HYPOTHESIS>::loadAligModel(const char* prefixFileName, int verbose /*=0*/)
{
  unsigned int ret;

  // Load phrase model vocabularies
  this->phraseModelInfo->phraseModelPars.srcTrainVocabFileName = prefixFileName;
  this->phraseModelInfo->phraseModelPars.srcTrainVocabFileName += "_swm.svcb";
  this->phraseModelInfo->phraseModelPars.trgTrainVocabFileName = prefixFileName;
  this->phraseModelInfo->phraseModelPars.trgTrainVocabFileName += "_swm.tvcb";

  ret = this->phraseModelInfo->invPhraseModel->loadSrcVocab(
      this->phraseModelInfo->phraseModelPars.srcTrainVocabFileName.c_str(), verbose);
  if (ret == THOT_ERROR)
    return THOT_ERROR;

  ret = this->phraseModelInfo->invPhraseModel->loadTrgVocab(
      this->phraseModelInfo->phraseModelPars.trgTrainVocabFileName.c_str(), verbose);
  if (ret == THOT_ERROR)
    return THOT_ERROR;

  // Load phrase model
  this->phraseModelInfo->phraseModelPars.readTablePrefix = prefixFileName;
  if (this->phraseModelInfo->invPhraseModel->load(prefixFileName, verbose) != 0)
    return THOT_ERROR;

  // Instantiate weight vectors for phrase model
  this->instantiateWeightVectors();

  // Load multiple sw models
  ret = loadMultipleSwModelsPrefix(prefixFileName, verbose);
  if (ret == THOT_ERROR)
    return THOT_ERROR;

  return THOT_OK;
}

template <class HYPOTHESIS>
bool _phrSwTransModel<HYPOTHESIS>::printAligModel(std::string printPrefix)
{
  // Print phrase model
  bool ret = _phraseBasedTransModel<HYPOTHESIS>::printAligModel(printPrefix);
  if (ret == THOT_ERROR)
    return THOT_ERROR;

  // TBD: handle multiple sw models
  // Print inverse sw model
  std::string invSwModelPrefix = printPrefix + "_swm";
  ret = swModelInfo->invSwAligModels[0]->print(invSwModelPrefix.c_str());
  if (ret == THOT_ERROR)
    return THOT_ERROR;

  // Print direct sw model
  std::string swModelPrefix = printPrefix + "_invswm";
  ret = swModelInfo->swAligModels[0]->print(swModelPrefix.c_str());
  if (ret == THOT_ERROR)
    return THOT_ERROR;

  return THOT_OK;
}

template <class HYPOTHESIS>
void _phrSwTransModel<HYPOTHESIS>::clear()
{
  _phraseBasedTransModel<HYPOTHESIS>::clear();
  for (unsigned int i = 0; i < swModelInfo->swAligModels.size(); ++i)
    swModelInfo->swAligModels[i]->clear();
  for (unsigned int i = 0; i < swModelInfo->invSwAligModels.size(); ++i)
    swModelInfo->invSwAligModels[i]->clear();
  sumSentLenProbVec.clear();
  lenRangeForGaps.clear();
  for (unsigned int i = 0; i < cSwmScoreVec.size(); ++i)
    cSwmScoreVec[i].clear();
  for (unsigned int i = 0; i < cInvSwmScoreVec.size(); ++i)
    cInvSwmScoreVec[i].clear();
}

template <class HYPOTHESIS>
Score _phrSwTransModel<HYPOTHESIS>::invSwScore(int idx, const std::vector<WordIndex>& s_,
                                               const std::vector<WordIndex>& t_)
{
  return swModelInfo->invSwModelPars.swWeight * (double)invSwLgProb(idx, s_, t_);
}

template <class HYPOTHESIS>
Score _phrSwTransModel<HYPOTHESIS>::swScore(int idx, const std::vector<WordIndex>& s_, const std::vector<WordIndex>& t_)
{
  return swModelInfo->swModelPars.swWeight * (double)swLgProb(idx, s_, t_);
}

template <class HYPOTHESIS>
LgProb _phrSwTransModel<HYPOTHESIS>::swLgProb(int idx, const std::vector<WordIndex>& s_,
                                              const std::vector<WordIndex>& t_)
{
  PhrasePairCacheTable::iterator ppctIter;
  ppctIter = cSwmScoreVec[idx].find(std::make_pair(s_, t_));
  if (ppctIter != cSwmScoreVec[idx].end())
  {
    // Score was previously stored in the cache table
    return ppctIter->second;
  }
  else
  {
    // Score is not stored in the cache table
    LgProb lp = swModelInfo->swAligModels[idx]->computePhraseSumLogProb(s_, t_);
    cSwmScoreVec[idx][std::make_pair(s_, t_)] = lp;
    return lp;
  }
}

template <class HYPOTHESIS>
LgProb _phrSwTransModel<HYPOTHESIS>::invSwLgProb(int idx, const std::vector<WordIndex>& s_,
                                                 const std::vector<WordIndex>& t_)
{
  PhrasePairCacheTable::iterator ppctIter;
  ppctIter = cInvSwmScoreVec[idx].find(std::make_pair(s_, t_));
  if (ppctIter != cInvSwmScoreVec[idx].end())
  {
    // Score was previously stored in the cache table
    return ppctIter->second;
  }
  else
  {
    // Score is not stored in the cache table
    LgProb lp = swModelInfo->invSwAligModels[idx]->computePhraseSumLogProb(t_, s_);
    cInvSwmScoreVec[idx][std::make_pair(s_, t_)] = lp;
    return lp;
  }
}

template <class HYPOTHESIS>
Score _phrSwTransModel<HYPOTHESIS>::sentLenScore(unsigned int slen, unsigned int tlen)
{
  return swModelInfo->invSwModelPars.lenWeight
       * (double)swModelInfo->invSwAligModels[0]->sentenceLengthLogProb(tlen, slen);
}

template <class HYPOTHESIS>
Score _phrSwTransModel<HYPOTHESIS>::sentLenScoreForPartialHyp(Bitset<MAX_SENTENCE_LENGTH_ALLOWED> key,
                                                              unsigned int curr_tlen)
{
  if (this->state == MODEL_TRANS_STATE)
  {
    // The model is being used to translate a sentence
    uint_pair range = obtainLengthRangeForGaps(key);
    range.first += curr_tlen;
    range.second += curr_tlen;
    return sumSentLenScoreRange(this->pbtmInputVars.srcSentVec.size(), range);
  }
  else
  {
    if (this->state == MODEL_TRANSREF_STATE)
    {
      // The model is being used to align a pair of sentences
      uint_pair range;
      range.first = this->pbtmInputVars.refSentVec.size();
      range.second = this->pbtmInputVars.refSentVec.size();
      return sumSentLenScoreRange(this->pbtmInputVars.srcSentVec.size(), range);
    }
    else
    {
      // The model is being used to translate a sentence given a
      // prefix
      if (curr_tlen >= this->pbtmInputVars.prefSentVec.size())
      {
        // The prefix has been generated
        uint_pair range = obtainLengthRangeForGaps(key);
        range.first += curr_tlen;
        range.second += curr_tlen;
        return sumSentLenScoreRange(this->pbtmInputVars.srcSentVec.size(), range);
      }
      else
      {
        // The prefix has not been generated yet.  The predicted
        // sentence range is (length(prefix),MAX_SENTENCE_LENGTH_ALLOWED),
        // the prediction can be improved but the required code
        // could be complex.
        uint_pair range;
        range.first = this->pbtmInputVars.prefSentVec.size();
        range.second = MAX_SENTENCE_LENGTH_ALLOWED;
        return sumSentLenScoreRange(this->pbtmInputVars.srcSentVec.size(), range);
      }
    }
  }
}

template <class HYPOTHESIS>
Prob _phrSwTransModel<HYPOTHESIS>::sumSentLenProb(unsigned int slen, unsigned int tlen)
{
  // Reserve memory if necesary
  while (sumSentLenProbVec.size() <= slen)
  {
    std::vector<Prob> vp;
    sumSentLenProbVec.push_back(vp);
  }
  while (sumSentLenProbVec[slen].size() <= tlen)
    sumSentLenProbVec[slen].push_back(-1.0);

  // Check if the probability is already stored
  if ((double)sumSentLenProbVec[slen][tlen] >= 0.0)
  {
    return sumSentLenProbVec[slen][tlen];
  }
  else
  {
    // The probability has to be calculated
    Prob result;
    if (tlen == 0)
    {
      result = swModelInfo->invSwAligModels[0]->sentenceLengthProb(tlen, slen);
    }
    else
    {
      result = sumSentLenProb(slen, tlen - 1) + swModelInfo->invSwAligModels[0]->sentenceLengthProb(tlen, slen);
    }
    sumSentLenProbVec[slen][tlen] = result;
    return result;
  }
}

template <class HYPOTHESIS>
Score _phrSwTransModel<HYPOTHESIS>::sumSentLenScoreRange(unsigned int slen, uint_pair range)
{
  if (range.first != 0)
    return swModelInfo->invSwModelPars.lenWeight
         * log((double)(sumSentLenProb(slen, range.second) - sumSentLenProb(slen, range.first - 1)));
  else
    return swModelInfo->invSwModelPars.lenWeight * log((double)sumSentLenProb(slen, range.second));
}

template <class HYPOTHESIS>
uint_pair _phrSwTransModel<HYPOTHESIS>::obtainLengthRangeForGaps(const Bitset<MAX_SENTENCE_LENGTH_ALLOWED>& hypKey)
{
  unsigned int J;
  std::vector<std::pair<PositionIndex, PositionIndex>> gaps;
  uint_pair result;

  J = this->pbtmInputVars.srcSentVec.size();
  this->extract_gaps(hypKey, gaps);
  for (unsigned int i = 0; i < gaps.size(); ++i)
  {
    uint_pair rangeForGap;

    rangeForGap = lenRangeForGaps[gaps[i].second - 1][J - gaps[i].first];
    result.first += rangeForGap.first;
    result.second += rangeForGap.second;
  }
  return result;
}

template <class HYPOTHESIS>
void _phrSwTransModel<HYPOTHESIS>::initLenRangeForGapsVec(int maxSrcPhraseLength)
{
  if (this->verbosity >= 1)
  {
    std::cerr << "Obtaining table with length range for gaps..." << std::endl;
  }

  unsigned int J, segmRightMostj, segmLeftMostj;
  std::vector<uint_pair> row;
  NbestTableNode<PhraseTransTableNodeData> ttNode;
  NbestTableNode<PhraseTransTableNodeData>::iterator ttNodeIter;
  uint_pair target_uip;
  std::vector<WordIndex> s_;

  J = this->pbtmInputVars.nsrcSentIdVec.size() - 1;
  lenRangeForGaps.clear();
  // Initialize row vector
  for (unsigned int j = 0; j < J; ++j)
    row.push_back(std::make_pair(0, 0));
  // Insert rows into lenRangeForGaps
  for (unsigned int j = 0; j < J; ++j)
    lenRangeForGaps.push_back(row);

  // Fill the length range table
  for (unsigned int y = 0; y < J; ++y)
  {
    for (unsigned int x = J - y - 1; x < J; ++x)
    {
      // obtain phrase
      segmRightMostj = y;
      segmLeftMostj = J - x - 1;
      s_.clear();

      target_uip.first = MAX_SENTENCE_LENGTH_ALLOWED * 10;
      target_uip.second = 0;
      if ((segmRightMostj - segmLeftMostj) + 1 > (unsigned int)maxSrcPhraseLength)
      {
        ttNode.clear();
      }
      else
      {
        for (unsigned int j = segmLeftMostj; j <= segmRightMostj; ++j)
          s_.push_back(this->pbtmInputVars.nsrcSentIdVec[j + 1]);

        // obtain translations for s_
        this->getNbestTransFor_s_(s_, ttNode, this->pbTransModelPars.W);

        if (ttNode.size() != 0) // Obtain best p(s_|t_)
        {
          for (ttNodeIter = ttNode.begin(); ttNodeIter != ttNode.end(); ++ttNodeIter)
          {
            // Update range
            if (target_uip.first > ttNodeIter->second.size())
              target_uip.first = ttNodeIter->second.size();
            if (target_uip.second < ttNodeIter->second.size())
              target_uip.second = ttNodeIter->second.size();
          }
        }
        else
        {
          // Check if source word has been marked as unseen
          if (s_.size() == 1 && this->unseenSrcWord(this->pbtmInputVars.srcSentVec[segmLeftMostj]))
          {
            target_uip.first = 1;
            target_uip.second = 1;
          }
        }
      }

      // if phrase has only one word
      if (x == J - y - 1)
      {
        lenRangeForGaps[y][x] = target_uip;
      }
      else
      {
        // phrase has more than one word
        lenRangeForGaps[y][x] = target_uip;
        for (unsigned int z = J - x - 1; z < y; ++z)
        {
          uint_pair composition_uip;
          composition_uip.first = lenRangeForGaps[z][x].first + lenRangeForGaps[y][J - 2 - z].first;
          composition_uip.second = lenRangeForGaps[z][x].second + lenRangeForGaps[y][J - 2 - z].second;
          if (lenRangeForGaps[y][x].first > composition_uip.first)
            lenRangeForGaps[y][x].first = composition_uip.first;
          if (lenRangeForGaps[y][x].second < composition_uip.second)
            lenRangeForGaps[y][x].second = composition_uip.second;
        }
      }
    }
  }

  // Correct invalid values due to coverage problems
  for (unsigned int y = 0; y < J; ++y)
  {
    for (unsigned int x = J - y - 1; x < J; ++x)
    {
      if (lenRangeForGaps[y][x].first > lenRangeForGaps[y][x].second)
      {
        lenRangeForGaps[y][x].first = 0;
        lenRangeForGaps[y][x].second = 0;
      }
    }
  }
  // Print verbose mode information
  if (this->verbosity >= 1)
  {
    for (unsigned int y = 0; y < J; ++y)
    {
      for (unsigned int x = 0; x < J; ++x)
      {
        fprintf(stderr, "(%3d,%3d)", lenRangeForGaps[y][x].first, lenRangeForGaps[y][x].second);
      }
      std::cerr << std::endl;
    }
  }
}

template <class HYPOTHESIS>
void _phrSwTransModel<HYPOTHESIS>::clearTempVars()
{
  _phraseBasedTransModel<HYPOTHESIS>::clearTempVars();
  for (unsigned int i = 0; i < swModelInfo->swAligModels.size(); ++i)
    swModelInfo->swAligModels[i]->clearTempVars();
  for (unsigned int i = 0; i < swModelInfo->invSwAligModels.size(); ++i)
    swModelInfo->invSwAligModels[i]->clearTempVars();
  sumSentLenProbVec.clear();
  lenRangeForGaps.clear();
  for (unsigned int i = 0; i < cSwmScoreVec.size(); ++i)
    cSwmScoreVec[i].clear();
  for (unsigned int i = 0; i < cInvSwmScoreVec.size(); ++i)
    cInvSwmScoreVec[i].clear();
}

template <class HYPOTHESIS>
WordIndex _phrSwTransModel<HYPOTHESIS>::addSrcSymbolToAligModels(std::string s)
{
  WordIndex windex_ipbm = this->phraseModelInfo->invPhraseModel->addTrgSymbol(s);
  WordIndex windex_lex = swModelInfo->swAligModels[0]->addSrcSymbol(s);
  WordIndex windex_ilex = swModelInfo->invSwAligModels[0]->addTrgSymbol(s);
  if (windex_ipbm != windex_lex || windex_ipbm != windex_ilex)
  {
    std::cerr << "Warning! phrase-based model vocabularies are now different from lexical model vocabularies."
              << std::endl;
  }

  return windex_ipbm;
}

template <class HYPOTHESIS>
WordIndex _phrSwTransModel<HYPOTHESIS>::addTrgSymbolToAligModels(std::string t)
{
  WordIndex windex_ipbm = this->phraseModelInfo->invPhraseModel->addSrcSymbol(t);
  WordIndex windex_lex = swModelInfo->swAligModels[0]->addTrgSymbol(t);
  WordIndex windex_ilex = swModelInfo->invSwAligModels[0]->addSrcSymbol(t);
  if (windex_ipbm != windex_lex || windex_ipbm != windex_ilex)
  {
    std::cerr << "Warning! phrase-based model vocabularies are now different from lexical model vocabularies."
              << std::endl;
  }

  return windex_ipbm;
}

template <class HYPOTHESIS>
void _phrSwTransModel<HYPOTHESIS>::updateAligModelsSrcVoc(const std::vector<std::string>& sStrVec)
{
  for (unsigned int i = 0; i < sStrVec.size(); ++i)
  {
    addSrcSymbolToAligModels(sStrVec[i]);
  }
}

template <class HYPOTHESIS>
void _phrSwTransModel<HYPOTHESIS>::updateAligModelsTrgVoc(const std::vector<std::string>& tStrVec)
{
  for (unsigned int i = 0; i < tStrVec.size(); ++i)
  {
    addTrgSymbolToAligModels(tStrVec[i]);
  }
}

template <class HYPOTHESIS>
void _phrSwTransModel<HYPOTHESIS>::pre_trans_actions(std::string srcsent)
{
  _phraseBasedTransModel<HYPOTHESIS>::pre_trans_actions(srcsent);
  initLenRangeForGapsVec(this->pbTransModelPars.A);
}

template <class HYPOTHESIS>
void _phrSwTransModel<HYPOTHESIS>::pre_trans_actions_ref(std::string srcsent, std::string refsent)
{
  _phraseBasedTransModel<HYPOTHESIS>::pre_trans_actions_ref(srcsent, refsent);
  initLenRangeForGapsVec(this->pbTransModelPars.A);
}

template <class HYPOTHESIS>
void _phrSwTransModel<HYPOTHESIS>::pre_trans_actions_ver(std::string srcsent, std::string refsent)
{
  _phraseBasedTransModel<HYPOTHESIS>::pre_trans_actions_ver(srcsent, refsent);
  initLenRangeForGapsVec(this->pbTransModelPars.A);
}

template <class HYPOTHESIS>
void _phrSwTransModel<HYPOTHESIS>::pre_trans_actions_prefix(std::string srcsent, std::string prefix)
{
  _phraseBasedTransModel<HYPOTHESIS>::pre_trans_actions_prefix(srcsent, prefix);
  initLenRangeForGapsVec(this->pbTransModelPars.A);
}

template <class HYPOTHESIS>
_phrSwTransModel<HYPOTHESIS>::~_phrSwTransModel()
{
}
