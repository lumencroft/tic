import sys
import pickle
import numpy as np
from sklearn.tree import DecisionTreeClassifier

# --- 1. 기능 정의 (이전 코드와 동일한 로직 유지) ---
def get_lines_passing_through(idx):
    all_lines = [
        [0,1,2], [3,4,5], [6,7,8], # 가로
        [0,3,6], [1,4,7], [2,5,8], # 세로
        [0,4,8], [2,4,6]           # 대각선
    ]
    return [line for line in all_lines if idx in line]

def get_global_context(board_str, player):
    possible_wins = 0
    possible_moves = [i for i, c in enumerate(board_str) if c == ' ']
    for move in possible_moves:
        lines = get_lines_passing_through(move)
        for line in lines:
            others = [board_str[i] for i in line if i != move]
            if others.count(player) == 2 and others.count(' ') == 0:
                possible_wins += 1
                break
    return 1 if possible_wins > 0 else 0

def get_final_features(board_str, move_idx, player, global_win_exist):
    opponent = 'O' if player == 'X' else 'X'
    lines = get_lines_passing_through(move_idx)
    
    intersecting_count = len(lines)
    my_2_lines = 0; opp_2_lines = 0; my_1_lines = 0; opp_1_lines = 0
    
    for line in lines:
        others = [board_str[i] for i in line if i != move_idx]
        my_cnt = others.count(player)
        opp_cnt = others.count(opponent)
        
        if my_cnt == 2 and opp_cnt == 0: my_2_lines += 1
        elif opp_cnt == 2 and my_cnt == 0: opp_2_lines += 1
        elif my_cnt == 1 and opp_cnt == 0: my_1_lines += 1
        elif opp_cnt == 1 and my_cnt == 0: opp_1_lines += 1
            
    return [intersecting_count, my_2_lines, opp_2_lines, my_1_lines, opp_1_lines, global_win_exist]

# --- 2. 시각화 로직 ---
def visualize_error(state, move_idx, feats, true_y, pred_y, error_type, count):
    player = 'X' if state.count('X') == state.count('O') else 'O'
    board = list(state)
    board[move_idx] = '?' # AI가 고민한 자리
    
    print(f"\n[{count}] {error_type} ===================================")
    print(f" Turn: {player}")
    print(f" {board[0]} | {board[1]} | {board[2]} ")
    print("-----------")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("-----------")
    print(f" {board[6]} | {board[7]} | {board[8]} ")
    
    # 특징 해석
    geo_map = {4: "중앙", 3: "구석", 2: "변"}
    geo_str = geo_map.get(feats[0], "기타")
    
    print(f"\n🔎 AI의 판단 근거 (Features):")
    print(f" 1. 위치: {geo_str} (선 {feats[0]}개 교차)")
    print(f" 2. 내 킬각 (Me_Win)  : {feats[1]}")
    print(f" 3. 적 킬각 (Op_Win)  : {feats[2]}")
    print(f" 4. 내 포크 (Me_Fork) : {feats[3]}")
    print(f" 5. 적 포크 (Op_Fork) : {feats[4]}  <-- 위험 요소")
    print(f" 6. 딴데 킬각(Global) : {'있음' if feats[5] else '없음'}")
    
    if error_type == "False Negative":
        print(f"\n❌ AI 결론: \"여기 별로야..\" (Pred: 0)")
        print(f"✅ 실제 정답: \"여기 둬야 해!\" (True: 1)")
        print(" -> 분석: 왜 AI는 이 좋은 수를 놓쳤을까? (특수 오프닝? 강제수?)")
    else:
        print(f"\n❌ AI 결론: \"여기 좋아!\" (Pred: 1)")
        print(f"✅ 실제 정답: \"거긴 아니야.\" (True: 0)")
        print(" -> 분석: AI가 '내 포크'나 '위치'만 보고 설레발 친 경우일 수 있음.")

def analyze_all_errors():
    print("🕵️‍♀️ Analyzing Logic Failures...")
    
    try:
        with open('perfect_lookup_table.pkl', 'rb') as f:
            lookup_table = pickle.load(f)
    except FileNotFoundError:
        print("룩업 테이블 없음")
        return

    X = []; y = []; meta = []

    # 데이터 준비
    for state, best_moves in lookup_table.items():
        current_player = 'X' if state.count('X') == state.count('O') else 'O'
        global_win = get_global_context(state, current_player)
        possible_moves = [i for i, c in enumerate(state) if c == ' ']
        
        for move in possible_moves:
            feats = get_final_features(state, move, current_player, global_win)
            is_best = 1 if move in best_moves else 0
            
            X.append(feats)
            y.append(is_best)
            meta.append((state, move))

    # 학습 및 예측
    dt = DecisionTreeClassifier(max_depth=7, random_state=42)
    dt.fit(X, y)
    predictions = dt.predict(X)
    
    # 틀린 것 출력
    fn_count = 0
    fp_count = 0
    max_show = 10  # 너무 많이 보면 어지러우니까 타입별로 10개씩만 보자
    
    print("\n🚨 [False Positive: 틀렸는데 좋다고 한 것] (Top 10)")
    for i in range(len(predictions)):
        if predictions[i] == 1 and y[i] == 0:
            if fp_count < max_show:
                visualize_error(meta[i][0], meta[i][1], X[i], y[i], predictions[i], "False Positive", fp_count+1)
            fp_count += 1
            
    print("\n" + "="*60)
    print("\n🚨 [False Negative: 정답인데 겁먹고 안 둔 것] (Top 10)")
    for i in range(len(predictions)):
        if predictions[i] == 0 and y[i] == 1:
            if fn_count < max_show:
                visualize_error(meta[i][0], meta[i][1], X[i], y[i], predictions[i], "False Negative", fn_count+1)
            fn_count += 1

    print("\n" + "="*60)
    print(f"총 분석 결과:")
    print(f" - 정답 놓침 (False Negative): {fn_count}개")
    print(f" - 오답 선택 (False Positive): {fp_count}개")
    print(f" - 전체 정확도: {accuracy_score(y, predictions)*100:.2f}%")
    print("="*60)

# accuracy_score import 추가 필요
from sklearn.metrics import accuracy_score

if __name__ == "__main__":
    analyze_all_errors()