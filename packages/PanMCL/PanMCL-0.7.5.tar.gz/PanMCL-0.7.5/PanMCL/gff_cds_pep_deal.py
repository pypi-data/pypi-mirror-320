#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Author        : yuzijian
# @Email         : yuzijian1010@163.com
# @FileName      : gff_cds_pep_deal.py
# @Time          : 2025-01-14 10:33:13
# @description   :处理原始的 gff、cds和pep文件，得到处理后的 gff、lens、pep和cds结果文件。
"""
import pandas as pd
from Bio import SeqIO


# 1. 对原始的gff文件，进行处理，得到处理后的 gff 和 lens 结果文件
class GFFProcessor:
    def __init__(self, input_gff, output_gff, species_prefix, feature_type="mRNA", id_attribute_index=1, id_separator="="):
        self.input_file = input_gff
        self.output_file = output_gff
        self.lens_output_file = species_prefix + '.lens'
        self.feature_type = feature_type
        self.id_attribute_index = id_attribute_index
        self.id_separator = id_separator
        self.species_prefix = species_prefix
        self.columns = ['seqid', 'source', 'type', 'start', 'end', 'score', 'strand', 'phase', 'attributes']
        self.gene_counts = {}

    def extract_gene_id(self, attr):
        first_part = attr.split(';')[self.id_attribute_index]
        gene_id = first_part.split(self.id_separator)[1]
        return gene_id

    def rename_chromosomes(self, df):
        unique_chroms = sorted(df['seqid'].unique())
        chrom_map = {old: str(i+1) for i, old in enumerate(unique_chroms)}
        df.loc[:, 'seqid'] = df['seqid'].map(chrom_map)
        return df

    def generate_gene_id(self, row):
        chrom_num = row['seqid']
        if chrom_num not in self.gene_counts:
            self.gene_counts[chrom_num] = 1
        
        chrom_part = f"{int(chrom_num):03d}g"
        count_part = f"{self.gene_counts[chrom_num]:05d}"
        self.gene_counts[chrom_num] += 1
        
        return f"{self.species_prefix}{chrom_part}{count_part}"

    def generate_lens_file(self):
        chr_lens = {}
        with open(self.output_file, "r") as f_in:
            for line in f_in:
                fields = line.strip().split("\t")
                chr_lens[fields[0]] = fields[6]  # 使用end位置作为长度
        with open(self.lens_output_file, "w") as f_out:
            for chrom in sorted(chr_lens.keys(), key=int):
                f_out.write(f"{chrom}\t{chr_lens[chrom]}\n")
        print(f"Chromosome lengths file saved to {self.lens_output_file}")

    def process(self):
        df = pd.read_csv(self.input_file, sep='\t', comment='#', names=self.columns)
        df_genes = df[df['type'] == self.feature_type].copy()
        df_genes['gene_id'] = df_genes['attributes'].apply(self.extract_gene_id)
        result_df = df_genes[['seqid', 'start', 'end', 'strand', 'gene_id']].copy()
        result_df = self.rename_chromosomes(result_df)
        result_df.loc[:, 'seqid'] = result_df['seqid'].astype(int)
        result_df = result_df.sort_values(['seqid', 'start'])
        result_df['new_gene_id'] = result_df.apply(self.generate_gene_id, axis=1)
        result_df['gene_count'] = result_df.groupby('seqid').cumcount() + 1
        result_df.to_csv(self.output_file, sep='\t', index=False, header=False)
        print(f"Processing complete, results saved to {self.output_file}")
        self.generate_lens_file()


# 2. 根据得到的处理后的gff文件，生成处理的 cds 和 pep 文件
class GeneProcessor:
    def __init__(self, gene_id_position=0, use_nested_split=False, nested_split_position=1):
        self.GENE_ID_POSITION = gene_id_position
        self.USE_NESTED_SPLIT = use_nested_split
        self.NESTED_SPLIT_POSITION = nested_split_position

    def create_gene_dict(self, gff_file_path):
        gene_dict = {}
        with open(gff_file_path, "r") as gff_file:
            for line in gff_file:
                columns = line.strip().split("\t")
                gene_dict[columns[4]] = columns[5]
        return gene_dict

    def process_protein_file(self, gene_dict, protein_file_path, output_file_path):
        output_file = open(output_file_path, "w")
        with open(protein_file_path, "r") as protein_file:
            for record in SeqIO.parse(protein_file, "fasta"):
                gene_id = self._extract_gene_id(record.description)
                if gene_id in gene_dict:
                    new_gene_id = gene_dict[gene_id]
                    new_sequence = str(record.seq)
                    output_file.write(f">{new_gene_id}\n{new_sequence}\n")
        output_file.close()

    def _extract_gene_id(self, description):
        parts = description.split("\t")
        if self.USE_NESTED_SPLIT:
            return parts[self.GENE_ID_POSITION].split("=")[self.NESTED_SPLIT_POSITION]
        return parts[self.GENE_ID_POSITION]

    def process_files(self, gff_file_path, input_file_path, output_file_path):
        gene_dict = self.create_gene_dict(gff_file_path)
        self.process_protein_file(gene_dict, input_file_path, output_file_path)
        print(f"Processing completed {output_file_path}")


# if __name__ == "__main__":
#     # 1. 对原始的gff文件，进行处理，得到处理后的 gff 和 lens 结果文件
#     processor = GFFProcessor(
#         input_gff='GWHEUVW00000000.1.gff',  # 改 - 输入的原始gff文件
#         output_gff='She.new.gff',  # 改 - 输出的结果gff文件
#         feature_type='mRNA',  # 改 - 筛选基因的结构
#         id_attribute_index=1,  # 改 - “;”号分割开之后的基因id的所在的元素数字
#         id_separator='=',  # 改 - 分割之后的元素，再分割的要求
#         species_prefix='She'  # 改 - 物种名字的简称
#     )
#     processor.process()

#     # 2. 根据得到的处理后的gff文件，生成处理的 cds 和 pep 文件
#     # 处理 pep 文件
#     processor = GeneProcessor(
#         gene_id_position=1,
#         use_nested_split=True,
#         nested_split_position=1
#     )
#     processor.process_files(
#         output_gff="She.new.gff",
#         input_pep="GWHEUVW00000000.1.Protein.faa",
#         output_pep="She.pep"
#     )

#     # 处理 pep 文件
#     processor = GeneProcessor(
#         gene_id_position=0,  # 改 - 对应基因id的位置，如果能和">"后的基因id对应上，值就为0，如果是description第二个元素，则这个值为1；依次往后
#         use_nested_split=False,  # 改 - 如果gene_id_position为0，则这个值为 False ，如果不为0，则是 Ture
#         nested_split_position=1  # 一般不需要改
#     )
#     processor.process_files(
#         output_gff="She.new.gff",
#         input_cds="GWHEUVW00000000.1.CDS.fasta",
#         output_cds="She.cds"
#     )

