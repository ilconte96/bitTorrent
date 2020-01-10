//
// Created by angelo1996 on 11/11/19.
//

#ifndef TRACKER_TCPSERVER_H
#define TRACKER_TCPSERVER_H

#include "RequestController.h"
#include <iostream>
#include <string>
#include <sys/socket.h>
#include <netinet/in.h>
#include <thread>
#include <unistd.h>
#include <iomanip>
#include "config.h"


using namespace std;


class TcpServer {
private:
    short int port, queueLength;
    int option, serverSocket, socketAddressLength;
    unsigned int bufferLength, headerSize;
    RequestController *requestController;
    struct sockaddr_in socketAddress;
    void serveRequest(int clientSocket);
    void sendMessage(int clientSocket, string message);
    string receiveMessage(int clientSocket);
public:
    TcpServer(short int port, short int queueLength, RequestController *requestController);
    void startServeRequests();
};


#endif //TRACKER_TCPSERVER_H
