#ifndef DIRENT_H
#define DIRENT_H

#ifdef _WIN32
#include <windows.h>

#define DT_UNKNOWN 0
#define DT_FIFO 1
#define DT_CHR 2
#define DT_DIR 4
#define DT_BLK 6
#define DT_REG 8
#define DT_LNK 10
#define DT_SOCK 12
#define DT_WHT 14

typedef struct {
    long d_ino;
    char d_name[MAX_PATH + 1];
    unsigned char d_type;
} FS_DIRENT_TYPE;

typedef struct {
    HANDLE handle;
    WIN32_FIND_DATAA find_data;
    FS_DIRENT_TYPE entry;
    int eof;
} FS_DIR_TYPE;

#else

#include <dirent.h>
#define FS_DIRENT_TYPE struct dirent
#define FS_DIR_TYPE DIR

#endif

#endif
