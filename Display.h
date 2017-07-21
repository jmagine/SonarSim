 /*****************************************************************************

                                                         Author: Jason Ma
                                                         Date:   Feb 01 2017
                                      sonarSim

 File Name:       Display.h
 Description:     Visualizes SONAR data using SDL
 *****************************************************************************/

#include <SDL2/SDL.h>
#include <SDL2/SDL_image.h>
#include <string>

#ifndef DISPLAY_H
#define DISPLAY_H

class Display{
  public:
  	int init();
  	int load();
  	int handleEvents();
  	void render();
  	void stop();

    SDL_Texture * loadTexture(std::string path);
    
};

#endif /* DISPLAY_H */


