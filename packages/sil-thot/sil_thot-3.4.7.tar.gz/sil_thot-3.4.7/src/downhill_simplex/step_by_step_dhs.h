/*
 * Code based on the implementation of the Nelder-Mead simplex method by
 * Michael F. Hutt.
 *
 * Copyright (c) 1997-2011 <Michael F. Hutt>
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 */

#pragma once

#include <stdio.h>

#define MAX_IT 5000 /* maximum number of iterations */
#define ALPHA 1.0   /* reflection coefficient */
#define BETA 0.5    /* contraction coefficient */
#define GAMMA 2.0   /* expansion coefficient */

#ifdef __cplusplus
extern "C"
{
#endif
  int step_by_step_simplex(double start[], int n, double FTOL, double scale, void (*constrain)(double[], int n),
                           FILE* images_file, int* nfunk, double* y, double* x, double* curr_ftol, int verbosity);
  int get_next_funk(FILE* images_file, double* y, int verbosity);
  int step_by_step_objfunc(FILE* images_file, int n, double* curr_vertex, double* x, double* y, int verbosity);
  void deallocate_dhs_mem(int n, double** v, double* f, double* vr, double* ve, double* vc, double* vm);

#ifdef __cplusplus
}
#endif
