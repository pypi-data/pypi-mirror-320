#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Author        : yuzijian
# @Email         : yuzijian1010@163.com
# @FileName      : orthogroups_identity.py
# @Time          : 2025-01-01 23:47:29
# @description   :
"""
import glob
import sqlite3
import numpy as np
import pandas as pd
from collections import defaultdict
from scipy.sparse import lil_matrix, csr_matrix


# 1. 将 BLAST 结果存储到 SQLite 数据库
def store_blast_results(blast_file, db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS blast_results (
                        seq1 TEXT,
                        seq2 TEXT,
                        score REAL
                    )''')

    with open(blast_file, 'r') as f:
        for line in f:
            seq1, seq2, score = line.strip().split("\t")[0], line.strip().split("\t")[1], float(line.strip().split("\t")[11])
            cursor.execute('INSERT INTO blast_results (seq1, seq2, score) VALUES (?, ?, ?)', (seq1, seq2, score))
    
    conn.commit()
    conn.close()


# 2. 从 SQLite 数据库查询相似性得分并构建稀疏相似性矩阵
def build_similarity_matrix_from_db(db_file, sequences, threshold=1e-5):
    n = len(sequences)
    similarity_matrix = lil_matrix((n, n), dtype=np.float64)
    seq_to_index = {seq: i for i, seq in enumerate(sequences)}
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    for seq1, seq2, score in cursor.execute('SELECT seq1, seq2, score FROM blast_results'):
        if score > threshold:  # 只保留高于阈值的相似性得分
            i, j = seq_to_index.get(seq1), seq_to_index.get(seq2)
            if i is not None and j is not None:
                similarity_matrix[i, j] = score
                similarity_matrix[j, i] = score  # 对称矩阵
    
    conn.close()
    return similarity_matrix


# 归一化矩阵，使每列的和为1
def normalize_matrix(matrix):
    return matrix / matrix.sum(axis=0)

# 扩展操作：矩阵乘法
def expand(matrix):
    return matrix @ matrix  # 使用稀疏矩阵乘法

# 膨胀操作：矩阵元素的幂运算
def inflate(matrix, power):
    return matrix.power(power)  # 使用稀疏矩阵的幂运算


# 3. MCL 算法实现
def mcl(similarity_matrix, power=2, max_iter=100, tol=1e-6):
    # 初始化转移矩阵
    transition_matrix = normalize_matrix(similarity_matrix).tolil()  # 转换为 lil_matrix
    
    for i in range(max_iter):
        # 保存上一次的矩阵
        prev_matrix = transition_matrix.copy()
        # 扩展操作
        transition_matrix = expand(transition_matrix)
        # 膨胀操作
        transition_matrix = inflate(transition_matrix, power)
        # 归一化
        transition_matrix = normalize_matrix(transition_matrix)
        # 计算稀疏矩阵的差异：避免生成密集矩阵
        diff = transition_matrix - prev_matrix
        if diff.nnz == 0 or (diff.sum() < tol):  # 检查非零元素的和是否小于 tol
            break
    # 聚类
    clusters = {}
    # 转换为 CSR 矩阵后再进行迭代
    transition_matrix = transition_matrix.tocsr()  # 转换为 csr_matrix
    for i, row in enumerate(transition_matrix):
        cluster = tuple(row.indices)  # 仅使用非零元素的索引
        if cluster not in clusters:
            clusters[cluster] = []
        clusters[cluster].append(i)

    return clusters


# 4. 将聚类结果转换为 Orthogroups
def get_orthogroups(clusters, sequences):
    orthogroups = []
    for cluster_indices in clusters.values():
        orthogroup = [sequences[i] for i in cluster_indices]
        orthogroups.append(orthogroup)
    orthogroups.sort(key=len, reverse=True)
    return orthogroups


def main_og_identity(input_blast_dir, db_file, output_file):
    # 获取所有 .blast 文件路径
    blast_files = glob.glob(f"{input_blast_dir}/*")

    # 解析所有 BLAST 结果并存储到数据库
    for blast_file in blast_files:
        store_blast_results(blast_file, db_file)
    
    # 获取所有唯一的序列
    # 从数据库查询所有唯一序列
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    sequences = list(set([seq for seq, in cursor.execute('SELECT seq1 FROM blast_results UNION SELECT seq2 FROM blast_results')]))
    # 为提高查询速度，创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_seq1 ON blast_results(seq1)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_seq2 ON blast_results(seq2)')
    conn.close()

    # 构建相似性矩阵
    similarity_matrix = build_similarity_matrix_from_db(db_file, sequences)
    # 运行 MCL 算法
    clusters = mcl(similarity_matrix)
    # 获取 Orthogroups
    orthogroups = get_orthogroups(clusters, sequences)
    # 将 Orthogroups 写入输出文件
    with open(output_file, 'w') as f:
        for i, group in enumerate(orthogroups):
            f.write(f"Orthogroup {i+1}: {', '.join(group)}\n")


# if __name__ == "__main__":
#     input_blast_dir = "input_blast"  # 改 - 输入的 blast 文件夹
#     output_file = "orthogroups.txt"  # 改 - 输出的 orthogroup 结果文件名字
#     db_name = "blast_results2.db"  # 改 - 数据库的名字

#     main(input_blast_dir, db_name, output_file)

