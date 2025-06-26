#!/usr/bin/env python3
"""
Swiss-Prot annotation with DIAMOND.

- 自动检测系统diamond命令；本地无则自动下载官方预编译版到脚本目录（支持直接解压为单文件）。
- 只要脚本目录下有 uniprot_sprot.dmnd（索引），即可直接注释分析，无需 fasta。
- 若未找到 dmnd，才需 fasta 建库，优先用 --dbaa 指定的 fasta，否则自动检测/下载到脚本目录。
"""

import argparse
import subprocess
import sys
import shutil
import gzip
import urllib.request
from pathlib import Path
import platform
import tarfile

UNIPROT_SPROT_URL = "https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz"

def run(cmd):
    """执行命令行并检测返回值"""
    proc = subprocess.Popen(cmd, shell=True)
    proc.communicate()
    if proc.returncode != 0:
        sys.exit(f"[ERROR] Command failed: {cmd}")

def download_with_progress(url, out_path):
    """下载url到out_path，并显示实时进度条"""
    with urllib.request.urlopen(url) as response, open(out_path, 'wb') as out_file:
        total = response.getheader('Content-Length')
        if total is None:
            shutil.copyfileobj(response, out_file)
            sys.stdout.write('\n')
            return
        total = int(total.strip())
        downloaded = 0
        block_size = 8192
        while True:
            buffer = response.read(block_size)
            if not buffer:
                break
            out_file.write(buffer)
            downloaded += len(buffer)
            done = int(50 * downloaded / total)
            percent = (downloaded / total) * 100
            sys.stdout.write('\r[{}{}] {:.1f}% ({:.1f} MB/{:.1f} MB)'.format(
                '█' * done, ' ' * (50-done), percent, downloaded/(1024**2), total/(1024**2)))
            sys.stdout.flush()
        sys.stdout.write('\n')

