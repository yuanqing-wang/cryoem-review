wget http://www.rcsb.org/pdb/files/$1.pdb
mv $1.pdb rec.pdb
count=0

# get the number of available gpus
n_cpus=$(nproc)

# ====================
# possible params here
# ====================
for ((idx=0; idx<=10; idx++)); do
for ((res=2; res<=10; res++)); do
for cs in 2.26 4.2; do \
for voltage in 200.0 300.0; do \
for ampcont in 0.10 0.12; do \
for defocus in 0.0 0.5 1.0 1.5 2.0 2.5 2.8; do \
for noiseamp in 0.3 0.4; do \
for noiseampwhite in 0.8 0.9; do \
for bfactor in 0.0 1.0 2.0 3.0; do

    # projection
    e2pdb2mrc.py rec.pdb $count'rec.mrc' --res=$res --center

    # translate and clip and project
    for ((dummy_idx; idx<=5; idx++)); do
      e2proc3d.py $count'rec.mrc' $count'rec_clipped.mrc' \
        --fftclip=500,500,500 \
        --trans=$(($RANDOM%100+1)),$(($RANDOM%100+1)),$((RANDOM%100+1))

      e2project3d.py $count'rec_clipped.mrc' --outfile=$count'rec_clean.mrcs' --orientgen=eman:delta=10 \
        --projector=standard --parallel=thread:$n_cpus
    done;

    # add noise
    e2proc2d.py $count'rec_clean.mrcs' $count'rec_noisy.mrcs' \
    --process=math.simulatectf:\
ampcont=$ampcont:\
apix=1.0:\
bfactor=$bfactor:\
cs=$cs:\
defocus=$defocus:\
noiseamp=$noiseamp:\
noiseampwhite=$noiseampwhite:\
voltage=$voltage

    # unstack and output to .png
    e2proc2d.py $count'rec_clean.mrcs' $count'rec_clean.png' --unstacking
    e2proc2d.py $count'rec_noisy.mrcs' $count'rec_noisy.png' --unstacking

    # increment
    count=$(($count+1))

    # clean up
    rm *.mrc
    rm *.mrcs
done; done; done; done; done; done; done; done; done
