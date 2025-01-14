#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Author        : yuzijian
# @Email         : yuzijian1010@163.com
# @FileName      : orthogroups_identity.py
# @Time          : 2025-01-01 23:47:29
# @description   :
"""
import numpy as np
import pandas as pd
from collections import defaultdict


def parse_blast(blast_file):
    """
    解析 BLAST 结果文件（outfmt 6 格式）
    返回一个字典，键为序列对，值为比对得分或 E 值
    """
    blast_data = pd.read_csv(blast_file, sep='\t', header=None)
    similarity_dict = {}
    for _, row in blast_data.iterrows():
        seq1, seq2, score = row[0], row[1], row[11]  # 假设第 12 列是比对得分
        similarity_dict[(seq1, seq2)] = float(score)
    return similarity_dict

def build_similarity_matrix(similarity_dict, sequences):
    """
    构建相似性矩阵
    :param similarity_dict: 序列对及其相似性得分的字典
    :param sequences: 所有唯一的序列列表
    :return: 相似性矩阵
    """
    n = len(sequences)
    similarity_matrix = np.zeros((n, n))
    seq_to_index = {seq: i for i, seq in enumerate(sequences)}
    
    for (seq1, seq2), score in similarity_dict.items():
        i, j = seq_to_index[seq1], seq_to_index[seq2]
        similarity_matrix[i][j] = score
        similarity_matrix[j][i] = score  # 对称矩阵
    
    return similarity_matrix

def normalize_matrix(matrix):
    """归一化矩阵，使每列的和为1"""
    return matrix / matrix.sum(axis=0)

def expand(matrix):
    """扩展操作：矩阵乘法"""
    return np.dot(matrix, matrix)

def inflate(matrix, power):
    """膨胀操作：矩阵元素的幂运算"""
    return np.power(matrix, power)

def mcl(similarity_matrix, power=2, max_iter=100, tol=1e-6):
    """MCL 算法实现"""
    # 初始化转移矩阵
    transition_matrix = normalize_matrix(similarity_matrix)
    
    for i in range(max_iter):
        # 保存上一次的矩阵
        prev_matrix = transition_matrix.copy()
        
        # 扩展操作
        transition_matrix = expand(transition_matrix)
        
        # 膨胀操作
        transition_matrix = inflate(transition_matrix, power)
        
        # 归一化
        transition_matrix = normalize_matrix(transition_matrix)
        
        # 检查是否收敛
        if np.linalg.norm(transition_matrix - prev_matrix) < tol:
            break
    
    # 聚类
    clusters = {}
    for i, row in enumerate(transition_matrix):
        cluster = tuple(np.where(row > 0)[0])
        if cluster not in clusters:
            clusters[cluster] = []
        clusters[cluster].append(i)
    
    return clusters

def get_orthogroups(clusters, sequences):
    """
    将聚类结果转换为 Orthogroups
    :param clusters: MCL 聚类结果
    :param sequences: 所有唯一的序列列表
    :return: Orthogroups 列表
    """
    orthogroups = []
    for cluster_indices in clusters.values():
        orthogroup = [sequences[i] for i in cluster_indices]
        orthogroups.append(orthogroup)
    return orthogroups

def main(blast_file):
    # 解析 BLAST 结果
    similarity_dict = parse_blast(blast_file)
    
    # 获取所有唯一的序列
    sequences = list(set([seq for pair in similarity_dict.keys() for seq in pair]))
    
    # 构建相似性矩阵
    similarity_matrix = build_similarity_matrix(similarity_dict, sequences)
    
    # 运行 MCL 算法
    clusters = mcl(similarity_matrix)
    
    # 获取 Orthogroups
    orthogroups = get_orthogroups(clusters, sequences)
    
    # 输出 Orthogroups
    for i, group in enumerate(orthogroups):
        print(f"Orthogroup {i+1}: {group}")

# 示例调用
if __name__ == "__main__":
    blast_file = "blast_results.txt"  # 替换为你的 BLAST 结果文件
    main(blast_file)
