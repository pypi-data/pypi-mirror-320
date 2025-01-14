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
 * @file AlignmentExtractor.cc
 *
 * @brief Definitions file for AlignmentExtractor.h
 */

//--------------- Include files --------------------------------------

#include "phrase_models/AlignmentExtractor.h"

#include "nlp_common/ErrorDefs.h"
#include "nlp_common/printAligFuncs.h"

//--------------- AlignmentExtractor class method definitions

//-------------------------
AlignmentExtractor::AlignmentExtractor(void)
{
  fileStream = NULL;
}

//----------
AlignmentExtractor::AlignmentExtractor(const AlignmentExtractor& alExt)
{
  ns = alExt.ns;
  t = alExt.t;
  wordAligMatrix = alExt.wordAligMatrix;
  numReps = alExt.numReps;
  fileFormat = alExt.fileFormat;
  fileStream = NULL;
  awkInpStrm = alExt.awkInpStrm;
}

//----------
AlignmentExtractor& AlignmentExtractor::operator=(const AlignmentExtractor& alExt)
{
  ns = alExt.ns;
  t = alExt.t;
  wordAligMatrix = alExt.wordAligMatrix;
  numReps = alExt.numReps;
  fileFormat = alExt.fileFormat;
  fileStream = NULL;
  awkInpStrm = alExt.awkInpStrm;

  return *this;
}

//-------------------------
bool AlignmentExtractor::open(const char* str, unsigned int _fileFormat /*=GIZA_ALIG_FILE_FORMAT*/)
{
  // Close previous files
  close();

  // Open new file
  fileStream = fopen(str, "r");
  if (fileStream == NULL)
  {
    std::cerr << "Error while opening file with alignments: " << str << std::endl;
    return THOT_ERROR;
  }

  // Set value of data member fileFormat
  fileFormat = _fileFormat;

  return awkInpStrm.open_stream(fileStream);
}

//-------------------------
bool AlignmentExtractor::open_stream(FILE* stream, unsigned int _fileFormat /*=GIZA_ALIG_FILE_FORMAT*/)
{
  // Close previous files
  close();

  fileFormat = _fileFormat;

  return awkInpStrm.open_stream(stream);
}

//-------------------------
void AlignmentExtractor::close(void)
{
  if (fileStream != NULL)
  {
    fclose(fileStream);
    fileStream = NULL;
  }
  awkInpStrm.close();
}

//-------------------------
bool AlignmentExtractor::rewind(void)
{
  return awkInpStrm.rwd();
}

//-------------------------
std::vector<std::string> AlignmentExtractor::get_ns(void)
{
  return ns;
}

//-------------------------
std::vector<std::string> AlignmentExtractor::get_s(void)
{
  std::vector<std::string> s;
  for (unsigned int i = 1; i < ns.size(); ++i)
    s.push_back(ns[i]);
  return s;
}

//-------------------------
std::vector<std::string> AlignmentExtractor::get_t(void)
{
  return t;
}

//-------------------------
WordAlignmentMatrix AlignmentExtractor::get_wamatrix(void)
{
  return wordAligMatrix;
}

//-------------------------
float AlignmentExtractor::get_numReps(void)
{
  return numReps;
}
//-------------------------
bool AlignmentExtractor::getNextAlignment(void)
{
  if (fileFormat == GIZA_ALIG_FILE_FORMAT)
    return getNextAlignInGIZAFormat();
  if (fileFormat == ALIG_OP_FILE_FORMAT)
    return getNextAlignInAlignOpFormat();
  return false;
}

