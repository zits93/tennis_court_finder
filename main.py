from src.NaverBookingAPI import NaverBookingAPI
from src.KakaoMessageAPI import KakaoMessageAPI
from src.TelegramBotAPI import TelegramBotAPI
import time
import schedule
import json
import os
import trio
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
file_handler = logging.FileHandler("log.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)


class TennisCourtFinder:
    def __init__(self, court_id=210031):
        self.kakao_api = KakaoMessageAPI()
        if os.path.isfile("refresh_token.json"):
            with open("refresh_token.json", "r") as fp:
                ts = json.load(fp)
                if not "refresh_token" in ts:
                    self.kakao_api.update_refresh_token()
        else:
            self.kakao_api.update_refresh_token()
        self.kakao_api.load_refresh_token()
        self.teleg_api = TelegramBotAPI()
        self.naver_api = NaverBookingAPI(court_id)
        self.buffer_size = -1

    def send_buffer(self):
        buffer = self.naver_api.find_court()
        buffer_size = len(buffer)
        if buffer_size != self.buffer_size:
            buffer_str =""
            if buffer_size > 0:
                for updated_data in buffer:
                    buffer_str += updated_data + "\n"
                logger.info(buffer_str)
                buffer_str += "\n[예약 링크](https://m.booking.naver.com/booking/10/bizes/210031)"
                trio.run(self.teleg_api.send_message, buffer_str)
            elif buffer_size == 0:
                buffer_str = "현재 예약 가능한 코트 없음\n\n[필터링 기준]\n1. 평일 7시 or 19시 이후\n2. 주말이나 휴일은 시간 무관\n3. 겨울 시즌(12월~2월) 실내 코트만"
                trio.run(self.teleg_api.send_message, buffer_str)
            self.buffer_size = buffer_size
        

if __name__ == "__main__":
    # 매헌 테니스장
    court_id = 210031
    
    # 내곡 테니스장
    # court_id = 217811
    
    # 잠원 테니스장
    # court_id = 617066
    
    tcf = TennisCourtFinder(court_id)
    logger.info("서버 시작")

    start = time.time()
    while True:
        try:
            tcf.send_buffer()
            end = time.time()
            elapsed_time = end - start
            if elapsed_time < 1.2:
                additional_wait = 1.2 - elapsed_time
                time.sleep(additional_wait)
            logger.debug(f"업데이트 {time.time() - start:.3f}초 경과")
            start = end
        except Exception as err:
            tcf = TennisCourtFinder(court_id)
            logger.error("서버 재시작: {err}")
