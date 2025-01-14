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
 * @file BaseNgramLM.h
 *
 * @brief Abstract class to manage n-gram language models.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "nlp_common/AwkInputStream.h"
#include "nlp_common/ErrorDefs.h"
#include "nlp_common/LM_Defs.h"
#include "nlp_common/MathDefs.h"

#include <string>
#include <vector>

//--------------- Constants ------------------------------------------

//--------------- typedefs -------------------------------------------

//--------------- function declarations ------------------------------

//--------------- Classes --------------------------------------------

//--------------- BaseNgramLM class

template <class LM_STATE>
class BaseNgramLM
{
public:
  typedef LM_STATE LM_State;

  // Declarations related to dynamic class loading
  typedef BaseNgramLM* create_t(const char*);
  typedef const char* type_id_t(void);

  // Thread/Process safety related functions
  virtual bool modelReadsAreProcessSafe(void);

  // Probability functions
  virtual LgProb getNgramLgProb(WordIndex w, const std::vector<WordIndex>& vu) = 0;
  // returns the probability of an n-gram, uv[0] stores the n-1'th
  // word of the n-gram, uv[1] the n-2'th one and so on
  virtual LgProb getNgramLgProbStr(std::string s, const std::vector<std::string>& rq) = 0;
  // returns the probability of an n-gram. Each string represents a
  // single word
  virtual LgProb getLgProbEnd(const std::vector<WordIndex>& vu) = 0;
  virtual LgProb getLgProbEndStr(const std::vector<std::string>& rq) = 0;
  virtual Prob getZeroGramProb(void);

  // Probability functions using states
  virtual bool getStateForWordSeq(const std::vector<WordIndex>& wordSeq, LM_STATE& state) = 0;
  virtual void getStateForBeginOfSentence(LM_STATE& state) = 0;
  virtual void addNextWordToState(WordIndex word, LM_State& state);
  virtual LgProb getNgramLgProbGivenState(WordIndex w, LM_STATE& state) = 0;
  virtual LgProb getNgramLgProbGivenStateStr(std::string s, LM_STATE& state) = 0;
  virtual LgProb getLgProbEndGivenState(LM_STATE& state) = 0;
  // In these functions, the state is updated once the
  // function is executed

  // Encoding-related functions
  virtual bool existSymbol(std::string s) const = 0;
  virtual WordIndex addSymbol(std::string s) = 0;
  virtual unsigned int getVocabSize(void) = 0;
  virtual WordIndex stringToWordIndex(std::string s) const = 0;
  virtual std::string wordIndexToString(WordIndex w) const = 0;
  virtual WordIndex getBosId(bool& found) const = 0;
  virtual WordIndex getEosId(bool& found) const = 0;
  virtual bool loadVocab(const char* fileName) = 0;
  // Load encoding information given a prefix file name
  virtual bool printVocab(const char* fileName) = 0;
  // Prints encoding information
  virtual void clearVocab(void) = 0;
  // Clears encoding information

  // Functions to obtain probability for a given sentence
  virtual LgProb getSentenceLog10Prob(std::vector<WordIndex> s, int verbose = 0);
  // Calculates the log-probability of the sentence 's' given as a
  // WordIndex vector
  virtual LgProb getSentenceLog10ProbStr(std::vector<std::string> s, int verbose = 0);
  // Calculates the log-probability of the sentence 's' given as a
  // string vector
  // Functions to obtain perplexity for a given corpus
  virtual int perplexity(const char* corpusFileName, unsigned int& numOfSentences, unsigned int& numWords,
                         LgProb& totalLogProb, double& perp, int verbose = 0);

  // Functions to extend the model
  virtual int trainSentence(std::vector<std::string> strVec, Count c = 1, Count lowerBound = 0, int verbose = 0);

  virtual int trainSentenceVec(std::vector<std::vector<std::string>> vecOfStrVec, Count c = 1, Count lowerBound = 0,
                               int verbose = 0);

  // Functions to load and print the model
  virtual bool load(const char* fileName, int verbose = 0) = 0;
  virtual bool print(const char* fileName) = 0;
  virtual unsigned int getNgramOrder(void) = 0;
  virtual void setNgramOrder(int _ngramOrder) = 0;

  // size and clear functions
  virtual size_t size(void) = 0;
  virtual void clear(void) = 0;
  virtual void clearTempVars(void)
  {
  }

  // Destructor
  virtual ~BaseNgramLM(){};
};

//--------------- Template function definitions

//---------------
template <class LM_STATE>
bool BaseNgramLM<LM_STATE>::modelReadsAreProcessSafe(void)
{
  // By default it will be assumed that model reads are thread safe,
  // those unsafe classes will override this method returning false
  // instead
  return true;
}

//---------------
template <class LM_STATE>
Prob BaseNgramLM<LM_STATE>::getZeroGramProb(void)
{
  return (double)1 / getVocabSize();
}

//---------------
template <class LM_STATE>
void BaseNgramLM<LM_STATE>::addNextWordToState(WordIndex word, LM_State& state)
{
  this->getNgramLgProbGivenState(word, state);
}

