import numpy as np
import itertools


class ChessLogic:
    def __init__(self):
        self.textBoard = np.array([
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ])

        self.activePlayer = "light"
        self.playerMoved = False

    def switchActivePlayer(self):
        if self.activePlayer == "light":
            self.activePlayer = "dark"
        else:
            self.activePlayer = "light"

    def getPiece(self, x, y):
        return self.textBoard[y, x]

    def setPiece(self, x, y, piece):
        self.textBoard[y, x] = piece

    def movePiece(self, oldX, oldY, newX, newY):
        piece = self.getPiece(oldX, oldY)

        self.setPiece(newX, newY, piece)
        self.setPiece(oldX, oldY, '.')

    # ----------------------------------------------------------

    def getPossibleMoves(self, x, y):
        piece = self.getPiece(x, y)

        if piece.lower() == 'p':
            return self.getPawnMoves(x, y)
        elif piece.lower() == 'r':
            return self.getRookMoves(x, y)
        elif piece.lower() == 'n':
            return self.getKnightMoves(x, y)
        elif piece.lower() == 'b':
            return self.getBishopMoves(x, y)
        elif piece.lower() == 'q':
            return self.getQueenMoves(x, y)
        elif piece.lower() == 'k':
            return self.getKingMoves(x, y)

        return []

    def getPawnMoves(self, x, y):
        moves = []
        piece = self.getPiece(x, y)

        moveDir = 1 if piece.islower() else -1

        if 0 <= y + moveDir < 8:
            target = self.getPiece(x, y + moveDir)

            if target == '.':
                moves.append([x, y + moveDir])

                if (piece.islower() and y == 1) or (piece.isupper() and y == 6):
                    target = self.getPiece(x, y + 2 * moveDir)

                    if target == '.':
                        moves.append([x, y + 2 * moveDir])

        for dx in [-1, 1]:
            if 0 <= x + dx < 8 and 0 <= y + moveDir < 8:
                target = self.getPiece(x + dx, y + moveDir)

                if target != '.' and (target.isupper() != piece.isupper()):
                    moves.append([x + dx, y + moveDir])

        return moves

    def getRookMoves(self, x, y):
        moves = []
        piece = self.getPiece(x, y)

        rookShifts = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dx, dy in rookShifts:
            newX, newY = x + dx, y + dy

            while 0 <= newX < 8 and 0 <= newY < 8:
                target = self.getPiece(newX, newY)

                if target == '.':
                    moves.append([newX, newY])
                else:
                    if target.isupper() != piece.isupper():
                        moves.append([newX, newY])
                    break

                newX += dx
                newY += dy

        return moves

    def getKnightMoves(self, x, y):
        moves = []
        piece = self.getPiece(x, y)

        knightShifts = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]

        for dx, dy in knightShifts:
            newX, newY = x + dx, y + dy

            if 0 <= newX < 8 and 0 <= newY < 8:
                target = self.getPiece(newX, newY)

                if target == '.' or target.isupper() != piece.isupper():
                    moves.append([newX, newY])

        return moves

    def getBishopMoves(self, x, y):
        moves = []
        piece = self.getPiece(x, y)

        bishopShifts = [(1, 1), (-1, 1), (1, -1), (-1, -1)]

        for dx, dy in bishopShifts:
            newX, newY = x + dx, y + dy

            while 0 <= newX < 8 and 0 <= newY < 8:
                target = self.getPiece(newX, newY)

                if target == '.':
                    moves.append((newX, newY))
                else:
                    if target.isupper() != piece.isupper():
                        moves.append([newX, newY])
                    break

                newX += dx
                newY += dy

        return moves

    def getQueenMoves(self, x, y):
        return self.getBishopMoves(x, y) + self.getRookMoves(x, y)

    def getKingMoves(self, x, y):
        moves = []
        piece = self.getPiece(x, y)

        kingShifts = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for dx, dy in kingShifts:
            newX, newY = x + dx, y + dy

            if 0 <= newX < 8 and 0 <= newY < 8:
                target = self.getPiece(newX, newY)

                if target == '.' or target.isupper() != piece.isupper():
                    moves.append([newX, newY])

        return moves

    # ----------------------------------------------------------

    def getKingPos(self, isLight):
        piece = 'K' if isLight else 'k'
        pos = np.where(np.array(self.textBoard) == piece)

        return pos[1][0], pos[0][0]

    def isSquareAttacked(self, x, y, isLight):
        for attackX, attackY in itertools.product(range(8), range(8)):
            piece = self.getPiece(attackX, attackY)

            if piece != '.' and piece.isupper() != isLight:
                moves = self.getPossibleMoves(attackX, attackY)

                if [x, y] in moves:
                    return True

        return False

    def isInCheck(self, isLight):
        kingX, kingY = self.getKingPos(isLight)

        return self.isSquareAttacked(kingX, kingY, isLight)

    def isCheckmate(self, isLight):
        if not self.isInCheck(isLight):
            return False

        for x, y in itertools.product(range(8), range(8)):
            piece = self.getPiece(x, y)

            if piece != '.' and piece.isupper() == isLight:
                legalMoves = self.getLegalMoves(x, y)

                if legalMoves:
                    return False

        return True

    def getLegalMoves(self, x, y):
        possibleMoves = self.getPossibleMoves(x, y)
        legalMoves = []

        piece = self.getPiece(x, y)
        for newX, newY in possibleMoves:
            
            targetPiece = self.getPiece(newX, newY)

            self.movePiece(x, y, newX, newY)

            if not self.isInCheck(piece.isupper()):
                legalMoves.append([newX, newY])

            self.movePiece(newX, newY, x, y)

            if targetPiece != '.':
                self.setPiece(newX, newY, targetPiece)

        return legalMoves
