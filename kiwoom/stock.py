from datetime import datetime
from log import file_logging

# 종목
class Stock :
    def __init__(self, code, name, price, qty) :
        self.code = code.replace('A', '').replace('*','')
        self.name = name
        self.price = int(price) if price else 0
        self.qty = int(qty) if qty else 0
        self.s_price = 0 # 시초가
        self.h_price = 0 # 고가
        self.l_price = 0 # 저가
        self.time = datetime.now()
        self.cur_price = int(0)
        self.before_price = int(0)

class Holding :
    # stk_cd : 종목코드
    # stk_nm : 종목명
    # cur_prc : 현재가
    # buy_uv : 매입가
    # rmnd_qty : 보유량
    # prft_rt : 수익률
    # evltv_prft : 평가손익
    # evlt_amt : 평가금액
    # buy_amount : 매입금액
    # s_price : 시초가
    def __init__(self, code, name, cur_prc, buy_uv, qty, earn_rate, evltv_prft, evlt_amt) :
        self.code = code.replace('A', '').replace('*','')
        self.name = name
        self.cur_prc = int(cur_prc) if cur_prc else 0
        self.buy_uv = int(buy_uv) if buy_uv else 0
        self.qty = int(qty) if qty else 0
        self.earn_rate = float(earn_rate) if earn_rate else 0
        self.evltv_prft = int(evltv_prft) if evltv_prft else 0
        self.evlt_amt = int(evlt_amt) if evlt_amt else 0
        self.buy_amount = self.buy_uv * self.qty
        self.s_price = 0

class Stockinfo :
    # stk_cd : 종목코드
    # stk_nm : 종목명
    # upl_pric : 상한가
    # lst_pric : 하한가
    # cur_prc : 현재가
    # open_pric : 시초가
    # flu_rt : 등락율
    def __init__(self, code, name, upl_pric, lst_pric, cur_prc, open_pric, flu_rt) :
        self.code = code.replace('A', '').replace('*','')
        self.name = name
        self.upl_pric = int(upl_pric) if upl_pric else 0
        self.lst_pric = int(lst_pric) if lst_pric else 0
        self.cur_prc = int(cur_prc) if cur_prc else 0
        self.open_pric = int(open_pric) if open_pric else 0
        self.flu_rt = float(flu_rt) if flu_rt else 0

class Contract :
    # stk_cd : 종목코드
    # stk_nm : 종목명
    # io_tp_nm : 주문구분 (현금매수, 현금매도)
    # cntr_tm : 체결시간 13:05:43
    def __init__(self, code, name, io_tp_nm, cntr_tm) :
        self.code = code.replace('A', '').replace('*','')
        self.name = name
        self.io_tp_nm = io_tp_nm
        self.cntr_tm = cntr_tm

class TodayStock :
    # dt : 일자
    # stk_cd : 종목코드
    # stk_nm : 종목명
    # buy_avg_pric : 매수평균가
    # buy_qty : 매수수량
    # buy_amt : 매수금액
    # sel_avg_pric : 매도평균가
    # sell_qty : 매도수량
    # sell_amt : 매도금액
    # pl_amt : 손익금액
    # prft_rt : 수익률
    # cmsn_alm_tax : 수수료_제세금
    # buy_time : 매수시간
    # sell_time : 매도시간
    # diff_time : 매도시간 - 매수시간
    def __init__(self, dt, code, name, buy_avg_pric, buy_qty, buy_amt, sel_avg_pric, sell_qty, sell_amt, pl_amt, prft_rt, cmsn_alm_tax) :
        self.dt = dt
        self.code = code.replace('A', '').replace('*','')
        self.name = name
        self.buy_avg_pric = int(buy_avg_pric) if buy_avg_pric else 0
        self.buy_qty = int(buy_qty) if buy_qty else 0
        self.buy_amt = int(buy_amt) if buy_amt else 0
        self.sel_avg_pric = int(sel_avg_pric) if sel_avg_pric else 0
        self.sell_qty = int(sell_qty) if sell_qty else 0
        self.sell_amt = int(sell_amt) if sell_amt else 0
        self.pl_amt = int(pl_amt) if pl_amt else 0
        self.prft_rt = float(prft_rt) if prft_rt else 0
        self.cmsn_alm_tax = int(cmsn_alm_tax) if cmsn_alm_tax else 0
        self.buy_time = ''
        self.sell_time = ''
        self.diff_time = ''

class TodayTotalEarnLoss :
    # dt : 일자
    # tot_buy_amt : 총매수금액
    # tot_sell_amt : 총매도금액
    # tot_cmsn_tax : 총수수료_세금
    # tot_exct_amt : 총정산금액
    # tot_pl_amt : 총손익금액
    # tot_prft_rt : 총수익률
    def __init__(self, dt, tot_buy_amt, tot_sell_amt, tot_cmsn_tax, tot_exct_amt, tot_pl_amt, tot_prft_rt) :
        self.dt = dt
        self.tot_buy_amt = int(tot_buy_amt) if tot_buy_amt else 0
        self.tot_sell_amt = int(tot_sell_amt) if tot_sell_amt else 0
        self.tot_cmsn_tax = int(tot_cmsn_tax) if tot_cmsn_tax else 0
        self.tot_exct_amt = int(tot_exct_amt) if tot_exct_amt else 0
        self.tot_pl_amt = int(tot_pl_amt) if tot_pl_amt else 0
        self.tot_prft_rt = float(tot_prft_rt) if tot_prft_rt else 0

# logging 처리
def stock_log(code, name, price, qty, type, is_jump, cur_price, before_price) :
    try :
        __stock = Stock(code, name, price, qty)
        __stock.cur_price = cur_price
        __stock.before_price = before_price

        # 파일에 저장
        file_logging.trading_logging(__stock, type, is_jump, '')

    except Exception as e :
        file_logging.error_logging(' 매매 stock_log logging 중 에러 : ' + str(e))

# logging 처리
def stock_log_1(code, name, price, qty, type, is_jump) :
    try :
        __stock = Stock(code, name, price, qty)

        # 파일에 저장
        file_logging.trading_logging(__stock, type, is_jump, '')

    except Exception as e :
        file_logging.error_logging(' 매매 stock_log_1 logging 중 에러 : ' + str(e))
