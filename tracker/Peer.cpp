//
// Created by angelo1996 on 11/11/19.
//

#include "Peer.h"
#include <iostream>

using namespace std;

Peer::Peer(const string &id, const string &ip, const unsigned int port, chrono::time_point<chrono::high_resolution_clock> timestamp) :id(id), ip(ip), port(port), timestamp(timestamp) {
    cout << "Peer Created" << std::endl;
}

const string &Peer::getId() const {
    return id;
}

const string &Peer::getIp() const {
    return ip;
}

unsigned int Peer::getPort() const {
    return port;
}


void Peer::setIp(const string &ip) {
    this->ip = ip;
}

void Peer::setPort(unsigned int port) {
    this->port = port;
}

chrono::time_point<chrono::high_resolution_clock> Peer::getTimestamp(){
    return timestamp;
}

void Peer::setTimestamp(chrono::time_point<chrono::high_resolution_clock> timestamp){
    this->timestamp = timestamp;
}

