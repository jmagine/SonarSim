ifeq ($(OS),Windows_NT)
	COMPILER_FLAGS = -std=c++11 -Wall

	RM = del /Q
	FixPath = $(subst /,\,$1)
else
	COMPILER_FLAGS = -std=c++11 -Wall
	RM = rm -f
	FixPath = $1
endif

OBJS = main.cpp util.cpp Trinar.cpp SensorTArray.cpp

OBJ_NAME = topLevelSonar

SIM_OBJS = sonarSim.cpp util.cpp Trinar.cpp SensorTArray.cpp

SIM_OBJ_NAME = sonarSim
#sonarSimSDL: sonarSimSDL.cpp util.o Trinar.o SensorTArray.o Display.o

#util.o: util.h

all : $(OBJS)
	g++ $(OBJS) $(COMPILER_FLAGS) -o $(OBJ_NAME)

sim : $(OBJS)
	g++ $(SIM_OBJS) $(COMPILER_FLAGS) -o $(SIM_OBJ_NAME)
#$(INCLUDE_PATHS) $(LIBRARY_PATHS) $(LINKER_FLAGS)

Display.o: Display.h

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
