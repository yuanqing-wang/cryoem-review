wget http://www.rcsb.org/pdb/files/$1.pdb
mv $1.pdb rec.pdb
count=0
n_cpus=$(nproc)

e2pdb2mrc.py rec.pdb rec.hdf --res=$res --center
e2project3d.py rec.hdf --outfile=rec_3d.hdf --orientgen=eman:delta=1 \
  --projector=standard --parallel=thread:$n_cpus
  
for ((idx=0; idx<=10; idx++)); do
for ((res=2; res<=10; res++)); do
for cs in 0.01 2.26; do \
for voltage in 200.0 300.0; do \
for ampcont in 0.06 0.08 0.10 0.12; do \
for defocus in 0.5 1.0 1.5 2.0 2.5; do \
for noiseamp in 0.1 0.2 0.3 0.4; do \
for noiseampwhite in 0.6 0.8 1.0 1.2; do \
for bfactor in 30, 1500; do \
    e2proc2d.py rec_3d.hdf rec_3d_noisy.hdf \
    --process=math.simulatectf:\
      ampcont=$ampcont:\
      apix=1.0:\
      bfactor=$bfactor:\
      cs=$cs:\
      defocus=$defocus:\
      noiseamp=$noiseamp:\
      noiseampwhite=:$noiseampwhite:\
      voltage=$voltage
    e2proc2d.py rec_3d_noisy.hdf rec_3d_noisy_unstacked.hdf --unstacking
    e2proc2d.py rec_3d_noisy_unstacked-*.hdf '$count'_@.png
    $count += 1

done; done; done; done; done; done; done; done; done
