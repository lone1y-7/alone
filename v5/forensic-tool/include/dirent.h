#ifndef DIRENT_H
#define DIRENT_H

#ifdef _WIN32

#include <windows.h>
#include <stdlib.h>
#include <string.h>

#define DT_UNKNOWN 0
#define DT_REG     8
#define DT_DIR     4

typedef struct {
    char d_name[MAX_PATH];
    unsigned char d_type;
} FS_DIRENT_TYPE;

typedef struct {
    HANDLE hFind;
    WIN32_FIND_DATAA find_data;
    FS_DIRENT_TYPE current;
    int first;
    char path[MAX_PATH];
} FS_DIR_TYPE;

/* open directory */
static FS_DIR_TYPE* fs_opendir(const char* dirname) {
    FS_DIR_TYPE* dir = (FS_DIR_TYPE*)calloc(1, sizeof(FS_DIR_TYPE));
    if (!dir) return NULL;

    strncpy(dir->path, dirname, MAX_PATH - 1);
    dir->path[MAX_PATH - 1] = '\0';

    char search_path[MAX_PATH];
    snprintf(search_path, MAX_PATH, "%s\\*", dir->path);

    dir->hFind = FindFirstFileA(search_path, &dir->find_data);
    if (dir->hFind == INVALID_HANDLE_VALUE) {
        free(dir);
        return NULL;
    }

    dir->first = 1;
    return dir;
}

/* read directory */
static FS_DIRENT_TYPE* fs_readdir(FS_DIR_TYPE* dir) {
    if (!dir) return NULL;

    while (1) {

        if (dir->first) {
            dir->first = 0;
        } else {
            if (!FindNextFileA(dir->hFind, &dir->find_data))
                return NULL;
        }

        if (strcmp(dir->find_data.cFileName, ".") == 0 ||
            strcmp(dir->find_data.cFileName, "..") == 0)
            continue;

        strncpy(dir->current.d_name,
                dir->find_data.cFileName,
                MAX_PATH - 1);
        dir->current.d_name[MAX_PATH - 1] = '\0';

        if (dir->find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)
            dir->current.d_type = DT_DIR;
        else
            dir->current.d_type = DT_REG;

        return &dir->current;
    }
}

/* close directory */
static int fs_closedir(FS_DIR_TYPE* dir) {
    if (!dir) return -1;
    FindClose(dir->hFind);
    free(dir);
    return 0;
}

#else
#include <dirent.h>
#define FS_DIR_TYPE DIR
#define FS_DIRENT_TYPE struct dirent
#define fs_opendir opendir
#define fs_readdir readdir
#define fs_closedir closedir
#endif

#endif
