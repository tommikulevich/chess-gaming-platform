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
        self.activePlayer = "dark" if self.activePlayer == "light" else "light"

    def getPiece(self, x, y):
        return self.textBoard[y, x]

    def setPiece(self, x, y, piece):
        self.textBoard[y, x] = piece

    def findPiecesXY(self, pieceType):
        coords = np.where(self.textBoard == pieceType)
        return list(zip(coords[1], coords[0]))

    def movePiece(self, startX, startY, newX, newY):
        piece = self.getPiece(startX, startY)

        if [newX, newY] != [startX, startY]:
            if piece.lower() == 'k' and [newX, newY] in self.getCastlingMoves(startX, startY):
                rookStartX, rookNewX = 7 if newX - startX > 0 else 0, (newX + startX) // 2
                rookPiece = self.getPiece(rookStartX, startY)
                self.castlingRookPos = (rookStartX, rookNewX)
                self.castlingPerformed = True

                self.setPiece(rookNewX, startY, rookPiece)
                self.setPiece(rookStartX, startY, '.')

                if startY == (0 if self.activePlayer == "dark" else 7):
                    if rookStartX == 0:
                        self.castling[self.activePlayer]['leftRookMoved'] = True
                    elif rookStartX == 7:
                        self.castling[self.activePlayer]['rightRookMoved'] = True

            if piece.lower() == 'k':
                self.castling[self.activePlayer]['kingMoved'] = True
            elif piece.lower() == 'r':
                if startY == (0 if self.activePlayer == "dark" else 7):
                    if startX == 0:
                        self.castling[self.activePlayer]['leftRookMoved'] = True
                    elif startX == 7:
                        self.castling[self.activePlayer]['rightRookMoved'] = True

            if self.enPassantTarget is not None:
                x, y = self.enPassantTarget
                if (piece == 'P' and self.getPiece(x, y) == 'p') or (piece == 'p' and self.getPiece(x, y) == 'P'):
                    if (newX, newY + (1 if piece.isupper() else -1)) == self.enPassantTarget:
                        self.setPiece(*self.enPassantTarget, '.')
                        self.enPassantPerformed = True

            self.setPiece(newX, newY, piece)
            self.setPiece(startX, startY, '.')

            if not self.enPassantPerformed:
                if piece.lower() == 'p' and abs(newY - startY) == 2:
                    self.enPassantTarget = (newX, newY)
                else:
                    self.enPassantTarget = None

    def testMovePiece(self, startX, startY, newX, newY):
        piece = self.getPiece(startX, startY)

        self.setPiece(newX, newY, piece)
        self.setPiece(startX, startY, '.')

    # ----------------------------------------------------------

    def getLegalMoves(self, x, y):
        possibleMoves = self.getPossibleMoves(x, y)
        piece = self.getPiece(x, y)

        legalMoves = [[newX, newY] for newX, newY in possibleMoves if not self.simulateMove(x, y, newX, newY, piece)]

        return legalMoves

    def simulateMove(self, x1, y1, x2, y2, piece):
        targetPiece = self.getPiece(x2, y2)

        self.testMovePiece(x1, y1, x2, y2)
        inCheck = self.isInCheck(piece.isupper())[2]
        self.testMovePiece(x2, y2, x1, y1)

        if targetPiece != '.':
            self.setPiece(x2, y2, targetPiece)

        return inCheck

    def getPossibleMoves(self, x, y):
        piece = self.getPiece(x, y)
        movesDict = {
            'p': self.getPawnMoves,
            'n': self.getKnightMoves,
            'r': self.getRookMoves,
            'b': self.getBishopMoves,
            'q': self.getQueenMoves,
            'k': self.getKingMoves,
        }

        if piece.lower() in movesDict:
            return movesDict[piece.lower()](x, y)

        return []

    def getPawnMoves(self, x, y):
        piece = self.getPiece(x, y)
        moveDir = 1 if piece.islower() else -1

        regularMoves = []
        if self.getPiece(x, y + moveDir) == '.':
            regularMoves.append([x, y + moveDir])
            if (y == 1 and piece.islower()) or (y == 6 and piece.isupper()):
                if self.getPiece(x, y + 2 * moveDir) == '.':
                    regularMoves.append([x, y + 2 * moveDir])

        if self.enPassantTarget is not None:
            enX, enY = self.enPassantTarget
            if y == enY and (x - 1 == enX or x + 1 == enX):
                regularMoves.append([enX, enY + moveDir])

        captureMoves = [[x + dx, y + moveDir] for dx in (-1, 1)
                        if 0 <= x + dx < 8
                        and self.getPiece(x + dx, y + moveDir).isupper() != piece.isupper()
                        and self.getPiece(x + dx, y + moveDir) != '.']

        return regularMoves + captureMoves

    def getRookMoves(self, x, y):
        piece = self.getPiece(x, y)
        rookShifts = np.array([(1, 0), (-1, 0), (0, 1), (0, -1)])

        moves = [move for shift in rookShifts for move in self.rookMoveCalculations(piece, np.array([x, y]), shift)]

        return moves

    def rookMoveCalculations(self, piece, position, shift):
        boardInd = np.array([(i * shift[0] + position[0], i * shift[1] + position[1]) for i in range(1, 8)])
        validInd = np.all((boardInd >= 0) & (boardInd < 8), axis=1)
        validPos = boardInd[validInd]

        targetPieces = [self.getPiece(*pos) for pos in validPos]
        try:
            firstNonEmpty = targetPieces.index(next(filter(lambda p: p != '.', targetPieces)))

            if targetPieces[firstNonEmpty].isupper() != piece.isupper():
                return validPos[:firstNonEmpty + 1].tolist()
            else:
                return validPos[:firstNonEmpty].tolist()
        except StopIteration:
            return validPos.tolist()

    def getKnightMoves(self, x, y):
        piece = self.getPiece(x, y)
        knightShifts = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]

        moves = [[x + dx, y + dy]
                 for dx, dy in knightShifts
                 if 0 <= x + dx < 8 and 0 <= y + dy < 8 and (self.getPiece(x + dx, y + dy) == '.'
                 or self.getPiece(x + dx, y + dy).isupper() != piece.isupper())]

        return moves

    def getBishopMoves(self, x, y):
        piece = self.getPiece(x, y)
        bishopShifts = [(1, 1), (-1, 1), (1, -1), (-1, -1)]

        moves = [move for shift in bishopShifts for move in self.bishopMoveCalculations(piece, x, y, *shift)]

        return moves

    def bishopMoveCalculations(self, piece, x, y, dx, dy):
        validPos = [[x + i * dx, y + i * dy]
                    for i in range(1, 8)
                    if 0 <= x + i * dx < 8 and 0 <= y + i * dy < 8 and (self.getPiece(x + i * dx, y + i * dy) == '.'
                    or self.getPiece(x + i * dx, y + i * dy).isupper() != piece.isupper())
                    and not any(self.getPiece(x + j * dx, y + j * dy) != '.' for j in range(1, i))]

        return validPos

    def getQueenMoves(self, x, y):
        return self.getBishopMoves(x, y) + self.getRookMoves(x, y)

    def getKingMoves(self, x, y):
        piece = self.getPiece(x, y)
        kingShifts = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]

        moves = [[x + dx, y + dy]
                 for dx, dy in kingShifts
                 if 0 <= x + dx < 8 and 0 <= y + dy < 8 and (self.getPiece(x + dx, y + dy) == '.'
                 or self.getPiece(x + dx, y + dy).isupper() != piece.isupper())]

        castlingMoves = self.getCastlingMoves(x, y)
        if castlingMoves:
            moves.extend(castlingMoves)

        return moves

    # ----------------------------------------------------------

    def getKingPos(self, isLight):
        piece = 'K' if isLight else 'k'
        pos = np.where(np.array(self.textBoard) == piece)

        return pos[1][0], pos[0][0]

    def isSquareAttacked(self, x, y, isLight):
        attacked = any([x, y] in self.getPossibleMoves(attackX, attackY)
                       for attackX, attackY in itertools.product(range(8), range(8))
                       if self.getPiece(attackX, attackY) != '.'
                       and self.getPiece(attackX, attackY).isupper() != isLight)

        return attacked

    def isInCheck(self, isLight):
        kingX, kingY = self.getKingPos(isLight)

        return kingX, kingY, self.isSquareAttacked(kingX, kingY, isLight)

    def isCheck(self, side):
        isLight = (self.activePlayer == side)

        return self.isInCheck(not isLight)

    def isCheckmate(self, isLight):
        if not self.isInCheck(isLight)[2]:
            return False

        checkmate = not any(self.getLegalMoves(x, y)
                            for x, y in itertools.product(range(8), range(8))
                            if self.getPiece(x, y) != '.'
                            and self.getPiece(x, y).isupper() == isLight)

        return checkmate

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
        newPieceName = newPieceName.upper() if piece.isupper() else newPieceName.lower()

        self.setPiece(x, y, newPieceName)

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
            endX, endY = ord(end[0]) - ord('a'), 8 - int(end[1])

            if not piece:
                piece = 'P' if self.activePlayer == 'light' else 'p'

            if self.activePlayer == 'dark':
                piece = piece.lower()

            piecePositions = self.findPiecesXY(piece)
            if not piecePositions:
                return self.getError(3)

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
                return self.getError(4)
            else:
                return self.getError(5)

        return None

    @staticmethod
    def getError(no):
        errors = ["Error when parsing move! Probably format is incorrect",
                  "You have already made your move!",
                  "You are trying to move the opponent's piece!",
                  "You are trying to move wrong piece!",
                  "Disambiguating move! Specify it with file and/or rank",
                  "Move is incorrect",
                  "Please make your move!"]

        return errors[no]
