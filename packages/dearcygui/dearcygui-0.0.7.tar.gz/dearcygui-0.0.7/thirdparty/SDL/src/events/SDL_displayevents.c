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

// Display event handling code for SDL

#include "SDL_events_c.h"

void SDL_SendDisplayEvent(SDL_VideoDisplay *display, SDL_EventType displayevent, int data1, int data2)
{
    if (!display || display->id == 0) {
        return;
    }
    switch (displayevent) {
    case SDL_EVENT_DISPLAY_ORIENTATION:
        if (data1 == SDL_ORIENTATION_UNKNOWN || data1 == display->current_orientation) {
            return;
        }
        display->current_orientation = (SDL_DisplayOrientation)data1;
        break;
    default:
        break;
    }

    // Post the event, if desired
    if (SDL_EventEnabled(displayevent)) {
        SDL_Event event;
        event.type = displayevent;
        event.common.timestamp = 0;
        event.display.displayID = display->id;
        event.display.data1 = data1;
        event.display.data2 = data2;
        SDL_PushEvent(&event);
    }

    switch (displayevent) {
    case SDL_EVENT_DISPLAY_ADDED:
        SDL_OnDisplayAdded(display);
        break;
    case SDL_EVENT_DISPLAY_MOVED:
        SDL_OnDisplayMoved(display);
        break;
    default:
        break;
    }
}
