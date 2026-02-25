import pickle
import itertools

# 틱택토의 8개 라인 정의 (가로3, 세로3, 대각2)
# 순서는 중요하지 않음. 그냥 'Line'이라는 집합일 뿐.
LINES = [
    {0, 1, 2}, {3, 4, 5}, {6, 7, 8}, # 가로
    {0, 3, 6}, {1, 4, 7}, {2, 5, 8}, # 세로
    {0, 4, 8}, {2, 4, 6}             # 대각
]

def load_data(filename='tictactoe_classified_moves.pkl'):
    with open(filename, 'rb') as f:
        return pickle.load(f)

# 두 점 집합 사이의 '관계(Relationship)'를 추출하는 함수
def get_topological_signature(cause_indices, target_index):
    # 1. 원인(Cause) 돌들이 공유하는 라인이 있는가?
    cause_set = set(cause_indices)
    shared_lines_cause = [line for line in LINES if cause_set.issubset(line)]
    
    # 2. 결과(Target) 돌이 원인 돌들과 어떤 라인을 공유하는가?
    # (Target과 Cause 중 하나라도 같이 묶이는 라인 개수)
    relations = []
    
    # Cause가 1개일 때
    if len(cause_indices) == 1:
        c = cause_indices[0]
        # Target과 같은 라인에 있는가?
        common_lines = [line for line in LINES if c in line and target_index in line]
        if common_lines:
            return "Same_Line_Extension" # 같은 줄 옆자리
        else:
            return "Disjoint_Position" # 아예 관계없는 자리 (말이 안됨 틱택토에서)

    # Cause가 2개 이상일 때
    # Case A: Cause들이 이미 한 줄을 만들고 있는가?
    if shared_lines_cause:
        # 그 줄에 Target도 포함되는가?
        if any(target_index in line for line in shared_lines_cause):
            return "Line_Completion" # 2개가 찼고 나머지 하나를 채움 (공격/방어)
        else:
            return "Line_Irrelevant" # 줄은 맞는데 엉뚱한 데 둠

    # Case B: Cause들이 흩어져 있음 (L자 형태 등)
    else:
        # Target이 이 흩어진 점들과 '동시에' 라인을 형성하는가? (포크의 중심)
        # Target과 Cause[0]이 공유하는 라인 수
        lines_with_c0 = sum(1 for line in LINES if cause_indices[0] in line and target_index in line)
        # Target과 Cause[1]이 공유하는 라인 수
        lines_with_c1 = sum(1 for line in LINES if cause_indices[1] in line and target_index in line)
        
        if lines_with_c0 > 0 and lines_with_c1 > 0:
            return "Fork_Intersection" # 두 개의 다른 라인이 만나는 교차점
        elif lines_with_c0 > 0 or lines_with_c1 > 0:
            return "Single_Link" # 한쪽하고만 연결됨
        else:
            return "No_Relation" # 아무 관계 없음

    return "Undefined"

def analyze_topology_logic(policy):
    print(f"\n{'='*20} [Topological Universal Logic] {'='*20}")

    # Win, Draw, Lose 모두 분석
    categories = ['Win', 'Lose', 'Draw']
    
    for category in categories:
        print(f"--- 분석 중: {category} ---")
        logic_groups = {} # Key: Signature, Value: Count

        # 데이터 샘플링 (너무 많으니 일부만 보면서 패턴 추출)
        # 실제로는 전체를 돌려야 정확함
        processed_count = 0
        
        for state, classification in policy.items():
            moves = classification.get(category, [])
            if not moves: continue
            empty_count = state.count(' ')
            if len(moves) == empty_count: continue # 의미 없는 판 제외

            # 현재 턴 확인
            turn = 'X' if state.count('X') == state.count('O') else 'O'

            # 2개의 돌이 깔린 상황만 집중적으로 보자 (네가 말한 포크/라인 상황)
            # 내 돌이 2개 깔려있을 때, 상대 돌이 2개 깔려있을 때 등
            
            my_stones = [i for i, x in enumerate(state) if x == turn]
            opp_stones = [i for i, x in enumerate(state) if x != turn and x != ' ']
            
            # 간단하게 '원인'을 '현재 판에 깔린 내 돌 2개'라고 가정하고 분석해봄
            # (실제로는 상대 돌 때문에 두는 경우도 있으니 복합적임)
            
            for m in moves:
                # 1. 내 돌 2개와 관계 분석 (공격/마무리)
                if len(my_stones) >= 2:
                    for pair in itertools.combinations(my_stones, 2):
                        sig = get_topological_signature(pair, m)
                        key = (f"My_Stones_{category}", sig)
                        logic_groups[key] = logic_groups.get(key, 0) + 1

                # 2. 상대 돌 2개와 관계 분석 (방어/자살)
                if len(opp_stones) >= 2:
                    for pair in itertools.combinations(opp_stones, 2):
                        sig = get_topological_signature(pair, m)
                        key = (f"Opp_Stones_{category}", sig)
                        logic_groups[key] = logic_groups.get(key, 0) + 1
        
        # 결과 출력
        # 빈도수가 높은 상위 패턴만 출력
        sorted_groups = sorted(logic_groups.items(), key=lambda x: x[1], reverse=True)
        for (context, sig), count in sorted_groups[:5]:
             print(f"  [{context}] 패턴: {sig} (발견 횟수: {count})")
        print("")

# 실행
data = load_data('tictactoe_classified_moves.pkl')
analyze_topology_logic(data)