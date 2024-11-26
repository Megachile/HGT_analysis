#!/bin/bash
#SBATCH --job-name=blastp_wasp_fungal
#SBATCH --output=logs/blastp_wasp_fungal_%A_%a.out
#SBATCH --error=logs/blastp_wasp_fungal_%A_%a.err
#SBATCH --time=240:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --partition=ceti
#SBATCH --mail-type=ALL
#SBATCH --mail-user=akranz8174@unm.edu
#SBATCH --array=0-9%4

source ~/.bashrc
conda activate genomics
cd /export/martinsons/adam

echo "Starting job array ${SLURM_ARRAY_TASK_ID} at $(date)"
echo "Working directory: $PWD"
echo "BLAST version: $(blastp -version)"

# Create directories if they don't exist
mkdir -p temp/wasp_query_chunks
mkdir -p blast_results
mkdir -p logs

# Split query file if not already done and if this is the first array task
if [ $SLURM_ARRAY_TASK_ID -eq 0 ]; then
    if [ ! -f temp/wasp_query_chunks/chunk_0.faa ]; then
        echo "Splitting query file at $(date)"
        awk 'BEGIN {n=0;c=0} /^>/ {n++; if(n%1000==1){c++; file="temp/wasp_query_chunks/chunk_" int((n-1)/1000) ".fa$
    fi
fi

# Process chunk
chunk="temp/wasp_query_chunks/chunk_${SLURM_ARRAY_TASK_ID}.faa"
outfile="blast_results/results_wasp_fungal_${SLURM_ARRAY_TASK_ID}.out"

# Check if output already exists and has content
if [ -s "$outfile" ]; then
    echo "Output file already exists and has content. Skipping."
    exit 0
fi

# Check input exists
if [ ! -f "$chunk" ]; then
    echo "Error: Input file $chunk not found"
    exit 1
fi
echo "Input file exists and contains $(grep -c "^>" $chunk) sequences"

# Check database
echo "Checking database..."
if [ ! -f blast_dbs/fungal_insect_db.pin ]; then
    echo "Error: Database files not found"
    exit 1
fi
