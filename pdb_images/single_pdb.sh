wget http://www.rcsb.org/pdb/files/$1.pdb
mv $1.pdb rec.pdb
count=0
n_cpus=$(nproc)


for ((idx=0; idx<=10; idx++)); do
for ((res=2; res<=10; res++)); do
for cs in 0.01 2.26; do \
for voltage in 200.0 300.0; do \
for ampcont in 0.06 0.08 0.10 0.12; do \
for defocus in 0.5 1.0 1.5 2.0 2.5; do \
for noiseamp in 0.1 0.2 0.3 0.4; do \
for noiseampwhite in 0.6 0.7 0.8; do \
for bfactor in 0.0 1.0 2.0 3.0; do

    # projection
    e2pdb2mrc.py rec.pdb rec.hdf --res=$res --center
    e2project3d.py rec.hdf --outfile=rec_2d_stack.hdf --orientgen=eman:delta=1 \
     --projector=standard --parallel=thread:$n_cpus
    e2proc2d.py rec_2d_stack.hdf rec_2d_unstack.hdf --unstacking
    
    # convert to .png and add noise
    for f in rec_2d_unstack-*.hdf; do   
      # randomly transform the image
      # dx=$(($RANDOM%200+500))
      # dy=$(($RANDOM%200+500))
      # scale='0.'$(($RANDOM%30+30))
      e2proc2d.py $f $count'.hdf' # --clip=1024,1024,$dx,$dy --scale=$scale
      e2proc2d.py $count'.hdf' $count'_clean.png'
      e2proc2d.py $count'.hdf' $count'_noisy.png' \
      --process=math.simulatectf:\
ampcont=$ampcont:\
apix=1.0:\
bfactor=$bfactor:\
cs=$cs:\
defocus=$defocus:\
noiseamp=$noiseamp:\
noiseampwhite=$noiseampwhite:\
voltage=$voltage
      count=$(($count+1))

      # delete stuff

done;
  rm *.hdf
done; done; done; done; done; done; done; done; done
