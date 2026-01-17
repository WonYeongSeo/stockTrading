import time
from datetime import datetime
from kiwoom import kiwoom_token, search_trading_condition
from kiwoom import kiwoom_rest_api as api
from log import db_saving, file_logging, excel_logging
from helper import util
from helper.constants import CONST_HOST, CONST_APP_KEY, CONST_SECRET_KEY, CONST_JUMP_START_TIME

#======================================================================================================
# v1.0 : 초기버전
# v1.1 : 엑셀 저장 기능 추가
# v1.2 : Database 저장 기능 추가
# v1.3 : 에러 로깅 기능 추가
# v1.4 : 시초가 이상인 경우만 매수
# v1.5 : 현재가와 고가 차이 체크 추가
# v2.0 : 매수 시 조검검색종목간 비교 추가(auto_trading_condition, search_trading_condition)
# v2.1 : 1분급등조건 추가
#======================================================================================================
# 접근토큰
token = kiwoom_token.get_token(CONST_HOST, CONST_APP_KEY, CONST_SECRET_KEY)

if token :

    # 장 시작 시간 체크
    if datetime.now() < CONST_JUMP_START_TIME :
        __delay_time = CONST_JUMP_START_TIME - datetime.now()
        print(f'### {__delay_time} 후에 자동매매 시작!!')
        time.sleep(int(__delay_time.total_seconds()))

    # log 파일 초기화
    file_logging.log_truncate()

    # 기존 보유한 종목코드 리스트 - 재 매수 및 매도 대상에서 제외
    old_holding_codes = api.old_holding_codes(token)

    # 9시부터 15시 11분까지 6분마다 상승주 검색 및 당일 매수한 종목 매도
    # 15시 11분 이후에는 당일 매수한 종목 일괄 매도
    is_excel_db_logging = search_trading_condition.auto_trading(token, old_holding_codes)

    # 오늘 매매결과 excel/Dababase에 저장
    try :
        if is_excel_db_logging :
            is_excel_logging = False
            is_db_save = True

            __today = util.today('%Y%m%d')

            # 당일 총 손익
            __today_tot_info = api.get_today_tot_info(token, __today)
            #print(__today_tot_info.dt, __today_tot_info.tot_pl_amt, __today_tot_info.tot_prft_rt)

            # 당일매매종목 리스트
            __today_stocks = api.get_today_stocks(token, __today)

            if __today_stocks :
                for s in __today_stocks :
                    contract = api.get_contract_detail(token, __today, s.code)
                    if contract :
                        s.buy_time = util.get_buy_time(contract)
                        s.sell_time = util.get_sell_time(contract)
                        s.diff_time = util.get_diff_time(__today, s.buy_time, s.sell_time)
                try :
                    if is_excel_logging :
                        print(datetime.now(), '**** Excel에 저장합니다.')
                        # 엑셀파일에 저장
                        excel_logging.write(__today_tot_info, __today_stocks)
                except Exception as ee:
                    print(f'### excel 저장 시 에러발생!! : {ee}')
                    file_logging.error_logging(' excel 저장 시 에러 : ' + str(ee))

                try :
                    if is_db_save :
                        print(datetime.now(), '*** Database에 저장합니다.')
                        # Database에 저장
                        db_saving.save(__today_tot_info, __today_stocks)
                except Exception as ed:
                    print(f'### Database 저장 시 에러발생!! : {ed}')
                    file_logging.error_logging(' Datebase 저장 시 에러 : ' + str(ed))

                file_logging.file_copy()

    except Exception as e:
        print(f'### excel/Database 저장 시 에러발생!! : {e}')
        file_logging.error_logging(' excel/Database 저장 시 에러 : ' + str(e))


    print(datetime.now(), '** 자동매매 프로그램을 정상종료합니다.')
    #---------------------------------------------------------------------------------------------------


# os.system('shutdown -s -t 0')