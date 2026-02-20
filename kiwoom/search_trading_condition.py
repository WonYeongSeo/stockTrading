
import time
from datetime import datetime
from kiwoom import kiwoom_condition, kiwoom_rest_api as api
from kiwoom.stock import stock_log
from helper import util
from helper.constants import CONST_BUY_TOTAL_AMOUNT, CONST_DEPOSIT_MINIMUM_AMOUNT, CONST_EXCEL_DB_TIME
from helper.constants import CONST_JUMP_START_TIME, CONST_JUMP_SLEEP_TIME
from helper.constants import CONST_RISE_START_TIME, CONST_RISE_END_TIME, CONST_RISE_SLEEP_TIME, CONST_RISE_BUY_DELAY_TIME
from helper.constants import CONST_SELL_LOSS_JUMP_RATE, CONST_SELL_LOSS_RISE_RATE
from helper.constants import CONST_SELL_EARNING_RATE, CONST_SELL_STANDBY_EARNING_RATE, CONST_SELL_STANDBY_FLU_RATE, CONST_SELL_EXCLUDE_RATE
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

    # 조건검색종목 리스트
    conditions_jump = []
    conditions_rise = []

    # 매수종목 리스트
    buys = []

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
                process_sell(token, today_holdings, False)

                # 검색한 종목에 대한 매수처리
                process_buy_rise(token, conditions_rise, conditions_jump, holdings, buys, DEPOSIT_MIN_AMOUNT, BUY_TOTAL_AMOUNT)

                # 3분봉기간상승 조건검색
                # process_condition_2(token, BUY_TOTAL_AMOUNT)

                time.sleep(CONST_RISE_SLEEP_TIME)

            # 급등주 매매
            # elif datetime.now() > CONST_JUMP_START_TIME :
            #     # 당일 매수한 종목에 대한 매도처리
            #     process_sell(token, today_holdings, True)

            #     # 검색한 종목에 대한 매수처리
            #     process_buy_jump(token, conditions_jump, holdings, buys, DEPOSIT_MIN_AMOUNT, BUY_TOTAL_AMOUNT)

            #     time.sleep(CONST_JUMP_SLEEP_TIME)

        except Exception as e :
            print(f'### 자동매매 중 에러발생!! : {e}')
            error_logging(' 자동매매 중 에러 : ' + str(e))
            time.sleep(CONST_RISE_SLEEP_TIME)

    return is_excel_db_logging

# 상승주 조건검색된 종목 중 매수조건에 해당되면 매수 -------------------------------------------------------------------------------------------------------
def process_buy_rise(token, conditions_rise, conditions_jump, holdings, buys, DEPOSIT_MIN_AMOUNT, BUY_TOTAL_AMOUNT) :
    try :
        __seq = '0' # 3분급등조건
        __temp_stocks = []
        __stocks = kiwoom_condition.search(token, __seq, BUY_TOTAL_AMOUNT, __temp_stocks)

        if __stocks :
            if not conditions_rise :
                for s in __stocks :
                    __already_holding = []
                    if holdings :
                        __already_holding = list(filter(lambda x: x.code == s.code, holdings))
                    if not __already_holding and int(s.price) < BUY_TOTAL_AMOUNT :
                        conditions_rise.append(s)
            else :
                # 급등주 검색종목은 제외
                if conditions_jump :
                    conditions_rise = list(set(conditions_rise) - set(conditions_jump))
                    conditions_jump = []

                # 매수 체크 flag
                __is_buy = False

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

                    list_rise = []
                    if conditions_rise :
                        list_rise = list(filter(lambda x: x.code == s.code, conditions_rise))

                    if list_rise :
                        c = list_rise[0]

                        # 예수금 조회
                        __buy_total_prc = api.deposit(token)

                        # 예수금이 최저 잔고금액 이상이면 매수
                        if __buy_total_prc > DEPOSIT_MIN_AMOUNT:
                            __is_buy = True
                        else :
                            __is_buy = False

                        # 고가와 체크할 금액
                        # __high_check_price = util.get_high_check_price(s.price)

                        # 이전 검색 금액보다 현재 검색 금액이 큰 경우 매수
                        if __is_buy and int(s.price) > int(c.price) : # and __high_check_price > s.h_price :
                            c.price = s.price

                            __time_second = util.get_diff_timesecond(datetime.now(), c.time)

                            if __time_second > CONST_RISE_BUY_DELAY_TIME :
                                if __buy_total_prc > BUY_TOTAL_AMOUNT :
                                    __buy_total_prc = BUY_TOTAL_AMOUNT

                                # 매수할 단가 구하기
                                __buyprice = util.get_buy_price(s.price, False)

                                # 종목당 매수할 총 금액이 매수금액보다 큰 경우에만 매수 호출
                                if __buy_total_prc > __buyprice :
                                    __buy_qty = int(__buy_total_prc / __buyprice)

                                    if __buy_qty > 0 :
                                        __flu_rt = api.get_flu_rt(token, s.code)
                                        stock_log(s.code, s.name, __buyprice, __buy_qty, 'BUY', False, s.price, c.price, 0, __flu_rt, c.time)
                                        # 매수 호출
                                        __buy_flag = api.buy(token, s.code, s.name, str(__buyprice), str(__buy_qty), '0', False)

                                        if __buy_flag :
                                            # 조건검색종목 리스트에서 제외
                                            conditions_rise.remove(c)
                                            # 매수종목 리스트에 추가
                                            buys.append(s)

                        elif int(s.price) > int(c.price) :
                            c.price = s.price
                        # elif __high_check_price < s.h_price :
                        #     conditions.remove(c)
                    else :
                        if int(s.price) < BUY_TOTAL_AMOUNT :
                            conditions_rise.append(s)

    except Exception as e :
        print(f'### 상승주 매수 중 에러발생!! : {e}')
        error_logging(' 상승주 매수 중 에러 : ' + str(e))

    try :
        # 파일에 저장
        if conditions_rise :
            condition_logging(False, ' 검색종목 ' +  str(list(map(lambda x : str(x.code) + '/' + str(x.name) + '/' + str(x.price), conditions_rise))))
            # condition_logging(is_jump, ' 검색종목 ' +  str(list(map(lambda x : str(x.code) + '/' + str(x.name) + '/' + str(x.price)
            #                                                     + '/' + str(x.s_price) + '/' + str(x.h_price) + '/' + str(x.l_price)
            #                                                     , conditions))))

    except Exception as e :
        print(f'### 상승주 조건검색 파일 저장 중 에러발생!! : {e}')
        error_logging(' 상승주 조건검색 파일 저장 중 에러 : ' + str(e))

