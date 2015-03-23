# flask is running on port 5000, so redirect port 80 to 5000

sudo iptables -A PREROUTING -t nat -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 5000