//-------------------------
bool AlignmentExtractor::getNextAlignInGIZAFormat(void)
{
  unsigned int i, srcPos, trgPos, slen;

  ns.clear();
  t.clear();

  // Each alignment entry has three lines. The first line
  // must start with the '#' symbol.
  if (awkInpStrm.getln())
  {
    if (awkInpStrm.NF >= 1
        && (strcmp("#", awkInpStrm.dollar(1).c_str()) == 0
            || strcmp("<ALMOHADILLA>", awkInpStrm.dollar(1).c_str()) == 0))
    {
      if (awkInpStrm.NF > 2)
        numReps = 1;
      else
      {
        if (awkInpStrm.NF == 1)
          numReps = 1;
        else
          numReps = atof(awkInpStrm.dollar(2).c_str());
      }

      awkInpStrm.getln();
      for (i = 1; i <= awkInpStrm.NF; ++i)
      {
        t.push_back(awkInpStrm.dollar(i));
      }

      awkInpStrm.getln();
      i = 1;
      slen = 0;
      while (i <= awkInpStrm.NF)
      {
        if (strcmp("({", awkInpStrm.dollar(i).c_str()) == 0)
          ++slen;
        ++i;
      }
      i = 1;
      srcPos = 0;

      if (slen == 0)
      {
        std::cerr << "Error: GIZA alignment file corrupted!\n";
        std::cerr << "Alignment extraction process aborted!\n";
        return false;
      }

      wordAligMatrix.init(slen - 1, t.size());
      while (i <= awkInpStrm.NF)
      {
        std::string ew;
        bool opBraceFound;

        opBraceFound = false;
        ew = awkInpStrm.dollar(i);
        ++i;
        if (strcmp("({", awkInpStrm.dollar(i).c_str()) == 0)
          opBraceFound = true;
        while (i <= awkInpStrm.NF && strcmp("({", awkInpStrm.dollar(i).c_str()) != 0)
        {
          ++i;
        }
        ++i;
        while (i <= awkInpStrm.NF && strcmp("})", awkInpStrm.dollar(i).c_str()) != 0)
        {
          trgPos = atoi(awkInpStrm.dollar(i).c_str());

          if (trgPos - 1 >= t.size())
          {
            return 1;
          }
          else
          {
            if (srcPos > 0 && (srcPos - 1) < wordAligMatrix.get_I() && (trgPos - 1) < wordAligMatrix.get_J())
            {
              wordAligMatrix.set(srcPos - 1, trgPos - 1);
            }
          }
          ++i;
        }
        if (opBraceFound)
          ns.push_back(ew);
        else
          std::cerr << "alig_op: Anomalous entry! (perhaps a problem with file codification?)\n";
        ++srcPos;
        ++i;
      }
      return true;
    }
    else
      return false;
  }
  else
    return false;
}

//-------------------------
bool AlignmentExtractor::getNextAlignInAlignOpFormat(void)
{
  unsigned int i, col, row;

  t.clear();
  ns.clear();

  wordAligMatrix.clear();

  if (awkInpStrm.getln())
  {
    if (awkInpStrm.NF == 2 && strcmp("#", awkInpStrm.dollar(1).c_str()) == 0)
    {
      numReps = atof(awkInpStrm.dollar(2).c_str());
      awkInpStrm.getln();
      for (i = 1; i <= awkInpStrm.NF; ++i)
      {
        t.push_back(awkInpStrm.dollar(i));
      }

      awkInpStrm.getln();
      for (i = 1; i <= awkInpStrm.NF; ++i)
      {
        ns.push_back(awkInpStrm.dollar(i));
      }

      wordAligMatrix.init(ns.size() - 1, t.size());
      for (row = ns.size() - 1; row >= 1; --row)
      {
        awkInpStrm.getln();

        if (awkInpStrm.NF != t.size())
          return 0;
        else
        {
          for (col = 1; col <= t.size(); ++col)
          {
            wordAligMatrix.setValue(row - 1, col - 1, atoi(awkInpStrm.dollar(col).c_str()) > 0);
          }
        }
      }
      return true;
    }
    else
      return false;
  }
  return false;
}

//-------------------------
void AlignmentExtractor::transposeAlig(void)
{
  std::vector<std::string> aux;
  unsigned int i;
  std::string nullw;

  aux = t;
  t.clear();
  for (i = 1; i < ns.size(); ++i)
  {
    t.push_back(ns[i]);
  }
  if (ns.size() > 0)
    nullw = ns[0];
  ns.clear();
  ns.push_back(nullw);
  for (i = 0; i < aux.size(); ++i)
  {
    ns.push_back(aux[i]);
  }
  wordAligMatrix.transpose();
}

