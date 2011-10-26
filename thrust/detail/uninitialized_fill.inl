/*
 *  Copyright 2008-2011 NVIDIA Corporation
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */


/*! \file uninitialized_fill.inl
 *  \brief Inline file for uninitialized_fill.h.
 */

#include <thrust/uninitialized_fill.h>
#include <thrust/system/detail/generic/select_system.h>
#include <thrust/system/detail/generic/uninitialized_fill.h>
#include <thrust/iterator/iterator_traits.h>

namespace thrust
{

template<typename ForwardIterator,
         typename T>
  void uninitialized_fill(ForwardIterator first,
                          ForwardIterator last,
                          const T &x)
{
  using thrust::system::detail::generic::select_system;
  using thrust::system::detail::generic::uninitialized_fill;

  typedef typename thrust::iterator_space<ForwardIterator>::type space;

  uninitialized_fill(select_system(space()), first, last, x);
} // end uninitialized_fill()

template<typename ForwardIterator,
         typename Size,
         typename T>
  ForwardIterator uninitialized_fill_n(ForwardIterator first,
                                       Size n,
                                       const T &x)
{
  using thrust::system::detail::generic::select_system;
  using thrust::system::detail::generic::uninitialized_fill_n;

  typedef typename thrust::iterator_space<ForwardIterator>::type space;

  return uninitialized_fill_n(select_system(space()), first, n, x);
} // end uninitialized_fill_n()

} // end thrust

