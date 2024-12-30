#!/bin/bash
#SBATCH --job-name=find_clusters
#SBATCH --output=/export/martinsons/adam/logs/find_clusters_%j.out
#SBATCH --error=/export/martinsons/adam/logs/find_clusters_%j.err
#SBATCH --time=4:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=1
#SBATCH --partition=ceti

# Load conda environment
source ~/.bashrc
conda activate genomics

# Set paths
SCRIPTS_DIR="/export/martinsons/adam/scripts"
MAPPED_DIR="/export/martinsons/adam/kmer_analysis/mapped"
OUTPUT_DIR="/export/martinsons/adam/kmer_analysis/clusters"

# Create output directory
mkdir -p ${OUTPUT_DIR}

# Process Q. virginiana clusters
echo "Finding clusters in Q. virginiana..."
python ${SCRIPTS_DIR}/find_clusters.py \
    ${MAPPED_DIR}/shared_kmers_qv.bam \
    ${OUTPUT_DIR}/qv_clusters \
    --min-kmers 3 \
    --min-length 100 \
    --max-gap 50 \
    --min-density 0.1

# Process B. kinseyi clusters
echo "Finding clusters in B. kinseyi..."
python ${SCRIPTS_DIR}/find_clusters.py \
    ${MAPPED_DIR}/shared_kmers_bk.bam \
    ${OUTPUT_DIR}/bk_clusters \
    --min-kmers 3 \
    --min-length 100 \
    --max-gap 50 \
    --min-density 0.1
