#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Author        : yuzijian
# @Email         : yuzijian1010@163.com
# @FileName      : core_test_2.py
# @Time          : 2023/9/2 1:48
# @description   :
"""

import os
import re
import glob
import time
import shutil
from Bio import SeqIO
from concurrent.futures import ProcessPoolExecutor


# 1 提取出基因id
class GeneIdProcessor:
    def __init__(self, sp_name, syn_list):
        self.sp_name = sp_name
        self.syn_list = syn_list

    def process_gene_ids(self):
        shutil.rmtree("output_1_CSDP_id_file", ignore_errors=True)
        os.makedirs("output_1_CSDP_id_file")
        shutil.rmtree("output_1_CSDP_sp_id", ignore_errors=True)
        os.makedirs("output_1_CSDP_sp_id")

        with open(self.syn_list, "r") as file:
            for line in file:
                gene_ids = line.strip().split()
                match_count = len(set("".join(re.findall("[a-zA-Z]", re.split("g", gene_id)[0])) for gene_id in gene_ids if "".join(re.findall("[a-zA-Z]", re.split("g", gene_id)[0])) in self.sp_name))
                match_percentage = match_count / len(self.sp_name) * 100
                with open("output_1_CSDP_id_file/core.txt", "a+") as core, open("output_1_CSDP_id_file/softcore.txt", "a+") as softcore, open("output_1_CSDP_id_file/dispensable.txt", "a+") as dispensable, open("output_1_CSDP_id_file/private.txt", "a+") as private:
                    for gene_id in gene_ids:
                        sp_name = "".join(re.findall("[a-zA-Z]", re.split("g", gene_id)[0]))
                        if sp_name == "Pvu" or gene_id == ".":  # 改 - 物种的第一列名字！！！
                            continue
                        if match_percentage == 100:  # 24
                            core.write(gene_id + "\n")
                            sp_type_pfam = open(f"output_1_CSDP_sp_id/{sp_name}_core.txt", "a+")
                            sp_type_pfam.write(f"{gene_id}\n")
                        elif match_percentage >= 80:  # 24 * 0.8 = 19.2 ==》 20-24
                            softcore.write(gene_id + "\n")
                            sp_type_pfam = open(f"output_1_CSDP_sp_id/{sp_name}_softcore.txt", "a+")
                            sp_type_pfam.write(f"{gene_id}\n")
                        elif match_count == 1:  # 1
                            private.write(gene_id + "\n")
                            sp_type_pfam = open(f"output_1_CSDP_sp_id/{sp_name}_private.txt", "a+")
                            sp_type_pfam.write(f"{gene_id}\n")
                        else:  # 1-20
                            dispensable.write(gene_id + "\n")
                            sp_type_pfam = open(f"output_1_CSDP_sp_id/{sp_name}_dispensable.txt", "a+")
                            sp_type_pfam.write(f"{gene_id}\n")


# 2 获取core、softcore、sidpensable、private四种基因id的cds和pep序列，并写入到文件中
class CodeEditor:
    def __init__(self):
        self.cds_gene_ids = self.cds_files_ids(glob.glob("input_cds_file/*"))  # （可改） - 物种 cds 文件夹
        self.pep_gene_ids = self.pep_files_ids(glob.glob("input_pep_file/*"))  # （可改） - 物种 pep 文件夹

    def pep_files_ids(self, input_pep_files):  # 返回pep字典 {sp_name:{id,seq}}
        pep_gene_ids = {}
        for file in input_pep_files:
            file_name = os.path.basename(file).split(".")[0]
            pep_gene_ids[file_name] = {record.id: str(record.seq).replace("*", "").replace(".", "") for record in SeqIO.parse(file, "fasta")}
        return pep_gene_ids

    def cds_files_ids(self, input_cds_files):  # 返回cds字典 {sp_name:{id,seq}}
        cds_gene_ids = {}
        for file in input_cds_files:
            file_name = os.path.basename(file).split(".")[0]
            cds_gene_ids[file_name] = {record.id: str(record.seq).replace("*", "").replace(".", "") for record in SeqIO.parse(file, "fasta")}
        return cds_gene_ids
    
    # 增加 生成 privatefrompep.txt
    # 1.将output_1_CSDP_id_file文件夹中的四个文件的基因id写入到{sp:[id]}中,字典命名为 sp_csdp_gene_dict
    # 2.sp_csdp_gene_dict 字典的与 pep_gene_ids 字典相同的键进行取差值， sp_csdp_gene_dict 都在 pep_gene_ids 字典中，但是pep_gene_ids不一定在 sp_csdp_gene_dict。生成取差值的字典。
    # 3.将取差值的字典中的值中的值基因id，写入到output_1_CSDP_id_file文件夹中，文件名字命名为privatefrompep.txt。
    # 4.将取差值的字典中的值中的值加上“privatefrompep.txt”作为文件的名字，值写入到该文件中，写入到 output_1_CSDP_sp_id 文件夹中，文件名字命名为{sp_name}_privatefrompep.txt。
    def generate_private_from_pep(self, output_1_CSDP_id_files):
        # Step 1: Create a dictionary to store gene IDs from output_1_CSDP_id_files
        sp_csdp_gene_dict = {}
        for file in output_1_CSDP_id_files:
            with open(file, "r") as f:
                for line in f:
                    gene_id = line.strip()
                    sp_name = "".join(re.findall("[a-zA-Z]", re.split("g", gene_id)[0]))
                    if sp_name not in sp_csdp_gene_dict:
                        sp_csdp_gene_dict[sp_name] = []
                    sp_csdp_gene_dict[sp_name].append(gene_id)

        # Step 2: Find the difference between sp_csdp_gene_dict and pep_gene_ids
        private_gene_dict = {}
        for sp_name in sp_csdp_gene_dict:
            if sp_name in self.pep_gene_ids:
                # private_genes = list(set(sp_csdp_gene_dict[sp_name]) - set(self.pep_gene_ids[sp_name]))
                private_genes = list(set(self.pep_gene_ids[sp_name]) - set(sp_csdp_gene_dict[sp_name]))
                if private_genes:
                    private_gene_dict[sp_name] = private_genes

        # # Step 3: Write the private gene IDs to privatefrompep.txt and {sp_name}_privatefrompep.txt files
        # with open(os.path.join("output_1_CSDP_id_file/privatefrompep.txt"), "w") as private_file:
        #     for sp_name, private_genes in private_gene_dict.items():
        #         sp_file_path = os.path.join(f"output_1_CSDP_sp_id/{sp_name}_privatefrompep.txt")
        #         with open(sp_file_path, "w") as sp_private_file, open(f"output_1_CSDP_sp_id_merge/{sp_name}_private.txt", "a+") as merge_private:
        #             for gene_id in private_genes:
        #                 private_file.write(f"{gene_id}\n")
        #                 sp_private_file.write(f"{gene_id}\n")
        # Step 3: Write the private gene IDs to privatefrompep.txt and {sp_name}_privatefrompep.txt files
        with open(os.path.join("output_1_CSDP_id_file/private.txt"), "a+") as private_file:
            for sp_name, private_genes in private_gene_dict.items():
                with open(f"output_1_CSDP_sp_id/{sp_name}_private.txt", "a+") as sp_private_file:
                    private_file.write("\n".join(private_genes) + "\n")
                    sp_private_file.write("\n".join(private_genes) + "\n")


    def process_files(self, output_1_CSDP_id_files):  # 根据存放的基因id文件，获取对应基因id的pep和cds序列
        shutil.rmtree("output_2_CSDP_cds_file", ignore_errors=True)
        os.makedirs("output_2_CSDP_cds_file")
        shutil.rmtree("output_2_CSDP_pep_file", ignore_errors=True)
        os.makedirs("output_2_CSDP_pep_file")

        for file in output_1_CSDP_id_files:
            file_name = os.path.basename(file).split(".")[0]
            with open(f"output_2_CSDP_cds_file/{file_name}_cds.txt", "a+") as type_cds, open(f"output_2_CSDP_pep_file/{file_name}_pep.txt", "a+") as type_pep, open(file, "r") as f:
                for line in f:
                    new_line = line.strip()
                    sp_name = "".join(re.findall("[a-zA-Z]", re.split("g", new_line)[0]))
                    type_cds.write(f">{new_line}\n{str(self.cds_gene_ids[sp_name][new_line])}\n")
                    type_pep.write(f">{new_line}\n{str(self.pep_gene_ids[sp_name][new_line])}\n")


# 3 分割为物种 + 四种类型的文件，并统计个数
class FileProcessor:
    def __init__(self):
        self.species_counts = {}

    def process_cds_files(self, file_path):
        species_name = os.path.basename(file_path).split(".")[0]
        with open(file_path) as file:
            for line in SeqIO.parse(file, "fasta"):
                sp_name = "".join(re.findall("[a-zA-Z]", re.split("g", line.id)[0]))
                new_cds_file = open(f"output_3_CSDP_all_cds/{sp_name}_{species_name}.txt", "a+")
                new_cds_file.write(f">{line.id}\n{str(line.seq)}\n")

    def process_pep_files(self, file_path):
        species_name = os.path.basename(file_path).split(".")[0]
        with open(file_path) as file:
            for line in SeqIO.parse(file, "fasta"):
                sp_name = "".join(re.findall("[a-zA-Z]", re.split("g", line.id)[0]))
                new_pep_file = open(f"output_3_CSDP_all_pep/{sp_name}_{species_name}.txt", "a+")
                new_pep_file.write(f">{line.id}\n{str(line.seq)}\n")

    def count_species_types(self, file_paths):
        for file_path in file_paths:
            sp_name, species_type = os.path.basename(file_path).split("_")[:2]
            self.species_counts.setdefault(sp_name, {}).setdefault(species_type, 0)
            self.species_counts[sp_name][species_type] += len(list(SeqIO.parse(file_path, "fasta")))

        with open("sp_type_count.txt", "w") as file:  # 改 - 物种与四种类型的数目统计文件名字
            file.write(f"sp\tcore\tdispensable\tprivate\tsoftcore\n")
            for key in self.species_counts.keys():
                sorted_keys = sorted(self.species_counts[key].keys())
                num = [self.species_counts[key][sorted_key] for sorted_key in sorted_keys]
                if "private" not in sorted_keys:
                    num.insert(2, 0)
                str_hhh = '\t'.join(map(str, num))
                file.write(f"{key}\t{str_hhh}\n")

    def process_files(self):
        shutil.rmtree("output_3_CSDP_all_cds", ignore_errors=True)
        os.makedirs("output_3_CSDP_all_cds")
        shutil.rmtree("output_3_CSDP_all_pep", ignore_errors=True)
        os.makedirs("output_3_CSDP_all_pep")
        cds_folder_path = glob.glob(os.path.join("output_2_CSDP_cds_file", "*.txt"))
        pep_folder_path = glob.glob(os.path.join("output_2_CSDP_pep_file", "*.txt"))
        with ProcessPoolExecutor(max_workers=12) as executor:  # 改 - 最大线程数
            executor.map(self.process_cds_files, cds_folder_path)
            executor.map(self.process_pep_files, pep_folder_path)
        self.count_species_types(glob.glob(os.path.join("output_3_CSDP_all_pep", "*.txt")))


# 4 生成四种类型和sp_四种类型的文件，并统计个数
class PfamProcessor:
    def __init__(self):
        self.pfam_dict = {}
        self.sp_pfam_counts = {}

    def process_pfam_files(self, input_pfam_file):
        self.pfam_dict = {}
        for file_path in glob.glob(input_pfam_file):
            with open(file_path, 'r') as file:
                file_name = os.path.basename(file_path).split(".")[0]
                gene_dict = {line.split()[0]: line.split()[1:] for line in file if not line.startswith(("#", "\n", "\t"))}
                self.pfam_dict[file_name] = gene_dict

    def extract_pfam_files(self, output_1_CSDP_id_files):
        shutil.rmtree("output_4_CSDP_pfam", ignore_errors=True)
        os.makedirs("output_4_CSDP_pfam")
        shutil.rmtree("output_4_CSDP_sp_type_pfam", ignore_errors=True)
        os.makedirs("output_4_CSDP_sp_type_pfam")

        total_pfam_count = {"core": 0, "softcore": 0, "dispensable": 0, "private": 0}
        # total_pfam_count = {"core": 0, "softcore": 0, "dispensable": 0, "private": 0, "privatefrompep": 0}
        for file in output_1_CSDP_id_files:
            file_name = os.path.basename(file).split(".")[0]
            with open(f"output_4_CSDP_pfam/{file_name}_pfam.txt", "a+") as pfam, open(file, "r") as f:
                for line in f:
                    new_line = line.strip()
                    sp_name = "".join(re.findall("[a-zA-Z]", re.split("g", new_line)[0]))
                    
                    if new_line not in self.pfam_dict[sp_name]:
                        continue
                    hhhh = "\t".join(self.pfam_dict[sp_name][new_line])
                    pfam.write(f"{new_line}\t{hhhh}\n")
                    total_pfam_count[file_name] += 1

                    sp_type_pfam = open(f"output_4_CSDP_sp_type_pfam/{sp_name}_{file_name}.pfam", "a+")
                    sp_type_pfam.write(f"{new_line}\t{hhhh}\n")

        with open("pfam_type_count.txt", "w") as count_file:
            for key, value in total_pfam_count.items():
                count_file.write(f"{key}\t{value}\n")
    
    def count_pfam_num(self, file_paths):
        for file_path in file_paths:
            sp_name, species_type = os.path.basename(file_path).split(".")[0].split("_")
            self.sp_pfam_counts.setdefault(sp_name, {}).setdefault(species_type, 0)
            self.sp_pfam_counts[sp_name][species_type] += sum(1 for line in open(file_path))

        with open("sp_type_pfam_count.txt", "w") as file:  # 改 - 物种与四种类型的数目统计文件名字
            file.write(f"sp\tcore\tdispensable\tprivate\tsoftcore\n")
            for key in self.sp_pfam_counts.keys():
                sorted_keys = sorted(self.sp_pfam_counts[key].keys())
                num = [self.sp_pfam_counts[key][sorted_key] for sorted_key in sorted_keys]
                if "private" not in sorted_keys:
                    num.insert(2, 0)
                str_hhh = '\t'.join(map(str, num))
                file.write(f"{key}\t{str_hhh}\n")


# 5 获取四种类型基因的 cds 数目和总长度，并将结果写入到文件中
class PfamCounter:
    def __init__(self):
        self.sp_cds_counts = {}

    def count_pfam_num(self, file_paths):
        for file_path in file_paths:
            sp_name, species_type = os.path.basename(file_path).split("_")[:2]
            self.sp_cds_counts.setdefault(sp_name, {}).setdefault(species_type, 0)
            id_num = len(list(SeqIO.parse(file_path, "fasta")))
            seq_lengths = sum([len(record.seq) for record in SeqIO.parse(file_path, "fasta")])
            average_len = round(seq_lengths / id_num, 3)  # 计算平均长度并保留三位小数
            self.sp_cds_counts[sp_name][species_type] = [id_num, seq_lengths, average_len]

        with open("sp_type_cds_count.txt", "w") as file:  # 改 - 物种与四种类型的数目统计文件名字
            file.write(f"sp\tcore\t\t\tdispensable\t\t\tprivate\t\t\tsoftcore\n")
            file.write(f"sp\tid_num\tseq_len\tavg_len\tid_num\tseq_len\tavg_len\tid_num\tseq_len\tavg_len\t\n")
            for key in self.sp_cds_counts.keys():
                sorted_keys = sorted(self.sp_cds_counts[key].keys())
                num = [self.sp_cds_counts[key][sorted_key] for sorted_key in sorted_keys]
                if "private" not in sorted_keys:
                    num.insert(2, [0, 0, 0.000])
                num_CSDP = '\t'.join(map(str, [item for line in num for item in line]))
                file.write(f"{key}\t{num_CSDP}\n")


if __name__ == "__main__":
    start_time = time.time()  # 记录开始时间

    # 1 提取出基因id
    sp_name = ["Bva","Sto","Psa","Aip","Amo","Ahy","Adu","Lal","Lan","Aev","Dod","Apr","Lja","Aed","Cca","Gma","Gso","Mtr","Car","Mal","Tpr","Tsu","Vra","Ssu"]  # 改 - 物种的简称。注意：第一列的物种简称别放到这个列表中！！
    syn_list = "Pvu_list_add_Bva.txt"  # 改 - 共线性列表文件 
    gene_id_processor = GeneIdProcessor(sp_name, syn_list)
    gene_id_processor.process_gene_ids()
    print("The first step, extracting the gene id is done")

    # 2 获取core、softcore、sidpensable、private四种基因id的cds和pep序列，并写入到文件中
    editor = CodeEditor()
    editor.generate_private_from_pep(glob.glob("output_1_CSDP_id_file/*"))  # 新加 - 时间：23.9.1
    editor.process_files(glob.glob("output_1_CSDP_id_file/*"))
    print("The second step, obtaining the cds and pep sequences of the four types of gene ids has been completed")

    # 3 分割为物种+四种类型的文件，并统计个数
    fp = FileProcessor()
    fp.process_files()
    print("The third step, split the file into species and four types, and count the number")

    # 5 获取四种类型基因的 cds 数目和总长度，并将结果写入到文件中
    pfam_counter = PfamCounter()
    pfam_counter.count_pfam_num(glob.glob("output_3_CSDP_all_cds/*.txt"))
    print("The five step, the cds number and total length of the four types of genes were obtained")


    # # 4 生成四种类型和sp_四种类型的文件，并统计个数
    # pfam_processor = PfamProcessor()
    # pfam_processor.process_pfam_files("input_pfam_file/*.pfam")
    # pfam_processor.extract_pfam_files(glob.glob("output_1_CSDP_id_file/*"))
    # pfam_processor.count_pfam_num(glob.glob("output_4_CSDP_sp_type_pfam/*.pfam"))
    # print("The fourth step, generate four types and SP_four types of files, and the number of statistics is completed")

    end_time = time.time()
    print(f"End of run, total time is: {end_time - start_time} seconds!")

