//
// Created by angelo1996 on 11/11/19.
//

#include "TcpServer.h"


TcpServer::TcpServer(short int port, short int queueLength, RequestController *requestController) : port(port), queueLength(queueLength), requestController(requestController){
    option = 1;
    socketAddressLength = sizeof(socketAddress);

    if ((serverSocket= socket(AF_INET, SOCK_STREAM, 0)) == 0)
    {
        cerr << "socket failed" << endl;
        exit(EXIT_FAILURE);
    }
    if (setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT,&option, sizeof(option)))
    {
        cerr << "setsockopt failed" << endl;
        exit(EXIT_FAILURE);
    }
    socketAddress.sin_family = AF_INET;
    socketAddress.sin_addr.s_addr = INADDR_ANY;
    socketAddress.sin_port = htons( this->port );
    if (bind(serverSocket, (struct sockaddr *)&socketAddress,sizeof(socketAddress))<0)
    {
        cerr << "bind failed" << endl;
        exit(EXIT_FAILURE);
    }
    if (listen(serverSocket, this->queueLength) < 0)
    {
        cerr << "listen failed" << endl;
        exit(EXIT_FAILURE);
    }

    cout << "Tcp server started with success";

}

void TcpServer::startServeRequests(){
    while(true){
        int clientSocket = accept(serverSocket, (struct sockaddr *)&socketAddress,(socklen_t*)&socketAddressLength);
        if(clientSocket < 0)
            cerr << "accept failed" << endl;
        thread requestServer([=] () {
            this->serveRequest(clientSocket);
        });

        requestServer.detach();
    }
}

void TcpServer::serveRequest(int clientSocket) {
    cout << "New Request" << endl;
    try{
        string requestMessage = this->receiveMessage(clientSocket);
        string responseMessage = requestController->serveRequest(requestMessage);
        this->sendMessage(clientSocket, responseMessage);
    }
    catch(char const* exceptionMessage){
        cout << exceptionMessage << endl;
    }
    close(clientSocket);
}

string TcpServer::receiveMessage(int clientSocket) {
    char buffer[BUFFER_LENGTH + 1] = {0};
    uint32_t header;
    if(read(clientSocket, &header, HEADER_SIZE) == -1)
        throw "Error in reading from connection";

    int messageLength = ntohl(header);
    string message;
    for (int i = 0; i < messageLength/BUFFER_LENGTH; ++i){
        if(read(clientSocket, buffer, BUFFER_LENGTH) == -1)
            throw "Error in reading from connection";
        message += string(buffer).substr(0, BUFFER_LENGTH);
    }
    unsigned int remainder = messageLength % BUFFER_LENGTH;
    if(remainder != 0){
        if(read(clientSocket, buffer, remainder) == -1)
            throw "Error in reading from connection";
        message += string(buffer).substr(0, remainder);
    }
    cout << message << endl;
    return message;
}

void TcpServer::sendMessage(int clientSocket, string message) {
    int messageSize = message.size();
    uint32_t networkByteOrderValue = htonl(message.size());

    if(send(clientSocket , &networkByteOrderValue , HEADER_SIZE, 0 ) == -1)
        throw "Error in sending data in connection";

    for (int i = 0; i < messageSize/BUFFER_LENGTH; ++i)
        if(send(clientSocket , message.substr((i*BUFFER_LENGTH),(i*BUFFER_LENGTH)+BUFFER_LENGTH).c_str() , BUFFER_LENGTH, 0 ) == -1)
            throw "Error in sending data in connection";

    unsigned int remainder = messageSize % BUFFER_LENGTH;

    if(remainder != 0){
        if(send(clientSocket , message.substr(messageSize-remainder, messageSize).c_str() , remainder , 0 ) == -1)
            throw "Error in sending data in connection";
    }
}


