# DNS Hijacker

DNS Hijacker is a tool to use a man-on-the-side technique to listen for DNS traffic. When it sees DNS traffic to hijack, it attempts to craft a response packet to send to a victim machine faster than a legitimate response can be sent. If the response is received before the legitimate response, the tool can successfully redirect the victim machine to an attacker controlled site instead of the victim's intended location.

## Installation

DNS Hijacker includes a Makefile. From the directory in which the source code is located type `make` to create the dns_hijacker binary.

## Dependencies

DNS Hijacker requires the libpcap library is installed.

## Running DNS Hijacker

DNS Hijacker needs to be run as a superuser in order to enable it to connect to the interface. While running as root or with using `sudo`, DNS Hijacker can be run with the command `./dns_hijacker <interface> <IP address>` in which interface is the interface to listen on and send the fake DNS responses on and IP address is the IP address to trick the target into going to.

## Future Work

This is an early version of the DNS Hijacker tool that requires further development. Future plans for work on this tool include:

* Fixing the UDP checksum
* Providing the user with more options, including allowing to filter DNS requests that are redirected based off of specific hosts
* Support for DNS requests that have multiple queries or additional info in them
* Support for IP headers of sizes other than 20
* Support for additional DNS record types
