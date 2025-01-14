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
 * @file AwkInputStream.cc
 *
 * @brief Definitions file for AwkInputStream.h
 */

#include "nlp_common/AwkInputStream.h"

#include "nlp_common/ErrorDefs.h"
#include "nlp_common/getline.h"

//----------
AwkInputStream::AwkInputStream(void)
{
  FS = 0;
  buff = NULL;
  buftlen = 0;
  fopen_called = false;
}

//----------
AwkInputStream& AwkInputStream::operator=(const AwkInputStream& awk)
{
  FS = 0;
  if (awk.FS != 0)
  {
    open(awk.fileName.c_str());
    FS = awk.FS;
    while (FNR != awk.FNR)
      getln();
  }
  return *this;
}

//----------
bool AwkInputStream::getln(void)
{
  if (FS != 0)
  {
    ssize_t read;

    read = getline(&buff, &buftlen, filePtr);
    if (read != -1)
    {
      if (buff[read - 1] == '\n')
      {
        buff[read - 1] = '\0';
      }
      else
      {
        if ((size_t)read == buftlen)
        {
          buftlen++;
          buff = (char*)realloc(buff, buftlen);
        }
        buff[read] = '\0';
      }
      ++FNR;
      NF = get_NF();
      return true;
    }
    else
      return false;
  }
  else
    return false;
}

//----------
std::string AwkInputStream::dollar(unsigned int n)
{
  if (FS != 0)
  {
    if (n == 0)
    {
      return buff;
    }
    else
    {
      if (n > NF)
        return "";
      else
      {
        retrieveField(n - 1);
        return fieldStr;
      }
    }
  }
  else
    return NULL;
}

//----------
bool AwkInputStream::open(const char* str)
{
  if (fopen_called)
    close();
  filePtr = fopen(str, "r");
  if (filePtr == NULL)
  {
    FS = 0;
    return THOT_ERROR;
  }
  else
  {
    fopen_called = true;
    fileName = str;
    FNR = 0;
    FS = ' ';
    return THOT_OK;
  }
}

//----------
bool AwkInputStream::open_stream(FILE* stream)
{
  if (fopen_called)
    close();
  filePtr = stream;
  if (filePtr == NULL)
  {
    FS = 0;
    return THOT_ERROR;
  }
  else
  {
    FNR = 0;
    FS = ' ';
    return THOT_OK;
  }
}

//----------
void AwkInputStream::close(void)
{
  if (fopen_called)
    fclose(filePtr);
  fieldStr = "";
  FS = 0;
  fopen_called = false;
}

//----------
bool AwkInputStream::rwd(void)
{
  if (FS != 0)
  {
    FNR = 0;
    rewind(filePtr);
    return THOT_OK;
  }
  else
    return THOT_ERROR;
}

//----------
void AwkInputStream::printFields(void)
{
  unsigned int i;

  if (FS != 0)
  {
    for (i = 0; i < NF; ++i)
    {
      retrieveField(i);
      printf("|%s", fieldStr.c_str());
    }
  }
  printf("|\n");
}

//----------
AwkInputStream::~AwkInputStream()
{
  if (buff != NULL)
    free(buff);
  if (fopen_called)
    close();
}

//----------
int AwkInputStream::get_NF(void)
{
  unsigned int i = 0;

  NF = 0;

  while (buff[i] != 0 && buff[i] == FS)
    ++i;
  while (buff[i] != 0)
  {
    if (buff[i] == FS)
    {
      ++NF;
      while (buff[i] != 0 && buff[i] == FS)
        ++i;
    }
    else
    {
      ++i;
      if (buff[i] == 0)
        ++NF;
    }
  }
  return NF;
}

//----------
void AwkInputStream::retrieveField(unsigned int n)
{
  unsigned int numFields = 0, i = 0;

  fieldStr = "";
  NF = 0;

  while (buff[i] != 0 && buff[i] == FS)
    ++i;
  while (buff[i] != 0)
  {
    if (buff[i] == FS)
    {
      ++NF;
      while (buff[i] != 0 && buff[i] == FS)
        ++i;
    }
    else
    {
      ++i;
      if (buff[i] == 0)
        ++NF;
    }
  }

  i = 0;
  numFields = 0;
  while (buff[i] != 0 && buff[i] == FS)
    ++i;
  while (buff[i] != 0)
  {
    if (buff[i] == FS)
    {
      ++numFields;
      while (buff[i] != 0 && buff[i] == FS)
        ++i;
    }
    else
    {
      if (n == numFields)
        fieldStr += buff[i];
      ++i;
      if (buff[i] == 0 && n == numFields)
      {
        ++numFields;
      }
    }
    if (numFields > n)
      break;
  }
}
