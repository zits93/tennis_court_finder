from datetime import datetime, date
from collections import defaultdict
from pytimekr import pytimekr
import time
import requests

class NaverBookingAPI:
    def __init__(self, court_id):
        # 테니스장 코트별 id 가져오기
        self.court_id = court_id
        self.tennisBizItemsMap = defaultdict(str)
        self.get_court_id()

        # 공휴일 리스트 만들기
        self.holiday_list = pytimekr.holidays()
        self.holiday_list.append(date(2023, 10, 2))
        self.weekday_dict = {0:"월", 1:"화", 2:"수", 3:"목", 4:"금", 5:"토", 6:"일"}

        # 조회 시작 & 끝 날짜
        curr_year = datetime.now().year
        curr_month = datetime.now().month
        if curr_month == 12:
            next_year = curr_year + 1
            next_month = 1
        else:
            next_year = curr_year
            next_month = curr_month + 1
        self.start = f'{curr_year}-{curr_month:02d}-01T00:00:00'
        self.end = f'{next_year}-{next_month:02d}-01T00:00:00'
        
    def get_court_id(self, max_court_num=11):
        url = f"https://api.booking.naver.com/v3.0/businesses/{self.court_id}/biz-items?lang=ko&isDeleted=false&isImp=true&sellingCountry=KR"
        res = requests.get(url).json()
        court_num = len(res)
        try:
            if court_num > 0:  # 찾은 biz id에 해당하는 코트가 있을 때
                self.tennisBizItemsMap = defaultdict(str)
                if court_num > max_court_num: # 찾은 코트수가 court_num을 초과할 때
                    for i in range(max_court_num):
                        item = res[i]
                        self.tennisBizItemsMap.update({item['bizItemId']: item['name']})
                else:
                    for item in res:
                        self.tennisBizItemsMap.update({item['bizItemId']: item['name']})
                    # time.sleep((max_court_num - court_num) * 0.2)
        except:
            print(f'Error response: {res}')
            
    def find_court(self):
        self.get_court_id()
        # 코트별 빈 시간대 조회
        buffer = []
        buffer_size = 0
        for key, value in self.tennisBizItemsMap.items():
            url = f"https://api.booking.naver.com/v3.0/businesses/{self.court_id}/biz-items/{key}/hourly-schedules?lang=ko&endDateTime={self.end}&startDateTime={self.start}"
            res = requests.get(url).json()
            try:
                if len(res) > 0:  # 찾은 코트에서 빈 시간대가 있을 때
                    indices = [index for index, item in enumerate(res) if item['unitBookingCount'] == 0 and datetime.fromisoformat(item['unitStartTime']) > datetime.now() and item['isUnitBusinessDay'] and item['isUnitSaleDay']]

                    # 휴일, 주말, 아침, 저녁 필터링
                    if indices:
                        court_name = value.split()[1][0]  # 양재 테니스장 코트 인식용
                        indoor_court_list = ['A', 'B', 'C']
                        if court_name in indoor_court_list:  # 겨울 시즌 실내 코트만 잡기
                            for index in indices:
                                date_str = res[index]['unitStartTime']
                                year = int(date_str[:4])
                                month = int(date_str[5:7])
                                day = int(date_str[8:10])
                                hour = int(date_str[11:13])
                                ddate = date(year, month, day)
                                weekday = ddate.weekday()
                                time_str = f"{month}월 {day}일 ({self.weekday_dict[weekday]}) {hour}시 {court_name}코트"
                                if ddate in self.holiday_list:
                                    time_str += " 휴일"
                                elif weekday > 4:
                                    time_str += " 주말"
                                elif hour == 7:
                                    time_str += " 아침"
                                elif hour >= 19:
                                    time_str += " 저녁"
                                else:
                                    continue
                                buffer.append(f"{time_str}")
                                buffer_size += 1
            except:
                print(f'Error response: {res}')
                raise BufferError
        return buffer