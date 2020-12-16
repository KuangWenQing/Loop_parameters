#!/usr/bin/env python3
import numpy as np
import math
import re
import sys
from builtins import print

gps_fs = 2 * 1024000.0
gps_fs1 = 8 * 1024000.0
gps_car_norm = (2 ** 31) / gps_fs
gps_car_norm1 = (2 ** 31) / gps_fs1


class control:
    high = 0
    mid = 1
    low = 2
    num = 3


class para_convert:
    gl_nCn0 = 'U32 nCn0[10] = {'
    gl_nSmooth = 'U32 nSmooth[2][2] = '
    gl_nThreshold = 'U32 nThreshold[3][2] = {'
    gl_nPll2 = 'U32 nPll2[3][5][6] = {{'
    gl_nLongPll = "U32 nLongPll[5][6] = {"
    gl_all = "U32 nAll[5][6] = {"
    gl_nPll3 = "U32 nPll3[3][5][9] = {{"
    gl_nFll2 = "U32 nFll2[3][4][3] = {{"
    gl_nFll3 = "U32 nFll3[3][4][6] = {{"
    gl_nDllBit = "U32 nDllBit[3][6] = {"
    gl_nDllSum1 = "U32 nDllSum1[3][2][3] = {{"
    gl_nDllSum2 = "U32 nDllSum2[6][3] = {"

    def __init__(self):
        self.gps_code_norm = gps_car_norm1 * 2.0
        self.gps_car_norm1_7 = gps_car_norm1 / (2.0 ** 7)

    """function to transform the vector for table"""

    def dll_bit(self, dll_bn, gps_code_norm):
        # para_num = np.shape(dll_bn)
        length = len(dll_bn)
        coe = []
        for i in range(length):
            if i < 3:
                dll_ms = 1
            elif i < 10:
                dll_ms = 20
            else:
                dll_ms = 100
            '''new para'''
            coe0 = 0.001 * dll_ms * gps_code_norm * ((dll_bn[i] / 0.53) ** 2)
            lg_fac0 = int(np.log2((2.0 ** 19 - 1) / coe0))
            coe_dll_0 = int(np.ceil(coe0 * (2.0 ** lg_fac0)))
            coe20 = gps_code_norm * dll_bn[i] * 8 / 3.0
            lg_fac1 = int(np.log2((2.0 ** 19 - 1) / coe20))
            coe_dll_1 = int(np.ceil(coe20 * (2.0 ** lg_fac1)))

            frac_dll_0 = -(lg_fac0 - lg_fac1)  # lg_fac0 > lg_fac1; -12
            frac_dll_1 = -(lg_fac1 + 12)  # -10

            dll_coe_l = coe_dll_0 & (2 ** 15 - 1)
            dll_coe_h = coe_dll_0 >> 15

            dll_coe_l2 = coe_dll_1 & (2 ** 15 - 1)
            dll_coe_h2 = coe_dll_1 >> 15

            temp_coe = [dll_coe_l, dll_coe_h, frac_dll_0, dll_coe_l2, dll_coe_h2, frac_dll_1]
            coe.append(temp_coe)
        return coe

    def dll_sum(self, dll_sum_bn, gps_code_norm):
        length = len(dll_sum_bn)
        coe = []
        for i in range(length):
            coe0 = gps_code_norm * dll_sum_bn[i]
            lg_fac = int(np.log2((2.0 ** 19 - 1) / coe0))
            fll_bit_coe = int(np.ceil(coe0 * (2.0 ** lg_fac)))
            fll_bit_shift = -(lg_fac + 12)

            fll_bit_coe_l = fll_bit_coe & (2 ** 15 - 1)
            fll_bit_coe_h = fll_bit_coe >> 15
            temp_coe = [fll_bit_coe_l, fll_bit_coe_h, fll_bit_shift]
            coe.append(temp_coe)

        return coe

    def fll_bit(self, fll_bn, gps_car_norm_7):
        bn_len = len(fll_bn)
        coe = []
        for cnl in range(0, bn_len):
            '''new para'''
            coe0 = math.pi * gps_car_norm_7 * fll_bn[cnl]
            lg_fac0 = int(np.log2((2.0 ** 23 - 1) / coe0))
            fll_bit_coe = int(np.ceil(coe0 * (2.0 ** lg_fac0)))
            fll_bit_shift = -lg_fac0

            fll_bit_coe_l = fll_bit_coe & (2 ** 15 - 1)
            fll_bit_coe_h = fll_bit_coe >> 15
            temp_coe = [fll_bit_coe_l, fll_bit_coe_h, fll_bit_shift]
            coe.append(temp_coe)
        return coe

    def fll_bit_3(self, fll3_bn, gps_car_norm_7):
        bn_len = len(fll3_bn)
        coe = []
        for cnl in range(bn_len):
            '''new para'''
            coe0 = 0.001 * math.pi * gps_car_norm_7 * ((fll3_bn[cnl] / 0.53) ** 2)  # * fll_sum_ms
            lg_fac0 = int(np.log2((2.0 ** 23 - 1) / coe0))
            fll_bit3_coe = int(np.ceil(coe0 * (2.0 ** lg_fac0)))
            fll_bit3_frac = -lg_fac0
            coe1 = math.pi * gps_car_norm_7 * fll3_bn[cnl] * 8 / 3.0
            lg_fac1 = int(np.log2((2.0 ** 23 - 1) / coe1))
            fll_bit3_coe2 = int(np.ceil(coe1 * (2.0 ** lg_fac1)))
            fll_bit3_frac2 = -lg_fac1

            fll_bit3_coe_l = fll_bit3_coe & (2 ** 15 - 1)
            fll_bit3_coe_h = fll_bit3_coe >> 15
            fll_bit3_coe_l2 = fll_bit3_coe2 & (2 ** 15 - 1)
            fll_bit3_coe_h2 = fll_bit3_coe2 >> 15
            temp_coe = [fll_bit3_coe_l, fll_bit3_coe_h, fll_bit3_frac, fll_bit3_coe_l2, fll_bit3_coe_h2, fll_bit3_frac2]
            coe.append(temp_coe)

        return coe

    def fll_sum(self, fll_sum_bn, gps_car_norm_7):
        para_num = np.shape(fll_sum_bn)
        coe = []
        for i in range(0, para_num[0]):
            for cnl in range(0, para_num[1]):
                '''new para'''
                coe0 = math.pi * gps_car_norm_7 * fll_sum_bn[i][cnl]
                lg_fac0 = int(np.log2((2.0 ** 23 - 1) / coe0))
                fll_sum_coe = int(np.ceil(coe0 * (2.0 ** lg_fac0)))
                fll_sum_frac = -lg_fac0

                fll_sum_coe_l = fll_sum_coe & (2 ** 15 - 1)
                fll_sum_coe_h = fll_sum_coe >> 15
                temp_coe = [fll_sum_coe_l, fll_sum_coe_h, fll_sum_frac]
                coe.append(temp_coe)
        return coe

    def fll_3_sum(self, fll3_sum_bn, gps_car_norm_7):
        para_num = np.shape(fll3_sum_bn)
        coe = []
        for i in range(0, para_num[0]):
            if i == 0:
                fll_sum_ms = 2
            elif i == 1:
                fll_sum_ms = 4
            elif i == 2:
                fll_sum_ms = 10
            for cnl in range(0, para_num[1]):
                '''new para'''
                coe0 = 0.001 * fll_sum_ms * math.pi * gps_car_norm_7 * ((fll3_sum_bn[i][cnl] / 0.53) ** 2)
                lg_fac0 = int(np.log2((2.0 ** 23 - 1) / coe0))
                fll_sum3_coe = int(np.ceil(coe0 * (2.0 ** lg_fac0)))
                fll_sum3_frac = -lg_fac0
                coe1 = math.pi * gps_car_norm_7 * fll3_sum_bn[i][cnl] * 8 / 3.0
                lg_fac1 = int(np.log2((2.0 ** 23 - 1) / coe1))
                fll_sum3_coe2 = int(np.ceil(coe1 * (2.0 ** lg_fac1)))
                fll_sum3_frac2 = -lg_fac1

                fll_sum3_coe_l = fll_sum3_coe & (2 ** 15 - 1)
                fll_sum3_coe_h = fll_sum3_coe >> 15
                fll_sum3_coe_l2 = fll_sum3_coe2 & (2 ** 15 - 1)
                fll_sum3_coe_h2 = fll_sum3_coe2 >> 15

                temp_coe = [fll_sum3_coe_l, fll_sum3_coe_h, fll_sum3_frac, fll_sum3_coe_l2, fll_sum3_coe_h2,
                            fll_sum3_frac2]
                coe.append(temp_coe)
        return coe

    def pll(self, pll_bn, pll_long_bn, pll_bn_narrow, gps_car_norm_7):
        coe = []
        length = len(pll_bn_narrow)
        for i in range(0, length):
            pll_sum_ms = 2
            if i == 0:
                pll_sum_ms = 2
            elif i == 1:
                pll_sum_ms = 4
            elif i == 2:
                pll_sum_ms = 10
            elif i == 3:
                pll_sum_ms = 20
            elif i == 4:
                pll_sum_ms = 2 * 20
            '''new para'''
            coe0 = 0.001 * pll_sum_ms * math.pi * gps_car_norm_7 * ((pll_bn_narrow[i] / 0.53) ** 2)
            lg_fac0 = int(np.log2((2.0 ** 23 - 1) / coe0))
            pll_coe = int(np.ceil(coe0 * (2.0 ** lg_fac0)))
            pll_frac = -lg_fac0
            coe1 = math.pi * gps_car_norm_7 * (pll_bn_narrow[i] * 8 / 3.0)
            lg_fac1 = int(np.log2((2.0 ** 23 - 1) / coe1))
            pll_coe2 = int(np.ceil(coe1 * (2.0 ** lg_fac1)))
            pll_frac2 = -lg_fac1

            pll_coe_l = pll_coe & (2 ** 15 - 1)
            pll_coe_h = pll_coe >> 15
            pll_coe_l2 = pll_coe2 & (2 ** 15 - 1)
            pll_coe_h2 = pll_coe2 >> 15
            temp_coe = [pll_coe_l, pll_coe_h, pll_frac, pll_coe_l2, pll_coe_h2, pll_frac2]
            coe.append(temp_coe)
        para_num = np.shape(pll_bn)
        for i in range(0, para_num[0]):
            if i == 0:
                pll_sum_ms = 1
            elif i == 1:
                pll_sum_ms = 2
            elif i == 2:
                pll_sum_ms = 4
            elif i == 3:
                pll_sum_ms = 10
            elif i == 4:
                pll_sum_ms = 20
            elif i == 5:
                pll_sum_ms = 100
            for cnl in range(0, para_num[1]):
                '''new para'''
                coe0 = 0.001 * pll_sum_ms * math.pi * gps_car_norm_7 * ((pll_bn[i][cnl] / 0.53) ** 2)
                lg_fac0 = int(np.log2((2.0 ** 23 - 1) / coe0))
                pll_coe = int(np.ceil(coe0 * (2.0 ** lg_fac0)))
                pll_frac = -lg_fac0
                coe1 = math.pi * gps_car_norm_7 * (pll_bn[i][cnl] * 8 / 3.0)
                lg_fac1 = int(np.log2((2.0 ** 23 - 1) / coe1))
                pll_coe2 = int(np.ceil(coe1 * (2.0 ** lg_fac1)))
                pll_frac2 = -lg_fac1

                pll_coe_l = pll_coe & (2 ** 15 - 1)
                pll_coe_h = pll_coe >> 15
                pll_coe_l2 = pll_coe2 & (2 ** 15 - 1)
                pll_coe_h2 = pll_coe2 >> 15
                temp_coe = [pll_coe_l, pll_coe_h, pll_frac, pll_coe_l2, pll_coe_h2, pll_frac2]
                coe.append(temp_coe)
        length = len(pll_long_bn)
        for i in range(0, length):
            pll_sum_ms = 2 * 20
            if i == 0:
                pll_sum_ms = 2 * 20
            elif i == 1:
                pll_sum_ms = 5 * 20
            elif i == 2:
                pll_sum_ms = 10 * 20
            elif i == 3:
                pll_sum_ms = 15 * 20
            elif i == 4:
                pll_sum_ms = 30 * 20
            '''new para'''
            coe0 = 0.001 * pll_sum_ms * math.pi * gps_car_norm_7 * ((pll_long_bn[i] / 0.53) ** 2)
            lg_fac0 = int(np.log2((2.0 ** 23 - 1) / coe0))
            pll_coe = int(np.ceil(coe0 * (2.0 ** lg_fac0)))
            pll_frac = -lg_fac0
            coe1 = math.pi * gps_car_norm_7 * (pll_long_bn[i] * 8 / 3.0)
            lg_fac1 = int(np.log2((2.0 ** 23 - 1) / coe1))
            pll_coe2 = int(np.ceil(coe1 * (2.0 ** lg_fac1)))
            pll_frac2 = -lg_fac1

            pll_coe_l = pll_coe & (2 ** 15 - 1)
            pll_coe_h = pll_coe >> 15
            pll_coe_l2 = pll_coe2 & (2 ** 15 - 1)
            pll_coe_h2 = pll_coe2 >> 15
            temp_coe = [pll_coe_l, pll_coe_h, pll_frac, pll_coe_l2, pll_coe_h2, pll_frac2]
            coe.append(temp_coe)
        return coe

    def pll3(self, pll3_bn, gps_car_norm_7):
        coe_size = np.shape(pll3_bn)
        coe = []
        pll_sum_ms = 1
        for i in range(0, coe_size[0]):
            if i == 0:
                pll_sum_ms = 1
            elif i == 1:
                pll_sum_ms = 2
            elif i == 2:
                pll_sum_ms = 4
            elif i == 3:
                pll_sum_ms = 10
            elif i == 4:
                pll_sum_ms = 20
            elif i == 5:
                pll_sum_ms = 40
            for cnl in range(0, coe_size[1]):
                '''new para'''
                coe0 = 0.001 * pll_sum_ms * math.pi * ((pll3_bn[i][cnl] / 0.7845) ** 3)
                lg_fac0 = int(np.log2((2.0 ** 23 - 1) / coe0))
                pll3_coe = int(np.ceil(coe0 * (2.0 ** lg_fac0)))
                pll3_frac = -lg_fac0
                coe1 = 0.001 * pll_sum_ms * math.pi * gps_car_norm_7 * 1.1 * ((pll3_bn[i][cnl] / 0.7845) ** 2)
                lg_fac1 = int(np.log2((2.0 ** 23 - 1) / coe1))
                pll3_coe2 = int(np.ceil(coe1 * (2.0 ** lg_fac1)))
                pll3_frac2 = -lg_fac1
                coe3_0 = math.pi * gps_car_norm_7 * 2.4 * (pll3_bn[i][cnl] / 0.7845)
                lg_fac3 = int(np.log2((2.0 ** 23 - 1) / coe3_0))
                pll3_coe3 = int(np.ceil(coe3_0 * (2.0 ** lg_fac3)))
                pll3_frac3 = -lg_fac3

                pll3_coe_l = pll3_coe & (2 ** 15 - 1)
                pll3_coe_h = pll3_coe >> 15
                pll3_coe_l2 = pll3_coe2 & (2 ** 15 - 1)
                pll3_coe_h2 = pll3_coe2 >> 15
                pll3_coe_l3 = pll3_coe3 & (2 ** 15 - 1)
                pll3_coe_h3 = pll3_coe3 >> 15
                temp_coe = [pll3_coe_l, pll3_coe_h, pll3_frac, pll3_coe_l2, pll3_coe_h2, pll3_frac2, pll3_coe_l3,
                            pll3_coe_h3, pll3_frac3]
                coe.append(temp_coe)
        return coe

    def hexPrint(self, arr, head):
        if head == "PLL ??ms:":
            para_convert.gl_nLongPll = "U32 nLongPll[5][6] = {"
            para_convert.gl_all = "U32 nAll[5][6] = {"
        if head == "DLL 20ms:":
            para_convert.gl_nDllSum2 = "U32 nDllSum2[6][3] = {"
        idx = 0
        for each_arr in arr:
            print(head, end=' ')
            if head == "CN0:":
                if len(para_convert.gl_nCn0) < 33:
                    for item in each_arr:
                        if item < 0:
                            item = 2 ** 32 + item
                        para_convert.gl_nCn0 += '0x{:0>8X}, '.format(item)
                    para_convert.gl_nCn0 = para_convert.gl_nCn0[:-2] + "};"
            if head == "PLL ??ms:":
                if idx < 5:
                    para_convert.gl_all += "{"
                    for item in each_arr:
                        if item < 0:
                            item = 2 ** 32 + item
                            para_convert.gl_all += '0x{:X}, '.format(item)
                        elif item > 65535:
                            para_convert.gl_all += '0x{:0>8X}, '.format(item)
                        else:
                            para_convert.gl_all += '0x{:0>4X}, '.format(item)
                    para_convert.gl_all = para_convert.gl_all[:-2] + '},\n\t\t\t\t\t\t'
                if idx > 4 and idx < 10:
                    para_convert.gl_nPll2 += '{'
                    for item in each_arr:
                        if item < 0:
                            item = 2 ** 32 + item
                            para_convert.gl_nPll2 += '0x{:X}, '.format(item)
                        elif item > 65535:
                            para_convert.gl_nPll2 += '0x{:0>8X}, '.format(item)
                        else:
                            para_convert.gl_nPll2 += '0x{:0>4X}, '.format(item)
                    para_convert.gl_nPll2 = para_convert.gl_nPll2[:-2] + '},\n\t\t\t\t\t\t'
                if idx >= 10:
                    para_convert.gl_nLongPll += "{"
                    for item in each_arr:
                        if item < 0:
                            item = 2 ** 32 + item
                            para_convert.gl_nLongPll += '0x{:X}, '.format(item)
                        elif item > 65535:
                            para_convert.gl_nLongPll += '0x{:0>8X}, '.format(item)
                        else:
                            para_convert.gl_nLongPll += '0x{:0>4X}, '.format(item)
                    para_convert.gl_nLongPll = para_convert.gl_nLongPll[:-2] + '},\n\t\t\t\t\t\t'
            if head == "PLL3 ?ms:":
                para_convert.gl_nPll3 += '{'
                for item in each_arr:
                    if item < 0:
                        item = 2 ** 32 + item
                        para_convert.gl_nPll3 += '0x{:X}, '.format(item)
                    elif item > 65535:
                        para_convert.gl_nPll3 += '0x{:0>8X}, '.format(item)
                    else:
                        para_convert.gl_nPll3 += '0x{:0>4X}, '.format(item)
                para_convert.gl_nPll3 = para_convert.gl_nPll3[:-2] + '},\n\t\t\t\t\t\t'
            if head == "FLL ?ms:":
                para_convert.gl_nFll2 += "{"
                for item in each_arr:
                    if item < 0:
                        item = 2 ** 32 + item
                        para_convert.gl_nFll2 += '0x{:X}, '.format(item)
                    elif item > 65535:
                        para_convert.gl_nFll2 += '0x{:0>8X}, '.format(item)
                    else:
                        para_convert.gl_nFll2 += '0x{:0>4X}, '.format(item)
                para_convert.gl_nFll2 = para_convert.gl_nFll2[:-2] + '},\n\t\t\t\t\t\t'
            if head == "FLL3 ?ms:":
                para_convert.gl_nFll3 += '{'
                for item in each_arr:
                    if item < 0:
                        item = 2 ** 32 + item
                        para_convert.gl_nFll3 += '0x{:X}, '.format(item)
                    elif item > 65535:
                        para_convert.gl_nFll3 += '0x{:0>8X}, '.format(item)
                    else:
                        para_convert.gl_nFll3 += '0x{:0>4X}, '.format(item)
                para_convert.gl_nFll3 = para_convert.gl_nFll3[:-2] + '},\n\t\t\t\t\t\t'
            if head == "DLL 1ms:":
                para_convert.gl_nDllBit += "{"
                for item in each_arr:
                    if item < 0:
                        item = 2 ** 32 + item
                        para_convert.gl_nDllBit += '0x{:X}, '.format(item)
                    elif item > 65535:
                        para_convert.gl_nDllBit += '0x{:0>8X}, '.format(item)
                    else:
                        para_convert.gl_nDllBit += '0x{:0>4X}, '.format(item)
                para_convert.gl_nDllBit = para_convert.gl_nDllBit[:-2] + '},\n\t\t\t\t\t\t'
            if head == "DLL 20ms:":
                if idx < 2:
                    para_convert.gl_nDllSum1 += '{'
                    for item in each_arr:
                        if item < 0:
                            item = 2 ** 32 + item
                            para_convert.gl_nDllSum1 += '0x{:X}, '.format(item)
                        elif item > 65535:
                            para_convert.gl_nDllSum1 += '0x{:0>8X}, '.format(item)
                        else:
                            para_convert.gl_nDllSum1 += '0x{:0>4X}, '.format(item)
                    para_convert.gl_nDllSum1 = para_convert.gl_nDllSum1[:-2] + '},\n\t\t\t\t\t\t'
                if idx > 1:
                    para_convert.gl_nDllSum2 += "{"
                    for item in each_arr:
                        if item < 0:
                            item = 2 ** 32 + item
                            para_convert.gl_nDllSum2 += '0x{:X}, '.format(item)
                        elif item > 65535:
                            para_convert.gl_nDllSum2 += '0x{:0>8X}, '.format(item)
                        else:
                            para_convert.gl_nDllSum2 += '0x{:0>4X}, '.format(item)
                    para_convert.gl_nDllSum2 = para_convert.gl_nDllSum2[:-2] + '},\n\t\t\t\t\t\t'
            for item in each_arr:
                if item < 0:
                    item = 2 ** 32 + item
                    print('0x{:X},'.format(item), end=' ')
                elif item > 65535:
                    print('0x{:0>8X},'.format(item), end=' ')
                else:
                    print('0x{:0>4X},'.format(item), end=' ')
            print()
            idx += 1
        if head == "PLL ??ms:":
            para_convert.gl_nPll2 = para_convert.gl_nPll2[:-8] + '},\n\t\t\t\t\t{\t'
        if head == "PLL3 ?ms:":
            para_convert.gl_nPll3 = para_convert.gl_nPll3[:-8] + '},\n\t\t\t\t\t{\t'
        if head == "FLL ?ms:" and idx > 1:
            para_convert.gl_nFll2 = para_convert.gl_nFll2[:-8] + '},\n\t\t\t\t\t{\t'
        if head == "FLL3 ?ms:" and idx > 1:
            para_convert.gl_nFll3 = para_convert.gl_nFll3[:-8] + '},\n\t\t\t\t\t{\t'
        if head == "DLL 20ms:":
            para_convert.gl_nDllSum1 = para_convert.gl_nDllSum1[:-8] + '},\n\t\t\t\t\t{\t'

    def cal(self, dll, pll, pll_long, pll3, fll, fll3, dll_bit, fll_bit, fll3_bit, all_bn, mode=0, rank=control.high,
            cnf=[], gps_cn0_db=[], smooth_fac_factor=[]):
        if mode == int(b'10', 2):
            dll_bit = np.append(dll_bit, dll)

            fll_m = self.fll_sum(fll, self.gps_car_norm1_7)
            pll_m = self.pll(pll, all_bn, self.gps_car_norm1_7)
            dll_bit_m = self.dll_bit(dll_bit, self.gps_code_norm)
            fll_bit_m = self.fll_bit(fll_bit, self.gps_car_norm1_7)
            para = [pll_m, fll_bit_m, fll_m, dll_bit_m]
            print('-*-*-', dll_bit, fll_m, pll_m, dll_bit_m, fll_bit_m, para, '-*-*-')
        elif mode == int(b'00', 2):
            dll_m = self.dll_sum(dll, self.gps_code_norm)
            fll_m = self.fll_sum(fll, self.gps_car_norm1_7)
            fll3_m = self.fll_3_sum(fll3, self.gps_car_norm1_7)
            pll_m = self.pll(pll, pll_long, all_bn, self.gps_car_norm1_7)
            pll3_m = self.pll3(pll3, self.gps_car_norm1_7)

            dll_bit_m = self.dll_bit(dll_bit, self.gps_code_norm)
            fll_bit_m = self.fll_bit(fll_bit, self.gps_car_norm1_7)
            fll3_bit_m = self.fll_bit_3(fll3_bit, self.gps_car_norm1_7)
            para = [pll_m, pll3_m, fll_bit_m, fll_m, fll3_bit_m, fll3_m, dll_bit_m, dll_m]
            # self.hexPrint([list(gps_cn0_db)], "CN0:")
            # self.hexPrint([smooth_fac_factor], "PLL smooth:")
            # self.hexPrint([], "FLL threshold:")
            self.hexPrint(pll_m, "PLL ??ms:")
            self.hexPrint(pll3_m, "PLL3 ?ms:")

            self.hexPrint(fll_bit_m, "FLL ?ms:")
            self.hexPrint(fll_m, "FLL ?ms:")
            self.hexPrint(fll3_bit_m, "FLL3 ?ms:")
            self.hexPrint(fll3_m, "FLL3 ?ms:")

            self.hexPrint(dll_bit_m, "DLL 1ms:")
            self.hexPrint(dll_m, "DLL 20ms:")
            print("FLL threshold:", "0x{:0>2X}{:0>2X}{:0>2X}{:0>2X}".format(cnf[3], cnf[2], cnf[1], cnf[0]))
            print("PLL threshold:", "0x{:0>2X}{:0>2X}{:0>2X}{:0>2X}".format(cnf[7], cnf[6], cnf[5], cnf[4]))
            para_convert.gl_nThreshold += " {}0x{:0>2X}{:0>2X}{:0>2X}{:0>2X}, 0x{:0>2X}{:0>2X}{:0>2X}{:0>2X}{}," \
                .format("{", cnf[3], cnf[2], cnf[1], cnf[0], cnf[7], cnf[6], cnf[5], cnf[4], "}")
            # print('-*-*-', dll_m, fll_m, fll3_m, pll_m, pll3_m, dll_bit_m, fll_bit_m, fll3_bit_m, para, '-*-*-')
        new_para = list(flat(para))
        # print(new_para)
        result = self.hex_to_dec(new_para, rank, cnf, gps_cn0_db, smooth_fac_factor)

        return result

    def hex_to_dec(self, data, mode, cnf, gps_cn0_db=[], smooth_fac_factor=[]):
        smooth_fac_shift0 = smooth_fac_factor[0]
        smooth_fac_shift1 = smooth_fac_factor[1]
        fli_smooth_factor = smooth_fac_factor[2]
        fli_smooth_par = np.floor(fli_smooth_factor * (2.0 ** smooth_fac_shift0) + 0.5).astype(int)
        f_parameter = [fli_smooth_par[0] & 0xff, fli_smooth_par[0] >> 8, fli_smooth_par[1] & 0xff,
                       fli_smooth_par[1] >> 8]
        print("FLL smooth:", "0x{:0>2X}{:0>2X},".format(f_parameter[1], f_parameter[0]),
              "0x{:0>2X}{:0>2X},".format(f_parameter[3], f_parameter[2]))

        pli_smooth_factor = smooth_fac_factor[3]
        # pli_smooth_par = np.array([np.ceil(pli_smooth_factor * (2.0 ** smooth_fac_shift0)),
        #                            np.ceil((1 - pli_smooth_factor) * (2.0 ** smooth_fac_shift1))], dtype=int)
        pli_smooth_par = np.floor(pli_smooth_factor * (2.0 ** smooth_fac_shift1) + 0.5).astype(int)
        p_parameter = [pli_smooth_par[0] & 0xff, pli_smooth_par[0] >> 8, pli_smooth_par[1] & 0xff,
                       pli_smooth_par[1] >> 8]
        print("PLL smooth:", "0x{:0>2X}{:0>2X},".format(p_parameter[1], p_parameter[0]),
              "0x{:0>2X}{:0>2X},".format(p_parameter[3], p_parameter[2]))
        if len(para_convert.gl_nSmooth) < 33:
            para_convert.gl_nSmooth += "{}0x{:0>2X}{:0>2X}, 0x{:0>2X}{:0>2X}{},".format("{{",
                                                                                        p_parameter[1], p_parameter[0],
                                                                                        p_parameter[3], p_parameter[2],
                                                                                        "}")
            para_convert.gl_nSmooth += "{}0x{:0>2X}{:0>2X}, 0x{:0>2X}{:0>2X}{};".format(" {", f_parameter[1],
                                                                                        f_parameter[0],
                                                                                        f_parameter[3], f_parameter[2],
                                                                                        "}}")
        send_data = [0xaa, 0xaa]
        lenth = len(data)
        bit_32 = 3 * np.arange(1, 100) - 1

        gps_cn0_th = (np.floor((gps_cn0_db / 10 - 3) * (2 ** (5 + smooth_fac_shift1)) / np.log10(2) + 0.5)).astype(int)
        self.hexPrint([list(gps_cn0_th)], "CN0:")

        i = 0
        for num in gps_cn0_th:
            if num < 0:
                gps_cn0_th[i] = num + 2 ** 32
            i += 1
        hex_8bit = []
        for num in gps_cn0_th:
            hex_8bit.append(num & 0xff)
            hex_8bit.append((num >> 8) & 0xff)
            hex_8bit.append((num >> 16) & 0xff)
            hex_8bit.append((num >> 24) & 0xff)

        menxian = [0x0, mode] + hex_8bit + p_parameter + f_parameter + cnf
        if mode == control.high:
            pass
            # menxian =[0x0, mode] + p_parameter + f_parameter + cnf
        elif mode == control.mid:
            pass
            # menxian =[0x0, mode, 0xAF, 0x07, 0xE2, 0x03, 0x9A, 0x19, 0x9A, 0x03, 0x0F, 0x64, 0x32, 0x10, 0x23, 0x1E, 0x19, 0x19]
        elif mode == control.low:
            pass
            # menxian = [0x0, mode, 0xAF, 0x07, 0xE2, 0x03, 0x9A, 0x19, 0x9A, 0x03, 0x0F, 0x64, 0x32, 0x10, 0x23, 0x1E, 0x19, 0x19]
        send_data.extend(menxian)
        for i in range(lenth):
            if i not in bit_32:
                data_H = int((data[i] & 0xff00) / 256)
                data_L = int(data[i] & 0x00ff)
                send_data.append(data_L)  # 低位在前高位在后
                send_data.append(data_H)
            else:
                data4 = int((data[i] & 0xff000000) / 2 ** 24)
                data3 = int((data[i] & 0x00ff0000) / 2 ** 16)
                data2 = int((data[i] & 0x0000ff00) / 2 ** 8)
                data1 = int((data[i] & 0x000000ff))
                send_data.append(data1)  #
                send_data.append(data2)
                send_data.append(data3)
                send_data.append(data4)
        send_data.extend([0xbb, 0xbb])  ##add the choose
        lenth = len(send_data) - 4
        print("the lenth is ", lenth)
        len_H = int((lenth & 0xff00) / 256)
        len_L = int(lenth & 0x00ff)
        send_data.insert(2, len_L)
        send_data.insert(3, len_H)
        print([hex(i) for i in send_data])
        hex_data = [hex(i) for i in send_data]
        hex_out(hex_data)
        return send_data


