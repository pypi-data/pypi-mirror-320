import os
import datetime
from collections import OrderedDict

from db_hj3415 import myredis
from utils_hj3415 import tools, setup_logger

from analyser_hj3415.analyser import tsa
from analyser_hj3415.analyser import eval

mylogger = setup_logger(__name__,'WARNING')
expire_time = tools.to_int(os.getenv('DEFAULT_EXPIRE_TIME_H', 48)) * 3600


class Score:
    def __init__(self, code):
        self._code = code
        self.c101 = myredis.C101(code)
        self.name = self.c101.get_name()
        self.c108 = myredis.C108(code)
        self.dart = myredis.Dart(code)
        self.red = eval.Red(code)
        self.mil = eval.Mil(code)
        self.lstm = tsa.MyLSTM(code)
        self.prophet = tsa.MyProphet(code)

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.info(f'change code : {self.code} -> {code}')
        self._code = code
        self.c101.code = code
        self.name = self.c101.get_name()
        self.c108.code = code
        self.dart.code = code
        self.red.code = code
        self.mil.code = code
        self.lstm.code = code
        self.prophet.code = code

    def get(self, refresh=False) -> dict:
        """
        한 종목의 각분야 평가를 모아서 딕셔너리 형태로 반환함.
        redis_name = self.code + '_score'

        Returns:
            dict: A dictionary containing the following key-value pairs:
                - 'name': str - 종목명
                - '시가총액': str - 시가총액
                - 'is_update_c108': bool - 최근 3일 이내에 c108이 없데이트 되었는가
                - 'red_score': float - Red score
                - '이익지표': float - Mil의 이익지표
                - '주주수익률': float - Mil의 주주수익률
                - 'is_lstm_up': Union[bool, None] - lstm 예측치가 상승인지 아닌지, returns None - 데이터가 없으면..
                - 'prophet_score': int - prophet score
        """
        print(f"{self.code}/{self.name}의 scoring을 시작합니다.")
        redis_name = self.code + '_score'
        print(
            f"redisname: '{redis_name}' / refresh : {refresh} / expire_time : {expire_time/3600}h")

        def fetch_score() -> dict:
            mylogger.info("시가총액 데이터 추출중..")
            시가총액 = tools.format_large_number(int(self.c101.get_recent()['시가총액']))

            mylogger.info("C108 최근 데이터 추출중..")
            # c108이 최근에 업데이트 되었는지...
            c108_recent_date = self.c108.get_recent_date()
            # print('code - ', code, ' | c108 recent date - ', c108_recent_date.date())
            if c108_recent_date is None:
                is_update_c108 = False
            else:
                is_update_c108 = tools.is_within_last_n_days(c108_recent_date,3)

            mylogger.info("Red score 계산중..")
            red_score = self.red.get(verbose=False).score

            mylogger.info("Mil data 계산중..")
            mil_data = self.mil.get(verbose=False)

            mylogger.info("Lstm 최근 데이터 조회중..")
            if myredis.Base.exists(f'{self.code}_mylstm_predictions'):
                is_lstm_up = self.lstm.is_up()
            else:
                is_lstm_up = None

            mylogger.info("\tProphet 최근 데이터 조회중..")
            prophet_score = self.prophet.scoring()

            return {
                'name': self.name,
                '시가총액': 시가총액,
                'is_update_c108': is_update_c108,
                'red_score': red_score,
                '이익지표': mil_data.이익지표,
                '주주수익률': mil_data.주주수익률,
                'is_lstm_up': is_lstm_up,
                'prophet_score': prophet_score,
            }
        data_dict = myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_score, timer=expire_time)
        return data_dict

    @classmethod
    def ranking(self, refresh=False, top='all') -> OrderedDict:
        """
            prophet score 기준으로 정렬하여 ordered dict로 반환함

            Parameters:
                refresh (bool): Specifies whether to refresh the ranking data. Defaults
                    to `False`.
                top (Union[str, int]): Determines how many top rankings to return.
                    Defaults to `'all'`. If an integer is provided, it limits the
                    ranking to the specified count.

            Returns:
                OrderedDict: A dictionary containing the rankings, sorted in
                    descending order by `prophet_score`.

            Raises:
                ValueError: Raised if the parameter `top` is neither `'all'` nor an
                    integer.
        """
        print("**** Start score_ranking... ****")
        redis_name = 'score_ranking'

        print(
            f"redisname: '{redis_name}' / refresh : {refresh} / expire_time : {expire_time/3600}h")

        def fetch_ranking() -> dict:
            data = {}
            s = Score('005930')
            for code in myredis.Corps.list_all_codes():
                try:
                    s.code = code
                except ValueError:
                    mylogger.error(f'score ranking error : {code}')
                    continue
                score = s.get(refresh=refresh)
                data[code] = score
            return data

        data_dict = myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_ranking, timer=expire_time)

        # prophet_score를 기준으로 정렬
        ranking = OrderedDict(sorted(data_dict.items(), key=lambda x: x[1]['prophet_score'], reverse=True))

        if top == 'all':
            return ranking
        else:
            if isinstance(top, int):
                return OrderedDict(list(ranking.items())[:top])
            else:
                raise ValueError("top 인자는 'all' 이나 int형 이어야 합니다.")
