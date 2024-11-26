#!/bin/bash
#SBATCH --job-name=prep_fungal_db
#SBATCH --output=logs/prep_fungal_%j.out
#SBATCH --error=logs/prep_fungal_%j.err
#SBATCH --time=12:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --partition=ceti

# Load modules
source ~/.bashrc
conda activate genomics

cd /export/martinsons/adam

# Create directories
mkdir -p fungal_data logs blast_dbs

# Download fungal proteins
cd fungal_data
echo "Starting downloads at $(date)"

# Get specific files (there are usually 4-5 of these)
wget https://ftp.ncbi.nlm.nih.gov/refseq/release/fungi/fungi.1.protein.faa.gz
wget https://ftp.ncbi.nlm.nih.gov/refseq/release/fungi/fungi.2.protein.faa.gz
wget https://ftp.ncbi.nlm.nih.gov/refseq/release/fungi/fungi.3.protein.faa.gz
wget https://ftp.ncbi.nlm.nih.gov/refseq/release/fungi/fungi.4.protein.faa.gz
wget https://ftp.ncbi.nlm.nih.gov/refseq/release/fungi/fungi.5.protein.faa.gz

echo "Downloads completed at $(date)"

# Decompress and combine
gunzip fungi.*.protein.faa.gz
cat fungi.*.protein.faa > combined_fungal.faa

echo "Files combined at $(date)"

# Add plant references
cat combined_fungal.faa \
    ../input_sequences/GCF_000001735.4_TAIR10.1_protein.faa \
    ../input_sequences/GCF_000002775.5_P.trichocarpa_v4.1_protein.faa \
    > ../fungal_plant_reference.faa

echo "Creating BLAST database at $(date)"

# Create BLAST database
cd ..
makeblastdb -in fungal_plant_reference.faa \
           -dbtype prot \
           -out blast_dbs/fungal_plant_db

echo "Process completed at $(date)"
