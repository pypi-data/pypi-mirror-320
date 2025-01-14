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

#include "nlp_common/Bitset.h"
#include "nlp_common/PositionIndex.h"
#include "nlp_common/Prob.h"
#include "nlp_common/SmtDefs.h"
#include "nlp_common/StrProcUtils.h"
#include "nlp_common/WordIndex.h"
#include "stack_dec/BaseSmtMultiStack.h"
#include "stack_dec/BaseSmtStack.h"
#include "stack_dec/BaseStackDecoder.h"
#include "stack_dec/SmtStack.h"
#include "stack_dec/_stack_decoder_statistics.h"

#include <float.h>
#include <memory>

#define MAX_NUM_OF_ITER 1000000
#define PRINT_GRAPH_STEP 1
#define G_EPSILON -100000000
#define DEC_IDLE_STATE 1
#define DEC_TRANS_STATE 2
#define DEC_TRANSREF_STATE 3
#define DEC_VER_STATE 4
#define DEC_TRANSPREFIX_STATE 5

/**
 * @brief The _stackDecoder abstract template class is derived from the
 * BaseStackDecoder class and serves as a first step in the
 * implementation of other stack-based decoders.
 */
template <class SMT_MODEL>
class _stackDecoder : public BaseStackDecoder<SMT_MODEL>
{
public:
  typedef typename BaseStackDecoder<SMT_MODEL>::Hypothesis Hypothesis;

  _stackDecoder();
  // Constructor.

  void setSmtModel(SMT_MODEL* model);
  SMT_MODEL* getSmtModel();

  void setParentSmtModel(SMT_MODEL* model);
  SMT_MODEL* getParentSmtModel();

  // Functions for setting the decoder parameters
  void set_S_par(unsigned int S_par);
  unsigned int get_S_par() const;
  void set_I_par(unsigned int I_par);
  unsigned int get_I_par() const;
  void set_breadthFirst(bool b);
  bool get_breadthFirst() const;

  // Basic services
  Hypothesis translate(std::string s);
  // Translates the sentence 's' using the model fixed previously
  // with 'setModel'
  Hypothesis getNextTrans();
  // Obtains the next hypothesis that the algorithm yields
  Hypothesis translateWithRef(std::string s, std::string ref);
  // Obtains the best alignment for the source and ref sentence pair
  virtual Hypothesis verifyCoverageForRef(std::string s, std::string ref);
  // Verifies coverage of the translation model given a source
  // sentence s and the desired output ref. For this purpose, the
  // decoder filters those translations of s that are compatible
  // with ref. The resulting hypothesis won't be complete if the
  // model can't generate the reference
  Hypothesis translateWithSuggestion(std::string s, typename Hypothesis::DataType sug);
  // Translates string s using hypothesis sug as suggestion instead
  // of using the null hypothesis
  Hypothesis translateWithPrefix(std::string s, std::string pref);
  // Translates string s using pref as prefix

  // Set different options
  void useBestScorePruning(bool b);
  void setWorstScoreAllowed(Score _worstScoreAllowed);

  // Functions to report information about the search
  void printGraphForHyp(const Hypothesis& hyp, std::ostream& outS);

  void clear();
  // Clear temporary data structures

  // Set verbosity level
  void setVerbosity(int _verbosity);

  // Destructor
  virtual ~_stackDecoder();

#ifdef THOT_STATS
  void printStats(void);
  _stack_decoder_statistics _stack_decoder_stats;
#endif

protected:
  std::unique_ptr<SMT_MODEL> smtModel{}; // Pointer to a statistical machine translation
                                         // model
  SMT_MODEL* parentSmtModel;
  BaseSmtStack<Hypothesis>* stack_ptr; // Pointer to a stack-based container
  BaseSmtMultiStack<Hypothesis>* baseSmtMultiStackPtr;
  // Pointer to a multiple stack container (it is instantiated from
  // the set_breadthFirst() function and used as an auxiliary
  // variable)

  unsigned int state; // Stores the state of the decoder

  std::string srcSentence;    // srcSentence stores the sentence to be translated
  std::string refSentence;    // refSentence stores the reference sentence
  std::string prefixSentence; // prefixSentence stores the prefix given by the user

  unsigned int S; // Maximum stack size
  unsigned int I; // Number of hypotheses to be expanded
                  // at each iteration

  bool useRef; // If useRef=true, the expand process
               // will be based on a target reference
               // sentence

  bool usePrefix; // Translate using a prefix (CAT
                  // paradigm)

  bool breadthFirst; // Decides wether to use breadth-first
                     // search

  Score bestCompleteHypScore;
  Hypothesis bestCompleteHyp;
  bool applyBestScorePruning; // Decides wether to apply pruning
                              // based on the best score found during
                              // the translation process
  Score worstScoreAllowed;

  int verbosity; // Verbosity level

  // Actions previous to decoding
  int pre_trans_actions(std::string srcsent);
  void pre_trans_actions_ref(std::string srcsent, std::string refsent);
  void pre_trans_actions_ver(std::string srcsent, std::string refsent);
  void pre_trans_actions_prefix(std::string srcsent, std::string prefix);

