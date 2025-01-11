/*
  Copyright (C) 1997-2024 Sam Lantinga <slouken@libsdl.org>

  This software is provided 'as-is', without any express or implied
  warranty.  In no event will the authors be held liable for any damages
  arising from the use of this software.

  Permission is granted to anyone to use this software for any purpose,
  including commercial applications, and to alter it and redistribute it
  freely.
*/
/* This is a simple example of using GLSL shaders with SDL */

#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>
#include <SDL3/SDL_test.h>

#include "testutils.h"

#include <stdlib.h>

#ifdef HAVE_OPENGL

#include <SDL3/SDL_opengl.h>

static bool shaders_supported;
static int current_shader = 0;

enum
{
    SHADER_COLOR,
    SHADER_TEXTURE,
    SHADER_TEXCOORDS,
    NUM_SHADERS
};

typedef struct
{
    GLhandleARB program;
    GLhandleARB vert_shader;
    GLhandleARB frag_shader;
    const char *vert_source;
    const char *frag_source;
} ShaderData;

static ShaderData shaders[NUM_SHADERS] = {

    /* SHADER_COLOR */
    { 0, 0, 0,
      /* vertex shader */
      "varying vec4 v_color;\n"
      "\n"
      "void main()\n"
      "{\n"
      "    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;\n"
      "    v_color = gl_Color;\n"
      "}",
      /* fragment shader */
      "varying vec4 v_color;\n"
      "\n"
      "void main()\n"
      "{\n"
      "    gl_FragColor = v_color;\n"
      "}" },

    /* SHADER_TEXTURE */
    { 0, 0, 0,
      /* vertex shader */
      "varying vec4 v_color;\n"
      "varying vec2 v_texCoord;\n"
      "\n"
      "void main()\n"
      "{\n"
      "    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;\n"
      "    v_color = gl_Color;\n"
      "    v_texCoord = vec2(gl_MultiTexCoord0);\n"
      "}",
      /* fragment shader */
      "varying vec4 v_color;\n"
      "varying vec2 v_texCoord;\n"
      "uniform sampler2D tex0;\n"
      "\n"
      "void main()\n"
      "{\n"
      "    gl_FragColor = texture2D(tex0, v_texCoord) * v_color;\n"
      "}" },

    /* SHADER_TEXCOORDS */
    { 0, 0, 0,
      /* vertex shader */
      "varying vec2 v_texCoord;\n"
      "\n"
      "void main()\n"
      "{\n"
      "    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;\n"
      "    v_texCoord = vec2(gl_MultiTexCoord0);\n"
      "}",
      /* fragment shader */
      "varying vec2 v_texCoord;\n"
      "\n"
      "void main()\n"
      "{\n"
      "    vec4 color;\n"
      "    vec2 delta;\n"
      "    float dist;\n"
      "\n"
      "    delta = vec2(0.5, 0.5) - v_texCoord;\n"
      "    dist = dot(delta, delta);\n"
      "\n"
      "    color.r = v_texCoord.x;\n"
      "    color.g = v_texCoord.x * v_texCoord.y;\n"
      "    color.b = v_texCoord.y;\n"
      "    color.a = 1.0 - (dist * 4.0);\n"
      "    gl_FragColor = color;\n"
      "}" },
};

static PFNGLATTACHOBJECTARBPROC pglAttachObjectARB;
static PFNGLCOMPILESHADERARBPROC pglCompileShaderARB;
static PFNGLCREATEPROGRAMOBJECTARBPROC pglCreateProgramObjectARB;
static PFNGLCREATESHADEROBJECTARBPROC pglCreateShaderObjectARB;
static PFNGLDELETEOBJECTARBPROC pglDeleteObjectARB;
static PFNGLGETINFOLOGARBPROC pglGetInfoLogARB;
static PFNGLGETOBJECTPARAMETERIVARBPROC pglGetObjectParameterivARB;
static PFNGLGETUNIFORMLOCATIONARBPROC pglGetUniformLocationARB;
static PFNGLLINKPROGRAMARBPROC pglLinkProgramARB;
static PFNGLSHADERSOURCEARBPROC pglShaderSourceARB;
static PFNGLUNIFORM1IARBPROC pglUniform1iARB;
static PFNGLUSEPROGRAMOBJECTARBPROC pglUseProgramObjectARB;

