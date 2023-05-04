import numpy as np
import copy


class ChessBot:
    def __init__(self, depth=3):
        self.depth = depth

    def getBotMove(self, logic):
        bestMove, bestValue = self.minimax(logic, self.depth, float('-inf'), float('inf'))
        if bestMove is None:
            return None

        return tuple(bestMove)

    def minimax(self, logic, depth, alpha, beta):
        player = logic.activePlayer
        if depth == 0 or logic.isCheckmate(player != 'light'):
            return None, self.evaluateBoard(logic)

        moves = self.getAllLegalMoves(logic)
        bestMove = None
        if player == 'light':
            maxValue = float('-inf')

            for move in moves:
                newLogic = copy.deepcopy(logic)  # Simulate further playing
                newLogic.movePiece(*move)

                if newLogic.isPromotion(move[2], move[3]):
                    promotePiece = 'q'  # Queen is the most valuable in promotion
                    newLogic.promotePawn(move[2], move[3], promotePiece)
                    move = move + (promotePiece,)

                newLogic.switchActivePlayer()

                _, value = self.minimax(newLogic, depth - 1, alpha, beta)
                if value > maxValue:
                    maxValue = value
                    bestMove = move

                alpha = max(alpha, value)
                if beta <= alpha:
                    break

            return bestMove, maxValue
        else:
            minValue = float('inf')

            for move in moves:
                newLogic = copy.deepcopy(logic)  # Simulate further playing
                newLogic.movePiece(*move)

                if newLogic.isPromotion(move[2], move[3]):
                    promotePiece = 'q'  # Queen is the most valuable in promotion
                    newLogic.promotePawn(move[2], move[3], promotePiece)
                    move = move + (promotePiece,)

                newLogic.switchActivePlayer()

                _, value = self.minimax(newLogic, depth - 1, alpha, beta)
                if value < minValue:
                    minValue = value
                    bestMove = move

                beta = min(beta, value)
                if beta <= alpha:
                    break

            return bestMove, minValue

    @staticmethod
    def getAllLegalMoves(logic):
        player = logic.activePlayer
        pieces = np.where(np.char.isupper(logic.textBoard)) if player == 'light' else np.where(np.char.islower(logic.textBoard))
        moves = [(y, x, move[0], move[1]) for x, y in zip(*pieces) for move in logic.getLegalMoves(y, x)]
        return moves

    @staticmethod
    def evaluateBoard(logic):
        pieceValues = {
            'P': 100, 'p': -100,
            'N': 320, 'n': -320,
            'B': 330, 'b': -330,
            'R': 500, 'r': -500,
            'Q': 900, 'q': -900,
            'K': 0, 'k': 0
        }
        board = logic.textBoard
        unique, counts = np.unique(board, return_counts=True)
        pieceCounts = dict(zip(unique, counts))
        value = sum(pieceValues.get(piece, 0) * count for piece, count in pieceCounts.items())

        return value