//---------------
template <class LM_STATE>
LgProb BaseNgramLM<LM_STATE>::getSentenceLog10ProbStr(std::vector<std::string> s, int verbose /*=false*/)
{
  std::vector<WordIndex> vwi;

  for (unsigned int i = 0; i < s.size(); ++i)
  {
    vwi.push_back(stringToWordIndex(s[i]));
  }
  return getSentenceLog10Prob(vwi, verbose);
}
//---------------
template <class LM_STATE>
LgProb BaseNgramLM<LM_STATE>::getSentenceLog10Prob(std::vector<WordIndex> s, int verbose /*=false*/)
{
  LgProb lp;
  LgProb total_lp = 0;
  std::vector<WordIndex> hist, aux;
  int i, j, k;
  LM_STATE state;
  unsigned int ngram_order = getNgramOrder();
  bool found;

  getStateForBeginOfSentence(state);
  for (i = 0; i < (int)s.size(); ++i)
    aux.push_back(s[s.size() - 1 - i]);
  s = aux;
  for (i = (int)s.size() - 1; i >= 0; --i)
  {
    hist.clear();
    for (j = 1; j < (int)ngram_order; ++j)
    {
      if (i + j >= (int)s.size())
        hist.push_back(getBosId(found));
      else
        hist.push_back(s[i + j]);
    }
    lp = getNgramLgProbGivenState(s[i], state);
    total_lp = total_lp + lp;

    if (verbose)
    {
      std::cerr << "   P( " << wordIndexToString(s[i]) << " | ";
      for (k = 0; k < (int)hist.size(); ++k)
        std::cerr << wordIndexToString(hist[hist.size() - 1 - k]) << " ";
      std::cerr << ") = " << exp((double)lp) << " " << exp((double)total_lp) << "\n";
    }
  }
  hist.clear();

  for (j = 0; j < (int)ngram_order - 1; ++j)
  {
    if (j >= (int)s.size())
      hist.push_back(getBosId(found));
    else
      hist.push_back(s[j]);
  }
  lp = getLgProbEndGivenState(state);
  total_lp = total_lp + lp;

  if (verbose)
  {
    std::cerr << "   P( " << EOS_STR << " | ";
    for (k = 0; k < (int)hist.size(); ++k)
      std::cerr << wordIndexToString(hist[hist.size() - 1 - k]) << " ";
    std::cerr << ") = " << exp((double)lp) << " " << exp((double)total_lp) << "\n";
  }

  return total_lp * ((double)1 / M_LN10);
}

//---------------
template <class LM_STATE>
int BaseNgramLM<LM_STATE>::perplexity(const char* corpusFileName, unsigned int& numOfSentences, unsigned int& numWords,
                                      LgProb& totalLogProb, double& perp, int verbose)
{
  LgProb logp;
  totalLogProb = 0;
  AwkInputStream awk;
  std::vector<std::string> v;
  numWords = 0;
  numOfSentences = 0;

  // Open corpus file
  if (awk.open(corpusFileName) == THOT_ERROR)
  {
    std::cerr << "Error while opening corpus file " << corpusFileName << std::endl;
    return THOT_ERROR;
  }

  while (awk.getln())
  {
    // Process each sentence
    if (awk.NF >= 1)
    {
      numWords += awk.NF;

      if (verbose == 2)
        std::cerr << "*** Sentence " << numOfSentences << std::endl;

      // Store the sentence into the vector "v"
      v.clear();
      for (unsigned int i = 1; i <= awk.NF; ++i)
      {
        v.push_back(awk.dollar(i));
      }
      // Calculate the probability of the sentence
      if (verbose > 0)
        logp = getSentenceLog10ProbStr(v, verbose - 1);
      else
        logp = getSentenceLog10ProbStr(v, verbose);
      if (verbose == 1)
      {
        std::cerr << logp << " ";
        for (unsigned int i = 0; i < v.size(); ++i)
        {
          if (i < v.size() - 1)
            std::cerr << v[i] << " ";
          else
            std::cerr << v[i] << std::endl;
        }
      }
    }
    totalLogProb += logp;
    ++numOfSentences;
  }

  perp = exp(-((double)totalLogProb / (numWords + numOfSentences)) * M_LN10);

  return THOT_OK;
}

//---------------
template <class LM_STATE>
int BaseNgramLM<LM_STATE>::trainSentence(std::vector<std::string> /*strVec*/, Count /*c=1*/, Count /*lowerBound=0*/,
                                         int /*verbose=0*/)
{
  std::cerr << "Warning: lm training of a sentence was requested, but such functionality is not provided!" << std::endl;
  return THOT_ERROR;
}

//---------------
template <class LM_STATE>
int BaseNgramLM<LM_STATE>::trainSentenceVec(std::vector<std::vector<std::string>> /*vecOfStrVec*/, Count /*c=1*/,
                                            Count /*lowerBound=0*/, int /*verbose=0*/)
{
  std::cerr << "Warning: lm training of a sentence vector was requested, but such functionality is not provided!"
            << std::endl;
  return THOT_ERROR;
}
