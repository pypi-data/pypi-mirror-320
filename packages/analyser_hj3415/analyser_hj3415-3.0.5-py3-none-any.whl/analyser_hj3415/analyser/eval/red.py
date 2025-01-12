import os
from dataclasses import dataclass, asdict
from typing import Tuple
import math

from utils_hj3415 import tools, setup_logger
from db_hj3415 import myredis

from analyser_hj3415.analyser.eval.common import Tools


mylogger = setup_logger(__name__,'WARNING')
expire_time = tools.to_int(os.getenv('DEFAULT_EXPIRE_TIME_H', 48)) * 3600


@dataclass
class RedData:
    """
    A data structure for financial data representation and calculations.

    This class is designed to encapsulate financial details related to a company,
    including calculations for business value, property value, debt evaluation, and
    associated metrics. It validates specific attributes upon initialization and is
    useful for financial data analysis.

    Attributes:
        code (str): A 6-digit numeric string representing the company or entity's code.
        name (str): The name of the company or entity.
        사업가치 (float): Business value calculated as net income attributable to controlling
            shareholders divided by expected return rate.
        지배주주당기순이익 (float): Net income attributable to controlling shareholders.
        expect_earn (float): Expected return rate.
        재산가치 (float): Property value calculated as current assets minus 1.2
            times current liabilities, plus fixed assets under investment properties.
        유동자산 (float): Current assets of the company.
        유동부채 (float): Current liabilities of the company.
        투자자산 (float): Investment assets within fixed assets.
        투자부동산 (float): Investment real estate property.
        부채평가 (float): Debt evaluation, specifically focusing on non-current liabilities.
        발행주식수 (int): Number of issued shares by the company.
        date (list): List of dates relevant to the financial data.
        red_price (float): Red price associated with the company or entity.
        score (int): Score or rating given to the company or entity.

    Raises:
        ValueError: If the 'code' attribute is not a 6-digit numeric string.
    """
    code: str
    name: str

    # 사업가치 계산 - 지배주주지분 당기순이익 / 기대수익률
    사업가치: float
    지배주주당기순이익: float
    expect_earn: float

    # 재산가치 계산 - 유동자산 - (유동부채*1.2) + 고정자산중 투자자산
    재산가치: float
    유동자산: float
    유동부채: float
    투자자산: float
    투자부동산: float

    # 부채평가 - 비유동부채
    부채평가: float

    # 발행주식수
    발행주식수: int

    date: list
    주가: float
    red_price: float
    score: int

    def __post_init__(self):
        if not tools.is_6digit(self.code):
            raise ValueError(f"code는 6자리 숫자형 문자열이어야합니다. (입력값: {self.code})")


