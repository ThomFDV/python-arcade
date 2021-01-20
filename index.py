import arcade
from environment import Environment
from agent import Agent
from map import Map
from game import Game

def main():

    hauteur = 7
    largeur = 30
    piecesCoord = [(1, 11), (3, 22)]
    plateformeCoord = [(2, 5, 1), (2, 9, 1), (2, 10, 2), (2, 11, 1), (2, 12, 2), (2, 13, 1)]

    map = Map(hauteur, largeur, piecesCoord, plateformeCoord)

    environment = Environment(map.showMap())
    agent = Agent(environment)

    window = Game(agent, map.showMap())
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()