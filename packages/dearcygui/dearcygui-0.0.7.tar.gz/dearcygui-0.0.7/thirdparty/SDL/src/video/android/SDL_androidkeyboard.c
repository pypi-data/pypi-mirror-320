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
#include "SDL_internal.h"

#ifdef SDL_VIDEO_DRIVER_ANDROID

#include <android/log.h>

#include "../../events/SDL_events_c.h"

#include "SDL_androidkeyboard.h"

#include "../../core/android/SDL_android.h"

#define TYPE_CLASS_TEXT                         0x00000001
#define TYPE_CLASS_NUMBER                       0x00000002
#define TYPE_CLASS_PHONE                        0x00000003
#define TYPE_CLASS_DATETIME                     0x00000004

#define TYPE_DATETIME_VARIATION_NORMAL          0x00000000
#define TYPE_DATETIME_VARIATION_DATE            0x00000010
#define TYPE_DATETIME_VARIATION_TIME            0x00000020

#define TYPE_NUMBER_VARIATION_NORMAL            0x00000000
#define TYPE_NUMBER_VARIATION_PASSWORD          0x00000010
#define TYPE_NUMBER_FLAG_SIGNED                 0x00001000
#define TYPE_NUMBER_FLAG_DECIMAL                0x00002000

#define TYPE_TEXT_FLAG_CAP_CHARACTERS           0x00001000
#define TYPE_TEXT_FLAG_CAP_WORDS                0x00002000
#define TYPE_TEXT_FLAG_CAP_SENTENCES            0x00004000
#define TYPE_TEXT_FLAG_AUTO_CORRECT             0x00008000
#define TYPE_TEXT_FLAG_AUTO_COMPLETE            0x00010000
#define TYPE_TEXT_FLAG_MULTI_LINE               0x00020000
#define TYPE_TEXT_FLAG_IME_MULTI_LINE           0x00040000
#define TYPE_TEXT_FLAG_NO_SUGGESTIONS           0x00080000

#define TYPE_TEXT_VARIATION_NORMAL              0x00000000
#define TYPE_TEXT_VARIATION_URI                 0x00000010
#define TYPE_TEXT_VARIATION_EMAIL_ADDRESS       0x00000020
#define TYPE_TEXT_VARIATION_EMAIL_SUBJECT       0x00000030
#define TYPE_TEXT_VARIATION_SHORT_MESSAGE       0x00000040
#define TYPE_TEXT_VARIATION_LONG_MESSAGE        0x00000050
#define TYPE_TEXT_VARIATION_PERSON_NAME         0x00000060
#define TYPE_TEXT_VARIATION_POSTAL_ADDRESS      0x00000070
#define TYPE_TEXT_VARIATION_PASSWORD            0x00000080
#define TYPE_TEXT_VARIATION_VISIBLE_PASSWORD    0x00000090
#define TYPE_TEXT_VARIATION_WEB_EDIT_TEXT       0x000000a0
#define TYPE_TEXT_VARIATION_FILTER              0x000000b0
#define TYPE_TEXT_VARIATION_PHONETIC            0x000000c0
#define TYPE_TEXT_VARIATION_WEB_EMAIL_ADDRESS   0x000000d0
#define TYPE_TEXT_VARIATION_WEB_PASSWORD        0x000000e0


