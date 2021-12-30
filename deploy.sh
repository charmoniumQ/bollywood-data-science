#!/usr/bin/env sh

start=5400
step=700
max=7

for i in `seq 0 $max`; do
	gcloud beta compute --project=scratchf instances create "instance-${i}" --zone=us-central1-a --machine-type=f1-micro --subnet=default --network-tier=PREMIUM --maintenance-policy=MIGRATE --service-account=743103393586-compute@developer.gserviceaccount.com --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append --image=ubuntu-2004-focal-v20200609 --image-project=ubuntu-os-cloud --boot-disk-size=10GB --boot-disk-type=pd-standard --boot-disk-device-name=instance-0 --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --reservation-affinity=any &
done
wait

for i in `seq 0 $max`; do
	while ! gcloud compute ssh "instance-${i}" -- "echo hi"; do
		sleep 5
	done
done

for i in `seq 0 $max`; do
	gcloud compute scp --recurse $(ls) "instance-${i}": &
done
wait

for i in `seq 0 $max`; do
	gcloud compute ssh "instance-${i}" -- "sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv && pip3 install poetry && python3 -m poetry install && python3 -m poetry run python3 -m bollywood_data_science.main $((i*step+start)) $(((i+1)*step+start))" &
done
wait

for i in `seq 0 $max`; do
	gcloud compute scp "instance-${i}":tmp/bollywood_data_science.imdb_graph.imdb_graph/'*' tmp/bollywood_data_science.imdb_graph.imdb_graph/ &
done
wait

# for i in `seq 0 $max`; do
# 	gcloud compute instances delete "instance-${i}" &
# done
# wait
