#include <iostream>
#include <memory>

#include "body_tracker.h"

int main(int argc, char **argv) {
    std::unique_ptr<BodyTracker> body_tracker = std::make_unique<BodyTracker>();
    body_tracker->run(argc, argv);
}
