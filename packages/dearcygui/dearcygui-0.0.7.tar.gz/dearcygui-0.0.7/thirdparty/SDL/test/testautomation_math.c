/**
 * Math test suite
 */

#include <float.h>
#include <math.h>

#include <SDL3/SDL.h>
#include <SDL3/SDL_test.h>
#include "testautomation_suites.h"

/* ================= Test Constants ================== */

/* Range tests parameters */
#define RANGE_TEST_ITERATIONS 10000000
#define RANGE_TEST_STEP       ((Uint32)(SDL_MAX_UINT32 / RANGE_TEST_ITERATIONS))

/* Margin of error for imprecise tests */
#define EPSILON 1.0E-10

/* Euler constant (used in exp/log) */
#ifndef M_E
#define EULER 2.7182818284590450907955982984276488423347473144531250
#else
#define EULER M_E
#endif

#define IS_INFINITY(V) ISINF(V)

/* Square root of 3 (used in atan2) */
#define SQRT3 1.7320508075688771931766041234368458390235900878906250

/* ================= Test Structs ================== */

/**
 * Stores a single input and the expected result
 */
typedef struct
{
    double input;
    double expected;
} d_to_d;

/**
 * Stores a pair of inputs and the expected result
 */
typedef struct
{
    double x_input, y_input;
    double expected;
} dd_to_d;

/*
    NB: You cannot create an array of these structures containing INFINITY or NAN.
    On platforms such as OS/2, they are defined as 'extern const double' making them
    not compile-time constant.
*/

/* ================= Test Helpers ================== */

typedef double(SDLCALL *d_to_d_func)(double);
typedef double(SDLCALL *dd_to_d_func)(double, double);

/**
 * Runs all the cases on a given function with a signature double -> double.
 * The result is expected to be exact.
 *
 * \param func_name a printable name for the tested function.
 * \param func the function to call.
 * \param cases an array of all the cases.
 * \param cases_size the size of the cases array.
 */
static int
helper_dtod(const char *func_name, d_to_d_func func,
            const d_to_d *cases, const size_t cases_size)
{
    Uint32 i;
    for (i = 0; i < cases_size; i++) {
        const double result = func(cases[i].input);
        SDLTest_AssertCheck(SDL_fabs(result - cases[i].expected) < FLT_EPSILON,
                            "%s(%f), expected %f, got %f",
                            func_name,
                            cases[i].input,
                            cases[i].expected, result);
    }

    return TEST_COMPLETED;
}

/**
 * Runs all the cases on a given function with a signature double -> double.
 * Checks if the result between expected +/- EPSILON.
 *
 * \param func_name a printable name for the tested function.
 * \param func the function to call.
 * \param cases an array of all the cases.
 * \param cases_size the size of the cases array.
 */
static int
helper_dtod_inexact(const char *func_name, d_to_d_func func,
                    const d_to_d *cases, const size_t cases_size)
{
    Uint32 i;
    for (i = 0; i < cases_size; i++) {
        const double result = func(cases[i].input);
        double diff = result - cases[i].expected;
        double max_err = (cases[i].expected + 1.) * EPSILON;
        if (diff < 0) {
            diff = -diff;
        }
        if (max_err < 0) {
            max_err = -max_err;
        }
        SDLTest_AssertCheck(diff <= max_err,
                            "%s(%f), expected %f +/- %g, got %f",
                            func_name,
                            cases[i].input,
                            cases[i].expected, max_err,
                            result);
    }

    return TEST_COMPLETED;
}

/**
 * Runs all the cases on a given function with a signature
 * (double, double) -> double. The result is expected to be exact.
 *
 * \param func_name a printable name for the tested function.
 * \param func the function to call.
 * \param cases an array of all the cases.
 * \param cases_size the size of the cases array.
 */
static int
helper_ddtod(const char *func_name, dd_to_d_func func,
             const dd_to_d *cases, const size_t cases_size)
{
    Uint32 i;
    for (i = 0; i < cases_size; i++) {
        const double result = func(cases[i].x_input, cases[i].y_input);
        SDLTest_AssertCheck(result == cases[i].expected,
                            "%s(%f,%f), expected %f, got %f",
                            func_name,
                            cases[i].x_input, cases[i].y_input,
                            cases[i].expected, result);
    }

    return TEST_COMPLETED;
}

/**
 * Runs all the cases on a given function with a signature
 * (double, double) -> double. Checks if the result between expected +/- EPSILON.
 *
 * \param func_name a printable name for the tested function.
 * \param func the function to call.
 * \param cases an array of all the cases.
 * \param cases_size the size of the cases array.
 */
static int
helper_ddtod_inexact(const char *func_name, dd_to_d_func func,
                     const dd_to_d *cases, const size_t cases_size)
{
    Uint32 i;
    for (i = 0; i < cases_size; i++) {
        const double result = func(cases[i].x_input, cases[i].y_input);
        double diff = result - cases[i].expected;
        double max_err = (cases[i].expected + 1.) * EPSILON;
        if (diff < 0) {
            diff = -diff;
        }
        if (max_err < 0) {
            max_err = -max_err;
        }

        SDLTest_AssertCheck(diff <= max_err,
                            "%s(%f,%f), expected %f +/- %g, got %f",
                            func_name,
                            cases[i].x_input, cases[i].y_input,
                            cases[i].expected, max_err,
                            result);
    }

    return TEST_COMPLETED;
}

/**
 * Runs a range of values on a given function with a signature double -> double
 *
 * This function is only meant to test functions that returns the input value if it is
 * integral: f(x) -> x for x in N.
 *
 * \param func_name a printable name for the tested function.
 * \param func the function to call.
 */
static int
helper_range(const char *func_name, d_to_d_func func)
{
    Uint32 i;
    double test_value = 0.0;

    SDLTest_AssertPass("%s: Testing a range of %u values with steps of %" SDL_PRIu32,
                       func_name,
                       RANGE_TEST_ITERATIONS,
                       RANGE_TEST_STEP);

    for (i = 0; i < RANGE_TEST_ITERATIONS; i++, test_value += RANGE_TEST_STEP) {
        double result;
        /* These are tested elsewhere */
        if (ISNAN(test_value) || ISINF(test_value)) {
            continue;
        }

        result = func(test_value);
        if (result != test_value) { /* Only log failures to save performances */
            SDLTest_AssertCheck(false,
                                "%s(%.1f), expected %.1f, got %.1f",
                                func_name, test_value,
                                test_value, result);
            return TEST_ABORTED;
        }
    }

    return TEST_COMPLETED;
}

/* ================= Test Case Implementation ================== */

/* SDL_floor tests functions */

/**
 * Inputs: +/-Infinity.
 * Expected: Infinity is returned as-is.
 */
