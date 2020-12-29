import datetime
import requests
import json

# 현재 시각을 출력
now = datetime.datetime.now()
# print (now)
today = str(now.year) + "년 " + str(now.month) + "월 " + str(now.day) + "일 " + str(now.hour) + "시 " + str(
    now.minute) + "분 " + str(now.second) + "초"


# 네이버가 이제 실시간 검색어 부분을 동적으로 불러오도록 정책이 바뀌었네요.
# 덕분에 불필요한 리소스를 가져올 필요가 없어서 트래픽도 엄청 줄어들고 파싱을 할 때 HTML 파싱이 아닌 json 파싱이 가능해졌습니다.

class Class_NaverRealtime:

    def __init__(self):
        self.rank_text = ""
        return

    def get_text(self):
        url = 'https://www.naver.com/srchrank?frm=main&ag=all&gr=0&ma=0&si=0&en=0&sp=0'
        res = json.loads(requests.get(url).content)
        rank = [*map(lambda item: item['keyword'], res['data'])]
        # print(rank)

        # print(today)
        # print("네이버 실시간 검색순위")
        # print("=============================")
        self.rank_text += today + '\n'
        self.rank_text += "네이버 실시간 검색순위" + '\n'
        self.rank_text += "=============================" + "\n"

        cnt = 0
        for j in rank:
            cnt += 1
            # print(str(cnt) + "." + str(j))
            self.rank_text += str(cnt) + "." + str(j) + "\n"
            if cnt == 20:
                break  # 20위까지 파싱

        return self.rank_text

    def realtimetext_crawling(self):
        df_text = self.get_text()
        # df_master.head()
        # print(df_master)
        print(df_text)
        return df_text




def main():

    rank_text = Class_NaverRealtime()
    rank_text.realtimetext_crawling()

if __name__ == '__main__':
    main()
