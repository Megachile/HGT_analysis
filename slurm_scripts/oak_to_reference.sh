#!/bin/bash
#SBATCH --job-name=blastp_oak_ref
#SBATCH --output=logs/blastp_oak_%A_%a.out
#SBATCH --error=logs/blastp_oak_%A_%a.err
#SBATCH --time=240:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
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

# Split query file if not already done
if [ $SLURM_ARRAY_TASK_ID -eq 0 ]; then
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
          -db blast_dbs/wasp_plant_db \
          -out blast_results/results_oak_ref_${SLURM_ARRAY_TASK_ID}.out \
          -outfmt 6 \
          -evalue 1e-5 \
          -num_threads $SLURM_CPUS_PER_TASK
   
   echo "BLAST complete for chunk ${SLURM_ARRAY_TASK_ID} at $(date)"
else
   echo "Error: Chunk file $chunk not found"
   exit 1
fi

# Submit cleanup job after all array jobs complete
if [ $SLURM_ARRAY_TASK_ID -eq 0 ]; then
   echo "Submitting cleanup job"
   echo '#!/bin/bash
   cd /export/martinsons/adam
   cat blast_results/results_oak_ref_*.out > blast_results/Q_virginiana_vs_wasp_plant.out
   rm -r temp/oak_query_chunks' > cleanup_oak_ref.sh
   
   sbatch --dependency=afterany:${SLURM_ARRAY_JOB_ID} cleanup_oak_ref.sh
fi