def download_and_decompress(url, fasta_path):
    gz_path = fasta_path.with_suffix('.fasta.gz')
    print(f"[+] Downloading {url} ...")
    download_with_progress(url, gz_path)
    print(f"[+] Decompressing {gz_path} ...")
    with gzip.open(gz_path, 'rb') as f_in, open(fasta_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    gz_path.unlink()

def extract_diamond(tgz_path, script_dir):
    with tarfile.open(tgz_path, "r:gz") as tar:
        diamond_member = None
        for m in tar.getmembers():
            if m.isfile() and m.name.endswith('diamond'):
                diamond_member = m
                break
        if not diamond_member:
            sys.exit("[ERROR] DIAMOND binary not found in tarball!")
        tar.extract(diamond_member, path=script_dir)
        diamond_extract_path = script_dir / diamond_member.name
        target_diamond_path = script_dir / "diamond"
        # 移动到脚本目录下
        if diamond_extract_path.resolve() != target_diamond_path.resolve():
            shutil.move(str(diamond_extract_path), str(target_diamond_path))
        target_diamond_path.chmod(0o755)
    tgz_path.unlink()
    print(f"[+] DIAMOND downloaded to {target_diamond_path}")
    return str(target_diamond_path)

def find_or_download_diamond(script_dir):
    diamond_path = shutil.which("diamond")
    if diamond_path:
        return diamond_path
    local_diamond = script_dir / "diamond"
    if local_diamond.exists():
        return str(local_diamond)
    print("[+] DIAMOND not found, downloading precompiled binary ...")
    system = platform.system()
    if system == "Linux":
        url = "https://github.com/bbuchfink/diamond/releases/latest/download/diamond-linux64.tar.gz"
    elif system == "Darwin":
        url = "https://github.com/bbuchfink/diamond/releases/latest/download/diamond-macos.tar.gz"
    else:
        sys.exit("[ERROR] Automatic DIAMOND download is only supported for Linux/macOS. Please install manually.")

    tgz_path = script_dir / "diamond_download.tgz"
    download_with_progress(url, tgz_path)
    return extract_diamond(tgz_path, script_dir)

def main():
    parser = argparse.ArgumentParser(
        description="Annotate proteins against Swiss-Prot with DIAMOND"
    )
    parser.add_argument("-i", "--query", required=True,
                        help="Protein FASTA to annotate")
    parser.add_argument("-o", "--prefix", default="sprot_out",
                        help="Output prefix (default: sprot_out)")
    parser.add_argument("--id", type=float, default=30,
                        help="Minimum %% identity (default 30)")
    parser.add_argument("--cov", type=float, default=50,
                        help="Minimum query coverage (default 50)")
    parser.add_argument("--threads", type=int, default=8,
                        help="DIAMOND threads (default 8)")
    parser.add_argument("--dbaa", type=str, default=None,
                        help="Swiss-Prot FASTA file for building database index if needed (default: auto-download if missing in script dir)")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    diamond_bin = find_or_download_diamond(script_dir)
    db_dmnd = script_dir / "uniprot_sprot.dmnd"
    out_tsv = Path(f"{args.prefix}.tsv")
    idfile = Path(f"{args.prefix}.format.tsv")

    if not db_dmnd.exists():
        if args.dbaa:
            db_fasta = Path(args.dbaa).resolve()
            if not db_fasta.exists():
                sys.exit(f"[ERROR] Specified Swiss-Prot file {db_fasta} not found.")
        else:
            db_fasta = script_dir / "uniprot_sprot.fasta"
            if not db_fasta.exists():
                print("[+] Swiss-Prot FASTA not found, downloading from UniProt ...")
                download_and_decompress(UNIPROT_SPROT_URL, db_fasta)
        print(f"[+] Building DIAMOND DB at {db_dmnd} using {db_fasta} ...")
        run(f"{diamond_bin} makedb --in {db_fasta} -d {db_dmnd}")
    else:
        print(f"[+] Found index {db_dmnd}, skip building.")

    print("[+] Running DIAMOND ...")
    diamond_cmd = (
        f"{diamond_bin} blastp -d {db_dmnd} -q {args.query} -o {out_tsv} "
        f"--outfmt 6 qseqid sseqid pident length evalue bitscore stitle "
        f"--max-target-seqs 1 --evalue 1e-5 --id {args.id} "
        f"--query-cover {args.cov} --threads {args.threads}"
    )
    run(diamond_cmd)

    total = sum(1 for _ in open(args.query) if _.startswith(">"))
    annotated = len({line.split("\t")[0] for line in open(out_tsv)})
    rate = annotated / total * 100 if total else 0
    with open(out_tsv) as fin, open(idfile, "w") as fout:
        fout.write("ProteinID\tDB\tAccessionNumber\tEntryName\tDescription\tOrganismSpecies\n")
        for line in fin:
            parts = line.rstrip("\n").split("\t")
            qid = parts[0]
            title = parts[6]

            db, acc, entryname = ("", "", "")
            if title.startswith("sp|") or title.startswith("tr|"):
                fields = title.split(" ", 1)
                header = fields[0]
                description = fields[1].split("OS=")[0].strip() if "OS=" in fields[1] else fields[1].strip()
                organism = fields[1].split("OS=")[1].strip() if "OS=" in fields[1] else ""
                header_parts = header.split("|")
                if len(header_parts) == 3:
                    db, acc, entryname = header_parts
            else:
                description = title.split("(")[0].strip()
                organism = ""

            fout.write(f"{qid}\t{db}\t{acc}\t{entryname}\t{description}\t{organism}\n")

    print("\n=== Swiss-Prot annotation summary ===")
    print(f"Input proteins      : {total}")
    print(f"Annotated proteins  : {annotated}")
    print(f"Annotation rate     : {rate:.2f}%")
    print(f"Result table        : {out_tsv}")
    print(f"Annotated ID list   : {idfile}")

if __name__ == "__main__":
    main()
