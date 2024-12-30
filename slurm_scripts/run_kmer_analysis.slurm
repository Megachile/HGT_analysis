#!/bin/bash
#SBATCH --job-name=kmer_analysis
#SBATCH --output=/export/martinsons/adam/logs/kmer_analysis_%j.out
#SBATCH --error=/export/martinsons/adam/logs/kmer_analysis_%j.err
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
#SBATCH --partition=ceti
#SBATCH --nodes=1
#SBATCH --exclude=taos01  # exclude the down node

# Set paths
GENOME_DIR="/export/martinsons/adam/input_sequences/cleaned"
KMER_DIR="/export/martinsons/adam/kmer_analysis/kmers"
SHARED_DIR="/export/martinsons/adam/kmer_analysis/shared"
MAPPED_DIR="/export/martinsons/adam/kmer_analysis/mapped"
TEMP_DIR="/export/martinsons/adam/kmer_analysis/temp"

# Ensure temp directory exists and is empty
rm -rf ${TEMP_DIR}/*
mkdir -p ${TEMP_DIR}

echo "Starting k-mer analysis at $(date)"

# Generate k-mers for each genome
echo "Generating k-mers for Q. virginiana..."
kmc -k31 -m32 -fm -ci2 -cs65535 \
    ${GENOME_DIR}/Q_virginiana_genome.cleaned.fa \
    ${KMER_DIR}/qv_kmers \
    ${TEMP_DIR}

echo "Generating k-mers for B. kinseyi..."
kmc -k31 -m32 -fm -ci2 -cs65535 \
    ${GENOME_DIR}/B_kinseyi_genome.cleaned.fna \
    ${KMER_DIR}/bk_kmers \
    ${TEMP_DIR}

# Find shared k-mers
echo "Finding shared k-mers..."
kmc_tools simple ${KMER_DIR}/qv_kmers ${KMER_DIR}/bk_kmers intersect ${SHARED_DIR}/shared_kmers

# Convert shared k-mers to FASTA format for mapping
echo "Converting shared k-mers to FASTA..."
kmc_tools transform ${SHARED_DIR}/shared_kmers dump -s ${SHARED_DIR}/shared_kmers.txt
awk '{print ">kmer_" NR "\n" $1}' ${SHARED_DIR}/shared_kmers.txt > ${SHARED_DIR}/shared_kmers.fasta

# Index both genomes for BWA
echo "Indexing genomes..."
bwa index ${GENOME_DIR}/Q_virginiana_genome.cleaned.fa
bwa index ${GENOME_DIR}/B_kinseyi_genome.cleaned.fna

# Map shared k-mers back to Q. virginiana genome
echo "Mapping shared k-mers to Q. virginiana genome..."
bwa mem -t 8 ${GENOME_DIR}/Q_virginiana_genome.cleaned.fa \
    ${SHARED_DIR}/shared_kmers.fasta > ${MAPPED_DIR}/shared_kmers_qv.sam

# Map shared k-mers back to B. kinseyi genome
echo "Mapping shared k-mers to B. kinseyi genome..."
bwa mem -t 8 ${GENOME_DIR}/B_kinseyi_genome.cleaned.fna \
    ${SHARED_DIR}/shared_kmers.fasta > ${MAPPED_DIR}/shared_kmers_bk.sam

# Convert SAMs to sorted BAMs
echo "Converting SAMs to BAMs..."
# Q. virginiana BAM
samtools view -bS ${MAPPED_DIR}/shared_kmers_qv.sam | \
    samtools sort -o ${MAPPED_DIR}/shared_kmers_qv.bam -
samtools index ${MAPPED_DIR}/shared_kmers_qv.bam

# B. kinseyi BAM
samtools view -bS ${MAPPED_DIR}/shared_kmers_bk.sam | \
    samtools sort -o ${MAPPED_DIR}/shared_kmers_bk.bam -
samtools index ${MAPPED_DIR}/shared_kmers_bk.bam

# Generate coverage statistics for both genomes
echo "Generating coverage statistics..."
samtools depth -a ${MAPPED_DIR}/shared_kmers_qv.bam > ${MAPPED_DIR}/coverage_qv.txt
samtools depth -a ${MAPPED_DIR}/shared_kmers_bk.bam > ${MAPPED_DIR}/coverage_bk.txt

# Basic analysis of coverage for both genomes
echo "Analyzing coverage..."
echo "Q. virginiana coverage:" > ${MAPPED_DIR}/coverage_summary.txt
awk '{sum+=$3; if($3>0) regions++} END {print "Average coverage: " sum/NR "\nRegions with coverage: " regions}' \
    ${MAPPED_DIR}/coverage_qv.txt >> ${MAPPED_DIR}/coverage_summary.txt

echo -e "\nB. kinseyi coverage:" >> ${MAPPED_DIR}/coverage_summary.txt
awk '{sum+=$3; if($3>0) regions++} END {print "Average coverage: " sum/NR "\nRegions with coverage: " regions}' \
    ${MAPPED_DIR}/coverage_bk.txt >> ${MAPPED_DIR}/coverage_summary.txt

echo "Analysis complete at $(date)"
