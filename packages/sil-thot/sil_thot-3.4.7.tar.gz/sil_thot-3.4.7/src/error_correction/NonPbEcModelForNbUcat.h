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
 * @file NonPbEcModelForNbUcat.h
 *
 * @brief Defines the NonPbEcModelForNbUcat class, this class implements
 * a non phrase-based error correcting model for uncoupled computer
 * assisted translation based on n-best lists.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "error_correction/BaseEcModelForNbUcat.h"
#include "error_correction/BaseErrorCorrectionModel.h"
#include "error_correction/PrefAlignInfo.h"
#include "nlp_common/Prob.h"

#include <iomanip>
#include <iostream>
#include <map>
#include <string>
#include <vector>

//--------------- Constants ------------------------------------------

//--------------- Classes --------------------------------------------

//--------------- NonPbEcModelForNbUcat template class

/**
 * @brief The NonPbEcModelForNbUcat class aligns implements a non
 * phrase-based error correcting model for uncoupled computer assisted
 * translation based on n-best lists.
 */

class NonPbEcModelForNbUcat : public BaseEcModelForNbUcat
{
public:
  // Constructor
  NonPbEcModelForNbUcat();

  // Link error correcting model with the error correcting model for
  // uncoupled cat
  void link_ecm(BaseErrorCorrectionModel* _ecm_ptr);

  NbestCorrections correct(const std::vector<std::string>& outputSentVec, const std::vector<unsigned int>& sourceCuts,
                           const std::vector<std::string>& prefixVec, unsigned int _maxMapSize, int verbose = 0);
  // Correct sentence given in outputSentVec using prefixVec. The
  // basic units for the corrections can be restricted by means of
  // sourceCuts, which contains a vector of cuts for
  // outputSentVec. Set one cut per word for unrestricted correction

  // clear() function
  void clear(void);

  // Clear temporary variables
  void clearTempVars(void);

  // Destructor
  ~NonPbEcModelForNbUcat();

protected:
  typedef std::multimap<LgProb, PrefAlignInfo, std::greater<LgProb>> MonolingSegmNbest;

  std::vector<std::string> outputSentVec;
  std::vector<unsigned int> sourceCuts;
  std::vector<std::vector<std::string>> outputSegmVec;
  std::vector<std::string> prefixVec;
  unsigned int maxMapSize;
  MonolingSegmNbest monolingSegmNbest;

  BaseErrorCorrectionModel* ecm_ptr;

  MonolingSegmNbest nonPhraseBasedAlign(const std::vector<std::string>& _outputSentVec,
                                        const std::vector<std::string>& _prefixVec, unsigned int _maxMapSize,
                                        int verbose = 0);
  std::vector<std::string> correctedSent(PrefAlignInfo& prefAlignInfo);
  std::vector<std::vector<std::string>> obtainVectorWithSegms(std::vector<std::string> sentVec,
                                                              std::vector<unsigned int> cuts, int verbose = 0);
  void addSegm(LgProb lp, PrefAlignInfo& prefAlignInfo);
  void removeLastFromMonolingSegmNbest(void);
  void getLastOutSegm(std::vector<std::string>& x, std::vector<unsigned int>& cuts,
                      std::vector<std::string>& lastOutSegm);
};
