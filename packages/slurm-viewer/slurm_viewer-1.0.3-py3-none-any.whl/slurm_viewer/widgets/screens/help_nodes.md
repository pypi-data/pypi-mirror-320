The following needs to be known about the "Nodes" tab:
 - This tab uses the `scontrol --all show nodes` command
 - The GPU(Tot), GPU(Alloc), GPU(Avail) columns are calculated by slurm-viewer and are not tags available by default.
 - The Mem(Tot) is not always equivalent to Men (Alloc) + Mem(Avail) due to the way slurm reports memory.