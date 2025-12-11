// src/utils.hpp
#pragma once
#include <cstdlib>
#include <iostream>
#include <string>

class Config {
 public:
  static int getInt(const char* name, int defaultValue) {
    const char* val = std::getenv(name);
    return val ? std::atoi(val) : defaultValue;
  }

  static double getDouble(const char* name, double defaultValue) {
    const char* val = std::getenv(name);
    return val ? std::atof(val) : defaultValue;
  }

  static std::string getString(const char* name, const char* defaultValue) {
    const char* val = std::getenv(name);
    return val ? std::string(val) : std::string(defaultValue);
  }
};