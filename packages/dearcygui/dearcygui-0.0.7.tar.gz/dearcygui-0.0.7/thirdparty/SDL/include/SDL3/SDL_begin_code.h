/*
  Simple DirectMedia Layer
  Copyright (C) 1997-2024 Sam Lantinga <slouken@libsdl.org>

  This software is provided 'as-is', without any express or implied
  warranty.  In no event will the authors be held liable for any damages
  arising from the use of this software.

  Permission is granted to anyone to use this software for any purpose,
  including commercial applications, and to alter it and redistribute it
  freely, subject to the following restrictions:

  1. The origin of this software must not be misrepresented; you must not
     claim that you wrote the original software. If you use this software
     in a product, an acknowledgment in the product documentation would be
     appreciated but is not required.
  2. Altered source versions must be plainly marked as such, and must not be
     misrepresented as being the original software.
  3. This notice may not be removed or altered from any source distribution.
*/

/* WIKI CATEGORY: BeginCode */

/**
 * SDL_begin_code.h sets things up for C dynamic library function definitions,
 * static inlined functions, and structures aligned at 4-byte alignment.
 * If you don't like ugly C preprocessor code, don't look at this file. :)
 */

/* This shouldn't be nested -- included it around code only. */
#ifdef SDL_begin_code_h
#error Nested inclusion of SDL_begin_code.h
#endif
#define SDL_begin_code_h

#ifndef SDL_DEPRECATED
#  if defined(__GNUC__) && (__GNUC__ >= 4)  /* technically, this arrived in gcc 3.1, but oh well. */
#    define SDL_DEPRECATED __attribute__((deprecated))
#  elif defined(_MSC_VER)
#    define SDL_DEPRECATED __declspec(deprecated)
#  else
#    define SDL_DEPRECATED
#  endif
#endif

#ifndef SDL_UNUSED
#  ifdef __GNUC__
#    define SDL_UNUSED __attribute__((unused))
#  else
#    define SDL_UNUSED
#  endif
#endif

/* Some compilers use a special export keyword */
#ifndef SDL_DECLSPEC
# if defined(SDL_PLATFORM_WINDOWS)
#  ifdef DLL_EXPORT
#   define SDL_DECLSPEC __declspec(dllexport)
#  else
#   define SDL_DECLSPEC
#  endif
# else
#  if defined(__GNUC__) && __GNUC__ >= 4
#   define SDL_DECLSPEC __attribute__ ((visibility("default")))
#  else
#   define SDL_DECLSPEC
#  endif
# endif
#endif

/* By default SDL uses the C calling convention */
#ifndef SDLCALL
#if defined(SDL_PLATFORM_WINDOWS) && !defined(__GNUC__)
#define SDLCALL __cdecl
#else
#define SDLCALL
#endif
#endif /* SDLCALL */

/* Force structure packing at 4 byte alignment.
   This is necessary if the header is included in code which has structure
   packing set to an alternate value, say for loading structures from disk.
   The packing is reset to the previous value in SDL_close_code.h
 */
#if defined(_MSC_VER) || defined(__MWERKS__) || defined(__BORLANDC__)
#ifdef _MSC_VER
#pragma warning(disable: 4103)
#endif
#ifdef __clang__
#pragma clang diagnostic ignored "-Wpragma-pack"
#endif
#ifdef __BORLANDC__
#pragma nopackwarning
#endif
#ifdef _WIN64
/* Use 8-byte alignment on 64-bit architectures, so pointers are aligned */
#pragma pack(push,8)
#else
#pragma pack(push,4)
#endif
#endif /* Compiler needs structure packing set */

#ifndef SDL_INLINE
#ifdef __GNUC__
#define SDL_INLINE __inline__
#elif defined(_MSC_VER) || defined(__BORLANDC__) || \
      defined(__DMC__) || defined(__SC__) || \
      defined(__WATCOMC__) || defined(__LCC__) || \
      defined(__DECC) || defined(__CC_ARM)
#define SDL_INLINE __inline
#ifndef __inline__
#define __inline__ __inline
#endif
#else
#define SDL_INLINE inline
#ifndef __inline__
#define __inline__ inline
#endif
#endif
#endif /* SDL_INLINE not defined */

#ifndef SDL_FORCE_INLINE
#ifdef _MSC_VER
#define SDL_FORCE_INLINE __forceinline
#elif ( (defined(__GNUC__) && (__GNUC__ >= 4)) || defined(__clang__) )
#define SDL_FORCE_INLINE __attribute__((always_inline)) static __inline__
#else
#define SDL_FORCE_INLINE static SDL_INLINE
#endif
#endif /* SDL_FORCE_INLINE not defined */

