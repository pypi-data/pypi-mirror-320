import os
from dataclasses import dataclass, asdict
from typing import Tuple
import math

from utils_hj3415 import tools, setup_logger
from db_hj3415 import myredis, mymongo

from analyser_hj3415.analyser.eval.common import Tools


mylogger = setup_logger(__name__,'WARNING')
expire_time = tools.to_int(os.getenv('DEFAULT_EXPIRE_TIME_H', 48)) * 3600


@dataclass
class MilData:
    code: str
    name: str

    시가총액억: float

    주주수익률: float
    재무활동현금흐름: float

    이익지표: float
    영업활동현금흐름: float
    지배주주당기순이익: float

    #투자수익률
    roic_r: float
    roic_dict: dict
    roe_r: float
    roe_106: dict
    roa_r: float

    #가치지표
    fcf_dict: dict
    pfcf_dict: dict
    pcr_dict: dict

    score: list
    date: list


class Mil:
    def __init__(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Mil : 종목코드 ({code})")

        self.c101 = myredis.C101(code)
        self.c103 = myredis.C103(code, 'c103현금흐름표q')
        self.c104 = myredis.C104(code, 'c104q')
        self.c106 = myredis.C106(code, 'c106q')

        self.name = self.c101.get_name()
        self._code = code

    def __str__(self):
        return f"Mil({self.code}/{self.name})"

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Mil : 종목코드 변경({self.code} -> {code})")

        self.c101.code = code
        self.c103.code = code
        self.c104.code = code
        self.c106.code = code

        self.name = self.c101.get_name()
        self._code = code

    def get_marketcap억(self, refresh: bool) -> float:
        """
        시가총액(억원) 반환
        :return:
        """
        c101r = self.c101.get_recent(refresh)
        시가총액 = tools.to_int(tools.to_float(c101r.get('시가총액', math.nan)) / 100000000)
        mylogger.debug(f"시가총액: {시가총액}억원")
        return 시가총액

    def _calc주주수익률(self, 시가총액_억: float, refresh: bool) -> Tuple[str, float, float]:
        self.c103.page = 'c103현금흐름표q'
        d, 재무활동현금흐름 = self.c103.sum_recent_4q('재무활동으로인한현금흐름', refresh)
        try:
            주주수익률 = round((재무활동현금흐름 / 시가총액_억 * -100), 2)
        except ZeroDivisionError:
            주주수익률 = math.nan
            mylogger.warning(f'{self} 주주수익률: {주주수익률} 재무활동현금흐름: {재무활동현금흐름}')
        return d, 주주수익률, 재무활동현금흐름

    def _calc이익지표(self, 시가총액_억: float, refresh: bool) -> Tuple[str, float, float, float]:
        d1, 지배주주당기순이익 = Tools.calc당기순이익(self.c103, refresh)
        self.c103.page = 'c103현금흐름표q'
        d2, 영업활동현금흐름 = self.c103.sum_recent_4q('영업활동으로인한현금흐름', refresh)
        try:
            이익지표 = round(((지배주주당기순이익 - 영업활동현금흐름) / 시가총액_억) * 100, 2)
        except ZeroDivisionError:
            이익지표 = math.nan
            mylogger.warning(f'{self} 이익지표: {이익지표} 영업활동현금흐름: {영업활동현금흐름} 지배주주당기순이익: {지배주주당기순이익}')
        try:
            date, *_ = Tools.date_set(d1, d2)
        except ValueError:
            # 날짜 데이터가 없는경우
            date = ''
        return date , 이익지표, 영업활동현금흐름, 지배주주당기순이익

    def _calc투자수익률(self, refresh: bool) -> tuple:
        self.c104.page = 'c104q'
        self.c106.page = 'c106q'
        d1, roic_r = self.c104.sum_recent_4q('ROIC', refresh)
        _, roic_dict = self.c104.find('ROIC', remove_yoy=True, del_unnamed_key=True, refresh=refresh)
        d2, roe_r = self.c104.latest_value_pop2('ROE', refresh)
        roe106 = self.c106.find('ROE', refresh)
        d3, roa_r = self.c104.latest_value_pop2('ROA', refresh)

        try:
            date, *_ = Tools.date_set(d1, d2, d3)
        except ValueError:
            # 날짜 데이터가 없는경우
            date = ''

        return date, roic_r, roic_dict, roe_r, roe106, roa_r

    def _calcFCF(self, refresh: bool) -> dict:
        """
        FCF 계산
        Returns:
            dict: 계산된 fcf 딕셔너리 또는 영업현금흐름 없는 경우 - {}

        Note:
            CAPEX 가 없는 업종은 영업활동현금흐름을 그대로 사용한다.\n

        """
        self.c103.page = 'c103현금흐름표y'
        _, 영업활동현금흐름_dict = self.c103.find('영업활동으로인한현금흐름', remove_yoy=True, del_unnamed_key=True, refresh=refresh)

        self.c103.page = 'c103재무상태표y'
        _, capex = self.c103.find('*CAPEX', remove_yoy=True, del_unnamed_key=True, refresh=refresh)

        mylogger.debug(f'영업활동현금흐름 {영업활동현금흐름_dict}')
        mylogger.debug(f'CAPEX {capex}')

        if len(영업활동현금흐름_dict) == 0:
            return {}

        if len(capex) == 0:
            # CAPEX 가 없는 업종은 영업활동현금흐름을 그대로 사용한다.
            mylogger.warning(f"{self} - CAPEX가 없는 업종으로 영업현금흐름을 그대로 사용합니다..")
            return 영업활동현금흐름_dict

        # 영업 활동으로 인한 현금 흐름에서 CAPEX 를 각 연도별로 빼주어 fcf 를 구하고 리턴값으로 fcf 딕셔너리를 반환한다.
        fcf_dict = {}
        for i in range(len(영업활동현금흐름_dict)):
            # 영업활동현금흐름에서 아이템을 하나씩 꺼내서 CAPEX 전체와 비교하여 같으면 차를 구해서 fcf_dict 에 추가한다.
            영업활동현금흐름date, 영업활동현금흐름value = 영업활동현금흐름_dict.popitem()
            # 해당 연도의 capex 가 없는 경우도 있어 일단 capex를 0으로 치고 먼저 추가한다.
            fcf_dict[영업활동현금흐름date] = 영업활동현금흐름value
            for CAPEXdate, CAPEXvalue in capex.items():
                if 영업활동현금흐름date == CAPEXdate:
                    fcf_dict[영업활동현금흐름date] = round(영업활동현금흐름value - CAPEXvalue, 2)

        mylogger.debug(f'fcf_dict {fcf_dict}')
        # 연도순으로 정렬해서 딕셔너리로 반환한다.
        return dict(sorted(fcf_dict.items(), reverse=False))

    def _calcPFCF(self, 시가총액_억: float, fcf_dict: dict) -> dict:
        """Price to Free Cash Flow Ratio(주가 대비 자유 현금 흐름 비율)계산

            PFCF = 시가총액 / FCF

            Note:
                https://www.investopedia.com/terms/p/pricetofreecashflow.asp
            """
        if math.isnan(시가총액_억):
            mylogger.warning(f"{self} - 시가총액이 nan으로 pFCF를 계산할수 없습니다.")
            return {}

        # pfcf 계산
        pfcf_dict = {}
        for FCFdate, FCFvalue in fcf_dict.items():
            if FCFvalue == 0:
                pfcf_dict[FCFdate] = math.nan
            else:
                pfcf_dict[FCFdate] = round(시가총액_억 / FCFvalue, 2)

        pfcf_dict = mymongo.C1034.del_unnamed_key(pfcf_dict)

        mylogger.debug(f'pfcf_dict : {pfcf_dict}')
        return pfcf_dict

    def _calc가치지표(self, 시가총액_억: float, refresh: bool) -> tuple:
        self.c104.page = 'c104q'

        fcf_dict = self._calcFCF(refresh)
        pfcf_dict = self._calcPFCF(시가총액_억, fcf_dict)

        d, pcr_dict = self.c104.find('PCR', remove_yoy=True, del_unnamed_key=True, refresh=refresh)
        return d, fcf_dict, pfcf_dict, pcr_dict

    def _score(self) -> list:
        return [0,]

    def _generate_data(self, refresh: bool) -> MilData:
        mylogger.info(f"In generate_data..refresh : {refresh}")
        시가총액_억 = self.get_marketcap억(refresh)
        mylogger.info(f"{self} 시가총액(억) : {시가총액_억}")

        d1, 주주수익률, 재무활동현금흐름 = self._calc주주수익률(시가총액_억, refresh)
        mylogger.info(f"{self} 주주수익률 : {주주수익률}, {d1}")

        d2, 이익지표, 영업활동현금흐름, 지배주주당기순이익 = self._calc이익지표(시가총액_억, refresh)
        mylogger.info(f"{self} 이익지표 : {이익지표}, {d2}")

        d3, roic_r, roic_dict, roe_r, roe106, roa_r = self._calc투자수익률(refresh)
        d4, fcf_dict, pfcf_dict, pcr_dict = self._calc가치지표(시가총액_억, refresh)

        score = self._score()

        try:
            date_list = Tools.date_set(d1, d2, d3, d4)
        except ValueError:
            # 날짜 데이터가 없는경우
            date_list = ['',]

        return MilData(
            code= self.code,
            name= self.name,

            시가총액억= 시가총액_억,

            주주수익률= 주주수익률,
            재무활동현금흐름= 재무활동현금흐름,

            이익지표= 이익지표,
            영업활동현금흐름= 영업활동현금흐름,
            지배주주당기순이익= 지배주주당기순이익,

            roic_r= roic_r,
            roic_dict= roic_dict,
            roe_r= roe_r,
            roe_106= roe106,
            roa_r= roa_r,

            fcf_dict= fcf_dict,
            pfcf_dict= pfcf_dict,
            pcr_dict= pcr_dict,

            score= score,
            date = date_list,
        )

    def get(self, refresh = False, verbose = True) -> MilData:
        """
        MilData 형식의 데이터를 계산하여 리턴하고 레디스 캐시에 저장한다.
        :param refresh:
        :return:
        """
        redis_name = f"{self.code}_mil"
        mylogger.info(f"{self} MilData를 레디스캐시에서 가져오거나 새로 생성합니다.. refresh : {refresh}")
        if verbose:
            print(f"{self} redisname: '{redis_name}' / refresh : {refresh} / expire_time : {expire_time/3600}h")

        def fetch_generate_data(refresh_in: bool) -> dict:
            return asdict(self._generate_data(refresh_in))

        return MilData(**myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_generate_data, refresh, timer=expire_time))