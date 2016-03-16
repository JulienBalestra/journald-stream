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
	char *buf = NULL;
	char *cursor = NULL;
	char *cmd = NULL;

	if ((fd = open(SINCE_DB_PATH, O_RDONLY)) &&
		((buf = (char *) malloc(sizeof(char) * HEAP_CURSOR_SIZE))))
	{
		init_string(buf, HEAP_CURSOR_SIZE);
		if ((cursor = get_cursor_from_sincedb(fd, buf)))
		{
			if (is_cursor(cursor))
			{
				cmd = add_after_cursor(cursor);
			}
			else
				cmd = strdup(JOURNALCTL);
		}
		else
			cmd = strdup(JOURNALCTL);
		free(buf);
		close(fd);
	}
	else
		cmd = strdup(JOURNALCTL);
	return (cmd);
}

void display_command(char *command)
{
	char *debug = getenv("JOURNAL_DEBUG");

	if (debug && strcmp("true", debug) == 0)
	{
		write(2, command, strlen(command));
		write(2, "\n", 1);
	}
}

void process_pipe(char *command)
{
	FILE *pipe = NULL;
	char *buf = NULL;

	if ((pipe = popen(command, "r")))
	{
		if ((buf = (char *)malloc(sizeof(char) * HEAP_JOURNAL_SIZE)))
		{
			init_string(buf, HEAP_JOURNAL_SIZE);
		}
		else
			return ;
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
					return ;
				}
			}
			write(1, buf, strlen(buf));
		}
		pclose(pipe);
		free(buf);
	}
	else
	{
		write(2, PIPE_ERROR_MSG, strlen(PIPE_ERROR_MSG));
	}
}

int main(int ac, char **av)
{

	char *command = NULL;

	if ((command = find_cursor()))
	{
		if ((command = add_directory(command, ac, av)))
		{
			display_command(command);
			process_pipe(command);
		}
		free(command);
	}

	return (0);
}