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

#include "error_correction/WordGraph.h"
#include "nlp_common/PositionIndex.h"
#include "stack_dec/HypStateDict.h"
#include "stack_dec/_stackDecoder.h"

/**
 * @brief The _stackDecoderRec abstract template class is derived from
 * the _stackDecoder class and implements a base class for obtaining
 * stack decoders with recombination.
 */

template <class SMT_MODEL>
class _stackDecoderRec : public _stackDecoder<SMT_MODEL>
{
public:
  typedef typename BaseStackDecoder<SMT_MODEL>::Hypothesis Hypothesis;

  // Constructor.
  _stackDecoderRec();

  // Function to retrieve word graph ptr
  WordGraph* getWordGraphPtr();

  // Function to set word graph ptr
  void setWordGraphPtr(WordGraph* _wordGraphPtr);

  // Functions to parameterize word graphs
  void enableWordGraph();
  // Enable word graph
  void disableWordGraph();
  // Disable word graph
  void includeScoreCompsInWg();
  // Include score componentes in word graph
  void excludeScoreCompsInWg();
  // Exclude score componentes in word graph
  unsigned int pruneWordGraph(float threshold);
  // Prune word graph using the given threshold. Returns number of
  // pruned arcs

  // Functions to print word graphs
  bool printWordGraph(const char* filename);

  void clear();
  // Remove all partial hypotheses contained in the stack/s

  // Destructor
  ~_stackDecoderRec();

protected:
  bool wordGraphEnabled;
  bool scoreCompsInWgIncluded;
  WordGraph* wordGraphPtr;
  bool wgPtrOwnedByObject;
  HypStateDict<Hypothesis>* hypStateDictPtr;

  // Actions after decoding
  void post_trans_actions(const Hypothesis& result);

  bool pushGivenPredHyp(const Hypothesis& pred_hyp, const std::vector<Score>& scrComps, const Hypothesis& succ_hyp);
  // Overriden function to allow word-graph generation
  void addArcToWordGraph(Hypothesis pred_hyp, const std::vector<Score>& scrComps, Hypothesis succ_hyp);
  // Add an arc to the recombination graph.
  HypStateIndex getHypStateIndex(const Hypothesis& hyp, bool& existIndex);
  // Obtain hypothesis state index for hyp. If the index exist, the
  // value of existIndex will be set to true, and false otherwise
  bool printHypStateIdxInfo(const char* filename);
  void printHypStateIdxInfo(std::ostream& outS);
};

template <class SMT_MODEL>
_stackDecoderRec<SMT_MODEL>::_stackDecoderRec() : _stackDecoder<SMT_MODEL>()
{
  wordGraphPtr = new WordGraph;
  wgPtrOwnedByObject = true;
  hypStateDictPtr = new HypStateDict<Hypothesis>;
  wordGraphEnabled = false;
  scoreCompsInWgIncluded = true;
}

template <class SMT_MODEL>
void _stackDecoderRec<SMT_MODEL>::enableWordGraph()
{
  wordGraphEnabled = true;
}

template <class SMT_MODEL>
void _stackDecoderRec<SMT_MODEL>::disableWordGraph()
{
  wordGraphEnabled = false;
}

template <class SMT_MODEL>
void _stackDecoderRec<SMT_MODEL>::includeScoreCompsInWg()
{
  scoreCompsInWgIncluded = true;
}

template <class SMT_MODEL>
void _stackDecoderRec<SMT_MODEL>::excludeScoreCompsInWg()
{
  scoreCompsInWgIncluded = false;
}

template <class SMT_MODEL>
WordGraph* _stackDecoderRec<SMT_MODEL>::getWordGraphPtr()
{
  return wordGraphPtr;
}

template <class SMT_MODEL>
void _stackDecoderRec<SMT_MODEL>::setWordGraphPtr(WordGraph* _wordGraphPtr)
{
  if (wgPtrOwnedByObject)
    delete wordGraphPtr;

  wordGraphPtr = _wordGraphPtr;
  wgPtrOwnedByObject = false;
}