static bool CompileShader(GLhandleARB shader, const char *source)
{
    GLint status = 0;

    pglShaderSourceARB(shader, 1, &source, NULL);
    pglCompileShaderARB(shader);
    pglGetObjectParameterivARB(shader, GL_OBJECT_COMPILE_STATUS_ARB, &status);
    if (status == 0) {
        GLint length = 0;
        char *info;

        pglGetObjectParameterivARB(shader, GL_OBJECT_INFO_LOG_LENGTH_ARB, &length);
        info = (char *)SDL_malloc((size_t)length + 1);
        if (!info) {
            SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "Out of memory!");
        } else {
            pglGetInfoLogARB(shader, length, NULL, info);
            SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "Failed to compile shader:\n%s\n%s", source, info);
            SDL_free(info);
        }
        return false;
    } else {
        return true;
    }
}

static bool LinkProgram(ShaderData *data)
{
    GLint status = 0;

    pglAttachObjectARB(data->program, data->vert_shader);
    pglAttachObjectARB(data->program, data->frag_shader);
    pglLinkProgramARB(data->program);

    pglGetObjectParameterivARB(data->program, GL_OBJECT_LINK_STATUS_ARB, &status);
    if (status == 0) {
        GLint length = 0;
        char *info;

        pglGetObjectParameterivARB(data->program, GL_OBJECT_INFO_LOG_LENGTH_ARB, &length);
        info = (char *)SDL_malloc((size_t)length + 1);
        if (!info) {
            SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "Out of memory!");
        } else {
            pglGetInfoLogARB(data->program, length, NULL, info);
            SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "Failed to link program:\n%s", info);
            SDL_free(info);
        }
        return false;
    } else {
        return true;
    }
}

static bool CompileShaderProgram(ShaderData *data)
{
    const int num_tmus_bound = 4;
    int i;
    GLint location;

    glGetError();

    /* Create one program object to rule them all */
    data->program = pglCreateProgramObjectARB();

    /* Create the vertex shader */
    data->vert_shader = pglCreateShaderObjectARB(GL_VERTEX_SHADER_ARB);
    if (!CompileShader(data->vert_shader, data->vert_source)) {
        return false;
    }

    /* Create the fragment shader */
    data->frag_shader = pglCreateShaderObjectARB(GL_FRAGMENT_SHADER_ARB);
    if (!CompileShader(data->frag_shader, data->frag_source)) {
        return false;
    }

    /* ... and in the darkness bind them */
    if (!LinkProgram(data)) {
        return false;
    }

    /* Set up some uniform variables */
    pglUseProgramObjectARB(data->program);
    for (i = 0; i < num_tmus_bound; ++i) {
        char tex_name[5];
        (void)SDL_snprintf(tex_name, SDL_arraysize(tex_name), "tex%d", i);
        location = pglGetUniformLocationARB(data->program, tex_name);
        if (location >= 0) {
            pglUniform1iARB(location, i);
        }
    }
    pglUseProgramObjectARB(0);

    return (glGetError() == GL_NO_ERROR);
}

static void DestroyShaderProgram(ShaderData *data)
{
    if (shaders_supported) {
        pglDeleteObjectARB(data->vert_shader);
        pglDeleteObjectARB(data->frag_shader);
        pglDeleteObjectARB(data->program);
    }
}

