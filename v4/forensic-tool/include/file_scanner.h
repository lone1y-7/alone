#ifndef FILE_SCANNER_H
#define FILE_SCANNER_H

#ifdef __cplusplus
extern "C" {
#endif

void scan_files(const char *root_dir, char ***file_paths, int *file_count);
char *extract_content(const char *file_path, int *content_len);
void free_files(char **file_paths, int file_count);

#ifdef __cplusplus
}
#endif

#endif
