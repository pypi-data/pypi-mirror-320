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
 * @file TrgCutsTable.h
 *
 * @brief Defines the TrgCutsTable class, which stores a probability
 * table for the target phrase cuts.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "nlp_common/AwkInputStream.h"
#include "nlp_common/Prob.h"
#include "phrase_models/PhraseDefs.h"

#include <fstream>
#include <iomanip>
#include <iostream>

//--------------- Constants ------------------------------------------

#define STOP_JUMPS_DEFAULT_PAR 0.999
#define JUMP_ONE_POS_DEFAULT_PAR 1 - STOP_JUMPS_DEFAULT_PAR

//--------------- typedefs -------------------------------------------

//--------------- function declarations ------------------------------

//--------------- Classes --------------------------------------------

//--------------- TrgCutsTable class

class TrgCutsTable
{
public:
  // Constructor
  TrgCutsTable(void);

  // Functions to access model probabilities
  LgProb trgCutsLgProb(int offset);

  // load function
  bool load(const char* srcSegmLenFileName, int verbose = 0);

private:
  float jumpOnePar;
  float stopJumps;
};