#ifndef SDL_NORETURN
#ifdef __GNUC__
#define SDL_NORETURN __attribute__((noreturn))
#elif defined(_MSC_VER)
#define SDL_NORETURN __declspec(noreturn)
#else
#define SDL_NORETURN
#endif
#endif /* SDL_NORETURN not defined */

#ifdef __clang__
#if __has_feature(attribute_analyzer_noreturn)
#define SDL_ANALYZER_NORETURN __attribute__((analyzer_noreturn))
#endif
#endif

#ifndef SDL_ANALYZER_NORETURN
#define SDL_ANALYZER_NORETURN
#endif

/* Apparently this is needed by several Windows compilers */
#ifndef __MACH__
#ifndef NULL
#ifdef __cplusplus
#define NULL 0
#else
#define NULL ((void *)0)
#endif
#endif /* NULL */
#endif /* ! macOS - breaks precompiled headers */

#ifndef SDL_FALLTHROUGH
#if (defined(__cplusplus) && __cplusplus >= 201703L) || \
    (defined(__STDC_VERSION__) && __STDC_VERSION__ >= 202000L)
#define SDL_FALLTHROUGH [[fallthrough]]
#else
#if defined(__has_attribute) && !defined(__SUNPRO_C) && !defined(__SUNPRO_CC)
#define SDL_HAS_FALLTHROUGH __has_attribute(__fallthrough__)
#else
#define SDL_HAS_FALLTHROUGH 0
#endif /* __has_attribute */
#if SDL_HAS_FALLTHROUGH && \
   ((defined(__GNUC__) && __GNUC__ >= 7) || \
    (defined(__clang_major__) && __clang_major__ >= 10))
#define SDL_FALLTHROUGH __attribute__((__fallthrough__))
#else
#define SDL_FALLTHROUGH do {} while (0) /* fallthrough */
#endif /* SDL_HAS_FALLTHROUGH */
#undef SDL_HAS_FALLTHROUGH
#endif /* C++17 or C2x */
#endif /* SDL_FALLTHROUGH not defined */

#ifndef SDL_NODISCARD
#if (defined(__cplusplus) && __cplusplus >= 201703L) || \
    (defined(__STDC_VERSION__) && __STDC_VERSION__ >= 202311L)
#define SDL_NODISCARD [[nodiscard]]
#elif ( (defined(__GNUC__) && (__GNUC__ >= 4)) || defined(__clang__) )
#define SDL_NODISCARD __attribute__((warn_unused_result))
#elif defined(_MSC_VER) && (_MSC_VER >= 1700)
#define SDL_NODISCARD _Check_return_
#else
#define SDL_NODISCARD
#endif /* C++17 or C23 */
#endif /* SDL_NODISCARD not defined */

#ifndef SDL_MALLOC
#if defined(__GNUC__) && (__GNUC__ >= 3)
#define SDL_MALLOC __attribute__((malloc))
/** FIXME
#elif defined(_MSC_VER)
#define SDL_MALLOC __declspec(allocator) __desclspec(restrict)
**/
#else
#define SDL_MALLOC
#endif
#endif /* SDL_MALLOC not defined */

#ifndef SDL_ALLOC_SIZE
#if (defined(__clang__) && __clang_major__ >= 4) || (defined(__GNUC__) && (__GNUC__ > 4 || (__GNUC__ == 4 && __GNUC_MINOR__ >= 3)))
#define SDL_ALLOC_SIZE(p) __attribute__((alloc_size(p)))
#elif defined(_MSC_VER)
#define SDL_ALLOC_SIZE(p)
#else
#define SDL_ALLOC_SIZE(p)
#endif
#endif /* SDL_ALLOC_SIZE not defined */

#ifndef SDL_ALLOC_SIZE2
#if (defined(__clang__) && __clang_major__ >= 4) || (defined(__GNUC__) && (__GNUC__ > 4 || (__GNUC__ == 4 && __GNUC_MINOR__ >= 3)))
#define SDL_ALLOC_SIZE2(p1, p2) __attribute__((alloc_size(p1, p2)))
#elif defined(_MSC_VER)
#define SDL_ALLOC_SIZE2(p1, p2)
#else
#define SDL_ALLOC_SIZE2(p1, p2)
#endif
#endif /* SDL_ALLOC_SIZE2 not defined */
