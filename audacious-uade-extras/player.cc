#include </usr/include/python3.12/Python.h>
#include <string>
#include <vector>
#include <optional>

#include "player/player.h"

#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>

using namespace common;
using namespace player;
using namespace std;

// Struct to hold the memory-backed stream and buffer
struct MemoryStream {
    FILE* stream;
    char* buffer;
    size_t buffer_size;
};

// Function to create a memory-backed stream
MemoryStream* create_memory_stream() {
    MemoryStream* mem_stream = new MemoryStream();
    mem_stream->stream = open_memstream(&mem_stream->buffer, &mem_stream->buffer_size);
    if (!mem_stream->stream) {
        delete mem_stream;
        return nullptr;
    }
    return mem_stream;
}

// Destructor function for the capsule
static void free_memory_stream(PyObject* capsule) {
    MemoryStream* mem_stream = (MemoryStream*)PyCapsule_GetPointer(capsule, NULL);
    if (mem_stream) {
        if (mem_stream->stream) {
            fclose(mem_stream->stream);
        }
        if (mem_stream->buffer) {
            free(mem_stream->buffer);
        }
        free(mem_stream);
    }
}

// Function to write to the memory-backed stream
void write_to_memory_stream(MemoryStream* mem_stream, const char* buf, int bytes) {
    if (mem_stream && mem_stream->stream) {
        fwrite(buf, 1, bytes, mem_stream->stream);
        fflush(mem_stream->stream); // Ensure data is written to the buffer
    }
}

// Function to get the buffer content
static PyObject* get_buffer_content(PyObject* self, PyObject* args) {
    PyObject* capsule;
    if (!PyArg_ParseTuple(args, "O", &capsule)) {
        return NULL;
    }

    // Get the MemoryStream from the capsule
    MemoryStream* mem_stream = (MemoryStream*)PyCapsule_GetPointer(capsule, NULL);
    if (!mem_stream) {
        PyErr_SetString(PyExc_RuntimeError, "Invalid capsule");
        return NULL;
    }

    // Return the buffer content as a Python bytes object
    return PyBytes_FromStringAndSize(mem_stream->buffer, mem_stream->buffer_size);
}

// Python wrapper function to play audio and return a memory-backed stream
static PyObject* play_audio(PyObject* self, PyObject* args) {
    const char* fname;
    int frequency;
    int subsong = -1;
    if (!PyArg_ParseTuple(args, "si|i", &fname, &frequency, &subsong)) {
        return NULL;
    }

    FILE *f = fopen(fname, "rb");
    if (!f) {
        PyErr_SetString(PyExc_FileNotFoundError, "File not found");
        return NULL;
    }
    int fd = fileno(f);

    struct stat st;
    if (fstat(fd, &st)) {
        close(fd);
        PyErr_SetString(PyExc_IOError, "Failed to read file size");
        return NULL;
    }

    char buf[4096];
    vector<char> buffer;
    buffer.reserve(st.st_size);

    ssize_t count;
    while ((count = read(fd, buf, sizeof buf)) > 0) {
        buffer.insert(buffer.end(), buf, buf + count);
    }
    close(fd);

    const support::PlayerScope p;

    vector<Player> players = check(fname, buffer.data(), buffer.size());
    if (players.empty()) {
        PyErr_SetString(PyExc_RuntimeError, "Could not recognize file");
        return NULL;
    }

    optional<ModuleInfo> info;
    for (const auto player : players) {
        info = parse(fname, buffer.data(), buffer.size(), player);
        if (info) break;
    }
    if (!info) {
        PyErr_SetString(PyExc_RuntimeError, "Could not parse file");
        return NULL;
    }

    PlayerConfig player_config = { info->player, frequency };
    auto uade_config = uade::UADEConfig(player_config);
    auto it2play_config = it2play::IT2PlayConfig(player_config);
    auto &config =
            info->player == Player::uade ? uade_config :
            info->player == Player::it2play ? it2play_config :
            player_config;

    if (subsong < 0) {
        subsong = info->defsubsong;
    } else {
        subsong = subsong + info->minsubsong;
    }

    auto state = play(fname, buffer.data(), buffer.size(), subsong, config);
    if (!state) {
        PyErr_SetString(PyExc_RuntimeError, "Could not play file");
        return NULL;
    }

    if (state->frequency != frequency) {
        PyErr_SetString(PyExc_RuntimeError, "Frequency not supported");
        return NULL;
    }

    // Create a memory-backed stream
    MemoryStream* mem_stream = create_memory_stream();
    if (!mem_stream) {
        PyErr_SetString(PyExc_MemoryError, "Failed to create memory stream");
        return NULL;
    }

    // Modify the write_audio callback to write to the memory-backed stream
    const auto write_audio = [mem_stream](char *buf, int bytes) {
        write_to_memory_stream(mem_stream, buf, bytes);
    };

    const auto check_stop = []() { return false; };
    const auto check_seek = []() { return -1; };

    const auto res = support::playback_loop(state.value(), config, check_stop, check_seek, write_audio);

    if (!stop(state.value())) {
        PyErr_SetString(PyExc_RuntimeError, "Could not stop playback");
        free_memory_stream((PyObject*)mem_stream);
        return NULL;
    }

    if (res.songend.status == SongEnd::ERROR) {
        PyErr_SetString(PyExc_RuntimeError, "Error playing file");
        free_memory_stream((PyObject*)mem_stream);
        return NULL;
    }

    // Return the memory-backed stream as a PyCapsule
    return PyCapsule_New(mem_stream, NULL, free_memory_stream);
}

// Module method table
static PyMethodDef SongtoolsMethods[] = {
        {"play_audio", play_audio, METH_VARARGS, "Play audio and return a memory-backed stream"},
        {"get_buffer_content", get_buffer_content, METH_VARARGS, "Get the buffer content from a memory-backed stream"},
        {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef songtoolsmodule = {
        PyModuleDef_HEAD_INIT,
        "songtools",  // Module name
        NULL,      // Module documentation (can be NULL)
        -1,        // Size of per-interpreter state (or -1 if the module keeps state in global variables)
        SongtoolsMethods
};

// Module initialization function
PyMODINIT_FUNC PyInit_songtools(void) {
    return PyModule_Create(&songtoolsmodule);
}