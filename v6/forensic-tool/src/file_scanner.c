#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS
#include <windows.h>
#include <wchar.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <direct.h>
// 若原有 dirent.h 兼容层无需保留，可注释
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
#define MAX_PATH_LENGTH 4096  // 扩展路径长度，适配宽字符转换

#ifdef __cplusplus
#define EXPORT extern "C" __declspec(dllexport)
#else
#define EXPORT __declspec(dllexport)
#endif

static const wchar_t* supported_extensions_w[] = {
    L".db", L".sqlite", L".txt", L".log",
    L".json", L".xml", L".plist", L".rdb", L".aof"
};
static const char* supported_extensions[] = {
    ".db", ".sqlite", ".txt", ".log",
    ".json", ".xml", ".plist", ".rdb", ".aof"
};

// 宽字符版本：判断是否为支持的文件后缀（Windows 专用）
static int is_supported_file_w(const wchar_t* filename) {
    if (!filename) return 0;

    const wchar_t* ext = wcsrchr(filename, L'.');
    if (!ext) return 0;

    for (int i = 0; i < SUPPORTED_EXT_COUNT; i++) {
        if (wcscmp(ext, supported_extensions_w[i]) == 0)
            return 1;
    }
    return 0;
}

// 多字节版本：Linux/macOS 专用
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

// 宽字符版本：获取文件大小（Windows 专用）
static long get_file_size_w(const wchar_t* filepath) {
    WIN32_FILE_ATTRIBUTE_DATA file_attr;
    if (!GetFileAttributesExW(filepath, GetFileExInfoStandard, &file_attr))
        return -1;

    return (long)(((unsigned long long)file_attr.nFileSizeHigh << 32) | file_attr.nFileSizeLow);
}

// 多字节版本：获取文件大小（Linux/macOS 专用）
static long get_file_size(const char* filepath) {
    struct stat st;
    if (stat(filepath, &st) != 0)
        return -1;
    return st.st_size;
}

// Windows 专用：递归扫描目录（宽字符版）
static int scan_directory_w(const wchar_t* root_dir,
                           wchar_t*** file_paths,
                           int* file_count,
                           int* capacity) {
    if (!root_dir || !file_paths || !file_count || !capacity)
        return -1;

    wchar_t search_path[MAX_PATH_LENGTH];
    wcscpy_s(search_path, MAX_PATH_LENGTH, root_dir);
    wcscat_s(search_path, MAX_PATH_LENGTH, L"\\*");

    WIN32_FIND_DATAW find_data;
    HANDLE hFind = FindFirstFileW(search_path, &find_data);
    if (hFind == INVALID_HANDLE_VALUE) {
        return -1;
    }

    do {
        // 跳过 . 和 ..
        if (wcscmp(find_data.cFileName, L".") == 0 || wcscmp(find_data.cFileName, L"..") == 0)
            continue;

        // 拼接完整路径
        wchar_t full_path[MAX_PATH_LENGTH];
        wcscpy_s(full_path, MAX_PATH_LENGTH, root_dir);
        wcscat_s(full_path, MAX_PATH_LENGTH, L"\\");
        wcscat_s(full_path, MAX_PATH_LENGTH, find_data.cFileName);

        // 判断是否为目录：递归扫描
        if (find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
            scan_directory_w(full_path, file_paths, file_count, capacity);
        } else {
            // 是文件：判断后缀+大小
            if (is_supported_file_w(full_path)) {
                long file_size = get_file_size_w(full_path);
                if (file_size > 0 && file_size <= MAX_FILE_SIZE) {
                    // 动态扩容
                    if (*file_count >= *capacity) {
                        *capacity *= 2;
                        wchar_t** temp = (wchar_t**)realloc(*file_paths, (*capacity) * sizeof(wchar_t*));
                        if (!temp) {
                            FindClose(hFind);
                            return -1;
                        }
                        *file_paths = temp;
                    }
                    // 分配路径内存并拷贝
                    (*file_paths)[*file_count] = (wchar_t*)malloc(sizeof(wchar_t) * (wcslen(full_path) + 1));
                    if ((*file_paths)[*file_count]) {
                        wcscpy_s((*file_paths)[*file_count], wcslen(full_path) + 1, full_path);
                        (*file_count)++;
                    }
                }
            }
        }
    } while (FindNextFileW(hFind, &find_data));

    FindClose(hFind);
    return 0;
}

// Linux/macOS 专用：递归扫描目录（多字节版，保留原逻辑）
#ifndef _WIN32
static int scan_directory(const char* root_dir,
                          char*** file_paths,
                          int* file_count,
                          int* capacity) {
    if (!root_dir || !file_paths || !file_count || !capacity)
        return -1;

    DIR* dir = opendir(root_dir);
    if (!dir) return -1;

    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
        if (!strcmp(entry->d_name, ".") || !strcmp(entry->d_name, ".."))
            continue;

        char full_path[MAX_PATH_LENGTH];
        snprintf(full_path, MAX_PATH_LENGTH, "%s/%s", root_dir, entry->d_name);

        struct stat st;
        if (stat(full_path, &st) == 0 && S_ISDIR(st.st_mode)) {
            scan_directory(full_path, file_paths, file_count, capacity);
        } else {
            if (is_supported_file(full_path)) {
                long file_size = get_file_size(full_path);
                if (file_size > 0 && file_size <= MAX_FILE_SIZE) {
                    if (*file_count >= *capacity) {
                        *capacity *= 2;
                        char** temp = (char**)realloc(*file_paths, (*capacity) * sizeof(char*));
                        if (!temp) {
                            closedir(dir);
                            return -1;
                        }
                        *file_paths = temp;
                    }
                    (*file_paths)[*file_count] = (char*)malloc(sizeof(char) * (strlen(full_path) + 1));
                    if ((*file_paths)[*file_count]) {
                        strcpy((*file_paths)[*file_count], full_path);
                        (*file_count)++;
                    }
                }
            }
        }
    }

    closedir(dir);
    return 0;
}
#endif

