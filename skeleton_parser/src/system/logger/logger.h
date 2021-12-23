#ifndef _LOGGER_H_
#define _LOGGER_H_

#include <iostream>
#include <typeinfo>
#include <cxxabi.h>
#include <sstream>
#include <string>
#include <memory>

using namespace std;

enum class LOGLEVEL : int { FATAL, ERRORS, WARN, INFO, DEBUG };
static LOGLEVEL kLogLevel = LOGLEVEL::INFO;

class LogPrefix {
 public:
    LogPrefix(LOGLEVEL loglevel_ = LOGLEVEL::DEBUG) {
        if(loglevel_ == LOGLEVEL::FATAL) {
            message = "[FATAL]";
        } else if (loglevel_ == LOGLEVEL::ERRORS) {
            message = "[ERROR]";
        } else if (loglevel_ == LOGLEVEL::WARN) {
            message = "[WARN ]";
        } else if (loglevel_ == LOGLEVEL::INFO) {
            message = "[INFO ]";
        } else {
            message = "[DEBUG]";
        }
    }

    inline const std::string & GetMessage() { return std::move(message); }

 private:
    std::string message = "[DEBUG] ";
};

class Logger {
 public:
    Logger(LOGLEVEL level, std::string class_name = "") {
        logprefix_ = std::make_shared<LogPrefix>(level);
        buffer_ << logprefix_->GetMessage();
        if(class_name.size() > 0) buffer_ << "[" << class_name << "] ";
    }

    template <typename T>
    Logger& operator << (T const& value) {
        buffer_ << value;
        return *this;
    }

    virtual ~Logger() {
        buffer_ << std::endl;
        std::cerr << buffer_.str();
    }

 private:
    std::ostringstream buffer_;
    std::shared_ptr<LogPrefix> logprefix_;
};

static int status;

#define logFatal \
if(LOGLEVEL::FATAL > kLogLevel) ; \
else Logger(LOGLEVEL::FATAL)

#define logError \
if(LOGLEVEL::ERRORS > kLogLevel) ; \
else Logger(LOGLEVEL::ERRORS)

#define logWarn \
if(LOGLEVEL::WARN > kLogLevel) ; \
else Logger(LOGLEVEL::WARN)

#define logInfo \
if(LOGLEVEL::INFO > kLogLevel) ; \
else Logger(LOGLEVEL::INFO)

#define logDebug \
if(LOGLEVEL::DEBUG > kLogLevel) ; \
else Logger(LOGLEVEL::DEBUG, abi::__cxa_demangle(typeid(*this).name(), 0, 0, &status))

#endif
