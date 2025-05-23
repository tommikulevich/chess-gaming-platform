import re
import itertools
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Sequence


class ChessLogic:
    def __init__(self) -> None:
        # Main parameters
        self.textBoard: np.ndarray = np.full((8, 8), ".", dtype=str)
        self.moveHistory: List[str] = []
        self.activePlayer: Optional[str] = None
        self.lastMove: Optional[str] = None

        # Flags
        self.playerMoved: bool = False
        self.check: bool = False
        self.enPassantPerformed: bool = False
        self.castlingPerformed: bool = False

        # Additional parameters
        self.promotionPiece: Optional[str] = None
        self.enPassantTarget: Optional[Tuple[int, int]] = None
        self.castlingRookPos: Optional[Tuple[int, int]] = None
        self.castling: Dict[str, Dict[str, bool]] = {
            'light': {'kingMoved': False,
                      'leftRookMoved': False,
                      'rightRookMoved': False},
            'dark': {'kingMoved': False,
                     'leftRookMoved': False,
                     'rightRookMoved': False}
        }

    # -----------------
    # General functions
    # -----------------

    def switchActivePlayer(self) -> None:
        self.activePlayer = "dark" if self.activePlayer == "light" else "light"

    @staticmethod
    def getError(ind: int) -> str:
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
            "You can't do the capture!",
            "Wait for opponent's move!"
        ]

        return errors[ind]

    # ---------------
    # Piece positions
    # ---------------

    def getPiece(self, x: int, y: int) -> str:
        return self.textBoard[y, x]

    def setPiece(self, x: int, y: int, piece: str) -> None:
        self.textBoard[y, x] = piece

    def findPiecesXY(self, piece: str) -> List[Tuple[int, int]]:
        coords = np.where(self.textBoard == piece)
        return list(zip(coords[1], coords[0]))

    def getKingPos(self, isLight: bool) -> Tuple[int, int]:
        piece = 'K' if isLight else 'k'
        pos = np.where(np.array(self.textBoard) == piece)

        return pos[1][0], pos[0][0]

    # ----------------------
    # Piece moving (general)
    # ----------------------

    def movePiece(self, startX: int, startY: int,
                  newX: int, newY: int) -> None:
        piece = self.getPiece(startX, startY)

        # Check if the player has not changed the position of the piece
        if [newX, newY] == [startX, startY]:
            return

        # Check if castling is possible
        if piece.lower() == 'k' \
                and [newX, newY] in self.getCastlingMoves(startX, startY):
            rookStartX, rookNewX = 7 if newX - startX > 0 \
                else 0, (newX + startX) // 2
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

        # Change flags related to the movements of the kings and the rooks
        if piece.lower() == 'k':
            self.castling[self.activePlayer]['kingMoved'] = True
        elif piece.lower() == 'r':
            if startY == (0 if self.activePlayer == "dark" else 7):
                if startX == 0:
                    self.castling[self.activePlayer]['leftRookMoved'] = True
                elif startX == 7:
                    self.castling[self.activePlayer]['rightRookMoved'] = True

        # Check if en passant is possible
        if self.enPassantTarget is not None:
            x, y = self.enPassantTarget
            if (piece == 'P' and self.getPiece(x, y) == 'p') \
                    or (piece == 'p' and self.getPiece(x, y) == 'P'):
                if (newX, newY + (1 if piece.isupper() else -1)) \
                        == self.enPassantTarget:
                    self.setPiece(*self.enPassantTarget, '.')
                    self.enPassantPerformed = True

        # Check if en passant is not performed
        if not self.enPassantPerformed:
            self.enPassantTarget = (newX, newY) \
                if piece.lower() == 'p' and abs(newY - startY) == 2 else None

        # Convert move coordinates to the move according to SAN notation
        sanMove = self.coordsToSAN(startX, startY, newX, newY)

        # Perform move
        self.setPiece(newX, newY, piece)
        self.setPiece(startX, startY, '.')

        # Add additional chars to move in SAN
        if self.isInCheck(not self.activePlayer == 'light')[2]:
            sanMove += '#' \
                if self.isCheckmate(not self.activePlayer == 'light') else '+'

        # Remember and add performed move to the history
        self.lastMove = f"{startX}{startY}{newX}{newY}"
        self.lastMove += f"{self.promotionPiece}" \
            if self.promotionPiece else ""
        self.moveHistory.append(sanMove)

    def testMovePiece(self, startX: int, startY: int,
                      newX: int, newY: int) -> None:
        piece = self.getPiece(startX, startY)

        # En passant analyzing
        if self.enPassantPerformed:
            target = 'p' if piece.isupper() else 'P'
            self.setPiece(*self.enPassantTarget, target)
            self.enPassantPerformed = False
        elif self.enPassantTarget is not None:
            x, y = self.enPassantTarget
            if (piece == 'P' and self.getPiece(x, y) == 'p') \
                    or (piece == 'p' and self.getPiece(x, y) == 'P'):
                if (newX, newY + (1 if piece.isupper() else -1)) \
                        == self.enPassantTarget:
                    self.setPiece(*self.enPassantTarget, '.')
                    self.enPassantPerformed = True

        self.setPiece(newX, newY, piece)
        self.setPiece(startX, startY, '.')

    def simulateMove(self, x1: int, y1: int,
                     x2: int, y2: int, piece: str) -> bool:
        target = self.getPiece(x2, y2)

        self.testMovePiece(x1, y1, x2, y2)
        inCheck = self.isInCheck(piece.isupper())[2]
        self.testMovePiece(x2, y2, x1, y1)

        if target != '.':
            self.setPiece(x2, y2, target)

        return inCheck

    def getLegalMoves(self, x: int, y: int) -> List[List[int]]:
        possibleMoves = self.getPossibleMoves(x, y)
        piece = self.getPiece(x, y)

        # Castling analyzing
        if piece.lower() == 'k':
            castlingMoves = self.getCastlingMoves(x, y)
            if castlingMoves:
                possibleMoves.extend(castlingMoves)

        legalMoves = [[newX, newY] for newX, newY in possibleMoves
                      if not self.simulateMove(x, y, newX, newY, piece)]

        return legalMoves

    def getPossibleMoves(self, x: int, y: int) -> List[List[int]]:
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

    def getPawnMoves(self, x: int, y: int) -> List[List[int]]:
        piece = self.getPiece(x, y)
        moveDir = 1 if piece.islower() else -1

        regularMoves = []
        if 0 <= y + moveDir < 8:
            if self.getPiece(x, y + moveDir) == '.':
                regularMoves.append([x, y + moveDir])
                if (y == 1 and piece.islower()) \
                        or (y == 6 and piece.isupper()):
                    if self.getPiece(x, y + 2 * moveDir) == '.':
                        regularMoves.append([x, y + 2 * moveDir])

        # Check if en passant is possible
        if self.enPassantTarget is not None:
            enX, enY = self.enPassantTarget
            if y == enY and (x - 1 == enX or x + 1 == enX) \
                    and 0 <= enY + moveDir < 8:
                regularMoves.append([enX, enY + moveDir])

        captureMoves = [[x + dx, y + moveDir] for dx in (-1, 1)
                        if 0 <= x + dx < 8 and 0 <= y + moveDir < 8
                        and self.getPiece(x + dx, y + moveDir).isupper()
                        != piece.isupper()
                        and self.getPiece(x + dx, y + moveDir) != '.']

        return regularMoves + captureMoves

    def getRookMoves(self, x: int, y: int) -> List[List[int]]:
        piece = self.getPiece(x, y)
        rookShifts = np.array([(1, 0), (-1, 0), (0, 1), (0, -1)])

        moves = [move for shift in rookShifts
                 for move in self.rookMoveCalculations(piece, x, y, shift)]

        return moves

    def rookMoveCalculations(self, piece: str, x: int, y: int,
                             shift: Tuple[int, int]) -> List[List[int]]:
        allInd = np.array([(i * shift[0] + x, i * shift[1] + y)
                           for i in range(1, 8)])
        validInd = np.all((allInd >= 0) & (allInd < 8), axis=1)
        validPos = allInd[validInd]

        targetPieces = [self.getPiece(*pos) for pos in validPos]
        firstNonEmpty = next(
            (i for i, p in enumerate(targetPieces) if p != '.'),
            len(targetPieces))

        if firstNonEmpty < len(targetPieces) \
                and targetPieces[firstNonEmpty].isupper() != piece.isupper():
            return validPos[:firstNonEmpty + 1].tolist()
        else:
            return validPos[:firstNonEmpty].tolist()

    def getKnightMoves(self, x: int, y: int) -> List[List[int]]:
        piece = self.getPiece(x, y)
        knightShifts = [(1, 2), (2, 1), (-1, 2), (-2, 1),
                        (1, -2), (2, -1), (-1, -2), (-2, -1)]

        moves = [[x + dx, y + dy]
                 for dx, dy in knightShifts
                 if 0 <= x + dx < 8
                 and 0 <= y + dy < 8
                 and (self.getPiece(x + dx, y + dy) == '.'
                 or self.getPiece(x + dx, y + dy).isupper()
                 != piece.isupper())]

        return moves

    def getBishopMoves(self, x: int, y: int) -> List[List[int]]:
        piece = self.getPiece(x, y)
        bishopShifts = [(1, 1), (-1, 1), (1, -1), (-1, -1)]

        moves = [move for shift in bishopShifts
                 for move in self.bishopMoveCalculations(piece, x, y, *shift)]

        return moves

    def bishopMoveCalculations(self, piece: str, x: int, y: int,
                               dx: int, dy: int) -> List[List[int]]:
        validPos = [[x + i * dx, y + i * dy]
                    for i in range(1, 8)
                    if 0 <= x + i * dx < 8 and 0 <= y + i * dy < 8
                    and (self.getPiece(x + i * dx, y + i * dy) == '.'
                    or self.getPiece(x + i * dx, y + i * dy).isupper()
                    != piece.isupper())
                    and not any(self.getPiece(x + j * dx, y + j * dy)
                                != '.' for j in range(1, i))]

        return validPos

    def getQueenMoves(self, x: int, y: int) -> List[List[int]]:
        return self.getBishopMoves(x, y) + self.getRookMoves(x, y)

    def getKingMoves(self, x: int, y: int) -> List[List[int]]:
        piece = self.getPiece(x, y)
        kingShifts = [(1, 1), (-1, 1), (1, -1), (-1, -1),
                      (1, 0), (-1, 0), (0, 1), (0, -1)]

        moves = [[x + dx, y + dy]
                 for dx, dy in kingShifts
                 if 0 <= x + dx < 8 and 0 <= y + dy < 8
                 and (self.getPiece(x + dx, y + dy) == '.'
                 or self.getPiece(x + dx, y + dy).isupper()
                 != piece.isupper())]

        return moves

    # ----------------------
    # Piece moving (special)
    # ----------------------

    def isSquareAttacked(self, x: int, y: int, isLight: bool) -> bool:
        iAttacked = any([x, y] in self.getPossibleMoves(attackX, attackY)
                        for attackX, attackY in itertools.product(range(8),
                                                                  range(8))
                        if self.getPiece(attackX, attackY) != '.'
                        and self.getPiece(attackX, attackY).isupper()
                        != isLight)

        return iAttacked

    def isInCheck(self, isLight: bool) -> Tuple[int, int, bool]:
        kingX, kingY = self.getKingPos(isLight)

        return kingX, kingY, self.isSquareAttacked(kingX, kingY, isLight)

    def isCheck(self, side: str) -> Tuple[int, int, bool]:
        isLight = (self.activePlayer == side)

        return self.isInCheck(not isLight)

    def isCheckmate(self, isLight: bool) -> bool:
        if not self.isInCheck(isLight)[2]:
            return False

        isCheckmate = not any(self.getLegalMoves(x, y)
                              for x, y in itertools.product(range(8), range(8))
                              if self.getPiece(x, y) != '.'
                              and self.getPiece(x, y).isupper() == isLight)

        return isCheckmate

    def isEnPassant(self) -> Tuple[bool, Optional[Tuple[int, int]]]:
        enPassantPerformed = self.enPassantPerformed
        target = self.enPassantTarget

        if enPassantPerformed:
            self.enPassantPerformed = False
            self.enPassantTarget = None

        return enPassantPerformed, target

    def isCastling(self) -> Tuple[bool, Optional[Tuple[int, int]]]:
        castlingPerformed = self.castlingPerformed
        castlingRookPos = self.castlingRookPos

        if castlingPerformed:
            self.castlingPerformed = False
            self.castlingRookPos = None

        return castlingPerformed, castlingRookPos

    def isPromotion(self, x: int, y: int,
                    x0: Optional[int] = None,
                    y0: Optional[int] = None) -> bool:
        piece = self.getPiece(x, y) \
            if (x0, y0) == (None, None) else self.getPiece(x0, y0)

        if (piece == "P" and y == 0) or (piece == "p" and y == 7):
            return True

        return False

    def promotePawn(self, x: int, y: int, newPieceName: str) -> None:
        piece = self.getPiece(x, y)
        newPieceName = newPieceName.upper() \
            if piece.isupper() else newPieceName.lower()
        self.promotionPiece = newPieceName

        self.setPiece(x, y, newPieceName)

    def getCastlingMoves(self, x: int, y: int) -> List[List[int]]:
        king = self.getPiece(x, y)
        kingSide = "light" if king.isupper() else "dark"
        moves = []

        # Check if the king has already been moved
        if self.castling[kingSide]['kingMoved']:
            return moves

        isLight = (kingSide == "light")

        if not self.castling[kingSide]['leftRookMoved']:
            if self.isPathClear(x, y, "left") \
                    and not self.isKingCrossingAttackedSquares(x, y, "left",
                                                               isLight):
                moves.append([x - 2, y])

        if not self.castling[kingSide]['rightRookMoved']:
            if self.isPathClear(x, y, "right") \
                    and not self.isKingCrossingAttackedSquares(x, y, "right",
                                                               isLight):
                moves.append([x + 2, y])

        return moves

    def isPathClear(self, x: int, y: int, direction: str) -> bool:
        if direction == "left":
            return all(self.getPiece(i, y) == '.' for i in range(x - 1, 0, -1))
        elif direction == "right":
            return all(self.getPiece(i, y) == '.' for i in range(x + 1, 7))

    def isKingCrossingAttackedSquares(self, x: int, y: int,
                                      direction: str, isLight: bool) -> bool:
        if direction == "left":
            return self.isSquareAttacked(x, y, isLight) \
                   or self.isSquareAttacked(x - 1, y, isLight) \
                   or self.isSquareAttacked(x - 2, y, isLight)
        elif direction == "right":
            return self.isSquareAttacked(x, y, isLight) \
                   or self.isSquareAttacked(x + 1, y, isLight) \
                   or self.isSquareAttacked(x + 2, y, isLight)

    # ------------------------
    # Algebraic notation block
    # ------------------------

    def parseMove(self, moveText: str) \
            -> Union[None, str, Tuple[int, int, int, int, Optional[str]]]:
        # Remove spaces from text
        moveText = moveText.strip()

        # Check for castling combination
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
        pattern = re.compile(
            r"^([RNBQK]?)([a-h]?)([1-8]?)([x]?)([a-h][1-8])(=?[qrbnQRBN]?)$")
        match = pattern.match(moveText)

        # Check if the analysis failed
        if not match:
            return None

        # Get data from matching results
        piece, file, rank, capture, end, promotionPiece = match.groups()
        endX, endY = ord(end[0]) - ord('a'), 8 - int(end[1])

        # Check if there is no capture to perform
        if capture and self.getPiece(endX, endY) == '.' \
                and not self.enPassantTarget:
            return self.getError(10)

        # Check if no piece type is specified - it is about pawns (e.g. 'e4')
        if not piece:
            piece = 'P' if self.activePlayer == 'light' else 'p'

        # 'Resize' piece name
        if self.activePlayer == 'dark':
            piece = piece.lower()

        # Find the position of all player pieces of a given type
        piecePositions = self.findPiecesXY(piece)
        if not piecePositions:
            return self.getError(3)

        # Find possible piece positions
        possiblePositions = [
            (x, y) for x, y in piecePositions
            if [endX, endY] in self.getLegalMoves(x, y)
        ]

        # Check for unambiguous moves
        isUnambiguous, startX, startY = self.isMoveUnambiguous(
            possiblePositions, file, rank)
        if not isUnambiguous:
            return self.getError(4 if len(possiblePositions) > 1 else 5)

        # Check for promotion piece
        if promotionPiece:
            promotionPiece = promotionPiece[1].lower() \
                if self.getPiece(startX, startY).islower() else \
                promotionPiece[1].upper()
        else:
            promotionPiece = None

        return startX, startY, endX, endY, promotionPiece

    @staticmethod
    def isMoveUnambiguous(piecePositions: Sequence[Tuple[int, int]],
                          file: str, rank: str) \
            -> Tuple[bool, Optional[int], Optional[int]]:
        unambiguousPositions = [
            (x, y) for x, y in piecePositions if
            (not file or x == ord(file) - ord('a')) and
            (not rank or y == 8 - int(rank))
        ]

        startPos = unambiguousPositions[0] \
            if unambiguousPositions else (None, None)

        return len(unambiguousPositions) == 1, startPos[0], startPos[1]

    def coordsToSAN(self, startX, startY, newX, newY, promotionPiece=None):
        piece = self.getPiece(startX, startY)
        pieceType = piece.upper()

        pieceLetter = '' if pieceType == 'P' else pieceType
        capture = 'x' \
            if self.getPiece(newX, newY) != '.' \
            or self.enPassantPerformed else ''
        file = chr(ord('a') + startX)
        rank = str(8 - startY)
        endSquare = chr(ord('a') + newX) + str(8 - newY)

        if pieceType == 'K' and abs(newX - startX) == 2:
            return 'O-O' if newX > startX else 'O-O-O'

        if pieceType == 'P':
            sanMove = file + capture + endSquare if capture else endSquare
        else:
            possiblePositions = [(x, y) for x, y in self.findPiecesXY(piece)
                                 if [newX, newY] in self.getLegalMoves(x, y)]

            if len(possiblePositions) > 1:  # Unambiguous moves
                sameFilePositions = [pos for pos in possiblePositions
                                     if pos[0] == startX]
                sameRankPositions = [pos for pos in possiblePositions
                                     if pos[1] == startY]

                if len(sameFilePositions) == 1:
                    pieceLetter += file
                elif len(sameRankPositions) == 1:
                    pieceLetter += rank
                else:
                    pieceLetter += file
                    pieceLetter += rank

            sanMove = pieceLetter + capture + endSquare

        if self.enPassantPerformed:
            sanMove += 'ep'

        if self.promotionPiece:
            sanMove += '=' + self.promotionPiece.upper()

        if promotionPiece:
            sanMove += '=' + promotionPiece.upper()

        return sanMove
