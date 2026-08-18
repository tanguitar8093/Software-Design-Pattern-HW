from typing import Dict, List


def load_host_ip_config(path: str) -> Dict[str, List[str]]:
    """讀取「host: ip, ip, ip」格式的服務探索配置檔。"""
    host_to_ips: Dict[str, List[str]] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            host, ips = line.split(":", 1)
            host_to_ips[host.strip()] = [ip.strip() for ip in ips.split(",") if ip.strip()]
    return host_to_ips


def load_blacklist_config(path: str) -> List[str]:
    """讀取以逗號分隔的黑名單 Host 配置檔。"""
    with open(path, encoding="utf-8") as f:
        content = f.read()
    return [item.strip() for item in content.split(",") if item.strip()]