  // Actions after decoding
  virtual void post_trans_actions(const Hypothesis& result);

  // Functions related to g heuristic
  void addgToHyp(Hypothesis& hyp);
  void subtractgToHyp(Hypothesis& hyp);

  void suggest(const Hypothesis& sug);
  // Inserts a hypothesis into the stack
  void suggestNullHyp(void);
  // Inserts the null hypothesis into the stack

  bool push(Hypothesis hyp);
  // push operation: push the 'hyp' hypothesis in the stack with key
  // 'key', if that stack does not exist, it is created The push
  // function also adds a heuristic value to hyp. This function
  // returns true if hyp is inserted into a stack.
  // NOTE: hyp is not passed by reference to avoid collateral effects
  Hypothesis pop(void);
  // pop operation: pops the top of the stack
  // the pop function also subtracts a heuristic value to hyp

  virtual bool pushGivenPredHyp(const Hypothesis& pred_hyp, const std::vector<Score>& scrComps,
                                const Hypothesis& succ_hyp);
  // Push hypothesis succ_hyp given its predecessor pred_hyp. This
  // function can be overridden by derived classes which use
  // hypotheses-recombination

  // Implementation of decoding processes
  Hypothesis decode(void);
  Hypothesis decodeWithRef(void);
  Hypothesis decodeVer(void);
  Hypothesis decodeWithPrefix(void);

  // Puts the decoder in the initial state
  void init_state(void);

  // Utilities
  Score testHeuristic(std::string sentence, Score optimalTransScore);
};

