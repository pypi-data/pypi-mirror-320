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
 * @file BasePhrasePairFilter.h
 *
 * @brief Defines the BasePhrasePairFilter abstract base class. Phrase
 * pair filters are intended to be used to discard bad phrase table
 * entries when executing phrase extract.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "nlp_common/ErrorDefs.h"

#include <string>
#include <vector>

//--------------- Constants ------------------------------------------

#define DIGIT_CATEG "<digit>"
#define NUMBER_CATEG "<number>"
#define ALPHANUM_CATEG "<alfanum>"

//--------------- typedefs -------------------------------------------

//--------------- Classes --------------------------------------------

//--------------- BasePhrasePairFilter class

class BasePhrasePairFilter
{
public:
  // Declarations related to dynamic class loading
  typedef BasePhrasePairFilter* create_t(const char*);
  typedef const char* type_id_t(void);

  virtual bool phrasePairIsOk(std::vector<std::string> s_, std::vector<std::string> t_) = 0;

  virtual ~BasePhrasePairFilter(){};
};

