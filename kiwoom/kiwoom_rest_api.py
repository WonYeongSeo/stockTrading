import requests
import time
from kiwoom.stock import Contract, Holding, Stockinfo, TodayStock, TodayTotalEarnLoss
from log import file_logging
from helper import util
from helper.constants import CONST_HOST, CONST_SELL_EXCLUDE_RATE

cont_yn = 'N'
next_key = ''

def get_response(token, end_point, api_id, data, cont_yn, next_key) :
	# 1. 요청할 API URL
	__url = CONST_HOST + end_point

	# 2. header 데이터
	__headers = {
		'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
		'authorization': f'Bearer {token}', # 접근토큰
		'cont-yn': cont_yn, # 연속조회여부
		'next-key': next_key, # 연속조회키
		'api-id': api_id, # TR명
	}

	# 3. http POST 요청
	response = requests.post(__url, headers=__headers, json=data)

	# 4. 응답 상태 코드와 데이터 출력
	# print('Code:', response.status_code)
	# print('Header:', json.dumps({key: response.headers.get(key) for key in ['next-key', 'cont-yn', 'api-id']}, indent=4, ensure_ascii=False))
	# print('Body:', json.dumps(response.json(), indent=4, ensure_ascii=False))  # JSON 응답을 파싱하여 출력

	return response

# 예수금(d+2 추정인출금) 조회
def deposit(token) :
    __end_point = '/api/dostk/acnt'
    __api_id = 'kt00001'
    __data = {
        'qry_tp': '3',
    }

    __rep = get_response(token, __end_point, __api_id, __data, cont_yn, next_key)

    __alow_amt = 0
    if __rep :
        if __rep.json()['return_code'] == 0 :
            __alow_amt = __rep.json()['d2_pymn_alow_amt']

    return int(__alow_amt)

# 일별잔고수익률 조회
def stock_holdings(token, dt) :
    __end_point = '/api/dostk/acnt'
    __api_id = 'ka01690'
    __data = {
		'qry_dt': dt, # 조회일자
	}

    __rep = get_response(token, __end_point, __api_id, __data, cont_yn, next_key)

    # stk_cd : 종목코드
    # stk_nm : 종목명
    # cur_prc : 현재가
    # buy_uv : 매입가
    # rmnd_qty : 보유량
    # prft_rt : 수익률
    # evltv_prft : 평가손익
    # evlt_amt : 평가금액
    # s_price : 시초가

    __holdings = []
    if __rep :
        __stocks = __rep.json()['day_bal_rt']

        if __stocks :
            for s in __stocks :
                __holdings.append(Holding(s['stk_cd'], s['stk_nm'], s['cur_prc'], s['buy_uv'], s['rmnd_qty'], s['prft_rt'], s['evltv_prft'], s['evlt_amt']))

    return __holdings

# 일별잔고수익률 조회 - 기존 보유종목코드
def old_holding_codes(token) :
    __stocks = stock_holdings(token, util.yesterday())

    __holding_codes = []
    if __stocks :
        for s in __stocks :
            __holding_codes.append(s.code)

    return __holding_codes

# 종목 조회
def stock_info(token, code) :
    __end_point = '/api/dostk/stkinfo'
    __api_id = 'ka10001'
    __data = {
		'stk_cd': code, # 종목코드 거래소별 종목코드 (KRX:039490,NXT:039490_NX,SOR:039490_AL)
	}
    # stk_cd : 종목코드
    # stk_nm : 종목명
    # upl_pric : 상한가
    # lst_pric : 하한가
    # cur_prc : 현재가
    # open_pric : 시초가
    # flu_rt : 등락율

    __rep = get_response(token, __end_point, __api_id, __data, cont_yn, next_key)

    __stock = None
    if __rep :
        __info = __rep.json()
        if __info['stk_cd'] :
            __stock = Stockinfo(__info['stk_cd'], __info['stk_nm'], __info['upl_pric'], __info['lst_pric'], __info['cur_prc'], __info['open_pric'], __info['flu_rt'])
    return __stock

