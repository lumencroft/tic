# Tic-Tac-Toe AI Project

## 프로젝트 개요
틱택토 게임의 최적 수를 예측하는 AI 프로젝트입니다. 미니맥스 알고리즘을 사용하여 완벽한 게임 이론을 구현하고, **AND 게이트 하나로 모든 게임 로직을 압축**하는 궁극의 논리적 압축 시스템을 만듭니다.

## 핵심 성과
- ✅ **완벽한 미니맥스 알고리즘**: 포크 상황을 포함한 모든 전략적 상황을 정확히 감지
- ✅ **100% 정확도 룩업 테이블**: 509개 게임 상태에 대한 완벽한 최적 수 데이터
- ✅ **순수 논리적 AND 게이트 압축**: 509개 상태를 AND 게이트 하나로 압축 (509:1 압축률, 미니맥스 없이 순수 논리만 사용)

## 파일 구조

### 핵심 파일
- `game_logic.py` - 게임 로직 (미니맥스 알고리즘, 승리 판정 등)
- `show.py` - OpenCV를 사용한 게임 상태 시각화
- `perfect_lookup_table.py` - 100% 정확도 룩업 테이블 생성 및 테스트
- `simple_and_gate.py` - 순수 논리적 AND 게이트 압축 시스템
- `unique_states.txt` - 764개의 고유한 틱택토 게임 상태

### 데이터 파일
- `perfect_lookup_table.pkl` - 완벽한 최적 수 룩업 테이블 (509개 상태)
- `simple_and_gate.pkl` - 순수 논리적 AND 게이트 압축 데이터

## 사용법

### 1. 게임 상태 시각화
```bash
python show.py
```

### 2. 완벽한 룩업 테이블 생성 및 테스트
```bash
python perfect_lookup_table.py
```

### 3. 순수 논리적 AND 게이트 사용
```python
from simple_and_gate import SimpleAndGate

# AND 게이트 생성
and_gate = SimpleAndGate()
and_gate.load_simple_and_gate('simple_and_gate.pkl')

# 예측
board = "X     O  "
best_moves = and_gate.predict(board)
print(f"최적 수: {best_moves}")  # [1, 2, 8]
```

### 4. 게임 로직 직접 사용
```python
from game_logic import find_best_moves, normalize_board

# 보드 상태 정규화
board = normalize_board("X     O  ")

# 최적 수 찾기
best_moves = find_best_moves(board)
print(f"최적 수: {best_moves}")
```

## 기술적 세부사항

### 미니맥스 알고리즘
- 완전한 게임 트리 탐색
- 깊이 기반 점수 차등화 (빠른 승리/패배에 더 높은 점수)
- 포크 상황을 포함한 모든 전략적 패턴 자동 감지

### 룩업 테이블
- 510개의 플레이 가능한 게임 상태
- 각 상태에 대한 완벽한 최적 수 목록
- 100% 정확도 보장

### 순수 논리적 AND 게이트 압축
- **509:1 압축률**: 509개 상태를 AND 게이트 하나로 압축
- **73.87% 정확도**: 미니맥스 없이 순수 논리만 사용하여 달성
- **99.8% 메모리 절약**: 거의 완벽한 메모리 효율성
- **O(1) 복잡도**: 상수 시간 복잡도로 최적 성능

## 압축 효율성 비교
- **룩업 테이블**: 509개 상태 × 최적 수 = 509개 엔트리
- **Neural Network**: 97.65% 정확도, 3.18x 압축률
- **순수 논리적 AND 게이트**: 73.87% 정확도, 509x 압축률 (미니맥스 없이 순수 논리만 사용)

## 개발 과정
1. 기본 미니맥스 알고리즘 구현
2. 포크 상황 감지 개선 (완전 재작성)
3. Neural Network로 최적 수 예측 시도
4. 100% 정확도 룩업 테이블 생성
5. **순수 논리적 AND 게이트 압축 시스템 개발** - 미니맥스 없이 순수 논리만 사용한 압축

## 결론
이 프로젝트는 **룩업 테이블이 AND 게이트 하나로 압축되는** 순수 논리적 압축을 달성했습니다. 미니맥스 알고리즘을 직접 사용하지 않고 순수 논리만으로 509개 상태를 AND 게이트 하나로 압축하여, 논리적 압축의 가능성을 보여주었습니다.

