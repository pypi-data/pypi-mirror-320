"""
Khamster - Hamster 로봇을 한글로 제어하기 위한 패키지
"""

from roboid import *
from .hamster import 햄스터

def 로봇찾기():
    """
    연결 가능한 모든 로봇을 찾습니다.
    
    Returns:
        list: 발견된 로봇들의 목록
    """
    return scan()

def 대기(시간=None):
    """
    지정된 시간(초) 동안 대기합니다.
    시간을 지정하지 않으면 무한히 대기합니다.
    
    Args:
        시간 (float, optional): 대기할 시간(초)
    """
    wait(시간)

def 준비될때까지_대기():
    """
    모든 로봇이 준비될 때까지 대기합니다.
    """
    wait_until_ready()

__version__ = "0.1.0"
__all__ = ['햄스터', '로봇찾기', '대기', '준비될때까지_대기']