template <class SMT_MODEL>
unsigned int _stackDecoderRec<SMT_MODEL>::pruneWordGraph(float threshold)
{
  // Prune word graph
  unsigned int numPrunedArcs = wordGraphPtr->prune(threshold);
  return numPrunedArcs;
}

template <class SMT_MODEL>
bool _stackDecoderRec<SMT_MODEL>::printWordGraph(const char* filename)
{
  int ret;

  if (scoreCompsInWgIncluded)
  {
    // Set weights of the components in the wordgraph (this may be
    // misplaced)
    std::vector<std::pair<std::string, float>> compWeights;
    this->smtModel->getWeights(compWeights);
    wordGraphPtr->setCompWeights(compWeights);
  }
  // Print word graph
  std::string filenameWordGraph = filename;
  filenameWordGraph = filenameWordGraph + ".wg";
  ret = wordGraphPtr->print(filenameWordGraph.c_str(), true);
  // NOTE: if the second parameter of wordGraphPtr->print() is set to
  // true, only useful states (those that allow us to reach to a
  // final state) are printed
  if (ret == THOT_ERROR)
    return THOT_ERROR;

  // Print state index info
  std::string filenameHypStateIdx = filename;
  filenameHypStateIdx = filenameHypStateIdx + ".idx";
  return printHypStateIdxInfo(filenameHypStateIdx.c_str());
}

template <class SMT_MODEL>
void _stackDecoderRec<SMT_MODEL>::clear()
{
  _stackDecoder<SMT_MODEL>::clear();
  hypStateDictPtr->clear();
  wordGraphPtr->clear();
}

template <class SMT_MODEL>
void _stackDecoderRec<SMT_MODEL>::post_trans_actions(const Hypothesis& result)
{
  // If result hypothesis is not a complete hypothesis, then we need
  // to add the corresponding state to the set of final states of
  // the translation word graph. Otherwise, it will be empty
  if (!this->smtModel->isComplete(result))
  {
    bool existIndex;
    HypStateIndex stateIdx = getHypStateIndex(result, existIndex);
    wordGraphPtr->addFinalState(stateIdx);
  }
}

template <class SMT_MODEL>
bool _stackDecoderRec<SMT_MODEL>::pushGivenPredHyp(const Hypothesis& pred_hyp, const std::vector<Score>& scrComps,
                                                   const Hypothesis& succ_hyp)

{
  bool retval = this->push(succ_hyp);
  addArcToWordGraph(pred_hyp, scrComps, succ_hyp);

  return retval;
}

