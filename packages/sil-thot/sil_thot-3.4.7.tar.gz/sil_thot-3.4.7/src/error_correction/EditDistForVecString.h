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
 * @file EditDistForVecString.h
 *
 * @brief Defines the EditDistForVec class that calculates the edit
 * distance between vectors of strings.  Such edit distance is the same
 * that can be calculated by means of the EditDistForStr class, but here
 * the words are the smallest units to be used in edit operations. Blank
 * characters are appended at the right side of each word.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "error_correction/EditDistForStr.h"
#include "error_correction/EditDistForVec.h"
#include "nlp_common/StrProcUtils.h"

#include <map>
#include <string>

//--------------- Constants ------------------------------------------

//--------------- Type definitions -----------------------------------

typedef std::map<std::pair<std::string, std::string>, Score> SubstCostMap;

//--------------- Classes --------------------------------------------

//--------------- EditDistForVecString class declaration

class EditDistForVecString : public EditDistForVec<std::string>
{
public:
  EditDistForVecString(void);

  Score calculateEditDist(const std::vector<std::string>& x, const std::vector<std::string>& y, int verbose = 0);
  // Calculates edit distance between strings x and y (operations
  // to transform x into y)

  Score calculateEditDistPrefix(const std::vector<std::string>& x, const std::vector<std::string>& y, int verbose = 0);
  // Calculates edit distance between x and y and returns edit
  // distance between x and y, given that y is an incomplete prefix

  Score calculateEditDistPrefixOps(const std::vector<std::string>& x, const std::vector<std::string>& y,
                                   std::vector<unsigned int>& opsWordLevel, std::vector<unsigned int>& opsCharLevel,
                                   int verbose = 0);
  // The same as the previous function, but it also returns the
  // sequence of string operations at both the word level and the
  // character level

  Score calculateEditDistPrefixOpsNoPrefDel(const std::vector<std::string>& x, const std::vector<std::string>& y,
                                            std::vector<unsigned int>& opsWordLevel,
                                            std::vector<unsigned int>& opsCharLevel, int verbose = 0);
  // The same as the previous function, but the special PREF_DEL_OP
  // operation is not allowed

  void incrEditDistPrefixFirstRow(const std::vector<std::string>& incr_y, const std::vector<Score> prevScoreVec,
                                  std::vector<Score>& newScoreVec);
  // Incrementally calculates the first row of the edit distance
  // matrix

  void incrEditDistPrefix(const std::string& xWord, const std::vector<std::string>& incr_y,
                          const std::vector<Score> prevScoreVec, std::vector<Score>& newScoreVec,
                          std::vector<int>& opIdVec);
  // Incrementally calculates edit distance given xWord, incr_y,
  // previous vector of costs and new partially calculated vector of
  // costs

  void incrEditDistPrefixCached(const std::string& xWord, const std::vector<std::string>& incr_y,
                                const std::vector<Score> prevScoreVec, SubstCostMap& substCostMap,
                                std::vector<Score>& newScoreVec, std::vector<int>& opIdVec);
  // Incrementally calculates edit distance given xWord, incr_y,
  // previous vector of costs and new partially calculated vector of
  // costs (uses substCostMap to cache subsitution costs)

  void setErrorModel(Score _hitCost, Score _insCost, Score _substCost, Score _delCost);
  // Sets the cost of each operation (insertions, deletions and
  // substitutions)

  ~EditDistForVecString(void);

protected:
  EditDistForStr editDistForStr;

  Score processMatrixCell(const std::vector<std::string>& x, const std::vector<std::string>& y, const DistMatrix& dm,
                          int i, int j, int& pred_i, int& pred_j, int& op_id);
  // Basic function to calculate edit distance

  Score processMatrixCellPref(const std::vector<std::string>& x, const std::vector<std::string>& y,
                              const DistMatrix& dm, SubstCostMap& substCostMap, bool lastWordIsComplete,
                              bool usePrefDelOp, int i, int j, int& pred_i, int& pred_j, int& op_id);
  // Basic function to calculate edit distance given a prefix

  void obtainOperationsPref(const std::vector<std::string>& x, const std::vector<std::string>& y, const DistMatrix& dm,
                            bool lastWordIsComplete, bool usePrefDelOp, int i, int j,
                            std::vector<unsigned int>& opsWordLevel, std::vector<unsigned int>& opsCharLevel,
                            std::vector<Score>& opCosts);
  // After an edit distance calculation given a prefix, this
  // function obtains the optimal sequence of operations.

  void addBlankCharacters(std::vector<std::string> strVec);

  inline Score insertionCost(const std::string& s)
  {
#ifdef EDIT_DIST_FAST_ED_VECSTR
    return insCost;
#else
    return insCost * s.size();
#endif
  }

  inline Score deletionCost(const std::string& s)
  {
#ifdef EDIT_DIST_FAST_ED_VECSTR
    return delCost;
#else
    return delCost * s.size();
#endif
  }

  Score cachedSubstCost(std::string xWord, std::string yWord, SubstCostMap& substCostMap);

  inline Score substitutionCost(const std::string& x, const std::string& y)
  {
#ifdef EDIT_DIST_FAST_ED_VECSTR
    if (x == y)
      return hitCost;
    else
      return substCost;
#else
    unsigned int hCount;
    unsigned int iCount;
    unsigned int sCount;
    unsigned int dCount;

    editDistForStr.calculateEditDistOps(x, y, hCount, iCount, sCount, dCount);
    return hitCost * hCount + insCost * iCount + substCost * sCount + delCost * dCount;
#endif
  }

  Score cachedPrefSubstCost(std::string xWord, std::string yWord, SubstCostMap& substCostMap);

  inline Score prefSubstitutionCost(const std::string& x, const std::string& y)
  {
#ifdef EDIT_DIST_FAST_ED_VECSTR
    if (StrProcUtils::isPrefix(y, x))
      return hitCost;
    else
      return substCost;
#else
    // Obtain edit distance for prefix
    std::vector<unsigned int> ops;
    editDistForStr.calculateEditDistPrefixOps(x, y, ops);

    // Obtain operation counts
    std::vector<unsigned int> opsPerType;
    countOpsGivenOpVec(ops, opsPerType);
    unsigned int hCount = opsPerType[HIT_OP];
    unsigned int iCount = opsPerType[INS_OP];
    unsigned int sCount = opsPerType[SUBST_OP];
    unsigned int dCount = opsPerType[DEL_OP];

    // Return substitution cost
    return hitCost * hCount + insCost * iCount + substCost * sCount + delCost * dCount;
#endif
  }

  Score calculateEditDistPrefixOpsAux(const std::vector<std::string>& x, const std::vector<std::string>& y,
                                      std::vector<unsigned int>& opsWordLevel, std::vector<unsigned int>& opsCharLevel,
                                      bool usePrefDelOp, int verbose = 0);
  // Auxiliary function for calculateEditDistPrefixOps
};

