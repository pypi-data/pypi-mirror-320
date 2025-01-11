// SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
//
// SPDX-License-Identifier: MPL-2.0

#pragma once

#include "common.hpp"
#include "enum.hpp"

#include <concepts>
#include <exception>
#include <sstream>
#include <string>

namespace power_grid_model_io_native {
namespace detail {
inline auto to_string(std::floating_point auto x) {
    std::ostringstream sstr{}; // NOLINT(misc-const-correctness) // https://github.com/llvm/llvm-project/issues/57297
    sstr << x;
    return sstr.str();
}
inline auto to_string(std::integral auto x) { return std::to_string(x); }
} // namespace detail

class PGMIOError : public std::exception {
  public:
    void append_msg(std::string_view msg) { msg_ += msg; }
    char const* what() const noexcept final { return msg_.c_str(); }

  private:
    std::string msg_;
};

class InvalidArguments : public PGMIOError {
  public:
    struct TypeValuePair {
        std::string name;
        std::string value;
    };

    template <std::same_as<TypeValuePair>... Options>
    InvalidArguments(std::string const& method, std::string const& arguments) {
        append_msg(method + " is not implemented for " + arguments + "!\n");
    }

    template <class... Options>
        requires(std::same_as<std::remove_cvref_t<Options>, TypeValuePair> && ...)
    InvalidArguments(std::string const& method, Options&&... options)
        : InvalidArguments{method, "the following combination of options"} {
        (append_msg(" " + std::forward<Options>(options).name + ": " + std::forward<Options>(options).value + "\n"),
         ...);
    }
};

class MissingCaseForEnumError : public InvalidArguments {
  public:
    template <typename T>
    MissingCaseForEnumError(std::string const& method, const T& value)
        : InvalidArguments{method, std::string{typeid(T).name()} + " #" + detail::to_string(static_cast<IntS>(value))} {
    }
};

class ExperimentalFeature : public InvalidArguments {
    using InvalidArguments::InvalidArguments;
};

class NotImplementedError : public PGMIOError {
  public:
    NotImplementedError() { append_msg("Function not yet implemented"); }
};

class UnreachableHit : public PGMIOError {
  public:
    UnreachableHit(std::string const& method, std::string const& reason_for_assumption) {
        append_msg("Unreachable code hit when executing " + method +
                   ".\n The following assumption for unreachability was not met: " + reason_for_assumption +
                   ".\n This may be a bug in the library\n");
    }
};

} // namespace power_grid_model_io_native
