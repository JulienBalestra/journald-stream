#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>

#include "journal.h"
#include "../includes/journal.h"

char *find_cursor(void)
{
	int fd;
	char *buf;
	char *cursor;
	char *cmd;

	if ((fd = open(SINCE_DB_PATH, O_RDONLY)) &&
		((buf = (char *) malloc(sizeof(char) * HEAP_CURSOR_SIZE))))
	{
		if ((cursor = get_cursor_from_sincedb(fd, buf)))
		{
			if (is_cursor(cursor) == 122)
			{
				cmd = full_command(cursor);
			}
			else
				cmd = strdup(JOURNALCTL);
		}
		else
			cmd = strdup(JOURNALCTL);
		free(buf);
	}
	else
		cmd = strdup(JOURNALCTL);
	close(fd);
	return (cmd);
}

int main(void)
{
	FILE *pipe;
	char *buf;
	char *command;

	command = find_cursor();
	command = add_directory(command);
	//write(2, command, strlen(command));
	if ((pipe = popen(command, "r")))
	{
		if ((buf = (char *)malloc(sizeof(char) * HEAP_JOURNAL_SIZE)))
		{
			init_string(buf, HEAP_JOURNAL_SIZE);
		}
		else
			return (3);
		while (fgets(buf, HEAP_JOURNAL_SIZE, pipe))
		{
			if (starts_with("-- cursor: ", buf))
			{
				if (refresh_cursor(buf) == 1)
					break;
				else
				{
					write(2, CURSOR_ERROR_MSG, strlen(CURSOR_ERROR_MSG));
					free(command);
					pclose(pipe);
					return (1);
				}
			}
			write(1, buf, strlen(buf));
		}
	}
	else
	{
		write(2, PIPE_ERROR_MSG, strlen(PIPE_ERROR_MSG));
		free(command);
		pclose(pipe);
		return (2);
	}
	free(buf);
	free(command);
	pclose(pipe);
	return (0);
}