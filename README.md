# swissprot-auto-annotator/自动swissprot注释工具
**swissprot-auto-annotator** is an easy-to-use, automated Swiss-Prot annotation tool for protein FASTA files.  
It leverages the ultra-fast [DIAMOND](https://github.com/bbuchfink/diamond) aligner and can automatically handle database downloads, index building, and batch annotation.Suitable for beginners who have just started learning bioinformatics.

**Features:**
- One-step Swiss-Prot annotation of protein FASTA files
- Automatic download of DIAMOND and the latest Swiss-Prot database (or use your own)
- Built-in support for database indexing and multi-threaded annotation
- Customizable identity and coverage thresholds
- Clean, user-friendly output for downstream analysis

**Typical usage scenario:**  
Quickly annotate large-scale protein datasets in microbial genomics, metagenomics, or custom pipelines with minimal configuration.

---

**swissprot-auto-annotator** 是一款自动化的 Swiss-Prot 蛋白质注释脚本工具，面向蛋白质FASTA文件的快速批量注释。  
本工具集成了高速的 [DIAMOND](https://github.com/bbuchfink/diamond) 比对引擎，可自动下载和管理 Swiss-Prot 数据库、构建索引，并实现批量注释。适合刚接触生物信息学的初学者使用。  

**主要特点：**
- 一步式完成蛋白FASTA文件的 Swiss-Prot 功能注释
- 自动下载 DIAMOND 程序和最新版 Swiss-Prot 数据库（也可使用自有数据库/索引）
- 自动构建数据库索引、支持多线程注释
- 支持自定义比对相似度和覆盖度参数
- 输出结构化、便于后续分析的数据表

**典型应用场景：**  
适用于微生物基因组、宏基因组或自定义流程中大批量蛋白质序列的高效功能注释。

## Usage / 使用方法

### 1. Quick Start / 快速开始

```bash
python3 annotate_sprot.py --help
```

### 2. Basic Usage / 基本用法

```bash
python3 annotate_sprot.py -i your_protein.faa
```

### 3. Main Parameters / 主要参数

| Parameter / 参数 | Description / 说明 | Default / 默认值 |
|------------------|--------------------|------------------|
| `-i, --query`    | Input protein FASTA file / 输入蛋白FASTA文件 | *required / 必填* |
| `-o, --prefix`   | Output prefix / 输出前缀 | `sprot_out` |
| `--id`           | Minimum percent identity / 最低相似度百分比 | `30` |
| `--cov`          | Minimum query coverage (%) / 最低覆盖率 | `50` |
| `--threads`      | Number of threads / 线程数 | `8` |
| `--dbaa`         | Swiss-Prot FASTA file path / Swiss-Prot FASTA路径 | 自动下载（如未提供） |

### 4. Example / 运行示例

```bash
python3 annotate_sprot.py \
  -i example_proteins.faa \
  -o my_annotation \
  --id 50 \
  --cov 75 \
  --threads 16
```

### 5. Output Description / 输出说明

- `${prefix}.tsv`  
  Raw DIAMOND output in tab-delimited format / DIAMOND 原始注释结果

- `${prefix}.format.tsv`  
  Formatted annotation table: `ProteinID`, `DB`, `AccessionNumber`, `EntryName`, `Description`, `OrganismSpecies`  
  标准化注释表，便于后续分析

