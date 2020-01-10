//
// Created by angelo1996 on 11/11/19.
//

#ifndef TRACKER_TORRENTSESSION_H
#define TRACKER_TORRENTSESSION_H

#include <string>
#include <unordered_map>
#include <chrono>
#include <mutex>
#include "Peer.h"
#include "Job.h"
#include <vector>

using namespace std;

class TorrentSession {
private:
    string id;
    string authenticationToken;
    unsigned int jobInterval, delay;
    unordered_map<string, Peer*> peers;
    Job *job;
    mutable mutex objectMutex;
    bool containsPeer(const string &id) const;

public:
    TorrentSession(const string &id, const string &authenticationToken, unsigned int jobInterval, unsigned int delay);
    virtual ~TorrentSession();

    void addPeer(const string &id, const string &ip, const unsigned  int port);
    void updatePeerTimestamp(const string &id, const string &ip, const unsigned int port);
    void deletePeer(const string &id);
    void checkPeers();
    vector<Peer> getPeers() const;
    const string &getId() const;

    const string &getAuthenticationToken() const;

};


#endif //TRACKER_TORRENTSESSION_H