template <class SMT_MODEL>
void _stackDecoderRec<SMT_MODEL>::addArcToWordGraph(Hypothesis pred_hyp, const std::vector<Score>& scrComps,
                                                    Hypothesis succ_hyp)
{
  if (wordGraphEnabled)
  {
    // Obtain indices for predecessor and successor states, the
    // indices will not exist if the corresponding hypotheses has not
    // been inserted or recombined into the stack
    bool existIndexPred;
    bool existIndexSucc;
    HypStateIndex predStateIndex = getHypStateIndex(pred_hyp, existIndexPred);
    HypStateIndex succStateIndex = getHypStateIndex(succ_hyp, existIndexSucc);

    if (existIndexPred && existIndexSucc)
    {
      // The arc is added only if the hypotheses has been inserted or
      // recombined into the stack

      // Add heuristic to hypotheses
      this->smtModel->addHeuristicToHyp(pred_hyp);
      this->smtModel->addHeuristicToHyp(succ_hyp);

      // Set score for the initial state
      if (predStateIndex == INITIAL_STATE)
        wordGraphPtr->setInitialStateScore(pred_hyp.getScore());

      // Add final state if succ_hyp is complete
      bool succStateIndexComplete = this->smtModel->isComplete(succ_hyp);
      if (succStateIndexComplete)
        wordGraphPtr->addFinalState(succStateIndex);

      // Obtain the score of the arc
      LgProb arcScore = succ_hyp.getScore() - pred_hyp.getScore();

      // Obtain the words associated to the arc
      std::vector<std::string> predPartialTrans = this->smtModel->getTransInPlainTextVec(pred_hyp);
      std::set<PositionIndex> unknownWords;
      std::vector<std::string> succPartialTrans = this->smtModel->getTransInPlainTextVec(succ_hyp, unknownWords);
      std::vector<std::string> words;

      bool unknown = false;
      for (unsigned int i = predPartialTrans.size(); i < succPartialTrans.size(); ++i)
      {
        if (!unknown && unknownWords.find(i) != unknownWords.end())
          unknown = true;
        words.push_back(succPartialTrans[i]);
      }

      std::pair<PositionIndex, PositionIndex> lastSeg = this->smtModel->getLastSourceSegment(succ_hyp);

      if (scoreCompsInWgIncluded)
      {
        // Obtain components using unitary weights
        std::vector<Score> scrCompsUnitary;
        this->smtModel->getUnweightedComps(scrComps, scrCompsUnitary);

        // Add arc with score components
        wordGraphPtr->addArcWithScrComps(predStateIndex, succStateIndex, words, lastSeg.first, lastSeg.second, unknown,
                                         arcScore, scrCompsUnitary);
      }
      else
      {
        // Add arc
        wordGraphPtr->addArc(predStateIndex, succStateIndex, words, lastSeg.first, lastSeg.second, unknown, arcScore);
      }
    }
  }
}

template <class SMT_MODEL>
HypStateIndex _stackDecoderRec<SMT_MODEL>::getHypStateIndex(const Hypothesis& hyp, bool& existIndex)
{
  // Obtain hypothesis state index for hyp
  typename HypStateDict<Hypothesis>::iterator hypStateDictIter;
  HypStateIndex hypStateIndex;
  typename Hypothesis::HypState hypState;

  hypState = hyp.getHypState();
  hypStateDictIter = hypStateDictPtr->find(hypState);
  if (hypStateDictIter == hypStateDictPtr->end())
  {
    hypStateIndex = 0;
    existIndex = false;
    return hypStateIndex;
  }
  else
  {
    hypStateIndex = hypStateDictIter->second.hypStateIndex;
    existIndex = true;
    return hypStateIndex;
  }
}

template <class SMT_MODEL>
bool _stackDecoderRec<SMT_MODEL>::printHypStateIdxInfo(const char* filename)
{
  std::ofstream outS;

  outS.open(filename, std::ios::out);
  if (!outS)
  {
    std::cerr << "Error while printing hypothesis state info file." << std::endl;
    return THOT_ERROR;
  }
  else
  {
    printHypStateIdxInfo(outS);
    outS.close();
    return THOT_OK;
  }
}

template <class SMT_MODEL>
void _stackDecoderRec<SMT_MODEL>::printHypStateIdxInfo(std::ostream& outS)
{
  typename HypStateDict<Hypothesis>::iterator hsdIter;

  outS << "# SOURCE SENTENCE: " << this->srcSentence << std::endl;
  outS << "# SOURCE SENTENCE WITHOUT METADATA: " << this->smtModel->getCurrentSrcSent() << std::endl;
  for (hsdIter = hypStateDictPtr->begin(); hsdIter != hypStateDictPtr->end(); ++hsdIter)
  {
    outS << hsdIter->second.hypStateIndex << " " << hsdIter->second.coverage << " ";
    // Subtract g value if decoder running in breadth-first mode
    if (this->breadthFirst)
    {
      double g = trunc((double)hsdIter->second.score / (double)G_EPSILON);
      outS << hsdIter->second.score - (g * G_EPSILON);
    }
    else
      outS << hsdIter->second.score;

    outS << std::endl;
  }
}

template <class SMT_MODEL>
_stackDecoderRec<SMT_MODEL>::~_stackDecoderRec(void)
{
  if (wgPtrOwnedByObject)
    delete wordGraphPtr;
  delete hypStateDictPtr;
}
