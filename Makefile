ifeq ($(OS),Windows_NT)
	COMPILER_FLAGS = -std=c++11 -Wall

	RM = del /Q
	FixPath = $(subst /,\,$1)
else
	COMPILER_FLAGS = -std=c++11 -Wall
	RM = rm -f
	FixPath = $1
endif

OBJS = sonarSim.cpp util.cpp Trinar.cpp SensorTArray.cpp

OBJ_NAME = sonarSim

all : $(OBJS)
	g++ $(OBJS) $(COMPILER_FLAGS) -o $(OBJ_NAME)
#$(INCLUDE_PATHS) $(LIBRARY_PATHS) $(LINKER_FLAGS)

clean:
	$(RM) sonarSim.exe *.o core*/


#CC=g++
#CPPFLAGS= -g -Wall -std=c++11

#all: sonarSim

#sonarSim: sonarSim.cpp util.o Trinar.o SensorTArray.o

#util.o: util.h

#Trinar.o: Trinar.h util.o

#SensorTArray.o: SensorTArray.h

#clean:
#	rm -f sonarSim *.o core*/