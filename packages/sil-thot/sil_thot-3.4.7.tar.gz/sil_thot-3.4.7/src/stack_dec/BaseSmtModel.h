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
#include "nlp_common/Bitset.h"
#include "nlp_common/Count.h"
#include "nlp_common/ErrorDefs.h"
#include "nlp_common/PositionIndex.h"
#include "nlp_common/Score.h"
#include "stack_dec/OnlineTrainingPars.h"

#include <fstream>
#include <iomanip>
#include <iostream>
#include <set>
#include <string>
#include <utility>
#include <vector>

/**
 * @brief Base abstract class that defines the interface that a
 * statistical machine translation model should offer to a stack-based
 * decoder.
 */
template <class HYPOTHESIS>
class BaseSmtModel
{
public:
  typedef HYPOTHESIS Hypothesis;
  typedef typename HYPOTHESIS::ScoreInfo HypScoreInfo;
  typedef typename HYPOTHESIS::DataType HypDataType;

  // Virtual object copy
  virtual BaseSmtModel<HYPOTHESIS>* clone() = 0;

  // Actions to be executed before the translation and before using
  // hypotheses-related functions
  virtual void pre_trans_actions(std::string srcsent) = 0;
  virtual void pre_trans_actions_ref(std::string srcsent, std::string refsent) = 0;
  virtual void pre_trans_actions_ver(std::string srcsent, std::string refsent) = 0;
  virtual void pre_trans_actions_prefix(std::string srcsent, std::string prefix) = 0;

  ////// Hypotheses-related functions

  // Heuristic-related functions
  virtual void addHeuristicToHyp(Hypothesis& hyp);
  virtual void subtractHeuristicToHyp(Hypothesis& hyp);

  // Expansion-related functions
  virtual void expand(const Hypothesis& hyp, std::vector<Hypothesis>& hypVec,
                      std::vector<std::vector<Score>>& scrCompVec) = 0;
  virtual void expand_ref(const Hypothesis& hyp, std::vector<Hypothesis>& hypVec,
                          std::vector<std::vector<Score>>& scrCompVec) = 0;
  virtual void expand_ver(const Hypothesis& hyp, std::vector<Hypothesis>& hypVec,
                          std::vector<std::vector<Score>>& scrCompVec) = 0;
  virtual void expand_prefix(const Hypothesis& hyp, std::vector<Hypothesis>& hypVec,
                             std::vector<std::vector<Score>>& scrCompVec) = 0;

  // Misc. operations with hypothesis
  virtual Hypothesis nullHypothesis() = 0;
  virtual HypDataType nullHypothesisHypData() = 0;
  virtual void obtainHypFromHypData(const HypDataType& hypDataType, Hypothesis& hyp) = 0;
  virtual bool obtainPredecessor(Hypothesis& hyp) = 0;
  // The obtainPredecessor() function obtains the predecessor
  // hypothesis for hyp. This function is required only for the
  // generation of search graphs
  virtual bool obtainPredecessorHypData(HypDataType& hypd) = 0;
  // The obtainPredecessorHypData() function obtains the predecessor
  // data for hypd. This function is required only for the
  // generation of search graphs
  virtual bool isComplete(const Hypothesis& hyp) const;
  virtual bool isCompleteHypData(const HypDataType& hypd) const = 0;
  virtual unsigned int distToNullHyp(const Hypothesis& hyp) = 0;

  // Printing functions and data conversion
  virtual void printHyp(const Hypothesis& hyp, std::ostream& outS, int verbose = false) = 0;
  virtual unsigned int partialTransLength(const Hypothesis& hyp) const = 0;
  virtual std::vector<std::string> getTransInPlainTextVec(const Hypothesis& hyp) const = 0;
  virtual std::vector<std::string> getTransInPlainTextVec(const Hypothesis& hyp,
                                                          std::set<unsigned int>& unknownWords) const = 0;
  virtual std::string getTransInPlainText(const Hypothesis& hyp) const;

  // IMPORTANT NOTE: Before using the hypothesis-related functions
  // it is mandatory the previous invocation of one of the
  // pre_trans_actionsXXXX functions

