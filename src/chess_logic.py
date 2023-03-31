import re
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

        self.activePlayer = None
        self.playerMoved = False

        self.check = False

        self.enPassantTarget = None
        self.enPassantPerformed = False

        self.castlingRookPos = None
        self.castlingPerformed = False
        self.castling = {'light': {'kingMoved': False, 'leftRookMoved': False, 'rightRookMoved': False},
                         'dark': {'kingMoved': False, 'leftRookMoved': False, 'rightRookMoved': False}}

    def switchActivePlayer(self):
        if self.activePlayer == "light":
            self.activePlayer = "dark"
        else:
            self.activePlayer = "light"

    def getPiece(self, x, y):
        return self.textBoard[y, x]

    def setPiece(self, x, y, piece):
        self.textBoard[y, x] = piece

    def testMovePiece(self, oldX, oldY, newX, newY):
        piece = self.getPiece(oldX, oldY)

        self.setPiece(newX, newY, piece)
        self.setPiece(oldX, oldY, '.')

    def movePiece(self, oldX, oldY, newX, newY):
        piece = self.getPiece(oldX, oldY)

        if [newX, newY] != [oldX, oldY]:
            if piece.lower() == 'k' and [newX, newY] in self.getCastlingMoves(oldX, oldY):
                rookOldX, rookNewX = 7 if newX - oldX > 0 else 0, (newX + oldX) // 2
                rookPiece = self.getPiece(rookOldX, oldY)
                self.castlingRookPos = (rookOldX, rookNewX)
                self.castlingPerformed = True

                self.setPiece(rookNewX, oldY, rookPiece)
                self.setPiece(rookOldX, oldY, '.')

                if oldY == (0 if self.activePlayer == "dark" else 7):
                    if rookOldX == 0:
                        self.castling[self.activePlayer]['leftRookMoved'] = True
                    elif rookOldX == 7:
                        self.castling[self.activePlayer]['rightRookMoved'] = True

            if piece.lower() == 'k':
                self.castling[self.activePlayer]['kingMoved'] = True
            elif piece.lower() == 'r':
                if oldY == (0 if self.activePlayer == "dark" else 7):
                    if oldX == 0:
                        self.castling[self.activePlayer]['leftRookMoved'] = True
                    elif oldX == 7:
                        self.castling[self.activePlayer]['rightRookMoved'] = True

            if self.enPassantTarget is not None:
                x, y = self.enPassantTarget
                if (piece == 'P' and self.getPiece(x, y) == 'p') or (piece == 'p' and self.getPiece(x, y) == 'P'):
                    if (newX, newY + (1 if piece.isupper() else -1)) == self.enPassantTarget:
                        self.setPiece(*self.enPassantTarget, '.')
                        self.enPassantPerformed = True

            self.setPiece(newX, newY, piece)
            self.setPiece(oldX, oldY, '.')

            if not self.enPassantPerformed:
                if piece.lower() == 'p' and abs(newY - oldY) == 2:
                    self.enPassantTarget = (newX, newY)
                else:
                    self.enPassantTarget = None

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

        if self.enPassantTarget is not None:
            enX, enY = self.enPassantTarget
            if y == enY and (x - 1 == enX or x + 1 == enX):
                moves.append([enX, enY + moveDir])

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

        castlingMoves = self.getCastlingMoves(x, y)
        if castlingMoves:
            moves.extend(castlingMoves)

        return moves

    def getCastlingMoves(self, x, y):
        moves = []

        if not self.castling[self.activePlayer]['kingMoved']:
            if not self.castling[self.activePlayer]['leftRookMoved']:
                if all(self.getPiece(i, y) == '.' for i in range(x - 1, 0, -1)):
                    moves.append([x - 2, y])
            if not self.castling[self.activePlayer]['rightRookMoved']:
                if all(self.getPiece(i, y) == '.' for i in range(x + 1, 7)):
                    moves.append([x + 2, y])

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

        return kingX, kingY, self.isSquareAttacked(kingX, kingY, isLight)

    def isCheck(self, side):
        isLight = (self.activePlayer == side)

        return self.isInCheck(not isLight)

    def isCheckmate(self, isLight):
        if not self.isInCheck(isLight)[2]:
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

            self.testMovePiece(x, y, newX, newY)
            if not self.isInCheck(piece.isupper())[2]:
                legalMoves.append([newX, newY])
            self.testMovePiece(newX, newY, x, y)

            if targetPiece != '.':
                self.setPiece(newX, newY, targetPiece)

        return legalMoves

    def isEnPassant(self):
        enPassantPerformed = self.enPassantPerformed
        target = self.enPassantTarget

        if enPassantPerformed:
            self.enPassantPerformed = False
            self.enPassantTarget = None

        return enPassantPerformed, target

    def isCastling(self):
        castlingPerformed = self.castlingPerformed
        castlingRookPos = self.castlingRookPos

        if castlingPerformed:
            self.castlingPerformed = False
            self.castlingRookPos = None

        return castlingPerformed, castlingRookPos

    def isPromotion(self, x, y):
        piece = self.getPiece(x, y)
        if (piece == "P" and y == 0) or (piece == "p" and y == 7):
            return True

        return False

    def promotePawn(self, x, y, newPieceName):
        piece = self.getPiece(x, y)
        if piece.isupper():
            newPieceName = newPieceName.upper()
        else:
            newPieceName = newPieceName.lower()

        self.setPiece(x, y, newPieceName)

    # ----------------------------------------------------------

    def findPiecesXY(self, pieceType):
        coords = np.where(self.textBoard == pieceType)
        return list(zip(coords[1], coords[0]))

    def parseMove(self, moveText):
        moveText = moveText.strip()
        if moveText == "O-O" or moveText == "O-O-O":
            piece = 'K' if self.activePlayer == 'light' else 'k'
            startX, startY = self.findPiecesXY(piece)[0]
            dx = 2 if moveText == "O-O" else -2
            endX, endY = startX + dx, startY

            return startX, startY, endX, endY, None

        pattern = re.compile(r"^([RNBQK]?)([a-h]?)([1-8]?)([x]?)([a-h][1-8])(=?[qrbnQRBN]?)$")
        match = pattern.match(moveText)

        if match:
            piece, file, rank, capture, end, promotionPiece = match.groups()

            if not piece:
                piece = 'P' if self.activePlayer == 'light' else 'p'

            if self.activePlayer == 'dark':
                piece = piece.lower()

            endX, endY = ord(end[0]) - ord('a'), 8 - int(end[1])
            piecePositions = self.findPiecesXY(piece)
            if piecePositions:
                count = 0
                startX, startY = 0, 0
                notDisambiguating = False

                for x, y in piecePositions:
                    legalMoves = self.getLegalMoves(x, y)

                    if [endX, endY] in legalMoves:
                        if promotionPiece:
                            promotionPiece = promotionPiece[1].lower() if self.getPiece(x, y).islower() else \
                                promotionPiece[1].upper()
                        else:
                            promotionPiece = None

                        if piece.lower() != 'p':
                            if file and rank:
                                startX, startY = ord(file) - ord('a'), 8 - int(rank)
                                if startX == x and startY == y:
                                    notDisambiguating = True
                                    break
                            elif file:
                                startX, startY = ord(file) - ord('a'), y

                                if startX == x:
                                    notDisambiguating = True
                                    break
                            elif rank:
                                startX, startY = x, 8 - int(rank)

                                if startY == y:
                                    notDisambiguating = True
                                    break
                            else:
                                count += 1
                                startX, startY = x, y
                        else:
                            count += 1
                            startX, startY = x, y

                if count == 1 or notDisambiguating:
                    return startX, startY, endX, endY, promotionPiece
                elif count > 1:
                    print("Disambiguating move")
                else:
                    print("Wrong move")
            else:
                print("Parse error")
        else:
            print("Match error")

        return None