// 对外暴露：扫描文件（统一接口，适配Python UTF-8路径）
EXPORT void scan_files(const char* root_dir_utf8, char*** file_paths, int* file_count) {
    if (!root_dir_utf8 || !file_paths || !file_count) {
        if (file_count) *file_count = 0;
        if (file_paths) *file_paths = NULL;
        return;
    }

    *file_count = 0;
    *file_paths = NULL;

#ifdef _WIN32
    // Windows 流程：UTF-8 -> 宽字符 -> 扫描 -> 宽字符 -> UTF-8
    // 1. UTF-8 转宽字符（wchar_t）
    int wlen = MultiByteToWideChar(CP_UTF8, 0, root_dir_utf8, -1, NULL, 0);
    wchar_t* root_dir_w = (wchar_t*)malloc(sizeof(wchar_t) * wlen);
    if (!root_dir_w) return;
    MultiByteToWideChar(CP_UTF8, 0, root_dir_utf8, -1, root_dir_w, wlen);

    // 2. 初始化宽字符数组，调用宽字符扫描函数
    int capacity_w = 100;
    wchar_t** w_file_paths = (wchar_t**)calloc(capacity_w, sizeof(wchar_t*));
    if (!w_file_paths) {
        free(root_dir_w);
        return;
    }
    int w_file_count = 0;
    scan_directory_w(root_dir_w, &w_file_paths, &w_file_count, &capacity_w);

    // 3. 宽字符路径转 UTF-8（供Python解析）
    if (w_file_count > 0) {
        *file_paths = (char**)malloc(sizeof(char*) * w_file_count);
        for (int i = 0; i < w_file_count; i++) {
            int clen = WideCharToMultiByte(CP_UTF8, 0, w_file_paths[i], -1, NULL, 0, NULL, NULL);
            (*file_paths)[i] = (char*)malloc(sizeof(char) * clen);
            WideCharToMultiByte(CP_UTF8, 0, w_file_paths[i], -1, (*file_paths)[i], clen, NULL, NULL);
            free(w_file_paths[i]); // 释放宽字符路径
        }
        // 缩容：释放冗余内存
        char** temp = (char**)realloc(*file_paths, w_file_count * sizeof(char*));
        if (temp) *file_paths = temp;
    }
    free(w_file_paths);
    free(root_dir_w);
    *file_count = w_file_count;

#else
    // Linux/macOS 流程：保留原逻辑
    int capacity = 100;
    *file_paths = (char**)calloc(capacity, sizeof(char*));
    if (!*file_paths) return;

    scan_directory(root_dir_utf8, file_paths, file_count, &capacity);

    if (*file_count > 0) {
        char** temp = (char**)realloc(*file_paths, (*file_count) * sizeof(char*));
        if (temp) *file_paths = temp;
    }
#endif
}

// 对外暴露：读取文件内容（适配中文路径）
EXPORT char* extract_content(const char* file_path_utf8, int* content_len) {
    if (!file_path_utf8 || !content_len) {
        if (content_len) *content_len = 0;
        return NULL;
    }

    *content_len = 0;
    char* content = NULL;
    long file_size = 0;

#ifdef _WIN32
    // Windows：UTF-8 转宽字符，读取文件
    int wlen = MultiByteToWideChar(CP_UTF8, 0, file_path_utf8, -1, NULL, 0);
    wchar_t* file_path_w = (wchar_t*)malloc(sizeof(wchar_t) * wlen);
    if (!file_path_w) return NULL;
    MultiByteToWideChar(CP_UTF8, 0, file_path_utf8, -1, file_path_w, wlen);

    file_size = get_file_size_w(file_path_w);
    if (file_size <= 0 || file_size > MAX_FILE_SIZE) {
        free(file_path_w);
        return NULL;
    }

    FILE* fp = NULL;
    _wfopen_s(&fp, file_path_w, L"rb"); // 宽字符版 fopen
    if (!fp) {
        free(file_path_w);
        return NULL;
    }

    content = (char*)calloc(file_size + 1, sizeof(char));
    if (content) {
        *content_len = (int)fread(content, 1, file_size, fp);
    }
    fclose(fp);
    free(file_path_w);

#else
    // Linux/macOS：保留原逻辑
    file_size = get_file_size(file_path_utf8);
    if (file_size <= 0 || file_size > MAX_FILE_SIZE) {
        return NULL;
    }

    FILE* fp = fopen(file_path_utf8, "rb");
    if (!fp) return NULL;

    content = (char*)calloc(file_size + 1, sizeof(char));
    if (content) {
        *content_len = (int)fread(content, 1, file_size, fp);
    }
    fclose(fp);
#endif

    return content;
}

// 对外暴露：释放文件路径内存
EXPORT void free_files(char** file_paths, int file_count) {
    if (!file_paths || file_count <= 0)
        return;

    for (int i = 0; i < file_count; i++) {
        if (file_paths[i]) {
            free(file_paths[i]);
            file_paths[i] = NULL; // 避免野指针
        }
    }
    free(file_paths);
}

// 对外暴露：释放文件内容内存（新增，建议配套使用）
EXPORT void free_content(char* content) {
    if (content) {
        free(content);
    }
}