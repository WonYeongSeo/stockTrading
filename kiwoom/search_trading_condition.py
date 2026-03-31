
import time
from datetime import datetime
from kiwoom import kiwoom_condition, kiwoom_rest_api as api
from kiwoom.stock import stock_log
from helper import util
from helper.constants import CONST_BUY_TOTAL_AMOUNT, CONST_DEPOSIT_MINIMUM_AMOUNT, CONST_EXCEL_DB_TIME
from helper.constants import CONST_BUY_DELAY_TIME,CONST_START_TIME, CONST_END_TIME, CONST_SLEEP_TIME
from helper.constants import CONST_SELL_LOSS_RATE, CONST_SELL_EARNING_RATE, CONST_SELL_EXCLUDE_RATE, CONST_SELL_PRICE_RATE
from log.file_logging import search_logging, error_logging, analysis_logging
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
    buys = old_holding_codes
    # 조건검색종목 리스트
    conditions = []
    # 매도대기 리스트
    sell_standbys = []

    # sells = []

    is_excel_db_logging = False

    while True :
        try :
            # 보유종목코드 리스트
            holdings = api.stock_holdings(token, __today)

            # 오늘 매수하고 보유한 종목 리스트만 추출 - 매도 대상 종목임
            today_holdings = util.today_holdings(old_holding_codes, holdings)

            # 금일 매매 마감
            if datetime.now() > CONST_END_TIME :
                if datetime.now() < CONST_EXCEL_DB_TIME :
                    # 오늘 매수한 종목 전부 매도처리
                    print(datetime.now(), '*** 오늘 매수한 종목 전부 매도 처리')
                    process_sell_all(token, today_holdings)

                    # 오늘 매수한 종목 중 수익중인 종목 전부 매도처리
                    # print(datetime.now(), '*** 오늘 매수한 종목 중 수익중인 종목 전부 매도 처리')
                    # process_sell_earning_all(token, old_holding_codes, sells)

                    # excel/DB logging 하기 위해 대기
                    print(datetime.now(), '**', CONST_EXCEL_DB_TIME, '에 excel/DB logging 하기 위해 대기')
                    __logging_delay_time = CONST_EXCEL_DB_TIME - datetime.now()
                    time.sleep(int(__logging_delay_time.total_seconds()))
                    is_excel_db_logging = True

                break

            # 매매
            elif datetime.now() > CONST_START_TIME :
                try :
                    analysis_logging('')
                except Exception as ae :
                    print(f'현재시간 파일 저장 중 에러 : {ae}')

                # 검색한 종목에 대해 매수 후 바로 매도주문
                # process_buy_immediate_sell(token, buys, sells, DEPOSIT_MIN_AMOUNT, BUY_TOTAL_AMOUNT)

                # 당일 매수한 종목에 대한 매도처리
                process_sell(token, today_holdings, sell_standbys)

                # 검색한 종목에 대한 매수처리
                process_buy(token, conditions,holdings, buys, DEPOSIT_MIN_AMOUNT, BUY_TOTAL_AMOUNT)

                # 분석용 검색 -------------------------------------------------------------------------------------------------------
                # process_analysis(token, BUY_TOTAL_AMOUNT)

                time.sleep(CONST_SLEEP_TIME)

        except Exception as e :
            print(f'### 자동매매 중 에러발생!! : {e}')
            error_logging(' 자동매매 중 에러 : ' + str(e))
            time.sleep(CONST_SLEEP_TIME)

    return is_excel_db_logging

