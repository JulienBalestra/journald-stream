#include <stddef.h>
#include <string.h>
#include <stdlib.h>

#include "journal.h"
#include "../includes/journal.h"

char		*strjoin(char const *s1, char const *s2)
{
	char	*str;
	size_t	i;
	size_t	len_s1 = strlen(s1);
	size_t	len_s2 = strlen(s2);

	if (s1 && s2 &&
			(str = (char *)malloc(sizeof(char) * (len_s1 + len_s2 + 1))))
	{
		i = 0;
		while (i < len_s1)
		{
			str[i] = s1[i];
			i++;
		}
		i = 0;
		while (i < len_s2)
		{
			str[i + len_s1] = s2[i];
			i++;
		}
		str[i + len_s1] = '\0';
	}
	return (str);
}

int starts_with(const char *pre, const char *str)
{
	size_t lenpre = strlen(pre),
			lenstr = strlen(str);

	return lenstr < lenpre ? 0 : strncmp(pre, str, lenpre) == 0;
}

char *get_directory_arg(int ac, char **av)
{
	int i = 1;

	while (ac > i)
	{
		if (starts_with("--directory=", av[i]) && strlen(av[i]) > 13)
			return (&av[i][12]);
		i++;
	}
	return (NULL);
}

char *add_directory(char *cmd, int ac, char **av)
{
	char *tmp = NULL;
	char *dir = NULL;
	char *dir_args = NULL;

	dir = getenv("JOURNAL_DIRECTORY");
	dir_args = get_directory_arg(ac, av);

	if (dir_args)
		dir = dir_args;
	else if (! dir)
		dir = DEFAULT_DIRECTORY;

	if (dir && cmd)
	{
		tmp = cmd;
		cmd = strjoin(cmd, " ");
		if (! cmd)
			return (tmp);
		free(tmp);

		tmp = cmd;
		cmd = strjoin(cmd, "--directory=");
		if (! cmd)
			return (tmp);
		free(tmp);

		tmp = cmd;
		cmd = strjoin(cmd, dir);
		if (! cmd)
			return (tmp);
		free(tmp);
	}
	return (cmd);
}

char *add_after_cursor(char *cursor)
{
	char *tmp = NULL;
	char *cmd = NULL;

	cmd = strjoin(JOURNALCTL, " ");
	if (! cmd)
		return (NULL);
	else if (! cursor)
		return (cmd);

	tmp = cmd;
	cmd = strjoin(cmd, "--after-cursor=");
	if (! cmd)
		return (tmp);
	free(tmp);

	tmp = cmd;
	cmd = strjoin(cmd, "\"");
	if (! cmd)
		return (tmp);
	free(tmp);

	tmp = cmd;
	cmd = strjoin(cmd, cursor);
	if (! cmd)
		return (tmp);
	free(tmp);

	tmp = cmd;
	cmd = strjoin(cmd, "\"");
	if (! cmd)
		return (tmp);
	free(tmp);
	return (cmd);
}

void init_string(char *str, size_t size)
{
	size_t i = 0;

	while(i < size)
	{
		str[i] = '\0';
		i++;
	}
}