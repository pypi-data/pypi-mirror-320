#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Author        : yuzijian
# @Email         : yuzijian1010@163.com
# @FileName      : run_interproscan_2.py
# @Time          : 2025-01-02 16:22:41
# @description   : 对序列文件进行去重，然后将去重之后的文件，拆分成多个序列
"""
import os
import time
import glob
import shutil
import subprocess
from Bio import SeqIO
from Bio.Seq import Seq
import concurrent.futures


# 1. 使用 Biopython 读取 FASTA 文件，去除重复的基因ID，并将唯一的基因ID及其序列写入新文件。
def deduplicate_fasta(input_file, output_file):
    id_counts = {}
    for record in SeqIO.parse(input_file, "fasta"):
        gene_id = record.id
        if gene_id in id_counts:
            id_counts[gene_id] += 1
        else:
            id_counts[gene_id] = 1

    unique_records = []
    translation_table = str.maketrans("", "", "*._")
    for record in SeqIO.parse(input_file, "fasta"):
        gene_id = record.id
        if id_counts[gene_id] == 1:
            # 将序列转换为字符串，移除“.”和“*”
            cleaned_seq_str = str(record.seq).translate(translation_table)
            # 将清洗后的字符串转换回 Seq 对象
            cleaned_seq = Seq(cleaned_seq_str)
            # 更新记录的序列
            record.seq = cleaned_seq
            unique_records.append(record)
    with open(output_file, "w") as fp:
        SeqIO.write(unique_records, fp, "fasta")
    print(f"去重后的序列已成功写入 {output_file}")


# 2. 将 FASTA 文件拆分成多个文件，每个文件包含大致相同数量的序列。
def split_fasta(input_file, output_dir, number_of_splits):
    records = list(SeqIO.parse(input_file, "fasta"))
    total_records = len(records)
    print(f"总共需要拆分的序列数量: {total_records}")

    records_per_split = total_records // number_of_splits
    remainder = total_records % number_of_splits
    print(f"每个文件大致包含 {records_per_split} 条序列，剩余 {remainder} 条序列将分配到前 {remainder} 个文件中。")

    start_index = 0
    for i in range(1, number_of_splits + 1):
        end_index = start_index + records_per_split + (1 if i <= remainder else 0)
        split_records = records[start_index:end_index]
        split_file = os.path.join(output_dir, f"All_{i}.fasta")
        SeqIO.write(split_records, split_file, "fasta")
        print(f"已创建文件: {split_file}，包含 {len(split_records)} 条序列。")
        start_index = end_index
    print(f"所有序列已成功拆分到 {output_dir} 文件夹中。")


# 3. 批量调用 interproscan 软件
def run_interproscan(input_file, CPU):
    cmd = ["interproscan.sh", "-i", input_file, "-b", "output_interproscan_result/", "-goterms", "-iprlookup", "-pa", "-dp", "-f", "tsv", "-cpu", str(CPU)]
    print("Running command: ", " ".join(cmd))
    subprocess.run(cmd)


# if __name__ == "__main__":
#     start_time = time.time()

#     input_fasta = "genome_s.fasta"     # 改- 输入需要去重的文件名字
#     output_fasta = "unique.fasta" # 改 - 输出的去重之后的结果文件名字
#     number_of_splits = 100  # 改 - 拆分的文件个数
#     process_interpro = 1  # 改 - 设置的进程数
#     thread_interpro = 10  # 改 - 每个进程占用的线程数

#     output_disassemble = "output_disassemble"  # 改 - 拆分的文件夹
#     output_interproscan_result = "output_interproscan_result"  # 改 - interproscan 鉴定的结果文件夹
#     shutil.rmtree(output_disassemble, ignore_errors=True)
#     os.makedirs(output_disassemble)
#     shutil.rmtree(output_interproscan_result, ignore_errors=True)
#     os.makedirs(output_interproscan_result)

#     # 1. 使用 Biopython 读取 FASTA 文件，去除重复的基因ID，并将唯一的基因ID及其序列写入新文件。
#     deduplicate_fasta(input_fasta, output_fasta)
#     # 2. 将 FASTA 文件拆分成多个文件，每个文件包含大致相同数量的序列。
#     split_fasta(output_fasta, output_disassemble, number_of_splits)

#     # 3. 批量调用 interproscan 软件
#     pep_file = glob.glob(f"{output_disassemble}/*.fasta")  # （可改） - 文件的路径和文件后缀
#     with concurrent.futures.ProcessPoolExecutor(max_workers=process_interpro) as executor:  # 改 - 线程池最大线程数
#         for file in pep_file:
#             executor.submit(run_interproscan, file, thread_interpro)  # 改 - 运行单个文件所占的CPU
#     end_time = time.time()
#     print(f"Time taken: {end_time - start_time} seconds")

