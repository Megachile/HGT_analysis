
#!/bin/bash
#SBATCH --job-name=clean_genomes
#SBATCH --output=/export/martinsons/adam/logs/clean_genomes_%j.out
#SBATCH --error=/export/martinsons/adam/logs/clean_genomes_%j.err
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=1
#SBATCH --partition=ceti
#SBATCH --nodes=1
#SBATCH --exclude=taos01

# Initialize conda for bash
eval "$(conda shell.bash hook)"
conda activate genomics

# Print environment info for debugging
which python
python -V
conda env list
echo "Current conda env: $CONDA_DEFAULT_ENV"

# Rest of script...
SCRIPTS_DIR=/export/martinsons/adam/scripts
INPUT_DIR=/export/martinsons/adam/input_sequences
OUTPUT_DIR=/export/martinsons/adam/input_sequences/cleaned

# Process genomes
python ${SCRIPTS_DIR}/clean_genome.py \
    ${INPUT_DIR}/B_kinseyi_genome.fna \
    --output ${OUTPUT_DIR}/B_kinseyi_genome.cleaned.fna \
    --aggressive-clean \
    --standardize-case

python ${SCRIPTS_DIR}/clean_genome.py \
    ${INPUT_DIR}/Q_virginiana_genome.genome.fa \
    --output ${OUTPUT_DIR}/Q_virginiana_genome.cleaned.fa \
    --line-length 80

python ${SCRIPTS_DIR}/clean_genome.py \
    ${INPUT_DIR}/D_quercuslanigerum_genome.fna \
    --output ${OUTPUT_DIR}/D_quercuslanigerum_genome.cleaned.fna \
    --aggressive-clean \
    --standardize-case