class Red:
    """
    Represents a financial analysis object with methods to calculate metrics
    and gather data related to a specific code.

    The Red class is designed to interact with specific data sources and provide
    tools for financial calculations and analysis. This includes fetching and
    processing information related to liabilities, assets, stock prices, and
    other financial indicators. The class facilitates both specific calculations
    such as 비유동부채(Non-current Liability) and the generation of comprehensive
    financial datasets.
    """


    def __init__(self, code: str, expect_earn: float = 0.06):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Red : 초기화 ({code})")
        self.c101 = myredis.C101(code)
        self.c103 = myredis.C103(code, 'c103재무상태표q')

        self.name = self.c101.get_name()
        self.recent_price = tools.to_float(self.c101.get_recent()['주가'])
        self._code = code

        self.expect_earn = expect_earn

    def __str__(self):
        return f"Red({self.code}/{self.name})"

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Red : 종목코드 변경({self.code} -> {code})")
        self.c101.code = code
        self.c103.code = code

        self.name = self.c101.get_name()
        self.recent_price = tools.to_float(self.c101.get_recent()['주가'])
        self._code = code

    def _calc비유동부채(self, refresh: bool) -> Tuple[str, float]:
        """유효한 비유동부채 계산

        일반적인 경우로 비유동부채를 찾아서 반환한다.\n
        금융기관의 경우는 간접적으로 계산한다.\n
        """
        mylogger.info(f'In the calc비유동부채... refresh : {refresh}')
        self.c103.page = 'c103재무상태표q'

        d, 비유동부채 = self.c103.sum_recent_4q('비유동부채', refresh)
        if math.isnan(비유동부채):
            mylogger.warning(f"{self} - 비유동부채가 없는 종목. 수동으로 계산합니다.")
            # 보험관련업종은 예수부채가 없는대신 보험계약부채가 있다...
            d1, v1 = self.c103.latest_value_pop2('예수부채', refresh)
            d2, v2 = self.c103.latest_value_pop2('보험계약부채(책임준비금)', refresh)
            d3, v3 = self.c103.latest_value_pop2('차입부채', refresh)
            d4, v4 = self.c103.latest_value_pop2('기타부채', refresh)
            mylogger.debug(f'예수부채 : {d1}, {v1}')
            mylogger.debug(f'보험계약부채(책임준비금) : {d2}, {v2}')
            mylogger.debug(f'차입부채 : {d3}, {v3}')
            mylogger.debug(f'기타부채 : {d4}, {v4}')

            try:
                date, *_ = Tools.date_set(d1, d2, d3, d4)
            except ValueError:
                # 날짜 데이터가 없는경우
                date = ''
            계산된비유동부채value = round(tools.nan_to_zero(v1) + tools.nan_to_zero(v2) + tools.nan_to_zero(v3) + tools.nan_to_zero(v4),1)
            mylogger.info(f"{self} - 계산된 비유동부채 : {계산된비유동부채value}")
            return date, 계산된비유동부채value
        else:
            return d, 비유동부채

    def _score(self, red_price: int) -> int:
        """red price와 최근 주가의 괴리율 파악

            Returns:
                int : 주가와 red price 비교한 괴리율
            """
        if math.isnan(self.recent_price):
            return 0

        deviation = Tools.cal_deviation(self.recent_price, red_price)

        score = tools.to_int(Tools.sigmoid_score(deviation))
        #score = tools.to_int(Tools.log_score(deviation))
        if self.recent_price >= red_price:
            score = -score

        mylogger.debug(f"최근주가 : {self.recent_price} red가격 : {red_price} 괴리율 : {tools.to_int(deviation)} score : {score}")

        return score

    def _generate_data(self, refresh: bool) -> RedData:
        d1, 지배주주당기순이익 = Tools.calc당기순이익(self.c103, refresh)
        mylogger.debug(f"{self} 지배주주당기순이익: {지배주주당기순이익}")
        d2, 유동자산 = Tools.calc유동자산(self.c103, refresh)
        d3, 유동부채 = Tools.calc유동부채(self.c103, refresh)
        d4, 부채평가 = self._calc비유동부채(refresh)

        self.c103.page = 'c103재무상태표q'
        d5, 투자자산 = self.c103.latest_value_pop2('투자자산', refresh)
        d6, 투자부동산 = self.c103.latest_value_pop2('투자부동산', refresh)

        # 사업가치 계산 - 지배주주지분 당기순이익 / 기대수익률
        사업가치 = round(지배주주당기순이익 / self.expect_earn, 2)

        # 재산가치 계산 - 유동자산 - (유동부채*1.2) + 고정자산중 투자자산
        재산가치 = round(유동자산 - (유동부채 * 1.2) + tools.nan_to_zero(투자자산) + tools.nan_to_zero(투자부동산), 2)

        _, 발행주식수 = self.c103.latest_value_pop2('발행주식수', refresh)
        if math.isnan(발행주식수):
            발행주식수 = tools.to_int(self.c101.get_recent(refresh).get('발행주식'))
        else:
            발행주식수 = 발행주식수 * 1000

        try:
            red_price = round(((사업가치 + 재산가치 - 부채평가) * 100000000) / 발행주식수)
        except (ZeroDivisionError, ValueError):
            red_price = math.nan

        score = self._score(red_price)

        try:
            date_list = Tools.date_set(d1, d2, d3, d4)
        except ValueError:
            # 날짜 데이터가 없는경우
            date_list = ['',]

        return RedData(
            code = self.code,
            name = self.name,
            사업가치 = 사업가치,
            지배주주당기순이익 = 지배주주당기순이익,
            expect_earn = self.expect_earn,
            재산가치 = 재산가치,
            유동자산 = 유동자산,
            유동부채 = 유동부채,
            투자자산 = 투자자산,
            투자부동산 = 투자부동산,
            부채평가 = 부채평가,
            발행주식수 = 발행주식수,
            date = date_list,
            red_price = red_price,
            주가 = self.recent_price,
            score = score,
        )

    def get(self, refresh = False, verbose = True) -> RedData:
        """
        RedData 형식의 데이터를 계산하여 리턴하고 레디스 캐시에 저장한다.

        redis_name = f"{self.code}_red_data"

        Fetch or create RedData from Redis cache.

        This function attempts to retrieve the RedData from a Redis cache. If the data is
        not available or if a refresh is requested, it generates new data and caches
        them back in Redis. The function logs its operations and can provide
        verbose output when specified.

        Parameters:
        refresh : bool, optional
            Whether to refresh and generate new data instead of using the cached data.
        verbose : bool, optional
            Whether to enable verbose logging/display of additional runtime information.

        Returns:
        RedData
            The RedData object either retrieved from the cache or newly generated.

        """
        redis_name = f"{self.code}_red_data"
        mylogger.info(f"{self} RedData를 레디스캐시에서 가져오거나 새로 생성합니다.. refresh : {refresh}")
        if verbose:
            print(f"{self} redisname: '{redis_name}' / expect_earn: {self.expect_earn} / refresh : {refresh} / expire_time : {expire_time/3600}h")

        def fetch_generate_data(refresh_in: bool) -> dict:
            return asdict(self._generate_data(refresh_in))

        return RedData(**myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_generate_data, refresh, timer=expire_time))

