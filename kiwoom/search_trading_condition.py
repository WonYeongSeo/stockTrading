
import time
from datetime import datetime
from kiwoom import kiwoom_condition, kiwoom_rest_api as api
from kiwoom.stock import stock_log
from helper import util
from helper.constants import CONST_BUY_TOTAL_PRICE, CONST_SELL_EARN_RATE, CONST_SELL_LOSS_RATE, CONST_SELL_CHECK_RATE, CONST_SELL_STOCK_FLU_RATE, CONST_JUMP_SLEEP_TIME
from helper.constants import CONST_RISE_START_TIME, CONST_RISE_END_TIME, CONST_EXCEL_DB_TIME, CONST_RISE_SLEEP_TIME, CONST_RISE_BUY_DELAY_TIME, CONST_JUMP_START_TIME
from log.file_logging import condition_logging, error_logging

# ---------------------------------------------------------------------------------------------------------------------------------
__today = util.today('%Y%m%d')

# 조건검색  ---------------------------------------------------------------------------------------------------------------------------------
def auto_trading(token, old_holding_codes) :
    print(datetime.now(), '***** 자동매매를 시작합니다.')

    # 조건검색종목 리스트
    conditions = []

    # 매수종목 리스트
    buys = []

    is_excel_db_logging = False

    while True :
        try :
            # 보유종목코드 리스트
            holdings = api.stock_holdings(token, __today)

            # 당일 매수하고 보유한 종목 리스트만 추출 - 매도 대상 종목임
            today_holdings = util.today_holdings(old_holding_codes, holdings)

            if datetime.now() > CONST_RISE_END_TIME :
                # 당일 매수한 종목 전부 매도처리
                process_sell_all(token, today_holdings)

                # 테스트 시 excel logging/ database save 하지 않기 위해 추가
                if datetime.now() < CONST_EXCEL_DB_TIME :
                    __logging_delay_time = CONST_EXCEL_DB_TIME - datetime.now()
                    time.sleep(int(__logging_delay_time.total_seconds()))
                    is_excel_db_logging = True

                break

            elif datetime.now() > CONST_RISE_START_TIME :
                # 당일 매수한 종목에 대한 매도처리
                process_sell(token, today_holdings, False)

                # 검색한 종목에 대한 매수처리
                process_condition_buy(token, conditions, holdings, buys, False)

                time.sleep(CONST_RISE_SLEEP_TIME)

            elif datetime.now() > CONST_JUMP_START_TIME :
                # 당일 매수한 종목에 대한 매도처리
                process_sell(token, today_holdings, True)

                # 검색한 종목에 대한 매수처리
                process_condition_buy(token, conditions, holdings, buys, True)

                time.sleep(CONST_JUMP_SLEEP_TIME)

        except Exception as e :
            print(f'### 자동매매 중 에러발생!! : {e}')
            error_logging(' 자동매매 중 에러 : ' + str(e))
            time.sleep(CONST_RISE_SLEEP_TIME)

    return is_excel_db_logging