def str_tohex(str):
    getstr = []
    for sub in str.split(' '):
        getstr.append(hex(int(sub, 16)))
    return getstr


def hex_out(hex_data):
    for i, x in enumerate(hex_data):
        if (len(x) == 3):
            hex_data[i] = "0x0" + x[2:3].upper()
        elif (len(x) == 4):
            hex_data[i] = "0x" + x[2:4].upper()
    st_da = str(hex_data)
    newdata = re.sub('[\[\]\']', '', st_da)
    print(newdata)
    st_da = re.sub(r'\W', "", st_da)
    st_da = re.sub(r'0x', " ", st_da)
    print(st_da)
    return st_da


def flat(l):
    for k in l:
        if not isinstance(k, (list, tuple)):
            yield k
        else:
            yield from flat(k)


def cal_para(dll, pll, fll, dll_bit, fll_bit):
    A = para_convert()
    dll_m = A.dll_sum(dll, A.gps_code_norm)
    fll_m = A.fll_sum(fll, A.gps_car_norm1_7)
    pll_m = A.pll(pll, A.gps_car_norm1_7)
    dll_bit_m = A.dll_bit(dll_bit, A.gps_code_norm)
    fll_bit_m = A.fll_bit(fll_bit, A.gps_car_norm1_7)
    para = [dll_m, fll_m, pll_m, dll_bit_m, fll_bit_m]
    # print(para)
    new_para = list(flat(para))
    print(new_para)
    result = A.hex_to_dec(new_para)
    return result


