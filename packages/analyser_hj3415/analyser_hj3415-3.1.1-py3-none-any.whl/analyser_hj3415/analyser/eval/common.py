import math
from typing import Tuple

from db_hj3415 import myredis
from utils_hj3415.tools import nan_to_zero
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')


class Tools:
    @staticmethod
    def sigmoid_score(deviation, a=1.0, b=2.0):
        """
        Calculates a normalized score using a sigmoid function based on the provided deviation value.

        This method applies the sigmoid function to a logarithmically transformed deviation value
        to map it to a range between 0 and 100. The shape of the sigmoid curve can be adjusted
        with parameters `a` and `b`.

        Parameters:
            deviation (float): The deviation value to be transformed. Must be a non-negative value.
            a (float): The steepness of the sigmoid curve. Default is 1.0.
            b (float): The x-offset for the sigmoid curve. Default is 2.0.

        Returns:
            float: A score between 0 and 100 derived from the provided deviation value.
        """
        # 예: x = log10(deviation + 1)
        x = math.log10(deviation + 1)
        s = 1 / (1 + math.exp(-a * (x - b)))  # 0~1 범위
        return s * 100  # 0~100 범위

    @staticmethod
    def log_score(deviation):
        """
            Compute and return the logarithmic score scaled by a constant factor.

            This method takes a numerical deviation value, adds one to it, computes its
            base-10 logarithm, and then multiplies the result by a constant factor of 33
            to scale the resulting logarithmic score.

            Parameters:
                deviation (float): The numerical deviation value to calculate the
                logarithmic score for. Should be a non-negative number.

            Returns:
                float: The scaled logarithmic score computed based on the input deviation.
        """
        return math.log10(deviation + 1) * 33

    @staticmethod
    def cal_deviation(v1: float, v2: float) -> float:
        """
            Calculates the percentage deviation between two values.

            This method computes the percentage deviation of the second value
            from the first value based on the formula:
            deviation = abs((v1 - v2) / v1) * 100. In the event the first value is
            zero (division by zero), the function will return NaN to signify
            an invalid computation.

            Parameters:
            v1 (float): The reference value. It represents the base for the relative
                        deviation calculation.
            v2 (float): The value to compare against the reference.

            Returns:
            float: The computed percentage deviation. Returns NaN if the reference
                   value (v1) is zero.
        """
        try:
            deviation = abs((v1 - v2) / v1) * 100
        except ZeroDivisionError:
            deviation = math.nan
        return deviation

    @staticmethod
    def date_set(*args) -> list:
        """
            인자로 받은 값의 비유효한 내용 제거(None,nan)하고 중복된 항목 제거하고 리스트로 반환한다.

            여기서 set의 의미는 집합을 뜻함

            Filters and returns a list of unique non-null, non-empty values from
            the provided arguments.

            This static method processes the input arguments to retain only unique
            values that are not empty strings, NaN values, or None. The result is
            returned as a list.

            Args:
                *args: Arbitrary positional arguments to be filtered.

            Returns:
                list: A list of unique values after filtering out invalid entries.
        """
        return [i for i in {*args} if i != "" and i is not math.nan and i is not None]

    @staticmethod
    def calc당기순이익(c103: myredis.C103, refresh: bool) -> Tuple[str, float]:
        """
            지배지분 당기순이익 계산

            일반적인 경우로는 직전 지배주주지분 당기순이익을 찾아서 반환한다.

            금융기관의 경우는 지배당기순이익이 없기 때문에 계산을 통해서 간접적으로 구한다.

            Calculates "지배당기순이익" (Controlling Comprehensive Income) based on the given
            financial data. The method retrieves or computes the value utilizing methods from
            the `myredis.C103` class. It handles missing or 'Not-a-Number' conditions by
            manually calculating from quarterly and annual financial figures. Logs the process
            at various stages for debugging and auditing.

            Args:
                c103 (myredis.C103): An instance containing financial data and utilities to
                    access specific data points for the targeted calculation.
                refresh (bool): A flag to determine whether or not to refresh the data
                    while accessing or computing financial values.

            Returns:
                Tuple[str, float]: A tuple where the first item is the most relevant date for
                    the calculated or retrieved value, and the second item is the calculated
                    or retrieved "지배당기순이익" (Controlling Comprehensive Income).
        """
        name = myredis.Corps(c103.code, 'c101').get_name(refresh=refresh)

        mylogger.info(f'{c103.code} / {name} Tools : 당기순이익 계산.. refresh : {refresh}')
        c103.page = 'c103재무상태표q'

        d1, 지배당기순이익 = c103.latest_value_pop2('*(지배)당기순이익', refresh)
        mylogger.debug(f"*(지배)당기순이익: {지배당기순이익}")

        if math.isnan(지배당기순이익):
            mylogger.warning(f"{c103.code} / {name} - (지배)당기순이익이 없는 종목. 수동으로 계산합니다.")
            c103.page = 'c103손익계산서q'
            d2, 최근4분기당기순이익 = c103.sum_recent_4q('당기순이익', refresh)
            mylogger.debug(f"{c103.code} / {name} - 최근4분기당기순이익 : {최근4분기당기순이익}")
            c103.page = 'c103재무상태표y'
            d3, 비지배당기순이익 = c103.latest_value_pop2('*(비지배)당기순이익', refresh)
            mylogger.debug(f"{c103.code} / {name} - 비지배당기순이익y : {비지배당기순이익}")
            # 가변리스트 언패킹으로 하나의 날짜만 사용하고 나머지는 버린다.
            # 여기서 *_는 “나머지 값을 다 무시하겠다”는 의미
            mylogger.debug(f"d2:{d2}, d3: {d3}")
            try:
                date, *_ = Tools.date_set(d2, d3)
            except ValueError:
                # 날짜 데이터가 없는경우
                date = ''
            계산된지배당기순이익 = round(최근4분기당기순이익 - nan_to_zero(비지배당기순이익), 1)
            mylogger.debug(f"{c103.code} / {name} - 계산된 지배당기순이익 : {계산된지배당기순이익}")
            return date, 계산된지배당기순이익
        else:
            return d1, 지배당기순이익

    @staticmethod
    def calc유동자산(c103: myredis.C103, refresh: bool) -> Tuple[str, float]:
        """
            유효한 유동자산 계산

            일반적인 경우로 유동자산을 찾아서 반환한다.

            금융기관의 경우는 간접적으로 계산한다.

            Calculates the current assets for a given company code.

            For a specified company, the function calculates the recent 4-quarter
            sum of current assets if available. If the data is not available or
            contains invalid values, it attempts to calculate the current assets
            manually using financial asset data such as cash equivalents, trading
            securities, available-for-sale securities, and held-to-maturity securities.

            Logs relevant information and warnings during the calculation process,
            including any cases where data is unavailable or a manual calculation
            is required.

            Parameters:
                c103 (myredis.C103): The instance representing financial data of a
                    specific company. This includes methods to extract and calculate
                    various data points.
                refresh (bool): Indicator flag to determine whether to refresh the
                    underlying data before performing calculations.

            Returns:
                Tuple[str, float]: A tuple containing the date associated with the
                    financial data and the calculated or retrieved value of current
                    assets. If dates are not available, the date field may be empty.
        """

        name = myredis.Corps(c103.code, 'c101').get_name(refresh=refresh)

        mylogger.info(f'{c103.code} / {name} Tools : 유동자산계산... refresh : {refresh}')
        c103.page = 'c103재무상태표q'

        d, 유동자산 = c103.sum_recent_4q('유동자산', refresh)
        if math.isnan(유동자산):
            mylogger.warning(f"{c103.code} / {name} - 유동자산이 없는 종목. 수동으로 계산합니다(금융관련업종일 가능성있음).")
            d1, v1 = c103.latest_value_pop2('현금및예치금', refresh)
            d2, v2 = c103.latest_value_pop2('단기매매금융자산', refresh)
            d3, v3 = c103.latest_value_pop2('매도가능금융자산', refresh)
            d4, v4 = c103.latest_value_pop2('만기보유금융자산', refresh)
            mylogger.debug(f'{c103.code} / {name} 현금및예치금 : {d1}, {v1}')
            mylogger.debug(f'{c103.code} / {name} 단기매매금융자산 : {d2}, {v2}')
            mylogger.debug(f'{c103.code} / {name} 매도가능금융자산 : {d3}, {v3}')
            mylogger.debug(f'{c103.code} / {name} 만기보유금융자산 : {d4}, {v4}')

            try:
                date, *_ = Tools.date_set(d1, d2, d3, d4)
            except ValueError:
                # 날짜 데이터가 없는경우
                date = ''
            계산된유동자산value = round(
                nan_to_zero(v1) + nan_to_zero(v2) + nan_to_zero(v3) + nan_to_zero(v4), 1)

            mylogger.info(f"{c103.code} / {name} - 계산된 유동자산 : {계산된유동자산value}")
            return date, 계산된유동자산value
        else:
            return d, 유동자산

    @staticmethod
    def calc유동부채(c103: myredis.C103, refresh: bool) -> Tuple[str, float]:
        """
            유효한 유동부채 계산

            일반적인 경우로 유동부채를 찾아서 반환한다.

            금융기관의 경우는 간접적으로 계산한다.

            Calculate '유동부채' (Current Liabilities) based on financial data of a specific entity.

            This static method computes the recent '유동부채' value either from the sum of recent four
            quarters using predefined keys or calculates manually if no valid data is available.
            It includes logging for intermediate steps and supports handling missing values by logging
            warnings and attempting a composed manual computation using alternative financial terms.

            Args:
                c103 (myredis.C103): The object containing financial data and operations for obtaining the required data.
                refresh (bool): A flag to indicate whether to fetch the latest data forcibly.

            Returns:
                Tuple[str, float]: A tuple containing the `date` of financial data and the computed '유동부채' value.
        """

        name = myredis.Corps(c103.code, 'c101').get_name(refresh=refresh)

        mylogger.info(f'{c103.code} / {name} Tools : 유동부채계산... refresh : {refresh}')
        c103.page = 'c103재무상태표q'

        d, 유동부채 = c103.sum_recent_4q('유동부채', refresh)
        if math.isnan(유동부채):
            mylogger.warning(f"{c103.code} / {name} - 유동부채가 없는 종목. 수동으로 계산합니다.")
            d1, v1 = c103.latest_value_pop2('당기손익인식(지정)금융부채', refresh)
            d2, v2 = c103.latest_value_pop2('당기손익-공정가치측정금융부채', refresh)
            d3, v3 = c103.latest_value_pop2('매도파생결합증권', refresh)
            d4, v4 = c103.latest_value_pop2('단기매매금융부채', refresh)
            mylogger.debug(f'{c103.code} / {name} 당기손익인식(지정)금융부채 : {d1}, {v1}')
            mylogger.debug(f'{c103.code} / {name} 당기손익-공정가치측정금융부채 : {d2}, {v2}')
            mylogger.debug(f'{c103.code} / {name} 매도파생결합증권 : {d3}, {v3}')
            mylogger.debug(f'{c103.code} / {name} 단기매매금융부채 : {d4}, {v4}')

            try:
                date, *_ = Tools.date_set(d1, d2, d3, d4)
            except ValueError:
                # 날짜 데이터가 없는경우
                date = ''
            계산된유동부채value = round(
                nan_to_zero(v1) + nan_to_zero(v2) + nan_to_zero(v3) + nan_to_zero(v4), 1)

            mylogger.info(f"{c103.code} / {name} - 계산된 유동부채 : {계산된유동부채value}")
            return date, 계산된유동부채value
        else:
            return d, 유동부채


"""
- 각분기의 합이 연이 아닌 타이틀(즉 sum_4q를 사용하면 안됨)
'*(지배)당기순이익'
'*(비지배)당기순이익'
'장기차입금'
'현금및예치금'
'매도가능금융자산'
'매도파생결합증권'
'만기보유금융자산'
'당기손익-공정가치측정금융부채'
'당기손익인식(지정)금융부채'
'단기매매금융자산'
'단기매매금융부채'
'예수부채'
'차입부채'
'기타부채'
'보험계약부채(책임준비금)'
'*CAPEX'
'ROE'
"""

"""
- sum_4q를 사용해도 되는 타이틀
'자산총계'
'당기순이익'
'유동자산'
'유동부채'
'비유동부채'

'영업활동으로인한현금흐름'
'재무활동으로인한현금흐름'
'ROIC'
"""
