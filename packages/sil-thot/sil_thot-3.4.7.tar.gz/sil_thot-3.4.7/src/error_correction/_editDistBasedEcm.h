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
 * @file _editDistBasedEcm.h
 *
 * @brief Defines the _editDistBasedEcm class, this class is a base
 * class for error correcting models based on edit distance
 */

#pragma once

//--------------- Include files --------------------------------------

#include "error_correction/BaseErrorCorrectionModel.h"
#include "error_correction/EditDistForVecString.h"
#include "error_correction/WordAndCharLevelOps.h"

//--------------- Constants ------------------------------------------

//--------------- Classes --------------------------------------------

//--------------- _editDistBasedEcm template class

/**
 * @brief The _editDistBasedEcm class is a base class for error
 * correcting models based on edit distance
 */

class _editDistBasedEcm : public BaseErrorCorrectionModel
{
protected:
  void correctStrGivenPrefOps(WordAndCharLevelOps wordCharOpsForSegm, std::vector<std::string> uncorrStrVec,
                              std::vector<std::string> prefStrVec, std::vector<std::string>& correctedStrVec);
  void correctWordGivenPrefOps(std::vector<unsigned int> charOpsForWord, std::string word, std::string pref,
                               std::string& correctedWord);
};
