//
// Created by angelo1996 on 11/11/19.
//

#include "MainController.h"


MainController::MainController() {

}

MainController::~MainController() {
    for(auto iterator : torrentSessions){
        delete iterator.second;
        torrentSessions.erase(iterator.first);
    }
}

bool MainController::containsTorrentSession(const string &id) const {
    return torrentSessions.find(id) != torrentSessions.end();
}

void MainController::addTorrentSession(const string &id, const string &authenticationToken) {
    lock_guard<mutex> lock(objectMutex);
    if(containsTorrentSession(id)) throw "Torrent session just added";
    TorrentSession *torrentSession = new TorrentSession(id, authenticationToken, JOB_INTERVAL, DELAY);
    torrentSessions[torrentSession->getId()] = torrentSession;
}

void MainController::deleteTorrentSession(const string &id, const string &authenticationToken) {
    lock_guard<mutex> lock(objectMutex);
    if(!containsTorrentSession(id)) throw "Torrent session not present";
    TorrentSession * torrentSession = torrentSessions[id];
    if(torrentSession->getAuthenticationToken() != authenticationToken) throw "Unauthorized action";
    torrentSessions.erase(id);
    delete torrentSession;
}

void MainController::addPeer(const string &torrentSessionId, const string &peerId, const string &peerIp, unsigned int peerPort){
    lock_guard<mutex> lock(objectMutex);
    if(!containsTorrentSession(torrentSessionId)) throw "Torrent session not present";
    TorrentSession * torrentSession = torrentSessions[torrentSessionId];
    torrentSession->addPeer(peerId, peerIp, peerPort);
}

void MainController::deletePeer(const string &torrentSessionId, const string &peerId) {
    lock_guard<mutex> lock(objectMutex);
    if(!containsTorrentSession(torrentSessionId)) throw "Torrent session not present";
    TorrentSession * torrentSession = torrentSessions[torrentSessionId];
    torrentSession->deletePeer(peerId);
}

void MainController::updatePeerTimestamp(const string &torrentSessionId, const string &peerId, const string &peerIp, unsigned int peerPort){
    lock_guard<mutex> lock(objectMutex);
    if(!containsTorrentSession(torrentSessionId)) throw "Torrent session not present";
    TorrentSession * torrentSession = torrentSessions[torrentSessionId];
    torrentSession->updatePeerTimestamp(peerId, peerIp, peerPort);
}

vector<Peer> MainController::getPeers(const string &torrentSessionId) {
    lock_guard<mutex> lock(objectMutex);
    if(!containsTorrentSession(torrentSessionId)) throw "Torrent session not present";
    TorrentSession * torrentSession = torrentSessions[torrentSessionId];
    return torrentSession->getPeers();
}
