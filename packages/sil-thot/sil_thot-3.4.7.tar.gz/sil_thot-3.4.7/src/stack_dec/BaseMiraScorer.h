/*
thot package for statistical machine translation

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
 * @file BaseMiraScorer.h
 *
 * @brief Base class defining the interface of MIRA scorers.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "stack_dec/BaseScorer.h"

#include <string>
#include <vector>

//--------------- Classes --------------------------------------------

//--------------- BaseMiraScorer class

/**
 * @brief Base class to implement MIRA scorers.
 */

class BaseMiraScorer : public BaseScorer
{
public:
  // Functions to manage background corpus
  virtual void resetBackgroundCorpus() = 0;
  virtual void updateBackgroundCorpus(const std::vector<unsigned int>& stats, double decay) = 0;

  // Score for sentence with background corpus stats
  virtual void sentBackgroundScore(const std::string& candidate, const std::string& reference, double& score,
                                   std::vector<unsigned int>& stats) = 0;

  // Score for corpus
  virtual void corpusScore(const std::vector<std::string>& candidates, const std::vector<std::string>& references,
                           double& score) = 0;

  // Score for sentence
  virtual void sentScore(const std::string& candidate, const std::string& reference, double& score) = 0;

  // Destructor
  virtual ~BaseMiraScorer(){};
};

