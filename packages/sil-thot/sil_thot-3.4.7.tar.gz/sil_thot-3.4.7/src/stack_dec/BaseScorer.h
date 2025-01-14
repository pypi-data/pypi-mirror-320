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
 * @file BaseScorer.h
 *
 * @brief Declares the BaseScorer abstract template class, this class is
 * a base class for implementing scorer classes.
 */

#pragma once

//--------------- Include files --------------------------------------

#include <string>
#include <utility>
#include <vector>

//--------------- Constants ------------------------------------------

//--------------- typedefs -------------------------------------------

//--------------- Classes --------------------------------------------

//--------------- BaseScorer class

class BaseScorer
{
public:
  // Declarations related to dynamic class loading
  typedef BaseScorer* create_t(const char*);
  typedef const char* type_id_t(void);

  // Score for corpus
  virtual void corpusScore(const std::vector<std::string>& candidates, const std::vector<std::string>& references,
                           double& score) = 0;

  // Score for sentence
  virtual void sentScore(const std::string& candidate, const std::string& reference, double& score) = 0;

  // Destructor
  virtual ~BaseScorer(){};
};