//-------------------------
bool AlignmentExtractor::join(const char* GizaAligFileName, const char* outFileName, bool transpose, bool verbose)
{
  AlignmentExtractor alExt;
  unsigned int numSent = 0;

#ifdef _GLIBCXX_USE_LFS
  std::ofstream outF;
  outF.open(outFileName, std::ios::out);
  if (!outF)
  {
    std::cerr << "Error while opening output file." << std::endl;
    return 1;
  }
#else
  FILE* outF;
  outF = fopen(outFileName, "wb");
  if (outF == NULL)
  {
    std::cerr << "Error while opening output file." << std::endl;
    return 1;
  }
#endif

  if (alExt.open(GizaAligFileName) == THOT_ERROR)
  {
    return THOT_ERROR;
  }
  else
  {
    while (alExt.getNextAlignment() && getNextAlignment())
    {
      ++numSent;
      if (verbose)
        std::cerr << "Operating sentence pair # " << numSent << std::endl;
      if (transpose)
        alExt.transposeAlig();
      if (t == alExt.t && ns == alExt.ns)
      {
        wordAligMatrix |= alExt.wordAligMatrix;
      }
      else
      {
        std::cerr << "Warning: sentences to operate are not equal!!!"
                  << " (Sent. pair:" << numSent << ")" << std::endl;
      }

      char header[256];
      snprintf(header, 256, "# %g", numReps);
      printAlignmentInGIZAFormat(outF, ns, t, wordAligMatrix, header);
    }
    alExt.close();
  }
  rewind();
#ifndef _GLIBCXX_USE_LFS
  fclose(outF);
#endif

  return THOT_OK;
}
//-------------------------
bool AlignmentExtractor::intersect(const char* GizaAligFileName, const char* outFileName, bool transpose, bool verbose)
{
  AlignmentExtractor alExt;
  unsigned int numSent = 0;

#ifdef _GLIBCXX_USE_LFS
  std::ofstream outF;
  outF.open(outFileName, std::ios::out);
  if (!outF)
  {
    std::cerr << "Error while opening output file." << std::endl;
    return 1;
  }
#else
  FILE* outF;
  outF = fopen(outFileName, "wb");
  if (outF == NULL)
  {
    std::cerr << "Error while opening output file." << std::endl;
    return 1;
  }
#endif

  if (alExt.open(GizaAligFileName) == THOT_ERROR)
  {
    return THOT_ERROR;
  }
  else
  {
    while (alExt.getNextAlignment() && getNextAlignment())
    {
      ++numSent;
      if (verbose)
        std::cerr << "Operating sentence pair # " << numSent << std::endl;

      if (transpose)
        alExt.transposeAlig();
      if (t == alExt.t && ns == alExt.ns)
      {
        wordAligMatrix &= alExt.wordAligMatrix;
      }
      else
      {
        std::cerr << "Warning: sentences to operate are not equal!!!"
                  << " (Sent. pair:" << numSent << ")" << std::endl;
      }

      char header[256];
      snprintf(header, 256, "# %g", numReps);
      printAlignmentInGIZAFormat(outF, ns, t, wordAligMatrix, header);
    }
    alExt.close();
  }
  rewind();
#ifndef _GLIBCXX_USE_LFS
  fclose(outF);
#endif

  return THOT_OK;
}
//-------------------------
bool AlignmentExtractor::sum(const char* GizaAligFileName, const char* outFileName, bool transpose, bool verbose)
{
  AlignmentExtractor alExt;
  unsigned int numSent = 0;

#ifdef _GLIBCXX_USE_LFS
  std::ofstream outF;
  outF.open(outFileName, std::ios::out);
  if (!outF)
  {
    std::cerr << "Error while opening output file." << std::endl;
    return 1;
  }
#else
  FILE* outF;
  outF = fopen(outFileName, "wb");
  if (outF == NULL)
  {
    std::cerr << "Error while opening output file." << std::endl;
    return 1;
  }
#endif

  if (alExt.open(GizaAligFileName) == THOT_ERROR)
  {
    return THOT_ERROR;
  }
  else
  {
    while (alExt.getNextAlignment() && getNextAlignment())
    {
      ++numSent;
      if (verbose)
        std::cerr << "Operating sentence pair # " << numSent << std::endl;

      if (transpose)
        alExt.transposeAlig();
      if (t == alExt.t && ns == alExt.ns)
      {
        wordAligMatrix += alExt.wordAligMatrix;
      }
      else
      {
        std::cerr << "Warning: sentences to operate are not equal!!!"
                  << " (Sent. pair:" << numSent << ")" << std::endl;
      }

      char header[256];
      snprintf(header, 256, "# %g", numReps);
      printAlignmentInGIZAFormat(outF, ns, t, wordAligMatrix, header);
    }
    alExt.close();
  }
  rewind();
#ifndef _GLIBCXX_USE_LFS
  fclose(outF);
#endif

  return THOT_OK;
}
//-------------------------
bool AlignmentExtractor::symmetr1(const char* GizaAligFileName, const char* outFileName, bool transpose, bool verbose)
{
  AlignmentExtractor alExt;
  unsigned int numSent = 0;

#ifdef _GLIBCXX_USE_LFS
  std::ofstream outF;
  outF.open(outFileName, std::ios::out);
  if (!outF)
  {
    std::cerr << "Error while opening output file." << std::endl;
    return 1;
  }
#else
  FILE* outF;
  outF = fopen(outFileName, "wb");
  if (outF == NULL)
  {
    std::cerr << "Error while opening output file." << std::endl;
    return 1;
  }
#endif

  if (alExt.open(GizaAligFileName) == THOT_ERROR)
  {
    return THOT_ERROR;
  }
  else
  {
    while (alExt.getNextAlignment() && getNextAlignment())
    {
      ++numSent;
      if (verbose)
        std::cerr << "Operating sentence pair # " << numSent << std::endl;

      if (transpose)
        alExt.transposeAlig();
      if (t == alExt.t && ns == alExt.ns)
      {
        wordAligMatrix.symmetr1(alExt.wordAligMatrix);
      }
      else
      {
        std::cerr << "Warning: sentences to operate are not equal!!!"
                  << " (Sent. pair:" << numSent << ")" << std::endl;
      }

      char header[256];
      snprintf(header, 256, "# %g", numReps);
      printAlignmentInGIZAFormat(outF, ns, t, wordAligMatrix, header);
    }
    alExt.close();
  }
  rewind();
#ifndef _GLIBCXX_USE_LFS
  fclose(outF);
#endif

  return THOT_OK;
}