# 3분봉기간상승 조건검색 -------------------------------------------------------------------------------------------------------
def process_condition_2(token, BUY_TOTAL_AMOUNT) :
    try :
        __seq = '2' # 3분봉기간상승
        __temp_stocks = []
        __condition_stocks = kiwoom_condition.search(token, __seq, BUY_TOTAL_AMOUNT, __temp_stocks)

        # 파일에 저장
        if __condition_stocks :
            condition_logging(True, ' 검색종목 ' +  str(list(map(lambda x : str(x.code) + '/' + str(x.name) + '/' + str(x.price), __condition_stocks))))
            # condition_logging(is_jump, ' 검색종목 ' +  str(list(map(lambda x : str(x.code) + '/' + str(x.name) + '/' + str(x.price)
            #                                                     + '/' + str(x.s_price) + '/' + str(x.h_price) + '/' + str(x.l_price)
            #                                                     , conditions))))
    except Exception as e :
        print(f'### 3분봉기간상승 조건검색 파일 저장 중 에러발생!! : {e}')
        error_logging(' 3분봉기간상승 조건검색 파일 저장 중 에러 : ' + str(e))

# 급등주 조건검색된 종목 중 매수조건에 해당되면 매수 -------------------------------------------------------------------------------------------------------
def process_buy_jump(token, conditions_jump, holdings, buys, DEPOSIT_MIN_AMOUNT, BUY_TOTAL_AMOUNT) :
    try :
        __seq = '1' # 1분급등조건

        __temp_stocks = []
        __stocks = kiwoom_condition.search(token, __seq, BUY_TOTAL_AMOUNT, __temp_stocks)

        if __stocks :
            if not conditions_jump :
                for s in __stocks :
                    __already_holding = []
                    if holdings :
                        __already_holding = list(filter(lambda x: x.code == s.code, holdings))
                    if not __already_holding and int(s.price) < BUY_TOTAL_AMOUNT :
                        conditions_jump.append(s)
            else :
                __is_buy = False

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

                    list_jump = list(filter(lambda x: x.code == s.code, conditions_jump))

                    if list_jump :
                        c = list_jump[0]

                        # 예수금 조회
                        __buy_total_prc = api.deposit(token)

                        # 예수금이 최저 잔고금액 이상이면 매수
                        if __buy_total_prc > DEPOSIT_MIN_AMOUNT:
                            __is_buy = True
                        else :
                            __is_buy = False

                        # 이전 검색 금액보다 현재 검색 금액이 큰 경우 매수
                        if __is_buy and int(s.price) > int(c.price) :
                            c.price = s.price

                            if __buy_total_prc > BUY_TOTAL_AMOUNT :
                                __buy_total_prc = BUY_TOTAL_AMOUNT

                            # 매수할 단가 구하기
                            __buyprice = util.get_buy_price(s.price, True)

                            # 종목당 매수할 총 금액이 매수금액보다 큰 경우에만 매수 호출
                            if __buy_total_prc > __buyprice :
                                __buy_qty = int(__buy_total_prc / __buyprice)

                                if __buy_qty > 0 :
                                    __flu_rt = api.get_flu_rt(token, s.code)
                                    stock_log(s.code, s.name, __buyprice, __buy_qty, 'BUY', True, s.price, c.price, 0, __flu_rt, c.time)
                                    # 매수 호출
                                    __buy_flag = api.buy(token, s.code, s.name, str(__buyprice), str(__buy_qty), '0', True)

                                    if __buy_flag :
                                        # 조건검색종목 리스트에서 제외
                                        conditions_jump.remove(c)
                                        # 매수종목 리스트에 추가
                                        buys.append(s)

                        elif int(s.price) > int(c.price) :
                            c.price = s.price
                    else :
                        if int(s.price) < BUY_TOTAL_AMOUNT :
                            conditions_jump.append(s)

    except Exception as e :
        print(f'### 급등주 매수 중 에러발생!! : {e}')
        error_logging(' 급등주 매수 중 에러 : ' + str(e))

    try :
        # 파일에 저장
        if conditions_jump :
            condition_logging(True, ' 검색종목 ' +  str(list(map(lambda x : str(x.code) + '/' + str(x.name) + '/' + str(x.price), conditions_jump))))
            # condition_logging(is_jump, ' 검색종목 ' +  str(list(map(lambda x : str(x.code) + '/' + str(x.name) + '/' + str(x.price)
            #                                                     + '/' + str(x.s_price) + '/' + str(x.h_price) + '/' + str(x.l_price)
            #                                                     , conditions))))

    except Exception as e :
        print(f'### 급등주 조건검색 파일 저장 중 에러발생!! : {e}')
        error_logging(' 급등주 조건검색 파일 저장 중 에러 : ' + str(e))

