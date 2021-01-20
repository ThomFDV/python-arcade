# MARIO = """
#  0123456789.....
# 0XXXXXXXXXXXXXXXXXXXXXXXXXXXX
# 1X          $               X
# 2X    #   #?#?#             X
# 3X                      $   X
# 4X.                        *X
# 5X##########################X
# 6XXXXXXXXXXXXXXXXXXXXXXXXXXXX
# """

class Map():
    def __init__(self, hauteur, largeur, piecesCoord, plateformeCoord):
        self.hauteur = hauteur
        self.largeur = largeur
        self.piecesCoord = piecesCoord
        self.plateformeCoord = plateformeCoord

        self.mapTab = [[' ' for i in range(largeur)] for j in range(hauteur)]

        self.createBorder()
        self.createFloor()
        self.createStartingPoint()
        self.createEndPoint()
        self.placePieces()
        self.placePlateforme()

    def createBorder(self):
        self.mapTab[0] = ['X'] * self.largeur
        self.mapTab[self.hauteur - 1] = ['X'] * self.largeur

        for i in range(self.hauteur):
            self.mapTab[i][0] = 'X'
            self.mapTab[i][self.largeur - 1] = 'X'

    def createFloor(self):
        self.mapTab[self.hauteur - 2] = ['#' for i in range(self.largeur)]
        self.mapTab[self.hauteur - 2][0] = 'X'
        self.mapTab[self.hauteur - 2][self.largeur - 1] = 'X'

    def createStartingPoint(self):
        self.mapTab[self.hauteur - 3][1] = '.'

    def createEndPoint(self):
        self.mapTab[self.hauteur - 3][self.largeur - 2] = '*'

    def placePieces(self):
        for coord in self.piecesCoord:
            if self.mapTab[coord[0]][coord[1]] not in ['X', '#', '.', '*']:
                self.mapTab[coord[0]][coord[1]] = '$'

    def placePlateforme(self):
        for coord in self.plateformeCoord:
            if self.mapTab[coord[0]][coord[1]] not in ['X', '$', '.', '*', '#', '?']:
                if coord[2] == 1:
                    self.mapTab[coord[0]][coord[1]] = '#'
                if coord[2] == 2:
                    self.mapTab[coord[0]][coord[1]] = '?'

    def showMap(self):
        return '\n'.join(''.join(x) for x in self.mapTab)


map = Map(7, 30, [(1, 11), (3, 22)], [(2, 5, 1), (2, 9, 1), (2, 10, 2), (2, 11, 1), (2, 12, 2), (2, 13, 1)])
print(map.showMap())

# pieces = [(1,11), (3,17)]
# platform = [(1,2,1), (5,8,2), (5,4,1)]
