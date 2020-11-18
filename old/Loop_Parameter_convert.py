import numpy as np
import math
import re
gps_fs =2*1024000.0
gps_fs1 =8*1024000.0
gps_car_norm = (2**31)/gps_fs
gps_car_norm1 =(2**31)/gps_fs1 #
# gps_code_norm = gps_car_norm1*2.0
# gps_car_norm1_7 = gps_car_norm1/(2.0**7)
class control:
    high = 0
    mid = 1
    low = 2
    num =3

class para_convert:
    def __init__(self):
        self.gps_code_norm = gps_car_norm1 * 2.0
        self.gps_car_norm1_7 = gps_car_norm1 / (2.0 ** 7)

    """function to transform the vector for table"""

    def dll_bit(self,dll_bn, gps_code_norm):
        # para_num = np.shape(dll_bn)
        length = len(dll_bn)
        coe = []
        for i in range(length):
            '''old para'''
            # coe_dll_0 = int(np.ceil(0.001 * gps_code_norm * ((dll_bn[i] / 0.53) ** 2) * (2.0 ** 10))) # c1 = (0.001*2^20/1000.0*(bn/0.53)^2) / 2^12
            # coe_dll_1 = int(np.ceil((gps_code_norm * dll_bn[i] * 8 / 3.0) / (2.0**2)))
            # frac_dll_0 = -12   # >> (10 + 12)
            # frac_dll_1 = -10  # >> 10
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

        # for i in range(para_num[0]):
        #     if i == 0:
        #         dll_ms = 1
        #     elif i == 1:
        #         dll_ms = 2
        #     elif i == 2:
        #         dll_ms = 4
        #     elif i == 3:
        #         dll_ms = 10
        #     elif i == 4:
        #         dll_ms = 20
        return coe

    def dll_sum(self,dll_sum_bn, gps_code_norm):
        length = len(dll_sum_bn)
        coe = []
        # para_num = np.shape(dll_sum_bn)
        for i in range(length):
            '''old para'''
            # fll_bit_coe = int(np.ceil(math.pi * gps_car_norm_7 * fll_bn[i] * (2**10)))   # 0.01 -> 1054
            # fll_bit_shift = -10  # /1024
            '''new para'''
            coe0 = gps_code_norm * dll_sum_bn[i]
            lg_fac = int(np.log2((2.0 ** 19 - 1) / coe0))
            fll_bit_coe = int(np.ceil(coe0 * (2.0 ** lg_fac)))
            fll_bit_shift = -(lg_fac + 12)

            fll_bit_coe_l = fll_bit_coe & (2 ** 15 - 1)
            fll_bit_coe_h = fll_bit_coe >> 15
            temp_coe = [fll_bit_coe_l, fll_bit_coe_h, fll_bit_shift]
            coe.append(temp_coe)

        return coe

    def fll_bit(self,fll_bn, gps_car_norm_7):
        # length = len(fll_bn)
        # coe = []
        # for i in range(0, length):
        #     '''old para'''
        #     # fll_bit_coe = int(np.ceil(math.pi * gps_car_norm_7 * fll_bn[i] * (2**10)))   # 0.01 -> 1054
        #     # fll_bit_shift = -10  # /1024
        #     coe.append(temp_coe)
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
        # fll_sum_ms = 4
        # length = len(fll3_bn)
        # # coe_size = np.shape(fll3_bn)
        # coe = []
        # for i in range(0, length):
        #     '''old para'''
        #     # fll_bit3_coe = int(np.ceil(0.001 * fll_sum_ms * math.pi * gps_car_norm_7 * ((fll3_bn[0][i]/0.53)**2) * (2**10)))
        #     # fll_bit3_coe2 = int(np.ceil(math.pi * gps_car_norm_7 * fll3_bn[0][i] * 8/3.0 * (2**10)))
        #     # fll_bit3_frac = -10
        #     # fll_bit3_frac2 = -10
        #       coe.append(temp_coe)

        # fll_sum_ms = 10
        # for i in range(0, coe_size[1]):
        #     '''old para'''
        #     # fll_bit3_coe = int(np.ceil(0.001 * fll_sum_ms * math.pi * gps_car_norm_7 * ((fll3_bn[1][i]/0.53)**2) * (2**10)))
        #     # fll_bit3_coe2 = int(np.ceil(math.pi * gps_car_norm_7 * fll3_bn[1][i] * 8/3.0 * (2**10)))
        #     # fll_bit3_frac = -10
        #     # fll_bit3_frac2 = -10
        #
        #     '''new para'''
        #     coe0 = 0.001 * fll_sum_ms * math.pi * gps_car_norm_7 * ((fll3_bn[1][i] / 0.53) ** 2)
        #     lg_fac0 = int(np.log2((2.0 ** 23 - 1) / coe0))
        #     fll_bit3_coe = int(np.ceil(coe0 * (2.0 ** lg_fac0)))
        #     fll_bit3_frac = -lg_fac0
        #     coe1 = math.pi * gps_car_norm_7 * fll3_bn[1][i] * 8 / 3.0
        #     lg_fac1 = int(np.log2((2.0 ** 23 - 1) / coe1))
        #     fll_bit3_coe2 = int(np.ceil(coe1 * (2.0 ** lg_fac1)))
        #     fll_bit3_frac2 = -lg_fac1
        #
        #     fll_bit3_coe_l = fll_bit3_coe & (2**15 - 1)
        #     fll_bit3_coe_h = fll_bit3_coe >> 15
        #     fll_bit3_coe_l2 = fll_bit3_coe2 & (2**15 - 1)
        #     fll_bit3_coe_h2 = fll_bit3_coe2 >> 15
        #
        #     temp_coe = [fll_bit3_coe_l, fll_bit3_coe_h, fll_bit3_frac, fll_bit3_coe_l2, fll_bit3_coe_h2, fll_bit3_frac2]
        #     coe.append(temp_coe)
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

    def fll_sum(self,fll_sum_bn, gps_car_norm_7):
        # length = len(fll_sum_bn)
        para_num = np.shape(fll_sum_bn)
        coe = []
        for i in range(0, para_num[0]):
            '''old para'''
            # fll_sum_coe = int(np.ceil(math.pi * gps_car_norm_7 * fll_sum_bn[i] * (2**10)))
            # fll_sum_frac = -10  # /1024
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
        # coe_size = np.shape(fll_sum_bn)
        # coe = []
        # for irow in range(0, coe_size[0]):

        # for i in range(0, coe_size[1]):
        #     '''old para'''
        #     # fll_sum_coe = int(np.ceil(math.pi * gps_car_norm_7 * fll_sum_bn[i] * (2**10)))
        #     # fll_sum_frac = -10  # /1024
        #
        #     '''new para'''
        #     coe0 = math.pi * gps_car_norm_7 * fll_sum_bn[1][i]
        #     lg_fac0 = int(np.log2((2.0 ** 23 - 1) / coe0))
        #     fll_sum_coe = int(np.ceil(coe0 * (2.0 ** lg_fac0)))
        #     fll_sum_frac = -lg_fac0
        #
        #     fll_sum_coe_l = fll_sum_coe & (2 ** 15 - 1)
        #     fll_sum_coe_h = fll_sum_coe >> 15
        #     temp_coe = [fll_sum_coe_l, fll_sum_coe_h, fll_sum_frac]
        #     coe.append(temp_coe)
        return coe

    def fll_3_sum(self, fll3_sum_bn, gps_car_norm_7):
        # fll_sum_ms = 2
        # coe_size = np.shape(fll3_sum_bn)
        # coe = []
        # for irow in range(0, coe_size[0]):
        #     if irow == 0:
        #         fll_sum_ms = 2
        #     elif irow == 1:
        #         fll_sum_ms = 4
        #     elif irow == 2:
        #         fll_sum_ms = 10
        # fll_sum_ms = 10
        # for i in range(0, coe_size[1]):
        #     '''old para'''
        #     # fll_sum3_coe = int(np.ceil(0.001 * fll_sum_ms * math.pi * gps_car_norm_7 * ((fll3_sum_bn[1][i]/0.53)**2) * (2**10)))
        #     # fll_sum3_coe2 = int(np.ceil(math.pi * gps_car_norm_7 * fll3_sum_bn[1][i] * 8/3.0 * (2**10)))
        #     # fll_sum3_frac = -10
        #     # fll_sum3_frac2 = -10
        #
        #     '''new para'''
        #     coe0 = 0.001 * fll_sum_ms * math.pi * gps_car_norm_7 * ((fll3_sum_bn[1][i]/0.53)**2)
        #     lg_fac0 = int(np.log2((2.0 ** 23 - 1) / coe0))
        #     fll_sum3_coe = int(np.ceil(coe0 * (2.0 ** lg_fac0)))
        #     fll_sum3_frac = -lg_fac0
        #     coe1 = math.pi * gps_car_norm_7 * fll3_sum_bn[1][i] * 8/3.0
        #     lg_fac1 = int(np.log2((2.0 ** 23 - 1) / coe1))
        #     fll_sum3_coe2 = int(np.ceil(coe1 * (2.0 ** lg_fac1)))
        #     fll_sum3_frac2 = -lg_fac1
        #
        #     fll_sum3_coe_l = fll_sum3_coe & (2**15 - 1)
        #     fll_sum3_coe_h = fll_sum3_coe >> 15
        #     fll_sum3_coe_l2 = fll_sum3_coe2 & (2**15 - 1)
        #     fll_sum3_coe_h2 = fll_sum3_coe2 >> 15
        #     temp_coe = [fll_sum3_coe_l, fll_sum3_coe_h, fll_sum3_frac, fll_sum3_coe_l2, fll_sum3_coe_h2, fll_sum3_frac2]
        #     coe.append(temp_coe)

        # length = len(fll3_sum_bn)
        para_num = np.shape(fll3_sum_bn)
        coe = []
        for i in range(0, para_num[0]):
            '''old para'''
            # fll_sum3_coe = int(np.ceil(0.001 * fll_sum_ms * math.pi * gps_car_norm_7 * ((fll3_sum_bn[0][i]/0.53)**2) * (2**10)))
            # fll_sum3_coe2 = int(np.ceil(math.pi * gps_car_norm_7 * fll3_sum_bn[0][i] * 8/3.0 * (2**10)))
            # fll_sum3_frac = -10
            # fll_sum3_frac2 = -10
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

    def pll(self,pll_bn, pll_long_bn, all_bn, gps_car_norm_7):
        # length = len(pll_bn)
        # coe_size = np.shape(pll_bn)
        coe = []
        # pll_sum_ms = 1
        # for irow in range(0, coe_size[0]):
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
            '''old para'''
            # pll_coe = int(np.ceil(0.001 * pll_sum_ms * math.pi * gps_car_norm_7 * ((pll_bn[i] / 0.53)**2) * (2**10)))
            # pll_frac = -10
            # pll_coe2 = int(np.ceil(math.pi * gps_car_norm_7 * (pll_bn[i] * 8 / 3.0) * (2**10)))
            # pll_frac2 = -10
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

        # all_sum_ms = 10
        # coe_size = np.shape(all_bn)
        # for irow in range(0, coe_size[0]):
        # length = len(all_bn)
        # for i in range(0, length):
        #     all_sum_ms = 2
        #     if i == 0:
        #         all_sum_ms = 2
        #     elif i == 1:
        #         all_sum_ms = 4
        #     elif i == 2:
        #         all_sum_ms = 10
        #     elif i == 3:
        #         all_sum_ms = 20
        #     elif i == 4:
        #         all_sum_ms = 100
        #     '''new para'''
        #     coe0 = 0.001 * all_sum_ms * math.pi * gps_car_norm_7 * ((all_bn[i] / 0.53) ** 2)
        #     lg_fac0 = int(np.log2((2.0 ** 23 - 1) / coe0))
        #     all_coe = int(np.ceil(coe0 * (2.0 ** lg_fac0)))
        #     all_frac = -lg_fac0
        #     coe1 = math.pi * gps_car_norm_7 * (all_bn[i] * 8 / 3.0)
        #     lg_fac1 = int(np.log2((2.0 ** 23 - 1) / coe1))
        #     all_coe2 = int(np.ceil(coe1 * (2.0 ** lg_fac1)))
        #     all_frac2 = -lg_fac1
        #
        #     all_coe_l = all_coe & (2 ** 15 - 1)
        #     all_coe_h = all_coe >> 15
        #     all_coe_l2 = all_coe2 & (2 ** 15 - 1)
        #     all_coe_h2 = all_coe2 >> 15
        #     temp_coe = [all_coe_l, all_coe_h, all_frac, all_coe_l2, all_coe_h2, all_frac2]
        #     coe.append(temp_coe)
        return coe

    def pll3(self, pll3_bn, gps_car_norm_7):
        # length = len(pll3_bn)
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
            # elif i == 5:
            #     pll_sum_ms = 60  # must >= 60
            '''old para'''
            # pll3_coe = int(np.ceil(0.001 * pll_sum_ms * math.pi * ((pll3_bn[0][i]/0.7845)**3) * (2**10)))
            # pll3_frac = -10
            # pll3_coe2 = int(np.ceil(0.001 * pll_sum_ms * math.pi * gps_car_norm_7 * 1.1 * ((pll3_bn[0][i]/0.7845)**2) * (2**10)))
            # pll3_frac2 = -10
            # pll3_coe3 = int(np.ceil(math.pi * gps_car_norm_7 * 2.4 * (pll3_bn[0][i]/0.7845) * (2**10)))
            # pll3_frac3 = -10
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

        # pll_sum_ms = 100
        # for i in range(0, coe_size[1]):
        #     '''old para'''
        #     # pll3_coe = int(np.ceil(0.001 * pll_sum_ms * math.pi * ((pll3_bn[1][i]/0.7845)**3) * (2**10)))
        #     # pll3_frac = -10
        #     # pll3_coe2 = int(np.ceil(0.001 * pll_sum_ms * math.pi * gps_car_norm_7 * 1.1 * ((pll3_bn[1][i]/0.7845)**2) * (2**10)))
        #     # pll3_frac2 = -10
        #     # pll3_coe3 = int(np.ceil(math.pi * gps_car_norm_7 * 2.4 * (pll3_bn[1][i]/0.7845) * (2**10)))
        #     # pll3_frac3 = -10
        #
        #     '''new para'''
        #     coe0 = 0.001 * pll_sum_ms * math.pi * ((pll3_bn[1][i]/0.7845)**3)
        #     lg_fac0 = int(np.log2((2.0 ** 23 - 1) / coe0))
        #     pll3_coe = int(np.ceil(coe0 * (2.0 ** lg_fac0)))
        #     pll3_frac = -lg_fac0
        #     coe1 = 0.001 * pll_sum_ms * math.pi * gps_car_norm_7 * 1.1 * ((pll3_bn[1][i]/0.7845)**2)
        #     lg_fac1 = int(np.log2((2.0 ** 23 - 1) / coe1))
        #     pll3_coe2 = int(np.ceil(coe1 * (2.0 ** lg_fac1)))
        #     pll3_frac2 = -lg_fac1
        #     coe3_0 = math.pi * gps_car_norm_7 * 2.4 * (pll3_bn[1][i]/0.7845)
        #     lg_fac3 = int(np.log2((2.0 ** 23 - 1) / coe3_0))
        #     pll3_coe3 = int(np.ceil(coe3_0 * (2.0 ** lg_fac3)))
        #     pll3_frac3 = -lg_fac3
        #
        #     pll3_coe_l = pll3_coe & (2 ** 15 - 1)
        #     pll3_coe_h = pll3_coe >> 15
        #     pll3_coe_l2 = pll3_coe2 & (2**15 - 1)
        #     pll3_coe_h2 = pll3_coe2 >> 15
        #     pll3_coe_l3 = pll3_coe3 & (2**15 - 1)
        #     pll3_coe_h3 = pll3_coe3 >> 15
        #     temp_coe = [pll3_coe_l, pll3_coe_h, pll3_frac, pll3_coe_l2, pll3_coe_h2, pll3_frac2, pll3_coe_l3, pll3_coe_h3, pll3_frac3]
        #     coe.append(temp_coe)
        return coe

    def cal(self,dll,pll,pll_long,pll3,fll,fll3,dll_bit,fll_bit,fll3_bit,all_bn='',mode=0,rank =control.high, cnf = [], gps_cn0_db=[], smooth_fac_factor=[]):
        if mode ==int(b'10',2):
            dll_bit = np.append(dll_bit,dll)
            # dll_m = self.dll_sum(dll, self.gps_code_norm)
            fll_m = self.fll_sum(fll, self.gps_car_norm1_7)
            pll_m = self.pll(pll, all_bn,self.gps_car_norm1_7)##todo
            dll_bit_m = self.dll_bit(dll_bit,self.gps_code_norm)#todo
            fll_bit_m = self.fll_bit(fll_bit,self.gps_car_norm1_7)
            para = [pll_m, fll_bit_m, fll_m,dll_bit_m]
            print('-*-*-', dll_bit, fll_m, pll_m, dll_bit_m, fll_bit_m, para, '-*-*-')
        elif mode==int(b'00',2):
            dll_m = self.dll_sum(dll, self.gps_code_norm)
            fll_m = self.fll_sum(fll, self.gps_car_norm1_7)
            fll3_m = self.fll_3_sum(fll3, self.gps_car_norm1_7)##todo
            pll_m = self.pll(pll, pll_long, all_bn,self.gps_car_norm1_7)##todo
            pll3_m = self.pll3(pll3, self.gps_car_norm1_7)##todo
            dll_bit_m = self.dll_bit(dll_bit,self.gps_code_norm)#todo
            fll_bit_m = self.fll_bit(fll_bit,self.gps_car_norm1_7)
            fll3_bit_m = self.fll_bit_3(fll3_bit,self.gps_car_norm1_7)
            para = [pll_m,pll3_m,fll_bit_m,fll_m,fll3_bit_m,fll3_m,dll_bit_m,dll_m]
            print('-*-*-', dll_m, fll_m, fll3_m, pll_m, pll3_m, dll_bit_m, fll_bit_m, fll3_bit_m, para, '-*-*-')
        new_para=list(flat(para))
        # print(new_para)
        result=self.hex_to_dec(new_para,rank, cnf, gps_cn0_db, smooth_fac_factor)

        return result
    # def caljson(self,dict):
    #     dll_m = self.dll_sum(dll, self.gps_code_norm)
    #     fll_m = self.fll_sum(fll, self.gps_car_norm1_7)
    #     pll_m = self.pll(pll, self.gps_car_norm1_7)##todo
    #     dll_bit_m = self.dll_bit(dll_bit,self.gps_code_norm)#todo
    #     fll_bit_m = self.fll_bit(fll_bit,self.gps_car_norm1_7)
    #
    #     # para = [dll_m,fll_m,pll_m,,fll_bit_m]
    #     para = [dll_bit_m,dll_m,pll_m,fll_bit_m,fll_m]
    #     # print(para)
    #     new_para=list(flat(para))
    #     print(new_para)
    #     result=self.hex_to_dec(new_para)
    #     return result

    def hex_to_dec(self,data,mode, cnf, gps_cn0_db=[], smooth_fac_factor=[]):
        #cnf = [0x0A, 0x32, 0x19, 0x0C, 0x23, 0x1E, 0x19, 0x14]
        smooth_fac_shift0 = smooth_fac_factor[0]
        smooth_fac_shift1 = smooth_fac_factor[1]
        fli_smooth_factor = smooth_fac_factor[2]
        # fli_smooth_par = np.array([np.ceil(fli_smooth_factor * (2.0 ** smooth_fac_shift0)),
        #                            np.ceil((1 - fli_smooth_factor) * (2.0 ** smooth_fac_shift1))], dtype=int)
        fli_smooth_par = np.floor(fli_smooth_factor * (2.0 ** smooth_fac_shift0) + 0.5).astype(int)
        f_parameter = [fli_smooth_par[0] & 0xff, fli_smooth_par[0] >> 8, fli_smooth_par[1] & 0xff, fli_smooth_par[1] >> 8]
        pli_smooth_factor = smooth_fac_factor[3]
        # pli_smooth_par = np.array([np.ceil(pli_smooth_factor * (2.0 ** smooth_fac_shift0)),
        #                            np.ceil((1 - pli_smooth_factor) * (2.0 ** smooth_fac_shift1))], dtype=int)
        pli_smooth_par = np.floor(pli_smooth_factor * (2.0 ** smooth_fac_shift1) + 0.5).astype(int)
        p_parameter = [pli_smooth_par[0] & 0xff, pli_smooth_par[0] >> 8, pli_smooth_par[1] & 0xff, pli_smooth_par[1] >> 8]

        send_data = [0xaa ,0xaa]
        lenth = len(data)
        bit_32 = 3*np.arange(1,100) -1##96/3  =32    3*11(50) 给足够长

        # fl_cn0_nwr = np.array([6.0, 11.0, 15.0, 15.0])
        # nwr_fl_clns = np.floor(32 * np.log2(((fl_cn0_nwr - 1.0)/(20.0 - fl_cn0_nwr))) * (2**16)).astype(int)

        gps_cn0_th = (np.floor((gps_cn0_db/10 - 3) * (2**(5 + smooth_fac_shift1))/np.log10(2) + 0.5)).astype(int)
        # gps_cn0_th = nwr_fl_clns.tolist()
        i = 0
        for num in gps_cn0_th:
            if num < 0:
                gps_cn0_th[i] = num + 2**32
            i += 1
        hex_8bit = []
        for num in gps_cn0_th:
            hex_8bit.append(num & 0xff)
            hex_8bit.append((num >> 8) & 0xff)
            hex_8bit.append((num >> 16) & 0xff)
            hex_8bit.append((num >> 24) & 0xff)


        menxian = [0x0, mode] + hex_8bit + p_parameter + f_parameter + cnf
        if mode ==control.high:
            pass
            #menxian =[0x0, mode] + p_parameter + f_parameter + cnf
        elif mode==control.mid:
            pass
            #menxian =[0x0, mode, 0xAF, 0x07, 0xE2, 0x03, 0x9A, 0x19, 0x9A, 0x03, 0x0F, 0x64, 0x32, 0x10, 0x23, 0x1E, 0x19, 0x19]
        elif mode==control.low:
            pass
            #menxian = [0x0, mode, 0xAF, 0x07, 0xE2, 0x03, 0x9A, 0x19, 0x9A, 0x03, 0x0F, 0x64, 0x32, 0x10, 0x23, 0x1E, 0x19, 0x19]
        send_data.extend(menxian)
        for i in range(lenth):
            if i not in bit_32:
                data_H = int((data[i]&0xff00)/256)
                data_L = int(data[i]&0x00ff)
                send_data.append(data_L)  #低位在前高位在后
                send_data.append(data_H)
            else:
                data4 = int((data[i]&0xff000000)/2**24)
                data3 = int((data[i]&0x00ff0000)/2**16)
                data2 = int((data[i]&0x0000ff00)/2**8)
                data1 = int((data[i]&0x000000ff))
                send_data.append(data1) #
                send_data.append(data2)
                send_data.append(data3)
                send_data.append(data4)
        send_data.extend([0xbb,0xbb])  ##add the choose
        lenth = len(send_data) -4
        print("the lenth is ",lenth)
        len_H = int((lenth & 0xff00) / 256)
        len_L = int(lenth & 0x00ff)
        send_data.insert(2,len_L)
        send_data.insert(3,len_H)
        print([hex(i) for i in send_data])
        hex_data=[hex(i) for i in send_data]
        hex_out(hex_data)
        return send_data
