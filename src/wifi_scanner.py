"""
Класс WiFiScanner - реализация сканирования Wi-Fi сетей
Сгенерировано из диаграммы классов (diagrams/classes.puml)
"""

import subprocess
import re
from typing import List, Dict, Optional


class WiFiScanner:
    """Сканер Wi-Fi сетей с использованием aircrack-ng"""
    
    def __init__(self, interface: str):
        """
        Инициализация сканера
        
        Args:
            interface: Имя сетевого интерфейса (например, wlan0)
        """
        self.interface = interface
        self.channel: int = 0
        self.networks: List[Dict] = []
        self._set_monitor_mode()
    
    def _set_monitor_mode(self) -> bool:
        """
        Установка интерфейса в режим мониторинга
        
        Returns:
            bool: Успешность операции
        """
        try:
            subprocess.run(['sudo', 'airmon-ng', 'start', self.interface], 
                         check=True, capture_output=True)
            self.interface = f"{self.interface}mon"
            return True
        except subprocess.CalledProcessError:
            return False
    
    def scan_networks(self, duration: int = 30) -> List[Dict]:
        """
        Сканирование доступных Wi-Fi сетей
        
        Args:
            duration: Время сканирования в секундах
            
        Returns:
            List[Dict]: Список обнаруженных сетей
        """
        try:
            # Запуск airodump для захвата пакетов
            cmd = ['sudo', 'airodump-ng', '--write', 'scan', '--output-format', 'csv',
                   self.interface]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Ожидание указанное время
            process.wait(timeout=duration)
            process.terminate()
            
            # Парсинг результатов
            self.networks = self._parse_results()
            return self.networks
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return []
    
    def capture_packets(self, duration: int) -> None:
        """
        Захват пакетов для дальнейшего анализа
        
        Args:
            duration: Длительность захвата в секундах
        """
        try:
            cmd = ['sudo', 'tcpdump', '-i', self.interface, '-w', 'capture.pcap', 
                   '-G', str(duration), '-W', '1']
            subprocess.run(cmd, timeout=duration, capture_output=True)
        except subprocess.TimeoutExpired:
            pass
    
    def _parse_results(self) -> List[Dict]:
        """
        Парсинг CSV файла с результатами сканирования
        
        Returns:
            List[Dict]: Список сетей с параметрами
        """
        networks = []
        try:
            with open('scan-01.csv', 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                if 'Station' in line:
                    break
                parts = line.strip().split(',')
                if len(parts) >= 10 and parts[0] and 'BSSID' not in parts[0]:
                    network = {
                        'bssid': parts[0].strip(),
                        'channel': parts[3].strip(),
                        'ssid': parts[13].strip() if len(parts) > 13 else '',
                        'signal': parts[8].strip()
                    }
                    networks.append(network)
                    
        except FileNotFoundError:
            pass
            
        return networks
    
    def get_network_info(self, bssid: str) -> Optional[Dict]:
        """
        Получение информации о конкретной сети
        
        Args:
            bssid: MAC-адрес точки доступа
            
        Returns:
            Optional[Dict]: Информация о сети или None
        """
        for network in self.networks:
            if network['bssid'] == bssid:
                return network
        return None
