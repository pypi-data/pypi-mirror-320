import time
import random
import re
import requests
from typing import Tuple, List, Dict
from datetime import datetime

from utils_hj3415 import tools, noti
from webdriver_hj3415 import drivers


"""
공시 overview 예시
{'corp_cls': 'Y',
'corp_code': '00414850',
'corp_name': '효성 ITX',
'flr_nm': '효성 ITX',
'rcept_dt': '20240830',
'rcept_no': '20240830800804',
'report_nm': '[기재정정]거래처와의거래중단',
'rm': '유',
'stock_code': '094280'}
  
공시유형 - &pblntf_ty
A : 정기공시
B : 주요사항보고
C : 발행공시
D : 지분공시
E : 기타공시
F : 외부감사관련
G : 펀드공시
H : 자산유동화
I : 거래소공시
J : 공정위공시
"""


class OverView:
    # opendart id - hj3415@gmail.com
    HEAD_URL = 'https://opendart.fss.or.kr/api/list.json' + '?crtfc_key=' + '98b65db3b602f8419808baf0c5471c88edbf8a76'
    report_nm_types = {
        # 정기 공시
        'A': ['분기보고서', '반기보고서', '사업보고서'],
        # 주요 사항 보고
        'B': ['무상증자결정', '자기주식취득결정', '자기주식처분결정', '유상증자결정', '전환사채권발행결정',
              '신주인수권부사채권발행결정', '교환사채권발행결정', '회사합병결정', '회사분할결정'],
        # 거래소 공시
        'I': ['공급계약체결', '주식분할결정', '주식병합결정', '주식소각결정', '만기전사채취득', '신주인수권행사',
              '소송등의', '자산재평가실시결정', '현물배당결정', '주식배당결정', '매출액또는손익', '주주총회소집결의'],
        # 지분 공시
        'D': ['공개매수신고서', '특정증권등소유상황보고서', '주식등의대량보유상황보고서'],
    }
    SAVEFILENAME = 'overviews.json'

    def __init__(self, sdate='', edate='', code=''):
        """

        :param sdate: 검색시작날자 Ymd - 생략시 edate 단일날짜 조회
        :param edate: 검색종료날자 Ymd - 생략시 오늘날짜
        :param code: 종목코드 6자리 문자열 - 생략시 전체종목조회
        """
        self.sdate = sdate
        self.edate = edate
        self.code = code

    @property
    def sdate(self) -> str:
        return self._sdate

    @sdate.setter
    def sdate(self, sdate: str):
        assert tools.isYmd(sdate) or sdate == '', "sdate 형식이 맞지 않습니다.(Ymd)"
        self._sdate = sdate

    @property
    def edate(self) -> str:
        return self._edate

    @edate.setter
    def edate(self, edate: str):
        assert tools.isYmd(edate) or edate == '', "edate 형식이 맞지 않습니다.(Ymd)"
        self._edate = edate

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str):
        assert tools.is_6digit(code) or code == '', "code 형식이 맞지 않습니다.(6자리 숫자 문자열)"
        self._code = code

    @staticmethod
    def random_sleep(interval=10):
        # 너무 빠른 속도로 스크래핑하면 dart 가 막는다.
        # 랜덤을 추가하여 기본 interval 에 0.8 - 1.8배의 무작위시간을 추가한다.
        sec = int(interval * (random.random() + .8))
        print(f'Wait a {sec} secs...')
        time.sleep(sec)

    @staticmethod
    def ping_opendart(date=None, timeout=5) -> Tuple[str, str]:
        """
        date 날짜에 해당하는 https://opendart.fss.or.kr/의 접속상태를 확인하여 반환함.

        Messages:
        000 :정상
        010 :등록되지 않은 키입니다.
        011 :사용할 수 없는 키입니다. 오픈API에 등록되었으나, 일시적으로 사용 중지된 키를 통하여 검색하는 경우 발생합니다.
        012 :접근할 수 없는 IP입니다.
        013 :조회된 데이타가 없습니다.
        014 :파일이 존재하지 않습니다.
        020 :요청 제한을 초과하였습니다. 일반적으로는 10,000건 이상의 요청에 대하여 이 에러 메시지가 발생되나, 요청 제한이 다르게 설정된 경우에는 이에 준하여 발생됩니다.
        100 :필드의 부적절한 값입니다. 필드 설명에 없는 값을 사용한 경우에 발생하는 메시지입니다.
        101 :부적절한 접근입니다.
        800 :시스템 점검으로 인한 서비스가 중지 중입니다.
        900 :정의되지 않은 오류가 발생하였습니다.
        901 :사용자 계정의 개인정보 보유기간이 만료되어 사용할 수 없는 키입니다. 관리자 이메일(opendart@fss.or.kr)로 문의하시기 바랍니다.

        :return: tuple: (status, message)
        """
        if date is None:
            # 오늘 날짜를 Ymd 형식으로 변경
            date = datetime.now().strftime('%Y%m%d')
        assert tools.isYmd(date), "date의 형식이 맞지 않습니다.(%Y%m%d)"
        try:
            test_url = OverView.HEAD_URL + f'&end_de={date}'
            # print(test_url)
            m = requests.get(test_url, timeout=timeout,
                             headers={'User-Agent': random.choice(drivers.user_agents)}).json()
            return m['status'], m['message']
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            err_str = "Connection Error on opendart.fss.or.kr.."
            return '900', err_str

    def make_full_url(self, last_report='N', page_no=1) -> str:
        """
        인자에 해당하는 조건의 최종 url을 반환한다.
        &last_reprt_at : 최종보고서만 검색여부(Y or N) 기본값 : N
        &pblntf_ty : 공시유형

        :param page_no: 페이지번호
        :return: 최종 생성된 url 문자열
        """
        assert last_report in ['Y', 'N'], "last_report 인자가 올바르지 않습니다.(Y or N)"
        print(f'corp_code : {self.code}\tstart_date : {self.sdate}\tend_date : {self.edate}\tlast_report : {last_report}')

        # 최종 url을 만들기 위한 문장 요소들
        is_last = f'&last_reprt_at={last_report}'
        page_no = f'&page_no={page_no}'
        page_count = f'&page_count=100'  # 100이 최대임
        start_date = f'&bgn_de={self.sdate}' if self.sdate != '' else ''
        end_date = f'&end_de={self.edate}' if self.edate != '' else ''
        corp_code = f'&corp_code={self.code}' if self.code != '' else ''
        # pblntf_ty = f'&pblntf_ty={title_type}' if title_type != '' else ''

        final_url = ''.join(
            [OverView.HEAD_URL, is_last, page_no, page_count, start_date, end_date, corp_code])
        # print(f'final url : {final_url}')
        return final_url

    def get(self, save_to_file=False) -> List[Dict]:
        """
        dart에서 공시를 처음조회하면 한 페이지에 100개 아이템을 조회하는것이 최대라 모든 페이지를 조회해서 모든 아이템을 하나의 리스트로 반환하는 함수
        dart에서는 ddos공격에 매우 예민해서 user-agent를 바꿔가면서 사용해야하고 너무 빠른속도로 조회하면 안된다.
        :param save_to_file : self.SAVEFILENAME에 저장한다. 대부분 디버그용
        :return:
        """
        full_url = self.make_full_url()
        r_dict = requests.get(full_url, headers={'User-Agent': random.choice(drivers.user_agents)}).json()
        # print(r_dict)
        total_overviews = []
        if r_dict['status'] == '000':
            total_page = r_dict['total_page']
            print(f'Extracting all pages({total_page}) ')
            p = re.compile('&page_no=[0-9]+')

            for i in range(int(total_page)):
                nextpage_url = p.sub(f'&page_no={i + 1}', full_url)
                print(f'Page {i + 1}.. ', end='')
                # 첫번째 루프에서는 에러가 없기 때문에 대기시간 없이 넘어간다.
                OverView.random_sleep() if i != 0 else print()
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        total_overviews += requests.get(nextpage_url, timeout=(10, 30), headers={
                            'User-Agent': random.choice(drivers.user_agents)}).json()['list']
                        break  # 성공하면 루프 탈출
                    except requests.exceptions.ConnectionError as e:
                        print(f"Attempt {attempt + 1} failed: {e}")
                        time.sleep(2)  # 2초 대기 후 재시도
        elif r_dict['status'] == '013':
            # {'status': '013', 'message': '조회된 데이타가 없습니다.'}
            print(r_dict['message'])
        else:
            # 기타 에러 발생시 노티함.
            noti.telegram_to(botname='dart', text=r_dict['message'])
        if save_to_file:
            import json
            with open(self.SAVEFILENAME, 'w') as file:
                json.dump(total_overviews, file)
        return total_overviews