static SDL_Scancode Android_Keycodes[] = {
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_UNKNOWN
    SDL_SCANCODE_SOFTLEFT,         // AKEYCODE_SOFT_LEFT
    SDL_SCANCODE_SOFTRIGHT,        // AKEYCODE_SOFT_RIGHT
    SDL_SCANCODE_AC_HOME,          // AKEYCODE_HOME
    SDL_SCANCODE_AC_BACK,          // AKEYCODE_BACK
    SDL_SCANCODE_CALL,             // AKEYCODE_CALL
    SDL_SCANCODE_ENDCALL,          // AKEYCODE_ENDCALL
    SDL_SCANCODE_0,                // AKEYCODE_0
    SDL_SCANCODE_1,                // AKEYCODE_1
    SDL_SCANCODE_2,                // AKEYCODE_2
    SDL_SCANCODE_3,                // AKEYCODE_3
    SDL_SCANCODE_4,                // AKEYCODE_4
    SDL_SCANCODE_5,                // AKEYCODE_5
    SDL_SCANCODE_6,                // AKEYCODE_6
    SDL_SCANCODE_7,                // AKEYCODE_7
    SDL_SCANCODE_8,                // AKEYCODE_8
    SDL_SCANCODE_9,                // AKEYCODE_9
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_STAR
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_POUND
    SDL_SCANCODE_UP,               // AKEYCODE_DPAD_UP
    SDL_SCANCODE_DOWN,             // AKEYCODE_DPAD_DOWN
    SDL_SCANCODE_LEFT,             // AKEYCODE_DPAD_LEFT
    SDL_SCANCODE_RIGHT,            // AKEYCODE_DPAD_RIGHT
    SDL_SCANCODE_SELECT,           // AKEYCODE_DPAD_CENTER
    SDL_SCANCODE_VOLUMEUP,         // AKEYCODE_VOLUME_UP
    SDL_SCANCODE_VOLUMEDOWN,       // AKEYCODE_VOLUME_DOWN
    SDL_SCANCODE_POWER,            // AKEYCODE_POWER
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_CAMERA
    SDL_SCANCODE_CLEAR,            // AKEYCODE_CLEAR
    SDL_SCANCODE_A,                // AKEYCODE_A
    SDL_SCANCODE_B,                // AKEYCODE_B
    SDL_SCANCODE_C,                // AKEYCODE_C
    SDL_SCANCODE_D,                // AKEYCODE_D
    SDL_SCANCODE_E,                // AKEYCODE_E
    SDL_SCANCODE_F,                // AKEYCODE_F
    SDL_SCANCODE_G,                // AKEYCODE_G
    SDL_SCANCODE_H,                // AKEYCODE_H
    SDL_SCANCODE_I,                // AKEYCODE_I
    SDL_SCANCODE_J,                // AKEYCODE_J
    SDL_SCANCODE_K,                // AKEYCODE_K
    SDL_SCANCODE_L,                // AKEYCODE_L
    SDL_SCANCODE_M,                // AKEYCODE_M
    SDL_SCANCODE_N,                // AKEYCODE_N
    SDL_SCANCODE_O,                // AKEYCODE_O
    SDL_SCANCODE_P,                // AKEYCODE_P
    SDL_SCANCODE_Q,                // AKEYCODE_Q
    SDL_SCANCODE_R,                // AKEYCODE_R
    SDL_SCANCODE_S,                // AKEYCODE_S
    SDL_SCANCODE_T,                // AKEYCODE_T
    SDL_SCANCODE_U,                // AKEYCODE_U
    SDL_SCANCODE_V,                // AKEYCODE_V
    SDL_SCANCODE_W,                // AKEYCODE_W
    SDL_SCANCODE_X,                // AKEYCODE_X
    SDL_SCANCODE_Y,                // AKEYCODE_Y
    SDL_SCANCODE_Z,                // AKEYCODE_Z
    SDL_SCANCODE_COMMA,            // AKEYCODE_COMMA
    SDL_SCANCODE_PERIOD,           // AKEYCODE_PERIOD
    SDL_SCANCODE_LALT,             // AKEYCODE_ALT_LEFT
    SDL_SCANCODE_RALT,             // AKEYCODE_ALT_RIGHT
    SDL_SCANCODE_LSHIFT,           // AKEYCODE_SHIFT_LEFT
    SDL_SCANCODE_RSHIFT,           // AKEYCODE_SHIFT_RIGHT
    SDL_SCANCODE_TAB,              // AKEYCODE_TAB
    SDL_SCANCODE_SPACE,            // AKEYCODE_SPACE
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_SYM
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_EXPLORER
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_ENVELOPE
    SDL_SCANCODE_RETURN,           // AKEYCODE_ENTER
    SDL_SCANCODE_BACKSPACE,        // AKEYCODE_DEL
    SDL_SCANCODE_GRAVE,            // AKEYCODE_GRAVE
    SDL_SCANCODE_MINUS,            // AKEYCODE_MINUS
    SDL_SCANCODE_EQUALS,           // AKEYCODE_EQUALS
    SDL_SCANCODE_LEFTBRACKET,      // AKEYCODE_LEFT_BRACKET
    SDL_SCANCODE_RIGHTBRACKET,     // AKEYCODE_RIGHT_BRACKET
    SDL_SCANCODE_BACKSLASH,        // AKEYCODE_BACKSLASH
    SDL_SCANCODE_SEMICOLON,        // AKEYCODE_SEMICOLON
    SDL_SCANCODE_APOSTROPHE,       // AKEYCODE_APOSTROPHE
    SDL_SCANCODE_SLASH,            // AKEYCODE_SLASH
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_AT
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_NUM
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_HEADSETHOOK
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_FOCUS
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_PLUS
    SDL_SCANCODE_MENU,             // AKEYCODE_MENU
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_NOTIFICATION
    SDL_SCANCODE_AC_SEARCH,        // AKEYCODE_SEARCH
    SDL_SCANCODE_MEDIA_PLAY_PAUSE,  // AKEYCODE_MEDIA_PLAY_PAUSE
    SDL_SCANCODE_MEDIA_STOP,       // AKEYCODE_MEDIA_STOP
    SDL_SCANCODE_MEDIA_NEXT_TRACK, // AKEYCODE_MEDIA_NEXT
    SDL_SCANCODE_MEDIA_PREVIOUS_TRACK, // AKEYCODE_MEDIA_PREVIOUS
    SDL_SCANCODE_MEDIA_REWIND,     // AKEYCODE_MEDIA_REWIND
    SDL_SCANCODE_MEDIA_FAST_FORWARD, // AKEYCODE_MEDIA_FAST_FORWARD
    SDL_SCANCODE_MUTE,             // AKEYCODE_MUTE
    SDL_SCANCODE_PAGEUP,           // AKEYCODE_PAGE_UP
    SDL_SCANCODE_PAGEDOWN,         // AKEYCODE_PAGE_DOWN
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_PICTSYMBOLS
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_SWITCH_CHARSET
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_A
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_B
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_C
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_X
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_Y
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_Z
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_L1
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_R1
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_L2
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_R2
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_THUMBL
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_THUMBR
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_START
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_SELECT
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_MODE
    SDL_SCANCODE_ESCAPE,           // AKEYCODE_ESCAPE
    SDL_SCANCODE_DELETE,           // AKEYCODE_FORWARD_DEL
    SDL_SCANCODE_LCTRL,            // AKEYCODE_CTRL_LEFT
    SDL_SCANCODE_RCTRL,            // AKEYCODE_CTRL_RIGHT
    SDL_SCANCODE_CAPSLOCK,         // AKEYCODE_CAPS_LOCK
    SDL_SCANCODE_SCROLLLOCK,       // AKEYCODE_SCROLL_LOCK
    SDL_SCANCODE_LGUI,             // AKEYCODE_META_LEFT
    SDL_SCANCODE_RGUI,             // AKEYCODE_META_RIGHT
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_FUNCTION
    SDL_SCANCODE_PRINTSCREEN,      // AKEYCODE_SYSRQ
    SDL_SCANCODE_PAUSE,            // AKEYCODE_BREAK
    SDL_SCANCODE_HOME,             // AKEYCODE_MOVE_HOME
    SDL_SCANCODE_END,              // AKEYCODE_MOVE_END
    SDL_SCANCODE_INSERT,           // AKEYCODE_INSERT
    SDL_SCANCODE_AC_FORWARD,       // AKEYCODE_FORWARD
    SDL_SCANCODE_MEDIA_PLAY,       // AKEYCODE_MEDIA_PLAY
    SDL_SCANCODE_MEDIA_PAUSE,      // AKEYCODE_MEDIA_PAUSE
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_MEDIA_CLOSE
    SDL_SCANCODE_MEDIA_EJECT,      // AKEYCODE_MEDIA_EJECT
    SDL_SCANCODE_MEDIA_RECORD,     // AKEYCODE_MEDIA_RECORD
    SDL_SCANCODE_F1,               // AKEYCODE_F1
    SDL_SCANCODE_F2,               // AKEYCODE_F2
    SDL_SCANCODE_F3,               // AKEYCODE_F3
    SDL_SCANCODE_F4,               // AKEYCODE_F4
    SDL_SCANCODE_F5,               // AKEYCODE_F5
    SDL_SCANCODE_F6,               // AKEYCODE_F6
    SDL_SCANCODE_F7,               // AKEYCODE_F7
    SDL_SCANCODE_F8,               // AKEYCODE_F8
    SDL_SCANCODE_F9,               // AKEYCODE_F9
    SDL_SCANCODE_F10,              // AKEYCODE_F10
    SDL_SCANCODE_F11,              // AKEYCODE_F11
    SDL_SCANCODE_F12,              // AKEYCODE_F12
    SDL_SCANCODE_NUMLOCKCLEAR,     // AKEYCODE_NUM_LOCK
    SDL_SCANCODE_KP_0,             // AKEYCODE_NUMPAD_0
    SDL_SCANCODE_KP_1,             // AKEYCODE_NUMPAD_1
    SDL_SCANCODE_KP_2,             // AKEYCODE_NUMPAD_2
    SDL_SCANCODE_KP_3,             // AKEYCODE_NUMPAD_3
    SDL_SCANCODE_KP_4,             // AKEYCODE_NUMPAD_4
    SDL_SCANCODE_KP_5,             // AKEYCODE_NUMPAD_5
    SDL_SCANCODE_KP_6,             // AKEYCODE_NUMPAD_6
    SDL_SCANCODE_KP_7,             // AKEYCODE_NUMPAD_7
    SDL_SCANCODE_KP_8,             // AKEYCODE_NUMPAD_8
    SDL_SCANCODE_KP_9,             // AKEYCODE_NUMPAD_9
    SDL_SCANCODE_KP_DIVIDE,        // AKEYCODE_NUMPAD_DIVIDE
    SDL_SCANCODE_KP_MULTIPLY,      // AKEYCODE_NUMPAD_MULTIPLY
    SDL_SCANCODE_KP_MINUS,         // AKEYCODE_NUMPAD_SUBTRACT
    SDL_SCANCODE_KP_PLUS,          // AKEYCODE_NUMPAD_ADD
    SDL_SCANCODE_KP_PERIOD,        // AKEYCODE_NUMPAD_DOT
    SDL_SCANCODE_KP_COMMA,         // AKEYCODE_NUMPAD_COMMA
    SDL_SCANCODE_KP_ENTER,         // AKEYCODE_NUMPAD_ENTER
    SDL_SCANCODE_KP_EQUALS,        // AKEYCODE_NUMPAD_EQUALS
    SDL_SCANCODE_KP_LEFTPAREN,     // AKEYCODE_NUMPAD_LEFT_PAREN
    SDL_SCANCODE_KP_RIGHTPAREN,    // AKEYCODE_NUMPAD_RIGHT_PAREN
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_VOLUME_MUTE
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_INFO
    SDL_SCANCODE_CHANNEL_INCREMENT, // AKEYCODE_CHANNEL_UP
    SDL_SCANCODE_CHANNEL_INCREMENT, // AKEYCODE_CHANNEL_DOWN
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_ZOOM_IN
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_ZOOM_OUT
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_WINDOW
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_GUIDE
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_DVR
    SDL_SCANCODE_AC_BOOKMARKS,     // AKEYCODE_BOOKMARK
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_CAPTIONS
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_SETTINGS
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_POWER
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_INPUT
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_STB_POWER
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_STB_INPUT
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_AVR_POWER
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_AVR_INPUT
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_PROG_RED
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_PROG_GREEN
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_PROG_YELLOW
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_PROG_BLUE
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_APP_SWITCH
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_1
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_2
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_3
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_4
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_5
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_6
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_7
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_8
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_9
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_10
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_11
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_12
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_13
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_14
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_15
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BUTTON_16
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_LANGUAGE_SWITCH
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_MANNER_MODE
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_3D_MODE
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_CONTACTS
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_CALENDAR
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_MUSIC
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_CALCULATOR
    SDL_SCANCODE_LANG5,            // AKEYCODE_ZENKAKU_HANKAKU
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_EISU
    SDL_SCANCODE_INTERNATIONAL5,   // AKEYCODE_MUHENKAN
    SDL_SCANCODE_INTERNATIONAL4,   // AKEYCODE_HENKAN
    SDL_SCANCODE_LANG3,            // AKEYCODE_KATAKANA_HIRAGANA
    SDL_SCANCODE_INTERNATIONAL3,   // AKEYCODE_YEN
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_RO
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_KANA
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_ASSIST
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BRIGHTNESS_DOWN
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_BRIGHTNESS_UP
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_MEDIA_AUDIO_TRACK
    SDL_SCANCODE_SLEEP,            // AKEYCODE_SLEEP
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_WAKEUP
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_PAIRING
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_MEDIA_TOP_MENU
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_11
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_12
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_LAST_CHANNEL
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_DATA_SERVICE
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_VOICE_ASSIST
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_RADIO_SERVICE
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_TELETEXT
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_NUMBER_ENTRY
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_TERRESTRIAL_ANALOG
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_TERRESTRIAL_DIGITAL
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_SATELLITE
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_SATELLITE_BS
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_SATELLITE_CS
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_SATELLITE_SERVICE
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_NETWORK
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_ANTENNA_CABLE
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_INPUT_HDMI_1
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_INPUT_HDMI_2
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_INPUT_HDMI_3
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_INPUT_HDMI_4
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_INPUT_COMPOSITE_1
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_INPUT_COMPOSITE_2
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_INPUT_COMPONENT_1
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_INPUT_COMPONENT_2
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_INPUT_VGA_1
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_AUDIO_DESCRIPTION
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_AUDIO_DESCRIPTION_MIX_UP
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_AUDIO_DESCRIPTION_MIX_DOWN
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_ZOOM_MODE
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_CONTENTS_MENU
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_MEDIA_CONTEXT_MENU
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_TV_TIMER_PROGRAMMING
    SDL_SCANCODE_HELP,             // AKEYCODE_HELP
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_NAVIGATE_PREVIOUS
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_NAVIGATE_NEXT
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_NAVIGATE_IN
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_NAVIGATE_OUT
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_STEM_PRIMARY
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_STEM_1
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_STEM_2
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_STEM_3
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_DPAD_UP_LEFT
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_DPAD_DOWN_LEFT
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_DPAD_UP_RIGHT
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_DPAD_DOWN_RIGHT
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_MEDIA_SKIP_FORWARD
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_MEDIA_SKIP_BACKWARD
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_MEDIA_STEP_FORWARD
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_MEDIA_STEP_BACKWARD
    SDL_SCANCODE_UNKNOWN,          // AKEYCODE_SOFT_SLEEP
    SDL_SCANCODE_CUT,              // AKEYCODE_CUT
    SDL_SCANCODE_COPY,             // AKEYCODE_COPY
    SDL_SCANCODE_PASTE,            // AKEYCODE_PASTE
};

