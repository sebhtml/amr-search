#!/bin/bash

user=ubuntu
ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i $HOME/magellan.pem"

# create an instance
# Ubuntu 14.04
# i2.2xlarge.sd is 20
nova boot --flavor i2.2xlarge.sd --image a45ceb7b-cd09-4dd3-a9bf-e2acf0376051 --key-name Magellan \
                          --security-groups default name-1234 &> output

# wait for the instance to be active
id=$(grep " id " output | awk '{print $4}')

nova rename $id ardm-worker-$id

while test $(nova show $id | grep ACTIVE | wc -l) -ne 1
do
    sleep 1
done

nova show $id > output

address=$(nova show $id|grep network|awk '{print $5}')

echo "instance $id has address $address"

# wait a bit because there is no route to host..
#sleep 10

# wait until there is no error such as
# - no route to host
# - connection refused
# In an ideal world this is not required.
while true
do
    ssh $ssh_options $user@$address date
    exit_status=$?

    if test $exit_status -eq 0
    then
        break
    fi
done &> boot-$id.log

echo "instance $id is ready"

# install software
cat worker/install-requirements.sh | ssh $ssh_options $user@$address

# copy private assets
scp $ssh_options -r ~/ardm-assets $user@$address:/mnt/worker

# start the daemon.
ssh $ssh_options $user@$address /mnt/worker/amr-search/worker/start.sh

echo "Provisioned instance"

echo "-> uuid= $id addr= $address status= run-daemon"
