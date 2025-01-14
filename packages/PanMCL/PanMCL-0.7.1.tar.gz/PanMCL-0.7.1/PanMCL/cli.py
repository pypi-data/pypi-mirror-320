#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Author        : yuzijian
# @Email         : yuzijian1010@163.com
# @FileName      : cli.py
# @Time          : 2024-12-30 11:51:41
# @description   :
"""
# my_commandline_tool/cli.py
import os
import time
import glob
import shutil
import argparse
import concurrent.futures
from .run_mcscanx_V4 import MCScanX
from .run_blast_diamond import RunBioSoftware
from .orthogroups_identity_V3 import main_og_identity
from .core_test_3 import GeneIdProcessor, CodeEditor, FileProcessor, PfamCounter
from .run_interproscan_2 import deduplicate_fasta, split_fasta, run_interproscan
from .gff_cds_pep_deal import GFFProcessor, GeneProcessor  # 处理原始文件


# 1. 实现批量进行序列比对的功能
def run_blast_diamond(args):
    process = args.process
    thread = args.thread
    repeat = args.repeat
    software = args.software
    add_species = args.add_species

    species = []
    files = glob.glob('*.pep')
    for fn in files:
        species.append(fn.split('.')[0])

    sub = []
    if add_species:
        for na in add_species:
            for spec in species:
                sub.append(f'{na}_{spec}')
                sub.append(f'{spec}_{na}')
        sub = list(set(sub))
    RunBioSoftware(species, repeat, sub, [], software, process, thread)


# 2. 调用MCScanX批量进行序列比对
def run_mcscanx(args):
    start_time = time.time()

    input_blast = args.input_blast  # 输入的blast文件夹
    input_gff = args.input_gff  # 输入的gff文件夹
    match_score = args.match_score  # 匹配得分，最终得分 = MATCH_SCORE + NUM_GAPS * GAP_PENALTY
    gap_penalty = args.gap_penalty  # 间隙惩罚，即每出现一个间隙时的惩罚分数
    match_size = args.match_size  # 定义一个共线性区块所需的最小基因数量
    e_value = args.e_value  # BLAST比对结果的显著性阈值
    max_gaps = args.max_gaps  # 允许的最大间隙数量
    overlap_window = args.overlap_window  # 用于合并BLAST匹配结果的最大距离（以基因数量计）
    build_blocks_only = args.build_blocks_only  # 仅构建成对的共线性区块
    block_pattern = args.block_pattern  # 0-种内和种间；1-种内；2-种间
    synvisio = args.synvisio  # 改 - 是否启用 synvisio 文件处理
    max_workers = args.process  # 改 -p 或 --process

    for output_dir in ["output_mcacanx_result", "output_gff_blast"]:
        shutil.rmtree(output_dir, ignore_errors=True)
        os.makedirs(output_dir)

    if synvisio:
        shutil.rmtree("output_synvisio", ignore_errors=True)
        os.makedirs("output_synvisio")

    mc = MCScanX(input_blast, input_gff, match_score, gap_penalty, match_size, e_value, max_gaps, overlap_window, build_blocks_only, block_pattern, synvisio)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(mc.run_mcscanx, one, two) for one, two in mc.name]
        concurrent.futures.wait(futures)

    end_time = time.time()
    print(f"Total running time: {end_time - start_time} seconds")


# 3. 对序列的pep文件，进行去重、分割，然后批量的调用interproscan软件
def run_interproscan_command(args):
    start_time = time.time()

    # 解析参数
    input_fasta = args.input_fasta
    output_fasta = args.output_fasta
    number_of_splits = args.number_of_splits
    process_interpro = args.process_interpro
    thread_interpro = args.thread_interpro

    output_disassemble = "output_disassemble"
    output_interproscan_result = "output_interproscan_result"

    # 清理并创建输出目录
    shutil.rmtree(output_disassemble, ignore_errors=True)
    os.makedirs(output_disassemble)
    shutil.rmtree(output_interproscan_result, ignore_errors=True)
    os.makedirs(output_interproscan_result)

    # 1. 去重
    deduplicate_fasta(input_fasta, output_fasta)
    print("Deduplication completed.")

    # 2. 分割
    split_fasta(output_fasta, output_disassemble, number_of_splits)
    print("Splitting completed.")

    # 3. 调用 InterProScan
    pep_files = glob.glob(f"{output_disassemble}/*.fasta")
    with concurrent.futures.ProcessPoolExecutor(max_workers=process_interpro) as executor:
        for file in pep_files:
            executor.submit(run_interproscan, file, thread_interpro)
    print("InterProScan analysis completed.")

    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")


# 4. 根据序列比对结果，将其存储到sqlite中，然后使用MCL算法进行聚类
def run_orthogroups(args):
    # 解析参数
    input_blast_dir = args.input_blast_dir
    output_file = args.output_file
    db_name = args.db_name
    # 调用 main 函数
    main(input_blast_dir, db_name, output_file)
    print("Orthogroups calculation completed.")


# 5. 实现鉴定四类基因的功能，并进行提取相关的基因
def process_pangenes(args):
    start_time = time.time()

    sp_name = ["Bva", "Sto", "Psa", "Aip", "Amo", "Ahy", "Adu", "Lal", "Lan", "Aev", "Dod", "Apr", "Lja", "Aed", "Cca", "Gma", "Gso", "Mtr", "Car", "Mal", "Tpr", "Tsu", "Vra", "Ssu"]  # 改 - 需要优化！
    syn_list = args.file
    gene_id_processor = GeneIdProcessor(sp_name, syn_list)
    gene_id_processor.process_gene_ids()
    print("The first step, extracting the gene id is done")

    editor = CodeEditor()
    editor.generate_private_from_pep(glob.glob("output_1_CSDP_id_file/*"))
    editor.process_files(glob.glob("output_1_CSDP_id_file/*"))
    print("The second step, obtaining the cds and pep sequences of the four types of gene ids has been completed")

    fp = FileProcessor()
    fp.process_files()
    print("The third step, split the file into species and four types, and count the number")

    pfam_counter = PfamCounter()
    pfam_counter.count_pfam_num(glob.glob("output_3_CSDP_all_cds/*.txt"))
    print("The five step, the cds number and total length of the four types of genes were obtained")

    end_time = time.time()
    print(f"End of run, total time is: {end_time - start_time} seconds!")



# 处理原始 GFF 文件，生成处理后的 GFF 文件
def process_gff(args):
    processor = GFFProcessor(
        input_gff=args.input_gff,
        output_gff=args.output_gff,
        feature_type=args.feature_type,
        id_attribute_index=args.id_attribute_index,
        id_separator=args.id_separator,
        species_prefix=args.species_prefix
    )
    processor.process()
    print(f"Processed GFF file saved to {args.output_gff}")

# 根据处理后的 GFF 文件，生成处理后的 PEP 或 CDS 文件
def process_seq(args):
    processor = GeneProcessor(
        gene_id_position=args.gene_id_position,
        use_nested_split=args.use_nested_split,
        nested_split_position=args.nested_split_position
    )
    
    # 调用 process_files 方法处理文件
    processor.process_files(
        output_gff=args.output_gff,
        input_seq=args.input_seq,
        output_seq=args.output_seq
    )
    
    # 根据输出文件的扩展名判断是 PEP 还是 CDS
    if args.output_seq.endswith('.pep') or args.output_seq.endswith('.faa'):
        print(f"Processed PEP file saved to {args.output_seq}")
    elif args.output_seq.endswith('.cds') or args.output_seq.endswith('.fasta'):
        print(f"Processed CDS file saved to {args.output_seq}")
    else:
        print(f"Processed sequence file saved to {args.output_seq}")

# 直接输入原始 GFF、CDS、PEP 文件，生成处理后的文件
def process_all(args):
    # 处理 GFF 文件
    gff_processor = GFFProcessor(
        input_gff=args.input_gff,
        output_gff=args.output_gff,
        feature_type=args.feature_type,
        id_attribute_index=args.id_attribute_index,
        id_separator=args.id_separator,
        species_prefix=args.species_prefix
    )
    gff_processor.process()
    print(f"Processed GFF file saved to {args.output_gff}")

    # 处理 PEP 文件
    pep_processor = GeneProcessor(
        gene_id_position=args.pep_gene_id_position,  # 使用 PEP 的参数
        use_nested_split=args.pep_use_nested_split,
        nested_split_position=args.pep_nested_split_position
    )
    pep_processor.process_files(
        output_gff=args.output_gff,
        input_seq=args.input_pep,
        output_seq=args.output_pep
    )
    print(f"Processed PEP file saved to {args.output_pep}")

    # 处理 CDS 文件
    cds_processor = GeneProcessor(
        gene_id_position=args.cds_gene_id_position,  # 使用 CDS 的参数
        use_nested_split=args.cds_use_nested_split,
        nested_split_position=args.cds_nested_split_position
    )
    cds_processor.process_files(
        output_gff=args.output_gff,
        input_seq=args.input_cds,
        output_seq=args.output_cds
    )
    print(f"Processed CDS file saved to {args.output_cds}")




# 主要的代码部分
def main():
    parser = argparse.ArgumentParser(description="A simple command-line tool.")
    subparsers = parser.add_subparsers(help='sub-command help')


    # 1. 实现批量进行序列比对的功能
    parser_run = subparsers.add_parser('runbd', help='Run BLAST or DIAMOND for sequence alignment')
    parser_run.add_argument('-p', '--process', type=int, default=4, help='Number of processes (default: 4)')
    parser_run.add_argument('-t', '--thread', type=int, default=4, help='Number of threads per process (default: 4)')
    parser_run.add_argument('-r', '--repeat', action='store_true', default=True, help='Allow repeated comparisons (default: True)')
    parser_run.add_argument('-s', '--software', choices=['blast', 'diamond'], default='diamond', help='Software to use: blast or diamond (default: diamond)')
    parser_run.add_argument('-a', '--add-species', nargs='+', default=[], help='Additional species pairs to compare (e.g., Tpr)')
    parser_run.set_defaults(func=run_blast_diamond)


    # 2. run-mcscanx 命令
    parser_run = subparsers.add_parser('runsyn', help='Run MCScanX for genome comparison')
    # 必需参数
    parser_run.add_argument('-b', '--input-blast', required=True, help='Input directory containing BLAST results')
    parser_run.add_argument('-g', '--input-gff', required=True, help='Input directory containing GFF files')
    # MCScanX 可选参数
    parser_run.add_argument('-k', '--match-score', type=int, default=50, help='Match score, final score=MATCH_SCORE+NUM_GAPS*GAP_PENALTY (default: 50)')
    parser_run.add_argument('-gp', '--gap-penalty', type=int, default=-1, help='Gap penalty, gap penalty (default: -1)')
    parser_run.add_argument('-s', '--match-size', type=int, default=5, help='Match size, number of genes required to call a collinear block (default: 5)')
    parser_run.add_argument('-e', '--e-value', type=float, default=1e-05, help='E-value, alignment significance (default: 1e-05)')
    parser_run.add_argument('-m', '--max-gaps', type=int, default=25, help='Maximum gaps, maximum gaps allowed (default: 25)')
    parser_run.add_argument('-w', '--overlap-window', type=int, default=5, help='Overlap window, maximum distance (# of genes) to collapse BLAST matches (default: 5)')
    parser_run.add_argument('-a', '--build-blocks-only', action='store_true', help='Only builds the pairwise blocks (default: False)')
    parser_run.add_argument('-bp', '--block-pattern', type=int, default=0, help='Patterns of collinear blocks. 0:intra- and inter-species (default); 1:intra-species; 2:inter-species')
    parser_run.add_argument('-sv', '--synvisio', action='store_true', help='Enable SynVisio file processing (default: False)')
    # 并发进程数
    parser_run.add_argument('-p', '--process', type=int, default=10, help='Maximum number of concurrent workers (default: 10)')
    parser_run.set_defaults(func=run_mcscanx)


    # 3. 对序列的pep文件，进行去重、分割，然后批量的调用interproscan软件
    parser_run = subparsers.add_parser('runinter', help='Run InterProScan for sequence analysis')
    parser_run.add_argument('-i', '--input-fasta', required=True, help='Input FASTA file (e.g., genome_s.fasta)')
    parser_run.add_argument('-o', '--output-fasta', default="unique.fasta", help='Output deduplicated FASTA file (default: unique.fasta)')
    parser_run.add_argument('-n', '--number-of-splits', type=int, default=100, help='Number of splits (default: 100)')
    parser_run.add_argument('-p', '--process-interpro', type=int, default=3, help='Number of processes for InterProScan (default: 3)')
    parser_run.add_argument('-t', '--thread-interpro', type=int, default=4, help='Number of threads per process (default: 4)')
    parser_run.set_defaults(func=run_interproscan_command)


    # 4. 根据序列比对结果，将其存储到sqlite中，然后使用MCL算法进行聚类
    parser_run = subparsers.add_parser('runog', help='Calculate orthogroups using MCL')
    parser_run.add_argument('-i', '--input-blast-dir', required=True, help='Input directory containing BLAST results')
    parser_run.add_argument('-o', '--output-file', default="orthogroups.txt", help='Output file for orthogroups (default: orthogroups.txt)')
    parser_run.add_argument('-d', '--db-name', default="blast_results2.db", help='Name of the database (default: blast_results2.db)')
    parser_run.set_defaults(func=run_orthogroups)


    # 5. 实现鉴定四类基因的功能，并进行提取相关的基因
    parser_pangenes = subparsers.add_parser('pangenes', help='Process pangenes')
    parser_pangenes.add_argument('-f', '--file', required=True, help='Input file for syn list')
    parser_pangenes.add_argument('-c', '--cds', required=True, help='Input directory for CDS files')
    parser_pangenes.add_argument('-p', '--pep', required=True, help='Input directory for PEP files')
    parser_pangenes.set_defaults(func=process_pangenes)



    # process-gff 命令：单独处理 GFF 文件
    parser_gff = subparsers.add_parser('process-gff', help='Process raw GFF file')
    parser_gff.add_argument('-i', '--input-gff', required=True, help='Input raw GFF file')
    parser_gff.add_argument('-o', '--output-gff', required=True, help='Output processed GFF file')
    parser_gff.add_argument('-f', '--feature-type', default='mRNA', help='Feature type to filter (default: mRNA)')
    parser_gff.add_argument('-a', '--id-attribute-index', type=int, default=1, help='Index of gene ID in attributes (default: 1)')
    parser_gff.add_argument('-s', '--id-separator', default='=', help='Separator for gene ID (default: =)')
    parser_gff.add_argument('-p', '--species-prefix', required=True, help='Species prefix for gene IDs')
    parser_gff.set_defaults(func=process_gff)

    # process-seq 命令：根据处理后的 GFF 文件生成 PEP 或 CDS 文件
    parser_seq = subparsers.add_parser('process-seq', help='Generate processed PEP or CDS file from processed GFF')
    parser_seq.add_argument('-g', '--output-gff', required=True, help='Processed GFF file')
    parser_seq.add_argument('-i', '--input-seq', required=True, help='Input raw sequence file (PEP or CDS)')
    parser_seq.add_argument('-o', '--output-seq', required=True, help='Output processed sequence file (PEP or CDS)')
    parser_seq.add_argument('-gp', '--gene-id-position', type=int, default=1, help='Gene ID position in sequence file (default: 1)')
    parser_seq.add_argument('-ns', '--use-nested-split', action='store_true', help='Use nested split for gene ID (default: False)')
    parser_seq.add_argument('-nsp', '--nested-split-position', type=int, default=1, help='Nested split position (default: 1)')
    parser_seq.set_defaults(func=process_seq)

    # process-all 命令：直接处理原始 GFF、CDS、PEP 文件
    parser_all = subparsers.add_parser('process-all', help='Process raw GFF, CDS, and PEP files')
    parser_all.add_argument('-ig', '--input-gff', required=True, help='Input raw GFF file')
    parser_all.add_argument('-og', '--output-gff', required=True, help='Output processed GFF file')
    parser_all.add_argument('-ip', '--input-pep', required=True, help='Input raw PEP file')
    parser_all.add_argument('-op', '--output-pep', required=True, help='Output processed PEP file')
    parser_all.add_argument('-ic', '--input-cds', required=True, help='Input raw CDS file')
    parser_all.add_argument('-oc', '--output-cds', required=True, help='Output processed CDS file')
    parser_all.add_argument('-f', '--feature-type', default='mRNA', help='Feature type to filter (default: mRNA)')
    parser_all.add_argument('-a', '--id-attribute-index', type=int, default=1, help='Index of gene ID in attributes (default: 1)')
    parser_all.add_argument('-s', '--id-separator', default='=', help='Separator for gene ID (default: =)')
    parser_all.add_argument('-p', '--species-prefix', required=True, help='Species prefix for gene IDs')
    # PEP 文件的参数
    parser_all.add_argument('-pgp', '--pep-gene-id-position', type=int, default=1, help='Gene ID position in PEP file (default: 1)')
    parser_all.add_argument('-pns', '--pep-use-nested-split', action='store_true', help='Use nested split for gene ID in PEP file (default: False)')
    parser_all.add_argument('-pnsp', '--pep-nested-split-position', type=int, default=1, help='Nested split position in PEP file (default: 1)')
    # CDS 文件的参数
    parser_all.add_argument('-cgp', '--cds-gene-id-position', type=int, default=0, help='Gene ID position in CDS file (default: 0)')
    parser_all.add_argument('-cns', '--cds-use-nested-split', action='store_true', help='Use nested split for gene ID in CDS file (default: False)')
    parser_all.add_argument('-cnsp', '--cds-nested-split-position', type=int, default=1, help='Nested split position in CDS file (default: 1)')
    parser_all.set_defaults(func=process_all)


    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()



