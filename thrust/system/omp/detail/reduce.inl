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

#include <thrust/detail/config.h>
#include <thrust/system/omp/detail/reduce.h>
#include <thrust/system/detail/generic/reduce.h>

namespace thrust
{
namespace system
{
namespace omp
{
namespace detail
{


template<typename InputIterator, 
         typename OutputType,
         typename BinaryFunction>
  OutputType reduce(tag,
                    InputIterator begin,
                    InputIterator end,
                    OutputType init,
                    BinaryFunction binary_op)
{
  // omp prefers generic::reduce to cpp::reduce
  return thrust::system::detail::generic::reduce(tag(), begin, end, init, binary_op);
} // end reduce()


} // end detail
} // end omp
} // end system
} // end thrust

