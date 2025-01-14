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
 * @file WgProcessorForAnlp.h
 *
 * @brief Declares the WgProcessorForAnlp function, this class
 * implements a word-graph processor for assisted natural language
 * processing.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "error_correction/BaseWgProcessorForAnlp.h"
#include "nlp_common/StrProcUtils.h"
#include "nlp_common/ctimer.h"

#include <map>
#include <set>
#include <vector>

//--------------- Constants ------------------------------------------

//--------------- Functions ------------------------------------------

//--------------- Classes --------------------------------------------

//--------------- WgProcessorForAnlp template class

/**
 * @brief The WgProcessorForAnlp class implements a word-graph processor
 * for assisted natural language processing.
 */

template <class ECM_FOR_WG>
class WgProcessorForAnlp : public BaseWgProcessorForAnlp
{
public:
  // Constructor
  WgProcessorForAnlp();

  // Link word-graph with word-graph processor
  void link_wg(const WordGraph* _wg_ptr);

  // Link error correcting model for word-graph with the word-graph
  // processor
  bool link_ecm_wg(BaseErrorCorrectionModel* _ecm_wg_ptr);

  void set_wgw(float _wgWeight);
  // Set word-graph weight

  void set_ecmw(float _ecmWeight);
  // Set error correcting model weight

  NbestCorrections correct(std::string prefix, unsigned int n, const RejectedWordsSet& rejectedWords,
                           unsigned int verbose = 0);
  // Given a prefix, obtains a list of the
  // n-best corrections
  // IMPORTANT: the prefix should not be empty

  // clear() function
  void clear(void);

  // clearTempVars() function
  void clearTempVars(void);

  // print() function
  bool print(const char* filename) const;

protected:
  typedef typename ECM_FOR_WG::EcmScoreInfo EcmScoreInfo;
  typedef std::vector<EcmScoreInfo> EcmScrInfoForArc;
  typedef std::multimap<float, HypStateIndex, std::greater<float>> NbestHypStates;
  typedef std::pair<WordGraphArcId, unsigned int> HypSubStateIdx;
  typedef std::multimap<float, HypSubStateIdx, std::greater<float>> NbestHypSubStates;
  typedef std::set<HypStateIndex> StatesInvolvedInArcs;

  std::vector<std::string> previousPrefixVec;

  const WordGraph* wg_ptr;

  ECM_FOR_WG* ecm_wg_ptr;

  float wgWeight; // Weight assigned to word-graph scores

  float ecmWeight; // Weight assigned to error correcting model scores

  bool initVarsExecuted; // This variable is set to true if wg
                         // processor variables has been
                         // initialized for current word-graph

  std::vector<Score> restScores; // Rest scores for each state of the
                                 // word-graph

  std::vector<EcmScoreInfo> ecmScrInfoForState;
  // Ecm score info for each state

  std::vector<EcmScrInfoForArc> ecmScrInfoForArcVec;
  // Ecm score info for each arc

  std::vector<Score> wgScoreForState; // Best word-graph score for each
                                      // state

  std::vector<std::vector<Score>> bestScoresForState; // Best scores for each
                                                      // state

  std::vector<std::vector<WordGraphArcId>> bestPredsForState; // Best predecessors
                                                              // for each state

  StatesInvolvedInArcs statesInvolvedInArcs; // List of states involved in arcs

  // Auxiliary functions

  // Functions to initialize word-graph
  void initVars(unsigned int verbose = 0);
  void genListOfStatesInvolvedInArcs(StatesInvolvedInArcs& stInvInArcs) const;
  void updateSizeOfVars(const std::vector<std::string>& validProcPrefixVec);
  void initWgpInfoForArcs(unsigned int verbose = 0);
  void initWgpInfoForInitState(unsigned int verbose = 0);
  void initWgpInfoForArc(WordGraphArcId wgArcId, unsigned int verbose = 0);
  void initEcmScoreInfoForArc(WordGraphArcId wgArcId, unsigned int verbose = 0);

  // Functions to incrementally process the word-graph
  std::vector<std::string> getValidProcPrefixVec(const std::vector<std::string>& prefixVec);
  std::vector<std::string> getPrefixDiffVec(const std::vector<std::string>& validProcPrefixVec,
                                            const std::vector<std::string>& prefixVec);
  void procWgGivenPrefDiff(std::vector<std::string> prefixDiffVec, unsigned int verbose = 0);
  NbestHypStates obtainNbestHypStates(unsigned int n, const RejectedWordsSet& rejectedWords, unsigned int verbose = 0);
  // Given a prefix and a pair of weights, obtains a list of the n
  // states of the word-graph with best probability
  NbestHypSubStates obtainNbestHypSubStates(unsigned int n, const RejectedWordsSet& rejectedWords,
                                            unsigned int verbose = 0);
  // Given a prefix and a pair of weights, obtains a list of the n
  // substates of the words-graph with best probability
  bool wordSatisfiesRejWordConstraint(std::string word, const RejectedWordsSet& rejectedWords);
  void updateWgpInfoForInitState(const std::vector<std::string>& prefixDiffVec, unsigned int verbose = 0);
  // Auxiliar function of the obtainNbestHypStates() function, it
  // updates the information of the word-processor for the initial
  // state.
  void updateWgpInfoForArc(const std::vector<std::string>& prefixDiffVec, WordGraphArcId wgArcId,
                           unsigned int verbose = 0);
  // Auxiliar function of the obtainNbestHypStates() function, it
  // updates the information of the word-processor for a given state
  // and arc.
  void updateEcmScoreInfoForArc(const std::vector<std::string>& prefixDiffVec, WordGraphArcId wgArcId,
                                unsigned int verbose = 0);
  NbestCorrections obtainNbestCorrections(std::vector<std::string> prefixVec, unsigned int n,
                                          const RejectedWordsSet& rejectedWords, const NbestHypStates& nbestHypStates,
                                          const NbestHypSubStates& nbestHypSubStates, unsigned int verbose = 0);
  // Given a prefix and a list of n-best states, obtains a list of
  // the n-best corrections
  std::vector<std::string> obtainBestUncorrPrefHypState(unsigned int procPrefPos, HypStateIndex hypStateIndex,
                                                        std::vector<WordGraphArcId>& wgaidVec);
  std::vector<std::string> obtainBestUncorrPrefHypSubState(unsigned int procPrefPos, WordGraphArcId wgArcId,
                                                           unsigned int arcPos, std::vector<WordGraphArcId>& wgaidVec);
  std::vector<std::string> obtainCorrForHypState(std::vector<std::string> prefixVec, HypStateIndex hypStateIndex,
                                                 const RejectedWordsSet& rejectedWords, unsigned int verbose = 0);
  std::vector<std::string> obtainCorrForHypSubState(std::vector<std::string> prefixVec, HypSubStateIdx hypSubStateIdx,
                                                    unsigned int verbose = 0);
  void removeLastFromNbestHypStates(NbestHypStates& nbestHypStates);
  void removeLastFromNbestHypSubStates(NbestHypSubStates& nbestHypSubStates);
  void removeLastFromNbestCorrs(NbestCorrections& nbestCorrections);

  // Functions to update best scores
  void updateBestScoresForInitState(unsigned int verbose = 0);
  void updateBestScoresForState(WordGraphArcId wgArcId, unsigned int prefDiffSize, unsigned int verbose = 0);

