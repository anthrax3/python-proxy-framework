ArpSpoofer Module
==============

The ArpSpoofer Module implements an ARP-Cache Poisoning attack on a specified target: Faked ARP-Responses are sent out with the IP-Address of a impersonated host and the MAC-Address of the specified network interface of the proxy-framework's host. Configuration parameters are described as following:

interface :: Specify the interface for sending out the generated ARP-Responses
host :: IP-Address of the Host which should be impersonated
target-ip :: IP-Address of the target of the attack
target-mac :: MAC-Address of the target of the attack
mode :: Operation-Mode (can be either "continuous" for ARP-Responses each 5 seconds or "single")

Before starting the ARP-Cache Poisoning attack, the module sends out three ICMP-Messages (Pings) to the target hosts. Experiments have shown that multiple operating systems only accept incoming ARP-Responses in a very limited timing frame. Successfully sending ICMP-Messages is often followed by a regular ARP-Request from the target opening a timing frame for receiving ARP-Responses.
