//
// Created by angelo1996 on 11/11/19.
//

#include "TorrentSession.h"

TorrentSession::TorrentSession(const string &id, const string &authenticationToken, unsigned int jobInterval, unsigned int delay) : id(id), authenticationToken(authenticationToken), jobInterval(jobInterval), delay(delay) {
    cout << "Created torrent session with id: " << this->getId() << endl;
    job = new Job();
    job->setInterval([=] (){
        this->checkPeers();
    }, jobInterval);
}

TorrentSession::~TorrentSession() {
    if(job != nullptr)
        delete job;
    for(auto iterator : peers){
        delete iterator.second;
        peers.erase(iterator.first);
    }
}

const string &TorrentSession::getId() const {
    return id;
}

const string &TorrentSession::getAuthenticationToken() const {
    return authenticationToken;
}

bool TorrentSession::containsPeer(const string &id) const {
    return peers.find(id) != peers.end();
}

void TorrentSession::addPeer(const string &id, const string &ip, const unsigned int port){
    lock_guard<mutex> lock(objectMutex);
    if(containsPeer(id)) throw "Peer just added";
    Peer *peer = new Peer(id, ip, port, chrono::high_resolution_clock::now());
    peers[peer->getId()] = peer;
}

void TorrentSession::deletePeer(const string &id){
    lock_guard<mutex> lock(objectMutex);
    if(!containsPeer(id)) throw "Peer not present";
    Peer * peer = peers[id];
    peers.erase(id);
    delete peer;
}

void TorrentSession::updatePeerTimestamp(const string &id, const string &ip, const unsigned int port){
    lock_guard<mutex> lock(objectMutex);
    if(!containsPeer(id)){
        Peer *peer = new Peer(id, ip, port, chrono::high_resolution_clock::now());
        peers[peer->getId()] = peer;
    }
    else {
        peers[id]->setTimestamp(chrono::high_resolution_clock::now());
        peers[id]->setIp(ip);
        peers[id]->setPort(port);
    }
}

void TorrentSession::checkPeers(){
    lock_guard<mutex> lock(objectMutex);
    auto iterator = peers.begin();
    while(iterator != peers.end()){
        if(chrono::duration_cast<chrono::milliseconds>(chrono::high_resolution_clock::now() - iterator->second->getTimestamp()).count() >= delay){
            cout << "Peer scaduto " << iterator->first << endl;
            delete iterator->second;
            iterator = peers.erase(iterator);
        }
        else
            iterator++;
    }
}

vector<Peer> TorrentSession::getPeers() const{
    lock_guard<mutex> lock(objectMutex);
    vector<Peer> peersList;
    for (auto iterator : peers){
        peersList.push_back(*iterator.second);
    }
    return peersList;
}