# 현재가 조회
def get_current_price(token, code) :
    __stock = stock_info(token, code)
    __cur_prc = 0
    if __stock :
        __cur_prc = __stock.cur_prc
    return abs(int(__cur_prc)) if __cur_prc else 0

# 상한가 조회
def get_upl_price(token, code) :
    __stock = stock_info(token, code)
    __upl_pric = 0
    if __stock :
        __upl_pric = __stock.upl_pric
    return abs(int(__upl_pric)) if __upl_pric else 0

# 시초가 조회
def get_open_pric(token, code) :
    __stock = stock_info(token, code)
    __open_pric = 0
    if __stock :
        __open_pric = __stock.open_pric
    return abs(int(__open_pric)) if __open_pric else 0

# 등락률 조회
def get_flu_rt(token, code) :
    __stock = stock_info(token, code)
    __flu_rt = 0
    if __stock :
        __flu_rt = __stock.flu_rt
    return float(__flu_rt) if __flu_rt else 0

# 시초가 set
def set_open_pric(token, code) :
    return get_open_pric(token, code)

# 매도 제외 체크
def is_sell(token, code) :
    is_sell = True
    __stock = stock_info(token, code)
    if __stock :
        __flu_rt = __stock.__flu_rt
        if __flu_rt > CONST_SELL_EXCLUDE_RATE :
            is_sell = False
    return is_sell

# 주식 매수주문
def buy(token, code, price, qty, is_jump) :
    __end_point = '/api/dostk/ordr'
    __api_id = 'kt10000'
    __data =  {
		'dmst_stex_tp': 'KRX', # 국내거래소구분 KRX,NXT,SOR
		'stk_cd': code, # 종목코드
		'ord_qty': qty, # 주문수량
		'ord_uv': price, # 주문단가
		'trde_tp': '0', # 매매구분 0:보통 , 3:시장가 , 5:조건부지정가 , 81:장마감후시간외 , 61:장시작전시간외, 62:시간외단일가 , 6:최유리지정가 , 7:최우선지정가 , 10:보통(IOC) , 13:시장가(IOC) , 16:최유리(IOC) , 20:보통(FOK) , 23:시장가(FOK) , 26:최유리(FOK) , 28:스톱지정가,29:중간가,30:중간가(IOC),31:중간가(FOK)
		'cond_uv': '', # 조건단가
	}

    __rep = get_response(token, __end_point, __api_id, __data, cont_yn, next_key)

    __flag = False

    if __rep :
        if __rep.json()['return_code'] == 0 :
            __flag = True
        else :
            # print('*** 매수 시 에러 발생 : ', datetime.now(), rep.json()['return_msg'])
            file_logging.trading_logging('', 'BUY', is_jump, '매수 시 에러 발생 : ' + __rep.json()['return_msg'])

    return __flag

# 주식 매도주문
def sell(token, code, qty, is_jump) :
    __end_point = '/api/dostk/ordr'
    __api_id = 'kt10001'
    __data =  {
		'dmst_stex_tp': 'KRX', # 국내거래소구분 KRX,NXT,SOR
		'stk_cd': code, # 종목코드
		'ord_qty': qty, # 주문수량
		'ord_uv': '', # 주문단가
		'trde_tp': '3', # 매매구분 0:보통 , 3:시장가 , 5:조건부지정가 , 81:장마감후시간외 , 61:장시작전시간외, 62:시간외단일가 , 6:최유리지정가 , 7:최우선지정가 , 10:보통(IOC) , 13:시장가(IOC) , 16:최유리(IOC) , 20:보통(FOK) , 23:시장가(FOK) , 26:최유리(FOK) , 28:스톱지정가,29:중간가,30:중간가(IOC),31:중간가(FOK)
		'cond_uv': '', # 조건단가
	}

    __rep = get_response(token, __end_point, __api_id, __data, cont_yn, next_key)

    __flag = False

    if __rep :
        if __rep.json()['return_code'] == 0 :
            __flag = True
        else :
            # print('*** 매도 시 에러 발생 : ', datetime.now(), rep.json()['return_msg'])
            file_logging.trading_logging('', 'SELL', is_jump, '매도 시 에러 발생 : ' + __rep.json()['return_msg'])

    return __flag

