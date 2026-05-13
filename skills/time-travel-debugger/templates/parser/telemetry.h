#ifndef TELEMETRY_H
#define TELEMETRY_H

#include <string>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <iostream>

static int tele_sock = -1;
static struct sockaddr_in tele_addr;

inline void init_telemetry() {
    tele_sock = socket(AF_INET, SOCK_DGRAM, 0);
    memset(&tele_addr, 0, sizeof(tele_addr));
    tele_addr.sin_family = AF_INET;
    tele_addr.sin_port = htons(4000);
    tele_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
}

inline void telemetry_ping(const char* node_id) {
    if (tele_sock == -1) init_telemetry();
    std::string msg = node_id;
    sendto(tele_sock, msg.c_str(), msg.length(), 0, (struct sockaddr*)&tele_addr, sizeof(tele_addr));
}

#endif
