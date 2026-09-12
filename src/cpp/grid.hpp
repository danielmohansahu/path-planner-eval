#pragma once
#include <cstdint>
#include <utility>
#include <vector>

namespace path_planner {

inline constexpr int kImpassableThreshold = 254;

class Grid {
public:
  Grid(const uint8_t *data, int height, int width)
      : data_(data), height_(height), width_(width) {}

  [[nodiscard]] int height() const { return height_; }
  [[nodiscard]] int width() const { return width_; }

  [[nodiscard]] bool isValid(int r, int c) const {
    return r >= 0 && r < height_ && c >= 0 && c < width_;
  }

  [[nodiscard]] uint8_t cost(int r, int c) const {
    return data_[r * width_ + c];
  }

  [[nodiscard]] bool isPassable(int r, int c) const {
    return isValid(r, c) && cost(r, c) < kImpassableThreshold;
  }

  std::vector<std::pair<int, int>> neighbors(int r, int c,
                                             int connectivity) const {
    std::vector<std::pair<int, int>> result;
    static constexpr int dr4[] = {-1, 1, 0, 0};
    static constexpr int dc4[] = {0, 0, -1, 1};
    static constexpr int dr8[] = {-1, -1, 1, 1};
    static constexpr int dc8[] = {-1, 1, -1, 1};

    for (int i = 0; i < 4; ++i) {
      int nr = r + dr4[i], nc = c + dc4[i];
      if (isPassable(nr, nc))
        result.emplace_back(nr, nc);
    }
    if (connectivity == 8) {
      for (int i = 0; i < 4; ++i) {
        int nr = r + dr8[i], nc = c + dc8[i];
        if (isPassable(nr, nc) && isPassable(r, nc) && isPassable(nr, c))
          result.emplace_back(nr, nc);
      }
    }
    return result;
  }

private:
  const uint8_t *data_;
  int height_;
  int width_;
};

} // namespace path_planner
