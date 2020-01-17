#include <iostream>
#include <thread>
#include <vector>
#include "MainController.h"
#include "RequestController.h"
#include "TcpServer.h"
#include <signal.h>
#include "config.h"

using namespace std;

int main() {
    cout << "Hello, World!" << std::endl;

    signal(SIGPIPE, SIG_IGN);

    MainController *mainController = new MainController();

    RequestController *requestController = new RequestController(mainController);

    TcpServer *tcpServer = new TcpServer(LISTEN_PORT, QUEUE_LENGTH, requestController);

    thread *tcpServerThread = new thread([&] (){
        tcpServer->startServeRequests();
    });

    tcpServerThread->join();

    return 0;

}