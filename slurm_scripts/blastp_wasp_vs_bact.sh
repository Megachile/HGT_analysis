#!/bin/bash
#SBATCH --job-name=blastp_wasp_vs_bact
#SBATCH --output=logs/blastp_wasp_vs_bact_%A_%a.out
#SBATCH --error=logs/blastp_wasp_vs_bact_%A_%a.err
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

# Process chunk
chunk="temp/wasp_query_chunks/chunk_${SLURM_ARRAY_TASK_ID}.faa"
if [ -f "$chunk" ]; then
    echo "Starting BLAST for chunk ${SLURM_ARRAY_TASK_ID} at $(date)"
    echo "Chunk file size: $(ls -lh $chunk)"

    blastp -query $chunk \
           -db blast_dbs/bacterial_db \
           -out blast_results/results_wasp_bact_${SLURM_ARRAY_TASK_ID}.out \
           -outfmt 6 \
           -evalue 1e-5 \
           -num_threads $SLURM_CPUS_PER_TASK

    echo "BLAST complete for chunk ${SLURM_ARRAY_TASK_ID} at $(date)"
else
    echo "Error: Chunk file $chunk not found"
    exit 1
fi

# Submit cleanup only after successful completion of all array jobs
if [ $SLURM_ARRAY_TASK_ID -eq 0 ]; then
    echo "Submitting cleanup job"
    echo '#!/bin/bash
    cd /export/martinsons/adam
    cat blast_results/results_wasp_bact_*.out > blast_results/B_kinseyi_vs_bacterial.out' > cleanup_wasp_bact.sh

    sbatch --dependency=afterany:${SLURM_ARRAY_JOB_ID} cleanup_wasp_bact.sh
fi

echo "Job array ${SLURM_ARRAY_TASK_ID} finished at $(date)"