def str_tohex(str):
    getstr =[]
    for sub in str.split(' '):
        getstr.append(hex(int(sub,16)))
    return getstr
def hex_out(hex_data):
    for i, x in enumerate(hex_data):
        if (len(x) == 3):
            hex_data[i] = "0x0" + x[2:3].upper()
        elif(len(x)==4):
            hex_data[i] ="0x" +x[2:4].upper()
    st_da = str(hex_data)
    newdata=re.sub('[\[\]\']', '', st_da)
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

def cal_para(dll,pll,fll,dll_bit,fll_bit):
    A = para_convert()
    dll_m = A.dll_sum(dll, A.gps_code_norm)
    fll_m = A.fll_sum(fll, A.gps_car_norm1_7)
    pll_m = A.pll(pll, A.gps_car_norm1_7)
    dll_bit_m = A.dll_bit(dll_bit,A.gps_code_norm)
    fll_bit_m = A.fll_bit(fll_bit,A.gps_car_norm1_7)
    para = [dll_m,fll_m,pll_m,dll_bit_m,fll_bit_m]
    # print(para)
    new_para=list(flat(para))
    print(new_para)
    result=A.hex_to_dec(new_para)
    return result

A =6378137.0 # 地球长半轴[m]
GPS_EARTH_B =6356752.31424517950
WGS84_E2 =0.0066943799901413169961372335400448 # 地球偏心率的平方
DBL_EPSILON  =   2.2204460492503131e-016
HALFPI = 1
USR_EPSILON =1.0e-06
GPS_ECC_2 =0.00669437999014132
# longitude_norm = -3.59723
# latitude_norm = 50.42336
# height_norm = 0
"""
dLat ：纬度  #转化为幅度
dLon ：经度  #转化为幅度
dAlt ：高层
"""
"""
dLat ：纬度  #转化为幅度
dLon ：经度  #转化为幅度
dAlt ：高层
dx,dy,dz
"""
def  Llh2Xyz(dLat,dLon,dAlt,iswidth=False):
    """
    :param dLat:
    :param dLon:
    :param dAlt:
    :param mode:  False: angle
                 True: width
    :return:
    """
    e2 = WGS84_E2
    if iswidth==False:
        dLat= dLat*math.pi/180
        dLon= dLon*math.pi/180

    dSinlat = np.sin(dLat)
    dCoslat = np.cos(dLat)
    n = A / np.sqrt(1 - e2 * dSinlat * dSinlat)
    dX = (n + dAlt) * dCoslat * np.cos(dLon)
    dY = (n + dAlt) * dCoslat * np.sin(dLon)
    dZ = (n * (1 - e2) + dAlt) * dSinlat
    return np.array([dX,dY,dZ])

