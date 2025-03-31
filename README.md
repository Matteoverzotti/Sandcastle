# Sandcastle
Sandbox for testing attack and defense tools

## User

```
sudo docker network create -d macvlan \
  --subnet=192.168.100.0/24 \
  --gateway=192.168.100.254 \
  -o parent=enp4s0 \
  user_app1_net
```

## Bot

```
sudo docker network create -d macvlan \
  --subnet=192.168.101.0/24 \
  --gateway=192.168.101.254 \
  -o parent=enp4s0 \
  bot1_app1_net
```

```
sudo ip link add macvlan0 link eth0 type macvlan mode bridge
sudo ip addr add 192.168.100.100/24 dev macvlan0
sudo ip link set macvlan0 up

sudo ip link add macvlan101 link enp4s0 type macvlan mode bridge
sudo ip addr add 192.168.101.250/24 dev macvlan101
sudo ip link set macvlan101 up
```