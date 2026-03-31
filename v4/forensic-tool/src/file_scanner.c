#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <direct.h>
#include "../include/dirent.h"
#else
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <sys/stat.h>
#include <errno.h>
#endif

#define MAX_FILE_SIZE (100 * 1024 * 1024)
#define SUPPORTED_EXT_COUNT 9
#define MAX_PATH_LENGTH 4096

#ifdef __cplusplus
#define EXPORT extern "C" __declspec(dllexport)
#else
#define EXPORT __declspec(dllexport)
#endif

static const char* supported_extensions[] = {
    ".db", ".sqlite", ".txt", ".log",
    ".json", ".xml", ".plist", ".rdb", ".aof"
};

static int is_supported_file(const char* filename) {
    if (!filename) return 0;

    const char* ext = strrchr(filename, '.');
    if (!ext) return 0;

    for (int i = 0; i < SUPPORTED_EXT_COUNT; i++) {
        if (strcmp(ext, supported_extensions[i]) == 0)
            return 1;
    }
    return 0;
}

static long get_file_size(const char* filepath) {
#ifdef _WIN32
    WIN32_FILE_ATTRIBUTE_DATA file_attr;
    if (!GetFileAttributesExA(filepath, GetFileExInfoStandard, &file_attr))
        return -1;

    return (long)(((unsigned long long)file_attr.nFileSizeHigh << 32)
        | file_attr.nFileSizeLow);
#else
    struct stat st;
    if (stat(filepath, &st) != 0)
        return -1;
    return st.st_size;
#endif
}

static int scan_directory(const char* root_dir,
                          char*** file_paths,
                          int* file_count,
                          int* capacity) {

    if (!root_dir || !file_paths || !file_count || !capacity)
        return -1;

#ifdef _WIN32
    FS_DIR_TYPE* dir = fs_opendir(root_dir);
#else
    DIR* dir = opendir(root_dir);
#endif

    if (!dir) return -1;

#ifdef _WIN32
    FS_DIRENT_TYPE* entry;
    while ((entry = fs_readdir(dir)) != NULL) {
#else
    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
#endif

        if (!strcmp(entry->d_name, ".") ||
            !strcmp(entry->d_name, ".."))
            continue;

        char full_path[MAX_PATH_LENGTH];

#ifdef _WIN32
        snprintf(full_path, MAX_PATH_LENGTH, "%s\\%s",
                 root_dir, entry->d_name);
#else
        snprintf(full_path, MAX_PATH_LENGTH, "%s/%s",
                 root_dir, entry->d_name);
#endif

#ifdef _WIN32
        DWORD attr = GetFileAttributesA(full_path);
        if (attr != INVALID_FILE_ATTRIBUTES &&
            (attr & FILE_ATTRIBUTE_DIRECTORY)) {

            scan_directory(full_path,
                           file_paths,
                           file_count,
                           capacity);
        } else {
#else
        struct stat st;
        if (stat(full_path, &st) == 0 &&
            S_ISDIR(st.st_mode)) {

            scan_directory(full_path,
                           file_paths,
                           file_count,
                           capacity);
        } else {
#endif

            if (is_supported_file(full_path)) {

                long file_size = get_file_size(full_path);

                if (file_size > 0 &&
                    file_size <= MAX_FILE_SIZE) {

                    if (*file_count >= *capacity) {

                        *capacity *= 2;

                        char** temp =
                            (char**)realloc(*file_paths,
                                (*capacity) * sizeof(char*));

                        if (!temp) return -1;

                        *file_paths = temp;
                    }

                    (*file_paths)[*file_count] =
                        (char*)calloc(strlen(full_path) + 1,
                                      sizeof(char));

                    if ((*file_paths)[*file_count]) {
                        strcpy((*file_paths)[*file_count],
                               full_path);
                        (*file_count)++;
                    }
                }
            }
        }
    }

#ifdef _WIN32
    fs_closedir(dir);
#else
    closedir(dir);
#endif

    return 0;
}

EXPORT void scan_files(const char* root_dir,
                       char*** file_paths,
                       int* file_count) {

    if (!root_dir || !file_paths || !file_count) {

        if (file_count) *file_count = 0;
        if (file_paths) *file_paths = NULL;
        return;
    }

    int capacity = 100;

    *file_count = 0;

    *file_paths =
        (char**)calloc(capacity, sizeof(char*));

    if (!*file_paths) return;

    scan_directory(root_dir,
                   file_paths,
                   file_count,
                   &capacity);

    if (*file_count > 0) {

        char** temp =
            (char**)realloc(*file_paths,
                           (*file_count) * sizeof(char*));

        if (temp) *file_paths = temp;
    }
}

EXPORT char* extract_content(const char* file_path,
                             int* content_len) {

    if (!file_path || !content_len) {
        if (content_len) *content_len = 0;
        return NULL;
    }

    long file_size = get_file_size(file_path);

    if (file_size <= 0 ||
        file_size > MAX_FILE_SIZE) {

        *content_len = 0;
        return NULL;
    }

    FILE* fp = fopen(file_path, "rb");

    if (!fp) {
        *content_len = 0;
        return NULL;
    }

    char* content =
        (char*)calloc(file_size + 1,
                      sizeof(char));

    if (!content) {
        fclose(fp);
        *content_len = 0;
        return NULL;
    }

    *content_len =
        (int)fread(content, 1,
                   file_size, fp);

    fclose(fp);

    return content;
}

EXPORT void free_files(char** file_paths,
                       int file_count) {

    if (!file_paths || file_count <= 0)
        return;

    for (int i = 0; i < file_count; i++)
        free(file_paths[i]);

    free(file_paths);
}
