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
 * @file PhrHypNumcovJumpsEqClassF.h
 *
 * @brief Defines the PhrHypNumcovJumpsEqClassF class, this class is a
 * function object that for each hypothesis returns its equivalence
 * class.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "nlp_common/ins_op_pair.h"
#include "nlp_common/uiPairHashF.h"
#include "stack_dec/PhrHypData.h"

#include <utility>

//--------------- Constants ------------------------------------------

//--------------- Classes --------------------------------------------

//--------------- PhrHypNumcovJumpsEqClassF class

/**
 * @brief The PhrHypNumcovJumpsEqClassF class is a function object that
 * for each hypothesis returns its equivalence class.
 */

class PhrHypNumcovJumpsEqClassF
{
public:
  typedef std::pair<unsigned int, unsigned int> EqClassType;
  typedef uiPairHashF EqClassTypeHashF;

  EqClassType operator()(const PhrHypData& pbtHypData);

  virtual ~PhrHypNumcovJumpsEqClassF()
  {
  }

private:
  void set(unsigned int j, std::vector<unsigned int>& uivec);
  virtual void transformRawEqClass(EqClassType& eqc);
};

