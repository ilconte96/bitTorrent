//
// Created by angelo1996 on 11/11/19.
//

#ifndef TRACKER_REQUESTCONTROLLER_H
#define TRACKER_REQUESTCONTROLLER_H


#include "MainController.h"
#include "dist/json/json.h"
#include <string>

using namespace std;
using namespace Json;

class RequestController {
public:
    RequestController(MainController *mainController);

private:
    MainController *mainController;
    const Value decodeJsonRequest(const string &requestMessage);
    const string encodeJsonResponse(const string &statusCode, const string &statusMessage, unsigned int interval, const vector<Peer> &peersList);
    const string encodeJsonResponse(const string &statusCode, const string &statusMessage);

public:
    const string serveRequest(const string &requestMessage);

};


#endif //TRACKER_REQUESTCONTROLLER_H