# 당일매수종목에 대한 매도 -----------------------------------------------------------------------------------------------------------------------------
def process_sell(token, today_holdings, is_jump) :
    try :
        if today_holdings :
            for t in today_holdings :
                __flu_rt = api.get_flu_rt(token, t.code) # 현재 등락률
                # 매도 제외 체크
                if __flu_rt < CONST_SELL_EXCLUDE_RATE :
                    __earn_rate = float(t.earn_rate)

                    if is_jump :
                        # 수익률이 기준 손절율 이하이면  매도
                        if __earn_rate < CONST_SELL_LOSS_JUMP_RATE :
                            __sell_qty = int(t.qty)

                            if __sell_qty > 0 :
                                api.sell(token, t.code, t.name, str(__sell_qty), is_jump)
                                stock_log(t.code, t.name, 0, __sell_qty, 'SELL', is_jump, t.cur_prc, 0, __earn_rate, __flu_rt, '')

                    else :
                        # 수익률이 기준 수익률 이상이면  매도
                        if __earn_rate > CONST_SELL_EARNING_RATE  :
                            # 수익률이 check rate 이상 또는 25% 이상이면 매도 대기
                            if __earn_rate > CONST_SELL_STANDBY_EARNING_RATE or __flu_rt > CONST_SELL_STANDBY_FLU_RATE:
                                continue

                            __sell_qty = int(t.qty)
                            # if __earn_rate > CONST_SELL_EARNING_RATE and __sell_qty > 10 :
                            #     __sell_qty = int(__sell_qty / 2)

                            if __sell_qty > 0 :
                                api.sell(token, t.code, t.name, str(__sell_qty), is_jump)
                                stock_log(t.code, t.name, 0, __sell_qty, 'SELL', is_jump, t.cur_prc, 0, __earn_rate, __flu_rt, '')
                        # 수익률이 기준 손절율 이하이면 추가매수
                        elif __earn_rate < CONST_SELL_LOSS_RISE_RATE :
                            # 매수할 단가 구하기
                            __buyprice = util.get_buy_price(t.cur_prc, False)
                            __buy_qty = int(t.qty)
                            stock_log(t.code, t.name, __buyprice, __buy_qty, 'BUY', False, t.cur_prc, 0, __earn_rate, __flu_rt, '')
                            # 매수 호출
                            api.buy(token, t.code, t.name, str(__buyprice), str(__buy_qty), '0', False)

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
                        stock_log(t.code, t.name, 0, __sell_qty, 'SELL', False, t.cur_prc, 0, __earn_rate, __flu_rt, '')
                        api.sell(token, t.code, t.name, str(__sell_qty), False)

                time.sleep(0.5)

    except Exception as e :
        print(f'### 당일매수종목 전량 매도 중 에러발생!! : {e}')
        error_logging(' 당일매수종목 전량 매도 중 에러 : ' + str(e))
