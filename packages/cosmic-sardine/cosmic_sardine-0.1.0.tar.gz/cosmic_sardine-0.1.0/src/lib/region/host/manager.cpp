#include <sardine/region/host/manager.hpp>

#include <sardine/utility.hpp>

#include <fmt/format.h>

#include <fstream>

namespace sardine::region::host
{

    manager &manager::instance() {
        static manager instance;
        return instance;
    }

    span_b manager::open_shm(string name) {
        auto& h = find_or_emplace(static_cast<base&>(*this), name, [s = name.c_str()] {
            auto res = boost::interprocess::shared_memory_object(boost::interprocess::open_only, s, boost::interprocess::read_write);
            return handle(m_region(res, boost::interprocess::read_write), ressource_kind::shm);
        })->second;

        return map(h);
    }

    span_b manager::create_shm(string name, size_t size) {
        auto& h = emplace_or_throw(static_cast<base&>(*this), name, [s = name.c_str(), size] {
            auto res = boost::interprocess::shared_memory_object(boost::interprocess::create_only, s, boost::interprocess::read_write);
            res.truncate(size);
            return handle(m_region(res, boost::interprocess::read_write), ressource_kind::shm);
        })->second;

        return map(h);
    }

    span_b manager::open_or_create_shm(string name, size_t size) {
        auto& h = find_or_emplace(static_cast<base&>(*this), name, [s = name.c_str(), size] {
            auto res = boost::interprocess::shared_memory_object(boost::interprocess::open_or_create, s, boost::interprocess::read_write);
            res.truncate(size);
            return handle(m_region(res, boost::interprocess::read_write), ressource_kind::shm);
        })->second;

        return map(h);
    }

    span_b manager::open_file(string path) {
        auto& h = find_or_emplace(static_cast<base&>(*this), path, [p = path.c_str()] {
            fmt::print("Opening file {}\n", p);
            auto res = boost::interprocess::file_mapping(p, boost::interprocess::read_write);
            return handle(m_region(res, boost::interprocess::read_write), ressource_kind::file);
        })->second;

        return map(h);
    }

    span_b manager::create_file(string path, size_t size) {
        auto& h = emplace_or_throw(static_cast<base&>(*this), path, [p = path.c_str(), size] {
            {  //Create a file
                std::filebuf fbuf;
                fbuf.open(p, std::ios_base::in | std::ios_base::out
                                    | std::ios_base::trunc | std::ios_base::binary);
                //Set the size
                fbuf.pubseekoff(size - 1, std::ios_base::beg);
                fbuf.sputc(0);
            }
            auto res = boost::interprocess::file_mapping(p, boost::interprocess::read_write);
            return handle(m_region(res, boost::interprocess::read_write), ressource_kind::file);
        })->second;

        return map(h);
    }

    span_b manager::open_or_create_file(string path, size_t size) {
        auto& h = find_or_emplace(static_cast<base&>(*this), path, [p = path.c_str(), size] {
            {  //Create a file
                std::filebuf fbuf;
                fbuf.open(p, std::ios_base::in | std::ios_base::out
                                    | std::ios_base::trunc | std::ios_base::binary);
                //Set the size
                fbuf.pubseekoff(size - 1, std::ios_base::beg);
                fbuf.sputc(0);
            }
            auto res = boost::interprocess::file_mapping(p, boost::interprocess::read_write);
            return handle(m_region(res, boost::interprocess::read_write), ressource_kind::file);
        })->second;

        return map(h);
    }

    span_b manager::at(emu::cstring_view name) {
// #ifdef __cpp_lib_generic_unordered_lookup
        auto it = base::find(name);
// #else
//         auto it = base::find(string(name));
// #endif

        EMU_TRUE_OR_THROW_LOG(it != base::end(), errc::host_unknown_region,
            "No region named {} exists.", name);

        return map(it->second);
    }

    optional<region_handle> manager::find_handle(const byte* ptr) {
        for (auto& [name, h] : static_cast<base&>(*this)) {
            auto addr = reinterpret_cast<const byte*>(h.region.get_address());
            auto size = h.region.get_size();

            if (addr <= ptr && ptr < addr + size) {
                return region_handle{name, static_cast<size_t>(ptr - addr), h.r_kind};
            }
        }
        return emu::nullopt;
    }


} // namespace sardine::region::host
