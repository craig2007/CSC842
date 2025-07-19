#include <vector>

#ifndef __DNS_HIJACKER_H__
#define __DNS_HIJACKER_H__

struct __attribute__((packed)) UDPHeader
{
    uint16_t src_port;
    uint16_t dest_port;
    uint16_t length;
    uint16_t checksum;
};

struct __attribute__((packed)) DNSHeader
{
    uint16_t id;
    uint16_t flags;
    uint16_t qdcount;
    uint16_t ancount;
    uint16_t nscount;
    uint16_t arcount;
};

struct __attribute__((packed)) DNSRecord
{
    uint16_t name;
    uint16_t type;
    uint16_t dns_class;
    uint32_t ttl;
    uint16_t rdlength;
    uint32_t rdata;
};

#endif // __DNS_HIJACKER_H__
