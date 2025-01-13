#pragma once

#include <sardine/milk/type.hpp>
#include <sardine/milk/array/shm/handle.hpp>

#include <string>
#include <cstddef>
#include <span>
#include <type_traits>

namespace sardine
{

namespace milk
{

    void remove_array(cstring_view name);

    struct ArrayBase
    {
        using image_t = array::image_t;
        using s_image_t = array::s_image_t;
        using ScopedSemIndex = array::ScopedSemIndex;

        ArrayBase() = default;

        ArrayBase(s_image_t&& h, bool blocking);

        ArrayBase(ArrayBase && array) = default;
        ArrayBase(const ArrayBase & array);

        ArrayBase& operator=(ArrayBase && array) = default;
        ArrayBase& operator=(const ArrayBase & array);

        ~ArrayBase() = default;

        result<ArrayBase> convert_to(emu::dlpack::device_type_t requested_dt) const;

        array::image_t& handle();
        const array::image_t& handle() const;

        s_image_t handle_ptr() const { return handle_; }

        void recv();

        /// Increment shared index and sem notify.
        /// Also increment local if behind.
        void send();


        /// Check if local is behind.
        bool available() const;

        void next();

        uint64_t index() const;
        uint64_t next_index() const;
        void set_index(uint64_t index);

        size_t distance() const {
            auto ci = index();
            auto ni = next_index();
            if (ci <= ni) {
                return ni - ci;
            } else {
                return ni + buffer_nb() - ci;
            }
        }


        size_t buffer_nb() const;
        /// Number of buffer
        size_t rank() const;
        /// Number of element in a buffer.
        size_t size() const;
        /// Size in byte in a buffer.
        size_t size_byte() const;

        /// Shape of a buffer.
        span<const size_t> extents() const;


        /// Pointer to the first buffer.
        span_b base_bytes() const;
        /// Pointer to the active local buffer.
        span_b bytes() const;

        dtype_t dtype() const;
        size_t item_size() const;

        /// Return data location
        int location() const;

        // cstring_view sem_name() const;
        cstring_view name() const;

        sardine::url url_of() const;

        sardine::url url_of_current() const;

    private:
        s_image_t handle_;
        container_b data_;

        uint64_t local_index;
        ScopedSemIndex sem_index;
        bool blocking;
    };

    template<typename T>
    struct Array : ArrayBase
    {
        using ArrayBase::ArrayBase;

        using value_type = T;

        span<T> base_view() const { return emu::as_t<T>(base_bytes()); }
        span<T> view() const { return emu::as_t<T>(bytes()); }
    };

    ArrayBase from_url(url_view u);

    ArrayBase open(string name, bool blocking = true);

    ArrayBase create(string name, span<const size_t> extents, size_t buffer_nb, dtype_t type, int location, bool blocking = true);

    ArrayBase open_or_create(string name, span<const size_t> extents, size_t buffer_nb, dtype_t type, int location, bool blocking = true);

    template<typename T>
    Array<T> open(string name, bool blocking = true) {
        auto array = open(name, blocking);

        if (array.dtype() != emu::dlpack::data_type_ext<T>) {
            throw std::runtime_error("Array type mismatch.");
        }

        return {std::move(array)};
    }

    template<typename T>
    Array<T> create(string name, span<const size_t> extents, size_t buffer_nb, int location, bool blocking = true) {
        return {create(name, extents, buffer_nb, emu::dlpack::data_type_ext<T>, location, blocking)};
    }

    template<typename T>
    Array<T> open_or_create(string name, span<const size_t> extents, size_t buffer_nb, int location, bool blocking = true) {
        auto array = open_or_create(name, extents, buffer_nb, emu::dlpack::data_type_ext<T>, location, blocking);

        if (array.dtype() != emu::dlpack::data_type_ext<T>) {
            throw std::runtime_error("Array type mismatch.");
        }

        return {std::move(array)};
    }


namespace host
{

    ArrayBase open(string name, bool blocking = true);

    ArrayBase create(string name, span<const size_t> extents, size_t buffer_nb, dtype_t type, bool blocking = true);

    ArrayBase open_or_create(string name, span<const size_t> extents, size_t buffer_nb, dtype_t type, bool blocking = true);

    template<typename T>
    Array<T> open(string name, bool blocking = true) {
        return {open(name, blocking)};
    }

    template<typename T>
    Array<T> create(string name, span<const size_t> extents, size_t buffer_nb, bool blocking = true) {
        return {create(name, extents, buffer_nb, emu::dlpack::data_type_ext<T>, blocking)};
    }

    template<typename T>
    Array<T> open_or_create(string name, span<const size_t> extents, size_t buffer_nb, bool blocking = true) {
        return {open_or_create(name, extents, buffer_nb, emu::dlpack::data_type_ext<T>, blocking)};
    }

} // namespace host

namespace cuda
{

    ArrayBase open(string name, bool blocking = true);

    ArrayBase create(string name, span<const size_t> extents, size_t buffer_nb, dtype_t type, int location, bool blocking = true);

    ArrayBase open_or_create(string name, span<const size_t> extents, size_t buffer_nb, dtype_t type, int location, bool blocking = true);

    template<typename T>
    Array<T> open(string name, bool blocking = true) {
        return {open(name, blocking)};
    }

    template<typename T>
    Array<T> create(string name, span<const size_t> extents, size_t buffer_nb, int location, bool blocking = true) {
        return {create(name, extents, buffer_nb, emu::dlpack::data_type_ext<T>, location, blocking)};
    }

    template<typename T>
    Array<T> open_or_create(string name, span<const size_t> extents, size_t buffer_nb, int location, bool blocking = true) {
        return {open_or_create(name, extents, buffer_nb, emu::dlpack::data_type_ext<T>, location, blocking)};
    }

} // namespace cuda

} // namespace milk

} // namespace sardine
