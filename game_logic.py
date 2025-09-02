# --- 틱택토 게임 로직만 분리 ---

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
