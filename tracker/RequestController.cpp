//
// Created by angelo1996 on 11/11/19.
//

#include "RequestController.h"

RequestController::RequestController(MainController *mainController) : mainController(mainController) {
    this->mainController = mainController;
}

const string RequestController::serveRequest(const string &requestMessage) {
    Value dictionary = this->decodeJsonRequest(requestMessage);
    string event = dictionary["event"].asString();

    try {
        if (event == "add") {
            mainController->addTorrentSession(dictionary["info_hash"].asString(),
                                              dictionary["authentication_token"].asString());
            return this->encodeJsonResponse("1", "Successfully addedd torrent session");
        } else if (event == "delete") {
            mainController->deleteTorrentSession(dictionary["info_hash"].asString(),
                                                 dictionary["authentication_token"].asString());
            return this->encodeJsonResponse("1", "Successfully deleted torrent session");
        } else if (event == "start") {
            mainController->addPeer(dictionary["info_hash"].asString(), dictionary["peer_id"].asString(),
                                    dictionary["ip"].asString(), dictionary["port"].asInt());
            return this->encodeJsonResponse("1", "Successfully addedd to torrent session", PEER_INTERVAL,
                                            mainController->getPeers(dictionary["info_hash"].asString()));
        } else if (event == "update") {
            mainController->updatePeerTimestamp(dictionary["info_hash"].asString(), dictionary["peer_id"].asString(),
                                                dictionary["ip"].asString(), dictionary["port"].asInt());
            return this->encodeJsonResponse("1", "Successfully updated timestamp", PEER_INTERVAL,
                                            mainController->getPeers(dictionary["info_hash"].asString()));
        } else if (event == "stop") {
            mainController->deletePeer(dictionary["info_hash"].asString(), dictionary["peer_id"].asString());
            return this->encodeJsonResponse("1", "Successfully deleted from torrent session");
        } else
            return this->encodeJsonResponse("0", "Undefined event");
    }
    catch(char const* exceptionMessage){
        cout << exceptionMessage << endl;
        return this->encodeJsonResponse("0", exceptionMessage);
    }
}

const Value RequestController::decodeJsonRequest(const string &requestMessage) {
    Reader reader;
    Value dictionary;
    reader.parse(requestMessage, dictionary, false);
    return dictionary;
}

const string RequestController::encodeJsonResponse(const string &statusCode, const string &statusMessage, unsigned int interval, const vector<Peer> &peersList) {
    FastWriter writer;
    Value dictionary;
    dictionary["status_code"] = statusCode;
    dictionary["status_message"] = statusMessage;
    dictionary["interval"] = to_string(interval);
    int i = 0;
    for (auto iterator : peersList){
        dictionary["peers"][to_string(i)]["id"] = iterator.getId();
        dictionary["peers"][to_string(i)]["ip"] = iterator.getIp();
        dictionary["peers"][to_string(i)]["port"] = iterator.getPort();
        i++;
    }
    return writer.write(dictionary);
}

const string RequestController::encodeJsonResponse(const string &statusCode, const string &statusMessage) {
    FastWriter writer;
    Value dictionary;
    dictionary["status_code"] = statusCode;
    dictionary["status_message"] = statusMessage;
    return writer.write(dictionary);
}
