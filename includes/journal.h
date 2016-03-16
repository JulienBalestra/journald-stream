#ifndef JOURNAL_H
# define JOURNAL_H

# define HEAP_JOURNAL_SIZE 15360
# define HEAP_CURSOR_SIZE 1024
# define SINCE_DB_PATH "sincedb"
# define PIPE_ERROR_MSG "Could not open pipe for output\n"
# define CURSOR_ERROR_MSG "Not a predefined cursor\n"
# define JOURNALCTL "/bin/journalctl -o json --show-cursor"

/*
 * strings.c
 */
char *add_after_cursor(char *cursor);

int starts_with(const char *pre, const char *str);

void init_string(char *str, size_t size);

char *add_directory(char *cmd);


/*
 * cursor.c
 */
int refresh_cursor(char *cursor);

int is_cursor(char *cursor);

char *get_cursor_from_sincedb(int sincedb_fd, char *buf);

#endif