//-------------------------
bool AlignmentExtractor::symmetr2(const char* GizaAligFileName, const char* outFileName, bool transpose, bool verbose)
{
  AlignmentExtractor alExt;
  unsigned int numSent = 0;

#ifdef _GLIBCXX_USE_LFS
  std::ofstream outF;
  outF.open(outFileName, std::ios::out);
  if (!outF)
  {
    std::cerr << "Error while opening output file." << std::endl;
    return 1;
  }
#else
  FILE* outF;
  outF = fopen(outFileName, "wb");
  if (outF == NULL)
  {
    std::cerr << "Error while opening output file." << std::endl;
    return 1;
  }
#endif

  if (alExt.open(GizaAligFileName) == THOT_ERROR)
  {
    return THOT_ERROR;
  }
  else
  {
    while (alExt.getNextAlignment() && getNextAlignment())
    {
      ++numSent;
      if (verbose)
        std::cerr << "Operating sentence pair # " << numSent << std::endl;

      if (transpose)
        alExt.transposeAlig();
      if (t == alExt.t && ns == alExt.ns)
      {
        wordAligMatrix.symmetr2(alExt.wordAligMatrix);
      }
      else
      {
        std::cerr << "Warning: sentences to operate are not equal!!!"
                  << " (Sent. pair:" << numSent << ")" << std::endl;
      }

      char header[256];
      snprintf(header, 256, "# %g", numReps);
      printAlignmentInGIZAFormat(outF, ns, t, wordAligMatrix, header);
    }
    alExt.close();
  }
  rewind();
#ifndef _GLIBCXX_USE_LFS
  fclose(outF);
#endif

  return THOT_OK;
}

//-------------------------
bool AlignmentExtractor::growDiagFinal(const char* GizaAligFileName, const char* outFileName, bool transpose,
                                       bool verbose)
{
  AlignmentExtractor alExt;
  unsigned int numSent = 0;

#ifdef _GLIBCXX_USE_LFS
  std::ofstream outF;
  outF.open(outFileName, std::ios::out);
  if (!outF)
  {
    std::cerr << "Error while opening output file." << std::endl;
    return 1;
  }
#else
  FILE* outF;
  outF = fopen(outFileName, "wb");
  if (outF == NULL)
  {
    std::cerr << "Error while opening output file." << std::endl;
    return 1;
  }
#endif

  if (alExt.open(GizaAligFileName) == THOT_ERROR)
  {
    return THOT_ERROR;
  }
  else
  {
    while (alExt.getNextAlignment() && getNextAlignment())
    {
      ++numSent;
      if (verbose)
        std::cerr << "Operating sentence pair # " << numSent << std::endl;

      if (transpose)
        alExt.transposeAlig();
      if (t == alExt.t && ns == alExt.ns)
      {
        wordAligMatrix.growDiagFinal(alExt.wordAligMatrix);
      }
      else
      {
        std::cerr << "Warning: sentences to operate are not equal!!!"
                  << " (Sent. pair:" << numSent << ")" << std::endl;
      }

      char header[256];
      snprintf(header, 256, "# %g", numReps);
      printAlignmentInGIZAFormat(outF, ns, t, wordAligMatrix, header);
    }
    alExt.close();
  }
  rewind();
#ifndef _GLIBCXX_USE_LFS
  fclose(outF);
#endif

  return THOT_OK;
}

//-------------------------
AlignmentExtractor::~AlignmentExtractor()
{
  close();
}

//-------------------------
std::ostream& operator<<(std::ostream& outS, AlignmentExtractor& ae)
{
  char cad[128];

  ae.rewind();
  while (ae.getNextAlignment())
  {
    snprintf(cad, 128, "# %f", ae.get_numReps());
    printAlignmentInGIZAFormat(outS, ae.get_ns(), ae.get_t(), ae.get_wamatrix(), cad);
  }
  ae.rewind();

  return outS;
}
