#include <iostream>
#include <memory>

#include "skeleton_parser.h"

int main(int argc, char **argv) {
    std::unique_ptr<SkeletonParser> skeleton_parser = std::make_unique<SkeletonParser>();
    skeleton_parser->Initialize();
    skeleton_parser->Run();
    skeleton_parser->Shutdown();
}
