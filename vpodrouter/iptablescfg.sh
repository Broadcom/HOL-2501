#!/bin/sh

# DEFAULT HOL FIREWALL RULESET
# version 13-March 2024 

# clear any existing rules
iptables --flush

#set the default policy on FORWARD to DROP
iptables -P FORWARD DROP

# EXAMPLE allow SSH: do not use as-is. Too open!
#iptables -A FORWARD -s 192.168.110.0/24 -p TCP --dport 22 -j ACCEPT

# allow Manager VM ssh access to holgitlab.oc.vmware.com
#iptables -A INPUT -s 10.0.0.11 -j ACCEPT
#iptables -A FORWARD -p tcp -s 10.0.0.11 -d 208.91.1.219 --dport 22 -j ACCEPT
#iptables -A FORWARD -p tcp -d 10.0.0.11 -s 208.91.1.219 -j ACCEPT

# allow Manager 443 access to ws.labplatform.vmware.com
#wsIPs=`nslookup ws.labplatform.vmware.com | grep Address: | grep -v \# | cut -f2 -d":"`
#for i in $wsIPs;do
#  iptables -A FORWARD -p tcp -s 10.0.0.11 -d ${i} --dport 443 -j ACCEPT
#  iptables -A FORWARD -p tcp -d 10.0.0.11 -s ${i} -j ACCEPT
#done

# for VLP edit script open the Manager VM 
iptables -A FORWARD -p tcp -s 10.0.0.11 -d 0.0.0.0/0 -j ACCEPT
iptables -A FORWARD -p tcp -d 10.0.0.11 -j ACCEPT

# allow IP inside the vPod, only on private networks
iptables -A FORWARD -s 192.168.0.0/16 -d 192.168.0.0/16 -j ACCEPT
iptables -A FORWARD -s 192.168.0.0/16 -d 172.16.0.0/12  -j ACCEPT
iptables -A FORWARD -s 192.168.0.0/16 -d 10.0.0.0/8     -j ACCEPT
iptables -A FORWARD -s 172.16.0.0/12 -d 192.168.0.0/16  -j ACCEPT
iptables -A FORWARD -s 172.16.0.0/12 -d 172.16.0.0/12   -j ACCEPT
iptables -A FORWARD -s 172.16.0.0/12 -d 10.0.0.0/8      -j ACCEPT
iptables -A FORWARD -s 10.0.0.0/8 -d 192.168.0.0/16     -j ACCEPT
iptables -A FORWARD -s 10.0.0.0/8 -d 172.16.0.0/12      -j ACCEPT
iptables -A FORWARD -s 10.0.0.0/8 -d 10.0.0.0/8         -j ACCEPT


# allow access to and from Google DNS
iptables -A FORWARD -p UDP -d 8.8.8.8 --dport 53 -j ACCEPT
iptables -A FORWARD -p UDP -s 8.8.8.8 --sport 53 -j ACCEPT
iptables -A FORWARD -p UDP -d 8.8.4.4 --dport 53 -j ACCEPT
iptables -A FORWARD -p UDP -s 8.8.4.4 --sport 53 -j ACCEPT

# allow RDP requests so captains don't need to disable the firewall
iptables -A FORWARD -p TCP --dport 3389 -j ACCEPT
iptables -A FORWARD -p TCP --sport 3389 -j ACCEPT

# allow ping everywhere
iptables -A FORWARD -p icmp --icmp-type 8 -s 0/0 -d 0/0 -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -p icmp --icmp-type 0 -s 0/0 -d 0/0 -m state --state ESTABLISHED,RELATED -j ACCEPT

### LAB-SPECIFIC RULES

# (add your rules here)

### END RULES

# indicate that iptables has run
> ~holuser/firewall

