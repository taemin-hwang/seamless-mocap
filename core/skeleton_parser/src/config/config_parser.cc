#include <cstdio>
#include <iostream>

#include "config/config_parser.h"

using namespace rapidjson;

ConfigParser::ConfigParser(std::string path) {
    FILE* fp = fopen(path.c_str(), "rb");
    if(fp == 0) {
        std::cout << "file not exist : default param will be used" << std::endl;
        return;
    }
    char readbuffer[65536];
    FileReadStream is(fp, readbuffer, sizeof(readbuffer));

    Document document;
    document.ParseStream(is);

    if(document.HasMember("addr") && document["addr"].IsString()) {
        ip_addr_ = document["addr"].GetString();
    }
    if(document.HasMember("port") && document["port"].IsInt()) {
        port_ = document["port"].GetInt();
    }
    if(document.HasMember("viewer") && document["viewer"].IsString()) {
        is_enable_viewer_ = document["viewer"].GetString();
    }
    if(document.HasMember("logger") && document["logger"].IsString()) {
        log_level_ = document["logger"].GetString();
    }

    fclose(fp);
}