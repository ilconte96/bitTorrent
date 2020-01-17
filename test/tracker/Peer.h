//
// Created by angelo1996 on 11/11/19.
//

#ifndef TRACKER_PEER_H
#define TRACKER_PEER_H

#include <string>
#include <thread>
#include <chrono>

using namespace std;

class Peer {
public:
    Peer(const string &id, const string &ip, const unsigned int port, chrono::time_point<chrono::high_resolution_clock> timestamp);
    const string &getId() const;
    void setTimestamp(chrono::time_point<chrono::high_resolution_clock> timestamp);
    chrono::time_point<chrono::high_resolution_clock> getTimestamp();

    const string &getIp() const;

    unsigned int getPort() const;

    void setIp(const string &ip);

    void setPort(unsigned int port);


private:
    string id;
    string ip;
    unsigned int port;
    chrono::time_point<chrono::high_resolution_clock> timestamp;
};


#endif //TRACKER_PEER_H