static bool InitShaders(void)
{
    int i;

    /* Check for shader support */
    shaders_supported = false;
    if (SDL_GL_ExtensionSupported("GL_ARB_shader_objects") &&
        SDL_GL_ExtensionSupported("GL_ARB_shading_language_100") &&
        SDL_GL_ExtensionSupported("GL_ARB_vertex_shader") &&
        SDL_GL_ExtensionSupported("GL_ARB_fragment_shader")) {
        pglAttachObjectARB = (PFNGLATTACHOBJECTARBPROC)SDL_GL_GetProcAddress("glAttachObjectARB");
        pglCompileShaderARB = (PFNGLCOMPILESHADERARBPROC)SDL_GL_GetProcAddress("glCompileShaderARB");
        pglCreateProgramObjectARB = (PFNGLCREATEPROGRAMOBJECTARBPROC)SDL_GL_GetProcAddress("glCreateProgramObjectARB");
        pglCreateShaderObjectARB = (PFNGLCREATESHADEROBJECTARBPROC)SDL_GL_GetProcAddress("glCreateShaderObjectARB");
        pglDeleteObjectARB = (PFNGLDELETEOBJECTARBPROC)SDL_GL_GetProcAddress("glDeleteObjectARB");
        pglGetInfoLogARB = (PFNGLGETINFOLOGARBPROC)SDL_GL_GetProcAddress("glGetInfoLogARB");
        pglGetObjectParameterivARB = (PFNGLGETOBJECTPARAMETERIVARBPROC)SDL_GL_GetProcAddress("glGetObjectParameterivARB");
        pglGetUniformLocationARB = (PFNGLGETUNIFORMLOCATIONARBPROC)SDL_GL_GetProcAddress("glGetUniformLocationARB");
        pglLinkProgramARB = (PFNGLLINKPROGRAMARBPROC)SDL_GL_GetProcAddress("glLinkProgramARB");
        pglShaderSourceARB = (PFNGLSHADERSOURCEARBPROC)SDL_GL_GetProcAddress("glShaderSourceARB");
        pglUniform1iARB = (PFNGLUNIFORM1IARBPROC)SDL_GL_GetProcAddress("glUniform1iARB");
        pglUseProgramObjectARB = (PFNGLUSEPROGRAMOBJECTARBPROC)SDL_GL_GetProcAddress("glUseProgramObjectARB");
        if (pglAttachObjectARB &&
            pglCompileShaderARB &&
            pglCreateProgramObjectARB &&
            pglCreateShaderObjectARB &&
            pglDeleteObjectARB &&
            pglGetInfoLogARB &&
            pglGetObjectParameterivARB &&
            pglGetUniformLocationARB &&
            pglLinkProgramARB &&
            pglShaderSourceARB &&
            pglUniform1iARB &&
            pglUseProgramObjectARB) {
            shaders_supported = true;
        }
    }

    if (!shaders_supported) {
        return false;
    }

    /* Compile all the shaders */
    for (i = 0; i < NUM_SHADERS; ++i) {
        if (!CompileShaderProgram(&shaders[i])) {
            SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "Unable to compile shader!\n");
            return false;
        }
    }

    /* We're done! */
    return true;
}

static void QuitShaders(void)
{
    int i;

    for (i = 0; i < NUM_SHADERS; ++i) {
        DestroyShaderProgram(&shaders[i]);
    }
}

/* Quick utility function for texture creation */
static int
power_of_two(int input)
{
    int value = 1;

    while (value < input) {
        value <<= 1;
    }
    return value;
}

