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

def analyze_multipass_logic_exact(policy):
    print("응... 네 지시대로 '남은 빈칸 전부가 정답'인 판만 정확하게 쳐낼게... ♡\n")
    
    active_pairs = set()
    for state, moves in policy.items():
        empty_count = state.count(' ')
        if empty_count <= 1: continue
        
        # ★ 네가 짚어준 핵심 로직 수정 ★
        # 정답이 여러 개(len > 1)인 게 문제가 아니라, 
        # 남은 빈칸 전부가 다 정답(어딜 둬도 똑같음)인 보드만 제외!
        if len(moves) == empty_count: 
            continue 
            
        for m in moves:
            active_pairs.add((state, m))

    max_cause_k = 4 
    global_minimal_rules = [] 

    for cause_k in range(1, max_cause_k + 1):
        total_k = cause_k + 1 
        pass_num = 1
        
        while True:
            print(f"--- [Step {total_k} - Pass {pass_num}] 분석 중... ---")
            
            new_rules_this_pass = []
            indices_combinations = list(itertools.combinations(range(9), cause_k))
            
            for indices in indices_combinations:
                remaining_cells = [i for i in range(9) if i not in indices]
                
                seen_configs = set()
                for state in policy.keys():
                    empty_count = state.count(' ')
                    if empty_count <= 1: continue
                    # 여기서도 동일하게 필터링 적용
                    if len(policy[state]) == empty_count: continue 
                    
                    pat = tuple(state[i] for i in indices)
                    turn = 'X' if state.count('X') == state.count('O') else 'O'
                    seen_configs.add((pat, turn))

                for pattern, turn in seen_configs:
                    for target in remaining_cells:
                        
                        if is_superset_of_existing(indices, pattern, turn, target, global_minimal_rules):
                            continue
                            
                        matching_pairs_for_this_rule = []
                        is_100_pct = True
                        
                        for state, moves in policy.items():
                            empty_count = state.count(' ')
                            if empty_count <= 1: continue
                            
                            # ★ 철저한 배제 로직: 남은 칸 전부가 정답인 판만 무시!
                            if len(moves) == empty_count: 
                                continue 
                            
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
                                matching_pairs_for_this_rule.append((state, target))
                        
                        if not is_100_pct or len(matching_pairs_for_this_rule) < 2:
                            continue
                            
                        first_state = matching_pairs_for_this_rule[0][0]
                        is_exact_match = True
                        
                        for i in range(9):
                            if i == target or i in indices: 
                                continue
                            is_common = True
                            for state, _ in matching_pairs_for_this_rule:
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
                                'count': len(matching_pairs_for_this_rule),
                                'pairs_to_remove': matching_pairs_for_this_rule
                            }
                            new_rules_this_pass.append(new_rule)
                            global_minimal_rules.append(new_rule)

            if not new_rules_this_pass:
                print(f" -> Pass {pass_num} 결과: 더 이상 규칙 없음... ♡\n")
                break 

            print(f" -> Pass {pass_num} 결과: {len(new_rules_this_pass)}개의 규칙 발견... ♡")
            
            for rule in new_rules_this_pass:
                for pair in rule['pairs_to_remove']:
                    if pair in active_pairs:
                        active_pairs.remove(pair) # 증명 끝난 조합 풀에서 소거
            
            sorted_rules = sorted(new_rules_this_pass, key=lambda x: (x['cause_indices'], x['target']))
            for rule in sorted_rules:
                full_conditions = list(zip(rule['cause_indices'], rule['cause_pattern']))
                full_conditions.append((rule['target'], ' '))
                full_conditions.sort(key=lambda x: x[0])
                
                cond_str = ", ".join([f"{idx}:{val}" for idx, val in full_conditions])
                print(f"    IF [{cond_str}] & Turn='{rule['turn']}' -> {rule['target']} (Boards: {rule['count']})")
                
            pass_num += 1 

    print("=" * 60)
    print(f" [최종 결론] 제약 조건이 존재하는 진짜 보드들로만 뽑아낸 완벽한 규칙: 총 {len(global_minimal_rules)}개... ♡")

# 실행
data = load_data()
analyze_multipass_logic_exact(data)