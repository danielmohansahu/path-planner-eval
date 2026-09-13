#pragma once
#include <cstdint>
#include <span>
#include <vector>

#include "coord.hpp"

class Grid {
public:
  Grid(std::span<const uint8_t> data, int height, int width)
      : data_(data), height_(height), width_(width) {}

  int height() const { return height_; }
  int width() const { return width_; }

  bool isValid(Coord pos) const {
    return pos.row >= 0 && pos.row < height_ && pos.col >= 0 &&
           pos.col < width_;
  }

  uint8_t cost(int r, int c) const { return data_[r * width_ + c]; }

  bool isPassable(Coord pos) const {
    return isValid(pos) && cost(pos.row, pos.col) < 254;
  }

  std::vector<Coord> neighbors(Coord pos, int connectivity) const {
    std::vector<Coord> result;
    static constexpr int dr4[] = {-1, 1, 0, 0};
    static constexpr int dc4[] = {0, 0, -1, 1};
    static constexpr int dr8[] = {-1, -1, 1, 1};
    static constexpr int dc8[] = {-1, 1, -1, 1};

    for (int i = 0; i < 4; ++i) {
      Coord n{pos.row + dr4[i], pos.col + dc4[i]};
      if (isPassable(n))
        result.push_back(n);
    }
    if (connectivity == 8) {
      for (int i = 0; i < 4; ++i) {
        Coord n{pos.row + dr8[i], pos.col + dc8[i]};
        if (isPassable(n) && isPassable({pos.row, n.col}) &&
            isPassable({n.row, pos.col}))
          result.push_back(n);
      }
    }
    return result;
  }

private:
  std::span<const uint8_t> data_;
  int height_;
  int width_;
};