static GLuint
SDL_GL_LoadTexture(SDL_Surface *surface, GLfloat *texcoord)
{
    GLuint texture;
    int w, h;
    SDL_Surface *image;
    SDL_Rect area;
    SDL_BlendMode saved_mode;

    /* Use the surface width and height expanded to powers of 2 */
    w = power_of_two(surface->w);
    h = power_of_two(surface->h);
    texcoord[0] = 0.0f;                    /* Min X */
    texcoord[1] = 0.0f;                    /* Min Y */
    texcoord[2] = (GLfloat)surface->w / w; /* Max X */
    texcoord[3] = (GLfloat)surface->h / h; /* Max Y */

    image = SDL_CreateSurface(w, h, SDL_PIXELFORMAT_RGBA32);
    if (!image) {
        return 0;
    }

    /* Save the alpha blending attributes */
    SDL_GetSurfaceBlendMode(surface, &saved_mode);
    SDL_SetSurfaceBlendMode(surface, SDL_BLENDMODE_NONE);

    /* Copy the surface into the GL texture image */
    area.x = 0;
    area.y = 0;
    area.w = surface->w;
    area.h = surface->h;
    SDL_BlitSurface(surface, &area, image, &area);

    /* Restore the alpha blending attributes */
    SDL_SetSurfaceBlendMode(surface, saved_mode);

    /* Create an OpenGL texture for the image */
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexImage2D(GL_TEXTURE_2D,
                 0,
                 GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, image->pixels);
    SDL_DestroySurface(image); /* No longer needed */

    return texture;
}

/* A general OpenGL initialization function.    Sets all of the initial parameters. */
static void InitGL(int Width, int Height) /* We call this right after our OpenGL window is created. */
{
    GLdouble aspect;

    glViewport(0, 0, Width, Height);
    glClearColor(0.0f, 0.0f, 0.0f, 0.0f); /* This Will Clear The Background Color To Black */
    glClearDepth(1.0);                    /* Enables Clearing Of The Depth Buffer */
    glDepthFunc(GL_LESS);                 /* The Type Of Depth Test To Do */
    glEnable(GL_DEPTH_TEST);              /* Enables Depth Testing */
    glShadeModel(GL_SMOOTH);              /* Enables Smooth Color Shading */

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity(); /* Reset The Projection Matrix */

    aspect = (GLdouble)Width / Height;
    glOrtho(-3.0, 3.0, -3.0 / aspect, 3.0 / aspect, 0.0, 1.0);

    glMatrixMode(GL_MODELVIEW);
}

/* The main drawing function. */
static void DrawGLScene(SDL_Window *window, GLuint texture, GLfloat *texcoord)
{
    /* Texture coordinate lookup, to make it simple */
    enum
    {
        MINX,
        MINY,
        MAXX,
        MAXY
    };

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); /* Clear The Screen And The Depth Buffer */
    glLoadIdentity();                                   /* Reset The View */

    glTranslatef(-1.5f, 0.0f, 0.0f); /* Move Left 1.5 Units */

    /* draw a triangle (in smooth coloring mode) */
    glBegin(GL_POLYGON);            /* start drawing a polygon */
    glColor3f(1.0f, 0.0f, 0.0f);    /* Set The Color To Red */
    glVertex3f(0.0f, 1.0f, 0.0f);   /* Top */
    glColor3f(0.0f, 1.0f, 0.0f);    /* Set The Color To Green */
    glVertex3f(1.0f, -1.0f, 0.0f);  /* Bottom Right */
    glColor3f(0.0f, 0.0f, 1.0f);    /* Set The Color To Blue */
    glVertex3f(-1.0f, -1.0f, 0.0f); /* Bottom Left */
    glEnd();                        /* we're done with the polygon (smooth color interpolation) */

    glTranslatef(3.0f, 0.0f, 0.0f); /* Move Right 3 Units */

    /* Enable blending */
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    /* draw a textured square (quadrilateral) */
    glEnable(GL_TEXTURE_2D);
    glBindTexture(GL_TEXTURE_2D, texture);
    glColor3f(1.0f, 1.0f, 1.0f);
    if (shaders_supported) {
        pglUseProgramObjectARB(shaders[current_shader].program);
    }

    glBegin(GL_QUADS); /* start drawing a polygon (4 sided) */
    glTexCoord2f(texcoord[MINX], texcoord[MINY]);
    glVertex3f(-1.0f, 1.0f, 0.0f); /* Top Left */
    glTexCoord2f(texcoord[MAXX], texcoord[MINY]);
    glVertex3f(1.0f, 1.0f, 0.0f); /* Top Right */
    glTexCoord2f(texcoord[MAXX], texcoord[MAXY]);
    glVertex3f(1.0f, -1.0f, 0.0f); /* Bottom Right */
    glTexCoord2f(texcoord[MINX], texcoord[MAXY]);
    glVertex3f(-1.0f, -1.0f, 0.0f); /* Bottom Left */
    glEnd();                        /* done with the polygon */

    if (shaders_supported) {
        pglUseProgramObjectARB(0);
    }
    glDisable(GL_TEXTURE_2D);

    /* swap buffers to display, since we're double buffered. */
    SDL_GL_SwapWindow(window);
}

