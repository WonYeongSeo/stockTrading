
import time
from datetime import datetime
from kiwoom import kiwoom_condition, kiwoom_rest_api as api
from kiwoom.stock import stock_log
from helper import util
from helper.constants import CONST_BUY_TOTAL_AMOUNT, CONST_DEPOSIT_MINIMUM_AMOUNT, CONST_EXCEL_DB_TIME
from helper.constants import CONST_RISE_START_TIME, CONST_RISE_END_TIME, CONST_RISE_SLEEP_TIME
from helper.constants import CONST_SELL_LOSS_RISE_RATE, CONST_SELL_EARNING_RATE, CONST_SELL_EXCLUDE_RATE
from log.file_logging import condition_logging, error_logging
# ---------------------------------------------------------------------------------------------------------------------------------
__today = util.today('%Y%m%d')

# 조건검색  ---------------------------------------------------------------------------------------------------------------------------------
def auto_trading(token, old_holding_codes, DEPOSIT_MIN_AMOUNT, BUY_TOTAL_AMOUNT) :
    print(datetime.now(), '***** 자동매매를 시작합니다.')

    # 예수금 최저 금액 set
    if DEPOSIT_MIN_AMOUNT :
        DEPOSIT_MIN_AMOUNT = int(DEPOSIT_MIN_AMOUNT)
    else :
        DEPOSIT_MIN_AMOUNT = CONST_DEPOSIT_MINIMUM_AMOUNT

    # 종목당 매수할 금액 set
    if BUY_TOTAL_AMOUNT :
        BUY_TOTAL_AMOUNT = int(BUY_TOTAL_AMOUNT)
    else :
        BUY_TOTAL_AMOUNT = CONST_BUY_TOTAL_AMOUNT

    # 매수종목 리스트
    buys = []
    sell_standbys = []

    is_excel_db_logging = False

    while True :
        try :
            # 보유종목코드 리스트
            holdings = api.stock_holdings(token, __today)

            # 오늘 매수하고 보유한 종목 리스트만 추출 - 매도 대상 종목임
            today_holdings = util.today_holdings(old_holding_codes, holdings)

            # 금일 매매 마감
            if datetime.now() > CONST_RISE_END_TIME :
                # 오늘 매수한 종목 전부 매도처리
                print(datetime.now(), '*** 오늘 매수한 종목 전부 매도 처리')
                process_sell_all(token, today_holdings)

                # 테스트 시 excel logging/ database save 하지 않기 위해 추가
                if datetime.now() < CONST_EXCEL_DB_TIME :
                    print(datetime.now(), '**', CONST_EXCEL_DB_TIME, '에 excel/DB logging 하기 위해 대기')

                    __logging_delay_time = CONST_EXCEL_DB_TIME - datetime.now()
                    time.sleep(int(__logging_delay_time.total_seconds()))
                    is_excel_db_logging = True

                break

            # 상승주 매매
            elif datetime.now() > CONST_RISE_START_TIME :
                # 당일 매수한 종목에 대한 매도처리
                process_sell(token, today_holdings, sell_standbys)

                # 검색한 종목에 대한 매수처리
                process_buy_rise(token, holdings, buys, DEPOSIT_MIN_AMOUNT, BUY_TOTAL_AMOUNT)

                time.sleep(CONST_RISE_SLEEP_TIME)

        except Exception as e :
            print(f'### 자동매매 중 에러발생!! : {e}')
            error_logging(' 자동매매 중 에러 : ' + str(e))
            time.sleep(CONST_RISE_SLEEP_TIME)

    return is_excel_db_logging

