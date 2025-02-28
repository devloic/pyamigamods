// SPDX-License-Identifier: GPL-2.0-or-later
// Copyright (C) 2023-2025 Matti Tiainen <mvtiaine@cc.hut.fi>

// Outputs song lengths in milliseconds to stdout in TSV format (one line for each subsong in the module):
// <md5>\t<subsong>\t<length-milliseconds>\t<songend-reason>
// Optionally also the file size and file name is included:
// <md5>\t<subsong>\t<length-milliseconds>\t<songend-reason>\t<size>\t<filename>

// Errored songlengths are not recorded, except for whitelisted players (OctaMED,VSS) which always crash just at songend.

// Example usage:
// ./precalc <input-file> >> /tmp/Songlengths.csv 2>/dev/null

// NOTE: requires the audacious plugin to be installed to find some conf/data files

#include <vector>

#include "common/md5.h"
#include "player/player.h"
#include "songend/precalc.h"
#include "songdb/songdb.h"
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <bits/stdc++.h>

constexpr int MAX_ERROR_MSG_SIZE =  1024;
constexpr int MAX_FORMAT_SIZE   = 256;
constexpr int MAX_PLAYER_SIZE   = 48;
constexpr int MAX_STATUS_SIZE = 33;

using namespace std;
namespace songtools {

    struct stct_ {
        int i;
    };

    typedef struct {
        int index;
        int length;
        char status[33];
    } subsong_t;

    typedef struct {
        char md5[33];
        subsong_t subsongs[256];
        int nb_subsongs;
        char format[256];
        char player[48];
        int channels;
        int size;
        char error_msg[1024];
        int exit_value = 0;
        int minsubsong;
    } module_t;

    void print(const common::SongEnd &songend, const player::ModuleInfo &info, int subsong, vector<char> &buf,
               const string &md5hex, module_t *module, int i) {

        const auto reason = songend.status_string();
        if (subsong == info.minsubsong) {

            const auto pl = player::name(info.player);
            module->minsubsong= info.minsubsong;
            module->nb_subsongs = info.maxsubsong - info.minsubsong + 1;
            strcpy(module->md5, md5hex.c_str());
            snprintf(module->player,MAX_PLAYER_SIZE, "%s",pl.data());
            snprintf(module->format,MAX_FORMAT_SIZE, "%s",info.format.c_str());
            module->channels = info.channels;

            module->size = buf.size();

        }
        module->subsongs[i].index = subsong;
        module->subsongs[i].length = songend.length;

        snprintf(module->subsongs[i].status,MAX_STATUS_SIZE, "%s", reason.c_str());

    }

    int player_songend(const vector<player::Player> &players, vector<char> &buf, const char *path,
                       const string &md5hex, module_t *module) {

        for (const auto &player: players) {

            const auto &info = player::parse(path, buf.data(), buf.size(), player);

            if (!info) continue;
            const int minsubsong = info->minsubsong;
            const int maxsubsong = info->maxsubsong;
            int i = 0;
            for (int subsong = minsubsong; subsong <= maxsubsong; subsong++) {

                auto songend = songend::precalc::precalc_song_end(info.value(), buf.data(), buf.size(), subsong,
                                                                  md5hex);

                if (songend.status == common::SongEnd::ERROR && !songend::precalc::allow_songend_error(info->format)) {

                    songend.length = 0;
                    module->subsongs[i].length = 0;
                }
                print(songend, info.value(), subsong, buf, md5hex, module, i);
                i++;
            }
            module->exit_value = EXIT_SUCCESS;
            return EXIT_SUCCESS;
        }
        snprintf(module->error_msg,MAX_ERROR_MSG_SIZE, "Could not parse %s md5 %s\n", path, md5hex.c_str());
        module->exit_value = EXIT_FAILURE;

        return EXIT_FAILURE;

    }


    int precalc(char *path = NULL, module_t *module = NULL) {

        if (path == NULL) {
            snprintf(module->error_msg,MAX_ERROR_MSG_SIZE, "File not given\n");
            module->exit_value = EXIT_FAILURE;
            return EXIT_FAILURE;
        }

        FILE *f = fopen(path, "rb");
        if (!f) {
            snprintf(module->error_msg,MAX_ERROR_MSG_SIZE, "File not found: %s\n", path);
            module->exit_value = EXIT_FAILURE;
            return EXIT_FAILURE;
        }
        int fd = fileno(f);

        struct stat st;
        if (fstat(fd, &st)) {
            close(fd);
            snprintf(module->error_msg,MAX_ERROR_MSG_SIZE, "Failed to read file size for %s\n", path);
            module->exit_value = EXIT_FAILURE;
            return EXIT_FAILURE;
        }

        uint8_t buf[4096];
        vector<char> buffer;
        buffer.reserve(st.st_size);

        ssize_t count;
        MD5 md5;
        while ((count = read(fd, buf, sizeof buf)) > 0) {
            md5.update(buf, count);
            buffer.insert(buffer.end(), buf, buf + count);
        }
        close(fd);
        md5.finalize();
        string md5hex = md5.hexdigest();

        if (songdb::blacklist::is_blacklisted_songdb_key(md5hex)) {
            snprintf(module->error_msg,MAX_ERROR_MSG_SIZE, "Blacklisted songdb md5 for %s\n", path);
            module->exit_value = EXIT_FAILURE;
            return EXIT_FAILURE;
        }

        if (songdb::blacklist::is_blacklisted_md5(md5hex)) {
            snprintf(module->error_msg,MAX_ERROR_MSG_SIZE, "Blacklisted md5 for %s\n", path);
            fprintf(stdout, "%s\t%d\t%d\t%s\t\t\t\t%zu\n", md5hex.c_str(), 0, 0, "error", buffer.size());
            module->exit_value = EXIT_FAILURE;
            return EXIT_FAILURE;
        }

#ifdef __MINGW32__
        _setmode(_fileno(stdout), 0x8000);
#endif

        const player::support::PlayerScope p;
        vector<player::Player> players;
        if (getenv("PLAYER")) {
            player::Player player = player::player(getenv("PLAYER"));
            if (player == player::Player::NONE) {
                snprintf(module->error_msg,MAX_ERROR_MSG_SIZE, "Unknown player %s\n", getenv("PLAYER"));
                module->exit_value = EXIT_FAILURE;
                return EXIT_FAILURE;
            }
            players.push_back(player::player(getenv("PLAYER")));
        } else {
            players = player::check(path, buffer.data(), buffer.size());
        }
        if (players.empty()) {
            snprintf(module->error_msg,MAX_ERROR_MSG_SIZE, "Could not recognize %s md5 %s\n", path, md5hex.c_str());
            module->exit_value = EXIT_FAILURE;
            return EXIT_FAILURE;
        }

        int res = player_songend(players, buffer, path, md5hex, module);
        module->exit_value = res;
        return res;

    }
}

extern "C"
{
extern void cffi_precalc(char *path = NULL, songtools::module_t *module = NULL) {
    songtools::precalc(path, module);
}
}