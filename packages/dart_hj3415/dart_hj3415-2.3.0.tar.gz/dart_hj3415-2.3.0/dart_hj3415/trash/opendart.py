import requests
import re
import time
import pandas as pd
import pprint
from db_hj3415 import mongo2
from util_hj3415 import noti, utils



class DartInfo:
    def __init__(self, client,
                 code: str = '',
                 name: str = '',
                 rtitle: str = '',
                 rno: str = '',
                 rdt: str = '',
                 url: str = '',
                 price: int = 0,
                 per: float = 0.0,
                 pbr: float = 0.0,
                 high_52w: int = 0,
                 low_52w: int = 0):
        self.client = client
        self.유통주식 = None
        self.__code = ''
        self.__rdt = ''
        self.code = code
        self.rdt = rdt
        self.name = name
        self.rtitle = rtitle
        self.rno = rno
        self.url = url
        self.price = price
        self.per = per
        self.pbr = pbr
        self.high_52w = high_52w
        self.low_52w = low_52w

    @staticmethod
    def 유통주식계산(client, code: str, date: str) -> float:
        """
        c101에서 date에 해당하는 날짜의 유통주식을 계산하고 만약 그날짜가 없으면 최신날짜로 유통주식을 계산한다.\n
        :param code: ex - 005930
        :param date: ex - 20211011
        :return:
        """
        if not utils.is_6digit(code) or not utils.isYmd(date):
            raise ValueError(f'Invalid values - {code}/{date}')
        # c101을 통해서 실제 유통주식의 수를 반환한다.
        c101_db = mongo2.C101(client, code)
        c101_dict = c101_db.find(date=date)
        if len(c101_dict) == 0:
            c101_dict = c101_db.get_recent()

        logger.debug(pprint.pformat(f'In def 유통주식계산...c101 : {c101_dict}', width=80))

        try:
            return round((float(c101_dict['유통비율']) / 100) * float(c101_dict['발행주식']))
        except (ValueError, KeyError):
            return float('nan')

    @property
    def code(self) -> str:
        return self.__code

    @code.setter
    def code(self, code):
        self.__code = code
        if self.__code != '' and self.__rdt != '':
            self.유통주식 = self.유통주식계산(self.client, self.__code, self.__rdt)

    @property
    def rdt(self) -> str:
        return self.__rdt

    @rdt.setter
    def rdt(self, rdt):
        self.__rdt = rdt
        if self.__code != '' and self.__rdt != '':
            self.유통주식 = self.유통주식계산(self.client, self.__code, self.__rdt)

    def __str__(self):
        s = f'코드: {self.code}\t종목명: {self.name}\n'
        s += f'rtitle: {self.rtitle}\n'
        s += f'rno: {self.rno}\n'
        s += f'rdt: {self.rdt}\n'
        s += f'url: {self.url}\n'
        s += f'price: {self.price}\thigh_52w: {self.high_52w}\tlow_52w: {self.low_52w}\n'
        s += f'per: {self.per}\tpbr: {self.pbr}\n'
        s += f'유통주식: {self.유통주식}'
        return s


class Dart:
    """
    dart를 analysis에서 사용하는 dartinfo형식과 데이터베이스에 저장하는 df형식으로 2가지 함수가 필요하다.
    """
    URL = 'https://opendart.fss.or.kr/api/list.json'
    KEY = 'f93473130995a146c3e9e7b250b0f4d4c4dc1513'

    def __init__(self, client):
        self.client = client



    def make_dartinfos(self, sdate: str = '', edate: str = '', code: str = '', title: str = '', filter_needless_title: bool = True) -> list:
        """
        analysis에서 사용하는 data.DartInfo 클래스의 리스트를 반환한다.
        내부적으로 get_df()를 이용해 데이터프레임을 생성하고 c101의 데이터를 추가하여 합하여 만든다.
        """
        df = self.make_df(sdate, edate, code, title, filter_needless_title)
        logger.debug(df)
        dartinfo_list = []
        for i, namedtuple in enumerate(df.itertuples()):
            print(f'{i+1}. Making a darinfo {namedtuple.stock_code} {namedtuple.corp_name} ')
            dartinfo = DartInfo(self.client)

            # dart 로부터 데이터를 채운다.
            dartinfo.code = namedtuple.stock_code
            dartinfo.name = namedtuple.corp_name
            dartinfo.rtitle = namedtuple.report_nm
            dartinfo.rno = namedtuple.rcept_no
            dartinfo.rdt = namedtuple.rcept_dt
            dartinfo.url = 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo=' + str(namedtuple.rcept_no)

            # c101 로부터 데이터를 채운다.
            try:
                c101 = mongo2.C101(self.client, namedtuple.stock_code).get_recent()
                logger.debug(c101)
                dartinfo.price = utils.to_int(c101['주가'])
                dartinfo.per = c101['PER'] if c101['PER'] is not None else None
                dartinfo.pbr = c101['PBR'] if c101['PBR'] is not None else None
                dartinfo.high_52w = utils.to_int(c101['최고52주'])
                dartinfo.low_52w = utils.to_int(c101['최저52주'])
            except (StopIteration, KeyError):
                # 해당 코드의 c101이 없는 경우
                dartinfo.price = None
                dartinfo.per = None
                dartinfo.pbr = None
                dartinfo.high_52w = None
                dartinfo.low_52w = None
            logger.debug(dartinfo)
            dartinfo_list.append(dartinfo)
        return dartinfo_list





    def set_refresh_count(self, date: str) -> int:
        """
        '분기보고서', '반기보고서', '사업보고서' 의 세 타이틀의 데이터프레임을 받고 합쳐서 하나로 만든다.
        이 데이터프레임을 통해서 refresh 데이터베이스에 저장한다.

        Args:
            date (str): 리프레스 데이터를 만들기 원하는 날짜

        Returns:
            int: 저장된 데이터베이스 아이템 갯수
        """
        if not utils.isYmd(date):
            raise Exception(f'Invalid date format : {date}(%Y%m%d)')

        status, message = self.server_test(date)
        if status == '000':
            df1 = self.make_df(edate=date, title='분기보고서')
            df2 = self.make_df(edate=date, title='반기보고서')
            df3 = self.make_df(edate=date, title='사업보고서')
            report_df = pd.concat([df1, df2, df3], ignore_index=True)
            logger.info(report_df.to_string())
        elif status == '013':
            # 013 :조회된 데이타가 없습니다.의 경우 - 공휴일
            logger.error(f'{status}: {message}')
            report_df = pd.DataFrame()
        else:
            logger.error(f'{status}: {message}')
            noti.telegram_to(botname='dart', text=message)
            report_df = pd.DataFrame()

        crefresh = mongo2.CRefresh(self.client, '005930')
        for i, row in report_df.iterrows():
            crefresh.code = row['stock_code']
            crefresh.set_count(date)
        return len(report_df)


