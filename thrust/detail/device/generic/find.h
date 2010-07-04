/*
 *  Copyright 2008-2010 NVIDIA Corporation
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


/*! \file find.h
 *  \brief Search for values in (unsorted) ranges [generic device].
 */

#pragma once

namespace thrust
{
namespace detail
{
namespace device
{
namespace generic
{

template <typename InputIterator, typename Predicate>
InputIterator find_if(InputIterator first,
                      InputIterator last,
                      Predicate pred);

} // end namespace generic
} // end namespace device
} // end namespace detail
} // end namespace thrust

#include <thrust/detail/device/generic/find.inl>