class PostProcess:
    useless_titles = ['기재정정', '첨부정정', '자회사의', '종속회사의', '기타경영사항', '첨부추가']

    @staticmethod
    def all_in_one(overviews: List[Dict]) -> List[Dict]:
        """
        항상 필요한 후처리 함수를 일괄 처리하는 함수
        :param overviews:
        :return:
        """
        from db_hj3415 import myredis
        # 오리지널에 링크추가
        overviews = PostProcess.add_doc_link(overviews)
        # 타이틀 공백제거
        overviews = PostProcess.refine_title(overviews)
        # 코스피와 코스닥만 추림
        overviews = PostProcess.gathering_kospi_kosdaq(overviews)
        # krx300 종목만 추림
        krx300 = myredis.Corps.list_all_codes()
        overviews = PostProcess.gathering_by_code(overviews, krx300)
        return overviews

    @staticmethod
    def add_doc_link(overviews: List[Dict]) -> List[Dict]:
        """
        공시 overview 딕셔너리에 문서링크를 조합하여 link라는 항목으로 추가해줍니다.
        :param overviews:
        :return:
        """
        # print(f"각 공시 딕셔너리에 문서 링크를 추가합니다.")
        header = 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo='
        for item in overviews:
            item['link'] = header + item['rcept_no']
        return overviews

    @staticmethod
    def refine_title(overviews: List[Dict]) -> List[Dict]:
        # print(f"각 공시 제목에 좌우 공백을 제거합니다.")
        for item in overviews:
            item['report_nm'] = item['report_nm'].strip()
        return overviews

    @staticmethod
    def filtering_title(overviews: List[Dict], filtering_words: list) -> List[Dict]:
        """
        공시 overview의 report_nm(타이틀)에 불필요한 단어를 포함한 것들은 제거하는 함수
        :param overviews:
        :param filtering_words:
        :return:
        """
        print(f"report_nm에서 {filtering_words}가 포함된 것은 뺍니다.")
        return_list = []
        for item in overviews:
            found = False
            for filter_word in filtering_words:
                if filter_word in item['report_nm']:
                    found = True
                    # print(filter_word, item['report_nm'])
                    break
            if not found:
                item['report_nm'] = item['report_nm'].replace(' ', '')
                return_list.append(item)
        return return_list

    @staticmethod
    def gathering_kospi_kosdaq(overviews: List[Dict]) -> List[Dict]:
        filter_words = ['Y', 'K']
        # print(f"corp_cls에서 {filter_words}(코스피, 코스닥)만 모읍니다.")
        return_list = []
        for item in overviews:
            for filter in filter_words:
                if filter == item['corp_cls']:
                    return_list.append(item)
                    break
        return return_list

    @staticmethod
    def gathering_by_code(overviews: List[Dict], codes: list) -> List[Dict]:
        # print(f"stock_code가 {codes}인 공시를 추출합니다..")
        return_list = []
        for code in codes:
            for item in overviews:
                if code == item['stock_code']:
                    # print(f"{code} / {item['report_nm']}을 추가합니다.")
                    return_list.append(item)
        return return_list














