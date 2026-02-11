#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>
#include <tchar.h>

// 导出符号（确保 DLL 能被 Python 调用）
#ifdef BUILD_DLL
#define EXPORT __declspec(dllexport)
#else
#define EXPORT __declspec(dllimport)
#endif

// 支持的文件后缀
static const char *SUPPORTED_EXTS[] = {".db", ".sqlite", ".txt", ".rdb", ".aof", NULL};

/**
 * 检查文件后缀是否支持
 */
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

/**
 * 递归扫描目录（Windows 原生 API）
 */
static void scan_dir(const WCHAR *root_dir, char ***file_paths, int *file_count, int *capacity) {
    WCHAR search_path[MAX_PATH];
    WIN32_FIND_DATAW find_data;
    HANDLE hFind;

    // 拼接搜索路径：root_dir\*
    swprintf_s(search_path, MAX_PATH, L"%s\\*", root_dir);

    // 查找第一个文件/目录
    hFind = FindFirstFileW(search_path, &find_data);
    if (hFind == INVALID_HANDLE_VALUE) {
        return;
    }

    do {
        // 跳过 . 和 ..
        if (wcscmp(find_data.cFileName, L".") == 0 || wcscmp(find_data.cFileName, L"..") == 0) {
            continue;
        }

        // 拼接完整路径
        WCHAR full_path[MAX_PATH];
        swprintf_s(full_path, MAX_PATH, L"%s\\%s", root_dir, find_data.cFileName);

        // 判断是否是目录
        if (find_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
            // 递归扫描子目录
            scan_dir(full_path, file_paths, file_count, capacity);
        } else {
            // 转换宽字符到多字节（适配 Python 调用）
            char filename[MAX_PATH];
            WideCharToMultiByte(CP_UTF8, 0, find_data.cFileName, -1, filename, MAX_PATH, NULL, NULL);
            if (is_supported_file(filename)) {
                // 转换完整路径到多字节
                char path[MAX_PATH];
                WideCharToMultiByte(CP_UTF8, 0, full_path, -1, path, MAX_PATH, NULL, NULL);

                // 扩容检查
                if (*file_count >= *capacity) {
                    *capacity += 1024;
                    char **new_paths = (char **)realloc(*file_paths, *capacity * sizeof(char *));
                    if (new_paths == NULL) return;
                    *file_paths = new_paths;
                }

                // 保存路径
                (*file_paths)[*file_count] = (char *)malloc(strlen(path) + 1);
                strcpy((*file_paths)[*file_count], path);
                (*file_count)++;
            }
        }
    } while (FindNextFileW(hFind, &find_data));

    FindClose(hFind);
}

/**
 * 对外暴露的扫描函数（适配原接口）
 */
EXPORT void scan_files(const char *root_dir, char ***file_paths, int *file_count) {
    if (root_dir == NULL || file_paths == NULL || file_count == NULL) {
        *file_count = 0;
        return;
    }

    // 初始化
    int capacity = 1024;
    *file_count = 0;
    *file_paths = (char **)malloc(capacity * sizeof(char *));
    if (*file_paths == NULL) {
        *file_count = 0;
        return;
    }

    // 转换多字节到宽字符
    WCHAR w_root_dir[MAX_PATH];
    MultiByteToWideChar(CP_UTF8, 0, root_dir, -1, w_root_dir, MAX_PATH);

    // 开始扫描
    scan_dir(w_root_dir, file_paths, file_count, &capacity);
}

/**
 * 提取文件内容（适配原接口）
 */
EXPORT char *extract_content(const char *file_path, int *content_len) {
    if (file_path == NULL || content_len == NULL) {
        *content_len = 0;
        return NULL;
    }

    HANDLE hFile = CreateFileA(
        file_path,
        GENERIC_READ,
        FILE_SHARE_READ,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (hFile == INVALID_HANDLE_VALUE) {
        *content_len = 0;
        return NULL;
    }

    // 获取文件大小
    DWORD file_size = GetFileSize(hFile, NULL);
    *content_len = (int)file_size;

    // 分配内存
    char *content = (char *)malloc(file_size + 1);
    if (content == NULL) {
        CloseHandle(hFile);
        *content_len = 0;
        return NULL;
    }

    // 读取文件内容
    DWORD bytes_read;
    ReadFile(hFile, content, file_size, &bytes_read, NULL);
    content[file_size] = '\0';

    CloseHandle(hFile);
    return content;
}

/**
 * 释放内存（适配原接口）
 */
EXPORT void free_files(char **file_paths, int file_count) {
    if (file_paths == NULL || file_count <= 0) return;
    for (int i = 0; i < file_count; i++) {
        free(file_paths[i]);
    }
    free(file_paths);
}