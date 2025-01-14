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

### process-gff :

```
PanMCL process-gff -i GWHEUVW00000000.1.gff -o She.new.gff -p She 
```





