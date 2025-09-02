import cv2
import numpy as np

# --- 1. 보드 상태 변환 함수 ---
def normalize_board(board_str):
    """다양한 길이의 보드 상태를 9자리 문자열로 변환"""
    if len(board_str) == 9:
        return board_str
    
    # 9자리로 패딩 (뒤에 공백 추가)
    normalized = board_str.ljust(9, ' ')
    return normalized

# --- 2. 미니맥스 알고리즘 ---
def check_win(board_str):
    if len(board_str) != 9: return None
    b = list(board_str)
    lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for line in lines:
        if b[line[0]] == b[line[1]] == b[line[2]] and b[line[0]] != ' ':
            return b[line[0]]
    if ' ' not in b: return 'draw'
    return None

def get_turn(board_str):
    return 'O' if board_str.count('X') > board_str.count('O') else 'X'

def minimax(board_str, player, depth=0):
    """완전한 미니맥스 알고리즘 - 모든 가능한 게임 트리를 탐색"""
    winner = check_win(board_str)
    if winner:
        if winner == 'X': 
            return 100 - depth, []  # X 승리: 깊이에 따라 점수 차등
        elif winner == 'O': 
            return -100 + depth, []  # O 승리: 깊이에 따라 점수 차등
        else: 
            return 0, []  # 무승부

    moves = [i for i, char in enumerate(board_str) if char == ' ']
    if not moves:
        return 0, []  # 더 이상 둘 수 없으면 무승부
        
    best_moves = []
    if player == 'X':
        best_score = -float('inf')
        for move in moves:
            next_board_list = list(board_str)
            next_board_list[move] = 'X'
            score, _ = minimax("".join(next_board_list), 'O', depth + 1)
            if score > best_score: 
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
    else:
        best_score = float('inf')
        for move in moves:
            next_board_list = list(board_str)
            next_board_list[move] = 'O'
            score, _ = minimax("".join(next_board_list), 'X', depth + 1)
            if score < best_score: 
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
    return best_score, best_moves

def find_best_moves(board_str):
    if check_win(board_str): return []
    player = get_turn(board_str)
    _, best_moves = minimax(board_str, player)
    return best_moves

# --- 2. OpenCV 시각화 (이전과 동일) ---
def draw_board(state, best_moves):
    img = np.full((300, 300, 3), 240, dtype=np.uint8)
    for i in range(1, 3):
        cv2.line(img, (i * 100, 0), (i * 100, 300), (0, 0, 0), 2)
        cv2.line(img, (0, i * 100), (300, i * 100), (0, 0, 0), 2)

    for i, char in enumerate(state):
        if char == ' ': continue
        row, col = i // 3, i % 3
        center_x, center_y = col * 100 + 50, row * 100 + 50
        if char == 'X':
            cv2.line(img, (center_x-30, center_y-30), (center_x+30, center_y+30), (0,0,0), 4)
            cv2.line(img, (center_x+30, center_y-30), (center_x-30, center_y+30), (0,0,0), 4)
        else:
            cv2.circle(img, (center_x, center_y), 30, (0,0,0), 4)

    # 모든 최적의 수를 빨간색으로 표시
    if best_moves:
        player = get_turn(state)
        for best_move_idx in best_moves:
            row, col = best_move_idx // 3, best_move_idx % 3
            center_x, center_y = col * 100 + 50, row * 100 + 50
            if player == 'X':
                cv2.line(img, (center_x-30, center_y-30), (center_x+30, center_y+30), (0,0,255), 4)
                cv2.line(img, (center_x+30, center_y-30), (center_x-30, center_y+30), (0,0,255), 4)
            else:
                cv2.circle(img, (center_x, center_y), 30, (0,0,255), 4)
    return img

# --- 3. 메인 로직 ---
try:
    with open('unique_states.txt', 'r', encoding='utf-8') as f:
        states = [line.strip() for line in f.readlines() if line.strip()]
    print(f"파일에서 성공적으로 로드한 상태의 수: {len(states)}")
except FileNotFoundError:
    print("오류: 'unique_states.txt' 파일을 찾을 수 없습니다."); exit()
if not states:
    print("오류: 'unique_states.txt' 파일에서 유효한 상태를 찾을 수 없습니다."); exit()

current_idx = 0
print("OpenCV 창이 뜨면 'n' 키를 눌러 다음 상태를 확인하세요. 'q' 키로 종료합니다.")

while True:
    state = states[current_idx]
    normalized_state = normalize_board(state)
    best_moves = find_best_moves(normalized_state)
    board_image = draw_board(normalized_state, best_moves)
    
    # 상태 정보 텍스트 (State x / 765)
    info_text = f"State {current_idx + 1} / {len(states)}"
    cv2.putText(board_image, info_text, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)

    # 코드가 판단한 현재 게임 상태를 화면에 직접 표시
    winner = check_win(normalized_state)
    if winner == 'X': status_text = "Status: X Wins"
    elif winner == 'O': status_text = "Status: O Wins"
    elif winner == 'draw': status_text = "Status: Draw"
    else: status_text = "Status: In Progress"
    cv2.putText(board_image, status_text, (5, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    cv2.imshow("Tic-Tac-Toe Best Move", board_image)

    key = cv2.waitKey(0) & 0xFF
    if key == ord('n'):
        current_idx = (current_idx + 1) % len(states)
    elif key == ord('q'):
        break

cv2.destroyAllWindows()