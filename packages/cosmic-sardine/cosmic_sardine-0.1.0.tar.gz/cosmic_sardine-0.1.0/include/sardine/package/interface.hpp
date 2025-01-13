#pragma once

#include <sardine/buffer/interface.hpp>
#include <sardine/mapping.hpp>

#include <sardine/context.hpp>

#include <memory>

namespace sardine::package
{

namespace interface
{

    struct buffer_package
    {

        virtual ~buffer_package() = default;

        virtual buffer::interface::producer& producer() = 0;
        virtual buffer::interface::consumer& consumer() = 0;

        virtual const sardine::interface::mapping& mapping() const = 0;
    };

    struct memory_package : buffer_package
    {

        // returns byte and a capsule.
        virtual span_b bytes() = 0;

    };

} // namespace interface

    using s_buffer_package = std::shared_ptr< interface::buffer_package >;

    using s_memory_package = std::shared_ptr< interface::memory_package >;

    /**
     * @brief Function to cast a memory_translator into a buffer_translator.
     *
     */
    inline s_buffer_package s_buffer_cast(s_memory_package mp) noexcept {
        return mp;
    }

} // namespace sardine::package
