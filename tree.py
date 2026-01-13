import sys
import pickle
import numpy as np
from sklearn.tree import DecisionTreeClassifier

# --- 기존 로직 (Feature Extraction) ---
def get_lines_passing_through(idx):
    all_lines = [
        [0,1,2], [3,4,5], [6,7,8], # 가로
        [0,3,6], [1,4,7], [2,5,8], # 세로
        [0,4,8], [2,4,6]           # 대각선
    ]
    return [line for line in all_lines if idx in line]

def get_advanced_raw_features(board_str, move_idx, player):
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
            
    return [intersecting_count, my_2_lines, opp_2_lines, my_1_lines, opp_1_lines]

# --- 시각화 도구 ---
def print_error_case(board_str, move_idx, features, true_label, pred_label, case_type):
    print(f"\n[{case_type}] ------------------------------------------------")
    
    # 보드 시각화
    display = list(board_str)
    # 현재 두려는 위치를 '?'로 표시
    display[move_idx] = '?'
    
    print(f"Board State (Player: {'X' if board_str.count('X') == board_str.count('O') else 'O'})")
    print(f" {display[0]} | {display[1]} | {display[2]} ")
    print("-----------")
    print(f" {display[3]} | {display[4]} | {display[5]} ")
    print("-----------")
    print(f" {display[6]} | {display[7]} | {display[8]} ")
    
    print("\n🔍 AI가 본 세상 (Raw Features):")
    print(f" - 교차 선 개수 (Geometry): {features[0]} {'(중앙)' if features[0]==4 else '(구석)' if features[0]==3 else '(변)'}")
    print(f" - 내 킬각 (My_Win)       : {features[1]}")
    print(f" - 방어 (Opp_Win)         : {features[2]}")
    print(f" - 내 포크 빌드 (My_Fork) : {features[3]}")
    print(f" - 쟤 포크 빌드 (Opp_Fork): {features[4]}")
    
    print(f"\n결과 분석:")
    if case_type == "놓친 수 (False Negative)":
        print(f"❌ AI 생각: \"여기 별로야..\" (Pred: 0)")
        print(f"✅ 실제 정답: \"여기 무조건 둬야 해!\" (True: 1)")
    else:
        print(f"❌ AI 생각: \"여기 개꿀인데?\" (Pred: 1)")
        print(f"✅ 실제 정답: \"거기 두면 망해!\" (True: 0)")

def visualize_failures():
    print("🔬 Analyzing Failures...")
    
    try:
        with open('perfect_lookup_table.pkl', 'rb') as f:
            lookup_table = pickle.load(f)
    except FileNotFoundError:
        print("룩업 테이블 없음")
        return

    X = []; y = []; meta_info = []

    # 데이터 준비
    for state, best_moves in lookup_table.items():
        current_player = 'X' if state.count('X') == state.count('O') else 'O'
        possible_moves = [i for i, c in enumerate(state) if c == ' ']
        
        for move in possible_moves:
            feats = get_advanced_raw_features(state, move, current_player)
            is_best = 1 if move in best_moves else 0
            
            X.append(feats)
            y.append(is_best)
            meta_info.append((state, move))

    # 학습
    dt = DecisionTreeClassifier(max_depth=6, random_state=42)
    dt.fit(X, y)
    
    predictions = dt.predict(X)
    
    # 틀린 것만 수집
    fn_count = 0 # 놓친 수
    fp_count = 0 # 틀린 수
    
    print("\n" + "="*60)
    print("🚨 ERROR REPORT: 왜 81%인가?")
    print("="*60)
    
    for i in range(len(predictions)):
        if predictions[i] != y[i]:
            state, move = meta_info[i]
            feats = X[i]
            
            # 케이스 1: 놓친 수 (보여줄 가치가 높음)
            if predictions[i] == 0 and y[i] == 1:
                if fn_count < 3: # 3개만 보여줌
                    print_error_case(state, move, feats, y[i], predictions[i], "놓친 수 (False Negative)")
                fn_count += 1
            
            # 케이스 2: 틀린 수
            elif predictions[i] == 1 and y[i] == 0:
                if fp_count < 3:
                    print_error_case(state, move, feats, y[i], predictions[i], "틀린 수 (False Positive)")
                fp_count += 1
                
    print("\n" + "="*60)
    print(f"총 분석 결과:")
    print(f" - AI가 정답인데 겁먹고 안 둔 경우: {fn_count}개")
    print(f" - AI가 오답인데 좋다고 둔 경우: {fp_count}개")
    print("="*60)

if __name__ == "__main__":
    visualize_failures()