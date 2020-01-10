//
// Created by angelo1996 on 13/11/19.
//

#include "Job.h"

Job::~Job() {
    this->stop();
}

void Job::stop() {
    this->clear = true;
    if(pThread != nullptr){
        pThread->join();
        delete pThread;
        pThread = nullptr;
    }
}
