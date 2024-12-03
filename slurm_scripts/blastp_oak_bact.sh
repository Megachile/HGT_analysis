#!/bin/bash
#SBATCH --job-name=blastp_oak_bact
#SBATCH --output=logs/blastp_oak_bact_%A_%a.out
#SBATCH --error=logs/blastp_oak_bact_%A_%a.err
#SBATCH --time=240:00:00
#SBATCH --mem=64G
#SBATCH --cpus-per-task=16
#SBATCH --partition=ceti
#SBATCH --array=0-9%4
#SBATCH --mail-type=ALL
#SBATCH --mail-user=akranz8174@unm.edu

source ~/.bashrc
conda activate genomics

cd /export/martinsons/adam

# Create directories
mkdir -p temp/oak_query_chunks
mkdir -p blast_results

# Initial setup by task 0
if [ $SLURM_ARRAY_TASK_ID -eq 0 ]; then
    # Combine oak reference with plant controls
    cat input_sequences/Q_virginiana_protein_prefixed.faa \
        input_sequences/GCF_000001735.4_TAIR10.1_protein.faa \
        input_sequences/GCF_000002775.5_P.trichocarpa_v4.1_protein.faa > oak_plant_reference.faa
    
    # Create BLAST database
    makeblastdb -in oak_plant_reference.faa -dbtype prot -out blast_dbs/oak_bact_db

    # Split query file
    if [ ! -f temp/oak_query_chunks/chunk_0.faa ]; then
        echo "Splitting query file at $(date)"
        awk 'BEGIN {n=0;c=0} /^>/ {n++; if(n%1000==1){c++; file="temp/oak_query_chunks/chunk_" int((n-1)/1000) ".faa"}} {print > file}' input_sequences/Q_virginiana_protein_prefixed.faa
    fi
fi

# Process chunk
chunk="temp/oak_query_chunks/chunk_${SLURM_ARRAY_TASK_ID}.faa"
if [ -f "$chunk" ]; then
    echo "Starting BLAST for chunk ${SLURM_ARRAY_TASK_ID} at $(date)"
    
    blastp -query $chunk \
           -db blast_dbs/oak_bact_db \
           -out blast_results/results_oak_bact_${SLURM_ARRAY_TASK_ID}.out \
           -outfmt 6 \
           -evalue 1e-5 \
           -num_threads $SLURM_CPUS_PER_TASK
    
    echo "BLAST complete for chunk ${SLURM_ARRAY_TASK_ID} at $(date)"
else
    echo "Error: Chunk file $chunk not found"
    exit 1
fi

# Submit cleanup after all array jobs complete
if [ $SLURM_ARRAY_TASK_ID -eq 0 ]; then
    echo "Submitting cleanup job"
    echo '#!/bin/bash
    cd /export/martinsons/adam
    cat blast_results/results_oak_bact_*.out > blast_results/Q_virginiana_vs_bacterial.out
    rm -r temp/oak_query_chunks
    rm oak_plant_reference.faa
    rm blast_dbs/oak_bact_db.*' > cleanup_oak_bact.sh
    
    sbatch --dependency=afterany:${SLURM_ARRAY_JOB_ID} cleanup_oak_bact.sh
fi
