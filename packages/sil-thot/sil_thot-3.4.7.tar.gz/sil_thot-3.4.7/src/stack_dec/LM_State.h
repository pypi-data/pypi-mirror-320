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

#pragma once

//--------------- Include files --------------------------------------

#include "nlp_common/WordIndex.h"

#include <vector>

//--------------- Constants ------------------------------------------

// Set the LM_State type used to represent the word history of an n-gram
// language model.

#define LM_STATE_TYPE_NAME "std::vector<WordIndex>"
#define LM_STATE_DESC ""

//--------------- User defined types ---------------------------------

typedef std::vector<WordIndex> LM_State;

