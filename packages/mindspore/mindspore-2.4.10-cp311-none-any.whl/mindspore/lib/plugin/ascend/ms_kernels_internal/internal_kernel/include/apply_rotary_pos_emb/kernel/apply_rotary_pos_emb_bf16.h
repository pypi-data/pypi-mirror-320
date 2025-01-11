/**
 * Copyright (c) Huawei Technologies Co., Ltd. 2024. All rights reserved.
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
#ifndef ROTARY_POS_EMB_BF16
#define ROTARY_POS_EMB_BF16
#include "apply_rotary_pos_emb_base.h"
template <typename QK_DTYPE, typename COS_DTYPE, bool IF_COS_BROADCAST>
class RopeBf16 : public RopeBase<QK_DTYPE, COS_DTYPE, IF_COS_BROADCAST> {
 public:
  __aicore__ inline RopeBf16(RopeTilingData *tilingData) : RopeBase<QK_DTYPE, COS_DTYPE, IF_COS_BROADCAST>(tilingData) {
    this->repeatSize_ = 64;                   // 64 = 256B / sizeof(float)
    this->maxProcessNum_ = 3 * MAX_LEN_FP16;  // 3 is fp16 space needed
    this->repeatTimesQ_ = (this->tilingData_->hiddenSizeQ + this->repeatSize_ - 1) / this->repeatSize_;
    this->repeatTimesK_ = (this->tilingData_->hiddenSizeK + this->repeatSize_ - 1) / this->repeatSize_;
    headDimAlign_ = ((this->tilingData_->headDim + ELE_NUM_FP16 - 1) / ELE_NUM_FP16) * ELE_NUM_FP16;
    this->alignHalfHeadDim_ = (this->rotateStride_ * NUM_TWO) % ELE_NUM_FP32;
    this->hiddenSizeAlign_ = ((this->hiddenSize_ + this->repeatSize_ - 1) / this->repeatSize_) * this->repeatSize_;
    this->syncOffset_ =
      (this->tilingData_->headDim % ELE_NUM_FP16 == 0) ? this->hiddenSizeAlign_ : this->headNum_ * headDimAlign_;
    this->offsetExtraGm_ = NUM_TWO * block_idx * this->syncOffset_;

    sliceSizeTmp_ = (SLICE_SIZE / this->tilingData_->headDim) * this->tilingData_->headDim;  // 向下取整

    // fp16
    this->oriPos_ = 0;
    this->removeBefore_ = this->oriPos_ + sliceSizeTmp_;
    this->padBefore_ = this->removeBefore_ + sliceSizeTmp_;

    // fp32
    this->cosPad_ = 0;
    this->sinPad_ = this->cosPad_ + sliceSizeTmp_;
    this->negOne_ = this->sinPad_ + sliceSizeTmp_;
    oriPosF32_ = this->negOne_ + sliceSizeTmp_;
    PadBeforeF32_ = oriPosF32_ + sliceSizeTmp_;
    removeBeforeF32_ = PadBeforeF32_ + sliceSizeTmp_;
    posOneF32_ = removeBeforeF32_ + sliceSizeTmp_;

    this->pipe_.InitBuffer(
      qkfp32QueueCO2_, 1,
      (this->tilingData_->maxUbSize - (this->batchSize_ + this->maxProcessNum_) * sizeof(half)));  // 留給fp32的
    AscendC::LocalTensor<float> qkfp32_perloop_ub = qkfp32QueueCO2_.AllocTensor<float>();
    qkfp32Ubuf_ = (__ubuf__ float *)qkfp32_perloop_ub.GetPhyAddr();
    this->pipe_.InitBuffer(outQueueCO2_, 1, ((this->maxProcessNum_) * sizeof(half)));
    AscendC::LocalTensor<QK_DTYPE> cache_perloop_ub2 = outQueueCO2_.AllocTensor<QK_DTYPE>();
    commonUbuf_ = (__ubuf__ QK_DTYPE *)cache_perloop_ub2.GetPhyAddr();

    // 判断是否需要切块计算
    if (this->tilingData_->hiddenSizeQ > sliceSizeTmp_) {
      sliceTimeQ_ = (this->tilingData_->hiddenSizeQ + sliceSizeTmp_ - 1) / sliceSizeTmp_;    // 向上取整
      lastSliceSizeQ_ = this->tilingData_->hiddenSizeQ - (sliceTimeQ_ - 1) * sliceSizeTmp_;  // 1024
    } else {
      sliceTimeQ_ = 1;
      lastSliceSizeQ_ = this->tilingData_->hiddenSizeQ;
    }

    if (this->tilingData_->hiddenSizeK > sliceSizeTmp_) {
      sliceTimeK_ = (this->tilingData_->hiddenSizeK + sliceSizeTmp_ - 1) / sliceSizeTmp_;  // 向上取整
      lastSliceSizeK_ = this->tilingData_->hiddenSizeK - (sliceTimeK_ - 1) * sliceSizeTmp_;
    } else {
      sliceTimeK_ = 1;
      lastSliceSizeK_ = this->tilingData_->hiddenSizeK;
    }
  }

  __aicore__ inline void ConvertCos(uint32_t repeatTimes) {
    vconv_bf162f32(qkfp32Ubuf_ + this->cosPad_, commonUbuf_ + this->cosPad_, repeatTimes, 1, 1, DEFAULT_REPEAT_STRIDE,
                   DEFAULT_REPEAT_STRIDE / NUM_TWO);
    vconv_bf162f32(qkfp32Ubuf_ + this->sinPad_, commonUbuf_ + this->sinPad_, repeatTimes, 1, 1, DEFAULT_REPEAT_STRIDE,
                   DEFAULT_REPEAT_STRIDE / NUM_TWO);
  }

  __aicore__ inline void CastB162F32(uint32_t repeatTimes1) {
    vconv_bf162f32(qkfp32Ubuf_ + oriPosF32_, commonUbuf_ + this->oriPos_, repeatTimes1, 1, 1, DEFAULT_REPEAT_STRIDE,
                   DEFAULT_REPEAT_STRIDE / NUM_TWO);
    vconv_bf162f32(qkfp32Ubuf_ + removeBeforeF32_, commonUbuf_ + this->removeBefore_, repeatTimes1, 1, 1,
                   DEFAULT_REPEAT_STRIDE, DEFAULT_REPEAT_STRIDE / NUM_TWO);
    vconv_bf162f32(qkfp32Ubuf_ + PadBeforeF32_, commonUbuf_ + this->padBefore_, repeatTimes1, 1, 1,
                   DEFAULT_REPEAT_STRIDE, DEFAULT_REPEAT_STRIDE / NUM_TWO);
  }

  __aicore__ inline void CastF322B16(__gm__ QK_DTYPE *dst, __ubuf__ QK_DTYPE *src1, __ubuf__ float *src,
                                     uint32_t repeatTimes1, uint32_t hiddenSize1) {
    vconv_f322bf16r(src1, src, repeatTimes1, 1, 1, DEFAULT_REPEAT_STRIDE / NUM_TWO, DEFAULT_REPEAT_STRIDE);
    set_flag(PIPE_V, PIPE_MTE3, EVENT_ID0);
    wait_flag(PIPE_V, PIPE_MTE3, EVENT_ID0);
    copy_ubuf_to_gm(dst, src1, 0, 1, hiddenSize1 / ELE_NUM_FP16, 0, 0);
  }

  __aicore__ inline void Process(__gm__ uint8_t *extraGm) {
    if (this->tilingData_->cosFormat == 1) {
      pipe_barrier((PIPE_ALL));
      this->ExpandCosSin(commonUbuf_, this->cosGm_, (__gm__ COS_DTYPE *)extraGm);
      this->cosGm_ = (__gm__ COS_DTYPE *)extraGm;
      pipe_barrier((PIPE_ALL));
      this->ExpandCosSin(commonUbuf_, this->sinGm_,
                         (__gm__ COS_DTYPE *)extraGm + this->tilingData_->ntokens * this->tilingData_->headDim);
      this->sinGm_ = (__gm__ COS_DTYPE *)extraGm + this->tilingData_->ntokens * this->tilingData_->headDim;
      extraGm =
        extraGm + this->tilingData_->ntokens * this->tilingData_->headDim * 4;  // sizeof(uint8_t) * 2 = sizeof(half)
      pipe_barrier((PIPE_ALL));
    }

    uint32_t dynamicSliceQ =
      this->tilingData_->hiddenSizeQ > sliceSizeTmp_ ? sliceSizeTmp_ : this->tilingData_->hiddenSizeQ;
    uint32_t headNumTempQ = dynamicSliceQ / this->tilingData_->headDim;

    uint32_t dynamicSliceK =
      this->tilingData_->hiddenSizeK > sliceSizeTmp_ ? sliceSizeTmp_ : this->tilingData_->hiddenSizeK;
    uint32_t headNumTempK = dynamicSliceK / this->tilingData_->headDim;
    uint32_t repeatTemp = (dynamicSliceQ + this->repeatSize_ - 1) / this->repeatSize_;
    this->ExpandNeg(qkfp32Ubuf_, posOneF32_, headNumTempQ, repeatTemp);
    for (uint32_t zz = 0; zz < this->dynamicRound_; ++zz) {
      this->CosSinBroadcast(extraGm, zz, commonUbuf_, dynamicSliceQ);
      if (this->tilingData_->headDim % ELE_NUM_FP16 == 0) {
        pipe_barrier(PIPE_V);
        ConvertCos(repeatTemp);
      } else {
        set_flag(PIPE_MTE2, PIPE_V, EVENT_ID1);
        wait_flag(PIPE_MTE2, PIPE_V, EVENT_ID1);
        ConvertCos(repeatTemp);
      }
      for (uint32_t perSlice = 0; perSlice < sliceTimeQ_; ++perSlice) {  // 核内每块
        uint32_t dynamicSliceQTemp = (perSlice == sliceTimeQ_ - 1) ? lastSliceSizeQ_ : sliceSizeTmp_;
        headNumTempQ = dynamicSliceQTemp / this->tilingData_->headDim;
        uint32_t repeatTimeOnce = (dynamicSliceQTemp + this->repeatSize_ - 1) / this->repeatSize_;
        pipe_barrier(PIPE_MTE2);
        set_flag(PIPE_V, PIPE_MTE2, EVENT_ID1);
        wait_flag(PIPE_V, PIPE_MTE2, EVENT_ID1);
        this->QkComm(this->qGm_ + block_idx * this->nlCoreRun_ * this->tilingData_->hiddenSizeQ +
                       zz * this->tilingData_->hiddenSizeQ + perSlice * sliceSizeTmp_,
                     extraGm, dynamicSliceQTemp, commonUbuf_, headNumTempQ);

        if (this->alignRotary_ == 0) {
          pipe_barrier((PIPE_V));
          CastB162F32(repeatTimeOnce);

          pipe_barrier((PIPE_V));
          this->CalcRopeAlign(qkfp32Ubuf_, repeatTimeOnce, oriPosF32_, removeBeforeF32_, PadBeforeF32_);
        } else {
          set_flag(PIPE_MTE2, PIPE_V, EVENT_ID1);
          wait_flag(PIPE_MTE2, PIPE_V, EVENT_ID1);

          CastB162F32(repeatTimeOnce);
          pipe_barrier((PIPE_V));
          this->CalcRope(qkfp32Ubuf_, repeatTimeOnce, oriPosF32_, removeBeforeF32_, PadBeforeF32_, posOneF32_,
                         PadBeforeF32_);
        }

        CastF322B16(this->outQGm_ + block_idx * this->nlCoreRun_ * this->tilingData_->hiddenSizeQ +
                      zz * this->tilingData_->hiddenSizeQ + perSlice * sliceSizeTmp_,
                    commonUbuf_ + this->padBefore_, qkfp32Ubuf_ + PadBeforeF32_, repeatTimeOnce, dynamicSliceQTemp);
        pipe_barrier((PIPE_ALL));
      }

      for (uint32_t perSlice = 0; perSlice < sliceTimeK_; ++perSlice) {  // 核内每块
        uint32_t dynamicSliceKTemp = (perSlice == sliceTimeK_ - 1) ? lastSliceSizeK_ : sliceSizeTmp_;
        headNumTempK = dynamicSliceKTemp / this->tilingData_->headDim;
        uint32_t repeatTimeOnce = (dynamicSliceKTemp + this->repeatSize_ - 1) / this->repeatSize_;
        pipe_barrier(PIPE_MTE2);
        this->QkComm(this->kGm_ + block_idx * this->nlCoreRun_ * this->tilingData_->hiddenSizeK +
                       zz * this->tilingData_->hiddenSizeK + perSlice * sliceSizeTmp_,
                     extraGm, dynamicSliceKTemp, commonUbuf_, headNumTempK);

        if (this->alignRotary_ == 0) {
          pipe_barrier((PIPE_V));
          CastB162F32(repeatTimeOnce);

          pipe_barrier((PIPE_V));
          this->CalcRopeAlign(qkfp32Ubuf_, repeatTimeOnce, oriPosF32_, removeBeforeF32_, PadBeforeF32_);
        } else {
          set_flag(PIPE_MTE2, PIPE_V, EVENT_ID1);
          wait_flag(PIPE_MTE2, PIPE_V, EVENT_ID1);
          CastB162F32(repeatTimeOnce);

          pipe_barrier((PIPE_V));
          this->CalcRope(qkfp32Ubuf_, repeatTimeOnce, oriPosF32_, removeBeforeF32_, PadBeforeF32_, posOneF32_,
                         PadBeforeF32_);
        }

        CastF322B16(this->outKGm_ + block_idx * this->nlCoreRun_ * this->tilingData_->hiddenSizeK +
                      zz * this->tilingData_->hiddenSizeK + perSlice * sliceSizeTmp_,
                    commonUbuf_ + this->padBefore_, qkfp32Ubuf_ + PadBeforeF32_, repeatTimeOnce, dynamicSliceKTemp);
        pipe_barrier((PIPE_ALL));
      }
    }
  }

 private:
  AscendC::TQue<AscendC::QuePosition::VECIN, 1> outQueueCO2_;
  AscendC::TQue<AscendC::QuePosition::VECIN, 1> qkfp32QueueCO2_;
  __ubuf__ QK_DTYPE *commonUbuf_{nullptr};
  __ubuf__ float *qkfp32Ubuf_{nullptr};
  uint32_t oriPosF32_{0};        // fp32的buf中qk的位置
  uint32_t PadBeforeF32_{0};     // fp32的buf中保存qk[-x : hiddensize - x]
  uint32_t removeBeforeF32_{0};  // fp32的buf中保存qk[x : hiddensize + x]
  uint32_t posOneF32_{0};        // fp32的buf中0 0 0 1 1 1的位置
  uint32_t headDimAlign_;        // 对齐的headDim
  uint32_t sliceTimeQ_;          // 切分块的次数
  uint32_t lastSliceSizeQ_;      // 最后一块的大小
  uint32_t sliceTimeK_;
  uint32_t lastSliceSizeK_;
  uint32_t sliceSizeTmp_;
};

#endif