template <class SMT_MODEL>
_stackDecoder<SMT_MODEL>::_stackDecoder(void)
{
  state = DEC_IDLE_STATE;
  worstScoreAllowed = -FLT_MAX;
  useBestScorePruning(false);
  breadthFirst = false;
  S = 10;
  I = 1;
  smtModel = NULL;
  stack_ptr = NULL;
  verbosity = 0;
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::setSmtModel(SMT_MODEL* model)
{
  // Link smt model
  smtModel.reset(model);
}

template <class SMT_MODEL>
SMT_MODEL* _stackDecoder<SMT_MODEL>::getSmtModel()
{
  return smtModel.get();
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::setParentSmtModel(SMT_MODEL* model)
{
  parentSmtModel = model;
}

template <class SMT_MODEL>
SMT_MODEL* _stackDecoder<SMT_MODEL>::getParentSmtModel()
{
  return parentSmtModel;
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::set_S_par(unsigned int S_par)
{
  S = S_par;
  stack_ptr->setMaxStackSize(S);
}

template <class SMT_MODEL>
unsigned int _stackDecoder<SMT_MODEL>::get_S_par() const
{
  return S;
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::set_I_par(unsigned int I_par)
{
  I = I_par;
}

template <class SMT_MODEL>
unsigned int _stackDecoder<SMT_MODEL>::get_I_par() const
{
  return I;
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::set_breadthFirst(bool b)
{
  // Initialize breadthFirst flag
  breadthFirst = b;

  // Initialize pointer to multiple stack if the dynamic cast is
  // succesfull (this pointer is used in the pop() function)
  baseSmtMultiStackPtr = dynamic_cast<BaseSmtMultiStack<Hypothesis>*>(stack_ptr);
}

template <class SMT_MODEL>
bool _stackDecoder<SMT_MODEL>::get_breadthFirst() const
{
  return breadthFirst;
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::addgToHyp(Hypothesis& hyp)
{
  unsigned int i;
  double g;

  i = smtModel->distToNullHyp(hyp);
  g = (double)i * (double)G_EPSILON;
  hyp.addHeuristic(g);
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::subtractgToHyp(Hypothesis& hyp)
{
  unsigned int i;
  double g;

  i = smtModel->distToNullHyp(hyp);
  g = (double)i * (double)G_EPSILON;
  hyp.subtractHeuristic(g);
}

template <class SMT_MODEL>
typename _stackDecoder<SMT_MODEL>::Hypothesis _stackDecoder<SMT_MODEL>::translate(std::string s)
{
  return translateWithSuggestion(s, smtModel->nullHypothesisHypData());
}

template <class SMT_MODEL>
typename _stackDecoder<SMT_MODEL>::Hypothesis _stackDecoder<SMT_MODEL>::getNextTrans(void)
{
  if (smtModel == NULL)
  {
    Hypothesis emptyHyp;
    std::cerr << "Error! model not initialized\n";
    return emptyHyp;
  }
  else
  {
#ifdef THOT_STATS
    _stack_decoder_stats.clear();
    smtm_ptr->clearStats();
    ++_stack_decoder_stats.sentencesTranslated;
#endif
    // reset bestCompleteHypScore
    this->bestCompleteHypScore = worstScoreAllowed;
    // reset bestCompleteHyp
    bestCompleteHyp = smtModel->nullHypothesis();

    // get next translation depending on the state of the decoder
    switch (state)
    {
    case DEC_TRANS_STATE:
      return decode();
    case DEC_TRANSREF_STATE:
      return decodeWithRef();
    case DEC_VER_STATE:
      return decodeVer();
    case DEC_TRANSPREFIX_STATE:
      return decodeWithPrefix();
    default:
      Hypothesis emptyHyp;
      return emptyHyp;
    }
  }
}

template <class SMT_MODEL>
typename _stackDecoder<SMT_MODEL>::Hypothesis _stackDecoder<SMT_MODEL>::translateWithSuggestion(
    std::string s, typename Hypothesis::DataType sug)
{
  if (smtModel == NULL)
  {
    Hypothesis emptyHyp;
    std::cerr << "Error! model not initialized\n";
    return emptyHyp;
  }
  else
  {
#ifdef THOT_STATS
    _stack_decoder_stats.clear();
    smtm_ptr->clearStats();
    ++_stack_decoder_stats.sentencesTranslated;
#endif

    Hypothesis initialHyp;

    // Execute actions previous to the translation process
    int ret = pre_trans_actions(s);
    if (ret == THOT_ERROR)
    {
      init_state();
      Hypothesis nullHyp;
      nullHyp = smtModel->nullHypothesis();
      return nullHyp;
    }

    // Obtain initialHyp
    smtModel->obtainHypFromHypData(sug, initialHyp);

    // Insert null hypothesis
    suggest(initialHyp);
    // Initializes the multi-stack decoder algorithm with a stack
    // containing the initial hypothesis "initialHyp"

    // Translate sentence
    if (verbosity > 0)
      std::cerr << "Decoding input..." << std::endl;
    Hypothesis result = decode();

    post_trans_actions(result);

    return result;
  }
}

template <class SMT_MODEL>
typename _stackDecoder<SMT_MODEL>::Hypothesis _stackDecoder<SMT_MODEL>::translateWithRef(std::string s, std::string ref)
{
  if (smtModel == NULL)
  {
    Hypothesis emptyHyp;
    std::cerr << "Error! model not initialized\n";
    return emptyHyp;
  }
  else
  {
#ifdef THOT_STATS
    _stack_decoder_stats.clear();
    smtm_ptr->clearStats();
#endif

    // Verify sentence length
    unsigned int srcSize = StrProcUtils::stringToStringVector(s).size();
    unsigned int refSize = StrProcUtils::stringToStringVector(ref).size();
    if (srcSize >= MAX_SENTENCE_LENGTH_ALLOWED || refSize >= MAX_SENTENCE_LENGTH_ALLOWED)
    {
      std::cerr << "Error: input sentences are too long (MAX= " << MAX_SENTENCE_LENGTH_ALLOWED << " words)"
                << std::endl;
      init_state();
      Hypothesis nullHyp;
      nullHyp = smtModel->nullHypothesis();
      return nullHyp;
    }

    if (srcSize == 0 || refSize == 0)
    {
      std::cerr << "Warning: input sentences empty" << std::endl;
      init_state();
      Hypothesis nullHyp;
      nullHyp = smtModel->nullHypothesis();
      return nullHyp;
    }

    // Execute actions previous to the translation process
    pre_trans_actions_ref(s, ref);

    // Insert Null hypothesis
    suggestNullHyp();

    if (verbosity > 0)
      std::cerr << "Decoding input..." << std::endl;
    return decodeWithRef();
  }
}

template <class SMT_MODEL>
typename _stackDecoder<SMT_MODEL>::Hypothesis _stackDecoder<SMT_MODEL>::verifyCoverageForRef(std::string s,
                                                                                             std::string ref)
{
  if (smtModel == NULL)
  {
    Hypothesis emptyHyp;
    std::cerr << "Error! model not initialized\n";
    return emptyHyp;
  }
  else
  {
#ifdef THOT_STATS
    _stack_decoder_stats.clear();
    smtm_ptr->clearStats();
#endif

    // Verify sentence length
    unsigned int srcSize = StrProcUtils::stringToStringVector(s).size();
    unsigned int refSize = StrProcUtils::stringToStringVector(ref).size();
    if (srcSize >= MAX_SENTENCE_LENGTH_ALLOWED || refSize >= MAX_SENTENCE_LENGTH_ALLOWED)
    {
      std::cerr << "Error: input sentences are too long (MAX= " << MAX_SENTENCE_LENGTH_ALLOWED << " words)"
                << std::endl;
      init_state();
      Hypothesis nullHyp;
      nullHyp = smtModel->nullHypothesis();
      return nullHyp;
    }

    if (srcSize == 0 || refSize == 0)
    {
      std::cerr << "Warning: input sentences empty" << std::endl;
      init_state();
      Hypothesis nullHyp;
      nullHyp = smtModel->nullHypothesis();
      return nullHyp;
    }

    // Execute actions previous to the translation process
    pre_trans_actions_ver(s, ref);

    // Insert Null hypothesis
    suggestNullHyp();

    if (verbosity > 0)
      std::cerr << "Decoding input..." << std::endl;
    return decodeVer();
  }
}

template <class SMT_MODEL>
typename _stackDecoder<SMT_MODEL>::Hypothesis _stackDecoder<SMT_MODEL>::translateWithPrefix(std::string s,
                                                                                            std::string pref)
{
  if (smtModel == NULL)
  {
    Hypothesis emptyHyp;
    std::cerr << "Error! model not initialized\n";
    return emptyHyp;
  }
  else
  {
#ifdef THOT_STATS
    _stack_decoder_stats.clear();
    smtm_ptr->clearStats();
#endif

    // Verify sentence length
    unsigned int srcSize = StrProcUtils::stringToStringVector(s).size();
    unsigned int prefSize = StrProcUtils::stringToStringVector(pref).size();
    if (srcSize >= MAX_SENTENCE_LENGTH_ALLOWED || prefSize >= MAX_SENTENCE_LENGTH_ALLOWED)
    {
      std::cerr << "Error: input sentences are too long (MAX= " << MAX_SENTENCE_LENGTH_ALLOWED << " words)"
                << std::endl;
      init_state();
      Hypothesis nullHyp;
      nullHyp = smtModel->nullHypothesis();
      return nullHyp;
    }

    if (srcSize == 0 || prefSize == 0)
    {
      std::cerr << "Warning: input sentences empty" << std::endl;
      init_state();
      Hypothesis nullHyp;
      nullHyp = smtModel->nullHypothesis();
      return nullHyp;
    }

    // Execute actions previous to the translation process
    pre_trans_actions_prefix(s, pref);

    // Insert Null hypothesis
    suggestNullHyp();

    if (verbosity > 0)
      std::cerr << "Decoding input..." << std::endl;
    return decodeWithPrefix();
  }
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::useBestScorePruning(bool b)
{
  applyBestScorePruning = b;
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::setWorstScoreAllowed(Score _worstScoreAllowed)
{
  worstScoreAllowed = _worstScoreAllowed;
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::printGraphForHyp(const Hypothesis& hyp, std::ostream& outS)
{
  Hypothesis aux_hyp;
  aux_hyp = hyp;

  if (!smtModel->obtainPredecessor(aux_hyp))
  {
    // print null hypothesis
    smtModel->printHyp(hyp, outS);
    outS << std::endl;
  }
  else
  {
    Hypothesis pred;

    pred = hyp;
    aux_hyp = pred;
    while (smtModel->obtainPredecessor(pred))
    {
      smtModel->printHyp(pred, outS);
      smtModel->printHyp(aux_hyp, outS);
      outS << std::endl;
      aux_hyp = pred;
    }
  }
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::clear(void)
{
  stack_ptr->clear();
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::init_state(void)
{
  clear();
  state = DEC_IDLE_STATE;
  srcSentence.clear();
  refSentence.clear();
  prefixSentence.clear();
}

template <class SMT_MODEL>
Score _stackDecoder<SMT_MODEL>::testHeuristic(std::string sentence, Score optimalTransScore)
{
  if (smtModel == NULL)
  {
    std::cerr << "Error! model not initialized\n";
    return 0;
  }
  else
  {
    std::vector<WordIndex> emptyVector;
    Hypothesis nullHyp;
    Score difference;

    nullHyp = smtModel->nullHypothesis();
    smtModel->pre_trans_actions(sentence);

    smtModel->addHeuristicToHyp(nullHyp);

    difference = optimalTransScore - nullHyp.getScore();
#ifdef THOT_STATS
    _stack_decoder_stats.nullHypHeuristicValue += nullHyp.getScore();
    _stack_decoder_stats.scoreOfOptimalHyp += optimalTransScore;
#endif
    return difference;
  }
}

template <class SMT_MODEL>
int _stackDecoder<SMT_MODEL>::pre_trans_actions(std::string srcsent)
{
  clear();
  state = DEC_TRANS_STATE;
  srcSentence = srcsent;
  smtModel->pre_trans_actions(srcsent);

  // Verify sentence length (it is done after calling
  // pre_trans_actions for the smt model, since translation
  // metadata information may affect the length)
  std::string modelSrcSent = smtModel->getCurrentSrcSent();
  unsigned int srcSize = StrProcUtils::stringToStringVector(modelSrcSent).size();
  if (srcSize == 0 || srcSize >= MAX_SENTENCE_LENGTH_ALLOWED)
  {
    if (srcSize == 0)
      std::cerr << "Warning: the sentence to translate is empty" << std::endl;
    else
      std::cerr << "Error: the sentence to translate is too long (MAX= " << MAX_SENTENCE_LENGTH_ALLOWED << " words)"
                << std::endl;
    return THOT_ERROR;
  }

  bestCompleteHypScore = worstScoreAllowed;
  bestCompleteHyp = smtModel->nullHypothesis();
  return THOT_OK;
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::pre_trans_actions_ref(std::string srcsent, std::string refsent)
{
  clear();
  state = DEC_TRANSREF_STATE;
  srcSentence = srcsent;
  refSentence = refsent;
  smtModel->pre_trans_actions_ref(srcsent, refsent);
  bestCompleteHypScore = worstScoreAllowed;
  bestCompleteHyp = smtModel->nullHypothesis();
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::pre_trans_actions_ver(std::string srcsent, std::string refsent)
{
  clear();
  state = DEC_VER_STATE;
  srcSentence = srcsent;
  refSentence = refsent;
  smtModel->pre_trans_actions_ver(srcsent, refsent);
  bestCompleteHypScore = worstScoreAllowed;
  bestCompleteHyp = smtModel->nullHypothesis();
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::pre_trans_actions_prefix(std::string srcsent, std::string prefix)
{
  clear();
  state = DEC_TRANSPREFIX_STATE;
  srcSentence = srcsent;
  prefixSentence = prefix;
  smtModel->pre_trans_actions_prefix(srcsent, prefix);
  bestCompleteHypScore = worstScoreAllowed;
  bestCompleteHyp = smtModel->nullHypothesis();
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::post_trans_actions(const Hypothesis& /*result*/)
{
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::suggest(const Hypothesis& sug)
{
  push(sug);
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::suggestNullHyp(void)
{
  Hypothesis nullHyp;

  nullHyp = smtModel->nullHypothesis();
  push(nullHyp);
}

template <class SMT_MODEL>
bool _stackDecoder<SMT_MODEL>::push(Hypothesis hyp)
{
  // Only insert hyp if its score is not equal to -inf. This may
  // ocurr when the translation model assigns zero probability to an
  // unseen event
  bool inserted = false;
  if ((double)hyp.getScore() >= -FLT_MAX)
  {
    // Add heuristic and g values
    smtModel->addHeuristicToHyp(hyp);
    if (breadthFirst)
      addgToHyp(hyp);

    // Check whether best score pruning is applied
    if (!applyBestScorePruning)
    {
      inserted = stack_ptr->push(hyp);
      if (inserted && smtModel->isComplete(hyp))
      {
        this->bestCompleteHypScore = hyp.getScore();
        this->bestCompleteHyp = hyp;
      }
    }
    else
    {
      // Apply best score pruning
      // The following check is done to perform best score
      // pruning
      if ((double)hyp.getScore() >= (double)bestCompleteHypScore)
      {
        inserted = stack_ptr->push(hyp);
        if (inserted && smtModel->isComplete(hyp))
        {
          this->bestCompleteHypScore = hyp.getScore();
          this->bestCompleteHyp = hyp;
        }
      }
      else
      {
        inserted = false;
#ifdef THOT_STATS
        ++this->_stack_decoder_stats.pushAborted;
#endif
      }
    }
#ifdef THOT_STATS
    ++this->_stack_decoder_stats.totalPushNo;
    ++this->_stack_decoder_stats.pushPerIter;
#endif
  }
  return inserted;
}

template <class SMT_MODEL>
typename _stackDecoder<SMT_MODEL>::Hypothesis _stackDecoder<SMT_MODEL>::pop(void)
{
  if (breadthFirst)
  {
    // Breadth-first search
    if (baseSmtMultiStackPtr)
      // Set breadth-first flag of the multiple stack container to
      // true
      baseSmtMultiStackPtr->set_bf(true);

    Hypothesis hyp;
    if (smtModel->isComplete(stack_ptr->top()))
    {
      // If the hypothesis is complete, the breadth-first flag of
      // the stack requires special treatment. Specifically it must
      // be set to false before calling the pop() function in order
      // to get the best complete hypothesis instead of the
      // hypothesis stored in the first container according to the
      // ordering function
      if (baseSmtMultiStackPtr)
        baseSmtMultiStackPtr->set_bf(false);
      hyp = stack_ptr->pop();
      if (baseSmtMultiStackPtr)
        baseSmtMultiStackPtr->set_bf(true);
    }
    else
    {
      hyp = stack_ptr->pop();
    }
    subtractgToHyp(hyp);
    smtModel->subtractHeuristicToHyp(hyp);
    return hyp;
  }
  else
  {
    // Non breadth-first search
    Hypothesis hyp;
    hyp = stack_ptr->pop();
    smtModel->subtractHeuristicToHyp(hyp);
    return hyp;
  }
}

template <class SMT_MODEL>
bool _stackDecoder<SMT_MODEL>::pushGivenPredHyp(const Hypothesis& /*pred_hyp*/, const std::vector<Score>& /*scrComps*/,
                                                const Hypothesis& succ_hyp)
{
  return push(succ_hyp);
}

template <class SMT_MODEL>
typename _stackDecoder<SMT_MODEL>::Hypothesis _stackDecoder<SMT_MODEL>::decode(void)
{
  bool end = false;
  std::vector<Hypothesis> hypsToExpand;
  Hypothesis result = smtModel->nullHypothesis();
  unsigned int iterNo = 1;

  while (!end && iterNo < MAX_NUM_OF_ITER)
  {
#ifdef THOT_ENABLE_GRAPH
    if ((iterNo % PRINT_GRAPH_STEP) == 0)
    {
      char printGraphFileName[128];
      snprintf(printGraphFileName, 128, "%d.graph_file", iterNo);
      this->printSearchGraph(printGraphFileName);
    }
#endif
    // Select hypothesis to be expanded
    hypsToExpand.clear();
    while (!stack_ptr->empty() && hypsToExpand.size() < I)
    {
      hypsToExpand.push_back(pop());
    }

    if (verbosity > 1)
    {
      std::cerr << std::endl;
      std::cerr << "* IterNo: " << iterNo << std::endl;
      std::cerr << "  Number of queues/hypotheses: " << stack_ptr->size() << std::endl;
      std::cerr << "  hypsToExpand: " << hypsToExpand.size() << std::endl;
    }

#ifdef THOT_STATS
    this->_stack_decoder_stats.pushPerIter = 0;
    ++this->_stack_decoder_stats.numIter;
#endif
    // Finish if there is not any hypothesis to be expanded
    if (hypsToExpand.empty())
      end = true;
    else
    {
      // There are hypotheses to be expanded
      for (unsigned int i = 0; i < hypsToExpand.size(); ++i)
      {
        // If the hypothesis is complete, finish the decoding
        // process, but expand the remaining hypotheses (required by
        // getNextTrans)
        if (smtModel->isComplete(hypsToExpand[i]))
        {
          if (!end)
          {
            // Return the first complete hypothesis as the final
            // translation
            result = hypsToExpand[i];
            end = true;
          }
          else
            push(hypsToExpand[i]);
        }
        else
        {
          // If the hypothesis is not complete, expand it
#ifdef THOT_STATS
          ++this->_stack_decoder_stats.totalExpansionNo;
#endif

          if (verbosity > 1)
          {
            std::cerr << "  Expanding hypothesis: ";
            smtModel->printHyp(hypsToExpand[i], std::cerr);
          }

          std::vector<Hypothesis> expandedHyps;
          std::vector<std::vector<Score>> scrCompVec;
          int numExpHyp = 0;
          smtModel->expand(hypsToExpand[i], expandedHyps, scrCompVec);

          // Update result variable (choose hypothesis further to
          // null hypothesis with a higher score)
          if (smtModel->distToNullHyp(result) < smtModel->distToNullHyp(hypsToExpand[i]))
          {
            result = hypsToExpand[i];
          }
          else
          {
            if (smtModel->distToNullHyp(result) == smtModel->distToNullHyp(hypsToExpand[i])
                && result.getScore() < hypsToExpand[i].getScore())
              result = hypsToExpand[i];
          }

          if (verbosity > 1)
            std::cerr << "  Generated " << expandedHyps.size() << " expansions" << std::endl;

          while (!expandedHyps.empty())
          {
            // Push expanded hyp into the stack container
            bool inserted = pushGivenPredHyp(hypsToExpand[i], scrCompVec.back(), expandedHyps.back());

            if (verbosity > 2)
            {
              ++numExpHyp;
              std::cerr << "  Expanded hypothesis " << numExpHyp << " : ";
              smtModel->printHyp(expandedHyps.back(), std::cerr);
              std::cerr << "  (Inserted: " << inserted << ")" << std::endl;
            }

            scrCompVec.pop_back();
            expandedHyps.pop_back();
          }
        }
      }
    }
    ++iterNo;
  }

  if (iterNo >= MAX_NUM_OF_ITER)
    std::cerr << "Maximum number of iterations exceeded!\n";
  return result;
}

template <class SMT_MODEL>
typename _stackDecoder<SMT_MODEL>::Hypothesis _stackDecoder<SMT_MODEL>::decodeWithRef(void)
{
  bool end = false;
  std::vector<Hypothesis> hypsToExpand;
  Hypothesis result = smtModel->nullHypothesis();
  unsigned int iterNo = 1;

  while (!end && iterNo < MAX_NUM_OF_ITER)
  {
#ifdef THOT_ENABLE_GRAPH
    if ((iterNo % PRINT_GRAPH_STEP) == 0)
    {
      char printGraphFileName[128];
      snprintf(printGraphFileName, 128, "%d.graph_file", iterNo);
      this->printSearchGraph(printGraphFileName);
    }
#endif
    // Select hypothesis to be expanded
    hypsToExpand.clear();
    while (!stack_ptr->empty() && hypsToExpand.size() < I)
    {
      hypsToExpand.push_back(pop());
    }

    if (verbosity > 1)
    {
      std::cerr << std::endl;
      std::cerr << "* IterNo: " << iterNo << std::endl;
      std::cerr << "  Number of queues/hypotheses: " << stack_ptr->size() << std::endl;
      std::cerr << "  hypsToExpand: " << hypsToExpand.size() << std::endl;
    }

#ifdef THOT_STATS
    this->_stack_decoder_stats.pushPerIter = 0;
    ++this->_stack_decoder_stats.numIter;
#endif
    // Finish if there is not any hypothesis to be expanded
    if (hypsToExpand.empty())
      end = true;
    else
    {
      // There are hypotheses to be expanded
      for (unsigned int i = 0; i < hypsToExpand.size(); ++i)
      {
        // If the hypothesis is complete, finish the decoding
        // process, but expand the remaining hypotheses (required by
        // getNextTrans)
        if (smtModel->isComplete(hypsToExpand[i]))
        {
          if (!end)
          {
            // Return the first complete hypothesis as the final
            // translation
            result = hypsToExpand[i];
            end = true;
          }
          else
            push(hypsToExpand[i]);
        }
        else
        {
          // If the hypothesis is not complete, expand it
#ifdef THOT_STATS
          ++this->_stack_decoder_stats.totalExpansionNo;
#endif

          if (verbosity > 1)
          {
            std::cerr << "  Expanding hypothesis: ";
            smtModel->printHyp(hypsToExpand[i], std::cerr);
          }

          std::vector<Hypothesis> expandedHyps;
          std::vector<std::vector<Score>> scrCompVec;
          int numExpHyp = 0;
          smtModel->expand_ref(hypsToExpand[i], expandedHyps, scrCompVec);

          if (verbosity > 1)
            std::cerr << "  Generated " << expandedHyps.size() << " expansions" << std::endl;

          while (!expandedHyps.empty())
          {
            // Push expanded hyp into the stack container
            bool inserted = pushGivenPredHyp(hypsToExpand[i], scrCompVec.back(), expandedHyps.back());

            // Print verbose information
            if (verbosity > 2)
            {
              ++numExpHyp;
              std::cerr << "  Expanded hypothesis " << numExpHyp << " : ";
              smtModel->printHyp(expandedHyps.back(), std::cerr);
              std::cerr << "  (Inserted: " << inserted << ")" << std::endl;
            }

            scrCompVec.pop_back();
            expandedHyps.pop_back();
          }
        }
      }
    }
    ++iterNo;
  }

  if (iterNo >= MAX_NUM_OF_ITER)
    std::cerr << "Maximum number of iterations exceeded!\n";
  return result;
}

template <class SMT_MODEL>
typename _stackDecoder<SMT_MODEL>::Hypothesis _stackDecoder<SMT_MODEL>::decodeVer(void)
{
  bool end = false;
  std::vector<Hypothesis> hypsToExpand;
  Hypothesis result = smtModel->nullHypothesis();
  unsigned int iterNo = 1;

  while (!end && iterNo < MAX_NUM_OF_ITER)
  {
#ifdef THOT_ENABLE_GRAPH
    if ((iterNo % PRINT_GRAPH_STEP) == 0)
    {
      char printGraphFileName[128];
      snprintf(printGraphFileName, 128, "%d.graph_file", iterNo);
      this->printSearchGraph(printGraphFileName);
    }
#endif
    // Select hypothesis to be expanded
    hypsToExpand.clear();
    while (!stack_ptr->empty() && hypsToExpand.size() < I)
    {
      hypsToExpand.push_back(pop());
    }

    if (verbosity > 1)
    {
      std::cerr << std::endl;
      std::cerr << "* IterNo: " << iterNo << std::endl;
      std::cerr << "  Number of queues/hypotheses: " << stack_ptr->size() << std::endl;
      std::cerr << "  hypsToExpand: " << hypsToExpand.size() << std::endl;
    }

#ifdef THOT_STATS
    this->_stack_decoder_stats.pushPerIter = 0;
    ++this->_stack_decoder_stats.numIter;
#endif
    // Finish if there is not any hypothesis to be expanded
    if (hypsToExpand.empty())
      end = true;
    else
    {
      // There are hypotheses to be expanded
      for (unsigned int i = 0; i < hypsToExpand.size(); ++i)
      {
        // If the hypothesis is complete, finish the decoding
        // process, but expand the remaining hypotheses (required by
        // getNextTrans)
        if (smtModel->isComplete(hypsToExpand[i]))
        {
          if (!end)
          {
            // Return the first complete hypothesis as the final
            // translation
            result = hypsToExpand[i];
            end = true;
          }
          else
            push(hypsToExpand[i]);
        }
        else
        {
          // If the hypothesis is not complete, expand it
#ifdef THOT_STATS
          ++this->_stack_decoder_stats.totalExpansionNo;
#endif

          if (verbosity > 1)
          {
            std::cerr << "  Expanding hypothesis: ";
            smtModel->printHyp(hypsToExpand[i], std::cerr);
          }

          std::vector<Hypothesis> expandedHyps;
          std::vector<std::vector<Score>> scrCompVec;
          int numExpHyp = 0;
          smtModel->expand_ver(hypsToExpand[i], expandedHyps, scrCompVec);

          if (verbosity > 1)
            std::cerr << "  Generated " << expandedHyps.size() << " expansions" << std::endl;

          while (!expandedHyps.empty())
          {
            // Push expanded hyp into the stack container
            bool inserted = pushGivenPredHyp(hypsToExpand[i], scrCompVec.back(), expandedHyps.back());

            if (verbosity > 2)
            {
              ++numExpHyp;
              std::cerr << "  Expanded hypothesis " << numExpHyp << " : ";
              smtModel->printHyp(expandedHyps.back(), std::cerr);
              std::cerr << "  (Inserted: " << inserted << ")" << std::endl;
            }

            scrCompVec.pop_back();
            expandedHyps.pop_back();
          }
        }
      }
    }
    ++iterNo;
  }

  if (iterNo >= MAX_NUM_OF_ITER)
    std::cerr << "Maximum number of iterations exceeded!\n";
  return result;
}

template <class SMT_MODEL>
typename _stackDecoder<SMT_MODEL>::Hypothesis _stackDecoder<SMT_MODEL>::decodeWithPrefix(void)
{
  bool end = false;
  std::vector<Hypothesis> hypsToExpand;
  Hypothesis result = smtModel->nullHypothesis();
  unsigned int iterNo = 1;

  while (!end && iterNo < MAX_NUM_OF_ITER)
  {
#ifdef THOT_ENABLE_GRAPH
    if ((iterNo % PRINT_GRAPH_STEP) == 0)
    {
      char printGraphFileName[128];
      snprintf(printGraphFileName, 128, "%d.graph_file", iterNo);
      this->printSearchGraph(printGraphFileName);
    }
#endif
    // Select hypothesis to be expanded
    hypsToExpand.clear();
    while (!stack_ptr->empty() && hypsToExpand.size() < I)
    {
      hypsToExpand.push_back(pop());
    }

    if (verbosity > 1)
    {
      std::cerr << std::endl;
      std::cerr << "* IterNo: " << iterNo << std::endl;
      std::cerr << "  Number of queues/hypotheses: " << stack_ptr->size() << std::endl;
      std::cerr << "  hypsToExpand: " << hypsToExpand.size() << std::endl;
    }

#ifdef THOT_STATS
    this->_stack_decoder_stats.pushPerIter = 0;
    ++this->_stack_decoder_stats.numIter;
#endif
    // Finish if there is not any hypothesis to be expanded
    if (hypsToExpand.empty())
      end = true;
    else
    {
      // There are hypotheses to be expanded
      for (unsigned int i = 0; i < hypsToExpand.size(); ++i)
      {
        // If the hypothesis is complete, finish the decoding
        // process, but expand the remaining hypotheses (required by
        // getNextTrans)
        if (smtModel->isComplete(hypsToExpand[i]))
        {
          if (!end)
          {
            // Return the first complete hypothesis as the final
            // translation
            result = hypsToExpand[i];
            end = true;
          }
          else
            push(hypsToExpand[i]);
        }
        else
        {
          // If the hypothesis is not complete, expand it
#ifdef THOT_STATS
          ++this->_stack_decoder_stats.totalExpansionNo;
#endif

          if (verbosity > 1)
          {
            std::cerr << "  Expanding hypothesis: ";
            smtModel->printHyp(hypsToExpand[i], std::cerr);
          }

          std::vector<Hypothesis> expandedHyps;
          std::vector<std::vector<Score>> scrCompVec;
          int numExpHyp = 0;
          smtModel->expand_prefix(hypsToExpand[i], expandedHyps, scrCompVec);

          if (verbosity > 1)
            std::cerr << "  Generated " << expandedHyps.size() << " expansions" << std::endl;

          while (!expandedHyps.empty())
          {
            // Push expanded hyp into the stack container
            bool inserted = pushGivenPredHyp(hypsToExpand[i], scrCompVec.back(), expandedHyps.back());

            if (verbosity > 2)
            {
              ++numExpHyp;
              std::cerr << "  Expanded hypothesis " << numExpHyp << " : ";
              smtModel->printHyp(expandedHyps.back(), std::cerr);
              std::cerr << "  (Inserted: " << inserted << ")" << std::endl;
            }

            scrCompVec.pop_back();
            expandedHyps.pop_back();
          }
        }
      }
    }
    ++iterNo;
  }

  if (iterNo >= MAX_NUM_OF_ITER)
    std::cerr << "Maximum number of iterations exceeded!\n";
  return result;
}

template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::setVerbosity(int _verbosity)
{
  verbosity = _verbosity;
}

template <class SMT_MODEL>
_stackDecoder<SMT_MODEL>::~_stackDecoder()
{
}

#ifdef THOT_STATS
template <class SMT_MODEL>
void _stackDecoder<SMT_MODEL>::printStats(void)
{
  _stack_decoder_stats.print(std::cerr);
  std::cerr << " * Push op's aborted due to S     : " << stack_ptr->discardedPushOpsDueToSize << std::endl;
  std::cerr << " * Push op's aborted due to rec.  : " << stack_ptr->discardedPushOpsDueToRec << std::endl;
  smtm_ptr->printStats(std::cerr);
}
#endif