static int SDLCALL
floor_infCases(void *args)
{
    double result;

    result = SDL_floor(INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Floor(%f), expected %f, got %f",
                        INFINITY, INFINITY, result);

    result = SDL_floor(-INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result < 0,
                        "Floor(%f), expected %f, got %f",
                        -INFINITY, -INFINITY, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: +/-0.0.
 * Expected: Zero is returned as-is.
 */
static int SDLCALL
floor_zeroCases(void *args)
{
    const d_to_d zero_cases[] = {
        { 0.0, 0.0 },
        { -0.0, -0.0 }
    };
    return helper_dtod("Floor", SDL_floor, zero_cases, SDL_arraysize(zero_cases));
}

/**
 * Input: NAN.
 * Expected: NAN is returned.
 */
static int SDLCALL
floor_nanCase(void *args)
{
    const double result = SDL_floor(NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Floor(nan), expected nan, got %f",
                        result);
    return TEST_COMPLETED;
}

/**
 * Inputs: integral values.
 * Expected: the input value is returned as-is.
 */
static int SDLCALL
floor_roundNumbersCases(void *args)
{
    const d_to_d round_cases[] = {
        { 1.0, 1.0 },
        { -1.0, -1.0 },
        { 15.0, 15.0 },
        { -15.0, -15.0 },
        { 125.0, 125.0 },
        { -125.0, -125.0 },
        { 1024.0, 1024.0 },
        { -1024.0, -1024.0 }
    };
    return helper_dtod("Floor", SDL_floor, round_cases, SDL_arraysize(round_cases));
}

/**
 * Inputs: fractional values.
 * Expected: the lower integral value is returned.
 */
static int SDLCALL
floor_fractionCases(void *args)
{
    const d_to_d frac_cases[] = {
        { 1.0 / 2.0, 0.0 },
        { -1.0 / 2.0, -1.0 },
        { 4.0 / 3.0, 1.0 },
        { -4.0 / 3.0, -2.0 },
        { 76.0 / 7.0, 10.0 },
        { -76.0 / 7.0, -11.0 },
        { 535.0 / 8.0, 66.0 },
        { -535.0 / 8.0, -67.0 },
        { 19357.0 / 53.0, 365.0 },
        { -19357.0 / 53.0, -366.0 }
    };
    return helper_dtod("Floor", SDL_floor, frac_cases, SDL_arraysize(frac_cases));
}

/**
 * Inputs: values in the range [0, UINT32_MAX].
 * Expected: the input value is returned as-is.
 */
static int SDLCALL
floor_rangeTest(void *args)
{
    return helper_range("Floor", SDL_floor);
}

/* SDL_ceil tests functions */

/**
 * Inputs: +/-Infinity.
 * Expected: Infinity is returned as-is.
 */
static int SDLCALL
ceil_infCases(void *args)
{
    double result;

    result = SDL_ceil(INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Ceil(%f), expected %f, got %f",
                        INFINITY, INFINITY, result);

    result = SDL_ceil(-INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result < 0,
                        "Ceil(%f), expected %f, got %f",
                        -INFINITY, -INFINITY, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: +/-0.0.
 * Expected: Zero is returned as-is.
 */
static int SDLCALL
ceil_zeroCases(void *args)
{
    const d_to_d zero_cases[] = {
        { 0.0, 0.0 },
        { -0.0, -0.0 }
    };
    return helper_dtod("Ceil", SDL_ceil, zero_cases, SDL_arraysize(zero_cases));
}

/**
 * Input: NAN.
 * Expected: NAN is returned.
 */
static int SDLCALL
ceil_nanCase(void *args)
{
    const double result = SDL_ceil(NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Ceil(nan), expected nan, got %f",
                        result);
    return TEST_COMPLETED;
}

/**
 * Inputs: integral values.
 * Expected: the input value is returned as-is.
 */
static int SDLCALL
ceil_roundNumbersCases(void *args)
{
    const d_to_d round_cases[] = {
        { 1.0, 1.0 },
        { -1.0, -1.0 },
        { 15.0, 15.0 },
        { -15.0, -15.0 },
        { 125.0, 125.0 },
        { -125.0, -125.0 },
        { 1024.0, 1024.0 },
        { -1024.0, -1024.0 }
    };
    return helper_dtod("Ceil", SDL_ceil, round_cases, SDL_arraysize(round_cases));
}

/**
 * Inputs: fractional values.
 * Expected: the higher integral value is returned.
 */
static int SDLCALL
ceil_fractionCases(void *args)
{
    const d_to_d frac_cases[] = {
        { 1.0 / 2.0, 1.0 },
        { -1.0 / 2.0, -0.0 },
        { 4.0 / 3.0, 2.0 },
        { -4.0 / 3.0, -1.0 },
        { 76.0 / 7.0, 11.0 },
        { -76.0 / 7.0, -10.0 },
        { 535.0 / 8.0, 67.0 },
        { -535.0 / 8.0, -66.0 },
        { 19357.0 / 53.0, 366.0 },
        { -19357.0 / 53.0, -365.0 }
    };
    return helper_dtod("Ceil", SDL_ceil, frac_cases, SDL_arraysize(frac_cases));
}

/**
 * Inputs: values in the range [0, UINT32_MAX].
 * Expected: the input value is returned as-is.
 */
static int SDLCALL
ceil_rangeTest(void *args)
{
    return helper_range("Ceil", SDL_ceil);
}

/* SDL_trunc tests functions */

/**
 * Inputs: +/-Infinity.
 * Expected: Infinity is returned as-is.
 */
static int SDLCALL
trunc_infCases(void *args)
{
    double result;

    result = SDL_trunc(INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Trunc(%f), expected %f, got %f",
                        INFINITY, INFINITY, result);

    result = SDL_trunc(-INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result < 0,
                        "Trunc(%f), expected %f, got %f",
                        -INFINITY, -INFINITY, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: +/-0.0.
 * Expected: Zero is returned as-is.
 */
static int SDLCALL
trunc_zeroCases(void *args)
{
    const d_to_d zero_cases[] = {
        { 0.0, 0.0 },
        { -0.0, -0.0 }
    };
    return helper_dtod("Trunc", SDL_trunc, zero_cases, SDL_arraysize(zero_cases));
}

/**
 * Input: NAN.
 * Expected: NAN is returned.
 */
static int SDLCALL
trunc_nanCase(void *args)
{
    const double result = SDL_trunc(NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Trunc(nan), expected nan, got %f",
                        result);
    return TEST_COMPLETED;
}

/**
 * Inputs: integral values.
 * Expected: the input value is returned as-is.
 */
static int SDLCALL
trunc_roundNumbersCases(void *args)
{
    const d_to_d round_cases[] = {
        { 1.0, 1.0 },
        { -1.0, -1.0 },
        { 15.0, 15.0 },
        { -15.0, -15.0 },
        { 125.0, 125.0 },
        { -125.0, -125.0 },
        { 1024.0, 1024.0 },
        { -1024.0, -1024.0 }
    };
    return helper_dtod("Trunc", SDL_trunc, round_cases, SDL_arraysize(round_cases));
}

/**
 * Inputs: fractional values.
 * Expected: the integral part is returned.
 */
static int SDLCALL
trunc_fractionCases(void *args)
{
    const d_to_d frac_cases[] = {
        { 1.0 / 2.0, 0.0 },
        { -1.0 / 2.0, -0.0 },
        { 4.0 / 3.0, 1.0 },
        { -4.0 / 3.0, -1.0 },
        { 76.0 / 7.0, 10.0 },
        { -76.0 / 7.0, -10.0 },
        { 535.0 / 8.0, 66.0 },
        { -535.0 / 8.0, -66.0 },
        { 19357.0 / 53.0, 365.0 },
        { -19357.0 / 53.0, -365.0 }
    };
    return helper_dtod("Trunc", SDL_trunc, frac_cases, SDL_arraysize(frac_cases));
}

/**
 * Inputs: values in the range [0, UINT32_MAX].
 * Expected: the input value is returned as-is.
 */
static int SDLCALL
trunc_rangeTest(void *args)
{
    return helper_range("Trunc", SDL_trunc);
}

/* SDL_round tests functions */

/**
 * Inputs: +/-Infinity.
 * Expected: Infinity is returned as-is.
 */
static int SDLCALL
round_infCases(void *args)
{
    double result;

    result = SDL_round(INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Round(%f), expected %f, got %f",
                        INFINITY, INFINITY, result);

    result = SDL_round(-INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result < 0,
                        "Round(%f), expected %f, got %f",
                        -INFINITY, -INFINITY, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: +/-0.0.
 * Expected: Zero is returned as-is.
 */
static int SDLCALL
round_zeroCases(void *args)
{
    const d_to_d zero_cases[] = {
        { 0.0, 0.0 },
        { -0.0, -0.0 }
    };
    return helper_dtod("Round", SDL_round, zero_cases, SDL_arraysize(zero_cases));
}

/**
 * Input: NAN.
 * Expected: NAN is returned.
 */
static int SDLCALL
round_nanCase(void *args)
{
    const double result = SDL_round(NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Round(nan), expected nan, got %f",
                        result);
    return TEST_COMPLETED;
}

/**
 * Inputs: integral values.
 * Expected: the input value is returned as-is.
 */
static int SDLCALL
round_roundNumbersCases(void *args)
{
    const d_to_d round_cases[] = {
        { 1.0, 1.0 },
        { -1.0, -1.0 },
        { 15.0, 15.0 },
        { -15.0, -15.0 },
        { 125.0, 125.0 },
        { -125.0, -125.0 },
        { 1024.0, 1024.0 },
        { -1024.0, -1024.0 }
    };
    return helper_dtod("Round", SDL_round, round_cases, SDL_arraysize(round_cases));
}

/**
 * Inputs: fractional values.
 * Expected: the nearest integral value is returned.
 */
static int SDLCALL
round_fractionCases(void *args)
{
    const d_to_d frac_cases[] = {
        { 1.0 / 2.0, 1.0 },
        { -1.0 / 2.0, -1.0 },
        { 4.0 / 3.0, 1.0 },
        { -4.0 / 3.0, -1.0 },
        { 76.0 / 7.0, 11.0 },
        { -76.0 / 7.0, -11.0 },
        { 535.0 / 8.0, 67.0 },
        { -535.0 / 8.0, -67.0 },
        { 19357.0 / 53.0, 365.0 },
        { -19357.0 / 53.0, -365.0 }
    };
    return helper_dtod("Round", SDL_round, frac_cases, SDL_arraysize(frac_cases));
}

/**
 * Inputs: values in the range [0, UINT32_MAX].
 * Expected: the input value is returned as-is.
 */
static int SDLCALL
round_rangeTest(void *args)
{
    return helper_range("Round", SDL_round);
}

/* SDL_fabs tests functions */

/**
 * Inputs: +/-Infinity.
 * Expected: Positive Infinity is returned.
 */
static int SDLCALL
fabs_infCases(void *args)
{
    double result;

    result = SDL_fabs(INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Fabs(%f), expected %f, got %f",
                        INFINITY, INFINITY, result);

    result = SDL_fabs(-INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Fabs(%f), expected %f, got %f",
                        -INFINITY, INFINITY, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: +/-0.0.
 * Expected: Positive zero is returned.
 */
static int SDLCALL
fabs_zeroCases(void *args)
{
    const d_to_d zero_cases[] = {
        { 0.0, 0.0 },
        { -0.0, 0.0 }
    };
    return helper_dtod("Fabs", SDL_fabs, zero_cases, SDL_arraysize(zero_cases));
}

/**
 * Input: NAN.
 * Expected: NAN is returned.
 */
static int SDLCALL
fabs_nanCase(void *args)
{
    const double result = SDL_fabs(NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Fabs(nan), expected nan, got %f",
                        result);
    return TEST_COMPLETED;
}

/**
 * Inputs: values in the range [0, UINT32_MAX].
 * Expected: the input value is returned as-is.
 */
static int SDLCALL
fabs_rangeTest(void *args)
{
    return helper_range("Fabs", SDL_fabs);
}

/* SDL_copysign tests functions */

/**
 * Inputs: (+/-Infinity, +/-1.0).
 * Expected: Infinity with the sign of 1.0 is returned.
 */
static int SDLCALL
copysign_infCases(void *args)
{
    double result;

    result = SDL_copysign(INFINITY, -1.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result < 0,
                        "Copysign(%f,%.1f), expected %f, got %f",
                        INFINITY, -1.0, -INFINITY, result);

    result = SDL_copysign(INFINITY, 1.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Copysign(%f,%.1f), expected %f, got %f",
                        INFINITY, 1.0, INFINITY, result);

    result = SDL_copysign(-INFINITY, -1.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result < 0,
                        "Copysign(%f,%.1f), expected %f, got %f",
                        -INFINITY, -1.0, -INFINITY, result);

    result = SDL_copysign(-INFINITY, 1.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Copysign(%f,%.1f), expected %f, got %f",
                        -INFINITY, 1.0, INFINITY, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: (+/-0.0, +/-1.0).
 * Expected: 0.0 with the sign of 1.0 is returned.
 */
static int SDLCALL
copysign_zeroCases(void *args)
{
    const dd_to_d zero_cases[] = {
        { 0.0, 1.0, 0.0 },
        { 0.0, -1.0, -0.0 },
        { -0.0, 1.0, 0.0 },
        { -0.0, -1.0, -0.0 }
    };
    return helper_ddtod("Copysign", SDL_copysign, zero_cases, SDL_arraysize(zero_cases));
}

/**
 * Inputs: (NAN, +/-1.0).
 * Expected: NAN with the sign of 1.0 is returned.
 * NOTE: On some platforms signed NAN is not supported, so we only check if the result is still NAN.
 */
static int SDLCALL
copysign_nanCases(void *args)
{
    double result;

    result = SDL_copysign(NAN, 1.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Copysign(nan,1.0), expected nan, got %f",
                        result);

    result = SDL_copysign(NAN, -1.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Copysign(nan,-1.0), expected nan, got %f",
                        result);
    return TEST_COMPLETED;
}

/**
 * Inputs: values in the range [0, UINT32_MAX], +/-1.0.
 * Expected: the input value with the sign of 1.0 is returned.
 */
static int SDLCALL
copysign_rangeTest(void *args)
{
    Uint32 i;
    double test_value = 0.0;

    SDLTest_AssertPass("Copysign: Testing a range of %u values with steps of %" SDL_PRIu32,
                       RANGE_TEST_ITERATIONS,
                       RANGE_TEST_STEP);

    for (i = 0; i < RANGE_TEST_ITERATIONS; i++, test_value += RANGE_TEST_STEP) {
        double result;
        /* These are tested elsewhere */
        if (ISNAN(test_value) || ISINF(test_value)) {
            continue;
        }

        /* Only log failures to save performances */
        result = SDL_copysign(test_value, 1.0);
        if (result != test_value) {
            SDLTest_AssertCheck(false,
                                "Copysign(%.1f,%.1f), expected %.1f, got %.1f",
                                test_value, 1.0, test_value, result);
            return TEST_ABORTED;
        }

        result = SDL_copysign(test_value, -1.0);
        if (result != -test_value) {
            SDLTest_AssertCheck(false,
                                "Copysign(%.1f,%.1f), expected %.1f, got %.1f",
                                test_value, -1.0, -test_value, result);
            return TEST_ABORTED;
        }
    }
    return TEST_COMPLETED;
}

/* SDL_fmod tests functions */

/**
 * Inputs: (+/-Infinity, +/-1.0).
 * Expected: NAN is returned.
 */
static int SDLCALL
fmod_divOfInfCases(void *args)
{
    double result;

    result = SDL_fmod(INFINITY, -1.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Fmod(%f,%.1f), expected %f, got %f",
                        INFINITY, -1.0, NAN, result);

    result = SDL_fmod(INFINITY, 1.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Fmod(%f,%.1f), expected %f, got %f",
                        INFINITY, 1.0, NAN, result);

    result = SDL_fmod(-INFINITY, -1.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Fmod(%f,%.1f), expected %f, got %f",
                        -INFINITY, -1.0, NAN, result);

    result = SDL_fmod(-INFINITY, 1.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Fmod(%f,%.1f), expected %f, got %f",
                        -INFINITY, 1.0, NAN, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: (+/-1.0, +/-Infinity).
 * Expected: 1.0 is returned as-is.
 */
static int SDLCALL
fmod_divByInfCases(void *args)
{
    double result;

    result = SDL_fmod(1.0, INFINITY);
    SDLTest_AssertCheck(1.0 == result,
                        "Fmod(%.1f,%f), expected %f, got %f",
                        1.0, INFINITY, 1.0, result);

    result = SDL_fmod(-1.0, INFINITY);
    SDLTest_AssertCheck(-1.0 == result,
                        "Fmod(%.1f,%f), expected %f, got %f",
                        -1.0, INFINITY, -1.0, result);

    result = SDL_fmod(1.0, -INFINITY);
    SDLTest_AssertCheck(1.0 == result,
                        "Fmod(%.1f,%f), expected %f, got %f",
                        1.0, -INFINITY, 1.0, result);

    result = SDL_fmod(-1.0, -INFINITY);
    SDLTest_AssertCheck(-1.0 == result,
                        "Fmod(%.1f,%f), expected %f, got %f",
                        -1.0, -INFINITY, -1.0, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: (+/-0.0, +/-1.0).
 * Expected: Zero is returned as-is.
 */
static int SDLCALL
fmod_divOfZeroCases(void *args)
{
    const dd_to_d zero_cases[] = {
        { 0.0, 1.0, 0.0 },
        { 0.0, -1.0, 0.0 },
        { -0.0, 1.0, -0.0 },
        { -0.0, -1.0, -0.0 }
    };
    return helper_ddtod("Fmod", SDL_fmod, zero_cases, SDL_arraysize(zero_cases));
}

/**
 * Inputs: (+/-1.0, +/-0.0).
 * Expected: NAN is returned.
 */
static int SDLCALL
fmod_divByZeroCases(void *args)
{
    double result;

    result = SDL_fmod(1.0, 0.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Fmod(1.0,0.0), expected nan, got %f",
                        result);

    result = SDL_fmod(-1.0, 0.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Fmod(-1.0,0.0), expected nan, got %f",
                        result);

    result = SDL_fmod(1.0, -0.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Fmod(1.0,-0.0), expected nan, got %f",
                        result);

    result = SDL_fmod(-1.0, -0.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Fmod(-1.0,-0.0), expected nan, got %f",
                        result);

    return TEST_COMPLETED;
}

/**
 * Inputs: all permutation of NAN and +/-1.0.
 * Expected: NAN is returned.
 */
static int SDLCALL
fmod_nanCases(void *args)
{
    double result;

    result = SDL_fmod(NAN, 1.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Fmod(nan,1.0), expected nan, got %f",
                        result);

    result = SDL_fmod(NAN, -1.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Fmod(nan,-1.0), expected nan, got %f",
                        result);

    result = SDL_fmod(1.0, NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Fmod(1.0,nan), expected nan, got %f",
                        result);

    result = SDL_fmod(-1.0, NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Fmod(-1.0,nan), expected nan, got %f",
                        result);

    return TEST_COMPLETED;
}

/**
 * Inputs: values within the domain of the function.
 * Expected: the correct result is returned.
 */
static int SDLCALL
fmod_regularCases(void *args)
{
    const dd_to_d regular_cases[] = {
        { 3.5, 2.0, 1.5 },
        { -6.25, 3.0, -0.25 },
        { 7.5, 2.5, 0.0 },
        { 2.0 / 3.0, -1.0 / 3.0, 0.0 }
    };
    return helper_ddtod("Fmod", SDL_fmod, regular_cases, SDL_arraysize(regular_cases));
}

/**
 * Inputs: values in the range [0, UINT32_MAX] divided by 1.0.
 * Expected: Positive zero is always returned.
 */
static int SDLCALL
fmod_rangeTest(void *args)
{
    Uint32 i;
    double test_value = 0.0;

    SDLTest_AssertPass("Fmod: Testing a range of %u values with steps of %" SDL_PRIu32,
                       RANGE_TEST_ITERATIONS,
                       RANGE_TEST_STEP);

    for (i = 0; i < RANGE_TEST_ITERATIONS; i++, test_value += RANGE_TEST_STEP) {
        double result;
        /* These are tested elsewhere */
        if (ISNAN(test_value) || ISINF(test_value)) {
            continue;
        }

        /* Only log failures to save performances */
        result = SDL_fmod(test_value, 1.0);
        if (0.0 != result) {
            SDLTest_AssertCheck(false,
                                "Fmod(%.1f,%.1f), expected %.1f, got %.1f",
                                test_value, 1.0, 0.0, result);
            return TEST_ABORTED;
        }
    }
    return TEST_COMPLETED;
}

/* SDL_exp tests functions */

/**
 * Inputs: +/-Infinity.
 * Expected: Infinity is returned as-is.
 */
static int SDLCALL
exp_infCases(void *args)
{
    double result;

    result = SDL_exp(INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Exp(%f), expected %f, got %f",
                        INFINITY, INFINITY, result);

    result = SDL_exp(-INFINITY);
    SDLTest_AssertCheck(0.0 == result,
                        "Exp(%f), expected %f, got %f",
                        -INFINITY, 0.0, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: +/-0.0.
 * Expected: 1.0 is returned.
 */
static int SDLCALL
exp_zeroCases(void *args)
{
    const d_to_d zero_cases[] = {
        { 0.0, 1.0 },
        { -0.0, 1.0 }
    };
    return helper_dtod("Exp", SDL_exp, zero_cases, SDL_arraysize(zero_cases));
}

/**
 * Input: 710.0 (overflows for 64bits double).
 * Expected: Infinity is returned.
 * NOTE: This test is skipped for double types larger than 64 bits.
 */
static int SDLCALL
exp_overflowCase(void *args)
{
    double result;

    if (sizeof(double) > 8) {
        return TEST_SKIPPED;
    }

    result = SDL_exp(710.0);
    SDLTest_AssertCheck(ISINF(result),
                        "Exp(%f), expected %f, got %f",
                        710.0, INFINITY, result);
    return TEST_COMPLETED;
}

/**
 * Input: 1.0
 * Expected: The euler constant.
 */
static int SDLCALL
exp_baseCase(void *args)
{
    const double result = SDL_exp(1.0);
    SDLTest_AssertCheck(result >= EULER - EPSILON &&
                            result <= EULER + EPSILON,
                        "Exp(%f), expected [%f,%f], got %f",
                        1.0, EULER - EPSILON, EULER + EPSILON, result);
    return TEST_COMPLETED;
}

/**
 * Inputs: values within the domain of the function.
 * Expected: the correct result is returned.
 */
static int SDLCALL
exp_regularCases(void *args)
{
    /* Hexadecimal floating constants are not supported on C89 compilers */
    const d_to_d regular_cases[] = {
        { -101.0, 1.36853947117385291381565719268793547578002532127613087E-44 },
        { -15.73, 0.00000014741707833928422931856502906683425990763681 },
        { -1.0, 0.36787944117144233402427744294982403516769409179688 },
        { -0.5, 0.60653065971263342426311737654032185673713684082031 },
        { 0.5, 1.64872127070012819416433558217249810695648193359375 },
        { 2.25, 9.48773583635852624240669683786109089851379394531250 },
        { 34.125, 661148770968660.375 },
        { 112.89, 10653788283588960962604279261058893737879589093376.0 },
        { 539.483, 1970107755334319939701129934673541628417235942656909222826926175622435588279443011110464355295725187195188154768877850257012251677751742837992843520967922303961718983154427294786640886286983037548604937796221048661733679844353544028160.0 },
    };
    return helper_dtod_inexact("Exp", SDL_exp, regular_cases, SDL_arraysize(regular_cases));
}

/* SDL_log tests functions */

/**
 * Inputs: Positive Infinity and +/-0.0.
 * Expected: Positive and negative Infinity respectively.
 */
static int SDLCALL
log_limitCases(void *args)
{
    double result;

    result = SDL_log(INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Log(%f), expected %f, got %f",
                        INFINITY, INFINITY, result);

    result = SDL_log(0.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result < 0,
                        "Log(%f), expected %f, got %f",
                        0.0, -INFINITY, result);

    result = SDL_log(-0.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result < 0,
                        "Log(%f), expected %f, got %f",
                        -0.0, -INFINITY, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: 1.0 and the Euler constant.
 * Expected: 0.0 and 1.0 respectively.
 */
static int SDLCALL
log_baseCases(void *args)
{
    double result;

    result = SDL_log(1.0);
    SDLTest_AssertCheck(0.0 == result,
                        "Log(%f), expected %f, got %f",
                        1.0, 0.0, result);

    result = SDL_log(EULER);
    SDLTest_AssertCheck(SDL_fabs(result - 1.) < FLT_EPSILON,
                        "Log(%f), expected %f, got %f",
                        EULER, 1.0, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: NAN and a negative value.
 * Expected: NAN is returned.
 */
static int SDLCALL
log_nanCases(void *args)
{
    double result;

    result = SDL_log(NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Log(%f), expected %f, got %f",
                        NAN, NAN, result);

    result = SDL_log(-1234.5678);
    SDLTest_AssertCheck(ISNAN(result),
                        "Log(%f), expected %f, got %f",
                        -1234.5678, NAN, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: values within the domain of the function.
 * Expected: the correct result is returned.
 */
static int SDLCALL
log_regularCases(void *args)
{
    const d_to_d regular_cases[] = {
        { 5.0, 1.60943791243410028179994242236716672778129577636718750 },
        { 10.0, 2.302585092994045901093613792909309267997741699218750 },
        { 56.32, 4.031049711849786554296315443934872746467590332031250 },
        { 789.123, 6.670922202231861497523368598194792866706848144531250 },
        { 2734.876324, 7.91384149408957959792587644187733530998229980468750 }
    };
    return helper_dtod("Log", SDL_log, regular_cases, SDL_arraysize(regular_cases));
}

/* SDL_log10 tests functions */

/**
 * Inputs: Positive Infinity and +/-0.0.
 * Expected: Positive and negative Infinity respectively.
 */
static int SDLCALL
log10_limitCases(void *args)
{
    double result;

    result = SDL_log10(INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Log10(%f), expected %f, got %f",
                        INFINITY, INFINITY, result);

    result = SDL_log10(0.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result < 0,
                        "Log10(%f), expected %f, got %f",
                        0.0, -INFINITY, result);

    result = SDL_log10(-0.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result < 0,
                        "Log10(%f), expected %f, got %f",
                        -0.0, -INFINITY, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: Powers of ten from 0 to 9.
 * Expected: the exact power of ten is returned.
 */
static int SDLCALL
log10_baseCases(void *args)
{
    const d_to_d base_cases[] = {
        { 1.0, 0.0 },
        { 10.0, 1.0 },
        { 100.0, 2.0 },
        { 1000.0, 3.0 },
        { 10000.0, 4.0 },
        { 100000.0, 5.0 },
        { 1000000.0, 6.0 },
        { 10000000.0, 7.0 },
        { 100000000.0, 8.0 },
        { 1000000000.0, 9.0 },
    };
    return helper_dtod("Log10", SDL_log10, base_cases, SDL_arraysize(base_cases));
}

/**
 * Inputs: NAN and a negative value.
 * Expected: NAN is returned.
 */
static int SDLCALL
log10_nanCases(void *args)
{
    double result;

    result = SDL_log10(NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Log10(%f), expected %f, got %f",
                        NAN, NAN, result);

    result = SDL_log10(-1234.5678);
    SDLTest_AssertCheck(ISNAN(result),
                        "Log10(%f), expected %f, got %f",
                        -1234.5678, NAN, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: values within the domain of the function.
 * Expected: the correct result is returned.
 */
static int SDLCALL
log10_regularCases(void *args)
{
    const d_to_d regular_cases[] = {
        { 5.0, 0.698970004336018857493684208748163655400276184082031250 },
        { 12.5, 1.09691001300805646145875016372883692383766174316406250 },
        { 56.32, 1.750662646134055755453573510749265551567077636718750 },
        { 789.123, 2.8971447016351858927407647570362314581871032714843750 },
        { 2734.876324, 3.436937691540090433761633903486654162406921386718750 }
    };
    return helper_dtod_inexact("Log10", SDL_log10, regular_cases, SDL_arraysize(regular_cases));
}

/* SDL_modf tests functions */

static int SDLCALL
modf_baseCases(void *args)
{
    double fractional, integral;

    fractional = SDL_modf(1.25, &integral);
    SDLTest_AssertCheck(integral == 1.0,
                        "modf(%f), expected integral %f, got %f",
                        1.25, 1.0, integral);
    SDLTest_AssertCheck(fractional == 0.25,
                        "modf(%f), expected fractional %f, got %f",
                        1.25, 0.25, fractional);

    return TEST_COMPLETED;
}

/* SDL_pow tests functions */

/* Tests with positive and negative infinities as exponents */

/**
 * Inputs: (-1.0, +/-Infinity).
 * Expected: 1.0 is returned.
 */
static int SDLCALL
pow_baseNOneExpInfCases(void *args)
{
    double result;

    result = SDL_pow(-1.0, INFINITY);
    SDLTest_AssertCheck(1.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        -1.0, INFINITY, 1.0, result);

    result = SDL_pow(-1.0, -INFINITY);
    SDLTest_AssertCheck(1.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        -1.0, -INFINITY, 1.0, result);

    return TEST_COMPLETED;
}
/**
 * Inputs: (+/-0.0, -Infinity).
 * Expected: Infinity is returned.
 */
static int SDLCALL
pow_baseZeroExpNInfCases(void *args)
{
    double result;

    result = SDL_pow(0.0, -INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Pow(%f,%f), expected %f, got %f",
                        0.0, -INFINITY, INFINITY, result);

    result = SDL_pow(-0.0, -INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Pow(%f,%f), expected %f, got %f",
                        -0.0, -INFINITY, INFINITY, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: (x, +/-Infinity) where x is not +/-0.0.
 * Expected: 0.0 when x < 1, Infinity when x > 1.
 */
static int SDLCALL
pow_expInfCases(void *args)
{
    double result;

    result = SDL_pow(0.5, INFINITY);
    SDLTest_AssertCheck(0.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        0.5, INFINITY, 0.0, result);

    result = SDL_pow(1.5, INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Pow(%f,%f), expected %f, got %f",
                        1.5, INFINITY, INFINITY, result);

    result = SDL_pow(0.5, -INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Pow(%f,%f), expected %f, got %f",
                        0.5, INFINITY, INFINITY, result);

    result = SDL_pow(1.5, -INFINITY);
    SDLTest_AssertCheck(0.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        1.5, -INFINITY, 0.0, result);

    return TEST_COMPLETED;
}

/* Tests with positive and negative infinities as base */

/**
 * Inputs: (Positive Infinity, x) where x is not +/-0.0.
 * Expected: 0.0 when x is < 0, positive Infinity when x > 0.
 */
static int SDLCALL
pow_basePInfCases(void *args)
{
    double result;

    result = SDL_pow(INFINITY, -3.0);
    SDLTest_AssertCheck(0.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        INFINITY, -3.0, 0.0, result);

    result = SDL_pow(INFINITY, 2.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Pow(%f,%f), expected %f, got %f",
                        INFINITY, 2.0, INFINITY, result);

    result = SDL_pow(INFINITY, -2.12345);
    SDLTest_AssertCheck(0.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        INFINITY, -2.12345, 0.0, result);

    result = SDL_pow(INFINITY, 3.1345);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Pow(%f,%f), expected %f, got %f",
                        INFINITY, 3.12345, INFINITY, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: (Negative Infinity, x) where x is not +/-0.0.
 * Expected:
 * - -0.0 when x is a negative odd integer,
 * - 0.0 when x is a negative even integer or negative non-integer,
 * - Negative Infinity when x is a positive odd integer,
 * - Positive Infinity when x is a positive even integer or positive non-integer.
 */
static int SDLCALL
pow_baseNInfCases(void *args)
{
    double result;

    result = SDL_pow(-INFINITY, -3.0);
    SDLTest_AssertCheck(-0.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        -INFINITY, -3.0, -0.0, result);

    result = SDL_pow(-INFINITY, -2.0);
    SDLTest_AssertCheck(0.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        -INFINITY, -2.0, 0.0, result);

    result = SDL_pow(-INFINITY, -5.5);
    SDLTest_AssertCheck(0.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        -INFINITY, -5.5, 0.0, result);

    result = SDL_pow(-INFINITY, 3.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result < 0,
                        "Pow(%f,%f), expected %f, got %f",
                        -INFINITY, 3.0, -INFINITY, result);

    result = SDL_pow(-INFINITY, 2.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Pow(%f,%f), expected %f, got %f",
                        -INFINITY, 2.0, INFINITY, result);

    result = SDL_pow(-INFINITY, 5.5);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Pow(%f,%f), expected %f, got %f",
                        -INFINITY, 5.5, INFINITY, result);

    return TEST_COMPLETED;
}

/* Tests related to NAN */

/**
 * Inputs:
 * - finite and negative base,
 * - finite and non-integer exponent.
 * Expected: NAN is returned.
 */
static int SDLCALL
pow_badOperationCase(void *args)
{
    const double result = SDL_pow(-2.0, 4.2);
    SDLTest_AssertCheck(ISNAN(result),
                        "Pow(%f,%f), expected %f, got %f",
                        -2.0, 4.2, NAN, result);
    return TEST_COMPLETED;
}

/**
 * Inputs: (1.0, NAN)
 * Expected: 1.0 is returned.
 */
static int SDLCALL
pow_base1ExpNanCase(void *args)
{
    const double result = SDL_pow(1.0, NAN);
    SDLTest_AssertCheck(1.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        1.0, NAN, 1.0, result);
    return TEST_COMPLETED;
}

/**
 * Inputs: (NAN, +/-0.0)
 * Expected: 1.0 is returned.
 */
static int SDLCALL
pow_baseNanExp0Cases(void *args)
{
    double result;

    result = SDL_pow(NAN, 0.0);
    SDLTest_AssertCheck(1.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        NAN, 0.0, 1.0, result);

    result = SDL_pow(NAN, -0.0);
    SDLTest_AssertCheck(1.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        NAN, -0.0, 1.0, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: NAN as base, exponent or both.
 * Expected: NAN is returned.
 */
static int SDLCALL
pow_nanArgsCases(void *args)
{
    double result;

    result = SDL_pow(7.8, NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Pow(%f,%f), expected %f, got %f",
                        7.8, NAN, NAN, result);

    result = SDL_pow(NAN, 10.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Pow(%f,%f), expected %f, got %f",
                        NAN, 10.0, NAN, result);

    result = SDL_pow(NAN, NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Pow(%f,%f), expected %f, got %f",
                        NAN, NAN, NAN, result);

    return TEST_COMPLETED;
}

/* Tests with positive and negative zeros as base */

/**
 * Inputs: (-0.0, x) where x is an odd integer.
 * Expected:
 * - Negative Infinity with a negative exponent,
 * - -0.0 with a positive exponent.
 */
static int SDLCALL
pow_baseNZeroExpOddCases(void *args)
{
    double result;

    result = SDL_pow(-0.0, -3.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result < 0,
                        "Pow(%f,%f), expected %f, got %f",
                        -0.0, -3.0, -INFINITY, result);

    result = SDL_pow(-0.0, 3.0);
    SDLTest_AssertCheck(-0.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        -0.0, 3.0, -0.0, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: (0.0, x) where x is an odd integer.
 * Expected:
 * - 0.0 with a positive exponent,
 * - Positive Infinity with a negative exponent.
 */
static int SDLCALL
pow_basePZeroExpOddCases(void *args)
{
    double result;

    result = SDL_pow(0.0, -5.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Pow(%f,%f), expected %f, got %f",
                        0.0, -5.0, INFINITY, result);

    result = SDL_pow(0.0, 5.0);
    SDLTest_AssertCheck(0.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        0.0, 5.0, 0.0, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: (-0.0, x), with x either:
 * - finite and even,
 * - finite and non-integer.
 * Expected:
 * - Positive Infinity if the exponent is negative,
 * - 0.0 if the exponent is positive.
 */
static int SDLCALL
pow_baseNZeroCases(void *args)
{
    double result;

    result = SDL_pow(-0.0, -3.5);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Pow(%f,%f), expected %f, got %f",
                        -0.0, -3.5, INFINITY, result);

    result = SDL_pow(-0.0, -4.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Pow(%f,%f), expected %f, got %f",
                        -0.0, -4.0, INFINITY, result);

    result = SDL_pow(-0.0, 3.5);
    SDLTest_AssertCheck(0.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        -0.0, 3.5, 0.0, result);

    result = SDL_pow(-0.0, 4.0);
    SDLTest_AssertCheck(0.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        -0.0, 4.0, 0.0, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: (0.0, x), with x either:
 * - finite and even,
 * - finite and non-integer.
 * Expected:
 * - Positive Infinity if the exponent is negative,
 * - 0.0 if the exponent is positive.
 */
static int SDLCALL
pow_basePZeroCases(void *args)
{
    double result;

    result = SDL_pow(0.0, -3.5);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Pow(%f,%f), expected %f, got %f",
                        0.0, -3.5, INFINITY, result);

    result = SDL_pow(0.0, -4.0);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Pow(%f,%f), expected %f, got %f",
                        0.0, -4.0, INFINITY, result);

    result = SDL_pow(0.0, 3.5);
    SDLTest_AssertCheck(0.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        0.0, 3.5, 0.0, result);

    result = SDL_pow(0.0, 4.0);
    SDLTest_AssertCheck(0.0 == result,
                        "Pow(%f,%f), expected %f, got %f",
                        0.0, 4.0, 0.0, result);

    return TEST_COMPLETED;
}

/* Remaining tests */

/**
 * Inputs: values within the domain of the function.
 * Expected: the correct result is returned.
 */
static int SDLCALL
pow_regularCases(void *args)
{
    const dd_to_d regular_cases[] = {
#if 0 /* These tests fail when using the Mingw C runtime, we'll disable them for now */
        { -391.25, -2.0, 0.00000653267870448815438463212659780943170062528224661946296691894531250 },
        { -72.3, 12.0, 20401381050275984310272.0 },
#endif
        { -5.0, 3.0, -125.0 },
        { 3.0, 2.5, 15.58845726811989607085706666111946105957031250 },
        { 39.23, -1.5, 0.0040697950366865498147972424192175822099670767784118652343750 },
        { 478.972, 12.125, 315326359630449587856007411793920.0 }
    };
    return helper_ddtod_inexact("Pow", SDL_pow, regular_cases, SDL_arraysize(regular_cases));
}

/**
 * Inputs: (2.0, x), with x in range [0, 8].
 * Expected: the correct result is returned.
 */
static int SDLCALL
pow_powerOfTwo(void *args)
{
    const dd_to_d power_of_two_cases[] = {
        { 2.0, 1.0, 2.0 },
        { 2.0, 2.0, 4.0 },
        { 2.0, 3.0, 8.0 },
        { 2.0, 4.0, 16.0 },
        { 2.0, 5.0, 32.0 },
        { 2.0, 6.0, 64.0 },
        { 2.0, 7.0, 128.0 },
        { 2.0, 8.0, 256.0 },
    };
    return helper_ddtod("Pow", SDL_pow, power_of_two_cases, SDL_arraysize(power_of_two_cases));
}

/**
 * Inputs: values in the range [0, UINT32_MAX] to the power of +/-0.0.
 * Expected: 1.0 is always returned.
 */
static int SDLCALL
pow_rangeTest(void *args)
{
    Uint32 i;
    double test_value = 0.0;

    SDLTest_AssertPass("Pow: Testing a range of %u values with steps of %" SDL_PRIu32,
                       RANGE_TEST_ITERATIONS,
                       RANGE_TEST_STEP);

    for (i = 0; i < RANGE_TEST_ITERATIONS; i++, test_value += RANGE_TEST_STEP) {
        double result;
        /* These are tested elsewhere */
        if (ISNAN(test_value) || ISINF(test_value)) {
            continue;
        }

        /* Only log failures to save performances */
        result = SDL_pow(test_value, 0.0);
        if (result != 1.0) {
            SDLTest_AssertCheck(false,
                                "Pow(%.1f,%.1f), expected %.1f, got %.1f",
                                test_value, 1.0, 1.0, result);
            return TEST_ABORTED;
        }

        result = SDL_pow(test_value, -0.0);
        if (result != 1.0) {
            SDLTest_AssertCheck(false,
                                "Pow(%.1f,%.1f), expected %.1f, got %.1f",
                                test_value, -0.0, 1.0, result);
            return TEST_ABORTED;
        }
    }
    return TEST_COMPLETED;
}

/* SDL_sqrt tests functions */

/**
 * Input: Positive Infinity.
 * Expected: Positive Infinity is returned.
 */
static int SDLCALL
sqrt_infCase(void *args)
{
    const double result = SDL_sqrt(INFINITY);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Sqrt(%f), expected %f, got %f",
                        INFINITY, INFINITY, result);
    return TEST_COMPLETED;
}

/**
 * Input: NAN.
 * Expected: NAN is returned.
 */
static int SDLCALL
sqrt_nanCase(void *args)
{
    const double result = SDL_sqrt(NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Sqrt(%f), expected %f, got %f",
                        NAN, NAN, result);
    return TEST_COMPLETED;
}

/**
 * Inputs: values outside the domain of the function.
 * Expected: NAN is returned.
 */
static int SDLCALL
sqrt_outOfDomainCases(void *args)
{
    double result;

    result = SDL_sqrt(-1.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Sqrt(%f), expected %f, got %f",
                        -1.0, NAN, result);

    result = SDL_sqrt(-12345.6789);
    SDLTest_AssertCheck(ISNAN(result),
                        "Sqrt(%f), expected %f, got %f",
                        -12345.6789, NAN, result);

    result = SDL_sqrt(-INFINITY);
    SDLTest_AssertCheck(ISNAN(result),
                        "Sqrt(%f), expected %f, got %f",
                        -INFINITY, NAN, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: +/-0.0 and 1.0.
 * Expected: the input value is returned as-is.
 */
static int SDLCALL
sqrt_baseCases(void *args)
{
    const d_to_d base_cases[] = {
        { -0.0, -0.0 },
        { 0.0, 0.0 },
        { 1.0, 1.0 }
    };
    return helper_dtod("Sqrt", SDL_sqrt, base_cases, SDL_arraysize(base_cases));
}

/**
 * Inputs: values within the domain of the function.
 * Expected: the correct result is returned.
 */
static int SDLCALL
sqrt_regularCases(void *args)
{
    const d_to_d regular_cases[] = {
        { 4.0, 2.0 },
        { 9.0, 3.0 },
        { 27.2, 5.21536192416211896727418206864967942237854003906250 },
        { 240.250, 15.5 },
        { 1337.0, 36.565010597564445049556525191292166709899902343750 },
        { 2887.12782400000014604302123188972473144531250, 53.732 },
        { 65600.0156250, 256.125 }
    };
    return helper_dtod_inexact("Sqrt", SDL_sqrt, regular_cases, SDL_arraysize(regular_cases));
}

/* SDL_scalbn tests functions */

/**
 * Input: (+/-Infinity, 1).
 * Expected: Infinity is returned as-is.
 */
static int SDLCALL
scalbn_infCases(void *args)
{
    double result;

    result = SDL_scalbn(INFINITY, 1);
    SDLTest_AssertCheck(IS_INFINITY(result) && result > 0,
                        "Scalbn(%f,%d), expected %f, got %f",
                        INFINITY, 1, INFINITY, result);

    result = SDL_scalbn(-INFINITY, 1);
    SDLTest_AssertCheck(IS_INFINITY(result) && result < 0,
                        "Scalbn(%f,%d), expected %f, got %f",
                        -INFINITY, 1, -INFINITY, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: (+/-0.0, 1).
 * Expected: Zero is returned as-is.
 */
static int SDLCALL
scalbn_baseZeroCases(void *args)
{
    double result;

    result = SDL_scalbn(0.0, 1);
    SDLTest_AssertCheck(0.0 == result,
                        "Scalbn(%f,%d), expected %f, got %f",
                        0.0, 1, 0.0, result);

    result = SDL_scalbn(-0.0, 1);
    SDLTest_AssertCheck(-0.0 == result,
                        "Scalbn(%f,%d), expected %f, got %f",
                        -0.0, 1, -0.0, result);

    return TEST_COMPLETED;
}

/**
 * Input: (x, 0)
 * Expected: x is returned as-is.
 */
static int SDLCALL
scalbn_expZeroCase(void *args)
{
    const double result = SDL_scalbn(42.0, 0);
    SDLTest_AssertCheck(42.0 == result,
                        "Scalbn(%f,%d), expected %f, got %f",
                        42.0, 0, 42.0, result);
    return TEST_COMPLETED;
}

/**
 * Input: (NAN, x).
 * Expected: NAN is returned.
 */
static int SDLCALL
scalbn_nanCase(void *args)
{
    const double result = SDL_scalbn(NAN, 2);
    SDLTest_AssertCheck(ISNAN(result),
                        "Scalbn(%f,%d), expected %f, got %f",
                        NAN, 2, NAN, result);
    return TEST_COMPLETED;
}

/**
 * Inputs: values inside the domain of the function.
 * Expected: the correct result is returned.
 * NOTE: This test depends on SDL_pow and FLT_RADIX.
 */
static int SDLCALL
scalbn_regularCases(void *args)
{
    double result, expected;

    result = SDL_scalbn(2.0, 2);
    expected = 2.0 * SDL_pow(FLT_RADIX, 2);
    SDLTest_AssertCheck(result == expected,
                        "Scalbn(%f,%d), expected %f, got %f",
                        2.0, 2, expected, result);

    result = SDL_scalbn(1.0, 13);
    expected = 1.0 * SDL_pow(FLT_RADIX, 13);
    SDLTest_AssertCheck(result == expected,
                        "Scalbn(%f,%d), expected %f, got %f",
                        1.0, 13, expected, result);

    result = SDL_scalbn(2.0, -5);
    expected = 2.0 * SDL_pow(FLT_RADIX, -5);
    SDLTest_AssertCheck(result == expected,
                        "Scalbn(%f,%d), expected %f, got %f",
                        2.0, -5, expected, result);

    result = SDL_scalbn(-1.0, -13);
    expected = -1.0 * SDL_pow(FLT_RADIX, -13);
    SDLTest_AssertCheck(result == expected,
                        "Scalbn(%f,%d), expected %f, got %f",
                        -1.0, -13, expected, result);

    return TEST_COMPLETED;
}

/* SDL_cos tests functions */

/**
 * Inputs: +/-Infinity.
 * Expected: NAN is returned.
 */
static int SDLCALL
cos_infCases(void *args)
{
    double result;

    result = SDL_cos(INFINITY);
    SDLTest_AssertCheck(ISNAN(result),
                        "Cos(%f), expected %f, got %f",
                        INFINITY, NAN, result);

    result = SDL_cos(-INFINITY);
    SDLTest_AssertCheck(ISNAN(result),
                        "Cos(%f), expected %f, got %f",
                        -INFINITY, NAN, result);

    return TEST_COMPLETED;
}

/**
 * Input: NAN.
 * Expected: NAN is returned.
 */
static int SDLCALL
cos_nanCase(void *args)
{
    const double result = SDL_cos(NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Cos(%f), expected %f, got %f",
                        NAN, NAN, result);
    return TEST_COMPLETED;
}

/**
 * Inputs: +/-0.0 and +/-Pi.
 * Expected: +1.0 and -1.0 respectively.
 */
static int SDLCALL
cos_regularCases(void *args)
{
    const d_to_d regular_cases[] = {
        { -SDL_PI_D, -1.0 },
        { -0.0, 1.0 },
        { 0.0, 1.0 },
        { SDL_PI_D, -1.0 }
    };
    return helper_dtod("Cos", SDL_cos, regular_cases, SDL_arraysize(regular_cases));
}

/**
 * Inputs: Angles between 1/10 and 9/10 of Pi (positive and negative).
 * Expected: The correct result is returned (+/-EPSILON).
 */
static int SDLCALL
cos_precisionTest(void *args)
{
    const d_to_d precision_cases[] = {
        { SDL_PI_D * 1.0 / 10.0, 0.9510565162951535 },
        { SDL_PI_D * 2.0 / 10.0, 0.8090169943749475 },
        { SDL_PI_D * 3.0 / 10.0, 0.5877852522924731 },
        { SDL_PI_D * 4.0 / 10.0, 0.30901699437494745 },
        { SDL_PI_D * 5.0 / 10.0, 0.0 },
        { SDL_PI_D * 6.0 / 10.0, -0.30901699437494734 },
        { SDL_PI_D * 7.0 / 10.0, -0.587785252292473 },
        { SDL_PI_D * 8.0 / 10.0, -0.8090169943749473 },
        { SDL_PI_D * 9.0 / 10.0, -0.9510565162951535 },
        { SDL_PI_D * -1.0 / 10.0, 0.9510565162951535 },
        { SDL_PI_D * -2.0 / 10.0, 0.8090169943749475 },
        { SDL_PI_D * -3.0 / 10.0, 0.5877852522924731 },
        { SDL_PI_D * -4.0 / 10.0, 0.30901699437494745 },
        { SDL_PI_D * -5.0 / 10.0, 0.0 },
        { SDL_PI_D * -6.0 / 10.0, -0.30901699437494734 },
        { SDL_PI_D * -7.0 / 10.0, -0.587785252292473 },
        { SDL_PI_D * -8.0 / 10.0, -0.8090169943749473 },
        { SDL_PI_D * -9.0 / 10.0, -0.9510565162951535 }
    };
    return helper_dtod_inexact("Cos", SDL_cos, precision_cases, SDL_arraysize(precision_cases));
}

/**
 * Inputs: Values in the range [0, UINT32_MAX].
 * Expected: A value between 0 and 1 is returned.
 */
static int SDLCALL
cos_rangeTest(void *args)
{
    Uint32 i;
    double test_value = 0.0;

    SDLTest_AssertPass("Cos: Testing a range of %u values with steps of %" SDL_PRIu32,
                       RANGE_TEST_ITERATIONS,
                       RANGE_TEST_STEP);

    for (i = 0; i < RANGE_TEST_ITERATIONS; i++, test_value += RANGE_TEST_STEP) {
        double result;
        /* These are tested elsewhere */
        if (ISNAN(test_value) || ISINF(test_value)) {
            continue;
        }

        /* Only log failures to save performances */
        result = SDL_cos(test_value);
        if (result < -1.0 || result > 1.0) {
            SDLTest_AssertCheck(false,
                                "Cos(%.1f), expected [%.1f,%.1f], got %.1f",
                                test_value, -1.0, 1.0, result);
            return TEST_ABORTED;
        }
    }
    return TEST_COMPLETED;
}

/* SDL_sin tests functions */

/**
 * Inputs: +/-Infinity.
 * Expected: NAN is returned.
 */
static int SDLCALL
sin_infCases(void *args)
{
    double result;

    result = SDL_sin(INFINITY);
    SDLTest_AssertCheck(ISNAN(result),
                        "Sin(%f), expected %f, got %f",
                        INFINITY, NAN, result);

    result = SDL_sin(-INFINITY);
    SDLTest_AssertCheck(ISNAN(result),
                        "Sin(%f), expected %f, got %f",
                        -INFINITY, NAN, result);

    return TEST_COMPLETED;
}

/**
 * Input: NAN.
 * Expected: NAN is returned.
 */
static int SDLCALL
sin_nanCase(void *args)
{
    const double result = SDL_sin(NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Sin(%f), expected %f, got %f",
                        NAN, NAN, result);
    return TEST_COMPLETED;
}

/**
 * Inputs: +/-0.0 and +/-Pi/2.
 * Expected: +/-0.0 and +/-1.0 respectively.
 */
static int SDLCALL
sin_regularCases(void *args)
{
    const d_to_d regular_cases[] = {
        { -SDL_PI_D / 2, -1.0 },
        { -0.0, -0.0 },
        { 0.0, 0.0 },
        { SDL_PI_D / 2, 1.0 }
    };
    return helper_dtod("Sin", SDL_sin, regular_cases, SDL_arraysize(regular_cases));
}

/**
 * Inputs: Angles between 1/10 and 10/10 of Pi (positive and negative).
 * Expected: The correct result is returned (+/-EPSILON).
 * NOTE: +/-Pi/2 is tested in the regular cases.
 */
static int SDLCALL
sin_precisionTest(void *args)
{
    const d_to_d precision_cases[] = {
        { SDL_PI_D * 1.0 / 10.0, 0.3090169943749474 },
        { SDL_PI_D * 2.0 / 10.0, 0.5877852522924731 },
        { SDL_PI_D * 3.0 / 10.0, 0.8090169943749475 },
        { SDL_PI_D * 4.0 / 10.0, 0.9510565162951535 },
        { SDL_PI_D * 6.0 / 10.0, 0.9510565162951536 },
        { SDL_PI_D * 7.0 / 10.0, 0.8090169943749475 },
        { SDL_PI_D * 8.0 / 10.0, 0.5877852522924732 },
        { SDL_PI_D * 9.0 / 10.0, 0.3090169943749475 },
        { SDL_PI_D, 0.0 },
        { SDL_PI_D * -1.0 / 10.0, -0.3090169943749474 },
        { SDL_PI_D * -2.0 / 10.0, -0.5877852522924731 },
        { SDL_PI_D * -3.0 / 10.0, -0.8090169943749475 },
        { SDL_PI_D * -4.0 / 10.0, -0.9510565162951535 },
        { SDL_PI_D * -6.0 / 10.0, -0.9510565162951536 },
        { SDL_PI_D * -7.0 / 10.0, -0.8090169943749475 },
        { SDL_PI_D * -8.0 / 10.0, -0.5877852522924732 },
        { SDL_PI_D * -9.0 / 10.0, -0.3090169943749475 },
        { -SDL_PI_D, 0.0 },
    };
    return helper_dtod_inexact("Sin", SDL_sin, precision_cases, SDL_arraysize(precision_cases));
}

/**
 * Inputs: Values in the range [0, UINT32_MAX].
 * Expected: A value between 0 and 1 is returned.
 */
static int SDLCALL
sin_rangeTest(void *args)
{
    Uint32 i;
    double test_value = 0.0;

    SDLTest_AssertPass("Sin: Testing a range of %u values with steps of %" SDL_PRIu32,
                       RANGE_TEST_ITERATIONS,
                       RANGE_TEST_STEP);

    for (i = 0; i < RANGE_TEST_ITERATIONS; i++, test_value += RANGE_TEST_STEP) {
        double result;
        /* These are tested elsewhere */
        if (ISNAN(test_value) || ISINF(test_value)) {
            continue;
        }

        /* Only log failures to save performances */
        result = SDL_sin(test_value);
        if (result < -1.0 || result > 1.0) {
            SDLTest_AssertCheck(false,
                                "Sin(%.1f), expected [%.1f,%.1f], got %.1f",
                                test_value, -1.0, 1.0, result);
            return TEST_ABORTED;
        }
    }
    return TEST_COMPLETED;
}

/* SDL_tan tests functions */

/**
 * Inputs: +/-Infinity.
 * Expected: NAN is returned.
 */
static int SDLCALL
tan_infCases(void *args)
{
    double result;

    result = SDL_tan(INFINITY);
    SDLTest_AssertCheck(ISNAN(result),
                        "Tan(%f), expected %f, got %f",
                        INFINITY, NAN, result);

    result = SDL_tan(-INFINITY);
    SDLTest_AssertCheck(ISNAN(result),
                        "Tan(%f), expected %f, got %f",
                        -INFINITY, NAN, result);

    return TEST_COMPLETED;
}

/**
 * Input: NAN.
 * Expected: NAN is returned.
 */
static int SDLCALL
tan_nanCase(void *args)
{
    const double result = SDL_tan(NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Tan(%f), expected %f, got %f",
                        NAN, NAN, result);
    return TEST_COMPLETED;
}

/**
 * Inputs: +/-0.0.
 * Expected: Zero is returned as-is.
 */
static int SDLCALL
tan_zeroCases(void *args)
{
    const d_to_d regular_cases[] = {
        { -0.0, -0.0 },
        { 0.0, 0.0 }
    };
    return helper_dtod("Tan", SDL_tan, regular_cases, SDL_arraysize(regular_cases));
}

/**
 * Inputs: Angles between 1/11 and 10/11 of Pi (positive and negative).
 * Expected: The correct result is returned (+/-EPSILON).
 * NOTE: +/-Pi/2 is intentionally avoided as it returns garbage values.
 */
static int SDLCALL
tan_precisionTest(void *args)
{
    const d_to_d precision_cases[] = {
        { SDL_PI_D * 1.0 / 11.0, 0.29362649293836673 },
        { SDL_PI_D * 2.0 / 11.0, 0.642660977168331 },
        { SDL_PI_D * 3.0 / 11.0, 1.1540615205330094 },
        { SDL_PI_D * 4.0 / 11.0, 2.189694562989681 },
        { SDL_PI_D * 5.0 / 11.0, 6.9551527717734745 },
        { SDL_PI_D * 6.0 / 11.0, -6.955152771773481 },
        { SDL_PI_D * 7.0 / 11.0, -2.189694562989682 },
        { SDL_PI_D * 8.0 / 11.0, -1.1540615205330096 },
        { SDL_PI_D * 9.0 / 11.0, -0.6426609771683314 },
        { SDL_PI_D * 10.0 / 11.0, -0.2936264929383667 },
        { SDL_PI_D * -1.0 / 11.0, -0.29362649293836673 },
        { SDL_PI_D * -2.0 / 11.0, -0.642660977168331 },
        { SDL_PI_D * -3.0 / 11.0, -1.1540615205330094 },
        { SDL_PI_D * -4.0 / 11.0, -2.189694562989681 },
        { SDL_PI_D * -5.0 / 11.0, -6.9551527717734745 },
        { SDL_PI_D * -6.0 / 11.0, 6.955152771773481 },
        { SDL_PI_D * -7.0 / 11.0, 2.189694562989682 },
        { SDL_PI_D * -8.0 / 11.0, 1.1540615205330096 },
        { SDL_PI_D * -9.0 / 11.0, 0.6426609771683314 },
        { SDL_PI_D * -10.0 / 11.0, 0.2936264929383667 }
    };
    return helper_dtod_inexact("Tan", SDL_tan, precision_cases, SDL_arraysize(precision_cases));
}

/* SDL_acos tests functions */

/**
 * Inputs: +/-1.0.
 * Expected: 0.0 and Pi respectively.
 */
static int SDLCALL
acos_limitCases(void *args)
{
    double result;

    result = SDL_acos(1.0);
    SDLTest_AssertCheck(0.0 == result,
                        "Acos(%f), expected %f, got %f",
                        1.0, 0.0, result);

    result = SDL_acos(-1.0);
    SDLTest_AssertCheck(SDL_fabs(SDL_PI_D - result) <= EPSILON,
                        "Acos(%f), expected %f, got %f",
                        -1.0, SDL_PI_D, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: Values outside the domain of [-1, 1].
 * Expected: NAN is returned.
 */
static int SDLCALL
acos_outOfDomainCases(void *args)
{
    double result;

    result = SDL_acos(1.1);
    SDLTest_AssertCheck(ISNAN(result),
                        "Acos(%f), expected %f, got %f",
                        1.1, NAN, result);

    result = SDL_acos(-1.1);
    SDLTest_AssertCheck(ISNAN(result),
                        "Acos(%f), expected %f, got %f",
                        -1.1, NAN, result);

    return TEST_COMPLETED;
}

/**
 * Input: NAN.
 * Expected: NAN is returned.
 */
static int SDLCALL
acos_nanCase(void *args)
{
    const double result = SDL_acos(NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Acos(%f), expected %f, got %f",
                        NAN, NAN, result);
    return TEST_COMPLETED;
}

/**
 * Inputs: Values between -0.9 and 0.9 with steps of 0.1.
 * Expected: The correct result is returned (+/-EPSILON).
 */
static int SDLCALL
acos_precisionTest(void *args)
{
    const d_to_d precision_cases[] = {
        { 0.9, 0.4510268117 },
        { 0.8, 0.6435011087 },
        { 0.7, 0.7953988301 },
        { 0.6, 0.9272952180 },
        { 0.5, 1.0471975511 },
        { 0.4, 1.1592794807 },
        { 0.3, 1.2661036727 },
        { 0.2, 1.3694384060 },
        { 0.1, 1.4706289056 },
        { 0.0, 1.5707963267 },
        { -0.0, 1.5707963267 },
        { -0.1, 1.6709637479 },
        { -0.2, 1.7721542475 },
        { -0.3, 1.8754889808 },
        { -0.4, 1.9823131728 },
        { -0.5, 2.0943951023 },
        { -0.6, 2.2142974355 },
        { -0.7, 2.3461938234 },
        { -0.8, 2.4980915447 },
        { -0.9, 2.6905658417 },
    };
    return helper_dtod_inexact("Acos", SDL_acos, precision_cases, SDL_arraysize(precision_cases));
}

/* SDL_asin tests functions */

/**
 * Inputs: +/-1.0.
 * Expected: +/-Pi/2 is returned.
 */
static int SDLCALL
asin_limitCases(void *args)
{
    double result;

    result = SDL_asin(1.0);
    SDLTest_AssertCheck(SDL_fabs(SDL_PI_D / 2.0 - result) <= EPSILON,
                        "Asin(%f), expected %f, got %f",
                        1.0, SDL_PI_D / 2.0, result);

    result = SDL_asin(-1.0);
    SDLTest_AssertCheck(SDL_fabs(-SDL_PI_D / 2.0 - result) <= EPSILON,
                        "Asin(%f), expected %f, got %f",
                        -1.0, -SDL_PI_D / 2.0, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: Values outside the domain of [-1, 1].
 * Expected: NAN is returned.
 */
static int SDLCALL
asin_outOfDomainCases(void *args)
{
    double result;

    result = SDL_asin(1.1);
    SDLTest_AssertCheck(ISNAN(result),
                        "Asin(%f), expected %f, got %f",
                        1.1, NAN, result);

    result = SDL_asin(-1.1);
    SDLTest_AssertCheck(ISNAN(result),
                        "Asin(%f), expected %f, got %f",
                        -1.1, NAN, result);

    return TEST_COMPLETED;
}

/**
 * Input: NAN.
 * Expected: NAN is returned.
 */
static int SDLCALL
asin_nanCase(void *args)
{
    const double result = SDL_asin(NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Asin(%f), expected %f, got %f",
                        NAN, NAN, result);
    return TEST_COMPLETED;
}

/**
 * Inputs: Values between -0.9 and 0.9 with steps of 0.1.
 * Expected: The correct result is returned (+/-EPSILON).
 */
static int SDLCALL
asin_precisionTest(void *args)
{
    const d_to_d precision_cases[] = {
        { 0.9, 1.1197695149986342 },
        { 0.8, 0.9272952180016123 },
        { 0.7, 0.775397496610753 },
        { 0.6, 0.6435011087932844 },
        { 0.5, 0.5235987755982989 },
        { 0.4, 0.41151684606748806 },
        { 0.3, 0.3046926540153976 },
        { 0.2, 0.20135792079033074 },
        { 0.1, 0.10016742116155977 },
        { 0.0, 0.0 },
        { -0.0, -0.0 },
        { -0.1, -0.10016742116155977 },
        { -0.2, -0.20135792079033074 },
        { -0.3, -0.3046926540153976 },
        { -0.4, -0.41151684606748806 },
        { -0.5, -0.5235987755982989 },
        { -0.6, -0.6435011087932844 },
        { -0.7, -0.775397496610753 },
        { -0.8, -0.9272952180016123 },
        { -0.9, -1.1197695149986342 }
    };
    return helper_dtod_inexact("Asin", SDL_asin, precision_cases, SDL_arraysize(precision_cases));
}

/* SDL_atan tests functions */

/**
 * Inputs: +/-Infinity.
 * Expected: +/-Pi/2 is returned.
 */
static int SDLCALL
atan_limitCases(void *args)
{
    double result;

    result = SDL_atan(INFINITY);
    SDLTest_AssertCheck((SDL_PI_D / 2.0) - EPSILON <= result &&
                            result <= (SDL_PI_D / 2.0) + EPSILON,
                        "Atan(%f), expected %f, got %f",
                        INFINITY, SDL_PI_D / 2.0, result);

    result = SDL_atan(-INFINITY);
    SDLTest_AssertCheck((-SDL_PI_D / 2.0) - EPSILON <= result &&
                            result <= (-SDL_PI_D / 2.0) + EPSILON,
                        "Atan(%f), expected %f, got %f",
                        -INFINITY, -SDL_PI_D / 2.0, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: +/-0.0.
 * Expected: Zero is returned as-is.
 */
static int SDLCALL
atan_zeroCases(void *args)
{
    double result;

    result = SDL_atan(0.0);
    SDLTest_AssertCheck(0.0 == result,
                        "Atan(%f), expected %f, got %f",
                        0.0, 0.0, result);

    result = SDL_atan(-0.0);
    SDLTest_AssertCheck(-0.0 == result,
                        "Atan(%f), expected %f, got %f",
                        -0.0, -0.0, result);

    return TEST_COMPLETED;
}

/**
 * Input: NAN.
 * Expected: NAN is returned.
 */
static int SDLCALL
atan_nanCase(void *args)
{
    const double result = SDL_atan(NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Atan(%f), expected %f, got %f",
                        NAN, NAN, result);
    return TEST_COMPLETED;
}

/**
 * Inputs: Values corresponding to angles between 9Pi/20 and -9Pi/20 with steps of Pi/20.
 * Expected: The correct result is returned (+/-EPSILON).
 */
static int SDLCALL
atan_precisionTest(void *args)
{
    const d_to_d precision_cases[] = {
        { 6.313751514675041, 1.413716694115407 },
        { 3.0776835371752527, 1.2566370614359172 },
        { 1.9626105055051504, 1.0995574287564276 },
        { 1.3763819204711734, 0.9424777960769379 },
        { 1.0, 0.7853981633974483 },
        { 0.7265425280053609, 0.6283185307179586 },
        { 0.5095254494944288, 0.47123889803846897 },
        { 0.3249196962329063, 0.3141592653589793 },
        { 0.15838444032453627, 0.15707963267948966 },
        { -0.15838444032453627, -0.15707963267948966 },
        { -0.3249196962329063, -0.3141592653589793 },
        { -0.5095254494944288, -0.47123889803846897 },
        { -0.7265425280053609, -0.6283185307179586 },
        { -1.0, -0.7853981633974483 },
        { -1.3763819204711734, -0.9424777960769379 },
        { -1.9626105055051504, -1.0995574287564276 },
        { -3.0776835371752527, -1.2566370614359172 },
        { -6.313751514675041, -1.413716694115407 },
    };
    return helper_dtod_inexact("Atan", SDL_atan, precision_cases, SDL_arraysize(precision_cases));
}

/* SDL_atan2 tests functions */

/* Zero cases */

/**
 * Inputs: (+/-0.0, +/-0.0).
 * Expected:
 * - Zero if the second argument is positive zero.
 * - Pi if the second argument is negative zero.
 * - The sign is inherited from the first argument.
 */
static int SDLCALL
atan2_bothZeroCases(void *args)
{
    const dd_to_d cases[] = {
        { 0.0, 0.0, 0.0 },
        { -0.0, 0.0, -0.0 },
        { 0.0, -0.0, SDL_PI_D },
        { -0.0, -0.0, -SDL_PI_D },
    };
    return helper_ddtod_inexact("SDL_atan2", SDL_atan2, cases, SDL_arraysize(cases));
}

/**
 * Inputs: (+/-0.0, +/-1.0).
 * Expected:
 * - Zero if the second argument is positive.
 * - Pi if the second argument is negative.
 * - The sign is inherited from the first argument.
 */
static int SDLCALL
atan2_yZeroCases(void *args)
{
    const dd_to_d cases[] = {
        { 0.0, 1.0, 0.0 },
        { 0.0, -1.0, SDL_PI_D },
        { -0.0, 1.0, -0.0 },
        { -0.0, -1.0, -SDL_PI_D }
    };
    return helper_ddtod_inexact("SDL_atan2", SDL_atan2, cases, SDL_arraysize(cases));
}

/**
 * Inputs: (+/-1.0, +/-0.0).
 * Expected: Pi/2 with the sign of the first argument.
 */
static int SDLCALL
atan2_xZeroCases(void *args)
{
    const dd_to_d cases[] = {
        { 1.0, 0.0, SDL_PI_D / 2.0 },
        { -1.0, 0.0, -SDL_PI_D / 2.0 },
        { 1.0, -0.0, SDL_PI_D / 2.0 },
        { -1.0, -0.0, -SDL_PI_D / 2.0 }
    };
    return helper_ddtod_inexact("SDL_atan2", SDL_atan2, cases, SDL_arraysize(cases));
}

/* Infinity cases */

/**
 * Inputs: (+/-Infinity, +/-Infinity).
 * Expected:
 * - (+int, +inf) -> Pi/4,
 * - (+int, -inf) -> 3Pi/4,
 * - (-int, +inf) -> -Pi/4,
 * - (-int, -inf) -> Pi.
 */
static int SDLCALL
atan2_bothInfCases(void *args)
{
    double result;

    result = SDL_atan2(INFINITY, INFINITY);
    SDLTest_AssertCheck(SDL_fabs(SDL_PI_D / 4.0 - result) <= EPSILON,
                        "Atan2(%f,%f), expected %f, got %f",
                        INFINITY, INFINITY, SDL_PI_D / 4.0, result);

    result = SDL_atan2(INFINITY, -INFINITY);
    SDLTest_AssertCheck(SDL_fabs(3.0 * SDL_PI_D / 4.0 - result) <= EPSILON,
                        "Atan2(%f,%f), expected %f, got %f",
                        INFINITY, -INFINITY, 3.0 * SDL_PI_D / 4.0, result);

    result = SDL_atan2(-INFINITY, INFINITY);
    SDLTest_AssertCheck(SDL_fabs(-SDL_PI_D / 4.0 - result) <= EPSILON,
                        "Atan2(%f,%f), expected %f, got %f",
                        -INFINITY, INFINITY, -SDL_PI_D / 4.0, result);

    result = SDL_atan2(-INFINITY, -INFINITY);
    SDLTest_AssertCheck(SDL_fabs(-3.0 * SDL_PI_D / 4.0 - result) <= EPSILON,
                        "Atan2(%f,%f), expected %f, got %f",
                        -INFINITY, -INFINITY, -3.0 * SDL_PI_D / 4.0, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: (+/-Infinity, +/-1.0).
 * Expected: Pi/2 with the sign of the first argument.
 */
static int SDLCALL
atan2_yInfCases(void *args)
{
    double result;

    result = SDL_atan2(INFINITY, 1.0);
    SDLTest_AssertCheck(SDL_fabs(SDL_PI_D / 2.0 - result) <= EPSILON,
                        "Atan2(%f,%f), expected %f, got %f",
                        INFINITY, 1.0, SDL_PI_D / 2.0, result);

    result = SDL_atan2(INFINITY, -1.0);
    SDLTest_AssertCheck(SDL_fabs(SDL_PI_D / 2.0 - result) <= EPSILON,
                        "Atan2(%f,%f), expected %f, got %f",
                        INFINITY, -1.0, SDL_PI_D / 2.0, result);

    result = SDL_atan2(-INFINITY, 1.0);
    SDLTest_AssertCheck(SDL_fabs(-SDL_PI_D / 2.0 - result) <= EPSILON,
                        "Atan2(%f,%f), expected %f, got %f",
                        -INFINITY, 1.0, -SDL_PI_D / 2.0, result);

    result = SDL_atan2(-INFINITY, -1.0);
    SDLTest_AssertCheck(SDL_fabs(-SDL_PI_D / 2.0 - result) <= EPSILON,
                        "Atan2(%f,%f), expected %f, got %f",
                        -INFINITY, -1.0, -SDL_PI_D / 2.0, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: (+/-1.0, +/-Infinity).
 * Expected:
 * - (+/-1.0, +inf) -> +/-0.0
 * - (+/-1.0, -inf) -> +/-Pi.
 */
static int SDLCALL
atan2_xInfCases(void *args)
{
    double result;

    result = SDL_atan2(1.0, INFINITY);
    SDLTest_AssertCheck(0.0 == result,
                        "Atan2(%f,%f), expected %f, got %f",
                        1.0, INFINITY, 0.0, result);

    result = SDL_atan2(-1.0, INFINITY);
    SDLTest_AssertCheck(-0.0 == result,
                        "Atan2(%f,%f), expected %f, got %f",
                        -1.0, INFINITY, -0.0, result);

    result = SDL_atan2(1.0, -INFINITY);
    SDLTest_AssertCheck(SDL_fabs(SDL_PI_D - result) <= EPSILON,
                        "Atan2(%f,%f), expected %f, got %f",
                        1.0, -INFINITY, SDL_PI_D, result);

    result = SDL_atan2(-1.0, -INFINITY);
    SDLTest_AssertCheck(SDL_fabs(-SDL_PI_D - result) <= EPSILON,
                        "Atan2(%f,%f), expected %f, got %f",
                        -1.0, -INFINITY, -SDL_PI_D, result);

    return TEST_COMPLETED;
}

/* Miscelanious cases */

/**
 * Inputs: NAN as either or both of the arguments.
 * Expected: NAN is returned.
 */
static int SDLCALL
atan2_nanCases(void *args)
{
    double result;

    result = SDL_atan2(NAN, NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Atan2(%f,%f), expected %f, got %f",
                        NAN, NAN, NAN, result);

    result = SDL_atan2(NAN, 1.0);
    SDLTest_AssertCheck(ISNAN(result),
                        "Atan2(%f,%f), expected %f, got %f",
                        NAN, 1.0, NAN, result);

    result = SDL_atan2(1.0, NAN);
    SDLTest_AssertCheck(ISNAN(result),
                        "Atan2(%f,%f), expected %f, got %f",
                        1.0, NAN, NAN, result);

    return TEST_COMPLETED;
}

/**
 * Inputs: (y, x) with x and y positive.
 * Expected: Angle in the top right quadrant.
 */
static int SDLCALL
atan2_topRightQuadrantTest(void *args)
{
    const dd_to_d top_right_cases[] = {
        { 1.0, 1.0, SDL_PI_D / 4.0 },
        { SQRT3, 3.0, SDL_PI_D / 6.0 },
        { SQRT3, 1.0, SDL_PI_D / 3.0 }
    };
    return helper_ddtod_inexact("SDL_atan2", SDL_atan2, top_right_cases, SDL_arraysize(top_right_cases));
}

/**
 * Inputs: (y, x) with x negative and y positive.
 * Expected: Angle in the top left quadrant.
 */
static int SDLCALL
atan2_topLeftQuadrantTest(void *args)
{
    const dd_to_d top_left_cases[] = {
        { 1.0, -1.0, 3.0 * SDL_PI_D / 4.0 },
        { SQRT3, -3.0, 5.0 * SDL_PI_D / 6.0 },
        { SQRT3, -1.0, 2.0 * SDL_PI_D / 3.0 }
    };
    return helper_ddtod_inexact("SDL_atan2", SDL_atan2, top_left_cases, SDL_arraysize(top_left_cases));
}

/**
 * Inputs: (y, x) with x positive and y negative.
 * Expected: Angle in the bottom right quadrant.
 */
static int SDLCALL
atan2_bottomRightQuadrantTest(void *args)
{
    const dd_to_d bottom_right_cases[] = {
        { -1.0, 1.0, -SDL_PI_D / 4 },
        { -SQRT3, 3.0, -SDL_PI_D / 6.0 },
        { -SQRT3, 1.0, -SDL_PI_D / 3.0 }
    };
    return helper_ddtod_inexact("SDL_atan2", SDL_atan2, bottom_right_cases, SDL_arraysize(bottom_right_cases));
}

/**
 * Inputs: (y, x) with x and y negative.
 * Expected: Angle in the bottom left quadrant.
 */
static int SDLCALL
atan2_bottomLeftQuadrantTest(void *args)
{
    const dd_to_d bottom_left_cases[] = {
        { -1.0, -1.0, -3.0 * SDL_PI_D / 4.0 },
        { -SQRT3, -3.0, -5.0 * SDL_PI_D / 6.0 },
        { -SQRT3, -1.0, -4.0 * SDL_PI_D / 6.0 }
    };
    return helper_ddtod_inexact("SDL_atan2", SDL_atan2, bottom_left_cases, SDL_arraysize(bottom_left_cases));
}

/* ================= Test References ================== */

/* SDL_floor test cases */

static const SDLTest_TestCaseReference floorTestInf = {
    floor_infCases, "floor_infCases",
    "Checks positive and negative infinity", TEST_ENABLED
};
static const SDLTest_TestCaseReference floorTestZero = {
    floor_zeroCases, "floor_zeroCases",
    "Checks positive and negative zero", TEST_ENABLED
};
static const SDLTest_TestCaseReference floorTestNan = {
    floor_nanCase, "floor_nanCase",
    "Checks NAN", TEST_ENABLED
};
static const SDLTest_TestCaseReference floorTestRound = {
    floor_roundNumbersCases, "floor_roundNumberCases",
    "Checks a set of integral values", TEST_ENABLED
};
static const SDLTest_TestCaseReference floorTestFraction = {
    floor_fractionCases, "floor_fractionCases",
    "Checks a set of fractions", TEST_ENABLED
};
static const SDLTest_TestCaseReference floorTestRange = {
    floor_rangeTest, "floor_rangeTest",
    "Checks a range of positive integer", TEST_ENABLED
};

/* SDL_ceil test cases */

static const SDLTest_TestCaseReference ceilTestInf = {
    ceil_infCases, "ceil_infCases",
    "Checks positive and negative infinity", TEST_ENABLED
};
static const SDLTest_TestCaseReference ceilTestZero = {
    ceil_zeroCases, "ceil_zeroCases",
    "Checks positive and negative zero", TEST_ENABLED
};
static const SDLTest_TestCaseReference ceilTestNan = {
    ceil_nanCase, "ceil_nanCase",
    "Checks NAN", TEST_ENABLED
};
static const SDLTest_TestCaseReference ceilTestRound = {
    ceil_roundNumbersCases, "ceil_roundNumberCases",
    "Checks a set of integral values", TEST_ENABLED
};
static const SDLTest_TestCaseReference ceilTestFraction = {
    ceil_fractionCases, "ceil_fractionCases",
    "Checks a set of fractions", TEST_ENABLED
};
static const SDLTest_TestCaseReference ceilTestRange = {
    ceil_rangeTest, "ceil_rangeTest",
    "Checks a range of positive integer", TEST_ENABLED
};

/* SDL_trunc test cases */

static const SDLTest_TestCaseReference truncTestInf = {
    trunc_infCases, "trunc_infCases",
    "Checks positive and negative infinity", TEST_ENABLED
};
static const SDLTest_TestCaseReference truncTestZero = {
    trunc_zeroCases, "trunc_zeroCases",
    "Checks positive and negative zero", TEST_ENABLED
};
static const SDLTest_TestCaseReference truncTestNan = {
    trunc_nanCase, "trunc_nanCase",
    "Checks NAN", TEST_ENABLED
};
static const SDLTest_TestCaseReference truncTestRound = {
    trunc_roundNumbersCases, "trunc_roundNumberCases",
    "Checks a set of integral values", TEST_ENABLED
};
static const SDLTest_TestCaseReference truncTestFraction = {
    trunc_fractionCases, "trunc_fractionCases",
    "Checks a set of fractions", TEST_ENABLED
};
static const SDLTest_TestCaseReference truncTestRange = {
    trunc_rangeTest, "trunc_rangeTest",
    "Checks a range of positive integer", TEST_ENABLED
};

/* SDL_round test cases */

static const SDLTest_TestCaseReference roundTestInf = {
    round_infCases, "round_infCases",
    "Checks positive and negative infinity", TEST_ENABLED
};
static const SDLTest_TestCaseReference roundTestZero = {
    round_zeroCases, "round_zeroCases",
    "Checks positive and negative zero", TEST_ENABLED
};
static const SDLTest_TestCaseReference roundTestNan = {
    round_nanCase, "round_nanCase",
    "Checks NAN", TEST_ENABLED
};
static const SDLTest_TestCaseReference roundTestRound = {
    round_roundNumbersCases, "round_roundNumberCases",
    "Checks a set of integral values", TEST_ENABLED
};
static const SDLTest_TestCaseReference roundTestFraction = {
    round_fractionCases, "round_fractionCases",
    "Checks a set of fractions", TEST_ENABLED
};
static const SDLTest_TestCaseReference roundTestRange = {
    round_rangeTest, "round_rangeTest",
    "Checks a range of positive integer", TEST_ENABLED
};

/* SDL_fabs test cases */

static const SDLTest_TestCaseReference fabsTestInf = {
    fabs_infCases, "fabs_infCases",
    "Checks positive and negative infinity", TEST_ENABLED
};
static const SDLTest_TestCaseReference fabsTestZero = {
    fabs_zeroCases, "fabs_zeroCases",
    "Checks positive and negative zero", TEST_ENABLED
};
static const SDLTest_TestCaseReference fabsTestNan = {
    fabs_nanCase, "fabs_nanCase",
    "Checks NAN", TEST_ENABLED
};
static const SDLTest_TestCaseReference fabsTestRange = {
    fabs_rangeTest, "fabs_rangeTest",
    "Checks a range of positive integer", TEST_ENABLED
};

/* SDL_copysign test cases */

static const SDLTest_TestCaseReference copysignTestInf = {
    copysign_infCases, "copysign_infCases",
    "Checks positive and negative infinity", TEST_ENABLED
};
static const SDLTest_TestCaseReference copysignTestZero = {
    copysign_zeroCases, "copysign_zeroCases",
    "Checks positive and negative zero", TEST_ENABLED
};
static const SDLTest_TestCaseReference copysignTestNan = {
    copysign_nanCases, "copysign_nanCases",
    "Checks NANs", TEST_ENABLED
};
static const SDLTest_TestCaseReference copysignTestRange = {
    copysign_rangeTest, "copysign_rangeTest",
    "Checks a range of positive integer", TEST_ENABLED
};

/* SDL_fmod test cases */

static const SDLTest_TestCaseReference fmodTestDivOfInf = {
    fmod_divOfInfCases, "fmod_divOfInfCases",
    "Checks division of positive and negative infinity", TEST_ENABLED
};
static const SDLTest_TestCaseReference fmodTestDivByInf = {
    fmod_divByInfCases, "fmod_divByInfCases",
    "Checks division by positive and negative infinity", TEST_ENABLED
};
static const SDLTest_TestCaseReference fmodTestDivOfZero = {
    fmod_divOfZeroCases, "fmod_divOfZeroCases",
    "Checks division of positive and negative zero", TEST_ENABLED
};
static const SDLTest_TestCaseReference fmodTestDivByZero = {
    fmod_divByZeroCases, "fmod_divByZeroCases",
    "Checks division by positive and negative zero", TEST_ENABLED
};
static const SDLTest_TestCaseReference fmodTestNan = {
    fmod_nanCases, "fmod_nanCases",
    "Checks NANs", TEST_ENABLED
};
static const SDLTest_TestCaseReference fmodTestRegular = {
    fmod_regularCases, "fmod_regularCases",
    "Checks a set of regular values", TEST_ENABLED
};
static const SDLTest_TestCaseReference fmodTestRange = {
    fmod_rangeTest, "fmod_rangeTest",
    "Checks a range of positive integer", TEST_ENABLED
};

/* SDL_exp test cases */

static const SDLTest_TestCaseReference expTestInf = {
    exp_infCases, "exp_infCases",
    "Checks positive and negative infinity", TEST_ENABLED
};
static const SDLTest_TestCaseReference expTestZero = {
    exp_zeroCases, "exp_zeroCases",
    "Checks for positive and negative zero", TEST_ENABLED
};
static const SDLTest_TestCaseReference expTestOverflow = {
    exp_overflowCase, "exp_overflowCase",
    "Checks for overflow", TEST_ENABLED
};
static const SDLTest_TestCaseReference expTestBase = {
    exp_baseCase, "exp_baseCase",
    "Checks the base case", TEST_ENABLED
};
static const SDLTest_TestCaseReference expTestRegular = {
    exp_regularCases, "exp_regularCases",
    "Checks a set of regular values", TEST_ENABLED
};

/* SDL_log test cases */

static const SDLTest_TestCaseReference logTestLimit = {
    log_limitCases, "log_limitCases",
    "Checks the domain limits", TEST_ENABLED
};
static const SDLTest_TestCaseReference logTestNan = {
    log_nanCases, "log_nanCases",
    "Checks NAN and negative values", TEST_ENABLED
};
static const SDLTest_TestCaseReference logTestBase = {
    log_baseCases, "log_baseCases",
    "Checks the base cases", TEST_ENABLED
};
static const SDLTest_TestCaseReference logTestRegular = {
    log_regularCases, "log_regularCases",
    "Checks a set of regular values", TEST_ENABLED
};

/* SDL_log10 test cases */

static const SDLTest_TestCaseReference log10TestLimit = {
    log10_limitCases, "log10_limitCases",
    "Checks the domain limits", TEST_ENABLED
};
static const SDLTest_TestCaseReference log10TestNan = {
    log10_nanCases, "log10_nanCases",
    "Checks NAN and negative values", TEST_ENABLED
};
static const SDLTest_TestCaseReference log10TestBase = {
    log10_baseCases, "log10_baseCases",
    "Checks the base cases", TEST_ENABLED
};
static const SDLTest_TestCaseReference log10TestRegular = {
    log10_regularCases, "log10_regularCases",
    "Checks a set of regular values", TEST_ENABLED
};

/* SDL_modf test cases */

static const SDLTest_TestCaseReference modfTestBase = {
    modf_baseCases, "modf_baseCases",
    "Checks the base cases", TEST_ENABLED
};

/* SDL_pow test cases */

static const SDLTest_TestCaseReference powTestExpInf1 = {
    pow_baseNOneExpInfCases, "pow_baseNOneExpInfCases",
    "Checks for pow(-1, +/-inf)", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestExpInf2 = {
    pow_baseZeroExpNInfCases, "pow_baseZeroExpNInfCases",
    "Checks for pow(+/-0, -inf)", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestExpInf3 = {
    pow_expInfCases, "pow_expInfCases",
    "Checks for pow(x, +/-inf)", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestBaseInf1 = {
    pow_basePInfCases, "pow_basePInfCases",
    "Checks for pow(inf, x)", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestBaseInf2 = {
    pow_baseNInfCases, "pow_baseNInfCases",
    "Checks for pow(-inf, x)", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestNan1 = {
    pow_badOperationCase, "pow_badOperationCase",
    "Checks for negative finite base and non-integer finite exponent", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestNan2 = {
    pow_base1ExpNanCase, "pow_base1ExpNanCase",
    "Checks for pow(1.0, NAN)", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestNan3 = {
    pow_baseNanExp0Cases, "pow_baseNanExp0Cases",
    "Checks for pow(NAN, +/-0)", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestNan4 = {
    pow_nanArgsCases, "pow_nanArgsCases",
    "Checks for pow(x, y) with either x or y being NAN", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestZero1 = {
    pow_baseNZeroExpOddCases, "pow_baseNZeroExpOddCases",
    "Checks for pow(-0.0, y), with y an odd integer.", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestZero2 = {
    pow_basePZeroExpOddCases, "pow_basePZeroExpOddCases",
    "Checks for pow(0.0, y), with y an odd integer.", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestZero3 = {
    pow_baseNZeroCases, "pow_baseNZeroCases",
    "Checks for pow(-0.0, y), with y finite and even or non-integer number", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestZero4 = {
    pow_basePZeroCases, "pow_basePZeroCases",
    "Checks for pow(0.0, y), with y finite and even or non-integer number", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestRegular = {
    pow_regularCases, "pow_regularCases",
    "Checks a set of regular values", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestPowOf2 = {
    pow_powerOfTwo, "pow_powerOfTwo",
    "Checks the powers of two from 1 to 8", TEST_ENABLED
};
static const SDLTest_TestCaseReference powTestRange = {
    pow_rangeTest, "pow_rangeTest",
    "Checks a range of positive integer to the power of 0", TEST_ENABLED
};

/* SDL_sqrt test cases */

static const SDLTest_TestCaseReference sqrtTestInf = {
    sqrt_infCase, "sqrt_infCase",
    "Checks positive infinity", TEST_ENABLED
};
static const SDLTest_TestCaseReference sqrtTestNan = {
    sqrt_nanCase, "sqrt_nanCase",
    "Checks NAN", TEST_ENABLED
};
static const SDLTest_TestCaseReference sqrtTestDomain = {
    sqrt_outOfDomainCases, "sqrt_outOfDomainCases",
    "Checks for values out of the domain", TEST_ENABLED
};
static const SDLTest_TestCaseReference sqrtTestBase = {
    sqrt_baseCases, "sqrt_baseCases",
    "Checks the base cases", TEST_ENABLED
};
static const SDLTest_TestCaseReference sqrtTestRegular = {
    sqrt_regularCases, "sqrt_regularCases",
    "Checks a set of regular values", TEST_ENABLED
};

/* SDL_scalbn test cases */

static const SDLTest_TestCaseReference scalbnTestInf = {
    scalbn_infCases, "scalbn_infCases",
    "Checks positive and negative infinity arg", TEST_ENABLED
};
static const SDLTest_TestCaseReference scalbnTestBaseZero = {
    scalbn_baseZeroCases, "scalbn_baseZeroCases",
    "Checks for positive and negative zero arg", TEST_ENABLED
};
static const SDLTest_TestCaseReference scalbnTestExpZero = {
    scalbn_expZeroCase, "scalbn_expZeroCase",
    "Checks for zero exp", TEST_ENABLED
};
static const SDLTest_TestCaseReference scalbnTestNan = {
    scalbn_nanCase, "scalbn_nanCase",
    "Checks NAN", TEST_ENABLED
};
static const SDLTest_TestCaseReference scalbnTestRegular = {
    scalbn_regularCases, "scalbn_regularCases",
    "Checks a set of regular cases", TEST_ENABLED
};

/* SDL_cos test cases */

static const SDLTest_TestCaseReference cosTestInf = {
    cos_infCases, "cos_infCases",
    "Checks for positive and negative infinity", TEST_ENABLED
};
static const SDLTest_TestCaseReference cosTestNan = {
    cos_nanCase, "cos_nanCase",
    "Checks NAN", TEST_ENABLED
};
static const SDLTest_TestCaseReference cosTestRegular = {
    cos_regularCases, "cos_regularCases",
    "Checks a set of regular cases", TEST_ENABLED
};
static const SDLTest_TestCaseReference cosTestPrecision = {
    cos_precisionTest, "cos_precisionTest",
    "Checks cosine precision", TEST_ENABLED
};
static const SDLTest_TestCaseReference cosTestRange = {
    cos_rangeTest, "cos_rangeTest",
    "Checks a range of positive integer", TEST_ENABLED
};

/* SDL_sin test cases */

static const SDLTest_TestCaseReference sinTestInf = {
    sin_infCases, "sin_infCases",
    "Checks for positive and negative infinity", TEST_ENABLED
};
static const SDLTest_TestCaseReference sinTestNan = {
    sin_nanCase, "sin_nanCase",
    "Checks NAN", TEST_ENABLED
};
static const SDLTest_TestCaseReference sinTestRegular = {
    sin_regularCases, "sin_regularCases",
    "Checks a set of regular cases", TEST_ENABLED
};
static const SDLTest_TestCaseReference sinTestPrecision = {
    sin_precisionTest, "sin_precisionTest",
    "Checks sine precision", TEST_ENABLED
};
static const SDLTest_TestCaseReference sinTestRange = {
    sin_rangeTest, "sin_rangeTest",
    "Checks a range of positive integer", TEST_ENABLED
};

/* SDL_tan test cases */

static const SDLTest_TestCaseReference tanTestInf = {
    tan_infCases, "tan_infCases",
    "Checks for positive and negative infinity", TEST_ENABLED
};
static const SDLTest_TestCaseReference tanTestNan = {
    tan_nanCase, "tan_nanCase",
    "Checks NAN", TEST_ENABLED
};
static const SDLTest_TestCaseReference tanTestZero = {
    tan_zeroCases, "tan_zeroCases",
    "Checks a set of regular cases", TEST_ENABLED
};
static const SDLTest_TestCaseReference tanTestPrecision = {
    tan_precisionTest, "tan_precisionTest",
    "Checks tangent precision", TEST_ENABLED
};

/* SDL_acos test cases */

static const SDLTest_TestCaseReference acosTestLimit = {
    acos_limitCases, "acos_limitCases",
    "Checks the edge of the domain (+/-1)", TEST_ENABLED
};
static const SDLTest_TestCaseReference acosTestOutOfDomain = {
    acos_outOfDomainCases, "acos_outOfDomainCases",
    "Checks values outside the domain", TEST_ENABLED
};
static const SDLTest_TestCaseReference acosTestNan = {
    acos_nanCase, "acos_nanCase",
    "Checks NAN", TEST_ENABLED
};
static const SDLTest_TestCaseReference acosTestPrecision = {
    acos_precisionTest, "acos_precisionTest",
    "Checks acos precision", TEST_ENABLED
};

/* SDL_asin test cases */

static const SDLTest_TestCaseReference asinTestLimit = {
    asin_limitCases, "asin_limitCases",
    "Checks the edge of the domain (+/-1)", TEST_ENABLED
};
static const SDLTest_TestCaseReference asinTestOutOfDomain = {
    asin_outOfDomainCases, "asin_outOfDomainCases",
    "Checks values outside the domain", TEST_ENABLED
};
static const SDLTest_TestCaseReference asinTestNan = {
    asin_nanCase, "asin_nanCase",
    "Checks NAN", TEST_ENABLED
};
static const SDLTest_TestCaseReference asinTestPrecision = {
    asin_precisionTest, "asin_precisionTest",
    "Checks asin precision", TEST_ENABLED
};

/* SDL_atan test cases */

static const SDLTest_TestCaseReference atanTestLimit = {
    atan_limitCases, "atan_limitCases",
    "Checks the edge of the domain (+/-Infinity)", TEST_ENABLED
};
static const SDLTest_TestCaseReference atanTestZero = {
    atan_zeroCases, "atan_zeroCases",
    "Checks for positive and negative zero", TEST_ENABLED
};
static const SDLTest_TestCaseReference atanTestNan = {
    atan_nanCase, "atan_nanCase",
    "Checks NAN", TEST_ENABLED
};
static const SDLTest_TestCaseReference atanTestPrecision = {
    atan_precisionTest, "atan_precisionTest",
    "Checks atan precision", TEST_ENABLED
};

/* SDL_atan2 test cases */

static const SDLTest_TestCaseReference atan2TestZero1 = {
    atan2_bothZeroCases, "atan2_bothZeroCases",
    "Checks for both arguments being zero", TEST_ENABLED
};
static const SDLTest_TestCaseReference atan2TestZero2 = {
    atan2_yZeroCases, "atan2_yZeroCases",
    "Checks for y=0", TEST_ENABLED
};
static const SDLTest_TestCaseReference atan2TestZero3 = {
    atan2_xZeroCases, "atan2_xZeroCases",
    "Checks for x=0", TEST_ENABLED
};
static const SDLTest_TestCaseReference atan2TestInf1 = {
    atan2_bothInfCases, "atan2_bothInfCases",
    "Checks for both arguments being infinity", TEST_ENABLED
};
static const SDLTest_TestCaseReference atan2TestInf2 = {
    atan2_yInfCases, "atan2_yInfCases",
    "Checks for y=0", TEST_ENABLED
};
static const SDLTest_TestCaseReference atan2TestInf3 = {
    atan2_xInfCases, "atan2_xInfCases",
    "Checks for x=0", TEST_ENABLED
};
static const SDLTest_TestCaseReference atan2TestNan = {
    atan2_nanCases, "atan2_nanCases",
    "Checks NANs", TEST_ENABLED
};
static const SDLTest_TestCaseReference atan2TestQuadrantTopRight = {
    atan2_topRightQuadrantTest, "atan2_topRightQuadrantTest",
    "Checks values in the top right quadrant", TEST_ENABLED
};
static const SDLTest_TestCaseReference atan2TestQuadrantTopLeft = {
    atan2_topLeftQuadrantTest, "atan2_topLeftQuadrantTest",
    "Checks values in the top left quadrant", TEST_ENABLED
};
static const SDLTest_TestCaseReference atan2TestQuadrantBottomRight = {
    atan2_bottomRightQuadrantTest, "atan2_bottomRightQuadrantTest",
    "Checks values in the bottom right quadrant", TEST_ENABLED
};
static const SDLTest_TestCaseReference atan2TestQuadrantBottomLeft = {
    atan2_bottomLeftQuadrantTest, "atan2_bottomLeftQuadrantTest",
    "Checks values in the bottom left quadrant", TEST_ENABLED
};

static const SDLTest_TestCaseReference *mathTests[] = {
    &floorTestInf, &floorTestZero, &floorTestNan,
    &floorTestRound, &floorTestFraction, &floorTestRange,

    &ceilTestInf, &ceilTestZero, &ceilTestNan,
    &ceilTestRound, &ceilTestFraction, &ceilTestRange,

    &truncTestInf, &truncTestZero, &truncTestNan,
    &truncTestRound, &truncTestFraction, &truncTestRange,

    &roundTestInf, &roundTestZero, &roundTestNan,
    &roundTestRound, &roundTestFraction, &roundTestRange,

    &fabsTestInf, &fabsTestZero, &fabsTestNan, &fabsTestRange,

    &copysignTestInf, &copysignTestZero, &copysignTestNan, &copysignTestRange,

    &fmodTestDivOfInf, &fmodTestDivByInf, &fmodTestDivOfZero, &fmodTestDivByZero,
    &fmodTestNan, &fmodTestRegular, &fmodTestRange,

    &expTestInf, &expTestZero, &expTestOverflow,
    &expTestBase, &expTestRegular,

    &logTestLimit, &logTestNan,
    &logTestBase, &logTestRegular,

    &log10TestLimit, &log10TestNan,
    &log10TestBase, &log10TestRegular,

    &modfTestBase,

    &powTestExpInf1, &powTestExpInf2, &powTestExpInf3,
    &powTestBaseInf1, &powTestBaseInf2,
    &powTestNan1, &powTestNan2, &powTestNan3, &powTestNan4,
    &powTestZero1, &powTestZero2, &powTestZero3, &powTestZero4,
    &powTestRegular, &powTestPowOf2, &powTestRange,

    &sqrtTestInf, &sqrtTestNan, &sqrtTestDomain,
    &sqrtTestBase, &sqrtTestRegular,

    &scalbnTestInf, &scalbnTestBaseZero, &scalbnTestExpZero,
    &scalbnTestNan, &scalbnTestRegular,

    &cosTestInf, &cosTestNan, &cosTestRegular,
    &cosTestPrecision, &cosTestRange,

    &sinTestInf, &sinTestNan, &sinTestRegular,
    &sinTestPrecision, &sinTestRange,

    &tanTestInf, &tanTestNan, &tanTestZero, &tanTestPrecision,

    &acosTestLimit, &acosTestOutOfDomain, &acosTestNan, &acosTestPrecision,

    &asinTestLimit, &asinTestOutOfDomain, &asinTestNan, &asinTestPrecision,

    &atanTestLimit, &atanTestZero, &atanTestNan, &atanTestPrecision,

    &atan2TestZero1, &atan2TestZero2, &atan2TestZero3,
    &atan2TestInf1, &atan2TestInf2, &atan2TestInf3,
    &atan2TestNan, &atan2TestQuadrantTopRight, &atan2TestQuadrantTopLeft,
    &atan2TestQuadrantBottomRight, &atan2TestQuadrantBottomLeft,

    NULL
};

SDLTest_TestSuiteReference mathTestSuite = {
    "Math",
    NULL,
    mathTests,
    NULL
};
