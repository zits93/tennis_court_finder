import requests
import json


class KakaoMessageAPI:
    def __init__(self):
        self.url = 'https://kauth.kakao.com/oauth/token'  
        self.rest_api_key = '3ffd51ed8258015d85dd92b4df6c080e'  
        self.redirect_uri = 'https://m.booking.naver.com'
        
    def update_refresh_token(self):
        print(f"Redirect link: https://kauth.kakao.com/oauth/authorize?client_id={self.rest_api_key}&redirect_uri={self.redirect_uri}&response_type=code&scope=talk_message,friends")
        authorize_code = input("Input authorize_code: ")
        data = {
                'grant_type': 'authorization_code',
                'client_id': self.rest_api_key,
                'redirect_uri': self.redirect_uri,
                'code': authorize_code
                }
        response = requests.post(self.url, data=data)
        tokens = response.json()
        with open("refresh_token.json", "w") as fp:
            json.dump(tokens, fp)
    
    def load_refresh_token(self):
        with open("refresh_token.json", "r") as fp:
            ts = json.load(fp)
        self.r_token = ts["refresh_token"]
        
    def send_message(self, text):
        # Refresh 토큰으로 Access 토큰 받기
        data = {
                "grant_type": "refresh_token",
                "client_id": self.rest_api_key,
                "refresh_token": self.r_token
               }
        response = requests.post(self.url, data=data)
        tokens = response.json()

        with open("access_token.json", "w") as fp:
            json.dump(tokens, fp)
        with open("access_token.json", "r") as fp:
            ts = json.load(fp)
        token = ts["access_token"]
        
        
        # 친구에게 메세지 보내기
        url = "https://kapi.kakao.com/v1/api/talk/friends"
        header = {"Authorization": 'Bearer ' + token}
        result = json.loads(requests.get(url, headers=header).text)
        friends_list = result.get("elements")
        print(friends_list)
        friend_id = friends_list[0].get("uuid")
        print(friend_id)
        url= "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
        header = {"Authorization": 'Bearer ' + token}
        post = {
                'object_type': 'text',
                'text': text,
                'link': {
                    'web_url': 'https://m.booking.naver.com/booking/10/bizes/210031',
                    'mobile_web_url': 'https://m.booking.naver.com/booking/10/bizes/210031'
                },
                'button_title': '예약 링크'
               }
        data = {'receiver_uuids': '["{}"]'.format(friend_id), 'template_object': json.dumps(post)}
        response = requests.post(url, headers=header, data=data)
        response.status_code
        
        # 나에게 메세지 보내기
        # header = {'Authorization': 'Bearer ' + token}
        # url = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'  
        # post = {
        #         'object_type': 'text',
        #         'text': text,
        #         'link': {
        #             'web_url': 'https://m.booking.naver.com/booking/10/bizes/210031',
        #             'mobile_web_url': 'https://m.booking.naver.com/booking/10/bizes/210031'
        #         },
        #         'button_title': '예약 링크'
        #        }
        # data = {'template_object': json.dumps(post)}
        # requests.post(url, headers=header, data=data)
