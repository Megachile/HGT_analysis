
#!/bin/bash
#SBATCH --job-name=download_bacterial_proteins
#SBATCH --output=download_bacterial_proteins.out
#SBATCH --error=download_bacterial_proteins.err
#SBATCH --time=12:00:00   
#SBATCH --mem=8G
#SBATCH --cpus-per-task=4
# Load necessary modules 
module load wget
module load gzip
# Set wd
cd /export/martinsons/adam

# Download bacterial protein sequences
wget ftp://ftp.ncbi.nlm.nih.gov/refseq/release/bacteria/bacteria..protein.faa.gz
# Uncompress all downloaded files
gunzip bacteria..protein.faa.gz
# Concatenate all protein files into a single file
cat bacteria..protein.faa > bacterial_proteins.faa
# Optionally, remove individual files to save space
rm bacteria..protein.faa