# 조건검색된 종목 중 매수조건에 해당되면 매수 -------------------------------------------------------------------------------------------------------
def process_buy(token, conditions,holdings, buys, DEPOSIT_MIN_AMOUNT, BUY_TOTAL_AMOUNT) :
    try :
        __seq = '0'
        __temp_stocks = []
        __stocks = kiwoom_condition.search(token, __seq, BUY_TOTAL_AMOUNT, __temp_stocks)

        if __stocks :
            if not conditions :
                for s in __stocks :
                    __already_holding = []
                    if holdings :
                        __already_holding = list(filter(lambda x: x.code == s.code, holdings))
                    if not __already_holding and int(s.price) < CONST_BUY_TOTAL_AMOUNT :
                        conditions.append(s)
            else :
                for s in __stocks :
                    # 매수 시 보유 종목은 제외
                    __already_holding = []
                    if holdings :
                        __already_holding = list(filter(lambda x: x.code == s.code, holdings))

                    # 오늘 매수했던 종목은 제외
                    __today_buys = []
                    if buys :
                        __today_buys = list(filter(lambda x: x == s.code, buys))

                    if __already_holding or __today_buys:
                        continue

                    # 예수금 조회
                    __buy_total_prc = api.deposit(token)

                    # 예수금이 최저 잔고금액 이상이면 매수
                    if __buy_total_prc > DEPOSIT_MIN_AMOUNT :
                        __is_buy = True
                    else :
                        __is_buy = False

                    list_c = list(filter(lambda x: x.code == s.code, conditions))

                    if list_c :
                        c = list_c[0]

                        # 이전 검색 금액보다 현재 검색 금액이 큰 경우 매수
                        if __is_buy and int(s.price) > int(c.price) :
                            __time_second = util.get_diff_timesecond(datetime.now(), c.time)

                            # 매수대기시간 이후 포착 시 매수
                            if __time_second > CONST_BUY_DELAY_TIME :
                                if __buy_total_prc > BUY_TOTAL_AMOUNT :
                                    __buy_total_prc = BUY_TOTAL_AMOUNT

                                # 매수할 단가 구하기
                                __buyprice = util.get_buy_price(s.price)

                                # 종목당 매수할 총 금액이 매수금액보다 큰 경우에만 매수 호출
                                if __buy_total_prc > __buyprice :
                                    __buy_qty = int(__buy_total_prc / __buyprice)

                                    if __buy_qty > 0 :
                                        __flu_rt = api.get_flu_rt(token, s.code)
                                        stock_log(s.code, s.name, __buyprice, __buy_qty, 'BUY', s.price, 0, 0, __flu_rt, s.time)
                                        # 매수 호출
                                        __buy_flag = api.buy(token, s.code, s.name, __buyprice, __buy_qty, '0')

                                        if __buy_flag :
                                            # 매수종목 리스트에 추가
                                            buys.append(s.code)
                                            # 조건검색종목 리스트에서 제외
                                            conditions.remove(c)
                                elif int(s.price) > int(c.price) :
                                    c.price = s.price
                            elif int(s.price) > int(c.price) :
                                c.price = s.price
                        elif int(s.price) > int(c.price) :
                            c.price = s.price
                    elif int(s.price) < CONST_BUY_TOTAL_AMOUNT :
                        conditions.append(s)

            try :
                # 파일에 저장
                search_logging(' 검색종목 ' +  str(list(map(lambda x : str(x.code) + '/' + str(x.name) + '/' + str(x.price), conditions))))

            except Exception as fe :
                print(f'### 상승주 조건검색 파일 저장 중 에러발생!! : {fe}')
                error_logging(' 상승주 조건검색 파일 저장 중 에러 : ' + str(fe))

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
                        __today_sell_standby = list(filter(lambda x: x == t.code, sell_standbys))

                    # 이익보존대상이면서 기준 수익률 미만이면 매도
                    if __today_sell_standby :
                        if __earn_rate < float(CONST_SELL_EARNING_RATE - 2) :
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
                        elif __earn_rate < CONST_SELL_LOSS_RATE :
                            __is_sell = True

                    if __is_sell and int(t.qty) > 0 :
                        api.sell(token, t.code, t.name, '', t.qty, '3')
                        stock_log(t.code, t.name, 0, t.qty, 'SELL', t.cur_prc, 0, __earn_rate, __flu_rt, '')

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
                if __flu_rt < CONST_SELL_EXCLUDE_RATE and int(t.qty) > 0 :
                    stock_log(t.code, t.name, 0, t.qty, 'SELL', t.cur_prc, 0, t.earn_rate, __flu_rt, '')
                    api.sell(token, t.code, t.name, '', t.qty, '3')

                time.sleep(1)

    except Exception as e :
        print(f'### 당일매수종목 전량 매도 중 에러발생!! : {e}')
        error_logging(' 당일매수종목 전량 매도 중 에러 : ' + str(e))


# 분석용 검색 -------------------------------------------------------------------------------------------------------
def process_analysis(token, BUY_TOTAL_AMOUNT) :
    try :
        __seq_analysis = '1' # 분석용
        __temp_stocks = []
        __analysis = kiwoom_condition.search(token, __seq_analysis, BUY_TOTAL_AMOUNT, __temp_stocks)

        try :
            if __analysis :
                # 파일에 저장
                analysis_logging(' 검색종목 ' +  str(list(map(lambda x : str(x.code) + '/' + str(x.name) + '/' + str(x.price), __analysis))))

        except Exception as fe :
            print(f'### 분석용 검색 파일 저장 중 에러발생!! : {fe}')
            error_logging(' 분석용 검색 파일 저장 중 에러 : ' + str(fe))

    except Exception as e :
        print(f'### 분석용 검색 중 에러발생!! : {e}')
        error_logging(' 분석용 검색 중 에러 : ' + str(e))

