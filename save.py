import pickle
import csv

class TicTacToeSolver:
    def __init__(self):
        # Key: Board State, Value: { 'Win': [], 'Draw': [], 'Lose': [] }
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
        # 점수 계산: 빨리 이길수록(+), 늦게 질수록(-) 좋음
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

        # --- 여기서부터 분류 로직 ---
        move_classification = {'Win': [], 'Draw': [], 'Lose': []}
        
        for m, s in zip(moves, scores):
            if is_maximizing: # 내 차례 (X)
                if s > 0: move_classification['Win'].append(m)
                elif s == 0: move_classification['Draw'].append(m)
                else: move_classification['Lose'].append(m)
                best_score = max(scores)
            else: # 상대 차례 (O) - O 입장에서는 점수가 낮아야 이기는 것
                if s < 0: move_classification['Win'].append(m) # O 승리
                elif s == 0: move_classification['Draw'].append(m)
                else: move_classification['Lose'].append(m) # O 패배 (X 승리)
                best_score = min(scores)

        # 상태별로 3가지 분류를 모두 저장 (단, 게임이 끝난 상태는 저장 안 함)
        if possible_moves:
            self.policy[state_key] = move_classification
        
        return best_score

    def solve_and_save(self):
        print("모든 수를 승/무/패로 분류하여 분석 시작... ♡")
        initial_board = [' '] * 9
        self.minimax(initial_board, 0, True) 
        
        print(f"분석 끝! 총 {len(self.policy)}개의 상태 분류 완료.")

        # 1. 피클로 저장 (딕셔너리 구조 유지)
        with open('tictactoe_classified_moves.pkl', 'wb') as f:
            pickle.dump(self.policy, f)

        # 2. CSV로 저장 (눈으로 보기 좋게)
        with open('tictactoe_classified_moves.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Board_State', 'Win_Moves', 'Draw_Moves', 'Lose_Moves'])
            
            for state, classification in self.policy.items():
                win_str = " ".join(map(str, classification['Win']))
                draw_str = " ".join(map(str, classification['Draw']))
                lose_str = " ".join(map(str, classification['Lose']))
                
                writer.writerow([state, win_str, draw_str, lose_str])
                
        print(" -> 완벽하게 분류된 데이터셋 완성! (Lose 데이터가 핵심이야)")

# 실행
solver = TicTacToeSolver()
solver.solve_and_save()