if __name__ == '__main__':
    mode = 0
    rank = control.high
    # dll_bn = np.array([2.0,1.0,0.4,2.0,1.2,1.0,0.5,0.3,0.1,0.02,0.01])
    # dll_sum_bn = np.array([2.0,1.2,1.0,2.0,1.2,1.0,0.02,0.01])
    # fll_bn  = np.array([1.5,1.5,0.6])
    # fll_sum_bn = np.array([[20.0, 10.0, 8.0], [16.0, 6.0, 4.0], [12.0, 3.5, 2.0]])  # 2ms, 4ms, 10ms
    #
    # pll_bn = np.array([[20.0, 8.0, 6.0] , [15.0, 6.0, 5.0], [10.0, 4.0, 4.0],
    #                    [4.0, 3.5, 3.0], [2.0, 2.0, 2.0], [1.0, 0.6, 0.4]])  # 1ms, 2ms, 4ms, 10ms, 20ms, 100ms
    # all_bn = np.array([1.0,0.6,0.5,0.4,0.3])# 2ms, 4ms, 10ms, 20ms, 100ms
    A = para_convert()
    '''for old track'''
    pll_bn_wide   = [16, 12, 5, 3.0]
    pll_bn_narrow = [10, 7,  3, 2.5, 1.5]
    pll_long_bn = np.array([2.0, 1.5, 1.5, 1.0, 1.0]) #1103
    smooth_fac_shift0 = 16
    smooth_fac_shift1 = 10
    fli_smooth_factor = np.array([0.1, 0.3])
    pli_smooth_factor = np.array([0.06, 0.06])
    #gps_cn0_db = np.array([33.0, 29.8, 27.3, 25.0, 22.5, 20.0, 18.5, 17.0, 39.0, 39.0])
    # gps_cn0_db = np.array([33.0, 29.8, 27.3, 25.0, 22.5, 20.0, 18.5, 17.0, 39.0, 00.0]) # disable
    # gps_cn0_db = np.array([33.0, 29.8, 27.3, 25.0, 22.0, 19.5, 18.0, 16.5, 39.0, 39.0])  # enable 1103
    # gps_cn0_db = np.array([32.0, 28, 25, 22, 19, 17, 15, 13, 36.0, 50.0])  # enable 1103
    gps_cn0_db = np.array([32.0, 28, 25, 22, 19, 17, 15, 13, 36.0, 50.0])  # enable 1103
    #gps_cn0_db = np.array([33.0, 29.8, 27.3, 25.0, 22.5, 20.0, 18.5, 17.0, 39.0, 39.0])  # enable
    # gps_cn0_db = np.array([35.0, 31.0, 28.3, 26.0, 23.5, 21.0, 19.0, 17.0, 39.0, 35.0])
    narrow_dll_bn = 1.0
    narrow_long_dll_bn =[narrow_dll_bn, 0.1, 0.1, 0.1, 0.05, 0.05]

    smooth_fac_factor = list()
    smooth_fac_factor.append(16)
    smooth_fac_factor.append(18)
    smooth_fac_factor.append(fli_smooth_factor)
    smooth_fac_factor.append(pli_smooth_factor)

    ###high
    dll_bn = np.array([2.0])
    dll_sum_bn = np.array([2.0, 1.0] + narrow_long_dll_bn)  # narrow, 2*20, 5*20, 10*20, 15*20, 30*20

    fll_bn = np.array([1.5])
    fll_sum_bn = np.array([[30], [20], [8]])
    # pll_bn = np.array([[12], [8], [6], [3.0], [pll_group_4]]) #1103
    pll_bn = np.array([[20], [pll_bn_wide[0]], [pll_bn_wide[1]], [pll_bn_wide[2]], [pll_bn_wide[3]]])
    fll3_bn = np.array([3.0])
    fll3_sum_bn = np.array([[20], [16], [12.0]])
    pll3_bn = np.array([[28], [22], [18], [12], [6.0]])

    #limit_cfg = [8, 50, 25, 12, 35, 22, 15, 12]
    limit_cfg = [8, 50, 25, 12, 33, 26, 16, 13]
    print("the high state:")
    result = A.cal(dll_sum_bn, pll_bn, pll_long_bn, pll3_bn, fll_sum_bn, fll3_sum_bn, dll_bn, fll_bn, fll3_bn, pll_bn_narrow, mode, rank, limit_cfg, gps_cn0_db, smooth_fac_factor)

    ###mid
    mode = 0
    rank = control.mid
    dll_bn = np.array([1.0])
    dll_sum_bn = np.array([1.2, 0.6]  # 0.6, 0.3, 0.15, 0.1
                           + narrow_long_dll_bn)
    fll_bn = np.array([1.5])
    fll_sum_bn = np.array([[20], [12], [5]])
    # pll_bn = np.array([[12], [8], [6], [4.5], [pll_group_4]])
    pll_bn = np.array([[16],  [pll_bn_wide[0]], [pll_bn_wide[1]], [pll_bn_wide[2]], [pll_bn_wide[3]]])
    fll3_bn = np.array([1.5])
    fll3_sum_bn = np.array([[16], [12], [6.0]])
    pll3_bn = np.array([[12], [8], [6], [5], [3]])

    # limit_cfg = [12, 100, 50, 16, 35, 22, 17, 12]
    limit_cfg = [10, 100, 40, 16, 33, 26, 16, 15]
    print("the middle state:")
    result = A.cal(dll_sum_bn, pll_bn, pll_long_bn, pll3_bn, fll_sum_bn, fll3_sum_bn, dll_bn, fll_bn, fll3_bn, pll_bn_narrow, mode, rank, limit_cfg, gps_cn0_db, smooth_fac_factor)

    ###low
    mode = 0
    rank = control.low
    dll_bn = np.array([0.4])
    # dll_sum_bn = np.array([1.0, 0.2,
    #                        narrow_dll_bn, 0.05, 0.03, 0.02, 0.02, 0.01])
    dll_sum_bn = np.array([1.0, 0.2]
                           + narrow_long_dll_bn)
    fll_bn = np.array([0.6])
    '''pwr-130 steady'''
    # fll_sum_bn = np.array([[20], [10], [6]])
    # pll_bn = np.array([[12], [8], [6], [5], [pll_group_4]])
    '''pwr-133 steady'''
    # fll_sum_bn = np.array([[20], [10], [5]])
    # pll_bn = np.array([[12], [8], [8], [5], [pll_group_4]])  # pll_group_4 = 3.5

    '''pwr-135 steady'''
    fll_sum_bn = np.array([[20], [10], [6]])  # 3.5~6
    pll_bn = np.array([[16],  [pll_bn_wide[0]], [pll_bn_wide[1]], [pll_bn_wide[2]], [pll_bn_wide[3]]])  # 3.0~4.5; 1.5~3.5
    '''old par'''
    # fll_sum_bn = np.array([[8], [4], [2.0]])
    # pll_bn = np.array([[8], [6], [4], [3.0], [pll_group_4]])
    '''new par'''
    # fll_sum_bn = np.array([[60], [8.75], [2.0]])
    # pll_bn = np.array([[12], [8], [4], [3.0], [pll_group_4]])

    fll3_bn = np.array([1.0])
    fll3_sum_bn = np.array([[12], [8], [4.0]])
    pll3_bn = np.array([[10], [8], [6.0], [3.5], [1.0]])

    # limit_cfg = [12, 100, 50, 16, 35, 22, 17, 12]
    limit_cfg = [12, 100, 45, 16, 33, 26, 23, 16]
    print("the low state:")
    result = A.cal(dll_sum_bn, pll_bn, pll_long_bn, pll3_bn, fll_sum_bn, fll3_sum_bn, dll_bn, fll_bn, fll3_bn, pll_bn_narrow, mode, rank, limit_cfg, gps_cn0_db, smooth_fac_factor)

    # data = {"fll_2": 7.573589424255466, "dll1": 0.7209415625849652, "fll_bit": 2.2019919183998953,
    #  "pll_3": 7.377932579656648, "pll_2": 9.231968331200513, "fll": 13.687896404735579, "pll_1": 11.848610966939232,
    #  "fll_1": 7.021750488014408, "dll": 2.1373946981326593, "pll": 35.68908386923844, "dll_bit": 0.7025611528814057}

    print(A.gl_nCn0)
    print(A.gl_nSmooth)
    para_convert.gl_nThreshold = para_convert.gl_nThreshold[:-1] + "};"
    print(A.gl_nThreshold)
    para_convert.gl_nPll2 = para_convert.gl_nPll2[:-9] + '};'
    print(para_convert.gl_nPll2)
    para_convert.gl_nLongPll = para_convert.gl_nLongPll[:-8] + '};'
    print(para_convert.gl_nLongPll)
    para_convert.gl_all = para_convert.gl_all[:-8] + '};'
    print(para_convert.gl_all)
    para_convert.gl_nPll3 = para_convert.gl_nPll3[:-9] + '};'
    print(para_convert.gl_nPll3)
    para_convert.gl_nFll2 = para_convert.gl_nFll2[:-9] + '};'
    print(para_convert.gl_nFll2)
    para_convert.gl_nFll3 = para_convert.gl_nFll3[:-9] + '};'
    print(para_convert.gl_nFll3)
    para_convert.gl_nDllBit = para_convert.gl_nDllBit[:-8] + '};'
    print(para_convert.gl_nDllBit)
    para_convert.gl_nDllSum1 = para_convert.gl_nDllSum1[:-9] + '};'
    print(para_convert.gl_nDllSum1)
    para_convert.gl_nDllSum2 = para_convert.gl_nDllSum2[:-8] + '};'
    print(para_convert.gl_nDllSum2)

    fd = open("tmp.c", 'w')
    fd.write(A.gl_nCn0 + '\n' + A.gl_nSmooth + '\n' + A.gl_nThreshold + '\n'
             + A.gl_nPll2 + '\n' + A.gl_nLongPll + '\n' + A.gl_all + '\n' + A.gl_nPll3 + '\n'
             + A.gl_nFll2 + '\n' + A.gl_nFll3 + '\n' + A.gl_nDllBit + '\n'
             + A.gl_nDllSum1 + '\n' + A.gl_nDllSum2)
    fd.close()