  // Model weights functions
  virtual void setWeights(std::vector<float> wVec) = 0;
  virtual void getWeights(std::vector<std::pair<std::string, float>>& compWeights);
  virtual unsigned int getNumWeights() = 0;
  virtual void printWeights(std::ostream& outS) = 0;
  virtual std::vector<Score> scoreCompsForHyp(const Hypothesis& hyp) = 0;
  // Returns the score components for a given hypothesis. This
  // function is a service for users of the model and it is not
  // required for the decoding process
  virtual Score getScoreForHyp(const Hypothesis& hyp) = 0;
  virtual void diffScoreCompsForHyps(const Hypothesis& pred_hyp, const Hypothesis& succ_hyp,
                                     std::vector<Score>& scoreComponents) = 0;
  virtual void getUnweightedComps(const std::vector<Score>& scrComps, std::vector<Score>& unweightedScrComps) = 0;

  // Functions for performing on-line training
  virtual void setOnlineTrainingPars(OnlineTrainingPars _onlineTrainingPars, int verbose = 0);
  virtual int onlineTrainFeatsSentPair(const char* srcSent, const char* refSent, const char* sysSent, int verbose = 0);

  // Word prediction functions
  virtual void addSentenceToWordPred(std::vector<std::string> strVec, int verbose = 0);
  // Add a new sentence to the word predictor
  virtual std::pair<Count, std::string> getBestSuffix(std::string input);
  // Returns a suffix that completes the input string. This function
  // is required for assisted translation purposes
  virtual std::pair<Count, std::string> getBestSuffixGivenHist(std::vector<std::string> hist, std::string input);
  // The same as the previous function, but the suffix is generated
  // taking into account a vector of prefix words that goes before
  // the string input. This function is required for assisted
  // translation purposes

  // Destructor
  virtual ~BaseSmtModel(){};
};

template <class HYPOTHESIS>
void BaseSmtModel<HYPOTHESIS>::getWeights(std::vector<std::pair<std::string, float>>& /*compWeights*/)
{
  std::cerr << "Warning: the functionality provided by getWeights() is not implemented in this class" << std::endl;
}

template <class HYPOTHESIS>
void BaseSmtModel<HYPOTHESIS>::addHeuristicToHyp(Hypothesis& /*hyp*/)
{
}

template <class HYPOTHESIS>
void BaseSmtModel<HYPOTHESIS>::subtractHeuristicToHyp(Hypothesis& /*hyp*/)
{
}

template <class HYPOTHESIS>
bool BaseSmtModel<HYPOTHESIS>::isComplete(const Hypothesis& hyp) const
{
  if (isCompleteHypData(hyp.getData()))
    return true;
  else
    return false;
}

template <class HYPOTHESIS>
std::string BaseSmtModel<HYPOTHESIS>::getTransInPlainText(const Hypothesis& hyp) const
{
  std::string s;
  std::vector<std::string> svec;

  svec = getTransInPlainTextVec(hyp);
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
void BaseSmtModel<HYPOTHESIS>::setOnlineTrainingPars(OnlineTrainingPars /*onlineTrainingPars*/, int /*verbose*/)

{
  std::cerr << "Warning: setting of online training parameters was requested, but such functionality is not provided!"
            << std::endl;
}

template <class HYPOTHESIS>
int BaseSmtModel<HYPOTHESIS>::onlineTrainFeatsSentPair(const char* /*srcSent*/, const char* /*refSent*/,
                                                       const char* /*sysSent*/, int /*verbose*/)
{
  std::cerr << "Warning: training of a sentence pair was requested, but such functionality is not provided!"
            << std::endl;
  return THOT_ERROR;
}

template <class HYPOTHESIS>
void BaseSmtModel<HYPOTHESIS>::addSentenceToWordPred(std::vector<std::string> /*strVec*/, int /*verbose=0*/)
{
  /* This function is left void */
}

template <class HYPOTHESIS>
std::pair<Count, std::string> BaseSmtModel<HYPOTHESIS>::getBestSuffix(std::string /*input*/)
{
  return std::make_pair(0, "");
}

template <class HYPOTHESIS>
std::pair<Count, std::string> BaseSmtModel<HYPOTHESIS>::getBestSuffixGivenHist(std::vector<std::string> /*hist*/,
                                                                               std::string /*input*/)
{
  return std::make_pair(0, "");
}
