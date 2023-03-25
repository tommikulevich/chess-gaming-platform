import itertools

import numpy as np


class ChessLogic:
    def __init__(self):
        self.pieces = {
            "P": 0x00FF000000000000,
            "p": 0x000000000000FF00,
            "N": 0x4200000000000000,
            "n": 0x0000000000000042,
            "B": 0x2400000000000000,
            "b": 0x0000000000000024,
            "R": 0x8100000000000000,
            "r": 0x0000000000000081,
            "Q": 0x0800000000000000,
            "q": 0x0000000000000008,
            "K": 0x1000000000000000,
            "k": 0x0000000000000010
        }

    def setPiece(self, piece, pos):
        self.pieces[piece] |= pos

    def getPiece(self, pos):
        for piece, bitboard in self.pieces.items():
            if bitboard & pos:
                return piece

        return None

    def getPieceAt(self, x, y):
        pos = self.xyToBit(x, y)

        return self.getPiece(pos)

    def getAllPieces(self):
        return sum(self.pieces.values())

    def movePiece(self, piece, oldPos, newPos):
        targetPiece = self.getPiece(newPos)
        if targetPiece:
            self.removePiece(targetPiece, newPos)

        self.removePiece(piece, oldPos)
        self.setPiece(piece, newPos)

    def removePiece(self, piece, pos):
        self.pieces[piece] &= ~pos

    # ----------------------------------------------------------

    def getPossibleMoves(self, piece, x, y):
        if piece.lower() == 'p':
            return self.getPawnMoves(piece, x, y)
        elif piece.lower() == 'r':
            return self.getRookMoves(piece, x, y)
        elif piece.lower() == 'n':
            return self.getKnightMoves(piece, x, y)
        elif piece.lower() == 'b':
            return self.getBishopMoves(piece, x, y)
        elif piece.lower() == 'q':
            return self.getQueenMoves(piece, x, y)
        elif piece.lower() == 'k':
            return self.getKingMoves(piece, x, y)

        return []

    def getPawnMoves(self, piece, x, y):
        moves = []

        moveDir = 1 if piece.islower() else -1
        enPassantRank = 5 if piece.islower() else 2

        if (piece.islower() and y == 7) or (piece.isupper() and y == 0):
            return moves

        # Checking moves one square forward
        move = self.xyToBit(x, y + moveDir)
        if not any(bitboard & move for bitboard in self.pieces.values()):
            moves.append([x, y + moveDir])

            # Checking moves two squares forward (only for pawns in the starting position)
            if (piece.islower() and y == 1) or (piece.isupper() and y == 6):
                move = self.xyToBit(x, y + 2 * moveDir)
                if not any(bitboard & move for bitboard in self.pieces.values()):
                    moves.append([x, y + 2 * moveDir])

        # Checking moves after the bevel (beating)
        for dx in [-1, 1]:
            if 0 <= x + dx < 8:
                target = self.xyToBit(x + dx, y + moveDir)
                targetPiece = self.getPiece(target)

                if targetPiece and (targetPiece.isupper() != piece.isupper()):
                    moves.append([x + dx, y + moveDir])
                elif y == enPassantRank and targetPiece is None:
                    # ...
                    pass

        return moves

    def getRookMoves(self, piece, x, y):
        moves = []
        rookShifts = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dx, dy in rookShifts:
            newX, newY = x + dx, y + dy

            while 0 <= newX < 8 and 0 <= newY < 8:
                target = self.xyToBit(newX, newY)
                targetPiece = self.getPiece(target)

                if targetPiece is None:
                    moves.append([newX, newY])
                else:
                    if targetPiece.isupper() != piece.isupper():
                        moves.append([newX, newY])
                    break

                newX += dx
                newY += dy

        return moves

    def getKnightMoves(self, piece, x, y):
        moves = []
        knightShifts = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]

        for dx, dy in knightShifts:
            newX, newY = x + dx, y + dy

            if 0 <= newX < 8 and 0 <= newY < 8:
                target = self.xyToBit(newX, newY)
                targetPiece = self.getPiece(target)

                if targetPiece is None or targetPiece.isupper() != piece.isupper():
                    moves.append([newX, newY])

        return moves

    def getBishopMoves(self, piece, x, y):
        moves = []
        bishopShifts = [(1, 1), (-1, 1), (1, -1), (-1, -1)]

        for dx, dy in bishopShifts:
            newX, newY = x + dx, y + dy

            while 0 <= newX < 8 and 0 <= newY < 8:
                target = self.xyToBit(newX, newY)
                targetPiece = self.getPiece(target)

                if targetPiece is None:
                    moves.append([newX, newY])
                else:
                    if targetPiece.isupper() != piece.isupper():
                        moves.append([newX, newY])
                    break

                newX += dx
                newY += dy

        return moves

    def getQueenMoves(self, piece, x, y):
        bishopMoves = self.getBishopMoves(piece, x, y)
        rookMoves = self.getRookMoves(piece, x, y)

        return bishopMoves + rookMoves

    def getKingMoves(self, piece, x, y):
        moves = []
        kingShifts = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for dx, dy in kingShifts:
            newX, newY = x + dx, y + dy

            if 0 <= newX < 8 and 0 <= newY < 8:
                target = self.xyToBit(newX, newY)
                targetPiece = self.getPiece(target)

                if targetPiece is None or targetPiece.isupper() != piece.isupper():
                    moves.append([newX, newY])

        return moves

    # ----------------------------------------------------------

    def getKingPos(self, isWhite):
        x, y = self.bitToXY(self.pieces['K' if isWhite else 'k'])

        return x, y

    def isSquareAttacked(self, x, y, isWhite):
        for piece, bitboard in self.pieces.items():
            if piece.isupper() != isWhite:
                for attackX, attackY in itertools.product(range(8), range(8)):
                    if bitboard & self.xyToBit(attackX, attackY):
                        moves = self.getPossibleMoves(piece, attackX, attackY)
                        if [x, y] in moves:
                            return True
        return False

    def isCheck(self, isWhite):
        kingX, kingY = self.getKingPos(isWhite)

        return self.isSquareAttacked(kingX, kingY, isWhite)

    def isCheckmate(self, isWhite):
        if not self.isCheck(isWhite):
            return False

        for piece, bitboard in self.pieces.items():
            if piece.isupper() == isWhite:
                for x, y in itertools.product(range(8), range(8)):
                    if bitboard & self.xyToBit(x, y):
                        legalMoves = self.getLegalMoves(piece, x, y)
                        if legalMoves:
                            return False

        return True

    def getLegalMoves(self, piece, x, y):
        possibleMoves = self.getPossibleMoves(piece, x, y)
        legalMoves = []

        for move in possibleMoves:
            newX, newY = move
            oldPos = self.xyToBit(x, y)
            newPos = self.xyToBit(newX, newY)
            targetPiece = self.getPiece(newPos)

            self.movePiece(piece, oldPos, newPos)
            if targetPiece:
                self.removePiece(targetPiece, newPos)

            if not self.isCheck(piece.isupper()):
                legalMoves.append(move)

            self.movePiece(piece, newPos, oldPos)
            if targetPiece:
                self.setPiece(targetPiece, newPos)

        return legalMoves

    # ----------------------------------------------------------

    @staticmethod
    def xyToBit(x, y):
        return 1 << (y * 8 + x)

    @staticmethod
    def bitToXY(bit):
        index = (bit & -bit).bit_length() - 1
        x = index % 8
        y = index // 8

        return x, y

    def printBoard(self):
        board = [['.' for _ in range(8)] for _ in range(8)]

        for piece, pos in self.pieces.items():
            for i in range(64):
                if pos & (1 << i):
                    x, y = self.bitToXY(1 << i)
                    board[y][x] = piece

        print("  A B C D E F G H")
        for i, row in enumerate(board):
            print(8 - i, end=" ")
            print(' '.join(row))
