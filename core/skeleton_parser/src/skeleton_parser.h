#ifndef _SKELETON_PARSER_H_
#define _SKELETON_PARSER_H_

#include <iostream>
#include <memory>

#include "tracker/tracker_manager.h"
#include "transfer/transfer_manager.h"
#include "viewer/viewer_manager.h"

#include "system/config/config_parser.h"
#include "system/types.h"

class SkeletonParser {
 public:
    SkeletonParser();
    virtual ~SkeletonParser() = default;

    void Initialize();
    void Run();
    void Shutdown();

 private:
    std::unique_ptr<TrackerInterface> body_tracker_;
    std::unique_ptr<TransferInterface> body_transfer_;
    std::unique_ptr<ConfigParser> config_parser_;
    std::unique_ptr<ViewerManager> viewer_manager_;
    bool enable_viewer_ = false;
};

#endif