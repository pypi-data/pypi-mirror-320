#include <sardine/region/host.hpp>
#include <sardine/region/host/utility.hpp>
#include <sardine/region/host/manager.hpp>
#include <sardine/error.hpp>
#include <sardine/memory_converter.hpp>
#include <sardine/config.hpp>

#include <emu/pointer.hpp>
#include <emu/charconv.hpp>

#include <boost/interprocess/detail/os_thread_functions.hpp>
#include <span>

namespace sardine::region::host
{

    span_b open_shm(string name, bool read_only) {
        return manager::instance().open_shm(std::move(name));
    }

    span_b create_shm(string name, size_t file_size, bool read_only) {
        return manager::instance().create_shm(std::move(name), file_size);
    }

    span_b open_or_create_shm(string name, size_t file_size, bool read_only) {
        return manager::instance().open_or_create_shm(std::move(name), file_size);
    }

    span_b open_file(fs::path path, bool read_only) {
        return manager::instance().open_file(fs::absolute(path));
    }

    span_b create_file(fs::path path, size_t file_size, bool read_only) {
        return manager::instance().create_file(fs::absolute(path), file_size);
    }

    span_b open_or_create_file(fs::path path, size_t file_size, bool read_only) {
        return manager::instance().open_or_create_file(fs::absolute(path), file_size);
    }

    inline auto handle_to_url(size_t size) {
        return [size](const region_handle& handle) -> result<url> {

            return (url()
                .set_scheme(url_scheme)
                .set_host(fmt::to_string(handle.r_kind))
                .segments() = { handle.name, fmt::to_string(handle.offset), fmt::to_string(size) })
                .url();


        };
    }

    optional<result<url>> url_from_bytes(span_cb data) {
        auto h2u = handle_to_url(data.size());


        if(auto handle = manager::instance().find_handle(data.data()); handle)
            return handle.map(h2u);


        // try to look for mapped files
        if(auto desc = emu::pointer_descritor_of(data.data()); desc) {
            auto& desc_ref = *desc;

            size_t offset = data.data() - desc_ref.base_region.data();

            auto absolute_path = fs::absolute(fs::path(desc_ref.location));

            optional<region_handle> res = nullopt;


            // if the file is in the shared memory path, we consider it as a shared memory region.
            if(absolute_path.parent_path() == shm_path_prefix) {
                auto filename = absolute_path.filename();

                res = region_handle{ .name=filename.c_str(), .offset=offset, .r_kind=ressource_kind::shm };

            // if the file is a regular file, we consider it as a file region.
            } else if (fs::exists(absolute_path) && fs::is_regular_file(absolute_path)){

                res = region_handle{ .name=absolute_path.c_str(), .offset=offset, .r_kind=ressource_kind::file };

            // if it is a local region, we consider it as a local region.
            } else if (desc_ref.location == "[heap]" or desc_ref.location == "[stack]") {
                // the name is the pid, just to check if it's a local region when opening the url.
                auto pid = boost::interprocess::ipcdetail::get_current_process_id();

                res = region_handle{ .name=fmt::to_string(pid), .offset=offset, .r_kind=ressource_kind::local };
            }
            return res.map(h2u);
        }

        return nullopt;
    }


    result<container_b> bytes_from_url(const url_view& url, device_type_t requested_dt) {
        auto r_kind = EMU_UNWRAP( ressource_kind_from(url.host()) );

        auto segments = url.segments();

        EMU_TRUE_OR_RETURN_UN_EC_LOG(segments.size() >= 3, errc::host_url_invalid_path,
            "Invalid segments number: {} in path {}", segments.size(), url.path());

        auto seg = segments.begin();

        // Put the region segment at the second last position.
        auto region_seg = segments.end(); region_seg--; region_seg--;

        span_b data;

        // first check if the memory is already open.
        if (r_kind == ressource_kind::shm or r_kind == ressource_kind::file) {
            fs::path path;
            switch (r_kind) {
                case ressource_kind::shm:
                    path = fs::path(shm_path_prefix) / *seg;
                    break;
                case ressource_kind::file:
                    {
                        path = (*seg).empty() ? fs::path("/") : fs::path(*seg);
                        while(++seg != region_seg) {
                            path /= *seg;
                        }
                    }
                    break;
            }

            if (auto maybe_data = emu::region_from_location(std::string(path)); maybe_data) {
                data = maybe_data.value();
            } else {
                switch (r_kind) {
                    case ressource_kind::shm:
                        data = open_shm(path.filename());
                    case ressource_kind::file:
                        data = open_file(path);
                }
            }

        } else if (r_kind == ressource_kind::local) {
            auto pid = boost::interprocess::ipcdetail::get_current_process_id();
            EMU_TRUE_OR_RETURN_UN_EC_LOG(*seg == fmt::to_string(pid), errc::host_non_local_region
                , "Trying to open a non local region from pid {} but current is {}.", *seg, pid);

            // create a span that will cover the whole memory region.
            data = span_b(reinterpret_cast<byte*>(0), std::dynamic_extent);
        }

        size_t offset = 0;
        EMU_RES_TRUE_OR_RETURN_UN_EC(emu::from_chars(*region_seg, offset));

        EMU_TRUE_OR_RETURN_UN_EC(offset <= data.size(), errc::host_url_offset_overflow);

        region_seg++;

        size_t size = 0;
        EMU_RES_TRUE_OR_RETURN_UN_EC(emu::from_chars(*region_seg, size));

        EMU_TRUE_OR_RETURN_UN_EC(offset + size <= data.size(), errc::host_url_size_overflow);

        return convert_bytes(
            bytes_and_device{
                .region=data,
                .data=data.subspan(offset, size),
                .device={
                    .device_type=emu::dlpack::device_type_t::kDLCPU,
                    .device_id=0
                }
            },
            requested_dt
        );
    }

} // namespace sardine::region::host
