#include <sardine/region_register.hpp>
#include <sardine/error.hpp>

#include <list>

namespace sardine
{

namespace registry
{

    using bytes_to_url_list = std::list<bytes_to_url_t>;

    bytes_to_url_list& bytes_to_url_instance() {
        static bytes_to_url_list list;
        return list;
    }

    void register_url_region_converter( string scheme_name, bytes_to_url_t btu ) {
        bytes_to_url_instance().push_back(std::move(btu));
    }

} // namespace registry

    optional<result<url>> dynamic_url_from_bytes( span_cb data ) {
        for (auto& converter : registry::bytes_to_url_instance())
            if (auto res = converter(data); res)
                return *res;

        return nullopt;
    }

} // namespace sardine