# 조건검색된 종목 중 매수조건에 해당되면 매수 -------------------------------------------------------------------------------------------------------
def process_condition_buy(token, conditions, holdings, buys, is_jump) :
    try :
        __seq = '1' # 3분급등조건
        if is_jump :
            __seq = '0' # 1분급등조건

        __stocks = kiwoom_condition.search(token, __seq)

        if __stocks :
            if not conditions :
                for s in __stocks :
                    __already_holding = []
                    if holdings :
                        __already_holding = list(filter(lambda x: x.code == s.code, holdings))
                    if not __already_holding and int(s.price) < CONST_BUY_TOTAL_PRICE :
                        conditions.append(s)
            else :
                __is_buy = False

                # 예수금 조회
                __buy_total_prc = api.deposit(token)

                for s in __stocks :
                    # 예수금이 최저 잔고금액 이상이면 매수
                    if __buy_total_prc > CONST_BUY_TOTAL_PRICE:
                        __is_buy = True
                    else :
                        __is_buy = False

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

                    list_c = list(filter(lambda x: x.code == s.code, conditions))

                    if list_c :
                        c = list_c[0]

                        # 고가와 체크할 금액
                        # __high_check_price = util.get_high_check_price(s.price)

                        # 이전 검색 금액보다 현재 검색 금액이 큰 경우 매수
                        if __is_buy and int(s.price) > int(c.price) : # and __high_check_price > s.h_price :
                            time_second = util.get_diff_timesecond(datetime.now(), c.time)

                            if is_jump or time_second > CONST_RISE_BUY_DELAY_TIME :
                                if __buy_total_prc > CONST_BUY_TOTAL_PRICE :
                                    __buy_total_prc = CONST_BUY_TOTAL_PRICE

                                # 매수할 단가 구하기
                                __buyprice = util.get_buy_price(s.price, is_jump)

                                condition_logging(True, ' 테스트로그 매수진행: ' + str(s.name) + '/' + str(s.price) + '/' + str(__buyprice) + '/' + str(c.name) + '/' + str(c.price))
                                # 종목당 매수할 총 금액이 매수금액보다 큰 경우에만 매수 호출
                                if __buy_total_prc > __buyprice :
                                    __buy_qty = int(__buy_total_prc / __buyprice)

                                    # 매수 호출
                                    # print('*** 매수 : 종목코드[',s.code,'] 종목명[',s.name,'] 매수단가[',__buyprice,'] 매수수량[',__buy_qty,']')
                                    stock_log(s.code, s.name, __buyprice, __buy_qty, 'BUY', is_jump, s.price, c.price)
                                    api.buy(token, s.code, str(__buyprice), str(__buy_qty), is_jump)

                                    # 조건검색종목 리스트에서 제외
                                    conditions.remove(c)
                                    # 매수종목 리스트에 추가
                                    buys.append(s)

                                    time.sleep(1)

                                    # 예수금 조회
                                    __buy_total_prc = api.deposit(token)

                            elif int(s.price) > int(c.price) :
                                condition_logging(True, ' 테스트로그 매수대기 종목대체 전: ' +  str(c.name) + '/' + str(c.price) + '/' + str(s.price))
                                c.price = s.price
                                condition_logging(True, ' 테스트로그 매수대기 종목대체 후: ' +  str(c.name) + '/' + str(c.price))
                        elif int(s.price) > int(c.price) :
                            condition_logging(True, ' 테스트로그 종목대체 전: ' +  str(c.name) + '/' + str(c.price) + '/' + str(s.price))
                            c.price = s.price
                            condition_logging(True, ' 테스트로그 종목대체 후: ' +  str(c.name) + '/' + str(c.price))
                        # elif __high_check_price < s.h_price :
                        #     conditions.remove(c)
                    elif int(s.price) < CONST_BUY_TOTAL_PRICE :
                        conditions.append(s)

    except Exception as e :
        print(f'### 매수 중 에러발생!! : {e}')
        error_logging(' 매수 중 에러 : ' + str(e))

    try :
        # 파일에 저장
        if conditions :
            condition_logging(is_jump, ' 검색종목 ' +  str(list(map(lambda x : str(x.name) + '/' + str(x.price), conditions))))
            # condition_logging(is_jump, ' 검색종목 ' +  str(list(map(lambda x : str(x.code) + '/' + str(x.name) + '/' + str(x.price)
            #                                                     + '/' + str(x.s_price) + '/' + str(x.h_price) + '/' + str(x.l_price)
            #                                                     , conditions))))

    except Exception as e :
        print(f'### 조건검색 파일 저장 중 에러발생!! : {e}')
        error_logging(' 조건검색 파일 저장 중 에러 : ' + str(e))

# 당일매수종목에 대한 매도 -----------------------------------------------------------------------------------------------------------------------------
def process_sell(token, today_holdings, is_jump) :
    try :
        if today_holdings :
            for t in today_holdings :
                # 상한가이면 매도에서 제외
                if not api.is_upl(token, t.code) :
                    __earn_rate = float(t.earn_rate)

                    # 장종반 전량 매도 / 수익률이 기준 수익률 이상 / 수익률이 기준 손절율 이하이면  매도
                    if __earn_rate > CONST_SELL_EARN_RATE or __earn_rate < CONST_SELL_LOSS_RATE :
                        __flu_rt = api.get_flu_rt(token, t.code) # 현재 등락률

                        # 장중이면서 수익율이 check rate 이상 또는 25% 이상이면 매도 대기
                        if __earn_rate > CONST_SELL_CHECK_RATE or __flu_rt > CONST_SELL_STOCK_FLU_RATE:
                            continue

                        __sell_qty = int(t.qty)
                        if __earn_rate > CONST_SELL_EARN_RATE and __sell_qty > 10 :
                            __sell_qty = int(__sell_qty / 2)

                        stock_log(t.code, t.name, __earn_rate, __sell_qty, 'SELL', is_jump, t.cur_prc, 0)
                        api.sell(token, t.code, str(__sell_qty), is_jump)

    except Exception as e :
        print(f'### 당일매수종목 매도 중 에러발생!! : {e}')
        error_logging(' 당일매수종목 매도 중 에러 : ' + str(e))


# 당일매수종목에 대한 전량 매도 -----------------------------------------------------------------------------------------------------------------------------
def process_sell_all(token, today_holdings) :
    try :
        if today_holdings :
            for t in today_holdings :
                # 상한가이면 매도에서 제외
                if not api.is_upl(token, t.code) :
                    __earn_rate = float(t.earn_rate)
                    __sell_qty = int(t.qty)
                    stock_log(t.code, t.name, __earn_rate, __sell_qty, 'SELL', False, t.cur_prc, 0)
                    api.sell(token, t.code, str(__sell_qty), False)

    except Exception as e :
        print(f'### 당일매수종목 전량 매도 중 에러발생!! : {e}')
        error_logging(' 당일매수종목 전량 매도 중 에러 : ' + str(e))