def XyzToLla(x=0,y=0,z=0): ##ndim
    sCnt = 0
    dLat =0.0
    if isinstance(x,np.ndarray):
        alldr = np.sqrt(x[:,0]** 2 + x[:,1]** 2)
        dLon,falt,dLat = np.zeros_like(alldr),np.zeros_like(alldr),np.zeros_like(alldr)
        for i,dr in enumerate(alldr):
            if dr < DBL_EPSILON:
                dLon[i] = 0.0
                if x[i,0]< DBL_EPSILON:
                    falt[i] = -x[i,2]- GPS_EARTH_B
                    dLat[i] = -(math.pi / 2)
                else:
                    falt[i] = x[:,2] - GPS_EARTH_B
                    dLat[i] = math.pi / 2
            else:
                dLatTmp = dLat[i]
                dSinLat = np.sin(dLatTmp)
                dTmp = GPS_ECC_2 * dSinLat
                dN = A / np.sqrt(1 - dTmp * dSinLat)
                dLat[i] = np.arctan((x[i, 2] + dN * dTmp) / dr)
                dErr = dLat[i] - dLatTmp
                sCnt += 1
                while (dErr > USR_EPSILON or dErr < -USR_EPSILON and sCnt < 10):
                    dLatTmp = dLat[i]
                    dSinLat = np.sin(dLatTmp)
                    dTmp = GPS_ECC_2 * dSinLat
                    # dN = A / math.sqrt(1 - dTmp * dSinLat)
                    dN = A / np.sqrt(1 - dTmp * dSinLat)
                    # dLat = math.atan((x[:,2] + dN * dTmp) / dr)
                    dLat[i] = np.arctan((x[i,2] + dN * dTmp) / dr)
                    dErr = dLat[i] - dLatTmp
                    sCnt += 1
                # dLon = math.atan2(x[:,1], x[:,0])
                dLon[i] = np.arctan2(x[i, 1], x[i, 0])
                dLat[i] = dLat[i]
                falt[i] = dr / np.cos(dLat[i]) - dN
    else:
        dr =math.sqrt(x**2+y**2)
        if dr <DBL_EPSILON:
            dLon = 0.0
            if z <DBL_EPSILON:
                falt = -z - GPS_EARTH_B
                dLat = -(math.pi/2)
            else:
                falt = z - GPS_EARTH_B
                dLat =math.pi/2
        else:
            dLatTmp = dLat
            dSinLat = math.sin(dLatTmp)
            dTmp = GPS_ECC_2 * dSinLat
            dN = A / math.sqrt(1 - dTmp * dSinLat)
            dLat = math.atan((z + dN * dTmp) / dr)
            dErr = dLat - dLatTmp
            sCnt += 1
            while(dErr>USR_EPSILON or dErr <-USR_EPSILON and sCnt <10):
                dLatTmp =dLat
                dSinLat = math.sin(dLatTmp)
                dTmp = GPS_ECC_2 *dSinLat
                dN = A/math.sqrt(1-dTmp*dSinLat)
                dLat =math.atan((z+dN*dTmp)/dr)
                dErr =dLat -dLatTmp
                sCnt +=1
            dLon =math.atan2(y,x)
            dLat =dLat
            falt =dr/math.cos(dLat) -dN
    return [dLat,dLon,falt]

