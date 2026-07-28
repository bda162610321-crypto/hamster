import sys
import time
import msvcrt
from roboid import *

def main():
    print("햄스터 로봇 연결을 시작합니다...")
    # Hamster 객체 생성
    hamster = Hamster()
    
    print("연결 성공!")
    print("--------------------------------------------------")
    print("★ 자연스러운 주행 조종 모드 ★")
    print("방향키를 눌러 부드럽게 조종하세요. 떼면 부드럽게 멈춥니다.")
    print("  ▲ (위): 전진 및 가속")
    print("  ▼ (아래): 후진 및 감속")
    print("  ◀ (왼쪽): 좌회전 (이동 중일 때는 부드럽게 곡선 주행)")
    print("  ▶ (오른쪽): 우회전 (이동 중일 때는 부드럽게 곡선 주행)")
    print("종료하려면 'q' 키 또는 ESC 키를 누르세요.")
    print("--------------------------------------------------")
    
    # 시간 및 키 상태 변수
    last_up_time = 0
    last_down_time = 0
    last_left_time = 0
    last_right_time = 0
    
    # 현재 제어 속도 및 방향 (부드러운 보간용)
    v_current = 0.0  # 전진/후진 속도 (-100 ~ 100)
    w_current = 0.0  # 회전 속도 (-100 ~ 100)
    
    # 조종 설정 값
    MAX_SPEED = 100      # 최대 속도 (0 ~ 100)
    STEER_SPEED = 80     # 제자리 회전 속도
    CURVE_STEER = 60     # 주행 중 회전 편차 (곡선 주행용)
    ACTIVE_LIMIT = 0.4   # 키 입력 활성 유지 시간 (초)
    ACCEL_FACTOR = 0.35  # 속도 변화 계수 (클수록 더 빠르게 반응하고 최대 속도에 빨리 도달합니다)
    
    try:
        while True:
            now = time.time()
            
            # 키 입력이 버퍼에 있는지 확인
            if msvcrt.kbhit():
                key = msvcrt.getch()
                
                # ESC(0x1b) 또는 'q' 키가 입력되면 종료
                if key == b'\x1b' or key.lower() == b'q':
                    print("\n프로그램을 종료합니다.")
                    break
                
                # 방향키 입력을 나타내는 접두사 (0x00 또는 0xe0)
                if key == b'\x00' or key == b'\xe0':
                    key = msvcrt.getch()  # 실제 키 값을 한 번 더 읽음
                    if key == b'H':      # 위 방향키 (전진)
                        last_up_time = now
                    elif key == b'P':    # 아래 방향키 (후진)
                        last_down_time = now
                    elif key == b'K':    # 왼쪽 방향키 (좌회전)
                        last_left_time = now
                    elif key == b'M':    # 오른쪽 방향키 (우회전)
                        last_right_time = now
            
            # 1. 각 방향키가 현재 활성 상태인지 계산 (지정 시간 내 입력 여부)
            up_active = (now - last_up_time < ACTIVE_LIMIT)
            down_active = (now - last_down_time < ACTIVE_LIMIT)
            left_active = (now - last_left_time < ACTIVE_LIMIT)
            right_active = (now - last_right_time < ACTIVE_LIMIT)
            
            # 2. 목표 속도(v_target) 및 회전값(w_target) 설정
            v_target = 0.0
            w_target = 0.0
            
            if up_active:
                v_target = float(MAX_SPEED)
            elif down_active:
                v_target = float(-MAX_SPEED)
                
            if left_active:
                # 전진/후진 중일 때는 곡선 주행, 제자리일 때는 제자리 회전
                if up_active or down_active:
                    w_target = float(-CURVE_STEER)
                else:
                    w_target = float(-STEER_SPEED)
            elif right_active:
                if up_active or down_active:
                    w_target = float(CURVE_STEER)
                else:
                    w_target = float(STEER_SPEED)
            
            # 3. 현재 속도를 목표 속도로 부드럽게 보간 (가속도/감속도 효과)
            v_current += (v_target - v_current) * ACCEL_FACTOR
            w_current += (w_target - w_current) * ACCEL_FACTOR
            
            # 4. 좌/우 바퀴 속도 계산
            # w_current가 양수이면 우회전 (왼쪽 바퀴 더 빠름, 오른쪽 바퀴 더 느림)
            # w_current가 음수이면 좌회전 (왼쪽 바퀴 더 느림, 오른쪽 바퀴 더 빠름)
            left_wheel = v_current + w_current
            right_wheel = v_current - w_current
            
            # 5. 속도 제한 클램핑 (-100 ~ 100)
            left_wheel = max(-100.0, min(100.0, left_wheel))
            right_wheel = max(-100.0, min(100.0, right_wheel))
            
            # 6. 로봇에 모터 명령 전송
            hamster.wheels(int(left_wheel), int(right_wheel))
            
            # 통신 및 CPU 점유율 제어를 위해 20ms 대기
            wait(20)
            
    except KeyboardInterrupt:
        print("\n사용자에 의해 프로그램이 중단되었습니다.")
    finally:
        # 종료 시 안전하게 모터 정지 및 LED 끄기
        hamster.wheels(0, 0)
        hamster.leds(hamster.LED_OFF, hamster.LED_OFF)

if __name__ == "__main__":
    main()