  // print() function given an output stream
  void print(std::ostream& outS) const;
  void printInfoAboutScores(std::ostream& outS) const;

  // auxiliary funtions to print state information
  void printInfoForStates(std::ostream& outS) const;
  void printStateInfo(HypStateIndex idx, std::ostream& outS) const;

  // auxiliary funtions to print sub-state information
  void printInfoForSubStates(std::ostream& outS) const;
  void printSubStateInfo(WordGraphArcId wgArcId, unsigned int w, std::ostream& outS) const;
};

//--------------- WgProcessorForAnlp template class function definitions

//---------------------------------------
template <class ECM_FOR_WG>
WgProcessorForAnlp<ECM_FOR_WG>::WgProcessorForAnlp()
{
  wg_ptr = NULL;
  ecm_wg_ptr = NULL;
  initVarsExecuted = false;
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::link_wg(const WordGraph* _wg_ptr)
{
  // Link word-graph
  wg_ptr = _wg_ptr;

  // Clear word-graph processor data structures
  clear();
}

//---------------------------------------
template <class ECM_FOR_WG>
bool WgProcessorForAnlp<ECM_FOR_WG>::link_ecm_wg(BaseErrorCorrectionModel* _ecm_wg_ptr)
{
  // Link ecm for word-graphs
  ecm_wg_ptr = dynamic_cast<ECM_FOR_WG*>(_ecm_wg_ptr);
  if (ecm_wg_ptr)
    return true;
  else
    return false;
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::set_wgw(float _wgWeight)
{
  wgWeight = _wgWeight;
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::set_ecmw(float _ecmWeight)
{
  ecmWeight = _ecmWeight;
}

//---------------------------------------
template <class ECM_FOR_WG>
NbestCorrections WgProcessorForAnlp<ECM_FOR_WG>::correct(std::string prefix, unsigned int n,
                                                         const RejectedWordsSet& rejectedWords,
                                                         unsigned int verbose /*=0*/)
{
  // Check if word graph is uninitialized or empty
  if (wg_ptr == NULL || wg_ptr->empty())
  {
    // Word graph empty
    std::cerr << "Word-graph proccessor error: word-graph is empty!" << std::endl;
    NbestCorrections nbestCorrections;
    return nbestCorrections;
  }
  else
  {
    // Word graph is not empty

    // Check if wg processor variables need to be initialized
    if (!initVarsExecuted)
    {
      // Initialize variables
      // Get initial time
      if (verbose)
        std::cerr << "Initialize word-graph processor variables..." << std::endl;
      double total_time = 0, elapsed_ant, elapsed, ucpu, scpu;
      ctimer(&elapsed_ant, &ucpu, &scpu);

      initVars(verbose);

      // Get final time
      ctimer(&elapsed, &ucpu, &scpu);
      // Obtain total time
      total_time += elapsed - elapsed_ant;
      if (verbose)
        std::cerr << "done, processing time: " << total_time << " seconds" << std::endl;
    }

    // Obtain prefix vector
    std::vector<std::string> prefixVec = StrProcUtils::stringToStringVector(prefix);
    if (prefix[prefix.size() - 1] == ' ' && prefixVec.size() > 0)
    {
      prefixVec[prefixVec.size() - 1] += ' ';
    }

    if (verbose)
    {
      std::cerr << "Processing prefix:";
      for (unsigned int i = 0; i < prefixVec.size(); ++i)
        std::cerr << " " << prefixVec[i];
      std::cerr << "|" << std::endl;
    }

    // Obtain portion of the processed prefix vector which is valid
    // in the current interaction and update size of variables if
    // necessary
    if (verbose)
      std::cerr << "Obtaining valid portion of the processed prefix vector..." << std::endl;
    std::vector<std::string> validProcPrefixVec = getValidProcPrefixVec(prefixVec);
    if (verbose)
    {
      std::cerr << " - Previously processed prefix:";
      for (unsigned int i = 0; i < previousPrefixVec.size(); ++i)
        std::cerr << " " << previousPrefixVec[i];
      std::cerr << "|" << std::endl;

      std::cerr << " - Valid portion of the processed prefix vector:";
      for (unsigned int i = 0; i < validProcPrefixVec.size(); ++i)
        std::cerr << " " << validProcPrefixVec[i];
      std::cerr << "|" << std::endl;
    }
    updateSizeOfVars(validProcPrefixVec);

    // Obtain difference between prefixVec and valid portion of the
    // processed prefix
    if (verbose)
      std::cerr << "Obtaining difference between prefix and valid portion..." << std::endl;
    std::vector<std::string> prefixDiffVec = getPrefixDiffVec(validProcPrefixVec, prefixVec);
    if (verbose)
    {
      std::cerr << " - Difference between prefix and valid portion:";
      for (unsigned int i = 0; i < prefixDiffVec.size(); ++i)
        std::cerr << " " << prefixDiffVec[i];
      std::cerr << "|" << std::endl;
    }

    // Process word-graph given prefix difference
    // Get initial time
    if (verbose)
      std::cerr << "Processing word-graph given prefix difference..." << std::endl;
    double total_time = 0, elapsed_ant, elapsed, ucpu, scpu;
    ctimer(&elapsed_ant, &ucpu, &scpu);

    procWgGivenPrefDiff(prefixDiffVec, verbose);

    // Get final time
    ctimer(&elapsed, &ucpu, &scpu);
    // Obtain total time
    total_time += elapsed - elapsed_ant;
    if (verbose)
      std::cerr << "done, processing time: " << total_time << " seconds" << std::endl;

    // Obtain n-best list of hypothesis states
    if (verbose)
      std::cerr << "Obtaining n-best list of hypothesis states..." << std::endl;
    NbestHypStates nbestHypStates = obtainNbestHypStates(n, rejectedWords, verbose);

    // Obtain n-best list of hypothesis sub-states
    if (verbose)
      std::cerr << "Obtain n-best list of hypothesis sub-states..." << std::endl;
    NbestHypSubStates nbestHypSubStates = obtainNbestHypSubStates(n, rejectedWords, verbose);

    // Obtain n-best list of corrections from n-best list of
    // hypothesis states and sub-states
    if (verbose)
      std::cerr << "Obtaining n-best corrections..." << std::endl;
    NbestCorrections nbestCorrections =
        obtainNbestCorrections(prefixVec, n, rejectedWords, nbestHypStates, nbestHypSubStates, verbose);

    // Update previousPrefixVec
    previousPrefixVec = prefixVec;

    // Return result
    return nbestCorrections;
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::initWgpInfoForArcs(unsigned int verbose /*=0*/)
{
  // Obtain arc range
  std::pair<WordGraphArcId, WordGraphArcId> arcIdxRange = wg_ptr->getArcIndexRange();

  // Iterate over the arcs of the word-graph (IMPORTANT: it is
  // assumed that the arcs of the word-graph are topologically
  // ordered)
  for (WordGraphArcId aIdx = arcIdxRange.first; aIdx <= arcIdxRange.second; ++aIdx)
  {
    // Initialize info for arc
    if (!wg_ptr->arcPruned(aIdx))
      initWgpInfoForArc(aIdx, verbose);
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::initWgpInfoForInitState(unsigned int verbose /*=0*/)
{
  // Construct initial ecm score info object
  ecmScrInfoForState[INITIAL_STATE] = ecm_wg_ptr->constructInitEsi();

  // Update best scores for initial state
  updateBestScoresForInitState(verbose);
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::initWgpInfoForArc(WordGraphArcId wgArcId, unsigned int verbose /*=0*/)
{
  // Init ecm score info for each word of the arc
  initEcmScoreInfoForArc(wgArcId, verbose);

  // Update best scores for state
  updateBestScoresForState(wgArcId, 0, verbose);
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::initEcmScoreInfoForArc(WordGraphArcId wgArcId, unsigned int /*verbose*/ /*=0*/)
{
  // Obtain arc from arc identifier
  WordGraphArc wgArc = wg_ptr->wordGraphArcId2WordGraphArc(wgArcId);

  // Obtain predecessor state index
  HypStateIndex idx = wgArc.predStateIndex;

  // Init ecm score info for each word of the arc
  EcmScoreInfo prevEsi = ecmScrInfoForState[idx];

  // Grow new esi for arc if necessary
  while (ecmScrInfoForArcVec[wgArcId].size() < wgArc.words.size())
  {
    EcmScoreInfo esi;
    ecmScrInfoForArcVec[wgArcId].push_back(esi);
  }
  for (unsigned int w = 0; w < wgArc.words.size(); ++w)
  {
    ecmScrInfoForArcVec[wgArcId][w] = ecm_wg_ptr->constructEsi(prevEsi, wgArc.words[w]);
    prevEsi = ecmScrInfoForArcVec[wgArcId][w];
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
std::vector<std::string> WgProcessorForAnlp<ECM_FOR_WG>::getValidProcPrefixVec(
    const std::vector<std::string>& prefixVec)
{
  std::vector<std::string> result;

  for (unsigned int i = 0; i < previousPrefixVec.size(); ++i)
  {
    if (i >= prefixVec.size())
      break;
    if (previousPrefixVec[i] == prefixVec[i])
      result.push_back(previousPrefixVec[i]);
  }
  return result;
}

//---------------------------------------
template <class ECM_FOR_WG>
std::vector<std::string> WgProcessorForAnlp<ECM_FOR_WG>::getPrefixDiffVec(
    const std::vector<std::string>& validProcPrefixVec, const std::vector<std::string>& prefixVec)
{
  std::vector<std::string> prefixDiffVec;

  if (validProcPrefixVec.size() == 0)
  {
    prefixDiffVec = prefixVec;
  }
  else
  {
    for (unsigned int i = validProcPrefixVec.size(); i < prefixVec.size(); ++i)
      prefixDiffVec.push_back(prefixVec[i]);
  }
  return prefixDiffVec;
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::procWgGivenPrefDiff(std::vector<std::string> prefixDiffVec,
                                                         unsigned int verbose /*=0*/)
{
  // Declare and initialize variables

  // Obtain arc range
  std::pair<WordGraphArcId, WordGraphArcId> arcIdxRange = wg_ptr->getArcIndexRange();

  // Process initial state
  if (prefixDiffVec.size() != 0)
  {
    updateWgpInfoForInitState(prefixDiffVec, verbose);
  }

  // Iterate over the arcs of the word-graph (IMPORTANT: it is
  // assumed that the arcs of the word-graph are topologically
  // ordered)
  if (verbose)
    std::cerr << "Arc id range: " << arcIdxRange.first << " " << arcIdxRange.second << std::endl;

  if (prefixDiffVec.size() != 0)
  {
    for (unsigned int aIdx = arcIdxRange.first; aIdx <= arcIdxRange.second; ++aIdx)
    {
      // Update info for arcs
      if (!wg_ptr->arcPruned(aIdx))
        updateWgpInfoForArc(prefixDiffVec, aIdx, verbose);
    }
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
typename WgProcessorForAnlp<ECM_FOR_WG>::NbestHypStates WgProcessorForAnlp<ECM_FOR_WG>::obtainNbestHypStates(
    unsigned int n, const RejectedWordsSet& rejectedWords, unsigned int /*verbose*/ /*=0*/)
{
  // nbestHypStates stores an ordered list of states
  NbestHypStates nbestHypStates;

  // Iterate over states involved in arcs
  StatesInvolvedInArcs::iterator iter;
  for (iter = statesInvolvedInArcs.begin(); iter != statesInvolvedInArcs.end(); ++iter)
  {
    HypStateIndex hsIdx = *iter;

    // Check if the state satisfies the constraints imposed by the
    // set of rejected words, calculate rest score for state.
    Score restScore = restScores[hsIdx];
    bool hypStateOk = true;
    if (!rejectedWords.empty())
    {
      // Obtain successors
      std::vector<WordGraphArc> wgArcs;
      wg_ptr->getArcsToSuccStates(hsIdx, wgArcs);

      // Find the best successor
      Score bestRestScoreForSucc = SMALL_SCORE;
      for (unsigned int i = 0; i < wgArcs.size(); ++i)
      {
        // Check that the constraint is satisfied
        bool wordSatisfiesConstraint = wordSatisfiesRejWordConstraint(wgArcs[i].words[0], rejectedWords);
        if (wordSatisfiesConstraint)
        {
          Score restScoreForArc = wgArcs[i].arcScore + restScores[wgArcs[i].succStateIndex];
          if (bestRestScoreForSucc < restScoreForArc)
            bestRestScoreForSucc = restScoreForArc;
        }
      }
      if (bestRestScoreForSucc == SMALL_SCORE)
        hypStateOk = false;
      else
        restScore = bestRestScoreForSucc;
    }

    if (hypStateOk)
    {
      // The state satisfies the constraints imposed by
      // the set of rejected words

      // Insert state in the n-best list
      Score score = bestScoresForState[hsIdx].back() + (wgWeight * restScore);
      nbestHypStates.insert(std::make_pair(score, hsIdx));

      // Prune list if necessary
      if (nbestHypStates.size() > n)
        removeLastFromNbestHypStates(nbestHypStates);
    }
  }

  // Return list of n-best states
  return nbestHypStates;
}

//---------------------------------------
template <class ECM_FOR_WG>
typename WgProcessorForAnlp<ECM_FOR_WG>::NbestHypSubStates WgProcessorForAnlp<ECM_FOR_WG>::obtainNbestHypSubStates(
    unsigned int n, const RejectedWordsSet& rejectedWords, unsigned int /*verbose*/ /*=0*/)
{
  // nbestHypStates stores an ordered list of sub-states
  NbestHypSubStates nbestHypSubStates;

  // Obtain arc range
  std::pair<WordGraphArcId, WordGraphArcId> arcIdxRange = wg_ptr->getArcIndexRange();

  // Process sub-states
  for (WordGraphArcId wgArcId = arcIdxRange.first; wgArcId <= arcIdxRange.second; ++wgArcId)
  {
    if (!wg_ptr->arcPruned(wgArcId))
    {
      // Insert sub-state in the n-best list
      // Obtain arc from arc id.
      WordGraphArc wgArc = wg_ptr->wordGraphArcId2WordGraphArc(wgArcId);
      // Iterate over the words of the arc
      if (wgArc.words.size() > 1)
      {
        // NOTE: the last word of the arc wgArc constitutes a sub-state
        // equivalent to wgArc.succStateIndex state

        // Obtain wg score for predecessor state
        Score wgScr = wgScoreForState[wgArc.predStateIndex];

        for (unsigned int w = 0; w < wgArc.words.size() - 1; ++w)
        {
          // Check that the sub-state satisfies the constraints
          // imposed by the set of rejected words
          bool subHypStateOk = true;
          if (!rejectedWords.empty())
          {
            bool wordSatisfiesConstraint = wordSatisfiesRejWordConstraint(wgArc.words[w + 1], rejectedWords);
            if (!wordSatisfiesConstraint)
              subHypStateOk = false;
          }
          if (subHypStateOk)
          {
            // The sub-state satisfies the constraints imposed by
            // the set of rejected words

            // Obtain ecm score vector for w'th word of current arc
            std::vector<Score> ecmScrVec = ecm_wg_ptr->obtainScrVecFromEsi(ecmScrInfoForArcVec[wgArcId][w]);
            // Calculate score of the sub-state
            Score score =
                wgWeight * wgScr + ecmWeight * ecmScrVec.back() + (wgWeight * restScores[wgArc.predStateIndex]);

            // Create sub-state object
            HypSubStateIdx hssIdx;
            hssIdx.first = wgArcId;
            hssIdx.second = w;
            // Insert sub-state in the n-best list
            nbestHypSubStates.insert(std::make_pair(score, hssIdx));

            // Prune list if necessary
            if (nbestHypSubStates.size() > n)
              removeLastFromNbestHypSubStates(nbestHypSubStates);
          }
        }
      }
    }
  }

  // Return n-best sub-state list
  return nbestHypSubStates;
}

//---------------------------------------
template <class ECM_FOR_WG>
bool WgProcessorForAnlp<ECM_FOR_WG>::wordSatisfiesRejWordConstraint(std::string word,
                                                                    const RejectedWordsSet& rejectedWords)
{
  RejectedWordsSet::const_iterator strSetIter;
  for (strSetIter = rejectedWords.begin(); strSetIter != rejectedWords.end(); ++strSetIter)
  {
    // Obtain accepted prefix and rejected suffix
    std::string accepted_prefix = strSetIter->first;
    std::string rejected_suffix = strSetIter->second;

    // Check if word is compatible with accepted prefix
    if (word.size() < accepted_prefix.size())
      return false;
    for (unsigned int i = 0; i < accepted_prefix.size(); ++i)
    {
      if (accepted_prefix[i] != word[i])
        return false;
    }

    // Check if word contains rejected suffix
    std::string word_suffix;
    for (unsigned int i = accepted_prefix.size(); i < word.size(); ++i)
      word_suffix += word[i];
    if (word_suffix == rejected_suffix)
      return false;
  }

  // word satisfies constraint
  return true;
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::updateWgpInfoForInitState(const std::vector<std::string>& prefixDiffVec,
                                                               unsigned int verbose /*=0*/)
{
  // Obtain initial Esi object
  EcmScoreInfo prevEsiInit = ecmScrInfoForState[INITIAL_STATE];

  // Extend initial ecm score info object
  ecm_wg_ptr->extendInitialEsi(prefixDiffVec, prevEsiInit, ecmScrInfoForState[INITIAL_STATE]);

  // Update best scores for initial state
  updateBestScoresForInitState(verbose);
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::updateWgpInfoForArc(const std::vector<std::string>& prefixDiffVec,
                                                         WordGraphArcId wgArcId, unsigned int verbose /*=0*/)
{
  // Update ecm score info for each word of the arc
  updateEcmScoreInfoForArc(prefixDiffVec, wgArcId, verbose);

  // Update best scores for state
  updateBestScoresForState(wgArcId, prefixDiffVec.size(), verbose);
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::updateEcmScoreInfoForArc(const std::vector<std::string>& prefixDiffVec,
                                                              WordGraphArcId wgArcId, unsigned int /*verbose*/ /*=0*/)
{
  // Obtain arc from arc identifier
  WordGraphArc wgArc = wg_ptr->wordGraphArcId2WordGraphArc(wgArcId);

  // Obtain predecessor state
  HypStateIndex idx = wgArc.predStateIndex;

  // Update ecm score info for each word of the arc
  EcmScoreInfo prevEsi = ecmScrInfoForState[idx];

  // Grow new esi for arc if necessary
  while (ecmScrInfoForArcVec[wgArcId].size() < wgArc.words.size())
  {
    EcmScoreInfo esi;
    ecmScrInfoForArcVec[wgArcId].push_back(esi);
  }

  for (unsigned int w = 0; w < wgArc.words.size(); ++w)
  {
    // Extend ecm score info
    ecm_wg_ptr->extendEsi(prefixDiffVec, prevEsi, wgArc.words[w], ecmScrInfoForArcVec[wgArcId][w]);
    prevEsi = ecmScrInfoForArcVec[wgArcId][w];
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::updateBestScoresForInitState(unsigned int /*verbose*/ /*=0*/)
{
  std::vector<Score> ecmScrVec = ecm_wg_ptr->obtainScrVecFromEsi(ecmScrInfoForState[INITIAL_STATE]);

  // Obtain wg score for initial state
  wgScoreForState[INITIAL_STATE] = wg_ptr->getInitialStateScore();

  // Update best scores and best predecessors for initial state
  // Grow both vectors for initial state if necessary
  bestScoresForState[INITIAL_STATE].clear();
  bestPredsForState[INITIAL_STATE].clear();
  while (bestScoresForState[INITIAL_STATE].size() < ecmScrVec.size())
  {
    bestScoresForState[INITIAL_STATE].push_back(SMALL_SCORE);
    bestPredsForState[INITIAL_STATE].push_back(INVALID_ARCID);
  }

  for (unsigned int i = 0; i < bestScoresForState[INITIAL_STATE].size(); ++i)
  {
    bestScoresForState[INITIAL_STATE][i] = (ecmWeight * ecmScrVec[i]) + (wgWeight * wgScoreForState[INITIAL_STATE]);
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::updateBestScoresForState(WordGraphArcId wgArcId, unsigned int prefDiffSize,
                                                              unsigned int /*verbose*/ /*=0*/)
{
  // Obtain arc from arc identifier
  WordGraphArc wgArc = wg_ptr->wordGraphArcId2WordGraphArc(wgArcId);

  // Retrieve predecessor and successor states
  HypStateIndex predIdx = wgArc.predStateIndex;
  HypStateIndex succIdx = wgArc.succStateIndex;

  // Check if ecmScrInfoForArcVec[wgArcId] is
  // empty. ecmScrInfoForArcVec[wgArcId] may be empty if wgArc has
  // no words
  EcmScoreInfo prevEsi;
  if (ecmScrInfoForArcVec[wgArcId].empty())
    prevEsi = ecmScrInfoForState[predIdx];
  else
    prevEsi = ecmScrInfoForArcVec[wgArcId].back();

  // Obtain ecm score vector for successor state
  std::vector<Score> ecmScrVec = ecm_wg_ptr->obtainScrVecFromEsi(prevEsi);

  // Obtain wg score for successor state from the wg score
  // vector of the predecessor state
  Score wgScr = wgScoreForState[predIdx] + wgArc.arcScore;

  // Update vector of best scores for state

  // Grow bestScoresForState vector size if necessary
  while (bestScoresForState[succIdx].size() < ecmScrVec.size())
  {
    bestScoresForState[succIdx].push_back(SMALL_SCORE);
    bestPredsForState[succIdx].push_back(INVALID_ARCID);
  }

  // Update best scores and create posVec vector
  std::vector<unsigned int> posVec;
  // Set value of startPos
  unsigned int startPos;
  if (prefDiffSize == 0)
    startPos = 0;
  else
    startPos = bestScoresForState[succIdx].size() - prefDiffSize;

  for (unsigned int i = startPos; i < bestScoresForState[succIdx].size(); ++i)
  {
    Score newScore = (ecmWeight * ecmScrVec[i]) + (wgWeight * wgScr);

    if (bestScoresForState[succIdx][i] < newScore)
    {
      // Update best score
      bestScoresForState[succIdx][i] = newScore;
      // Store updated position in posVec
      posVec.push_back(i);
      // Update best predecessor
      bestPredsForState[succIdx][i] = wgArcId;
    }
  }

  // Update ecm score info for succesor state
  ecm_wg_ptr->updateEsiPositions(prevEsi, posVec, ecmScrInfoForState[succIdx]);

  // Update wg score for succIdx
  wgScoreForState[succIdx] = wgScr;
}

//---------------------------------------
template <class ECM_FOR_WG>
NbestCorrections WgProcessorForAnlp<ECM_FOR_WG>::obtainNbestCorrections(
    std::vector<std::string> prefixVec, unsigned int n, const RejectedWordsSet& rejectedWords,
    const NbestHypStates& nbestHypStates, const NbestHypSubStates& nbestHypSubStates, unsigned int verbose /*=0*/)
{
  // Generate list with the n-best corrections given lists with
  // n-best hypothesis states and n-best hypothesis sub-states
  NbestCorrections nbestCorrections;
  nbestCorrections.clear();

  // Iterate over the n-best list of states
  NbestHypStates::const_iterator nbestHypStatesIter;
  for (nbestHypStatesIter = nbestHypStates.begin(); nbestHypStatesIter != nbestHypStates.end(); ++nbestHypStatesIter)
  {
    HypStateIndex hypStateIndex = nbestHypStatesIter->second;

    // Obtain suffix
    std::vector<std::string> correction = obtainCorrForHypState(prefixVec, hypStateIndex, rejectedWords, verbose);

    // Insert correction
    nbestCorrections.insert(std::make_pair(nbestHypStatesIter->first, correction));
    // Prune n-best corrections if necessary
    if (nbestCorrections.size() > n)
      removeLastFromNbestCorrs(nbestCorrections);
  }

  // Iterate over the n-best list of sub-states
  NbestHypSubStates::const_iterator nbestHypSubStatesIter;
  for (nbestHypSubStatesIter = nbestHypSubStates.begin(); nbestHypSubStatesIter != nbestHypSubStates.end();
       ++nbestHypSubStatesIter)
  {
    HypSubStateIdx hypSubStateIdx = nbestHypSubStatesIter->second;

    // Obtain suffix
    std::vector<std::string> correction = obtainCorrForHypSubState(prefixVec, hypSubStateIdx, verbose);

    // Insert correction
    nbestCorrections.insert(std::make_pair(nbestHypSubStatesIter->first, correction));

    // Prune n-best corrections if necessary
    if (nbestCorrections.size() > n)
      removeLastFromNbestCorrs(nbestCorrections);
  }

  // Print corrections
  if (verbose)
  {
    std::cerr << "Corrections:" << std::endl;
    NbestCorrections::const_iterator nbestCorrIter;
    for (nbestCorrIter = nbestCorrections.begin(); nbestCorrIter != nbestCorrections.end(); ++nbestCorrIter)
    {
      std::cerr << nbestCorrIter->first;
      for (unsigned int i = 0; i < nbestCorrIter->second.size(); ++i)
        std::cerr << " " << nbestCorrIter->second[i];
      std::cerr << "|" << std::endl;
    }

    // Print information about scores
    printInfoAboutScores(std::cerr);
  }

  // Return n-best corrections
  return nbestCorrections;
}

//---------------------------------------
template <class ECM_FOR_WG>
std::vector<std::string> WgProcessorForAnlp<ECM_FOR_WG>::obtainBestUncorrPrefHypState(
    unsigned int procPrefPos, HypStateIndex hypStateIndex, std::vector<WordGraphArcId>& wgaidVec)
{
  std::vector<std::string> invResult;
  std::vector<std::string> result;

  // Initialize wgaidVec
  wgaidVec.clear();

  // Trace back to INITIAL_STATE
  HypStateIndex hsidx = hypStateIndex;
  unsigned int currProcPrefPos = procPrefPos;
  while (hsidx != INITIAL_STATE)
  {
    /*     // Remove comments to get debug information */
    /* std::cerr<<currProcPrefPos<<" "<<hsidx<<" "<<bestScoresForState[hsidx][currProcPrefPos]<<std::endl; */

    // Obtain best predecessor hypothesis state
    WordGraphArcId wordGraphArcId = bestPredsForState[hsidx][currProcPrefPos];
    wgaidVec.push_back(wordGraphArcId);
    WordGraphArc wordGraphArc = wg_ptr->wordGraphArcId2WordGraphArc(wordGraphArcId);

    // Obtain new value for currProcPrefPos
    for (unsigned int w = wordGraphArc.words.size(); w > 0; --w)
    {
      std::vector<int> predPrefWordVec =
          ecm_wg_ptr->obtainLastInsPrefWordVecFromEsi(ecmScrInfoForArcVec[wordGraphArcId][w - 1]);
      currProcPrefPos = predPrefWordVec[currProcPrefPos];
    }

    // Obtain new value for hsidx
    hsidx = wordGraphArc.predStateIndex;

    // Add words to invResult
    for (unsigned int i = wordGraphArc.words.size(); i > 0; --i)
    {
      invResult.push_back(wordGraphArc.words[i - 1]);
    }
  }

  // Invert inverted result
  while (!invResult.empty())
  {
    result.push_back(invResult.back());
    invResult.pop_back();
  }
  // Return uncorrected prefix
  return result;
}

//---------------------------------------
template <class ECM_FOR_WG>
std::vector<std::string> WgProcessorForAnlp<ECM_FOR_WG>::obtainBestUncorrPrefHypSubState(
    unsigned int procPrefPos, WordGraphArcId wgArcId, unsigned int arcPos, std::vector<WordGraphArcId>& wgaidVec)
{
  // Initialize variables
  WordGraphArc wgArc = wg_ptr->wordGraphArcId2WordGraphArc(wgArcId);
  std::vector<std::string> auxResult;
  std::vector<std::string> result;

  // Obtain new value for currProcPrefPos
  unsigned int currProcPrefPos = procPrefPos;
  for (unsigned int w = arcPos + 1; w > 0; --w)
  {
    std::vector<int> predPrefWordVec = ecm_wg_ptr->obtainLastInsPrefWordVecFromEsi(ecmScrInfoForArcVec[wgArcId][w - 1]);
    currProcPrefPos = predPrefWordVec[currProcPrefPos];
  }

  // Backtrack path to initial state
  std::vector<WordGraphArcId> wgaidVecAux;
  result = obtainBestUncorrPrefHypState(currProcPrefPos, wgArc.predStateIndex, wgaidVecAux);

  // Compose result
  for (unsigned int i = 0; i <= arcPos; ++i)
    result.push_back(wgArc.words[i]);

  // Compose wgaidVec
  wgaidVec.clear();
  wgaidVec.push_back(wgArcId);
  for (unsigned int i = 0; i < wgaidVecAux.size(); ++i)
    wgaidVec.push_back(wgaidVecAux[i]);

  return result;
}

//---------------------------------------
template <class ECM_FOR_WG>
std::vector<std::string> WgProcessorForAnlp<ECM_FOR_WG>::obtainCorrForHypState(std::vector<std::string> prefixVec,
                                                                               HypStateIndex hypStateIndex,
                                                                               const RejectedWordsSet& rejectedWords,
                                                                               unsigned int verbose /*=0*/)
{
  if (verbose)
    std::cerr << " - Obtaining correction for hypothesis state " << hypStateIndex << std::endl;

  // Obtain uncorrected prefix
  std::vector<WordGraphArcId> wgaidVec;
  std::vector<std::string> uncorrPrefVec = obtainBestUncorrPrefHypState(prefixVec.size(), hypStateIndex, wgaidVec);
  // Combine prefix and uncorrected prefix
  std::vector<std::string> combinedPref;
  if (uncorrPrefVec.empty())
  {
    combinedPref = prefixVec;
    // Remove last blank if exists
    if (!combinedPref.empty())
      combinedPref.back() = StrProcUtils::removeLastBlank(combinedPref.back());
  }
  else
  {
    ecm_wg_ptr->correctStrGivenPrefWg(uncorrPrefVec, prefixVec, combinedPref);
    // The previous function corrects the string "uncorrPrefVec" given
    // the prefix "prefixVec", obtaining a new string which is
    // compatible with the prefix.
  }
  std::vector<std::string> result = combinedPref;

  // Obtain suffix for successor state

  // Obtain set of excluded arcs
  std::set<WordGraphArcId> excludedWgArcIdSet;
  std::vector<WordGraphArcId> arcIdsSuccStatesVec;
  if (!rejectedWords.empty())
  {
    wg_ptr->getArcIdsToSuccStates(hypStateIndex, arcIdsSuccStatesVec);
    for (unsigned int i = 0; i < arcIdsSuccStatesVec.size(); ++i)
    {
      WordGraphArc wgArc = wg_ptr->wordGraphArcId2WordGraphArc(arcIdsSuccStatesVec[i]);
      bool wordSatisfiesConstraint = wordSatisfiesRejWordConstraint(wgArc.words[0], rejectedWords);
      if (!wordSatisfiesConstraint)
        excludedWgArcIdSet.insert(arcIdsSuccStatesVec[i]);
    }
  }

  // Obtain best path
  std::vector<WordGraphArc> arcVec;
  wg_ptr->bestPathFromFinalStateToIdx(hypStateIndex, excludedWgArcIdSet, arcVec);

  for (std::vector<WordGraphArc>::reverse_iterator riter = arcVec.rbegin(); riter != arcVec.rend(); ++riter)
  {
    for (unsigned int i = 0; i < riter->words.size(); ++i)
      result.push_back(riter->words[i]);
  }

  // Remove last blank character if exists
  if (result.size() > 0)
    result.back() = StrProcUtils::removeLastBlank(result.back());

  if (verbose)
  {
    std::cerr << "   Uncorrected prefix:";
    for (unsigned int i = 0; i < uncorrPrefVec.size(); ++i)
      std::cerr << " " << uncorrPrefVec[i];
    std::cerr << "|" << std::endl;
    std::cerr << "   Associated word-graph state sequence:";
    for (unsigned int i = 0; i < wgaidVec.size(); ++i)
    {
      WordGraphArc wgArc = wg_ptr->wordGraphArcId2WordGraphArc(wgaidVec[i]);
      std::cerr << " " << wgArc.succStateIndex << "<-" << wgArc.predStateIndex;
    }
    std::cerr << std::endl;
    std::cerr << "   Prefix:";
    for (unsigned int i = 0; i < prefixVec.size(); ++i)
      std::cerr << " " << prefixVec[i];
    std::cerr << "|" << std::endl;
    std::cerr << "   Combined prefix:";
    for (unsigned int i = 0; i < combinedPref.size(); ++i)
      std::cerr << " " << combinedPref[i];
    std::cerr << "|" << std::endl;
    std::cerr << "   Correction:";
    for (unsigned int i = 0; i < result.size(); ++i)
      std::cerr << " " << result[i];
    std::cerr << "|" << std::endl;
    std::cerr << "   Score information: ";
    printStateInfo(hypStateIndex, std::cerr);
    std::cerr << std::endl;
  }

  // Return result
  return result;
}

//---------------------------------------
template <class ECM_FOR_WG>
std::vector<std::string> WgProcessorForAnlp<ECM_FOR_WG>::obtainCorrForHypSubState(std::vector<std::string> prefixVec,
                                                                                  HypSubStateIdx hypSubStateIdx,
                                                                                  unsigned int verbose /*=0*/)
{
  if (verbose)
  {
    std::cerr
        << " - Obtaining correction for hypothesis sub-state "; //<<hypSubStateIdx.first<<" "<<hypSubStateIdx.second;
                                                                // Obtain arc from arc id.
    WordGraphArc wgArc = wg_ptr->wordGraphArcId2WordGraphArc(hypSubStateIdx.first);
    std::cerr << wgArc.predStateIndex << "->" << wgArc.succStateIndex << ", " << hypSubStateIdx.second << "'th word"
              << std::endl;
  }

  std::vector<std::string> result;

  // Obtain uncorrected prefix
  std::vector<WordGraphArcId> wgaidVec;
  std::vector<std::string> uncorrPrefVec =
      obtainBestUncorrPrefHypSubState(prefixVec.size(), hypSubStateIdx.first, hypSubStateIdx.second, wgaidVec);
  // Combine prefix and uncorrected prefix
  std::vector<std::string> combinedPref;
  if (uncorrPrefVec.empty())
  {
    combinedPref = prefixVec;
    // Remove last blank if exists
    if (!combinedPref.empty())
      combinedPref.back() = StrProcUtils::removeLastBlank(combinedPref.back());
  }
  else
  {
    ecm_wg_ptr->correctStrGivenPrefWg(uncorrPrefVec, prefixVec, combinedPref);
    // The previous function corrects the string "uncorrPrefVec" given
    // the prefix "prefixVec", obtaining a new string which is
    // compatible with the prefix.
  }
  result = combinedPref;

  // Obtain arc from arc id
  WordGraphArc wgArc = wg_ptr->wordGraphArcId2WordGraphArc(hypSubStateIdx.first);

  // Obtain result concatenating words in the arc with suffix for
  // succesor state
  for (unsigned int w = hypSubStateIdx.second + 1; w < wgArc.words.size(); ++w)
    result.push_back(wgArc.words[w]);

  // Obtain suffix for successor state
  std::vector<Score> prevScores;
  std::vector<WordGraphArc> arcVec;

  // Obtain best path
  std::set<WordGraphArcId> emptyWgArcIdSet;
  wg_ptr->bestPathFromFinalStateToIdx(wgArc.succStateIndex, emptyWgArcIdSet, arcVec);

  for (std::vector<WordGraphArc>::reverse_iterator riter = arcVec.rbegin(); riter != arcVec.rend(); ++riter)
  {
    for (unsigned int i = 0; i < riter->words.size(); ++i)
      result.push_back(riter->words[i]);
  }

  // Remove last blank character if exists
  if (result.size() > 0)
    result.back() = StrProcUtils::removeLastBlank(result.back());

  if (verbose)
  {
    std::cerr << "   Uncorrected prefix:";
    for (unsigned int i = 0; i < uncorrPrefVec.size(); ++i)
      std::cerr << " " << uncorrPrefVec[i];
    std::cerr << "|" << std::endl;
    std::cerr << "   Associated word-graph state sequence:";
    for (unsigned int i = 0; i < wgaidVec.size(); ++i)
    {
      WordGraphArc wgArc = wg_ptr->wordGraphArcId2WordGraphArc(wgaidVec[i]);
      std::cerr << " " << wgArc.succStateIndex << "<-" << wgArc.predStateIndex;
    }
    std::cerr << std::endl;
    std::cerr << "   Prefix:";
    for (unsigned int i = 0; i < prefixVec.size(); ++i)
      std::cerr << " " << prefixVec[i];
    std::cerr << "|" << std::endl;
    std::cerr << "   Combined prefix:";
    for (unsigned int i = 0; i < combinedPref.size(); ++i)
      std::cerr << " " << combinedPref[i];
    std::cerr << "|" << std::endl;
    std::cerr << "   Correction:";
    for (unsigned int i = 0; i < result.size(); ++i)
      std::cerr << " " << result[i];
    std::cerr << "|" << std::endl;
    std::cerr << "   Score information: ";
    printSubStateInfo(hypSubStateIdx.first, hypSubStateIdx.second, std::cerr);
    std::cerr << std::endl;
  }

  // Return result
  return result;
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::removeLastFromNbestHypStates(NbestHypStates& nbestHypStates)
{
  NbestHypStates::iterator pos;

  if (!nbestHypStates.empty())
  {
    pos = nbestHypStates.end();
    --pos;
    nbestHypStates.erase(pos--);
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::removeLastFromNbestHypSubStates(NbestHypSubStates& nbestHypSubStates)
{
  NbestHypSubStates::iterator pos;

  if (!nbestHypSubStates.empty())
  {
    pos = nbestHypSubStates.end();
    --pos;
    nbestHypSubStates.erase(pos--);
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::removeLastFromNbestCorrs(NbestCorrections& nbestCorrections)
{
  NbestCorrections::iterator pos;

  if (!nbestCorrections.empty())
  {
    pos = nbestCorrections.end();
    --pos;
    nbestCorrections.erase(pos--);
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::clear(void)
{
  initVarsExecuted = false;
  previousPrefixVec.clear();
  restScores.clear();
  ecmScrInfoForState.clear();
  ecmScrInfoForArcVec.clear();
  wgScoreForState.clear();
  bestScoresForState.clear();
  bestPredsForState.clear();
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::clearTempVars(void)
{
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::initVars(unsigned int verbose /*=0*/)
{
  // Clear previous prefix vector
  previousPrefixVec.clear();

  // Generate rest scores for word-graph
  restScores.clear();
  wg_ptr->calcRestScores(restScores);

  // Make room for the ecmScrInfoForState and the ecmScrInfoForArcVec
  // variables
  ecmScrInfoForState.clear();
  ecmScrInfoForArcVec.clear();
  if (wg_ptr != NULL)
  {
    EcmScoreInfo esi;
    ecmScrInfoForState.insert(ecmScrInfoForState.begin(), wg_ptr->numStates(), esi);
    EcmScrInfoForArc esiArc;
    ecmScrInfoForArcVec.insert(ecmScrInfoForArcVec.begin(), wg_ptr->numArcs(), esiArc);
  }

  // Make room for the wgScoresForState variable
  wgScoreForState.clear();
  if (wg_ptr != NULL)
  {
    Score scr;
    wgScoreForState.insert(wgScoreForState.begin(), wg_ptr->numStates(), scr);
  }

  // Make room for bestScoresForState and bestPredsForState variables
  bestScoresForState.clear();
  bestPredsForState.clear();
  if (wg_ptr != NULL)
  {
    std::vector<Score> scoreVec;
    bestScoresForState.insert(bestScoresForState.begin(), wg_ptr->numStates(), scoreVec);

    std::vector<WordGraphArcId> wgArcIdVec;
    bestPredsForState.insert(bestPredsForState.begin(), wg_ptr->numStates(), wgArcIdVec);
  }

  // Init wgp info for hypothesis states and arcs
  if (wg_ptr != NULL && ecm_wg_ptr != NULL)
  {
    // Initialize initial state
    initWgpInfoForInitState(verbose);
    // Initialize arcs
    initWgpInfoForArcs(verbose);
  }

  // Generate list of states involved in arcs
  genListOfStatesInvolvedInArcs(statesInvolvedInArcs);

  // Update initVarsExecuted variable
  initVarsExecuted = true;
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::genListOfStatesInvolvedInArcs(StatesInvolvedInArcs& stInvInArcs) const
{
  stInvInArcs.clear();
  std::pair<WordGraphArcId, WordGraphArcId> arcIdxRange = wg_ptr->getArcIndexRange();
  for (unsigned int aIdx = arcIdxRange.first; aIdx <= arcIdxRange.second; ++aIdx)
  {
    // Update info for arcs
    if (!wg_ptr->arcPruned(aIdx))
    {
      WordGraphArc wgArc = wg_ptr->wordGraphArcId2WordGraphArc(aIdx);
      stInvInArcs.insert(wgArc.predStateIndex);
      stInvInArcs.insert(wgArc.succStateIndex);
    }
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::updateSizeOfVars(const std::vector<std::string>& validProcPrefixVec)
{
  // Obtain diff size
  unsigned int diffSize = previousPrefixVec.size() - validProcPrefixVec.size();

  // Adjust size of ecm score info for arcs
  for (unsigned int aIdx = 0; aIdx < ecmScrInfoForArcVec.size(); ++aIdx)
  {
    // Adjust size of ecm score info for the j'th word
    for (unsigned int j = 0; j < ecmScrInfoForArcVec[aIdx].size(); ++j)
    {
      for (unsigned int k = 0; k < diffSize; ++k)
        ecm_wg_ptr->removeLastPosFromEsi(ecmScrInfoForArcVec[aIdx][j]);
    }
  }

  // Iterate over states involved in arcs
  StatesInvolvedInArcs::iterator iter;
  for (iter = statesInvolvedInArcs.begin(); iter != statesInvolvedInArcs.end(); ++iter)
  {
    HypStateIndex idx = *iter;

    // Adjust size of ecm score info for state
    for (unsigned int i = 0; i < diffSize; ++i)
      ecm_wg_ptr->removeLastPosFromEsi(ecmScrInfoForState[idx]);

    // Adjust size of best score vector
    for (unsigned int i = 0; i < diffSize; ++i)
      bestScoresForState[idx].pop_back();

    // Adjust size of predecessors vector
    for (unsigned int i = 0; i < diffSize; ++i)
      bestPredsForState[idx].pop_back();
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
bool WgProcessorForAnlp<ECM_FOR_WG>::print(const char* filename) const
{
  std::ofstream outS;

  outS.open(filename, std::ios::out);
  if (!outS)
  {
    std::cerr << "Error while printing word-graph processing information to file." << std::endl;
    return THOT_ERROR;
  }
  else
  {
    print(outS);
    outS.close();
    return THOT_OK;
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::print(std::ostream& outS) const
{
  // Print prefix
  outS << "# Prefix:";
  for (unsigned int i = 0; i < previousPrefixVec.size(); ++i)
    outS << " " << previousPrefixVec[i];
  outS << "|" << std::endl;

  // Print final states
  WordGraph::FinalStateSet finalStateSet = wg_ptr->getFinalStateSet();
  WordGraph::FinalStateSet::const_iterator constIter;

  for (constIter = finalStateSet.begin(); constIter != finalStateSet.end(); ++constIter)
  {
    outS << *constIter << " ";
  }
  outS << std::endl;

  // Print information about scores
  printInfoAboutScores(outS);

  // Print state info
  printInfoForStates(outS);

  // Print separator
  outS << "#" << std::endl;

  // Print sub-state info
  printInfoForSubStates(outS);
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::printInfoAboutScores(std::ostream& outS) const
{
  outS << "# INFO ABOUT SCORE CALCULATION: totalScr = wgWeight*wgRestScr + wgWeight*wgPrefScr + ecmWeight*ecmScr"
       << std::endl;
  outS << "# (ecm and word-graph scores are multiplied by their corresponding weights," << std::endl;
  outS << "# ecm parameters: ";
  ecm_wg_ptr->printWeights(outS);
  outS << " ;" << std::endl;
  outS << "# wgWeight= " << wgWeight << " ; ecmWeight= " << ecmWeight << ")" << std::endl;
  outS << "#" << std::endl;
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::printInfoForStates(std::ostream& outS) const
{
  // Print state info header
  outS << "# State info..." << std::endl;

  // Generate list of states involved in arcs
  StatesInvolvedInArcs stInvInArcs;
  genListOfStatesInvolvedInArcs(stInvInArcs);

  // Iterate over states involved in arcs
  StatesInvolvedInArcs::iterator iter;
  for (iter = stInvInArcs.begin(); iter != stInvInArcs.end(); ++iter)
  {
    HypStateIndex idx = *iter;

    printStateInfo(idx, outS);

    outS << std::endl;
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::printStateInfo(HypStateIndex idx, std::ostream& outS) const
{
  // Print state index
  outS << "State index: " << idx << " ;";

  // Print total score
  if (restScores.size() > idx && bestScoresForState[idx].size() > 0)
    outS << " totalScr: " << wgWeight * restScores[idx] + bestScoresForState[idx].back();
  outS << " ;";

  // Print wg rest score
  outS << " wgRestScr: ";
  if (restScores.size() > idx)
    outS << restScores[idx] << " ";
  outS << ";";
  /*     // Print best scores */
  /* if(bestScoresForState.size()>idx) */
  /* { */
  /*   outS<<" bestScrs:"; */
  /*   for(unsigned int i=0;i<bestScoresForState[idx].size();++i) */
  /*     outS<<" "<<bestScoresForState[idx][i]; */
  /* } */
  /* outS<<" ;"; */

  // Print wg prefix score
  outS << " wgPrefScr: " << wgScoreForState[idx] << " ;";

  // Print ecm score
  std::vector<Score> ecmScrVec = ecm_wg_ptr->obtainScrVecFromEsi(ecmScrInfoForState[idx]);
  outS << " ecmScr: " << ecmScrVec.back() << " ;";

  // Print ecm score vector
  outS << " ecmScrVec:";
  for (unsigned int i = 0; i < ecmScrVec.size(); ++i)
    outS << " " << ecmScrVec[i];
  outS << " ;";

  // Print last inserted prefix word vector
  std::vector<int> lastInsPrefWordVec = ecm_wg_ptr->obtainLastInsPrefWordVecFromEsi(ecmScrInfoForState[idx]);
  outS << " lastInsPrefWordVec:";
  for (unsigned int i = 0; i < lastInsPrefWordVec.size(); ++i)
    outS << " " << lastInsPrefWordVec[i];
  outS << " ;";

  // Print predecessor state vector
  outS << " predStateVec:";
  for (unsigned int i = 0; i < bestPredsForState[idx].size(); ++i)
  {
    WordGraphArcId wordGraphArcId = bestPredsForState[idx][i];
    if (wordGraphArcId != INVALID_ARCID)
    {
      WordGraphArc wordGraphArc = wg_ptr->wordGraphArcId2WordGraphArc(wordGraphArcId);
      outS << " " << wordGraphArc.predStateIndex;
    }
    else
      outS << "-";
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::printInfoForSubStates(std::ostream& outS) const
{
  // Print sub-state info header
  outS << "# Sub-state info..." << std::endl;

  // Obtain arc range
  std::pair<WordGraphArcId, WordGraphArcId> arcIdxRange = wg_ptr->getArcIndexRange();

  // Iterate over the sub-states of the word-graph
  for (WordGraphArcId wgArcId = arcIdxRange.first; wgArcId <= arcIdxRange.second; ++wgArcId)
  {
    if (!wg_ptr->arcPruned(wgArcId))
    {
      // Obtain arc from arc id.
      WordGraphArc wgArc = wg_ptr->wordGraphArcId2WordGraphArc(wgArcId);
      // Iterate over the words of the arc
      for (unsigned int w = 0; w < wgArc.words.size(); ++w)
      {
        printSubStateInfo(wgArcId, w, outS);
        outS << std::endl;
      }
    }
  }
}

//---------------------------------------
template <class ECM_FOR_WG>
void WgProcessorForAnlp<ECM_FOR_WG>::printSubStateInfo(WordGraphArcId wgArcId, unsigned int w, std::ostream& outS) const
{
  // Obtain arc from arc id.
  WordGraphArc wgArc = wg_ptr->wordGraphArcId2WordGraphArc(wgArcId);

  // Obtain wg score vector for predecessor state
  Score wgScr = wgScoreForState[wgArc.predStateIndex];

  // Print sub-state info
  outS << "Sub-state index: " << wgArc.predStateIndex << "->" << wgArc.succStateIndex << "," << w << " ;";

  // Obtain ecm score vector for w'th word of current arc
  std::vector<Score> ecmScrVec = ecm_wg_ptr->obtainScrVecFromEsi(ecmScrInfoForArcVec[wgArcId][w]);

  // Print total score
  if (restScores.size() > wgArc.predStateIndex)
    outS << " totalScr: "
         << wgWeight * restScores[wgArc.predStateIndex] + wgWeight * wgScr + ecmWeight * ecmScrVec.back();
  outS << " ;";

  // Print wg rest score
  outS << " wgRestScr: ";
  if (restScores.size() > wgArc.predStateIndex)
    outS << restScores[wgArc.predStateIndex] << " ";
  outS << ";";

  /*     // Print best scores */
  /* outS<<" bestScrs:"; */
  /* for(unsigned int i=0;i<ecmScrVec.size();++i) */
  /*   outS<<" "<<wgWeight*wgScr+ecmWeight*ecmScrVec[i]; */
  /* outS<<" ;"; */

  // Print wg pref score
  if (wgScoreForState.size() > wgArc.predStateIndex)
  {
    outS << " wgPrefScr: " << wgScr << " ;";
  }

  // Print ecm score
  outS << " ecmScr: " << ecmScrVec.back() << " ;";

  // Print ecm score vector
  outS << " ecmScrVec:";
  for (unsigned int i = 0; i < ecmScrVec.size(); ++i)
    outS << " " << ecmScrVec[i];
  outS << " ;";

  // Print last inserted prefix word vector
  std::vector<int> lastInsPrefWordVec = ecm_wg_ptr->obtainLastInsPrefWordVecFromEsi(ecmScrInfoForArcVec[wgArcId][w]);
  outS << " lastInsPrefWordVec:";
  for (unsigned int i = 0; i < lastInsPrefWordVec.size(); ++i)
    outS << " " << lastInsPrefWordVec[i];
}

