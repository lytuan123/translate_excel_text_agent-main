# Network Configuration Guide

## Introduction

This document provides instructions for configuring a secure enterprise network infrastructure. It covers VLAN setup, router configuration, firewall rules, and security best practices.

## Requirements

Before proceeding with the configuration, ensure you have:

- Administrative access to all network devices
- Up-to-date firmware on all devices
- A network diagram showing the planned topology
- Reserved IP address ranges for different departments

## VLAN Configuration

### Step 1: Create VLANs

Log in to the core switch and enter configuration mode:

```
switch> enable
switch# configure terminal
```

Create VLANs for different departments:

```
switch(config)# vlan 10
switch(config-vlan)# name MANAGEMENT
switch(config-vlan)# exit
switch(config)# vlan 20
switch(config-vlan)# name SALES
switch(config-vlan)# exit
switch(config)# vlan 30
switch(config-vlan)# name ENGINEERING
switch(config-vlan)# exit
switch(config)# vlan 40
switch(config-vlan)# name GUEST
switch(config-vlan)# exit
```

### Step 2: Assign Ports to VLANs

Configure access ports for different departments:

```
switch(config)# interface range gigabitethernet 1/0/1-10
switch(config-if-range)# switchport mode access
switch(config-if-range)# switchport access vlan 20
switch(config-if-range)# exit

switch(config)# interface range gigabitethernet 1/0/11-20
switch(config-if-range)# switchport mode access
switch(config-if-range)# switchport access vlan 30
switch(config-if-range)# exit
```

Configure trunk ports to other switches:

```
switch(config)# interface gigabitethernet 1/0/48
switch(config-if)# switchport mode trunk
switch(config-if)# switchport trunk allowed vlan 10,20,30,40
switch(config-if)# exit
```

## Router Configuration

### Step 1: Basic Setup

Access the router and configure the hostname and domain name:

```
router> enable
router# configure terminal
router(config)# hostname central-router
central-router(config)# ip domain-name example.com
```

### Step 2: Configure Inter-VLAN Routing

Set up router-on-a-stick configuration:

```
central-router(config)# interface gigabitethernet 0/0
central-router(config-if)# no shutdown
central-router(config-if)# exit

central-router(config)# interface gigabitethernet 0/0.10
central-router(config-subif)# encapsulation dot1q 10
central-router(config-subif)# ip address 192.168.10.1 255.255.255.0
central-router(config-subif)# exit

central-router(config)# interface gigabitethernet 0/0.20
central-router(config-subif)# encapsulation dot1q 20
central-router(config-subif)# ip address 192.168.20.1 255.255.255.0
central-router(config-subif)# exit

central-router(config)# interface gigabitethernet 0/0.30
central-router(config-subif)# encapsulation dot1q 30
central-router(config-subif)# ip address 192.168.30.1 255.255.255.0
central-router(config-subif)# exit

central-router(config)# interface gigabitethernet 0/0.40
central-router(config-subif)# encapsulation dot1q 40
central-router(config-subif)# ip address 192.168.40.1 255.255.255.0
central-router(config-subif)# exit
```

## Firewall Configuration

### Step 1: Basic Security Rules

Configure access control lists (ACLs):

```
central-router(config)# ip access-list extended GUEST_RESTRICTIONS
central-router(config-ext-nacl)# deny ip 192.168.40.0 0.0.0.255 192.168.10.0 0.0.0.255
central-router(config-ext-nacl)# deny ip 192.168.40.0 0.0.0.255 192.168.20.0 0.0.0.255
central-router(config-ext-nacl)# deny ip 192.168.40.0 0.0.0.255 192.168.30.0 0.0.0.255
central-router(config-ext-nacl)# permit ip any any
central-router(config-ext-nacl)# exit
```

Apply the ACL to the guest VLAN interface:

```
central-router(config)# interface gigabitethernet 0/0.40
central-router(config-subif)# ip access-group GUEST_RESTRICTIONS in
central-router(config-subif)# exit
```

## DHCP Configuration

### Step 1: Configure DHCP Pools

Set up DHCP for each VLAN:

```
central-router(config)# ip dhcp excluded-address 192.168.10.1 192.168.10.10
central-router(config)# ip dhcp excluded-address 192.168.20.1 192.168.20.10
central-router(config)# ip dhcp excluded-address 192.168.30.1 192.168.30.10
central-router(config)# ip dhcp excluded-address 192.168.40.1 192.168.40.10

central-router(config)# ip dhcp pool MANAGEMENT
central-router(dhcp-config)# network 192.168.10.0 255.255.255.0
central-router(dhcp-config)# default-router 192.168.10.1
central-router(dhcp-config)# dns-server 8.8.8.8
central-router(dhcp-config)# exit

central-router(config)# ip dhcp pool SALES
central-router(dhcp-config)# network 192.168.20.0 255.255.255.0
central-router(dhcp-config)# default-router 192.168.20.1
central-router(dhcp-config)# dns-server 8.8.8.8
central-router(dhcp-config)# exit

central-router(config)# ip dhcp pool ENGINEERING
central-router(dhcp-config)# network 192.168.30.0 255.255.255.0
central-router(dhcp-config)# default-router 192.168.30.1
central-router(dhcp-config)# dns-server 8.8.8.8
central-router(dhcp-config)# exit

central-router(config)# ip dhcp pool GUEST
central-router(dhcp-config)# network 192.168.40.0 255.255.255.0
central-router(dhcp-config)# default-router 192.168.40.1
central-router(dhcp-config)# dns-server 8.8.8.8
central-router(dhcp-config)# exit
```

## Verification

To verify your configuration, use the following commands:

- Check VLAN status:
  ```
  switch# show vlan brief
  ```

- Verify interface status:
  ```
  switch# show interfaces status
  ```

- Test inter-VLAN routing:
  ```
  central-router# ping 192.168.20.2 source 192.168.10.1
  ```

- Verify DHCP operation:
  ```
  central-router# show ip dhcp binding
  ```

## Troubleshooting

If you encounter issues:

1. Check physical connections and port status
2. Verify VLAN assignments
3. Test connectivity between VLANs
4. Review firewall rules
5. Check DHCP server logs

## Security Best Practices

1. Change all default passwords
2. Implement 802.1X authentication where possible
3. Enable port security to prevent MAC address spoofing
4. Regularly update firmware on all network devices
5. Monitor network traffic for unusual patterns
6. Use encrypted protocols (SSH, HTTPS) for management
7. Implement NTP to ensure consistent timestamps for logs 