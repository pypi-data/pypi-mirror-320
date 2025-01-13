#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <config.hpp>

#include <sardine/sardine.hpp>

using namespace sardine;

namespace
{

    TEST(Box, ManagedIntegerBox)
    {
        auto managed = region::managed::open_or_create(managed_filename, managed_filesize);

        host_context ctx;

        int& scalar = managed.force_create<int>("integer_box", 42);

        ASSERT_EQ(scalar, 42);

        auto maybe_url = sardine::url_of(scalar);

        ASSERT_TRUE(maybe_url) << "Could not create url: " << maybe_url.error().message();

        auto url = maybe_url.value();

        ASSERT_EQ(url.scheme(), region::host::url_scheme);
        ASSERT_EQ(url.host(), region::host::shm_idenfier);

        auto maybe_box = box<int&>::open(url);

        ASSERT_TRUE(maybe_box) << "Could not open url: " << maybe_box.error().message() << " with url: " << url;

        auto b = maybe_box.value();

        ASSERT_EQ(b.value, 42);

        scalar = 43;

        ASSERT_EQ(b.value, 42);

        b.recv(ctx);

        ASSERT_EQ(b.value, 43);

        b.value = 44;

        ASSERT_EQ(scalar, 43);

        b.send(ctx);

        ASSERT_EQ(scalar, 44);
    }

} // namespace
