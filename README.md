# Sandcastle

Sandbox for testing attack and defense tools

```
sudo docker network create -d macvlan \
  --subnet=192.168.101.0/24 \
  --gateway=192.168.101.254 \
  -o parent=enp4s0 \
  global_macvlan_net
```

```
sudo ip link add ctflan link eth0 type macvlan mode bridge
sudo ip addr add 192.168.100.100/23 dev ctflan
sudo ip link set ctflan up
```