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
 * @file printAligFuncs.cc
 *
 * @brief Definitions file for printAligFuncs.h
 */

#include "nlp_common/printAligFuncs.h"

//-------------------------
void printAlignmentInGIZAFormat(std::ostream& outS, const std::vector<std::string>& ns,
                                const std::vector<std::string>& t, WordAlignmentMatrix waMatrix, const char* header)
{
  unsigned int i, j;

  outS << header << std::endl;
  for (i = 0; i < t.size(); ++i)
  {
    if (i < t.size() - 1)
      outS << t[i] << " ";
    else
      outS << t[i];
  }
  outS << std::endl;

  for (i = 0; i < ns.size(); ++i)
  {
    outS << ns[i] << " ({ ";
    for (j = 0; j < waMatrix.get_J(); ++j)
    {
      if (i == 0)
      {
        if (!waMatrix.isColumnAligned(j))
          outS << j + 1 << " ";
      }
      else
      {
        if (waMatrix.getValue(i - 1, j))
        {
          outS << j + 1 << " ";
        }
      }
    }
    outS << "}) ";
  }
  outS << std::endl;
}

//-------------------------
void printAlignmentInMyFormat(std::ostream& outS, const std::vector<std::string>& ns, const std::vector<std::string>& t,
                              WordAlignmentMatrix waMatrix, unsigned int numReps /*=1*/)
{
  unsigned int i;

  outS << "# " << numReps << std::endl;
  for (i = 0; i < t.size(); ++i)
  {
    if (i < t.size() - 1)
      outS << t[i] << " ";
    else
      outS << t[i];
  }
  outS << std::endl;

  for (i = 0; i < ns.size(); ++i)
  {
    if (i < ns.size() - 1)
      outS << ns[i] << " ";
    else
      outS << ns[i] << std::endl;
  }
  outS << waMatrix;
}
//-------------------------
void printAlignmentInGIZAFormat(FILE* outf, const std::vector<std::string>& ns, const std::vector<std::string>& t,
                                WordAlignmentMatrix waMatrix, const char* header)
{
  unsigned int i, j;

  fprintf(outf, "%s\n", header);
  for (i = 0; i < t.size(); ++i)
  {
    if (i < t.size() - 1)
      fprintf(outf, "%s ", t[i].c_str());
    else
      fprintf(outf, "%s", t[i].c_str());
  }
  fprintf(outf, "\n");

  for (i = 0; i < ns.size(); ++i)
  {
    fprintf(outf, "%s ({ ", ns[i].c_str());
    for (j = 0; j < waMatrix.get_J(); ++j)
    {
      if (i == 0)
      {
        if (!waMatrix.isColumnAligned(j))
          fprintf(outf, "%d ", j + 1);
      }
      else
      {
        if (waMatrix.getValue(i - 1, j))
        {
          fprintf(outf, "%d ", j + 1);
        }
      }
    }
    fprintf(outf, "}) ");
  }
  fprintf(outf, "\n");
}
//-------------------------
void printAlignmentInMyFormat(FILE* outf, const std::vector<std::string>& ns, const std::vector<std::string>& t,
                              WordAlignmentMatrix waMatrix, unsigned int numReps /*=1*/)
{
  unsigned int i;

  fprintf(outf, "# %d\n", numReps);
  for (i = 0; i < t.size(); ++i)
  {
    if (i < t.size() - 1)
      fprintf(outf, "%s ", t[i].c_str());
    else
      fprintf(outf, "%s", t[i].c_str());
  }
  fprintf(outf, "\n");

  for (i = 0; i < ns.size(); ++i)
  {
    if (i < ns.size() - 1)
      fprintf(outf, "%s ", ns[i].c_str());
    else
      fprintf(outf, "%s\n", ns[i].c_str());
  }
  waMatrix.print(outf);
}
