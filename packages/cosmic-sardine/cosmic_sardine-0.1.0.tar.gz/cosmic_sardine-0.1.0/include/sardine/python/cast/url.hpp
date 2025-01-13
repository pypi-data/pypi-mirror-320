#pragma once

#include <sardine/type/url.hpp>

#include <emu/pybind11.hpp>
#include <emu/optional.hpp>

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace sardine::cast::url
{

    inline py::module_ parse_module() {
        return py::module_::import("urllib").attr("parse");
    }

    // inline py::handle to_handle(sardine::url_view u) {
    //     auto buff = u.buffer();
    //     return py::str(buff.data(), buff.size()).inc_ref();
    // }

    inline py::handle select_handle(py::handle h) {
        if (py::isinstance(h, parse_module().attr("ParseResult")) )
            return h.attr("geturl")();

        return h;
    }

} // namespace sardine::cast::url

PYBIND11_NAMESPACE_BEGIN(PYBIND11_NAMESPACE)

namespace detail
{

    template <typename URLType, bool IsView = false>
    struct url_caster {
        using CharT = char;

        // Simplify life by being able to assume standard char sizes (the standard only guarantees
        // minimums, but Python requires exact sizes)
        static_assert(!std::is_same<CharT, char>::value || sizeof(CharT) == 1,
                    "Unsupported char size != 1");
    #if defined(PYBIND11_HAS_U8STRING)
        static_assert(!std::is_same<CharT, char8_t>::value || sizeof(CharT) == 1,
                    "Unsupported char8_t size != 1");
    #endif
        static_assert(!std::is_same<CharT, char16_t>::value || sizeof(CharT) == 2,
                    "Unsupported char16_t size != 2");
        static_assert(!std::is_same<CharT, char32_t>::value || sizeof(CharT) == 4,
                    "Unsupported char32_t size != 4");
        // wchar_t can be either 16 bits (Windows) or 32 (everywhere else)
        static_assert(!std::is_same<CharT, wchar_t>::value || sizeof(CharT) == 2 || sizeof(CharT) == 4,
                    "Unsupported wchar_t size != 2/4");
        static constexpr size_t UTF_N = 8 * sizeof(CharT);

        bool load(handle src, bool) {
            handle load_src = sardine::cast::url::select_handle(src);
            if (!src) {
                return false;
            }
            if (!PyUnicode_Check(load_src.ptr())) {
                return load_raw(load_src);
            }

            // For UTF-8 we avoid the need for a temporary `bytes` object by using
            // `PyUnicode_AsUTF8AndSize`.
            if (UTF_N == 8) {
                Py_ssize_t size = -1;
                const auto *buffer
                    = reinterpret_cast<const CharT *>(PyUnicode_AsUTF8AndSize(load_src.ptr(), &size));
                if (!buffer) {
                    PyErr_Clear();
                    return false;
                }
                value = URLType(std::string_view(buffer, static_cast<size_t>(size)));
                return true;
            }

            auto utfNbytes
                = reinterpret_steal<object>(PyUnicode_AsEncodedString(load_src.ptr(),
                                                                    UTF_N == 8    ? "utf-8"
                                                                    : UTF_N == 16 ? "utf-16"
                                                                                    : "utf-32",
                                                                    nullptr));
            if (!utfNbytes) {
                PyErr_Clear();
                return false;
            }

            const auto *buffer
                = reinterpret_cast<const CharT *>(PYBIND11_BYTES_AS_STRING(utfNbytes.ptr()));
            size_t length = (size_t) PYBIND11_BYTES_SIZE(utfNbytes.ptr()) / sizeof(CharT);
            // Skip BOM for UTF-16/32
            if (UTF_N > 8) {
                buffer++;
                length--;
            }
            value = URLType(std::string_view(buffer, length));

            // If we're loading a string_view we need to keep the encoded Python object alive:
            if constexpr (IsView) {
                loader_life_support::add_patient(utfNbytes);
            }

            return true;
        }

        static handle
        cast(const URLType &src, return_value_policy /* policy */, handle /* parent */) {
            const char *buffer = reinterpret_cast<const char *>(src.data());
            auto nbytes = ssize_t(src.size() * sizeof(CharT));
            handle s = decode_utfN(buffer, nbytes);
            if (!s) {
                throw error_already_set();
            }
            return s;
        }

        PYBIND11_TYPE_CASTER(URLType, const_name(PYBIND11_STRING_NAME));

    private:
        static handle decode_utfN(const char *buffer, ssize_t nbytes) {
    #if !defined(PYPY_VERSION)
            return UTF_N == 8    ? PyUnicode_DecodeUTF8(buffer, nbytes, nullptr)
                : UTF_N == 16 ? PyUnicode_DecodeUTF16(buffer, nbytes, nullptr, nullptr)
                                : PyUnicode_DecodeUTF32(buffer, nbytes, nullptr, nullptr);
    #else
            // PyPy segfaults when on PyUnicode_DecodeUTF16 (and possibly on PyUnicode_DecodeUTF32 as
            // well), so bypass the whole thing by just passing the encoding as a string value, which
            // works properly:
            return PyUnicode_Decode(buffer,
                                    nbytes,
                                    UTF_N == 8    ? "utf-8"
                                    : UTF_N == 16 ? "utf-16"
                                                : "utf-32",
                                    nullptr);
    #endif
        }

        // When loading into a std::string or char*, accept a bytes/bytearray object as-is (i.e.
        // without any encoding/decoding attempt).  For other C++ char sizes this is a no-op.
        // which supports loading a unicode from a str, doesn't take this path.
        template <typename C = CharT>
        bool load_raw(enable_if_t<std::is_same<C, char>::value, handle> src) {
            if (PYBIND11_BYTES_CHECK(src.ptr())) {
                // We were passed raw bytes; accept it into a std::string or char*
                // without any encoding attempt.
                const char *bytes = PYBIND11_BYTES_AS_STRING(src.ptr());
                if (!bytes) {
                    pybind11_fail("Unexpected PYBIND11_BYTES_AS_STRING() failure.");
                }
                value = URLType(std::string_view(bytes, (size_t) PYBIND11_BYTES_SIZE(src.ptr())));
                return true;
            }
            if (PyByteArray_Check(src.ptr())) {
                // We were passed a bytearray; accept it into a std::string or char*
                // without any encoding attempt.
                const char *bytearray = PyByteArray_AsString(src.ptr());
                if (!bytearray) {
                    pybind11_fail("Unexpected PyByteArray_AsString() failure.");
                }
                value = URLType(std::string_view(bytearray, (size_t) PyByteArray_Size(src.ptr())));
                return true;
            }

            return false;
        }

        template <typename C = CharT>
        bool load_raw(enable_if_t<!std::is_same<C, char>::value, handle>) {
            return false;
        }
    };

    template<>
    struct type_caster< sardine::url > : url_caster<sardine::url, /* IsVIew = */ false> {};

    template<>
    struct type_caster< sardine::url_view > : url_caster<sardine::url_view, /* IsVIew = */ true> {};

} // namespace detail

PYBIND11_NAMESPACE_END(PYBIND11_NAMESPACE)
