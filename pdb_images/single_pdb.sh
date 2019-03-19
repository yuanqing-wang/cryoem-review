wget http://www.rcsb.org/pdb/files/$1.pdb
mv $1.pdb rec.pdb
e2pdb2mrc.py rec.pdb rec.hdf --res=5 --center
e2project3d.py rec.hdf --outfile=rec_3d.hdf --orientgen=eman:delta=5 --projector=standard
e2proc2d.py rec_3d.hdf rec_3d_noisy.hdf \
--process=math.simulatectf:ampcont=0.1:apix=1.0:bfactor=3.0:cs=4.2:defocus=2.8:noiseamp=0.3:noiseampwhite=0.8:voltage=200.0
e2proc2d.py rec_3d_noisy.hdf rec_3d_noisy_unstacked.hdf --unstacking
e2proc2d.py rec_3d_noisy_unstacked-*.hdf @.png
