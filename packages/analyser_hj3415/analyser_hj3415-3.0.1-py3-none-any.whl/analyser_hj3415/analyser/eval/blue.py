import os
from dataclasses import dataclass, asdict
from typing import Tuple
import math

from utils_hj3415 import tools, setup_logger
from db_hj3415 import myredis

from analyser_hj3415.analyser.eval.common import Tools


mylogger = setup_logger(__name__,'WARNING')
expire_time = tools.to_int(os.getenv('DEFAULT_EXPIRE_TIME_H', 48)) * 3600


@dataclass()
class BlueData:
    code: str
    name: str

    유동비율: float

    이자보상배율_r: float
    이자보상배율_dict: dict

    순운전자본회전율_r: float
    순운전자본회전율_dict: dict

    재고자산회전율_r: float
    재고자산회전율_dict: dict
    재고자산회전율_c106: dict

    순부채비율_r: float
    순부채비율_dict: dict

    score: list
    date: list


class Blue:
    def __init__(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Blue : 종목코드 ({code})")

        self.c101 = myredis.C101(code)
        self.c103 = myredis.C103(code, 'c103재무상태표q')
        self.c104 = myredis.C104(code, 'c104q')

        self.name = self.c101.get_name()
        self._code = code

    def __str__(self):
        return f"Blue({self.code}/{self.name})"

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Blue : 종목코드 변경({self.code} -> {code})")

        self.c101.code = code
        self.c103.code = code
        self.c104.code = code

        self.name = self.c101.get_name()
        self._code = code

    def _calc유동비율(self, pop_count: int, refresh: bool) -> Tuple[str, float]:
        """유동비율계산 - Blue에서 사용

        c104q에서 최근유동비율 찾아보고 유효하지 않거나 \n
        100이하인 경우에는수동으로 계산해서 다시 한번 평가해 본다.\n
        """
        mylogger.info(f'In the calc유동비율... refresh : {refresh}')
        self.c104.page = 'c104q'

        유동비율date, 유동비율value = self.c104.latest_value('유동비율', pop_count=pop_count)
        mylogger.info(f'{self} 유동비율 : {유동비율value}/({유동비율date})')

        if math.isnan(유동비율value) or 유동비율value < 100:
            유동자산date, 유동자산value = Tools.calc유동자산(self.c103, refresh)
            유동부채date, 유동부채value = Tools.calc유동부채(self.c103, refresh)

            self.c103.page = 'c103현금흐름표q'
            추정영업현금흐름date, 추정영업현금흐름value = self.c103.sum_recent_4q('영업활동으로인한현금흐름', refresh)
            mylogger.debug(f'{self} 계산전 유동비율 : {유동비율value} / ({유동비율date})')

            계산된유동비율 = 0
            try:
                계산된유동비율 = round(((유동자산value + 추정영업현금흐름value) / 유동부채value) * 100, 2)
            except ZeroDivisionError:
                mylogger.info(f'유동자산: {유동자산value} + 추정영업현금흐름: {추정영업현금흐름value} / 유동부채: {유동부채value}')
                계산된유동비율 = float('inf')
            finally:
                mylogger.debug(f'{self} 계산된 유동비율 : {계산된유동비율}')

                try:
                    date, *_ = Tools.date_set(유동자산date, 유동부채date, 추정영업현금흐름date)
                except ValueError:
                    # 날짜 데이터가 없는경우
                    date = ''
                mylogger.warning(f'{self} 유동비율 이상(100 이하 또는 nan) : {유동비율value} -> 재계산 : {계산된유동비율}')
                return date, 계산된유동비율
        else:
            return 유동비율date, 유동비율value

    def _score(self) -> list:
        return [0 ,]

    def _generate_data(self, refresh: bool) -> BlueData:
        d1, 유동비율 = self._calc유동비율(pop_count=3, refresh=refresh)
        mylogger.info(f'유동비율 {유동비율} / [{d1}]')

        재고자산회전율_c106 = myredis.C106.make_like_c106(self.code, 'c104q', '재고자산회전율', refresh)

        self.c104.page = 'c104y'
        _, 이자보상배율_dict = self.c104.find('이자보상배율', remove_yoy=True, refresh=refresh)
        _, 순운전자본회전율_dict = self.c104.find('순운전자본회전율', remove_yoy=True, refresh=refresh)
        _, 재고자산회전율_dict = self.c104.find('재고자산회전율', remove_yoy=True, refresh=refresh)
        _, 순부채비율_dict = self.c104.find('순부채비율', remove_yoy=True, refresh=refresh)

        self.c104.page = 'c104q'
        d6, 이자보상배율_r = self.c104.latest_value_pop2('이자보상배율', refresh)
        d7, 순운전자본회전율_r = self.c104.latest_value_pop2('순운전자본회전율', refresh)
        d8, 재고자산회전율_r = self.c104.latest_value_pop2('재고자산회전율', refresh)
        d9, 순부채비율_r = self.c104.latest_value_pop2('순부채비율', refresh)

        if len(이자보상배율_dict) == 0:
            mylogger.warning(f'empty dict - 이자보상배율 : {이자보상배율_r} / {이자보상배율_dict}')

        if len(순운전자본회전율_dict) == 0:
            mylogger.warning(f'empty dict - 순운전자본회전율 : {순운전자본회전율_r} / {순운전자본회전율_dict}')

        if len(재고자산회전율_dict) == 0:
            mylogger.warning(f'empty dict - 재고자산회전율 : {재고자산회전율_r} / {재고자산회전율_dict}')

        if len(순부채비율_dict) == 0:
            mylogger.warning(f'empty dict - 순부채비율 : {순부채비율_r} / {순부채비율_dict}')

        score = self._score()

        try:
            date_list = Tools.date_set(d1, d6, d7, d8, d9)
        except ValueError:
            # 날짜 데이터가 없는경우
            date_list = ['' ,]

        return BlueData(
            code= self.code,
            name= self.name,
            유동비율= 유동비율,
            이자보상배율_r= 이자보상배율_r,
            이자보상배율_dict= 이자보상배율_dict,

            순운전자본회전율_r= 순운전자본회전율_r,
            순운전자본회전율_dict= 순운전자본회전율_dict,

            재고자산회전율_r= 재고자산회전율_r,
            재고자산회전율_dict= 재고자산회전율_dict,
            재고자산회전율_c106= 재고자산회전율_c106,

            순부채비율_r= 순부채비율_r,
            순부채비율_dict= 순부채비율_dict,

            score= score,
            date= date_list,
        )

    def get(self, refresh = False, verbose = True) -> BlueData:
        """
        BlueData 형식의 데이터를 계산하여 리턴하고 레디스 캐시에 저장한다.
        :param refresh:
        :return:
        """
        redis_name = f"{self.code}_blue"
        mylogger.info(f"{self} BlueData를 레디스캐시에서 가져오거나 새로 생성합니다.. refresh : {refresh}")
        if verbose:
            print(f"{self} redisname: '{redis_name}' / refresh : {refresh} / expire_time : {expire_time /3600}h")

        def fetch_generate_data(refresh_in: bool) -> dict:
            return asdict(self._generate_data(refresh_in))

        return BlueData \
            (**myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_generate_data, refresh, timer=expire_time))
