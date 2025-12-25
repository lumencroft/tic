import numpy as np
import matplotlib.pyplot as plt
import os
from collections import deque

# ==========================================
# 1. 엔진 및 유틸리티
# ==========================================
def check_winner(board):
    lines = [
        board[0,:], board[1,:], board[2,:], 
        board[:,0], board[:,1], board[:,2], 
        np.diag(board), np.diag(np.fliplr(board))
    ]
    for line in lines:
        if abs(sum(line)) == 3: return 1 if sum(line) == 3 else -1
    return 0

def is_full(board):
    return not np.any(board == 0)

def get_canonical_tuple(board):
    # 대칭 제거용 대표 ID 생성
    transformations = []
    curr = board.copy()
    for _ in range(4):
        transformations.append(tuple(curr.flatten()))
        transformations.append(tuple(np.fliplr(curr).flatten()))
        curr = np.rot90(curr)
    return min(transformations)

# ==========================================
# 2. 지능형 Minimax (빨리 이기는 것을 선호)
# ==========================================
memo = {}

def minimax_depth(board, player, depth):
    state_tuple = (tuple(board.flatten()), player)
    if state_tuple in memo: return memo[state_tuple]
    
    winner = check_winner(board)
    # ★ 핵심 수정: 깊이(depth)를 점수에 반영 ★
    # 빨리 이기면(depth가 작으면) 더 큰 양수, 늦게 이기면 작은 양수
    # 빨리 지면 더 큰 음수, 늦게 지면 작은 음수
    # 기본 점수 10점에서 depth를 뺌
    if winner == player: return 10 - depth
    if winner == -player: return depth - 10
    if is_full(board): return 0
    
    best_score = -float('inf')
    rows, cols = np.where(board == 0)
    
    for r, c in zip(rows, cols):
        board[r, c] = player
        # 상대방은 자신의 입장에서 최선의 점수를 냄 -> 나에겐 마이너스
        score = -minimax_depth(board, -player, depth + 1)
        board[r, c] = 0
        best_score = max(best_score, score)
        
    memo[state_tuple] = best_score
    return best_score

# ==========================================
# 3. BFS 기반 상태 생성 (합법적인 판만 생성)
# ==========================================
def generate_legal_states_bfs():
    print("BFS 방식으로 처음부터 합법적인 판만 생성 중... (버그 원천 봉쇄)")
    # 큐: (보드 상태, 다음 둘 플레이어)
    queue = deque([(np.zeros((3, 3), dtype=int), 1)])
    seen_canonicals = set()
    dataset = []
    
    empty_board_tuple = get_canonical_tuple(np.zeros((3, 3), dtype=int))
    seen_canonicals.add(empty_board_tuple)

    while queue:
        board, current_player = queue.popleft()
        
        # 이미 승패가 결정난 판은 더 진행 안 함 (하지만 데이터셋에는 포함)
        if check_winner(board) != 0 or is_full(board):
            continue

        # --- 현재 상태에서 최적의 수 계산 ---
        rows, cols = np.where(board == 0)
        if len(rows) == 0: continue

        optimal_moves = []
        best_val = -float('inf')
        
        # 1차적으로 모든 수의 점수 계산
        move_scores = []
        for r, c in zip(rows, cols):
            board[r, c] = current_player
            # depth 1부터 시작
            score = -minimax_depth(board, -current_player, 1)
            board[r, c] = 0
            move_scores.append(((r,c), score))
            best_val = max(best_val, score)
        
        # 최고점수와 같은 수만 정답으로 인정
        for move, score in move_scores:
            if score == best_val:
                optimal_moves.append(move)

        # 데이터셋에 저장 (승패가 안 난 상태만 저장)
        dataset.append({
            'board': board.copy(),
            'player': current_player,
            'optimal_moves': optimal_moves
        })
        
        # --- 다음 상태 탐색 (자식 노드 생성) ---
        for r, c in zip(rows, cols):
            next_board = board.copy()
            next_board[r, c] = current_player
            
            canon = get_canonical_tuple(next_board)
            if canon not in seen_canonicals:
                # 승패가 아직 안 났으면 큐에 추가해서 계속 진행
                if check_winner(next_board) == 0 and not is_full(next_board):
                     queue.append((next_board, -current_player))
                seen_canonicals.add(canon)
                
    return dataset

# ==========================================
# 4. 이미지 저장
# ==========================================
def save_images(dataset):
    save_dir = "tic_tac_toe_final_audit"
    if os.path.exists(save_dir):
        import shutil
        shutil.rmtree(save_dir) # 기존 폴더 삭제 후 재생성
    os.makedirs(save_dir, exist_ok=True)
    
    print(f"'{save_dir}' 폴더에 이미지 저장 시작. (약 {len(dataset)}장 예상)")

    for idx, data in enumerate(dataset):
        board = data['board']
        player = data['player']
        optimal_moves = data['optimal_moves']
        
        fig, ax = plt.subplots(figsize=(3, 3))
        ax.set_xlim(0, 3); ax.set_ylim(0, 3)
        ax.set_xticks([0,1,2,3]); ax.set_yticks([0,1,2,3])
        ax.grid(True, color='gray', linewidth=2)
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

        # X/O 개수 검증용
        x_c = np.sum(board==1)
        o_c = np.sum(board==-1)

        for r in range(3):
            for c in range(3):
                x_pos, y_pos = c + 0.5, 2.5 - r
                val = board[r, c]
                
                # 기존 돌 (검정)
                if val == 1: ax.text(x_pos, y_pos, 'X', ha='center', va='center', fontsize=40, color='black', weight='bold')
                elif val == -1: ax.text(x_pos, y_pos, 'O', ha='center', va='center', fontsize=40, color='black', weight='bold')
                
                # 최선의 수 (빨강)
                if val == 0 and (r, c) in optimal_moves:
                    mark = 'X' if player == 1 else 'O'
                    ax.text(x_pos, y_pos, mark, ha='center', va='center', fontsize=40, color='red', weight='bold', alpha=0.8)

        turn_str = "Turn: X" if player == 1 else "Turn: O"
        # 제목에 돌 개수도 같이 표시 (버그 확인사살용)
        plt.title(f"#{idx+1} {turn_str} (X:{x_c}, O:{o_c})", fontsize=9)
        
        plt.savefig(os.path.join(save_dir, f"state_{idx+1:03d}.png"), bbox_inches='tight')
        plt.close(fig)
        
        if (idx+1) % 100 == 0: print(f"{idx+1}장 완료...")

    print(f"저장 끝. 폴더를 확인해주세요. 주인님.")

# 실행
memo = {} # 메모 초기화
data = generate_legal_states_bfs()
print(f"생성된 유효 상태 수: {len(data)}")
save_images(data)