# My Command Line Tool

A command-line tool for pan-genome analysis using MCL algorithm.

## Installation

You can install this tool using pip:

```bash
pip install PanMCL
conda install PanMCL

## Usage
PanMCL
    runbd               Run BLAST or DIAMOND for sequence alignment
    runinter            Run InterProScan for sequence analysis
    pangenes            Process pangenes
    process-gff         Process raw GFF file
    process-seq         Generate processed PEP or CDS file from processed GFF
    process-all         Process raw GFF, CDS, and PEP files


PanMCL process-gff -i GWHEUVW00000000.1.gff -o She.new.gff -p She

```

## Usage

```
PanMCL:
    runbd               Run BLAST or DIAMOND for sequence alignment
    runinter            Run InterProScan for sequence analysis
    pangenes            Process pangenes
    process-gff         Process raw GFF file
    process-seq         Generate processed PEP or CDS file from processed GFF
    process-all         Process raw GFF, CDS, and PEP files
```

## 1. `process-gff` 命令：单独处理 GFF 文件

`process-gff` 命令用于处理原始的 GFF 文件，并生成处理后的 GFF 文件。

### 参数说明

- `-i`, `--input-gff` (**必需**):
  指定输入的原始 GFF 文件路径。

- `-o`, `--output-gff` (**必需**):
  指定输出的处理后的 GFF 文件路径。

- `-f`, `--feature-type` (默认值: `mRNA`):
  指定要过滤的特征类型。默认情况下，工具会处理 GFF 文件中的 `mRNA` 特征。

- `-a`, `--id-attribute-index` (默认值: `1`):
  指定基因 ID 在 GFF 文件属性字段中的索引位置。默认值为 `1`，表示基因 ID 位于属性字段的第一个位置。

- `-s`, `--id-separator` (默认值: `=`):
  指定基因 ID 的分隔符。默认值为 `=`，表示基因 ID 的格式为 `ID=gene_id`。

- `-p`, `--species-prefix` (**必需**):
  指定物种前缀，该前缀将添加到基因 ID 前面，以生成唯一的基因标识符。

- ### 示例

```
PanMCL process-gff -i GWHEUVW00000000.1.gff -o She.new.gff -p She 
or
PanMCL process-gff -i GWHEUVW00000000.1.gff -o She.new.gff -p She -f mRNA -a 1 -s = 
```

## 2. `process-seq` 命令：根据处理后的 GFF 文件生成 PEP 或 CDS 文件

`process-seq` 命令用于根据处理后的 GFF 文件生成处理后的 PEP 或 CDS 文件。

### 参数说明

- `-g`, `--output-gff` (**必需**):
  指定处理后的 GFF 文件路径。
- `-i`, `--input-seq` (**必需**):
  指定输入的原始序列文件路径（PEP 或 CDS 文件）。
- `-o`, `--output-seq` (**必需**):
  指定输出的处理后的序列文件路径（PEP 或 CDS 文件）。
- `-gp`, `--gene-id-position` (默认值: `0`):
  指定基因 ID 在序列文件中的位置。默认值为 `0`，表示基因 ID 位于序列文件的第一列。
- `-ns`, `--use-nested-split` (默认值: `False`):
  指定是否使用嵌套分割来提取基因 ID。默认情况下，工具不会使用嵌套分割。
- `-nsp`, `--nested-split-position` (默认值: `1`):
  指定嵌套分割的位置。默认值为 `1`，表示在嵌套分割后的第一个位置提取基因 ID。

### 示例

```
PanMCL process-seq -g She.new.gff -i GWHEUVW00000000.1.Protein.faa -o She.pep
PanMCL process-seq -g She.new.gff -i GWHEUVW00000000.1.Protein.faa -o She.pep -gp 0 -ns -nsp 1

or
PanMCL process-seq -g She.new.gff -i GWHEUVW00000000.1.CDS.fasta -o She.cds -gp 0 -ns -nsp 1
```

