Bridge Module
==============

The Bridge Module uses netfilter-queue to insert network packet into the user-space. In the context of the proxy-framework, netfilter-queue is used to represent a packet gathering module for inserting packets into the proxy-framework.

Multiple Queueing-Rules can be specified within the modules utilization:

<config>
    <param id="q1-protocol"
    <param id="q1-source-port"
    <param id="q1-destination-port"
    <param id="q1-source-ip"
    <param id="q1-destination-ip"
    <param id="q1-device-in"
    <param id="q1-device-out"
</config>