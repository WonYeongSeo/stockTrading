import time
from datetime import datetime
from kiwoom import kiwoom_token, search_trading_condition
from kiwoom import kiwoom_rest_api as api
from log import db_saving, file_logging, excel_logging
from helper import util
from helper.constants import CONST_START_TIME, CONST_DEPOSIT_MINIMUM_AMOUNT, CONST_BUY_TOTAL_AMOUNT

#======================================================================================================
# v1.0 : 초기버전
# v1.1 : 엑셀 저장 기능 추가
# v1.2 : Database 저장 기능 추가
# v1.3 : 에러 로깅 기능 추가
# v1.4 : 시초가 이상인 경우만 매수
# v1.5 : 현재가와 고가 차이 체크 추가
# v2.0 : 매수 시 조검검색종목간 비교 추가(auto_trading_condition, search_trading_condition)
# v2.1 : 1분급등조건(급등주) 추가
# v2.2 : 실행 시 입력값 기능 추가
# v2.3 : 1분급등조건(급등주)과 3분급등조건(상승주) 매수 함수 분리
# v2.4 : 1분급등조건(급등주) 매매 삭제
# v2.5 : 익절 시 이익보존 기능 추가
#======================================================================================================

# 예수금 최저 잔고금액 입력받기 - 입력값 없으면 constants 정의된 값으로 진행
DEPOSIT_MIN_AMOUNT = input('예수금 최저 잔고금액을 입력하세요 (입력하지 않으면 ' + str(f"{CONST_DEPOSIT_MINIMUM_AMOUNT: ,}") + '원 적용) : ')
# 종목당 매수할 금액 입력받기 - 입력값 없으면 constants 정의된 값으로 진행
BUY_TOTAL_AMOUNT = input('종목당 매수할 금액을 입력하세요 (입력하지 않으면 ' + str(f"{CONST_BUY_TOTAL_AMOUNT: ,}") + '원 적용) : ')

# 접근토큰
token = kiwoom_token.get_token()

# 장 시작 시간 체크
if datetime.now() < CONST_START_TIME :
    # log 파일 초기화
    file_logging.log_truncate()

    __delay_time = CONST_START_TIME - datetime.now()
    print(f'### {__delay_time} 후에 자동매매 시작!!')
    time.sleep(int(__delay_time.total_seconds()))

    # 접근토큰
    token = kiwoom_token.get_token()

if token :
    # 기존 보유한 종목코드 리스트 - 재 매수 및 매도 대상에서 제외
    old_holding_codes = api.old_holding_codes(token)

    # 1분급등/ 3분급등 자동 매매
    is_excel_db_logging = search_trading_condition.auto_trading(token, old_holding_codes, DEPOSIT_MIN_AMOUNT, BUY_TOTAL_AMOUNT)

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

else :
    print(datetime.now(), '** 접근토큰이 없어서 종료합니다.')

# os.system('shutdown -s -t 0')