# 조건검색된 종목 매수 후 바로 매도주문 -------------------------------------------------------------------------------------------------------
def process_buy_immediate_sell(token, buys, sells,DEPOSIT_MIN_AMOUNT, BUY_TOTAL_AMOUNT) :
    try :
        # 예수금 조회
        __buy_total_prc = api.deposit(token)
        # 예수금이 최저 잔고금액 이상이면
        if __buy_total_prc > DEPOSIT_MIN_AMOUNT :
            __seq = '0'
            __temp_stocks = []
            __stocks = kiwoom_condition.search(token, __seq, BUY_TOTAL_AMOUNT, __temp_stocks)

            if __stocks :
                for s in __stocks :
                    # 예수금 조회
                    __buy_total_prc = api.deposit(token)

                    # 예수금이 최저 잔고금액 미만이면 종료
                    if __buy_total_prc < DEPOSIT_MIN_AMOUNT :
                        break

                    # 기존 매수했던 종목은 제외
                    if s.code not in buys :
                        if __buy_total_prc > BUY_TOTAL_AMOUNT :
                            __buy_total_prc = BUY_TOTAL_AMOUNT

                        # 매수할 단가 구하기
                        __buyprice = util.get_buy_price(s.price)

                        # 종목당 매수할 총 금액이 매수금액보다 큰 경우에만 매수 호출
                        if __buy_total_prc > __buyprice :
                            __qty = int(__buy_total_prc / __buyprice)

                            if __qty > 0 :
                                __flu_rt = api.get_flu_rt(token, s.code)
                                stock_log(s.code, s.name, s.price, __qty, 'BUY', s.price, 0, 0, __flu_rt, s.time)
                                # 시장가 매수 호출
                                __buy_flag = api.buy(token, s.code, s.name, '', __qty, '3')

                                if __buy_flag :
                                    # 매수종목 리스트에 추가
                                    buys.append(s.code)

                                    time.sleep(3)

                                    # 바로 매도주문
                                    try :
                                        # 매도주문단가 구하기
                                        __sellprice = util.get_sell_price(s.price)
                                        # 매도 호출
                                        sells = api.sell_ordno(token, s.code, s.name, __sellprice, __qty, '0', sells)
                                        stock_log(s.code, s.name, __sellprice, __qty, 'SELL', __sellprice, 0, CONST_SELL_PRICE_RATE, __flu_rt, '')
                                    except Exception as se :
                                        print(f'### 바로 매도주문 중 에러발생!! : {se}')
                                        error_logging(' 바로 매도주문 중 에러 : ' + str(se))
                try :
                    # 파일에 저장
                    search_logging(' 검색종목 ' +  str(list(map(lambda x : str(x.code) + '/' + str(x.name) + '/' + str(x.price), __stocks))))
                except Exception as fe :
                    print(f'### 상승주 조건검색 파일 저장 중 에러발생!! : {fe}')
                    error_logging(' 상승주 조건검색 파일 저장 중 에러 : ' + str(fe))

    except Exception as e :
        print(f'### 상승주 매수 중 에러발생!! : {e}')
        error_logging(' 상승주 매수 중 에러 : ' + str(e))

# 당일매수 수익중인 종목 전량 매도 -----------------------------------------------------------------------------------------------------------------------------
def process_sell_earning_all(token, old_holding_codes, sells) :
    try :
        # 보유종목코드 리스트
        holdings = api.stock_holdings(token, __today)

        # 오늘 매수하고 보유한 종목 리스트만 추출 - 매도 대상 종목임
        today_holdings = util.today_holdings(old_holding_codes, holdings)

        if today_holdings :
            for t in today_holdings :
                __flu_rt = api.get_flu_rt(token, t.code) # 현재 등락률
                # 매도 제외 체크
                if __flu_rt > 1 and __flu_rt < CONST_SELL_EXCLUDE_RATE and int(t.qty) > 0 :
                    __cancels = []
                    if sells :
                        __cancels = list(filter(lambda x: x.code == t.code, sells))

                    if __cancels :
                        # 매도주문 취소
                        api.cancel(token, t.code, __cancels[0].ordno)

                        time.sleep(3)

                    stock_log(t.code, t.name, 0, t.qty, 'SELL', t.cur_prc, 0, t.earn_rate, __flu_rt, '')
                    api.sell(token, t.code, t.name, '', t.qty, '3')

                time.sleep(1)

    except Exception as e :
        print(f'### 당일매수 수익중인 종목 전량 매도 중 에러발생!! : {e}')
        error_logging(' 당일매수 수익중인 종목 전량 매도 중 에러 : ' + str(e))
