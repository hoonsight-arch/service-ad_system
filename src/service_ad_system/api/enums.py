from enum import Enum

class AdStatus(str, Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"

# D9 한글 라벨 매핑표
AD_STATUS_LABEL_MAP = {
    AdStatus.RUNNING: "진행중",
    AdStatus.PAUSED: "일시정지",
    AdStatus.STOPPED: "중단됨"
}