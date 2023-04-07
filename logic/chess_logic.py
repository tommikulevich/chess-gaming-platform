import re
import numpy as np
import itertools


class ChessLogic:
    def __init__(self):
        # Chess logic parameters
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

    # ---------------- General ----------------

    def switchActivePlayer(self):
        self.activePlayer = "dark" if self.activePlayer == "light" else "light"

    @staticmethod
    def getError(no):
        errors = [
            "Error when parsing move! Probably format is incorrect",
            "You have already made your move! Click to your clock to finish",
            "You are trying to move the opponent's piece!",
            "You are trying to move wrong piece!",
            "Ambiguous move! Specify it with file and/or rank",
            "Move is incorrect",
            "Please make your move!",
            "Start new game first!",
            "You can't do a promotion now!",
            "Castling is not possible!",
            "You can't do the capture!"
        ]

        return errors[no]

    # ---------------- Connected with positions ----------------

    def getPiece(self, x, y):
        return self.textBoard[y, x]

    def setPiece(self, x, y, piece):
        self.textBoard[y, x] = piece

    def findPiecesXY(self, pieceType):
        coords = np.where(self.textBoard == pieceType)
        return list(zip(coords[1], coords[0]))

    def getKingPos(self, isLight):
        piece = 'K' if isLight else 'k'
        pos = np.where(np.array(self.textBoard) == piece)

        return pos[1][0], pos[0][0]

    # ---------------- Moving (general) ----------------

    def movePiece(self, startX, startY, newX, newY):
        piece = self.getPiece(startX, startY)

        # If the player has not changed the position of the piece
        if [newX, newY] == [startX, startY]:
            return

        # If castling is possible
        if piece.lower() == 'k' and [newX, newY] in self.getCastlingMoves(startX, startY):
            rookStartX, rookNewX = 7 if newX - startX > 0 else 0, (newX + startX) // 2
            rookPiece = self.getPiece(rookStartX, startY)
            self.castlingRookPos = (rookStartX, rookNewX)
            self.castlingPerformed = True

            self.setPiece(rookNewX, startY, rookPiece)
            self.setPiece(rookStartX, startY, '.')

            # Changing flags related to the movements of the rooks
            if startY == (0 if self.activePlayer == "dark" else 7):
                if rookStartX == 0:
                    self.castling[self.activePlayer]['leftRookMoved'] = True
                elif rookStartX == 7:
                    self.castling[self.activePlayer]['rightRookMoved'] = True

        # Changing flags related to the movements of the kings and the rooks
        if piece.lower() == 'k':
            self.castling[self.activePlayer]['kingMoved'] = True
        elif piece.lower() == 'r':
            if startY == (0 if self.activePlayer == "dark" else 7):
                if startX == 0:
                    self.castling[self.activePlayer]['leftRookMoved'] = True
                elif startX == 7:
                    self.castling[self.activePlayer]['rightRookMoved'] = True

        # If en passant is possible
        if self.enPassantTarget is not None:
            x, y = self.enPassantTarget
            if (piece == 'P' and self.getPiece(x, y) == 'p') or (piece == 'p' and self.getPiece(x, y) == 'P'):
                if (newX, newY + (1 if piece.isupper() else -1)) == self.enPassantTarget:
                    self.setPiece(*self.enPassantTarget, '.')
                    self.enPassantPerformed = True

        self.setPiece(newX, newY, piece)
        self.setPiece(startX, startY, '.')

        # If en passant is not performed
        if not self.enPassantPerformed:
            self.enPassantTarget = (newX, newY) if piece.lower() == 'p' and abs(newY - startY) == 2 else None

    def testMovePiece(self, startX, startY, newX, newY):
        piece = self.getPiece(startX, startY)

        # En passant analyzing
        if self.enPassantPerformed:
            target = 'p' if piece.isupper() else 'P'
            self.setPiece(*self.enPassantTarget, target)
            self.enPassantPerformed = False
        elif self.enPassantTarget is not None:
            x, y = self.enPassantTarget
            if (piece == 'P' and self.getPiece(x, y) == 'p') or (piece == 'p' and self.getPiece(x, y) == 'P'):
                if (newX, newY + (1 if piece.isupper() else -1)) == self.enPassantTarget:
                    self.setPiece(*self.enPassantTarget, '.')
                    self.enPassantPerformed = True

        self.setPiece(newX, newY, piece)
        self.setPiece(startX, startY, '.')

    def getLegalMoves(self, x, y):
        possibleMoves = self.getPossibleMoves(x, y)
        piece = self.getPiece(x, y)

        # Castling analyzing
        if piece.lower() == 'k':
            castlingMoves = self.getCastlingMoves(x, y)
            if castlingMoves:
                possibleMoves.extend(castlingMoves)

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
        if 0 <= y + moveDir < 8:
            if self.getPiece(x, y + moveDir) == '.':
                regularMoves.append([x, y + moveDir])
                if (y == 1 and piece.islower()) or (y == 6 and piece.isupper()):
                    if self.getPiece(x, y + 2 * moveDir) == '.':
                        regularMoves.append([x, y + 2 * moveDir])

        # If en passant is possible
        if self.enPassantTarget is not None:
            enX, enY = self.enPassantTarget
            if y == enY and (x - 1 == enX or x + 1 == enX):
                regularMoves.append([enX, enY + moveDir])

        captureMoves = [[x + dx, y + moveDir] for dx in (-1, 1)
                        if 0 <= x + dx < 8 and 0 <= y + moveDir < 8
                        and self.getPiece(x + dx, y + moveDir).isupper() != piece.isupper()
                        and self.getPiece(x + dx, y + moveDir) != '.']

        return regularMoves + captureMoves

    def getRookMoves(self, x, y):
        piece = self.getPiece(x, y)
        rookShifts = np.array([(1, 0), (-1, 0), (0, 1), (0, -1)])

        moves = [move for shift in rookShifts for move in self.rookMoveCalculations(piece, x, y, shift)]

        return moves

    def rookMoveCalculations(self, piece, x, y, shift):
        allInd = np.array([(i * shift[0] + x, i * shift[1] + y) for i in range(1, 8)])
        validInd = np.all((allInd >= 0) & (allInd < 8), axis=1)
        validPos = allInd[validInd]

        targetPieces = [self.getPiece(*pos) for pos in validPos]
        firstNonEmpty = next((i for i, p in enumerate(targetPieces) if p != '.'), len(targetPieces))

        if firstNonEmpty < len(targetPieces) and targetPieces[firstNonEmpty].isupper() != piece.isupper():
            return validPos[:firstNonEmpty + 1].tolist()
        else:
            return validPos[:firstNonEmpty].tolist()

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

        return moves

    # ---------------- Moving (special) ----------------

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

        # If the king has already been moved
        if self.castling[self.activePlayer]['kingMoved']:
            return moves

        isLight = (self.activePlayer == "light")

        if not self.castling[self.activePlayer]['leftRookMoved']:
            if self.isPathClear(x, y, "left") and not self.isKingCrossingAttackedSquares(x, y, "left", isLight):
                moves.append([x - 2, y])

        if not self.castling[self.activePlayer]['rightRookMoved']:
            if self.isPathClear(x, y, "right") and not self.isKingCrossingAttackedSquares(x, y, "right", isLight):
                moves.append([x + 2, y])

        return moves

    def isPathClear(self, x, y, direction):
        if direction == "left":
            return all(self.getPiece(i, y) == '.' for i in range(x - 1, 0, -1))
        elif direction == "right":
            return all(self.getPiece(i, y) == '.' for i in range(x + 1, 7))

    def isKingCrossingAttackedSquares(self, x, y, direction, isLight):
        if direction == "left":
            return self.isSquareAttacked(x, y, isLight) \
                   or self.isSquareAttacked(x - 1, y, isLight) \
                   or self.isSquareAttacked(x - 2, y, isLight)
        elif direction == "right":
            return self.isSquareAttacked(x, y, isLight) \
                   or self.isSquareAttacked(x + 1, y, isLight) \
                   or self.isSquareAttacked(x + 2, y, isLight)

    # ---------------- Algebraic notation parsing ----------------

    def parseMove(self, moveText):
        # Removing spaces from text
        moveText = moveText.strip()

        # If castling combination
        if moveText in ["O-O", "O-O-O", "0-0", "0-0-0"]:
            piece = 'K' if self.activePlayer == 'light' else 'k'
            startX, startY = self.findPiecesXY(piece)[0]
            dx = 2 if moveText == "O-O" else -2
            endX, endY = startX + dx, startY

            if [endX, endY] in self.getCastlingMoves(startX, startY):
                return startX, startY, endX, endY, None
            else:
                return self.getError(9)

        # Text analysis
        pattern = re.compile(r"^([RNBQK]?)([a-h]?)([1-8]?)([x]?)([a-h][1-8])(=?[qrbnQRBN]?)$")
        match = pattern.match(moveText)

        # If the analysis failed
        if not match:
            return None

        # Getting data from analyzing results
        piece, file, rank, capture, end, promotionPiece = match.groups()
        endX, endY = ord(end[0]) - ord('a'), 8 - int(end[1])

        # If there is no capture to perform
        if capture and self.getPiece(endX, endY) == '.':
            return self.getError(10)

        # If no piece type is specified - it is about pawns (e.g. 'e4')
        if not piece:
            piece = 'P' if self.activePlayer == 'light' else 'p'

        # 'Resizing' piece name
        if self.activePlayer == 'dark':
            piece = piece.lower()

        # Finding the position of all player pieces of a given type
        piecePositions = self.findPiecesXY(piece)
        if not piecePositions:
            return self.getError(3)

        # Finding possible piece positions
        possiblePositions = [
            (x, y) for x, y in piecePositions
            if [endX, endY] in self.getLegalMoves(x, y)
        ]

        # Checking unambiguous moves
        isUnambiguous, startX, startY = self.isMoveUnambiguous(possiblePositions, file, rank)
        if not isUnambiguous:
            return self.getError(4 if len(possiblePositions) > 1 else 5)

        # Checking for promotion piece
        if promotionPiece:
            promotionPiece = promotionPiece[1].lower() if self.getPiece(startX, startY).islower() else \
                promotionPiece[1].upper()
        else:
            promotionPiece = None

        return startX, startY, endX, endY, promotionPiece

    @staticmethod
    def isMoveUnambiguous(piecePositions, file, rank):
        unambiguousPositions = [
            (x, y) for x, y in piecePositions if
            (not file or x == ord(file) - ord('a')) and
            (not rank or y == 8 - int(rank))
        ]

        startPos = unambiguousPositions[0] if unambiguousPositions else (None, None)

        return len(unambiguousPositions) == 1, startPos[0], startPos[1]

    def parseLongMove(self, moveText):
        """Long algebraic notation parser (not used)"""
        pattern = re.compile(r"^([a-h][1-8])([a-h][1-8])([qrbnQRBN]?)$")
        match = pattern.match(moveText)

        if match:
            start, end, promotionPiece = match.groups()
            startX, startY = ord(start[0]) - ord('a'), 8 - int(start[1])
            endX, endY = ord(end[0]) - ord('a'), 8 - int(end[1])

            if promotionPiece:
                promotionPiece = promotionPiece.lower() if self.getPiece(startX, startY).islower() \
                    else promotionPiece.upper()
            else:
                promotionPiece = None

            return startX, startY, endX, endY, promotionPiece
        else:
            return None
