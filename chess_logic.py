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

    def getPiecesByColor(self, isWhite):
        pieces = 0

        for piece, pos in self.pieces.items():
            if piece.isupper() == isWhite:
                pieces |= pos

        return pieces

    def getAllPieces(self):
        pieces = 0

        for pos in self.pieces.values():
            pieces |= pos

        return pieces

    def movePiece(self, piece, oldPos, newPos):
        self.removePiece(piece, oldPos)
        self.setPiece(piece, newPos)

    def removePiece(self, piece, pos):
        self.pieces[piece] &= ~pos

    # ----------------------------------------------------------

    def getPossibleMoves(self, piece, x, y):
        if piece.lower() == 'p':
            return self.getPawnMoves(piece, x, y)
        # elif piece.lower() == 'r':
        #     return self.get_rook_moves(piece)
        # ...

        return 0

    def getPawnMoves(self, piece, x, y):
        moves = []

        moveDir = 1 if piece.islower() else -1
        enPassantRank = 5 if piece.islower() else 2

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
