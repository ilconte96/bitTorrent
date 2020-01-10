//
// Created by angelo1996 on 11/11/19.
//

#ifndef TRACKER_MAINCONTROLLER_H
#define TRACKER_MAINCONTROLLER_H

#include <string>
#include "TorrentSession.h"
#include "Peer.h"
#include "config.h"

using namespace std;


class MainController {
private:
    unordered_map<string, TorrentSession *> torrentSessions;
    mutable mutex objectMutex;
    bool containsTorrentSession(const string &id) const;

public:
    MainController();
    void addTorrentSession(const string &id, const string &authenticationToken);
    void deleteTorrentSession(const string &id, const string &authenticationToken);
    void addPeer(const string &torrentSessionId, const string &peerId, const string &peerIp, unsigned int peerPort);
    void deletePeer(const string &torrentSessionId, const string &peerId);
    void updatePeerTimestamp(const string &torrentSessionId, const string &peerId, const string &peerIp, unsigned int peerPort);
    vector<Peer> getPeers(const string &torrentSessionId);
    virtual ~MainController();

};



#endif //TRACKER_MAINCONTROLLER_H
