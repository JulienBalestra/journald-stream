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

	if ((str = (char *)malloc(sizeof(char) * (len_s1 + len_s2))))
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

char *full_command(char *cursor)
{
	char *tmp;
	char *cmd;

	cmd = strjoin(JOURNALCTL, " ");

	tmp = cmd;
	cmd = strjoin(cmd, "--after-cursor=");
	free(tmp);

	tmp = cmd;
	cmd = strjoin(cmd, "\"");
	free(tmp);

	tmp = cmd;
	cmd = strjoin(cmd, cursor);
	free(tmp);

	tmp = cmd;
	cmd = strjoin(cmd, "\"");
	free(tmp);
	return (cmd);
}