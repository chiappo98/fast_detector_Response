/*
 * Copyright 2020-2022 N. Tosi, V. Pia <nicolo.tosi@bo.infn.it>
 *
 * This program is free software:
 * you can redistribute it and/or modify it under the terms of the GNU
 * Lesser General Public License as published by the Free Software Foundation,
 * either version 3 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

/** \mainpage Detector Response Data Format */

#include <array>
#include <cstdint>
#include <map>
#include <vector>
#include <uuid/uuid.h>

namespace drdf
 {

  typedef uint32_t checksum_t;

/** The event identifier is an unsigned 32-bit number. */
  typedef uint32_t eventid_t;

/** A file is identified globally using an URI type string. */
  typedef std::string uri_t;

/** Sensors are identified by their name, an ASCII-only string. */
  typedef std::string sourceid_t;

/** A run is identified by a 128-bit Universally Unique Identifier (RFC4122
 * type 1, since having the host ID and time is not a bad thing in this case).*/
  struct run_uuid_t
   {
    ::uuid_t uuid;
   };

  inline bool operator < (const run_uuid_t& lhs, const run_uuid_t& rhs)
   {
    return ::uuid_compare(lhs.uuid, rhs.uuid) < 0;
   }

  inline bool operator == (const run_uuid_t& lhs, const run_uuid_t& rhs)
   {
    return ::uuid_compare(lhs.uuid, rhs.uuid) == 0;
   }

/** Produces a new type-1 unique id (calls uuid_generate_time)*/
  run_uuid_t get_uuid();

  std::string to_string(const run_uuid_t&);

/** Pixel format code. */
  enum ifmttype_t : uint8_t
   {
    Au8 = 0, /*< Amplitude, 8 bit unsigned. */
    Au8Tu8, /*< Amplitude, 8 bit unsigned and Timestamp, 8 bit unsigned. */
    Au16, /*< Amplitude, 16 bit unsigned. */
    Au16Tu16, /*< Amplitude, 16 bit unsigned and Timestamp, 16 bit unsigned. */
    Af32Tf32, /*< Amplitude, 32 bit float and Timestamp, 32 bit float. */
   };

  struct __attribute__ ((packed)) ifmt_t
   {
    uint16_t size_x;
    uint16_t size_y;
    ifmttype_t pixelfmt;
    uint8_t _reserved1;
    uint16_t _reserved2;
    uint32_t size() const;
   };

  struct pixtype_Au8_t
   {
    uint8_t amplitude;
    static constexpr ifmttype_t fmttype = Au8;
   };

  struct pixtype_Au8Tu8_t
   {
    uint8_t amplitude;
    uint8_t time;
    static constexpr ifmttype_t fmttype = Au8Tu8;
   };

  struct pixtype_Au16_t
   {
    uint16_t amplitude;
    static constexpr ifmttype_t fmttype = Au16;
   };

  struct pixtype_Au16Tu16_t
   {
    uint16_t amplitude;
    uint16_t time;
    static constexpr ifmttype_t fmttype = Au16Tu16;
   };

  struct pixtype_Af32Tf32_t
   {
    float amplitude;
    float time;
    static constexpr ifmttype_t fmttype = Af32Tf32;
   };

/** Typeless image. Users should use @c image_t<T> instead. */
  class image_base_t
   {
    public:
    image_base_t(ifmt_t);
    image_base_t(ifmt_t, const void*);
    ~image_base_t();
    image_base_t(image_base_t&&);
    image_base_t(const image_base_t&);
    image_base_t& operator = (image_base_t&&);
    uint32_t size() const
     { return m_format.size(); }
    const void* pixels() const
     { return m_array_data; };
    const ifmt_t& format() const
     { return m_format; }
    protected:
    ifmt_t m_format;
    void* m_array_data;
   };

/** Image class, templated on Pixel Type.*/
  template <typename Pixtype>
  class image_t : public image_base_t
   {

    public:
    typedef Pixtype pixel_t;

    public:
/** Construct an empty image of size @p sx by @p sy pixels.*/
    image_t(uint16_t sx, uint16_t sy) : image_base_t(ifmt_t{sx, sy, pixel_t::fmttype})
     {}

/** Construct an empty image with format @p fmt .*/
    image_t(ifmt_t fmt) : image_base_t(fmt)
     {}

/** Construct an image with format @p fmt and initialize it from @p pxls .
    @p pxls is assumed to be a valid pointer to a pixel array of the correct format.
    It is copied into this image and left unmodified.*/
    image_t(ifmt_t fmt, const pixel_t* pxls) : image_base_t(fmt, pxls)
     {}

    image_t(const image_t&) = default;

    image_t(image_t&&) = default;

    image_t& operator = (image_t&&) = default;

    image_t& operator = (const image_t&) = delete;

/** Write access to pixel at @p x, @p y, starting from 0, 0 as the upper left corner.*/
    pixel_t& at(uint32_t x, uint32_t y)
     {
      if (x >= m_format.size_x || y >= m_format.size_y)
        throw std::out_of_range("Pixel index out of range");
      return pixels()[x + y * m_format.size_x];
     }

/** Read access to pixel at @p x, @p y, starting from 0, 0 as the upper left corner.*/
    pixel_t at(uint32_t x, uint32_t y) const
     {
      if (x >= m_format.size_x || y >= m_format.size_y)
        throw std::out_of_range("Pixel index out of range");
      return pixels()[x + y * m_format.size_x];
     }

    pixel_t* pixels()
     {
      return static_cast<pixel_t*>(m_array_data);
     }

    const pixel_t* pixels() const
     {
      return static_cast<const pixel_t*>(m_array_data);
     }

    uint32_t height() const
     {
      return m_format.size_y;
     }

    uint32_t width() const
     {
      return m_format.size_x;
     }

   };


/** Detector Response Data Format class

    This class provides methods for reading a drdf file into dictionary type structures
    as well as the reverse process.
    Generally, after loading a file with \ref read(), one would either use the iterator
    based interface (\ref begin(), \ref end()) to traverse the file or \ref find() to access a
    a specific item.
    In order to produce an output file, \ref start_run(), \ref start_event() and
    \ref add_image() allow to populate the data structures, and \ref write() places
    them in the actual output file.*/
  class drdf
   {

    public:
    typedef std::map<sourceid_t, image_base_t> event_map_t;
    struct run_map_t : public std::map<eventid_t, event_map_t>
     {
      public:
      run_map_t() : std::map<eventid_t, event_map_t>(), georef() {}
      public:
      uri_t georef;
     };
    typedef std::map<run_uuid_t, run_map_t> file_map_t;
    typedef file_map_t::const_iterator const_iterator;
/*
    template <typename Pixtype>
    class const_iterator
     {
      public:
      using iterator_category = std::bidirectional_iterator_tag;
      using value_type = const image_t<Pixtype>;
      using pointer = const image_t<Pixtype>*;
      using reference = const image_t<Pixtype>&;
      bool operator == (const const_iterator& rhs) const
       { return m_run == rhs.m_run && m_event == rhs.m_event && m_image == rhs.m_image; }
      bool operator != (const const_iterator& rhs) const
       { return !(*this == rhs); }
      reference operator * () const
       { return *static_cast<pointer>(m_image->second); }
      pointer operator -> () const
       { return static_cast<pointer>(m_image->second); }
      const_iterator& operator ++ ()
       { (m_image != m_event->second.end()) ? ++m_image : ((m_event != m_run->second.end()) ? (m_image = (++m_event)->second.begin()) : (m_image = (m_event = (++m_run)->second.begin())->second.begin())); return *this; }
      const_iterator operator ++ (int)
       { auto old = *this; ++(*this); return old; }
      const_iterator& operator -- ()
       { (m_image != m_event->second.begin()) ? --m_image : ((m_event != m_run->second.begin()) ? (m_image = --(--m_event)->second.end()) : (m_image = --(m_event = --(--m_run)->second.end())->second.end())); return *this; }
      const_iterator operator -- (int)
       { auto old = *this; --(*this); return old; }
      sourceid_t source() const
       { return m_image->first; }
      eventid_t event() const
       { return m_event->first; }
      run_uuid_t run() const
       { return m_run->first; }
      private:
      friend class drdf;
      const_iterator(file_map_t::const_iterator run, run_map_t::const_iterator evt, event_map_t::const_iterator img) : m_run(run), m_event(evt), m_image(img){}
      file_map_t::const_iterator m_run;
      run_map_t::const_iterator m_event;
      event_map_t::const_iterator m_image;
     };

    template <typename Pixtype>
    class iterator
     {
      public:
      using iterator_category = std::bidirectional_iterator_tag;
      using value_type = image_t<Pixtype>;
      using pointer = image_t<Pixtype>*;
      using reference = image_t<Pixtype>&;
      iterator(const const_iterator<Pixtype>& rhs) : m_run(rhs.m_run), m_event(rhs.m_event), m_image(rhs.m_image)
       {}
      bool operator == (const iterator& rhs) const
       { return m_run == rhs.m_run && m_event == rhs.m_event && m_image == rhs.m_image; }
      bool operator != (const iterator& rhs) const
       { return !(*this == rhs); }
      reference operator * () const
       { return *static_cast<pointer>(m_image->second); }
      pointer operator -> () const
       { return static_cast<pointer>(m_image->second); }
      iterator& operator ++ ()
       { (m_image != m_event->second.end()) ? ++m_image : ((m_event != m_run->second.end()) ? (m_image = (++m_event)->second.begin()) : (m_image = (m_event = (++m_run)->second.begin())->second.begin())); return *this; }
      iterator operator ++ (int)
       { auto old = *this; ++(*this); return old; }
      iterator& operator -- ()
       { (m_image != m_event->second.begin()) ? --m_image : ((m_event != m_run->second.begin()) ? (m_image = --(--m_event)->second.end()) : (m_image = --(m_event = --(--m_run)->second.end())->second.end())); return *this; }
      iterator operator -- (int)
       { auto old = *this; --(*this); return old; }
      sourceid_t source() const
       { return m_image->first; }
      eventid_t event() const
       { return m_event->first; }
      run_uuid_t run() const
       { return m_run->first; }
      private:
      friend class drdf;
      iterator(file_map_t::iterator run, run_map_t::iterator evt, event_map_t::iterator img) : m_run(run), m_event(evt), m_image(img){}
      file_map_t::iterator m_run;
      run_map_t::iterator m_event;
      event_map_t::iterator m_image;
     };
*/
    public:
    drdf();

    /** Writes the current contentes of this class to @p fname .*/
    void write(uri_t fname);

    /** Reads @p fname into a new instance of this class.*/
    static drdf read(uri_t fname);
/*
    template <typename Pixtype>
    const_iterator<Pixtype> begin() const
     {
      if (m_runs.begin() != m_runs.end())
       {
        if (m_runs.begin()->second.begin() != m_runs.begin()->second.end())
          return const_iterator<Pixtype>(m_runs.begin(), m_runs.begin()->second.begin(), m_runs.begin()->second.begin()->second.begin());
        else
          return const_iterator<Pixtype>(m_runs.begin(), m_runs.begin()->second.begin(), event_map_t::const_iterator());
       }
      else
        return const_iterator<Pixtype>(m_runs.begin(), run_map_t::const_iterator(), event_map_t::const_iterator());
     }

    template <typename Pixtype>
    iterator<Pixtype> begin()
     {
      if (m_runs.begin() != m_runs.end())
       {
        if (m_runs.begin()->second.begin() != m_runs.begin()->second.end())
          return iterator<Pixtype>(m_runs.begin(), m_runs.begin()->second.begin(), m_runs.begin()->second.begin()->second.begin());
        else
          return iterator<Pixtype>(m_runs.begin(), m_runs.begin()->second.begin(), event_map_t::iterator());
       }
      else
        return iterator<Pixtype>(m_runs.begin(), run_map_t::iterator(), event_map_t::iterator());
     }

    template <typename Pixtype>
    const_iterator<Pixtype> end() const
     {
      if (m_runs.begin() != m_runs.end())
       {
        if (m_runs.begin()->second.begin() != m_runs.begin()->second.end())
          return const_iterator<Pixtype>(m_runs.end(), (--m_runs.end())->second.end(), (--(--m_runs.end())->second.end())->second.end());
        else
          return const_iterator<Pixtype>(m_runs.end(), (--m_runs.end())->second.end(), event_map_t::const_iterator());
       }
      else
        return const_iterator<Pixtype>(m_runs.end(), run_map_t::const_iterator(), event_map_t::const_iterator());
     }

    template <typename Pixtype>
    iterator<Pixtype> end()
     {
      if (m_runs.begin() != m_runs.end())
       {
        if (m_runs.begin()->second.begin() != m_runs.begin()->second.end())
          return iterator<Pixtype>(m_runs.end(), (--m_runs.end())->second.end(), (--(--m_runs.end())->second.end())->second.end());
        else
          return iterator<Pixtype>(m_runs.end(), (--m_runs.end())->second.end(), event_map_t::iterator());
       }
      else
        return iterator<Pixtype>(m_runs.end(), run_map_t::iterator(), event_map_t::iterator());
     }
*/
    /** Returns a @p const_iterator to the first run. */
    const_iterator begin() const
     {
      return m_runs.begin();
     }

    /** Returns a @p const_iterator to the last run. */
    const_iterator end() const
     {
      return m_runs.end();
     }

    /** Returns a @p const_iterator to the run with UUID @p run. */
    const_iterator find(run_uuid_t run) const
     {
      return m_runs.find(run);
     }

    /** Returns a pointer to the unique image identified by run, event and signal source. */
    const image_base_t* find(run_uuid_t, eventid_t, sourceid_t) const;

    /** Begins a new run with UUID @p run . All subsequent events will be part of this run. */
    void start_run(run_uuid_t run);

    void set_georef(const uri_t&);

    /** Begins a new event with event ID @p evt . All subsequent images will be part of this event. */
    void start_event(eventid_t evt);

    /** Adds a new image with source id @p src, copied from @p img. */
    template <typename Pixtype>
    void add_image(sourceid_t src, const image_t<Pixtype>& img)
     {
      if (m_event == m_run->second.end())
        throw std::out_of_range("Cannot add image to null event");
      m_event->second.emplace(src, img);
     }

    /** Moves a new image with source id @p src and data @p img.
        The contents of @p img are undefined after the operation. */
    template <typename Pixtype>
    void move_image(sourceid_t src, image_t<Pixtype>&& img)
     {
      if (m_event == m_run->second.end())
        throw std::out_of_range("Cannot add image to null event");
      m_event->second.emplace(src, std::move(img));
     }

    private:
    static std::array<checksum_t, 256> generate_crc_table();

    static checksum_t crc32(checksum_t, const char*, const char*);

    static checksum_t write_chunk(std::ofstream&, const char*, uint32_t, const void*, checksum_t);

    private:
    file_map_t m_runs;
    file_map_t::iterator m_run;
    run_map_t::iterator m_event;

   };

  }
