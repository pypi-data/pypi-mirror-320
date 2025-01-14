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
 * @file ins_op_pair.h
 *
 * @brief defines the less-than operator for vectors.
 */

#pragma once

#include <iostream>
#include <utility>

template <class ELEM_X, class ELEM_Y>
std::ostream& operator<<(std::ostream& outS, const std::pair<ELEM_X, ELEM_Y>& pair)
{
  outS << pair.first << " " << pair.second;
  return outS;
}

