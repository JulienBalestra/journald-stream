#include <string.h>
#include <ctype.h>
#include <fcntl.h>
#include <unistd.h>

#include "journal.h"
#include "../includes/journal.h"

/*
 * "s=4dfc74db603b445d8908b82b62e5c874;i=338;b=c7588c627f7e44908e00712244a51313;m=1462190c2;t=52e065c40176b;x=5cf3c78222fd2868"
 */
int 	is_cursor(char *cursor)
{
	int i = 0;

	if (! cursor || strlen(cursor) != 122)
		return (i);
	if (starts_with("s=", &cursor[i]) == 0)
		return (i);
	i++;
	while (cursor[i] && cursor[i] != ';')
		i++;
	if (starts_with(";i=", &cursor[i]) == 0)
		return (i);
	i = i + 3;
	while (isxdigit(cursor[i]) && cursor[i] != ';')
		i++;
	if (starts_with(";b=", &cursor[i]) == 0)
		return (i);
	i = i + 3;
	while (isxdigit(cursor[i]) && cursor[i] != ';')
		i++;
	if (starts_with(";m=", &cursor[i]) == 0)
		return (i);
	i = i + 3;
	while (isxdigit(cursor[i]) && cursor[i] != ';')
		i++;
	if (starts_with(";t=", &cursor[i]) == 0)
		return (i);
	i = i + 3;
	while (isxdigit(cursor[i]) && cursor[i] != ';')
		i++;
	if (starts_with(";x=", &cursor[i]) == 0)
		return (i);
	i = i + 3;
	while (isxdigit(cursor[i]))
		i++;
	return (i);
}

int refresh_cursor(char *cursor)
{
	int fd;
	char *value;

	value = &cursor[11];
	if (value && (fd = open(SINCE_DB_PATH, O_WRONLY | O_TRUNC | O_CREAT,
							S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH)))
	{
		if (value[strlen(value) - 1] == '\n')
			value[strlen(value) - 1] = '\0';
		if (is_cursor(value) == 122)
		{
			write(fd, value, strlen(value));
			return (1);
		}
	}
	return (0);
}

char *get_cursor_from_sincedb(int sincedb_fd, char *buf)
{
	ssize_t ret;

	if ((ret = read(sincedb_fd, buf, HEAP_CURSOR_SIZE)))
	{
		buf[ret] = '\0';
	}
	return (ret > 1 ? buf : NULL);
}