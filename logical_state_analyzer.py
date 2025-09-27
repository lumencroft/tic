import sys
sys.path.append('.')
from game_logic import *
import pickle
from collections import defaultdict

class LogicalStateAnalyzer:
    """모든 게임 상태에서 사람의 논리적 사고 과정을 프로그래밍적으로 자동 추출"""
    
    def __init__(self):
        self.state_groups = {}
        self.logical_patterns = {}
        self.compression_stats = {}
    
    def analyze_all_states(self, lookup_table):
        """모든 게임 상태를 논리적으로 분석하여 자동 그룹화"""
        print("Analyzing all game states for logical patterns...")
        
        # 1. 모든 상태를 논리적 특성으로 분석
        self._analyze_logical_characteristics(lookup_table)
        
        # 2. 논리적 특성별로 상태 그룹화
        self._group_states_by_logic(lookup_table)
        
        # 3. 각 그룹의 공통 패턴 추출
        self._extract_common_patterns()
        
        # 4. 압축 통계 계산
        self._calculate_compression_stats(lookup_table)
        
        return self.state_groups
    
    def _analyze_logical_characteristics(self, lookup_table):
        """모든 상태의 논리적 특성을 프로그래밍적으로 분석"""
        print("Analyzing logical characteristics of all states...")
        
        self.logical_patterns = {
            'can_win_immediately': [],
            'must_block_immediately': [],
            'can_create_fork': [],
            'must_block_fork': [],
            'center_priority': [],
            'corner_priority': [],
            'edge_priority': [],
            'other_strategic': []
        }
        
        for board_str, best_moves in lookup_table.items():
            characteristics = self._get_logical_characteristics(board_str, best_moves)
            
            # 각 특성별로 상태 분류
            for characteristic, states in characteristics.items():
                if states:  # 해당 특성이 있으면
                    self.logical_patterns[characteristic].append({
                        'state': board_str,
                        'moves': best_moves,
                        'reason': self._get_reason(characteristic, board_str, best_moves)
                    })
    
    def _get_logical_characteristics(self, board_str, best_moves):
        """특정 상태의 논리적 특성을 프로그래밍적으로 분석"""
        characteristics = {
            'can_win_immediately': False,
            'must_block_immediately': False,
            'can_create_fork': False,
            'must_block_fork': False,
            'center_priority': False,
            'corner_priority': False,
            'edge_priority': False,
            'other_strategic': False
        }
        
        # 1. 즉시 승리 가능한지 확인
        if self._can_win_immediately(board_str):
            characteristics['can_win_immediately'] = True
        
        # 2. 즉시 방어해야 하는지 확인
        if self._must_block_immediately(board_str):
            characteristics['must_block_immediately'] = True
        
        # 3. 포크를 생성할 수 있는지 확인
        if self._can_create_fork(board_str, best_moves):
            characteristics['can_create_fork'] = True
        
        # 4. 포크를 막아야 하는지 확인
        if self._must_block_fork(board_str, best_moves):
            characteristics['must_block_fork'] = True
        
        # 5. 중심점 우선인지 확인
        if 4 in best_moves and board_str[4] == ' ':
            characteristics['center_priority'] = True
        
        # 6. 모서리 우선인지 확인
        corners = [0, 2, 6, 8]
        if any(move in best_moves and board_str[move] == ' ' for move in corners):
            characteristics['corner_priority'] = True
        
        # 7. 변 우선인지 확인
        edges = [1, 3, 5, 7]
        if any(move in best_moves and board_str[move] == ' ' for move in edges):
            characteristics['edge_priority'] = True
        
        # 8. 그 외 전략적 수인지 확인
        if not any(characteristics.values()):
            characteristics['other_strategic'] = True
        
        return characteristics
    
    def _get_reason(self, characteristic, board_str, best_moves):
        """특정 특성의 이유를 프로그래밍적으로 설명"""
        reasons = {
            'can_win_immediately': f"Player {get_turn(board_str)} can win in one move",
            'must_block_immediately': f"Player {get_turn(board_str)} must block opponent's winning move",
            'can_create_fork': f"Player {get_turn(board_str)} can create a fork",
            'must_block_fork': f"Player {get_turn(board_str)} must block opponent's fork",
            'center_priority': "Center position is optimal",
            'corner_priority': "Corner position is optimal",
            'edge_priority': "Edge position is optimal",
            'other_strategic': "Other strategic considerations"
        }
        return reasons.get(characteristic, "Unknown reason")
    
    def _can_win_immediately(self, board_str):
        """즉시 승리 가능한지 프로그래밍적으로 확인"""
        player = get_turn(board_str)
        return self._can_win(board_str, player)
    
    def _can_win(self, board_str, player):
        """특정 플레이어가 승리할 수 있는지 프로그래밍적으로 확인"""
        lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for line in lines:
            line_chars = [board_str[i] for i in line]
            if line_chars.count(player) == 2 and line_chars.count(' ') == 1:
                return True
        return False
    
    def _must_block_immediately(self, board_str):
        """즉시 방어해야 하는지 프로그래밍적으로 확인"""
        player = get_turn(board_str)
        opponent = 'O' if player == 'X' else 'X'
        return self._can_win(board_str, opponent)
    
    def _can_create_fork(self, board_str, best_moves):
        """포크를 생성할 수 있는지 프로그래밍적으로 확인"""
        player = get_turn(board_str)
        for move in best_moves:
            test_board = list(board_str)
            test_board[move] = player
            if self._count_winning_lines("".join(test_board), player) >= 2:
                return True
        return False
    
    def _must_block_fork(self, board_str, best_moves):
        """포크를 막아야 하는지 프로그래밍적으로 확인"""
        player = get_turn(board_str)
        opponent = 'O' if player == 'X' else 'X'
        
        for move in best_moves:
            test_board = list(board_str)
            test_board[move] = player
            if self._count_winning_lines("".join(test_board), opponent) < 2:
                return True
        return False
    
    def _count_winning_lines(self, board_str, player):
        """승리 가능한 라인 수를 프로그래밍적으로 계산"""
        lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        count = 0
        for line in lines:
            line_chars = [board_str[i] for i in line]
            if line_chars.count(player) == 2 and line_chars.count(' ') == 1:
                count += 1
        return count
    
    def _group_states_by_logic(self, lookup_table):
        """논리적 특성별로 상태 그룹화"""
        print("Grouping states by logical characteristics...")
        
        self.state_groups = {}
        
        for characteristic, states in self.logical_patterns.items():
            if states:
                self.state_groups[characteristic] = {
                    'count': len(states),
                    'states': states,
                    'common_pattern': self._find_common_pattern(states),
                    'compression_ratio': len(lookup_table) / len(states)
                }
    
    def _find_common_pattern(self, states):
        """그룹 내 상태들의 공통 패턴을 프로그래밍적으로 찾기"""
        if not states:
            return "No pattern"
        
        # 첫 번째 상태를 기준으로 패턴 분석
        first_state = states[0]['state']
        patterns = []
        
        # 기본 통계 패턴
        x_count = first_state.count('X')
        o_count = first_state.count('O')
        empty_count = first_state.count(' ')
        turn = 'O' if x_count > o_count else 'X'
        
        patterns.append(f"turn_{turn}")
        patterns.append(f"count_{x_count}X_{o_count}O_{empty_count}empty")
        
        # 승리 가능성 패턴
        if self._can_win(first_state, 'X'):
            patterns.append('X_can_win')
        if self._can_win(first_state, 'O'):
            patterns.append('O_can_win')
        
        # 위치 패턴
        if first_state[4] == ' ':
            patterns.append('center_empty')
        
        corners = [0, 2, 6, 8]
        empty_corners = [i for i in corners if first_state[i] == ' ']
        if empty_corners:
            patterns.append(f'corners_empty_{len(empty_corners)}')
        
        edges = [1, 3, 5, 7]
        empty_edges = [i for i in edges if first_state[i] == ' ']
        if empty_edges:
            patterns.append(f'edges_empty_{len(empty_edges)}')
        
        return ' AND '.join(patterns)
    
    def _extract_common_patterns(self):
        """모든 그룹의 공통 패턴을 추출"""
        print("Extracting common patterns across all groups...")
        
        # 전체 패턴 통계
        total_states = sum(group['count'] for group in self.state_groups.values())
        
        print(f"\n=== Logical State Analysis Results ===")
        print(f"Total states analyzed: {total_states}")
        print(f"Number of logical groups: {len(self.state_groups)}")
        
        for characteristic, group in self.state_groups.items():
            print(f"\n--- {characteristic.upper()} GROUP ---")
            print(f"States count: {group['count']}")
            print(f"Compression ratio: {group['compression_ratio']:.2f}x")
            print(f"Common pattern: {group['common_pattern']}")
            
            # 예시 상태들
            print("Example states:")
            for i, state_info in enumerate(group['states'][:3]):
                print(f"  {i+1}. {state_info['state']} -> {state_info['moves']} ({state_info['reason']})")
            if len(group['states']) > 3:
                print(f"  ... and {len(group['states']) - 3} more states")
    
    def _calculate_compression_stats(self, lookup_table):
        """압축 통계 계산"""
        total_entries = len(lookup_table)
        total_groups = len(self.state_groups)
        
        self.compression_stats = {
            'total_entries': total_entries,
            'logical_groups': total_groups,
            'compression_ratio': total_entries / total_groups,
            'compression_percentage': (total_groups / total_entries) * 100,
            'memory_reduction': ((total_entries - total_groups) / total_entries) * 100,
            'average_group_size': total_entries / total_groups
        }
    
    def save_analysis(self, filename='logical_state_analysis.pkl'):
        """분석 결과 저장"""
        data = {
            'state_groups': self.state_groups,
            'logical_patterns': self.logical_patterns,
            'compression_stats': self.compression_stats
        }
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
        print(f"Logical state analysis saved as '{filename}'")
    
    def load_analysis(self, filename='logical_state_analysis.pkl'):
        """분석 결과 로드"""
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        self.state_groups = data['state_groups']
        self.logical_patterns = data['logical_patterns']
        self.compression_stats = data['compression_stats']
        print(f"Logical state analysis loaded from '{filename}'")
    
    def predict_by_logic(self, board_str):
        """논리적 그룹 기반 예측"""
        # 각 논리적 특성을 확인하여 해당 그룹 찾기
        for characteristic, group in self.state_groups.items():
            if self._state_matches_characteristic(board_str, characteristic):
                # 해당 그룹의 일반적인 전략 적용
                return self._apply_group_strategy(board_str, characteristic)
        
        # 기본 전략
        return self._apply_basic_strategy(board_str)
    
    def _state_matches_characteristic(self, board_str, characteristic):
        """상태가 특정 특성과 매칭되는지 확인"""
        if characteristic == 'can_win_immediately':
            return self._can_win_immediately(board_str)
        elif characteristic == 'must_block_immediately':
            return self._must_block_immediately(board_str)
        elif characteristic == 'center_priority':
            return board_str[4] == ' '
        elif characteristic == 'corner_priority':
            corners = [0, 2, 6, 8]
            return any(board_str[i] == ' ' for i in corners)
        elif characteristic == 'edge_priority':
            edges = [1, 3, 5, 7]
            return any(board_str[i] == ' ' for i in edges)
        return False
    
    def _apply_group_strategy(self, board_str, characteristic):
        """그룹별 전략 적용"""
        if characteristic == 'can_win_immediately':
            return self._get_winning_moves(board_str)
        elif characteristic == 'must_block_immediately':
            return self._get_blocking_moves(board_str)
        elif characteristic == 'center_priority':
            return [4] if board_str[4] == ' ' else []
        elif characteristic == 'corner_priority':
            corners = [0, 2, 6, 8]
            return [i for i in corners if board_str[i] == ' ']
        elif characteristic == 'edge_priority':
            edges = [1, 3, 5, 7]
            return [i for i in edges if board_str[i] == ' ']
        return self._apply_basic_strategy(board_str)
    
    def _get_winning_moves(self, board_str):
        """승리하는 수 찾기"""
        player = get_turn(board_str)
        lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        
        for line in lines:
            line_chars = [board_str[i] for i in line]
            if line_chars.count(player) == 2 and line_chars.count(' ') == 1:
                empty_pos = line[line_chars.index(' ')]
                return [empty_pos]
        return []
    
    def _get_blocking_moves(self, board_str):
        """방어하는 수 찾기"""
        player = get_turn(board_str)
        opponent = 'O' if player == 'X' else 'X'
        lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        
        for line in lines:
            line_chars = [board_str[i] for i in line]
            if line_chars.count(opponent) == 2 and line_chars.count(' ') == 1:
                empty_pos = line[line_chars.index(' ')]
                return [empty_pos]
        return []
    
    def _apply_basic_strategy(self, board_str):
        """기본 전략 적용"""
        # 중심점이 비어있으면 중심점
        if board_str[4] == ' ':
            return [4]
        
        # 모서리가 비어있으면 모서리
        corners = [0, 2, 6, 8]
        empty_corners = [i for i in corners if board_str[i] == ' ']
        if empty_corners:
            return empty_corners
        
        # 그 외 유효한 수
        return [i for i, char in enumerate(board_str) if char == ' ']

