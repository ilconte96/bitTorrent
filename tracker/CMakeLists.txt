cmake_minimum_required(VERSION 3.15)
project(tracker)

set(CMAKE_CXX_STANDARD 17)
SET(CMAKE_CXX_FLAGS -pthread)

add_executable(tracker main.cpp Peer.cpp Peer.h MainController.cpp MainController.h TorrentSession.cpp TorrentSession.h RequestController.cpp RequestController.h TcpServer.cpp TcpServer.h Job.cpp Job.h dist/jsoncpp.cpp config.h)