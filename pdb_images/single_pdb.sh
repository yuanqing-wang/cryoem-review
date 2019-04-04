wget http://www.rcsb.org/pdb/files/$1.pdb
mv $1.pdb rec.pdb
count=0

# get the number of available gpus
n_cpus=$(nproc)

# ====================
# possible params here
# ====================
for ((idx=0; idx<=10; idx++)); do
for res in 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do \
for cs in 4.2 2.26; do \
for voltage in 200.0 300.0; do \
for ampcont in 0.10 0.12; do \
for defocus in 2.5 2.0 1.5 1.0; do \
for noiseamp in 0.01 0.02 0.03 0.04 0.05 0.06; do \
for noiseampwhite in 0.01 0.02 0.03 0.05 0.06; do \
for bfactor in 3.0 2.0 1.0 0.0; do

    # projection
    e2pdb2mrc.py rec.pdb $count'rec.mrc' --res=$res --center

    # translate and clip and project
    for ((dummy_idx=0; dummy_idx<=5; dummy_idx++)); do
      e2proc3d.py $count'rec.mrc' $count'rec_clipped.mrc' \
        --clip=500,500,500 \
        --trans=$((200-$RANDOM%400)),$((200-$RANDOM%400)),$((200-RANDOM%400))

      e2project3d.py $count'rec_clipped.mrc' --outfile=$count'rec_clean.mrcs' -a \
        --orientgen=eman:delta=10 \
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
    e2proc2d.py $count'rec_clean.mrcs' 'c-'$count'.png' --unstacking
    e2proc2d.py $count'rec_noisy.mrcs' 'r-'$count'.png' --unstacking

    # increment
    count=$(($count+1))

    # clean up
    rm *.mrc
    rm *.mrcs
done; done; done; done; done; done; done; done; done
