#! /bin/sh

source .rr_sim/bin/activate
for velocity_ratio in $(seq 1 0.1 2); do
	echo "Current velocity ratio: $velocity_ratio";
	python coupling_simulation.py max-amp-vs-coupling-length -i 10000 -d 1000 -e 0 -v 2.5 -r $velocity_ratio -e 1 --coupling-step 0.001 --max-coupling-length 6.5;
	echo "\n\n";
done