def xyztoenu(jwd,speed,id=[]):
    e2 = WGS84_E2
    dLat, dLon, dAlt =jwd[0],jwd[1],jwd[2]
    vx,vy,vz= speed[:, 0],speed[:, 1],speed[:, 2]

    # dLat= dLat*np.pi/180
    # dLon= dLon*np.pi/180

    dSinlat = np.sin(dLat)
    dCoslat = np.cos(dLat)
    dSinlon = np.sin(dLon)
    dCoslon = np.cos(dLon)

    n = A / np.sqrt(1 - e2 * dSinlat * dSinlat)

    # dX = (n + dAlt) * dCoslat * np.cos(dLon)
    # dY = (n + dAlt) * dCoslat * np.sin(dLon)
    # dZ = (n * (1 - e2) + dAlt) * dSinlat

    fEst = -vx*dSinlon +vy*dCoslon
    fNrt =-vx*dCoslon*dSinlat -vy*dSinlon*dSinlat +vz*dCoslat
    V = np.sqrt(fEst**2 +fNrt**2)
    # if id !=[]:
    #     V=np.vstack((id,V))
    # return np.array(dX,dY,dZ),V
    return V
def fileToNumpy(filename,sortid=8):
    file = open(filename)
    file_lines = file.readlines()
    numberOfLines = len(file_lines) -1
    dataArray = np.zeros((numberOfLines, sortid))
    # labels = []
    index = 0
    for i,line in enumerate(file_lines):
        if i ==0:
            continue
        line = line.strip() # 参数为空时，默认删除开头、结尾处空白符（包括'\n', '\r',  '\t',  ' ')
        formLine = line.split('\t')
        dataArray[index,:] = formLine[0:sortid]
        # labels.append((formLine[-1]))
        index += 1
    speed_array = dataArray[:,5::]
    id_array  =(dataArray[:,1:2]-dataArray[0,1:2])[:,0]
    xyz_array = dataArray[:,2:5]
    result_dic = {
        "id":id_array,
        "speed":speed_array,
        "xyz":xyz_array
    }
    return result_dic



