CC=g++
CPPFLAGS= -g -Wall -std=c++0x

all: sonarSim

sonarSim: sonarSim.cpp util.o Trinar.o SensorTArray.o

sonarSimSDL: sonarSimSDL.cpp util.o Trinar.o SensorTArray.o Display.o

util.o: util.h

Trinar.o: Trinar.h util.o

SensorTArray.o: SensorTArray.h

Display.o: Display.h

clean:
	rm -f sonarSim *.o core*