# 당일매매종목 리스트 조회
def get_today_trading_stocks(token, dt) :
    __end_point = '/api/dostk/acnt'
    __api_id = 'ka10170'
    __data = {
		'base_dt': dt, # 기준일자 YYYYMMDD(공백입력시 금일데이터,최근 2개월까지 제공)
		'ottks_tp': '2', # 단주구분 1:당일매수에 대한 당일매도,2:당일매도 전체
		'ch_crd_tp': '0', # 현금신용구분 0:전체, 1:현금매매만, 2:신용매매만
	}

    __rep = get_response(token, __end_point, __api_id, __data, cont_yn, next_key)

    return __rep

# 당일매매 총손익
def get_today_tot_info(token, dt) :
    __rep = get_today_trading_stocks(token, dt)

    # tot_buy_amt : 총매수금액
    # tot_sell_amt : 총매도금액
    # tot_cmsn_tax : 총수수료_세금
    # tot_exct_amt : 총정산금액
    # tot_pl_amt : 총손익금액
    # tot_prft_rt : 총수익률

    __today_tot_info = None
    if __rep :
        __info = __rep.json()
        if __info['tot_pl_amt'] :
            __today_tot_info = TodayTotalEarnLoss(dt, __info['tot_buy_amt'], __info['tot_sell_amt'], __info['tot_cmsn_tax'], __info['tot_exct_amt'], __info['tot_pl_amt'], __info['tot_prft_rt'])
    return __today_tot_info

# 당일매매종목별 손익
def get_today_stocks(token, dt) :
    __rep = get_today_trading_stocks(token, dt)

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

    __today_stocks = []
    if __rep :
        __info = __rep.json()['tdy_trde_diary']
        if __info :
            for s in __info :
                if s['stk_cd'] :
                    __today_stocks.append(TodayStock(dt, s['stk_cd'], s['stk_nm'], s['buy_avg_pric'], s['buy_qty'], s['buy_amt']
                                                    , s['sel_avg_pric'], s['sell_qty'], s['sell_amt'], s['pl_amt'], s['prft_rt'], s['cmsn_alm_tax']))

    return __today_stocks

# 계좌별주문체결내역상세요청 조회
def get_contract_detail(token, dt, code) :
    __end_point = '/api/dostk/acnt'
    __api_id = 'kt00007'
    __data = {
		'ord_dt': dt, # 주문일자 YYYYMMDD
		'qry_tp': '1', # 조회구분 1:주문순, 2:역순, 3:미체결, 4:체결내역만
		'stk_bond_tp': '0', # 주식채권구분 0:전체, 1:주식, 2:채권
		'sell_tp': '0', # 매도수구분 0:전체, 1:매도, 2:매수
		'stk_cd': code, # 종목코드 공백허용 (공백일때 전체종목)
		'fr_ord_no': '', # 시작주문번호 공백허용 (공백일때 전체주문)
		'dmst_stex_tp': '%', # 국내거래소구분 %:(전체),KRX:한국거래소,NXT:넥스트트레이드,SOR:최선주문집행
    }
    __rep = get_response(token, __end_point, __api_id, __data, cont_yn, next_key)

    __contracts = []
    if __rep :
        __stocks = __rep.json()['acnt_ord_cntr_prps_dtl']

    # stk_cd : 종목코드
    # stk_nm : 종목명
    # io_tp_nm : 주문구분 (현금매수, 현금매도)
    # ord_tm : 주문시간 13:05:43
        if __stocks :
            for s in __stocks :
                __contracts.append(Contract(s['stk_cd'], s['stk_nm'], s['io_tp_nm'], s['ord_tm']))

    return __contracts

