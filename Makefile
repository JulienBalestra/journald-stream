NAME = libjd
CC = gcc
CFLAGS = -Wall -Werror -Wextra -static
INC_DIR = includes/
SRC_DIR = sources/
OBJ_DIR = .objects/
OBJS = $(addprefix $(OBJ_DIR), $(SRC:.c=.o))
TARGET = $(NAME).a
BIN = journald-stream


CL_CYAN = \033[0;36m
CL_GREED = \033[0;32m
CL_RED = \033[0;31m
CL_WHITE = \033[0m


SRC =               \
cursor.c \
strings.c


MAIN = $(SRC_DIR)main.c


.PHONY: all clean fclean re

default: all

all: $(NAME)
	@echo " # js : Job done  $(shell pwd)/$(CL_GREED)$(TARGET)$(CL_WHITE)"
	@echo " # js : Job done  $(shell pwd)/$(CL_GREED)$(BIN)$(CL_WHITE)"

$(NAME): $(OBJ_DIR) $(TARGET)

$(TARGET): $(OBJS)
	@echo " + js : Creating  $(CL_GREED)$@$(CL_WHITE) $(shell sleep 0.01)"
	@ar -rcv $(TARGET) $(OBJS) > /dev/null
	@ranlib $(TARGET)
	@$(CC) $(CFLAGS) $(MAIN) $(TARGET) -I $(INC_DIR) -o $(BIN)

clean:
	@echo " $(shell\
				if [ -d $(OBJ_DIR) ];\
				then\
					echo "- js : Removing $(CL_RED)$(OBJ_DIR)$(CL_WHITE) with$(CL_RED)";\
					ls $(OBJ_DIR) | wc -w; echo "$(CL_WHITE)*.o";\
					rm -Rf $(OBJ_DIR);\
				else\
					echo "# js : Nothing to clean";\
				fi)"


fclean: clean
	@echo " $(shell\
					if [ -f $(TARGET) ];\
					then\
						echo "- js : Removing  $(CL_RED)$(TARGET)$(CL_WHITE)";\
						rm -f $(TARGET);\
					else\
						echo "# js : Nothing to fclean";\
					fi)"
	@echo " $(shell\
					if [ -f $(BIN) ];\
						then\
							echo "- js : Removing  $(CL_RED)$ $(BIN) $(CL_WHITE)";\
							rm -f $(BIN);\
					else\
							echo "# ft : Nothing to fclean";\
					fi)"

re: fclean all

$(addprefix $(OBJ_DIR), %.o): $(addprefix $(SRC_DIR), %.c)
	@echo " + js : Compiling $(CL_CYAN)$(OBJ_DIR) < $^$(CL_WHITE)"
	@$(CC) $(CFLAGS) -I $(INC_DIR) -o $@ -c $<

$(OBJ_DIR):
	@echo " + js : Creating $(CL_GREED)$(OBJ_DIR)$(CL_WHITE)$(CL_WHITE)"
	@mkdir -p $(OBJ_DIR)