static bool SDL_screen_keyboard_shown;

static SDL_Scancode TranslateKeycode(int keycode)
{
    SDL_Scancode scancode = SDL_SCANCODE_UNKNOWN;

    if (keycode < SDL_arraysize(Android_Keycodes)) {
        scancode = Android_Keycodes[keycode];
    }
    if (scancode == SDL_SCANCODE_UNKNOWN) {
        __android_log_print(ANDROID_LOG_INFO, "SDL", "Unknown keycode %d", keycode);
    }
    return scancode;
}

void Android_OnKeyDown(int keycode)
{
    SDL_SendKeyboardKey(0, SDL_DEFAULT_KEYBOARD_ID, keycode, TranslateKeycode(keycode), true);
}

void Android_OnKeyUp(int keycode)
{
    SDL_SendKeyboardKey(0, SDL_DEFAULT_KEYBOARD_ID, keycode, TranslateKeycode(keycode), false);
}

bool Android_HasScreenKeyboardSupport(SDL_VideoDevice *_this)
{
    return true;
}

void Android_ShowScreenKeyboard(SDL_VideoDevice *_this, SDL_Window *window, SDL_PropertiesID props)
{
    int input_type = 0;
    if (SDL_HasProperty(props, SDL_PROP_TEXTINPUT_ANDROID_INPUTTYPE_NUMBER)) {
        input_type = (int)SDL_GetNumberProperty(props, SDL_PROP_TEXTINPUT_ANDROID_INPUTTYPE_NUMBER, 0);
    } else {
        switch (SDL_GetTextInputType(props)) {
        default:
        case SDL_TEXTINPUT_TYPE_TEXT:
            input_type = (TYPE_CLASS_TEXT | TYPE_TEXT_VARIATION_NORMAL);
            break;
        case SDL_TEXTINPUT_TYPE_TEXT_NAME:
            input_type = (TYPE_CLASS_TEXT | TYPE_TEXT_VARIATION_PERSON_NAME);
            break;
        case SDL_TEXTINPUT_TYPE_TEXT_EMAIL:
            input_type = (TYPE_CLASS_TEXT | TYPE_TEXT_VARIATION_EMAIL_ADDRESS);
            break;
        case SDL_TEXTINPUT_TYPE_TEXT_USERNAME:
            input_type = (TYPE_CLASS_TEXT | TYPE_TEXT_VARIATION_NORMAL);
            break;
        case SDL_TEXTINPUT_TYPE_TEXT_PASSWORD_HIDDEN:
            input_type = (TYPE_CLASS_TEXT | TYPE_TEXT_VARIATION_PASSWORD);
            break;
        case SDL_TEXTINPUT_TYPE_TEXT_PASSWORD_VISIBLE:
            input_type = (TYPE_CLASS_TEXT | TYPE_TEXT_VARIATION_VISIBLE_PASSWORD);
            break;
        case SDL_TEXTINPUT_TYPE_NUMBER:
            input_type = (TYPE_CLASS_NUMBER | TYPE_NUMBER_VARIATION_NORMAL);
            break;
        case SDL_TEXTINPUT_TYPE_NUMBER_PASSWORD_HIDDEN:
            input_type = (TYPE_CLASS_NUMBER | TYPE_NUMBER_VARIATION_PASSWORD);
            break;
        case SDL_TEXTINPUT_TYPE_NUMBER_PASSWORD_VISIBLE:
            input_type = (TYPE_CLASS_NUMBER | TYPE_NUMBER_VARIATION_NORMAL);
            break;
        }

        switch (SDL_GetTextInputCapitalization(props)) {
        default:
        case SDL_CAPITALIZE_NONE:
            break;
        case SDL_CAPITALIZE_LETTERS:
            input_type |= TYPE_TEXT_FLAG_CAP_CHARACTERS;
            break;
        case SDL_CAPITALIZE_WORDS:
            input_type |= TYPE_TEXT_FLAG_CAP_WORDS;
            break;
        case SDL_CAPITALIZE_SENTENCES:
            input_type |= TYPE_TEXT_FLAG_CAP_SENTENCES;
            break;
        }

        if (SDL_GetTextInputAutocorrect(props)) {
            input_type |= (TYPE_TEXT_FLAG_AUTO_CORRECT | TYPE_TEXT_FLAG_AUTO_COMPLETE);
        }

        if (SDL_GetTextInputMultiline(props)) {
            input_type |= TYPE_TEXT_FLAG_MULTI_LINE;
        }
    }
    Android_JNI_ShowScreenKeyboard(input_type, &window->text_input_rect);
    SDL_screen_keyboard_shown = true;
}

void Android_HideScreenKeyboard(SDL_VideoDevice *_this, SDL_Window *window)
{
    Android_JNI_HideScreenKeyboard();
    SDL_screen_keyboard_shown = false;
}

void Android_RestoreScreenKeyboardOnResume(SDL_VideoDevice *_this, SDL_Window *window)
{
    if (SDL_screen_keyboard_shown) {
        Android_ShowScreenKeyboard(_this, window, window->text_input_props);
    }
}

bool Android_IsScreenKeyboardShown(SDL_VideoDevice *_this, SDL_Window *window)
{
    return Android_JNI_IsScreenKeyboardShown();
}

#endif // SDL_VIDEO_DRIVER_ANDROID
