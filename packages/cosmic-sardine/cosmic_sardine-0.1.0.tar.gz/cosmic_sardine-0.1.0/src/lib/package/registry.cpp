#include <sardine/error.hpp>
#include <sardine/package/registry.hpp>

#include <emu/associative_container.hpp>

namespace sardine::package
{

namespace registry
{
    using buffer_registry = emu::unordered_map<string, buffer_package_factory>;

    using memory_registry = emu::unordered_map<string, memory_package_factory>;

    buffer_registry& buffer_registry_instance() {
        static buffer_registry map;
        return map;
    }

    memory_registry& memory_registry_instance() {
        static memory_registry map;
        return map;
    }

    void register_buffer_package_factory(string&& scheme_name, buffer_package_factory&& creator) {
        buffer_registry_instance().emplace(std::move(scheme_name), std::move(creator));
    }

    void register_memory_package_factory(string&& scheme_name, memory_package_factory&& creator) {
        memory_registry_instance().emplace(std::move(scheme_name), std::move(creator));
    }

} // namespace registry

    result<s_buffer_package> url_to_buffer_package(const sardine::url_view& u, device_type_t requested_dt) {
        string_view scheme = u.scheme();

        {
            auto& buffer_registry_instance = registry::buffer_registry_instance();
#ifdef __cpp_lib_generic_unordered_lookup
            auto it = buffer_registry_instance.find(scheme);
#else
            auto it = buffer_registry_instance.find(string(scheme));
#endif
            if (it != buffer_registry_instance.end())
                return it->second(u, requested_dt);
        }
        {
            // memory packages can be used as buffer packages.
            auto& memory_registry_instance = registry::memory_registry_instance();
#ifdef __cpp_lib_generic_unordered_lookup
            auto it = memory_registry_instance.find(scheme);
#else
            auto it = memory_registry_instance.find(string(scheme));
#endif
     if (it != memory_registry_instance.end())
                return it->second(u, requested_dt).map(s_buffer_cast);
        }

        EMU_RETURN_UN_EC_LOG(errc::url_unknown_scheme,
            "No buffer package found for scheme: {}", scheme);
    }

    result<s_memory_package> url_to_memory_package(const sardine::url_view& u, device_type_t requested_dt) {
        string_view scheme = u.scheme();

        auto& memory_registry_instance = registry::memory_registry_instance();
#ifdef __cpp_lib_generic_unordered_lookup
        auto it = memory_registry_instance.find(scheme);
#else
        auto it = memory_registry_instance.find(string(scheme));
#endif
        if (it != memory_registry_instance.end())
            return it->second(u, requested_dt);

        EMU_RETURN_UN_EC_LOG(errc::url_unknown_scheme,
            "No memory package found for scheme: {}", scheme);
    }

} // namespace sardine::package