def test_logical_state_analyzer():
    """논리적 상태 분석기 테스트"""
    print("=== Logical State Analyzer Test ===")
    
    # 룩업 테이블 로드
    with open('perfect_lookup_table.pkl', 'rb') as f:
        lookup_table = pickle.load(f)
    
    print(f"Loaded lookup table with {len(lookup_table)} entries")
    
    # 논리적 상태 분석기 생성
    analyzer = LogicalStateAnalyzer()
    analyzer.analyze_all_states(lookup_table)
    
    # 압축 통계 출력
    stats = analyzer.compression_stats
    print(f"\n=== Compression Statistics ===")
    print(f"Total entries: {stats['total_entries']}")
    print(f"Logical groups: {stats['logical_groups']}")
    print(f"Compression ratio: {stats['compression_ratio']:.2f}x")
    print(f"Compression percentage: {stats['compression_percentage']:.1f}%")
    print(f"Memory reduction: {stats['memory_reduction']:.1f}%")
    print(f"Average group size: {stats['average_group_size']:.1f} states per group")
    
    # 정확도 테스트
    print(f"\n=== Accuracy Test ===")
    correct_predictions = 0
    total_predictions = 0
    
    for board_str, expected_moves in lookup_table.items():
        predicted_moves = analyzer.predict_by_logic(board_str)
        
        if set(predicted_moves) == set(expected_moves):
            correct_predictions += 1
        total_predictions += 1
    
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
    print(f"Logical state analyzer accuracy: {accuracy:.6f} ({correct_predictions}/{total_predictions})")
    
    if accuracy >= 0.9999:
        print("🎉 PERFECT! Logical state analyzer achieved 100% accuracy!")
    else:
        print(f"⚠️  Still {100-accuracy*100:.2f}% away from perfect accuracy")
    
    # 분석 결과 저장
    analyzer.save_analysis()
    
    return analyzer

if __name__ == "__main__":
    test_logical_state_analyzer()
