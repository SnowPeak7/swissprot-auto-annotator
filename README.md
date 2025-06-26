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

