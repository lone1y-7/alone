#ifndef DIRENT_H
#define DIRENT_H

#ifdef _WIN32

#include <windows.h>
#include <stdlib.h>
#include <string.h>

#define MAX_PATH 4096  // 新增：对齐 file_scanner.c 的 MAX_PATH_LENGTH
#define DT_UNKNOWN 0
#define DT_REG     8
#define DT_DIR     4

// 直接定义 dirent 结构体（而非 FS_DIRENT_TYPE），让代码无需修改
typedef struct dirent {
    char d_name[MAX_PATH];
    unsigned char d_type;
} dirent;

// 直接定义 DIR 结构体（而非 FS_DIR_TYPE）
typedef struct DIR {
    HANDLE hFind;
    WIN32_FIND_DATAA find_data;
    dirent current;  // 直接用 dirent 而非 FS_DIRENT_TYPE
    int first;
    char path[MAX_PATH];
} DIR;

/* open directory */
static DIR* opendir(const char* dirname) {  // 直接用 opendir 而非 fs_opendir
    DIR* dir = (DIR*)calloc(1, sizeof(DIR));
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
static struct dirent* readdir(DIR* dir) {  // 直接用 readdir 而非 fs_readdir
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
static int closedir(DIR* dir) {  // 直接用 closedir 而非 fs_closedir
    if (!dir) return -1;
    FindClose(dir->hFind);
    free(dir);
    return 0;
}

#else
#include <dirent.h>
#endif

#endif