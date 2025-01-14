#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Author        : yuzijian
# @Email         : yuzijian1010@163.com
# @FileName      : run_mcscanx_V4.py
# @Time          : 2025-01-04 11:44:21
# @description   : 调用McScanX v1.0.0 版本，实现鉴定共线性的功能
"""
import os
import time
import glob
import shutil
import itertools
import subprocess
import pandas as pd
import concurrent.futures


class MCScanX:
    def __init__(self, blastp_path, gff_path, match_score=50, gap_penalty=-1, match_size=5, e_value=1e-05, max_gaps=25, overlap_window=5, build_blocks_only=False, block_pattern=0, synvisio=False):
        self.blastp_path = blastp_path
        self.gff_path = gff_path
        self.gff_files = glob.glob(os.path.join(gff_path, "*.gff"))
        self.name = self.get_name()
        self.match_score = match_score
        self.gap_penalty = gap_penalty
        self.match_size = match_size
        self.e_value = e_value
        self.max_gaps = max_gaps
        self.overlap_window = overlap_window
        self.build_blocks_only = build_blocks_only
        self.block_pattern = block_pattern
        self.synvisio = synvisio

    def get_name(self):
        sp_name = []
        for line in self.gff_files:
            sp_name.append(os.path.basename(line).split('.')[0])
        new = list(itertools.permutations(sp_name, 2))
        return new

    def deal_blast(self, one, two):
        cat_command = f"cat {os.path.join(self.blastp_path, f'{one}_{one}.blast')} {os.path.join(self.blastp_path, f'{one}_{two}.blast')} {os.path.join(self.blastp_path, f'{two}_{two}.blast')} {os.path.join(self.blastp_path, f'{two}_{one}.blast')} > output_gff_blast/{one}_{two}.blast"
        subprocess.run(cat_command, shell=True)
        print(f"Blast file for {one}_{two} cat finish!!!")

    def deal_gff(self, one, two):
        sp_brr_one = one
        sp_brr_two = two
        # 处理 one 的 gff 文件
        df_one = pd.read_csv(os.path.join(self.gff_path, f"{sp_brr_one}.new.gff"), sep='\t', header=None)
        df_one = df_one.iloc[:, [0, 5, 1, 2]]
        df_one[0] = sp_brr_one + df_one[0].astype(str)
        df_one.to_csv(f"output_gff_blast/{sp_brr_one}.gff", sep='\t', header=None, index=None)
        print(f"gff file {one}.gff deal 4 col finish!")
        # 处理 two 的 gff 文件
        df_two = pd.read_csv(os.path.join(self.gff_path, f"{sp_brr_two}.new.gff"), sep='\t', header=None)
        df_two = df_two.iloc[:, [0, 5, 1, 2]]
        df_two[0] = sp_brr_two + df_two[0].astype(str)
        df_two.to_csv(f"output_gff_blast/{sp_brr_two}.gff", sep='\t', header=None, index=None)
        print(f"gff file {two}.gff deal 4 col finish!")

        gff_one = pd.read_csv(f"output_gff_blast/{one}.gff", sep='\t', header=None)
        gff_two = pd.read_csv(f"output_gff_blast/{two}.gff", sep='\t', header=None)
        new_gff = pd.concat([gff_one, gff_two], ignore_index=True)
        new_gff.to_csv(f"output_gff_blast/{one}_{two}.gff", sep='\t', header=None, index=None)
        print(f"gff files {one}_{two}.gff deal MCScanX finish!")

    def run_mcscanx(self, one, two):
        print(one, two)
        self.deal_gff(one, two)
        self.deal_blast(one, two)

        shutil.copy(f"output_gff_blast/{one}_{two}.gff", ".")
        shutil.copy(f"output_gff_blast/{one}_{two}.blast", ".")
        
        # 构建 MCScanX 命令
        mcscanx_command = f"MCScanX -k {self.match_score} -g {self.gap_penalty} -s {self.match_size} -e {self.e_value} -m {self.max_gaps} -w {self.overlap_window}"
        if self.build_blocks_only:
            mcscanx_command += " -a"
        if self.block_pattern in [0, 1, 2]:
            mcscanx_command += f" -b {self.block_pattern}"
        mcscanx_command += f" {one}_{two}"
        
        subprocess.run(mcscanx_command, shell=True)

        # 如果 synvisio 参数为 True，则处理 synvisio 相关文件
        if self.synvisio:
            shutil.copy(f"{one}_{two}.collinearity", "output_synvisio")
            shutil.move(f"output_synvisio/{one}_{two}.collinearity", f"output_synvisio/{one}_{two}_collinear.collinearity")
            shutil.copy(f"{one}_{two}.gff", "output_synvisio")
            shutil.move(f"output_synvisio/{one}_{two}.gff", f"output_synvisio/{one}_{two}_coordinate.gff")

        shutil.move(f"{one}_{two}.tandem", "output_mcacanx_result")
        shutil.move(f"{one}_{two}.collinearity", "output_mcacanx_result")
        # shutil.move(f"{one}_{two}.html", "output_mcacanx_result")
        shutil.rmtree(f"{one}_{two}.html")

        os.remove(f"{one}_{two}.gff")
        os.remove(f"{one}_{two}.blast")
        os.remove(f"output_gff_blast/{one}_{two}.gff")
        os.remove(f"output_gff_blast/{one}_{two}.blast")


# if __name__ == '__main__':
#     input_blast = "input_blast"  # 改 - blastp 文件路径的输入文件夹
#     input_gff = "input_gff"  # 改 - gff 文件路径的输入文件夹
#     start_time = time.time()

#     # 清理并重新创建输出目录
#     for output_dir in ["output_mcacanx_result", "output_gff_blast"]:
#         shutil.rmtree(output_dir, ignore_errors=True)
#         os.makedirs(output_dir)

#     # 用户自定义 MCScanX 参数
#     match_score = 50  #  匹配得分，最终得分 = MATCH_SCORE + NUM_GAPS * GAP_PENALTY
#     gap_penalty = -1  # 间隙惩罚，即每出现一个间隙时的惩罚分数
#     match_size = 5  # 定义一个共线性区块所需的最小基因数量
#     e_value = 1e-05  # BLAST比对结果的显著性阈值
#     max_gaps = 25  # 允许的最大间隙数量
#     overlap_window = 5  # 用于合并BLAST匹配结果的最大距离（以基因数量计）
#     build_blocks_only = False  # 仅构建成对的共线性区块
#     block_pattern = 0  # 0-种内和种间；1-种内；2-种间
#     synvisio = False  # 改 - 是否启用 synvisio 文件处理
#     max_workers = 10  # 改 - 并发进程数

#     # 如果 synvisio 参数为 True，则创建 output_synvisio 文件夹
#     if synvisio:
#         shutil.rmtree("output_synvisio", ignore_errors=True)
#         os.makedirs("output_synvisio")

#     mc = MCScanX(input_blast, input_gff, match_score, gap_penalty, match_size, e_value, max_gaps, overlap_window, build_blocks_only, block_pattern, synvisio)
#     with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
#         futures = [executor.submit(mc.run_mcscanx, one, two) for one, two in mc.name]
#         concurrent.futures.wait(futures)
#     end_time = time.time()
#     print(f"Total running time: {end_time - start_time} seconds")

