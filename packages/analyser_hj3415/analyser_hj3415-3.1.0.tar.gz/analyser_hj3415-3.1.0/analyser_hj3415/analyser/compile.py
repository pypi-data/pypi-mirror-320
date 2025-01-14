import os
from collections import OrderedDict
from typing import Union

from db_hj3415 import myredis,mymongo
from utils_hj3415 import tools, setup_logger

from analyser_hj3415.analyser import tsa
from analyser_hj3415.analyser import eval

mylogger = setup_logger(__name__,'WARNING')
expire_time = tools.to_int(os.getenv('DEFAULT_EXPIRE_TIME_H', 48)) * 3600


class Compile:
    def __init__(self, code: str, expect_earn=0.06):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        self._code = code
        self.name = mymongo.Corps.get_name(code)
        self.red = eval.Red(code, expect_earn)
        self.mil = eval.Mil(code)
        self.prophet = tsa.CorpProphet(code)

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.info(f'change code : {self.code} -> {code}')
        self._code = code
        self.name = mymongo.Corps.get_name(code)
        self.red.code = code
        self.mil.code = code
        self.prophet.code = code

    def get(self, refresh=False) -> dict:
        print(f"{self.code}/{self.name}의 compiling을 시작합니다.")
        redis_name = self.code + '_compile_scores'
        print(
            f"redisname: '{redis_name}' / refresh : {refresh} / expire_time : {expire_time/3600}h")

        def fetch_compile_scores() -> dict:
            mylogger.info("Red score 계산중..")
            red_score = self.red.get(verbose=False).score

            mylogger.info("Mil data 계산중..")
            mil_data = self.mil.get(verbose=False)

            mylogger.info("\tProphet 최근 데이터 조회중..")
            trading_action, prophet_score = self.prophet.scoring()

            return {
                'name': self.name,
                'red_score': red_score,
                '이익지표': mil_data.이익지표,
                '주주수익률': mil_data.주주수익률,
                'trading_action': trading_action,
                'prophet_score': prophet_score,
            }
        data_dict = myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_compile_scores, timer=expire_time)
        return data_dict

    @staticmethod
    def prophet_ranking(refresh=False, top: Union[int, str]='all') -> OrderedDict:

        print("**** Start Compiling scores and sorting... ****")
        redis_name = 'prophet_ranking'

        print(
            f"redisname: '{redis_name}' / refresh : {refresh} / expire_time : {expire_time/3600}h")

        def fetch_ranking() -> dict:
            data = {}
            c = Compile('005930')
            for code in myredis.Corps.list_all_codes():
                try:
                    c.code = code
                except ValueError:
                    mylogger.error(f'prophet ranking error : {code}')
                    continue
                scores= c.get(refresh=refresh)
                print(f'{code} compiled : {scores}')
                data[code] = scores
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

    @staticmethod
    def analyse_lstm_topn(refresh: bool, top=40):
        ranking_topn = Compile.prophet_ranking(refresh=False, top=top)
        mylogger.info(ranking_topn)
        corp_lstm = tsa.CorpLSTM('005930')
        print(f"*** LSTM prediction redis cashing top{top} items ***")
        for i, (code, _) in enumerate(ranking_topn.items()):
            corp_lstm.code = code
            print(f"{i + 1}. {corp_lstm.code}/{corp_lstm.name}")
            corp_lstm.initializing()
            corp_lstm.get_final_predictions(refresh=refresh, num=5)

    @staticmethod
    def red_ranking(expect_earn: float = 0.06, refresh=False) -> OrderedDict:
        # 이전 expect earn 과 비교하여 다르거나 없으면 강제 refresh 설정
        redis_name = 'red_ranking_prev_expect_earn'
        pee = tools.to_float(myredis.Base.get_value(redis_name))
        if pee != expect_earn:
            # expect earn의 이전 계산값이 없거나 이전 값과 다르면 새로 계산
            mylogger.warning(
                f"expect earn : {expect_earn} / prev expect earn : {pee} 두 값이 달라 refresh = True"
            )
            myredis.Base.set_value(redis_name, str(expect_earn))
            refresh = True

        print("**** Start red_ranking... ****")
        redis_name = 'red_ranking'
        print(
            f"redisname: '{redis_name}' / expect_earn: {expect_earn} / refresh : {refresh} / expire_time : {expire_time / 3600}h")

        def fetch_ranking(refresh_in: bool) -> dict:
            data = {}
            red = eval.Red(code='005930', expect_earn=expect_earn)
            for i, code in enumerate(myredis.Corps.list_all_codes()):
                red.code = code
                red_score = red.get(refresh=refresh_in, verbose=False).score
                if red_score > 0:
                    data[code] = red_score
                    print(f"{i}: {red} - {red_score}")
            return data

        data_dict = myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_ranking, refresh, timer=expire_time)

        return OrderedDict(sorted(data_dict.items(), key=lambda item: item[1], reverse=True))

