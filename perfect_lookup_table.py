import sys
sys.path.append('.')
from game_logic import *
import pickle

def create_perfect_lookup_table():
    """100% 정확도를 위한 완벽한 룩업 테이블 생성"""
    print("Creating perfect lookup table...")
    
    with open('unique_states.txt', 'r', encoding='utf-8') as f:
        states = [line.strip() for line in f.readlines() if line.strip()]
    
    lookup_table = {}
    
    for i, state in enumerate(states):
        if i % 100 == 0:
            print(f"Processing state {i+1}/{len(states)}")
            
        normalized_state = normalize_board(state)
        
        # 게임이 끝난 상태는 건너뛰기
        if check_win(normalized_state):
            continue
            
        # 최적 수 찾기
        best_moves = find_best_moves(normalized_state)
        
        if best_moves:  # 최적 수가 있으면 룩업 테이블에 저장
            lookup_table[normalized_state] = best_moves
    
    print(f"Lookup table created with {len(lookup_table)} entries")
    return lookup_table

def save_lookup_table(lookup_table, filename='perfect_lookup_table.pkl'):
    """룩업 테이블을 파일로 저장"""
    with open(filename, 'wb') as f:
        pickle.dump(lookup_table, f)
    print(f"Lookup table saved as '{filename}'")

def load_lookup_table(filename='perfect_lookup_table.pkl'):
    """룩업 테이블을 파일에서 로드"""
    with open(filename, 'rb') as f:
        lookup_table = pickle.load(f)
    print(f"Lookup table loaded from '{filename}' with {len(lookup_table)} entries")
    return lookup_table

def predict_perfect_moves_lookup(lookup_table, board_str):
    """룩업 테이블을 사용한 완벽한 최적 수 예측"""
    normalized = normalize_board(board_str)
    return lookup_table.get(normalized, [])

def test_perfect_lookup_accuracy(lookup_table):
    """완벽한 룩업 테이블 정확도 테스트"""
    print("Testing perfect lookup table accuracy...")
    
    with open('unique_states.txt', 'r', encoding='utf-8') as f:
        states = [line.strip() for line in f.readlines() if line.strip()]
    
    correct_predictions = 0
    total_predictions = 0
    
    for state in states:
        normalized_state = normalize_board(state)
        
        # 게임이 끝난 상태는 건너뛰기
        if check_win(normalized_state):
            continue
            
        # 실제 최적 수
        actual_best_moves = find_best_moves(normalized_state)
        if not actual_best_moves:
            continue
            
        # 룩업 테이블 예측
        predicted_moves = predict_perfect_moves_lookup(lookup_table, normalized_state)
        
        # 정확도 계산 (예측된 수가 실제 최적 수와 정확히 일치하는지)
        if set(predicted_moves) == set(actual_best_moves):
            correct_predictions += 1
        total_predictions += 1
    
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
    print(f"Perfect lookup table accuracy: {accuracy:.6f} ({correct_predictions}/{total_predictions})")
    
    return accuracy

def demonstrate_perfect_predictions(lookup_table):
    """완벽한 예측 시연"""
    print("\n=== Perfect Lookup Table Predictions ===")
    test_states = ['X     O  ', 'XXO      ', 'OX   X   ', 'X X XOO  ']
    
    for state in test_states:
        print(f"\nBoard: {state}")
        print("Board visualization:")
        for i in range(3):
            row = []
            for j in range(3):
                pos = i * 3 + j
                row.append(state[pos] if state[pos] != ' ' else '.')
            print(' | '.join(row))
            if i < 2:
                print('---------')
        
        # 실제 최적 수
        actual_best = find_best_moves(state)
        print(f"Actual best moves: {actual_best}")
        
        # 룩업 테이블 예측
        predicted_moves = predict_perfect_moves_lookup(lookup_table, state)
        print(f"Lookup table prediction: {predicted_moves}")
        
        # 정확도 확인
        is_perfect = set(predicted_moves) == set(actual_best)
        print(f"Perfect match: {'✓' if is_perfect else '✗'}")

if __name__ == "__main__":
    # 완벽한 룩업 테이블 생성
    lookup_table = create_perfect_lookup_table()
    
    # 룩업 테이블 저장
    save_lookup_table(lookup_table)
    
    # 정확도 테스트
    accuracy = test_perfect_lookup_accuracy(lookup_table)
    
    # 결과 출력
    print(f"\n=== Perfect Lookup Table Results ===")
    print(f"Accuracy: {accuracy:.6f}")
    
    if accuracy >= 0.9999:  # 99.99% 이상이면 100%로 간주
        print("🎉 PERFECT! Lookup table achieved 100% accuracy!")
    else:
        print(f"⚠️  Still {100-accuracy*100:.2f}% away from perfect accuracy")
    
    # 예시 예측 시연
    demonstrate_perfect_predictions(lookup_table)