# 계좌별주문체결현황요청 조회
def get_contract_info(token, dt, code, sell_tp) :
    __end_point = '/api/dostk/acnt'
    __api_id = 'kt00009'
    __data = {
		'ord_dt': dt, # 주문일자 YYYYMMDD
		'stk_bond_tp': '0', # 주식채권구분 0:전체, 1:주식, 2:채권
		'mrkt_tp': '0', # 시장구분 0:전체, 1:코스피, 2:코스닥, 3:OTCBB, 4:ECN
		'sell_tp': sell_tp, # 매도수구분 0:전체, 1:매도, 2:매수
		'qry_tp': '1', # 조회구분 0:전체, 1:체결
		'stk_cd': code, # 종목코드 전문 조회할 종목코드
		'fr_ord_no': '', # 시작주문번호
		'dmst_stex_tp': '%', # 국내거래소구분 %:(전체),KRX:한국거래소,NXT:넥스트트레이드,SOR:최선주문집행
    }
    __rep = get_response(token, __end_point, __api_id, __data, cont_yn, next_key)

    __contracts = []
    if __rep :
        __stocks = __rep.json()['acnt_ord_cntr_prst_array']
    # stk_cd : 종목코드
    # stk_nm : 종목명
    # io_tp_nm : 주문구분 (현금매수, 현금매도)
    # cntr_tm : 체결시간 13:05:43
        if __stocks :
            for s in __stocks :
                __contracts.append(Contract(s['stk_cd'], s['stk_nm'], s['io_tp_nm'], s['cntr_tm']))

    return __contracts

# 체결요청 조회
def get_contract(token, code) :
    __end_point = '/api/dostk/acnt'
    __api_id = 'ka10076'
    __data = {
		'stk_cd': code, # 종목코드
		'qry_tp': '1', # 조회구분 0:전체, 1:종목
		'sell_tp': '0', # 매도수구분 0:전체, 1:매도, 2:매수
		'ord_no': '', # 주문번호 검색 기준 값으로 입력한 주문번호 보다 과거에 체결된 내역이 조회됩니다.
		'stex_tp': '0', # 거래소구분  0 : 통합, 1 : KRX, 2 : NXT
    }
    __rep = get_response(token, __end_point, __api_id, __data, cont_yn, next_key)

    __contracts = []
    if __rep :
        __stocks = __rep.json()['cntr']
    # stk_cd : 종목코드
    # stk_nm : 종목명
    # io_tp_nm : 주문구분 (현금매수, 현금매도)
    # ord_tm : 체결시간 13:05:43
        if __stocks :
            for s in __stocks :
                __contracts.append(Contract(s['stk_cd'], s['stk_nm'], s['io_tp_nm'], s['ord_tm']))

    return __contracts

# 1분봉차트 조회
def minute_chart(token, tic_scope, code) :
    __end_point = '/api/dostk/chart'
    __api_id = 'ka10080'
    __data = {
		'stk_cd': code, # 종목코드 거래소별 종목코드 (KRX:039490,NXT:039490_NX,SOR:039490_AL)
		'tic_scope': str(tic_scope), # 틱범위 1:1분, 3:3분, 5:5분, 10:10분, 15:15분, 30:30분, 45:45분, 60:60분
		'upd_stkpc_tp': '1', # 수정주가구분 0(미적용) or 1(적용)
	}

    rep = get_response(token, __end_point, __api_id, __data, cont_yn, next_key)

    __current_price = 0
    if rep :
        __stock = rep.json()['stk_min_pole_chart_qry']
        if __stock :
            __current_price = __stock[0]['cur_prc']

    return int(__current_price)