# filename = "D:/2019-12-18/car_acc_trk_1g.RSIM(T1)GnssTrj(20191218-1057).dat.TXT"
# result_dic = fileToNumpy(filename)
# jwd=XyzToLla(result_dic["xyz"])
# # Llh2Xyz(jwd[])
# xyztoenu(jwd,result_dic['speed'],id=result_dic['id'])
# if __name__ == '__main__':
#         mode = 0
#         rank = control.high
#         # dll_bn = np.array([2.0,1.0,0.4,2.0,1.2,1.0,0.5,0.3,0.1,0.02,0.01])
#         # dll_sum_bn = np.array([2.0,1.2,1.0,2.0,1.2,1.0,0.02,0.01])
#         # fll_bn  = np.array([1.5,1.5,0.6])
#         # fll_sum_bn = np.array([[20.0, 10.0, 8.0], [16.0, 6.0, 4.0], [12.0, 3.5, 2.0]])  # 2ms, 4ms, 10ms
#         #
#         # pll_bn = np.array([[20.0, 8.0, 6.0] , [15.0, 6.0, 5.0], [10.0, 4.0, 4.0],
#         #                    [4.0, 3.5, 3.0], [2.0, 2.0, 2.0], [1.0, 0.6, 0.4]])  # 1ms, 2ms, 4ms, 10ms, 20ms, 100ms
#         # all_bn = np.array([1.0,0.6,0.5,0.4,0.3])# 2ms, 4ms, 10ms, 20ms, 100ms
#         A = para_convert()
# ###high
#         dll_bn = np.array([2.0])
#         dll_sum_bn = np.array([2.0, 0.5, 0.02, 0.01])
#         fll_bn = np.array([1.5])
#         fll_sum_bn = np.array([[20], [16], [12.0]])
#         pll_bn = np.array([[10], [6], [4], [2.0], [1.0], [1]])
#         all_bn = []
#         limit_cfg = [8, 50, 25, 12, 35, 22, 15, 12]
#         print("the high state:")
#         result = A.cal(dll_sum_bn, pll_bn, fll_sum_bn, dll_bn, fll_bn, all_bn, mode, rank, limit_cfg)
#
# ###mid
#         mode = 0
#         rank = control.mid
#         dll_bn = np.array([1.0])
#         dll_sum_bn = np.array([1.2, 0.3, 0.02, 0.01])
#         fll_bn = np.array([1.5])
#         fll_sum_bn = np.array([[10], [6], [3.5]])
#         pll_bn = np.array([[8], [6], [4], [3.5], [2], [0.6]])
#         all_bn = []
#         limit_cfg = [12, 100, 50, 16, 35, 30, 25, 18]
#         print("the middle state:")
#         result = A.cal(dll_sum_bn, pll_bn, fll_sum_bn, dll_bn, fll_bn, all_bn, mode, rank, limit_cfg)
#
# ###low
#         mode = 0
#         rank = control.low
#         dll_bn = np.array([0.4])
#         dll_sum_bn = np.array([1.0, 0.1, 0.02, 0.01])
#         fll_bn = np.array([0.6])
#         fll_sum_bn = np.array([[8], [4], [2.0]])
#         pll_bn = np.array([[6], [5], [4], [3], [1.5], [0.4]])
#         all_bn = []
#         limit_cfg = [12, 100, 50, 16, 35, 30, 25, 18]
#         print("the low state:")
#         result = A.cal(dll_sum_bn, pll_bn, fll_sum_bn, dll_bn, fll_bn, all_bn, mode, rank, limit_cfg)
#
#         # data = {"fll_2": 7.573589424255466, "dll1": 0.7209415625849652, "fll_bit": 2.2019919183998953,
#         #  "pll_3": 7.377932579656648, "pll_2": 9.231968331200513, "fll": 13.687896404735579, "pll_1": 11.848610966939232,
#         #  "fll_1": 7.021750488014408, "dll": 2.1373946981326593, "pll": 35.68908386923844, "dll_bit": 0.7025611528814057}
#
#
#         print(result)

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
    pll_long_bn = np.array([1.5, 1.0, 0.8, 0.8, 0.7])
    smooth_fac_shift0 = 16
    smooth_fac_shift1 = 10
    fli_smooth_factor = np.array([0.1, 0.3])
    pli_smooth_factor = np.array([0.04, 0.02])
    #gps_cn0_db = np.array([33.0, 29.8, 27.3, 25.0, 22.5, 20.0, 18.5, 17.0, 39.0, 39.0])
    # gps_cn0_db = np.array([33.0, 29.8, 27.3, 25.0, 22.5, 20.0, 18.5, 17.0, 39.0, 00.0]) # disable
    gps_cn0_db = np.array([33.0, 29.8, 27.3, 25.0, 22.5, 20.0, 18.5, 17.0, 39.0, 39.0])  # enable
    # gps_cn0_db = np.array([35.0, 31.0, 28.3, 26.0, 23.5, 21.0, 19.0, 17.0, 39.0, 35.0])
    narrow_dll_bn = 1.0

    smooth_fac_factor = list()
    smooth_fac_factor.append(16)
    smooth_fac_factor.append(18)
    smooth_fac_factor.append(fli_smooth_factor)
    smooth_fac_factor.append(pli_smooth_factor)

    ###high
    dll_bn = np.array([2.0])
    dll_sum_bn = np.array([2.0, 1.0,  # 1.0 # 0.5~1.0
                           narrow_dll_bn, 0.05, 0.03, 0.02, 0.02, 0.01])  # narrow, 2*20, 5*20, 10*20, 15*20, 30*20

    fll_bn = np.array([1.5])
    fll_sum_bn = np.array([[20], [16], [12.0]])
    pll_bn = np.array([[16], [14], [10], [6.0], [2.0]])
    fll3_bn = np.array([3.0])
    fll3_sum_bn = np.array([[20], [16], [12.0]])
    pll3_bn = np.array([[28], [22], [18], [12], [6.0]])

    all_bn = []
    #limit_cfg = [8, 50, 25, 12, 35, 22, 15, 12]
    limit_cfg = [8, 50, 25, 12, 35, 25, 16, 13]
    print("the high state:")
    result = A.cal(dll_sum_bn, pll_bn, pll_long_bn, pll3_bn, fll_sum_bn, fll3_sum_bn, dll_bn, fll_bn, fll3_bn, all_bn, mode, rank, limit_cfg, gps_cn0_db, smooth_fac_factor)

    ###mid
    mode = 0
    rank = control.mid
    dll_bn = np.array([1.0])
    dll_sum_bn = np.array([1.2, 0.6,  # 0.6, 0.3, 0.15, 0.1
                           narrow_dll_bn, 0.05, 0.03, 0.02, 0.02, 0.01])
    fll_bn = np.array([1.5])
    fll_sum_bn = np.array([[10], [6], [3.5]])
    # pll_bn = np.array([[10], [8], [6], [4.0], [1.5]])
    pll_bn = np.array([[10], [8], [5.0], [3.0], [1.5]])
    fll3_bn = np.array([1.5])
    fll3_sum_bn = np.array([[16], [12], [6.0]])
    pll3_bn = np.array([[12], [8], [6], [5], [3]])
    all_bn = []
    # limit_cfg = [12, 100, 50, 16, 35, 22, 17, 12]
    limit_cfg = [12, 100, 50, 16, 35, 25, 16, 15]
    print("the middle state:")
    result = A.cal(dll_sum_bn, pll_bn, pll_long_bn, pll3_bn, fll_sum_bn,fll3_sum_bn, dll_bn, fll_bn, fll3_bn, all_bn, mode, rank, limit_cfg, gps_cn0_db, smooth_fac_factor)

    ###low
    mode = 0
    rank = control.low
    dll_bn = np.array([0.4])
    # dll_sum_bn = np.array([1.0, 0.2,
    #                        narrow_dll_bn, 0.05, 0.03, 0.02, 0.02, 0.01])
    dll_sum_bn = np.array([1.0, 0.4,
                           narrow_dll_bn, 0.05, 0.03, 0.02, 0.02, 0.01])
    fll_bn = np.array([0.6])
    fll_sum_bn = np.array([[8], [4], [2.0]])
    # pll_bn = np.array([[8], [6], [4], [3.0], [1.5]])
    pll_bn = np.array([[8], [6], [4], [3.0], [1.0]])
    fll3_bn = np.array([1.0])
    fll3_sum_bn = np.array([[12], [8], [4.0]])
    pll3_bn = np.array([[10], [4], [4], [3], [2.0]])
    all_bn = []
    # limit_cfg = [12, 100, 50, 16, 35, 22, 17, 12]
    limit_cfg = [12, 100, 50, 16, 36, 32, 23, 17]
    print("the low state:")
    result = A.cal(dll_sum_bn, pll_bn, pll_long_bn, pll3_bn, fll_sum_bn,fll3_sum_bn, dll_bn, fll_bn, fll3_bn, all_bn, mode, rank, limit_cfg, gps_cn0_db, smooth_fac_factor)

    # data = {"fll_2": 7.573589424255466, "dll1": 0.7209415625849652, "fll_bit": 2.2019919183998953,
    #  "pll_3": 7.377932579656648, "pll_2": 9.231968331200513, "fll": 13.687896404735579, "pll_1": 11.848610966939232,
    #  "fll_1": 7.021750488014408, "dll": 2.1373946981326593, "pll": 35.68908386923844, "dll_bit": 0.7025611528814057}

    print(result)



