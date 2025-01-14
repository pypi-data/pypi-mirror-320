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
 * @file IncrNgramLM.h
 *
 * @brief Class to manage incremental encoded ngram language models
 * p(x|std::vector<x>).
 */

#pragma once

//--------------- Include files --------------------------------------

#include "incr_models/_incrNgramLM.h"
#include "incr_models/vecx_x_incr_cptable.h"

//--------------- Constants ------------------------------------------

#define INLM_SMOOTHING_FACTOR 0.1

//--------------- typedefs -------------------------------------------

//--------------- function declarations ------------------------------

//--------------- Classes --------------------------------------------

//--------------- IncrNgramLM class

class IncrNgramLM : public _incrNgramLM<Count, Count>
{
public:
  typedef _incrNgramLM<Count, Count>::SrcTableNode SrcTableNode;
  typedef _incrNgramLM<Count, Count>::TrgTableNode TrgTableNode;

  // Constructor
  IncrNgramLM() : _incrNgramLM<Count, Count>()
  {
    // Set new pointer to table
    this->tablePtr = new vecx_x_incr_cptable<WordIndex, Count, Count>;
  }

  // basic vecx_x_incr_ecpm function redefinitions
  Prob pHTrgGivenHSrc(const std::vector<std::string>& s, const std::string& t);
  Prob pTrgGivenSrc(const std::vector<WordIndex>& s, const WordIndex& t);

  // Destructor
  virtual ~IncrNgramLM();

protected:
};

//---------------

