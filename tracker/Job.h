//
// Created by angelo1996 on 13/11/19.
//

#ifndef TRACKER_JOB_H
#define TRACKER_JOB_H

#include <thread>
#include <chrono>
#include <iostream>
#include <string>

using namespace std;

class Job {
private:
    bool clear;
    thread *pThread;

public:
    template<typename F>
    void setInterval(F callback, int interval);
    void stop();

    virtual ~Job();

};

template<typename F>
void Job::setInterval(F callback, int interval) {
    this->stop();
    this->clear = false;
    pThread = new thread([=]() {
        while(true) {
            if(this->clear) return;
            this_thread::sleep_for(chrono::milliseconds(interval));
            if(this->clear) return;
            callback();
        }
    });
}

#endif //TRACKER_JOB_H
