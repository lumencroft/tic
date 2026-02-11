import pickle
import csv

class TicTacToeSolver:
    def __init__(self):
        self.policy = {} 
        
    def check_winner(self, board):
        lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]
        for a, b, c in lines:
            if board[a] == board[b] == board[c] and board[a] != ' ':
                return board[a]
        if ' ' not in board:
            return 'Draw'
        return None

    def minimax(self, board, depth, is_maximizing):
        state_key = "".join(board)
        
        winner = self.check_winner(board)
        if winner == 'X': return 10 - depth  
        if winner == 'O': return -10 + depth 
        if winner == 'Draw': return 0

        scores = []
        moves = []
        
        possible_moves = [i for i, x in enumerate(board) if x == ' ']

        for move in possible_moves:
            board[move] = 'X' if is_maximizing else 'O'
            score = self.minimax(board, depth + 1, not is_maximizing)
            board[move] = ' ' 
            
            scores.append(score)
            moves.append(move)

        if is_maximizing:
            best_score = max(scores) 
        else:
            best_score = min(scores) 

        optimal_moves = [m for m, s in zip(moves, scores) if s == best_score]

        # ★ 수정됨: '모든 수가 같다'는 멍청한 조건 삭제! 
        # 오직 '명백하게 지는 판(패배 확정)'일 때만 빈 배열로 처리!
        if (is_maximizing and best_score < 0) or \
           (not is_maximizing and best_score > 0):
            optimal_moves = []

        self.policy[state_key] = optimal_moves
        
        return best_score

    def solve_and_save(self):
        print("양수걸이를 포기로 착각하는 멍청한 버그 수정 완료... ♡")
        initial_board = [' '] * 9
        self.minimax(initial_board, 0, True) 
        
        print(f"계산 끝! 총 {len(self.policy)}개의 상태 저장 완료.")

        with open('tictactoe_all_moves.pkl', 'wb') as f:
            pickle.dump(self.policy, f)

        with open('tictactoe_all_moves.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Board_State', 'Optimal_Moves'])
            for state, moves in self.policy.items():
                moves_str = " ".join(map(str, moves))
                writer.writerow([state, moves_str])
        print(" -> 완벽하게 정제된 데이터 완성! ♡")

# 실행
solver = TicTacToeSolver()
solver.solve_and_save()