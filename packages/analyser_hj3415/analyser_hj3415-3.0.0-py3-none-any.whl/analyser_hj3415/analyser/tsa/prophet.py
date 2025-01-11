from datetime import datetime, timedelta
from typing import Optional
import yfinance as yf
import pandas as pd
from prophet import Prophet
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt  # Matplotlib 수동 임포트
import plotly.graph_objs as go
from plotly.offline import plot

from utils_hj3415 import tools, setup_logger
from db_hj3415 import myredis

from analyser_hj3415.analyser import eval

mylogger = setup_logger(__name__,'WARNING')


class MyProphet:
    def __init__(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        self.scaler = StandardScaler()

        self.model = Prophet()
        self._code = code
        self.name = myredis.Corps(code, 'c101').get_name()
        self.raw_data = self._get_raw_data()
        self.df_real = self._preprocessing_for_prophet()
        self.df_forecast = self._make_forecast()

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, code: str):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        mylogger.info(f'change code : {self.code} -> {code}')
        self.model = Prophet()
        self._code = code
        self.name = myredis.Corps(code, 'c101').get_name()
        self.raw_data = self._get_raw_data()
        self.df_real = self._preprocessing_for_prophet()
        self.df_forecast = self._make_forecast()

    @staticmethod
    def is_valid_date(date_string):
        try:
            # %Y-%m-%d 형식으로 문자열을 datetime 객체로 변환 시도
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            # 변환이 실패하면 ValueError가 발생, 형식이 맞지 않음
            return False

    def _get_raw_data(self) -> pd.DataFrame:
        """
        야후에서 해당 종목의 4년간 주가 raw data를 받아온다.
        :return:
        """
        # 오늘 날짜 가져오기
        today = datetime.today()

        # 4년 전 날짜 계산 (4년 = 365일 * 4)
        four_years_ago = today - timedelta(days=365 * 4)

        return yf.download(
            self.code + '.KS',
            start=four_years_ago.strftime('%Y-%m-%d'),
            end=today.strftime('%Y-%m-%d')
        )

    def _preprocessing_for_prophet(self) -> pd.DataFrame:
        """
        Prophet이 사용할 수 있도록 데이터 준비
        ds는 날짜, y는 주가
        :return:
        """
        df = self.raw_data[['Close', 'Volume']].reset_index()
        df.columns = ['ds', 'y', 'volume']  # Prophet의 형식에 맞게 열 이름 변경

        # ds 열에서 타임존 제거
        df['ds'] = df['ds'].dt.tz_localize(None)

        # 추가 변수를 정규화
        df['volume_scaled'] = self.scaler.fit_transform(df[['volume']])
        mylogger.debug('_preprocessing_for_prophet')
        mylogger.debug(df)
        return df

    def _make_forecast(self) -> pd.DataFrame:
        # 정규화된 'volume_scaled' 변수를 외부 변수로 추가
        self.model.add_regressor('volume_scaled')

        self.model.fit(self.df_real)

        # 향후 180일 동안의 주가 예측
        future = self.model.make_future_dataframe(periods=180)
        mylogger.debug('_make_forecast_future')
        mylogger.debug(future)

        # 미래 데이터에 거래량 추가 (평균 거래량을 사용해 정규화)
        future_volume = pd.DataFrame({'volume': [self.raw_data['Volume'].mean()] * len(future)})
        future['volume_scaled'] = self.scaler.transform(future_volume[['volume']])

        forecast = self.model.predict(future)
        mylogger.debug('_make_forecast')
        mylogger.debug(forecast)
        return forecast

    def get_yhat(self) -> dict:
        """
        최근 날짜의 예측데이터를 반환한다.
        :return: {'ds':..., 'yhat':.., 'yhat_lower':.., 'yhat_upper':..,}
        """
        df = self.df_forecast
        last_real_date = self.df_real.iloc[-1]['ds']
        mylogger.info(last_real_date)
        yhat_dict = df[df['ds']==last_real_date].iloc[0][['ds', 'yhat_lower', 'yhat_upper', 'yhat']].to_dict()
        mylogger.info(yhat_dict)
        return yhat_dict

    def visualization(self):
        # 예측 결과 출력
        print(self.df_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())
        # 예측 결과 시각화 (Matplotlib 사용)
        fig = self.model.plot(self.df_forecast)
        # 추세 및 계절성 시각화
        fig2 = self.model.plot_components(self.df_forecast)
        plt.show()  # 시각화 창 띄우기

    def export(self, to="str") -> Optional[str]:
        """
        prophet과 plotly로 그래프를 그려서 html을 문자열로 반환
        :param to: str, png, htmlfile
        :return:
        """
        # Plotly를 사용한 시각화
        fig = go.Figure()

        # 실제 데이터
        fig.add_trace(go.Scatter(x=self.df_real['ds'], y=self.df_real['y'], mode='markers', name='실제주가'))
        # 예측 데이터
        fig.add_trace(go.Scatter(x=self.df_forecast['ds'], y=self.df_forecast['yhat'], mode='lines', name='예측치'))

        # 상한/하한 구간
        fig.add_trace(
            go.Scatter(x=self.df_forecast['ds'], y=self.df_forecast['yhat_upper'], fill=None, mode='lines', name='상한'))
        fig.add_trace(
            go.Scatter(x=self.df_forecast['ds'], y=self.df_forecast['yhat_lower'], fill='tonexty', mode='lines', name='하한'))

        fig.update_layout(
            # title=f'{self.code} {self.name} 주가 예측 그래프(prophet)',
            xaxis_title='일자',
            yaxis_title='주가(원)',
            xaxis = dict(
                tickformat='%Y/%m',  # X축을 '연/월' 형식으로 표시
            ),
            yaxis = dict(
                tickformat=".0f",  # 소수점 없이 원래 숫자 표시
            ),
            showlegend=False,
        )

        if to == 'str':
            # 그래프 HTML로 변환 (string 형식으로 저장)
            graph_html = plot(fig, output_type='div')
            return graph_html
        elif to == 'png':
            # 그래프를 PNG 파일로 저장
            fig.write_image(f"myprophet_{self.code}.png")
            return None
        elif to == 'htmlfile':
            # 그래프를 HTML로 저장
            plot(fig, filename=f'myprophet_{self.code}.html', auto_open=False)
            return None
        else:
            Exception("to 인자가 맞지 않습니다.")

    def scoring(self) -> int:
        """
        prophet의 yhat_lower 예측치와 주가를 비교하여 주가가 낮으면 양의 점수를 높으면 음의 점수를 준다.

        Returns:
            int: The calculated score based on the deviation between the recent price
            and the expected lower limit.

        Raises:
            AttributeError: Raised if the necessary attributes like `df_real` or methods like `get_yhat`
            are not correctly set or implemented.
            KeyError: Raised if the expected keys (`'yhat_lower'` or `'y'`) are not found in the data involved.
            ValueError: Raised if the format of data does not conform to expected structure for calculations.
        """
        last_real_data = self.df_real.iloc[-1]
        recent_price = last_real_data['y']
        recent_date = datetime.strftime(last_real_data['ds'], '%Y-%m-%d')
        yhat_dict = self.get_yhat()
        mylogger.info(f'recent_price: {recent_price}, yhat_dict: {yhat_dict}')
        yhat_lower = int(yhat_dict['yhat_lower'])
        deviation = int(eval.Tools.cal_deviation(recent_price, yhat_lower))
        if recent_price > yhat_lower:
            score = -deviation
        else:
            score = deviation
        mylogger.info(f"{self.code}/{self.name} date: {recent_date} 가격:{recent_price} 기대하한값:{yhat_lower} 편차:{deviation} score:{score}")
        return score