int main(int argc, char **argv)
{
    int i;
    int done;
    SDL_Window *window;
    char *filename = NULL;
    SDL_Surface *surface;
    GLuint texture;
    GLfloat texcoords[4];
    SDLTest_CommonState *state;

    /* Initialize test framework */
    state = SDLTest_CommonCreateState(argv, 0);
    if (!state) {
        return 1;
    }

    /* Parse commandline */
    for (i = 1; i < argc;) {
        int consumed;

        consumed = SDLTest_CommonArg(state, i);
        if (!consumed) {
            if (!filename) {
                filename = argv[i];
                consumed = 1;
            }
        }
        if (consumed <= 0) {
            static const char *options[] = { "[icon.bmp]", NULL };
            SDLTest_CommonLogUsage(state, argv[0], options);
            exit(1);
        }

        i += consumed;
    }

    /* Initialize SDL for video output */
    if (!SDL_Init(SDL_INIT_VIDEO)) {
        SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "Unable to initialize SDL: %s\n", SDL_GetError());
        exit(1);
    }

    /* Create a 640x480 OpenGL screen */
    window = SDL_CreateWindow("Shader Demo", 640, 480, SDL_WINDOW_OPENGL);
    if (!window) {
        SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "Unable to create OpenGL window: %s\n", SDL_GetError());
        SDL_Quit();
        exit(2);
    }

    if (!SDL_GL_CreateContext(window)) {
        SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "Unable to create OpenGL context: %s\n", SDL_GetError());
        SDL_Quit();
        exit(2);
    }

    filename = GetResourceFilename(NULL, "icon.bmp");
    surface = SDL_LoadBMP(filename);
    SDL_free(filename);

    if (!surface) {
        SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "Unable to load icon.bmp: %s\n", SDL_GetError());
        SDL_Quit();
        exit(3);
    }
    texture = SDL_GL_LoadTexture(surface, texcoords);
    SDL_DestroySurface(surface);

    /* Loop, drawing and checking events */
    InitGL(640, 480);
    if (InitShaders()) {
        SDL_Log("Shaders supported, press SPACE to cycle them.\n");
    } else {
        SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "Shaders not supported!\n");
    }
    done = 0;
    while (!done) {
        DrawGLScene(window, texture, texcoords);

        /* This could go in a separate function */
        {
            SDL_Event event;
            while (SDL_PollEvent(&event)) {
                if (event.type == SDL_EVENT_QUIT) {
                    done = 1;
                }
                if (event.type == SDL_EVENT_KEY_DOWN) {
                    if (event.key.key == SDLK_SPACE) {
                        current_shader = (current_shader + 1) % NUM_SHADERS;
                    }
                    if (event.key.key == SDLK_ESCAPE) {
                        done = 1;
                    }
                }
            }
        }
    }
    QuitShaders();
    SDL_Quit();
    SDLTest_CommonDestroyState(state);
    return 1;
}

#else /* HAVE_OPENGL */

int main(int argc, char *argv[])
{
    SDL_LogError(SDL_LOG_CATEGORY_APPLICATION, "No OpenGL support on this system\n");
    return 1;
}

#endif /* HAVE_OPENGL */
