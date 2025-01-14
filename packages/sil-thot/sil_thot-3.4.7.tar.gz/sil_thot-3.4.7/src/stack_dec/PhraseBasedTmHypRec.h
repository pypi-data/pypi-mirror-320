/*
stack_dec package for statistical machine translation
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
 * @file PhraseBasedTmHypRec.h
 *
 * @brief Declares the PhraseBasedTmHypRec template class, this class
 * is derived from the _phraseHypothesisRec class.
 */

#pragma once

//--------------- Include files --------------------------------------

#include "stack_dec/PhrHypEqClassF.h"
#include "stack_dec/PhrHypState.h"
#include "stack_dec/PhrScoreInfo.h"
#include "stack_dec/_phraseHypothesisRec.h"

//--------------- Classes --------------------------------------------

//--------------- PhraseBasedTmHypRec template class

/**
 * @brief The PhraseBasedTmHypRec template class is derived from the
 * _phraseHypothesisRec class.
 */

template <class EQCLASS_FUNC = PhrHypEqClassF>
class PhraseBasedTmHypRec : public _phraseHypothesisRec<PhrScoreInfo, EQCLASS_FUNC, PhrHypState>
{
public:
  typedef typename _phraseHypothesisRec<PhrScoreInfo, EQCLASS_FUNC, PhrHypState>::ScoreInfo ScoreInfo;
  typedef typename _phraseHypothesisRec<PhrScoreInfo, EQCLASS_FUNC, PhrHypState>::DataType DataType;
  typedef typename _phraseHypothesisRec<PhrScoreInfo, EQCLASS_FUNC, PhrHypState>::EqClassFunc EqClassFunc;
  typedef typename _phraseHypothesisRec<PhrScoreInfo, EQCLASS_FUNC, PhrHypState>::HypState HypState;

  // Hypothesis to state mapping
  HypState getHypState(void) const;

  // Destructor
  ~PhraseBasedTmHypRec()
  {
  }
};

//--------------- PhraseBasedTmHypRec class functions
//

//---------------------------------
template <class EQCLASS_FUNC>
typename PhraseBasedTmHypRec<EQCLASS_FUNC>::HypState PhraseBasedTmHypRec<EQCLASS_FUNC>::getHypState(void) const
{
  typename PhraseBasedTmHypRec::HypState hypState;

  hypState.lmHist = this->scoreInfo.lmHist;
  hypState.trglen = this->data.ntarget.size() - 1;
  if (this->data.sourceSegmentation.size() == 0)
    hypState.endLastSrcPhrase = 0;
  else
    hypState.endLastSrcPhrase = this->data.sourceSegmentation.back().second;
  hypState.sourceWordsAligned = this->getKey();

  return hypState;
}

