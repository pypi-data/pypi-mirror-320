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
 * @file BasePhraseModel.h
 *
 * @brief Defines the BasePhraseModel abstract base class.
 * BasePhraseModel class provides basic functionality to be extended in
 * specific phrase models.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "nlp_common/AwkInputStream.h"
#include "nlp_common/ErrorDefs.h"
#include "nlp_common/MathDefs.h"
#include "phrase_models/BasePhraseTable.h"
#include "phrase_models/PhraseDefs.h"

#include <string>
#include <vector>

//--------------- Constants ------------------------------------------

//--------------- typedefs -------------------------------------------

//--------------- Classes --------------------------------------------

//--------------- BasePhraseModel class

class BasePhraseModel
{
public:
  typedef BasePhraseTable::SrcTableNode SrcTableNode;
  typedef BasePhraseTable::TrgTableNode TrgTableNode;

  // Declarations related to dynamic class loading
  typedef BasePhraseModel* create_t(const char*);
  typedef const char* type_id_t(void);

  // Thread/Process safety related functions
  virtual bool modelReadsAreProcessSafe(void);

  // Functions to access model probabilities

  virtual Prob pk_tlen(unsigned int tlen, unsigned int k) = 0;
  // Returns p(k|tlen), k-> segmentation length, tlen-> length of the
  // target sentence

  virtual LgProb srcSegmLenLgProb(unsigned int x_k, unsigned int x_km1, unsigned int srcLen) = 0;
  // obtains the log-probability for the length of a source
  // segment log(p(x_k|x_{k-1},srcLen))

  virtual LgProb trgCutsLgProb(int offset) = 0;
  // Returns phrase alignment log-probability given the offset
  // between the last target phrase and the new one
  // log(p(y_k|y_{k-1}))

  virtual LgProb trgSegmLenLgProb(unsigned int k, const SentSegmentation& trgSegm, unsigned int trgLen,
                                  unsigned int lastSrcSegmLen) = 0;
  // obtains the log-probability for the length of a target
  // segment log(p(z_k|y_k,x_k-x_{k-1},trgLen))

  virtual Prob strPt_s_(const std::vector<std::string>& s, const std::vector<std::string>& t);
  virtual LgProb strLogpt_s_(const std::vector<std::string>& s, const std::vector<std::string>& t);
  virtual Prob pt_s_(const std::vector<WordIndex>& s, const std::vector<WordIndex>& t);
  virtual LgProb logpt_s_(const std::vector<WordIndex>& s, const std::vector<WordIndex>& t) = 0;

  virtual Prob strPs_t_(const std::vector<std::string>& s, const std::vector<std::string>& t);
  virtual LgProb strLogps_t_(const std::vector<std::string>& s, const std::vector<std::string>& t);
  virtual Prob ps_t_(const std::vector<WordIndex>& s, const std::vector<WordIndex>& t);
  virtual LgProb logps_t_(const std::vector<WordIndex>& s, const std::vector<WordIndex>& t) = 0;

  // Functions to obtain translations for source or target phrases
  virtual bool strGetTransFor_s_(const std::vector<std::string>& s, TrgTableNode& trgtn);
  virtual bool getTransFor_s_(const std::vector<WordIndex>& s, TrgTableNode& trgtn) = 0;
  virtual bool strGetTransFor_t_(const std::vector<std::string>& t, SrcTableNode& srctn);
  virtual bool getTransFor_t_(const std::vector<WordIndex>& t, SrcTableNode& srctn) = 0;
  virtual bool strGetNbestTransFor_s_(const std::vector<std::string>& s, NbestTableNode<PhraseTransTableNodeData>& nbt);
  virtual bool getNbestTransFor_s_(const std::vector<WordIndex>& s, NbestTableNode<PhraseTransTableNodeData>& nbt) = 0;
  virtual bool strGetNbestTransFor_t_(const std::vector<std::string>& t, NbestTableNode<PhraseTransTableNodeData>& nbt,
                                      int N = -1);
  virtual bool getNbestTransFor_t_(const std::vector<WordIndex>& t, NbestTableNode<PhraseTransTableNodeData>& nbt,
                                   int N = -1) = 0;

  // Functions for extending the model
  virtual int trainSentPair(const std::vector<std::string>& srcSentStrVec,
                            const std::vector<std::string>& trgSentStrVec, Count c = 1, int verbose = 0);
  virtual int trainBilPhrases(const std::vector<std::vector<std::string>>& srcPhrVec,
                              const std::vector<std::vector<std::string>>& trgPhrVec, Count c = 1, Count lowerBound = 0,
                              int verbose = 0);

  // Loading functions
  virtual bool load(const char* prefix, int verbose = 0) = 0;

  // Printing functions
  virtual bool print(const char* prefix) = 0;

  // Source vocabulary functions
  virtual size_t getSrcVocabSize(void) const = 0;
  // Returns the source vocabulary size
  virtual WordIndex stringToSrcWordIndex(std::string s) const = 0;
  virtual std::string wordIndexToSrcString(WordIndex w) const = 0;
  virtual bool existSrcSymbol(std::string s) const = 0;
  virtual WordIndex addSrcSymbol(std::string s) = 0;
  virtual bool loadSrcVocab(const char* srcInputVocabFileName, int verbose = 0) = 0;
  // loads source vocabulary, returns non-zero if error
  virtual bool printSrcVocab(const char* outputFileName) = 0;

  // Target vocabulary functions
  virtual size_t getTrgVocabSize(void) const = 0;
  // Returns the target vocabulary size
  virtual WordIndex stringToTrgWordIndex(std::string t) const = 0;
  virtual std::string wordIndexToTrgString(WordIndex w) const = 0;
  virtual bool existTrgSymbol(std::string t) const = 0;
  virtual WordIndex addTrgSymbol(std::string t) = 0;
  virtual bool loadTrgVocab(const char* trgInputVocabFileName, int verbose = 0) = 0;
  // loads target vocabulary, returns non-zero if error
  virtual bool printTrgVocab(const char* outputFileName) = 0;

  // size and clear functions
  virtual size_t size(void) = 0;
  virtual void clear(void) = 0;
  virtual void clearTempVars(void)
  {
  }

  virtual ~BasePhraseModel(){};

protected:
};

