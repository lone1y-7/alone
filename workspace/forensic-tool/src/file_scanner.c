#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <sys/stat.h>
#include "dirent.h"
#include <windows.h>
#else
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

#ifdef BUILD_DLL
#define EXPORT __declspec(dllexport)
#else
#define EXPORT __declspec(dllimport)
#endif

#define MAX_FILE_SIZE (100 * 1024 * 1024)

static const char *SUPPORTED_EXTS[] = {
    ".db", ".sqlite", ".txt", ".rdb", ".aof",
    ".xml", ".json", ".log", ".plist", NULL
};

#ifdef _WIN32

EXPORT FS_DIR_TYPE *fs_opendir(const char *dirname) {
    FS_DIR_TYPE *dir = (FS_DIR_TYPE *)malloc(sizeof(FS_DIR_TYPE));
    if (!dir) return NULL;

    char search_path[MAX_PATH];
    snprintf(search_path, sizeof(search_path), "%s\\*.*", dirname);

    dir->handle = FindFirstFileA(search_path, &dir->find_data);
    if (dir->handle == INVALID_HANDLE_VALUE) {
        free(dir);
        return NULL;
    }

    dir->eof = 0;
    return dir;
}

EXPORT FS_DIRENT_TYPE *fs_readdir(FS_DIR_TYPE *dirp) {
    if (!dirp || dirp->eof) {
        return NULL;
    }

    while (strcmp(dirp->find_data.cFileName, ".") == 0 ||
           strcmp(dirp->find_data.cFileName, "..") == 0) {
        if (!FindNextFileA(dirp->handle, &dirp->find_data)) {
            dirp->eof = 1;
            return NULL;
        }
    }

    strncpy(dirp->entry.d_name, dirp->find_data.cFileName, MAX_PATH);
    dirp->entry.d_name[MAX_PATH] = '\0';
    dirp->entry.d_ino = 0;

    if (dirp->find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
        dirp->entry.d_type = DT_DIR;
    } else if (dirp->find_data.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT) {
        dirp->entry.d_type = DT_LNK;
    } else {
        dirp->entry.d_type = DT_REG;
    }

    if (!FindNextFileA(dirp->handle, &dirp->find_data)) {
        dirp->eof = 1;
    }

    return &dirp->entry;
}

EXPORT int fs_closedir(FS_DIR_TYPE *dirp) {
    if (!dirp) return -1;

    if (dirp->handle != INVALID_HANDLE_VALUE) {
        FindClose(dirp->handle);
    }

    free(dirp);
    return 0;
}

#endif

static int is_supported_file(const char *filename) {
    if (filename == NULL) return 0;

    const char *ext = strrchr(filename, '.');
    if (ext == NULL) return 0;

    for (int i = 0; SUPPORTED_EXTS[i] != NULL; i++) {
        if (strcmp(ext, SUPPORTED_EXTS[i]) == 0) {
            return 1;
        }
    }
    return 0;
}

static void scan_dir(const char *root_dir, char ***file_paths, int *file_count, int *capacity) {
#ifdef _WIN32
    FS_DIR_TYPE *dir = fs_opendir(root_dir);
#else
    FS_DIR_TYPE *dir = opendir(root_dir);
#endif

    if (dir == NULL) {
        return;
    }

    FS_DIRENT_TYPE *entry;
    char full_path[4096];

#ifdef _WIN32
    const char *sep = "\\";
#else
    const char *sep = "/";
#endif

#ifdef _WIN32
    while ((entry = fs_readdir(dir)) != NULL) {
#else
    while ((entry = readdir(dir)) != NULL) {
#endif
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        snprintf(full_path, sizeof(full_path), "%s%s%s", root_dir, sep, entry->d_name);

        if (entry->d_type == DT_DIR) {
            scan_dir(full_path, file_paths, file_count, capacity);
        } else if (entry->d_type == DT_REG) {
            if (is_supported_file(entry->d_name)) {
                if (*file_count >= *capacity) {
                    *capacity += 1024;
                    char **new_paths = (char **)realloc(*file_paths, *capacity * sizeof(char *));
                    if (new_paths == NULL) return;
                    *file_paths = new_paths;
                }

                (*file_paths)[*file_count] = (char *)malloc(strlen(full_path) + 1);
                if ((*file_paths)[*file_count] != NULL) {
                    strcpy((*file_paths)[*file_count], full_path);
                    (*file_count)++;
                }
            }
        }
    }

#ifdef _WIN32
    fs_closedir(dir);
#else
    closedir(dir);
#endif
}

EXPORT void scan_files(const char *root_dir, char ***file_paths, int *file_count) {
    if (root_dir == NULL || file_paths == NULL || file_count == NULL) {
        *file_count = 0;
        return;
    }

    int capacity = 1024;
    *file_count = 0;
    *file_paths = (char **)malloc(capacity * sizeof(char *));
    if (*file_paths == NULL) {
        *file_count = 0;
        return;
    }

    scan_dir(root_dir, file_paths, file_count, &capacity);
}

EXPORT char *extract_content(const char *file_path, int *content_len) {
    if (file_path == NULL || content_len == NULL) {
        *content_len = 0;
        return NULL;
    }

    FILE *fp = fopen(file_path, "rb");
    if (fp == NULL) {
        *content_len = 0;
        return NULL;
    }

    fseek(fp, 0, SEEK_END);
    long file_size = ftell(fp);
    fseek(fp, 0, SEEK_SET);

    if (file_size <= 0 || file_size > MAX_FILE_SIZE) {
        fclose(fp);
        *content_len = 0;
        return NULL;
    }

    *content_len = (int)file_size;

    char *content = (char *)calloc(file_size + 1, sizeof(char));
    if (content == NULL) {
        fclose(fp);
        *content_len = 0;
        return NULL;
    }

    size_t bytes_read = fread(content, 1, file_size, fp);
    content[bytes_read] = '\0';

    fclose(fp);
    return content;
}

EXPORT void free_files(char **file_paths, int file_count) {
    if (file_paths == NULL || file_count <= 0) return;

    for (int i = 0; i < file_count; i++) {
        if (file_paths[i] != NULL) {
            free(file_paths[i]);
        }
    }
    free(file_paths);
}
