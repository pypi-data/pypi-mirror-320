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
 * @file SrfNodeInfoMap.h
 *
 * @brief Defines the SrfNodeInfoMap class, which stores a set of
 * indices corresponding to consistent bilingual phrase pairs.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "nlp_common/Bitset.h"
#include "phrase_models/PhraseDefs.h"
#include "phrase_models/SrfNodeInfo.h"
#include "phrase_models/SrfNodeKey.h"

#include <map>

//--------------- Constants ------------------------------------------

//--------------- typedefs -------------------------------------------

//--------------- function declarations ------------------------------

//--------------- Classes --------------------------------------------

//--------------- SrfNodeInfoMap class

class SrfNodeInfoMap
{
public:
  SrfNodeInfoMap(void);

  void insert(const SrfNodeKey& k, const SrfNodeInfo& sni);
  SrfNodeInfo find(const SrfNodeKey& k, bool& found) const;
  size_t numNodesWithLeafs(void);
  size_t size(void);
  void clear(void);

private:
  typedef std::map<SrfNodeKey, SrfNodeInfo> BitsetSniMap;

  BitsetSniMap bitsetSniMap;
};

