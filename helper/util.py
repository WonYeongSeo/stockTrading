import math
from datetime import date, datetime, timedelta
from helper.constants import CONST_BUY_JUMP_PRICE_RATE, CONST_BUY_RISE_PRICE_RATE, CONST_SELL_EXCLUDE_AMOUNT, CONST_CONDITIN_HIGH_DIFF_RATE

# 오늘날짜 가져오기
def today(format) :
    return datetime.now().strftime(format)

def yesterday() :
    yesterday = date.today() - timedelta(1)
    return yesterday.strftime('%Y%m%d')

# 금액을 호가단위로 변환
def convert_bid_unit(price) :
    __bid_unit = 1
    if price >= 2000 and price < 20000 :
        __bid_unit = 10
    elif price >= 20000 and price < 200000 :
        __bid_unit = 100
    elif price >= 200000 :
        __bid_unit = 1000
    else :
        __bid_unit = 1

    return int(math.ceil(price / __bid_unit) * __bid_unit)

# 매수 호가금액 구하기
def get_buy_price(price, is_jump) :
    if is_jump :
        return convert_bid_unit(int(price) + int(int(price) * CONST_BUY_JUMP_PRICE_RATE))
    else :
        return convert_bid_unit(int(price) + int(int(price) * CONST_BUY_RISE_PRICE_RATE))

# 당일 매수해서 보유한 종목만 추출
def today_holdings(old_holding_codes, holdings) :
    __temp_holdings = []
    if old_holding_codes and holdings :
        for h in holdings :
            if h.buy_amount < CONST_SELL_EXCLUDE_AMOUNT :
                __olds = list(filter(lambda x: x == h.code, old_holding_codes))
                if not __olds :
                    __temp_holdings.append(h)
    return __temp_holdings

# 매수할 단가인지 판단
def check_buy(current_price, price) :
    __is_buy_price = False
    if current_price > price and current_price < int(price + int(price * 0.03)):
        __is_buy_price = True
    return __is_buy_price

def get_high_check_price(price) :
    return (int(price) + int(int(price) * CONST_CONDITIN_HIGH_DIFF_RATE))

# 매수 시간 추출
def get_buy_time(contract) :
    __buy_time = None
    if contract :
        c = list(filter(lambda x: '매수' in x.io_tp_nm, contract))

        if c :
            __buy_time = c[0].cntr_tm
    return __buy_time

# 매도 시간 추출
def get_sell_time(contract) :
    __sell_time = None
    if contract :
        c = list(filter(lambda x: '매도' in x.io_tp_nm, contract))

        if c :
            __sell_time = c[0].cntr_tm
    return __sell_time

# 매도시간 - 매수시간
def get_diff_time(today, buy_time, sell_time) :
    __diff_time = None
    if buy_time and sell_time :
        __bt = datetime.strptime(today + ' ' + buy_time, '%Y%m%d %H:%M:%S')
        __st = datetime.strptime(today + ' ' + sell_time, '%Y%m%d %H:%M:%S')
        __diff_time = str(__st - __bt)
    return __diff_time

# 시간 차이
def get_diff_timesecond(time1, time2) :
    return (time1 - time2).total_seconds()