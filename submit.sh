#!/bin/bash
#PBS -N cpg_paths_generation
#PBS -l nodes=3:ppn=24
#PBS -o out.log
#PBS -q cpu7d

python main.py