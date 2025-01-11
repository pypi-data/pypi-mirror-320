/**
 * Copyright 2024 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef MS_KERNELS_INTERNAL_KERNEL_ASCENDC_COMPARE_TILING_H_
#define MS_KERNELS_INTERNAL_KERNEL_ASCENDC_COMPARE_TILING_H_
#include "utils/elewise_tiling.h"
namespace mindspore::internal {
struct CompareTilingData : public ElewiseTailTilingData {
  uint32_t input_dtype{0};
  uint32_t broadcast_mode{0};
  uint32_t compare_mode{0};
};
}  // namespace mindspore::internal
#endif  // MS_KERNELS_INTERNAL_KERNEL_ASCENDC_COMPARE_TILING_H_