#pragma once
#include <compare>

struct Coord {
  int row;
  int col;

  auto operator<=>(const Coord &) const = default;
  bool operator==(const Coord &) const = default;
};
