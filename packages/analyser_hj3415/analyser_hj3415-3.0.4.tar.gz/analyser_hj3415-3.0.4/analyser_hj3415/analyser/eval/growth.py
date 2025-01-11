import os
from dataclasses import dataclass, asdict

from utils_hj3415 import tools, setup_logger
from db_hj3415 import myredis

from analyser_hj3415.analyser.eval.common import Tools


mylogger = setup_logger(__name__,'WARNING')
expire_time = tools.to_int(os.getenv('DEFAULT_EXPIRE_TIME_H', 48)) * 3600


@dataclass()
class GrowthData:
    code: str
    name: str

    매출액증가율_r: float
    매출액증가율_dict: dict

    영업이익률_c106: dict

    score: list
    date: list


class Growth:
    def __init__(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Growth : 종목코드 ({code})")

        self.c101 = myredis.C101(code)
        self.c104 = myredis.C104(code, 'c104q')
        self.c106 = myredis.C106(code, 'c106q')

        self.name = self.c101.get_name()
        self._code = code

    def __str__(self):
        return f"Growth({self.code}/{self.name})"

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.debug(f"Growth : 종목코드 변경({self.code} -> {code})")

        self.c101.code = code
        self.c104.code = code
        self.c106.code = code

        self.name = self.c101.get_name()
        self._code = code

    def _score(self) -> list:
        return [0,]

    def _generate_data(self, refresh=False) -> GrowthData:
        self.c104.page = 'c104y'
        _, 매출액증가율_dict = self.c104.find('매출액증가율', remove_yoy=True, refresh=refresh)

        self.c104.page = 'c104q'
        d2, 매출액증가율_r = self.c104.latest_value_pop2('매출액증가율')

        mylogger.info(f'매출액증가율 : {매출액증가율_r} {매출액증가율_dict}')

        # c106 에서 타 기업과 영업이익률 비교
        self.c106.page = 'c106y'
        영업이익률_c106 = self.c106.find('영업이익률', refresh)

        score = self._score()

        try:
            date_list = Tools.date_set(d2)
        except ValueError:
            # 날짜 데이터가 없는경우
            date_list = ['', ]

        return GrowthData(
            code= self.code,
            name= self.name,

            매출액증가율_r= 매출액증가율_r,
            매출액증가율_dict= 매출액증가율_dict,

            영업이익률_c106= 영업이익률_c106,

            score= score,
            date= date_list,
        )

    def get(self, refresh = False, verbose = True) -> GrowthData:
        """
        GrowthData 형식의 데이터를 계산하여 리턴하고 레디스 캐시에 저장한다.
        :param refresh:
        :return:
        """
        redis_name = f"{self.code}_growth"
        mylogger.info(f"{self} GrowthData를 레디스캐시에서 가져오거나 새로 생성합니다.. refresh : {refresh}")
        if verbose:
            print(f"{self} redisname: '{redis_name}' / refresh : {refresh} / expire_time : {expire_time/3600}h")

        def fetch_generate_data(refresh_in: bool) -> dict:
            return asdict(self._generate_data(refresh_in))

        return GrowthData(**myredis.Base.fetch_and_cache_data(redis_name, refresh, fetch_generate_data, refresh, timer=expire_time))
