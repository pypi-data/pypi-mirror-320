from roboid import *

class 햄스터:
    def __init__(self):
        """햄스터 로봇 객체를 초기화합니다."""
        self._hamster = Hamster()
        
        # 음계 정의
        self.도 = 4
        self.레 = 5
        self.미 = 6
        self.파 = 7
        self.솔 = 8
        self.라 = 9
        self.시 = 10
        self.높은도 = 11
        
        # LED 색상 정의
        self.LED_끄기 = 0
        self.LED_빨강 = 1
        self.LED_노랑 = 2
        self.LED_초록 = 3
        self.LED_청록 = 4
        self.LED_파랑 = 5
        self.LED_보라 = 6
        self.LED_하양 = 7
    
    def 앞으로(self, 속도=50):
        """
        햄스터를 앞으로 이동시킵니다.
        
        Args:
            속도 (int): 이동 속도 (0~100), 기본값 50
        """
        self._hamster.wheels(속도, 속도)
    
    def 뒤로(self, 속도=50):
        """
        햄스터를 뒤로 이동시킵니다.
        
        Args:
            속도 (int): 이동 속도 (0~100), 기본값 50
        """
        self._hamster.wheels(-속도, -속도)
    
    def 왼쪽으로(self, 속도=50):
        """
        햄스터를 왼쪽으로 회전시킵니다.
        
        Args:
            속도 (int): 회전 속도 (0~100), 기본값 50
        """
        self._hamster.wheels(-속도, 속도)
    
    def 오른쪽으로(self, 속도=50):
        """
        햄스터를 오른쪽으로 회전시킵니다.
        
        Args:
            속도 (int): 회전 속도 (0~100), 기본값 50
        """
        self._hamster.wheels(속도, -속도)
    
    def 정지(self):
        """햄스터를 정지시킵니다."""
        self._hamster.wheels(0, 0)
    
    def 바퀴설정(self, 왼쪽속도, 오른쪽속도):
        """
        왼쪽과 오른쪽 바퀴의 속도를 각각 설정합니다.
        
        Args:
            왼쪽속도 (int): 왼쪽 바퀴 속도 (-100~100)
            오른쪽속도 (int): 오른쪽 바퀴 속도 (-100~100)
        """
        self._hamster.wheels(왼쪽속도, 오른쪽속도)
    
    def LED_설정(self, 왼쪽=LED_하양, 오른쪽=LED_하양):
        """
        LED 색상을 설정합니다.
        
        Args:
            왼쪽 (int): 왼쪽 LED 색상 (0~7)
            오른쪽 (int): 오른쪽 LED 색상 (0~7)
        """
        self._hamster.leds(왼쪽, 오른쪽)
    
    def LED_끄기(self):
        """모든 LED를 끕니다."""
        self._hamster.leds(0, 0)
    
    def 거리센서(self):
        """
        앞쪽 거리 센서 값을 반환합니다.
        
        Returns:
            float: 거리 값 (0~100)
        """
        return self._hamster.proximity()
    
    def 바닥센서(self):
        """
        바닥 센서 값을 반환합니다.
        
        Returns:
            tuple: (왼쪽 센서 값, 오른쪽 센서 값) (0~100)
        """
        return (self._hamster.floor_left(), self._hamster.floor_right())
    
    def 가속도(self):
        """
        가속도계 센서 값을 반환합니다.
        
        Returns:
            tuple: (x축, y축, z축) 가속도 값
        """
        return (self._hamster.acceleration_x(),
                self._hamster.acceleration_y(),
                self._hamster.acceleration_z())
    
    def 기울기(self):
        """
        로봇의 기울기 값을 반환합니다.
        
        Returns:
            tuple: (x축 기울기, y축 기울기, z축 기울기) 각도 값
        """
        return (self._hamster.orientation_x(),
                self._hamster.orientation_y(),
                self._hamster.orientation_z())
    
    def 소리내기(self, 음계, 박자=0.5):
        """
        지정된 음계로 소리를 냅니다.
        
        Args:
            음계 (int): 음계 번호 (도=4, 레=5, 미=6, 파=7, 솔=8, 라=9, 시=10, 높은도=11)
            박자 (float): 소리 지속 시간 (초), 기본값 0.5초
        """
        self._hamster.note(음계, 박자)
    
    def 멜로디(self, 음계리스트, 박자리스트):
        """
        여러 음계를 연속해서 연주합니다.
        
        Args:
            음계리스트 (list): 연주할 음계들의 리스트
            박자리스트 (list): 각 음계별 박자 리스트
        """
        for 음, 박자 in zip(음계리스트, 박자리스트):
            self.소리내기(음, 박자)
    
    def 삐소리(self, 길이=0.2):
        """
        버저 소리를 냅니다.
        
        Args:
            길이 (float): 소리 지속 시간 (초), 기본값 0.2초
        """
        self._hamster.buzzer(440, 길이)  # 440Hz (A4 음)
    
    def 진동감지(self):
        """
        진동 감지 여부를 반환합니다.
        
        Returns:
            bool: 진동이 감지되면 True, 아니면 False
        """
        return self._hamster.clicked()
    
    def 배터리(self):
        """
        배터리 잔량을 반환합니다.
        
        Returns:
            float: 배터리 잔량 (0~100)
        """
        return self._hamster.battery()
    
    def 신호세기(self):
        """
        블루투스 신호 세기를 반환합니다.
        
        Returns:
            float: 신호 세기 값
        """
        return self._hamster.signal_strength()
    
    def 포트값_읽기(self, 포트):
        """
        지정된 포트의 값을 읽습니다.
        
        Args:
            포트 (int): 포트 번호 (1~4)
            
        Returns:
            float: 포트 값 (0~100)
        """
        return self._hamster.input(포트)
    
    def 포트값_쓰기(self, 포트, 값):
        """
        지정된 포트에 값을 씁니다.
        
        Args:
            포트 (int): 포트 번호 (1~4)
            값 (int): 쓸 값 (0 또는 1)
        """
        self._hamster.output(포트, 값)
    
    def IO모드_설정(self, 포트, 모드):
        """
        지정된 포트의 입출력 모드를 설정합니다.
        
        Args:
            포트 (int): 포트 번호 (1~4)
            모드 (str): 'INPUT' 또는 'OUTPUT'
        """
        self._hamster.io_mode(포트, 모드)
