#ifndef _CONFIG_PARSER_H_
#define _CONFIG_PARSER_H_

#include <string>

// include rapidjson
#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/filereadstream.h"

class ConfigParser {
 public:
    ConfigParser(std::string path);
    virtual ~ConfigParser() = default;

    inline int GetCamId() { return camid_; }
    inline std::string GetAddress() { return ip_addr_; }
    inline int GetPort() { return port_; }
    inline bool IsViewerOn() { return is_enable_viewer_ == "on" || is_enable_viewer_ == "ON" || is_enable_viewer_ == "On"; }
   //  inline std::string GetLogLevel() { return log_level_; }

 private:
    std::string ip_addr_ = "";
    int port_ = 0;
    int camid_ = 0;
    std::string is_enable_viewer_ = "off";
    std::string log_level_ = "debug";
};

#endif
