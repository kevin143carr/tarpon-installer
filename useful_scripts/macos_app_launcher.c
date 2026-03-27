#include <errno.h>
#include <libgen.h>
#include <limits.h>
#include <mach-o/dyld.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#ifndef TARGET_RELATIVE_PATH
#define TARGET_RELATIVE_PATH "tarpon_installer_real"
#endif

int main(int argc, char *argv[]) {
    uint32_t executable_path_size = 0;
    if (_NSGetExecutablePath(NULL, &executable_path_size) != -1) {
        fprintf(stderr, "Could not determine executable path size.\n");
        return 1;
    }

    char *executable_path = (char *)malloc(executable_path_size);
    if (executable_path == NULL) {
        perror("malloc");
        return 1;
    }

    if (_NSGetExecutablePath(executable_path, &executable_path_size) != 0) {
        fprintf(stderr, "Could not determine executable path.\n");
        free(executable_path);
        return 1;
    }

    char resolved_path[PATH_MAX];
    if (realpath(executable_path, resolved_path) == NULL) {
        perror("realpath");
        free(executable_path);
        return 1;
    }
    free(executable_path);

    char dir_buffer[PATH_MAX];
    strncpy(dir_buffer, resolved_path, sizeof(dir_buffer) - 1);
    dir_buffer[sizeof(dir_buffer) - 1] = '\0';

    char *dir_path = dirname(dir_buffer);
    char target_path[PATH_MAX];
    if (snprintf(target_path, sizeof(target_path), "%s/%s", dir_path, TARGET_RELATIVE_PATH) >= (int)sizeof(target_path)) {
        fprintf(stderr, "Resolved launcher target path is too long.\n");
        return 1;
    }

    argv[0] = target_path;
    execv(target_path, argv);

    fprintf(stderr, "Failed to launch '%s': %s\n", target_path, strerror(errno));
    return 1;
}
