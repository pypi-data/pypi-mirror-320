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
 * @file BaseErrorCorrectionModel.cc
 *
 * @brief Definitions file for BaseErrorCorrectionModel.h
 */

//--------------- Include files --------------------------------------

#include "error_correction/BaseErrorCorrectionModel.h"

#include <iostream>

//--------------- BaseErrorCorrectionModel template class method definitions

//---------------------------------
int BaseErrorCorrectionModel::trainStrPair(const char* /*x*/, const char* /*y*/, int /*verbose*/)
{
  std::cerr << "Warning: training of a string pair was requested, but such functionality is not provided!" << std::endl;
  return THOT_OK;
}