# 상승주 조건검색된 종목 중 매수조건에 해당되면 매수 -------------------------------------------------------------------------------------------------------
def process_buy_rise(token, holdings, buys, DEPOSIT_MIN_AMOUNT, BUY_TOTAL_AMOUNT) :
    try :
        __seq = '0' # 3분급등조건
        __temp_stocks = []
        __stocks = kiwoom_condition.search(token, __seq, BUY_TOTAL_AMOUNT, __temp_stocks)

        if __stocks :
            for s in __stocks :
                # 매수 시 보유 종목은 제외
                __already_holding = []
                if holdings :
                    __already_holding = list(filter(lambda x: x.code == s.code, holdings))

                # 오늘 매수했던 종목은 제외
                __today_buys = []
                if buys :
                    __today_buys = list(filter(lambda x: x.code == s.code, buys))

                if __already_holding or __today_buys:
                    continue

                # 예수금 조회
                __buy_total_prc = api.deposit(token)

                # 예수금이 최저 잔고금액 이상이면 매수
                if __buy_total_prc > DEPOSIT_MIN_AMOUNT :
                    if __buy_total_prc > BUY_TOTAL_AMOUNT :
                        __buy_total_prc = BUY_TOTAL_AMOUNT

                    # 매수할 단가 구하기
                    __buyprice = util.get_buy_price(s.price)

                    # 종목당 매수할 총 금액이 매수금액보다 큰 경우에만 매수 호출
                    if __buy_total_prc > __buyprice :
                        __buy_qty = int(__buy_total_prc / __buyprice)

                        if __buy_qty > 0 :
                            __flu_rt = api.get_flu_rt(token, s.code)
                            stock_log(s.code, s.name, __buyprice, __buy_qty, 'BUY', s.price, 0, 0, __flu_rt, datetime.now())
                            # 매수 호출
                            __buy_flag = api.buy(token, s.code, s.name, str(__buyprice), str(__buy_qty), '0', False)

                            if __buy_flag :
                                # 매수종목 리스트에 추가
                                buys.append(s)

            try :
                # 파일에 저장
                condition_logging(False, ' 검색종목 ' +  str(list(map(lambda x : str(x.code) + '/' + str(x.name) + '/' + str(x.price), __stocks))))

            except Exception as e :
                print(f'### 상승주 조건검색 파일 저장 중 에러발생!! : {e}')
                error_logging(' 상승주 조건검색 파일 저장 중 에러 : ' + str(e))

    except Exception as e :
        print(f'### 상승주 매수 중 에러발생!! : {e}')
        error_logging(' 상승주 매수 중 에러 : ' + str(e))

# 당일매수종목에 대한 매도 -----------------------------------------------------------------------------------------------------------------------------
def process_sell(token, today_holdings, sell_standbys) :
    try :
        if today_holdings :
            for t in today_holdings :
                # 현재 등락률
                __flu_rt = api.get_flu_rt(token, t.code)
                # 매도 제외 체크
                if __flu_rt < CONST_SELL_EXCLUDE_RATE :
                    __earn_rate = float(t.earn_rate)

                    __is_sell = False

                    # 이익보존 체크
                    __today_sell_standby = []
                    if sell_standbys :
                        __today_sell_standby = list(filter(lambda x: x.code == t.code, sell_standbys))

                    # 이익보존대상이면서 기준 수익률 미만이면 매도
                    if __today_sell_standby :
                        if __earn_rate < CONST_SELL_EARNING_RATE :
                            __is_sell = True
                            sell_standbys.remove(t.code)
                        else :
                            continue
                    else :
                        # 수익률이 기준 수익률 이상이면 이익보존 대상
                        if __earn_rate > CONST_SELL_EARNING_RATE  :
                            sell_standbys.append(t.code)
                            continue
                        # 수익률이 기준 손절율 이하이면 매도
                        elif __earn_rate < CONST_SELL_LOSS_RISE_RATE :
                            __is_sell = True

                    if __is_sell :
                        __sell_qty = int(t.qty)

                        if __sell_qty > 0 :
                            api.sell(token, t.code, t.name, str(__sell_qty))
                            stock_log(t.code, t.name, 0, __sell_qty, 'SELL', t.cur_prc, 0, __earn_rate, __flu_rt, '')

    except Exception as e :
        print(f'### 당일매수종목 매도 중 에러발생!! : {e}')
        error_logging(' 당일매수종목 매도 중 에러 : ' + str(e))

# 당일매수종목에 대한 전량 매도 -----------------------------------------------------------------------------------------------------------------------------
def process_sell_all(token, today_holdings) :
    try :
        if today_holdings :
            for t in today_holdings :
                __flu_rt = api.get_flu_rt(token, t.code) # 현재 등락률
                # 매도 제외 체크
                if __flu_rt < CONST_SELL_EXCLUDE_RATE :
                    __earn_rate = float(t.earn_rate)
                    __sell_qty = int(t.qty)

                    if __sell_qty > 0 :
                        stock_log(t.code, t.name, 0, __sell_qty, 'SELL', t.cur_prc, 0, __earn_rate, __flu_rt, '')
                        api.sell(token, t.code, t.name, str(__sell_qty), False)

                time.sleep(0.5)

    except Exception as e :
        print(f'### 당일매수종목 전량 매도 중 에러발생!! : {e}')
        error_logging(' 당일매수종목 전량 매도 중 에러 : ' + str(e))
