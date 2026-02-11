import pickle
import itertools

def load_data(filename='tictactoe_all_moves.pkl'):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def is_superset_of_existing(current_causes, current_pattern, turn, target, minimal_rules):
    for rule in minimal_rules:
        if rule['target'] != target: continue
        if rule['turn'] != turn: continue
        
        old_causes_set = set(rule['cause_indices'])
        current_causes_set = set(current_causes)
        
        if not old_causes_set.issubset(current_causes_set): continue
        
        match = True
        for old_idx, old_val in zip(rule['cause_indices'], rule['cause_pattern']):
            curr_pos = current_causes.index(old_idx)
            if current_pattern[curr_pos] != old_val:
                match = False
                break
        
        if match:
            return True 
    return False

def trace_specific_14_boards(policy):
    print("응... 지시한 대로 Pass 3에서 [1:O, 3:O -> 8] 규칙의 14개 보드만 출력할게... ♡\n")
    
    active_pairs = set()
    for state, moves in policy.items():
        empty_count = state.count(' ')
        if empty_count <= 1: continue
        if len(moves) == empty_count: continue # 모든 곳이 정답인 판 제외
        for m in moves:
            active_pairs.add((state, m))

    global_minimal_rules = [] 
    cause_k = 2 # Step 3 (원인 2개)

    pass_num = 1
    while True:
        new_rules_this_pass = []
        indices_combinations = list(itertools.combinations(range(9), cause_k))
        
        for indices in indices_combinations:
            remaining_cells = [i for i in range(9) if i not in indices]
            
            seen_configs = set()
            for state in policy.keys():
                empty_count = state.count(' ')
                if empty_count <= 1: continue
                if len(policy[state]) == empty_count: continue 
                
                pat = tuple(state[i] for i in indices)
                turn = 'X' if state.count('X') == state.count('O') else 'O'
                seen_configs.add((pat, turn))

            for pattern, turn in seen_configs:
                for target in remaining_cells:
                    
                    if is_superset_of_existing(indices, pattern, turn, target, global_minimal_rules):
                        continue
                        
                    matching_pairs = []
                    is_100_pct = True
                    
                    for state, moves in policy.items():
                        empty_count = state.count(' ')
                        if empty_count <= 1: continue
                        if len(moves) == empty_count: continue 
                        
                        if not any((state, m) in active_pairs for m in moves):
                            continue
                            
                        current_turn = 'X' if state.count('X') == state.count('O') else 'O'
                        if current_turn != turn: continue
                        
                        current_pat = tuple(state[i] for i in indices)
                        if current_pat != pattern: continue
                        
                        if state[target] != ' ': continue
                        
                        if target not in moves:
                            is_100_pct = False
                            break 
                            
                        if (state, target) in active_pairs:
                            matching_pairs.append((state, target))
                    
                    if not is_100_pct or len(matching_pairs) < 2:
                        continue
                        
                    first_state = matching_pairs[0][0]
                    is_exact_match = True
                    for i in range(9):
                        if i == target or i in indices: continue
                        is_common = True
                        for state, _ in matching_pairs:
                            if state[i] != first_state[i]:
                                is_common = False
                                break
                        if is_common:
                            is_exact_match = False
                            break
                            
                    if is_exact_match:
                        new_rule = {
                            'cause_indices': indices,
                            'cause_pattern': pattern,
                            'turn': turn,
                            'target': target,
                            'pairs_to_remove': matching_pairs
                        }
                        new_rules_this_pass.append(new_rule)
                        global_minimal_rules.append(new_rule)

                        # ★ 네가 명령한 바로 그 규칙 추적기 ★
                        if indices == (1, 4) and pattern == (' ', 'O') and target == 7 and turn == 'O' and pass_num == 3:
                            print(f"-> [Pass 3 도달] 네가 찾던 그 {len(matching_pairs)}개의 보드를 찾았어... ♡\n")
                            for idx, (s, tgt) in enumerate(matching_pairs):
                                print(f"=== [발견된 보드 {idx+1}] ===")
                                print(f" {s[0]} | {s[1]} | {s[2]} ")
                                print(f"---+---+---")
                                print(f" {s[3]} | {s[4]} | {s[5]} ")
                                print(f"---+---+---")
                                print(f" {s[6]} | {s[7]} | {s[8]} ")
                                print(f" -> 이 판의 최선의 수(Optimal Moves): {policy[s]}\n")

        if not new_rules_this_pass:
            break 

        for rule in new_rules_this_pass:
            for pair in rule['pairs_to_remove']:
                if pair in active_pairs:
                    active_pairs.remove(pair)
        
        pass_num += 1

# 실행
data = load_data()
trace_specific_14_boards(data)