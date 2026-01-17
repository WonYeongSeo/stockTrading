import oracledb
from helper.constants import CONST_DB_DSN, CONST_DB_PWD, CONST_DB_USER, CONST_DB_INSTANT_CLIENT_PATH

def save(total_info, stocks) :
    # Thick모드를 위한 set
    oracledb.init_oracle_client(lib_dir=CONST_DB_INSTANT_CLIENT_PATH)
    # DB 연결
    con = oracledb.connect(user=CONST_DB_USER, password=CONST_DB_PWD, dsn=CONST_DB_DSN)

    if con :
        cursor = con.cursor()   # 연결된 DB 지시자(커서) 생성

        if cursor :
            if total_info :
                # cursor.execute("SELECT * FROM TB_STOCK_TRADING_SUMMARY") # 데이터베이스 명령 실행( cursor가 임시로 보관)

                # out_data = cursor.fetchall() # 커서의 내용을 out_data에 저장
                # for record in out_data: # out_data의 내용을 출력
                #     print(record)

                # dt : 일자
                # tot_buy_amt : 총매수금액
                # tot_sell_amt : 총매도금액
                # tot_cmsn_tax : 총수수료_세금
                # tot_exct_amt : 총정산금액
                # tot_pl_amt : 총손익금액
                # tot_prft_rt : 총수익률

                params = ([total_info.dt, total_info.tot_buy_amt, total_info.tot_sell_amt, total_info.tot_cmsn_tax, total_info.tot_pl_amt, total_info.tot_exct_amt, total_info.tot_prft_rt])
                cursor.execute("merge into TB_STOCK_TRADING_SUMMARY a using dual on (a.STOCK_TRADING_DATE = to_date(:1, 'yyyy-mm-dd'))"
                                + " when matched then  update set a.TOTAL_BUY_AMOUNT = :2, a.TOTAL_SELL_AMOUNT = :3, a.TOTAL_COMMISION_TAX = :4, a.TOTAL_CALC_AMOUNT = :5"
                                + " ,a.TOTAL_EARNING_AMOUNT = :6, a.TOTAL_EARNING_RATE = :7, a.LAST_TIMESTAMP = sysdate"
                                + " when not matched then insert (STOCK_TRADING_DATE, TOTAL_BUY_AMOUNT, TOTAL_SELL_AMOUNT, TOTAL_COMMISION_TAX, TOTAL_CALC_AMOUNT, TOTAL_EARNING_AMOUNT"
                                + " , TOTAL_EARNING_RATE, CREATE_TIMESTAMP, LAST_TIMESTAMP)"
                                + " values (to_date(:1, 'yyyy-mm-dd'), :2, :3, :4, :5, :6, :7, sysdate, sysdate)"
                            , params)
                con.commit()

            if stocks :
                for s in stocks :
                    # code : 종목코드
                    # name : 종목명
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

                    params = ([s.dt, s.code, s.name, s.buy_avg_pric, s.buy_qty, s.buy_amt, s.sel_avg_pric, s.sell_qty, s.sell_amt, s.pl_amt, s.prft_rt, s.cmsn_alm_tax
                               , s.buy_time, s.sell_time, s.diff_time])
                    cursor.execute("merge into TB_STOCK_TRADING_DETAIL a using dual on (a.STOCK_TRADING_DATE = to_date(:1, 'yyyy-mm-dd') and a.STOCK_ITEM_CODE = :2)"
                                    + " when matched then  update set a.STOCK_ITEM_NM = :3, a.STOCK_BUY_UNIT_COST = :4, a.STOCK_BUY_QTY = :5, a.STOCK_BUY_AMOUNT = :6"
                                    + " ,a.STOCK_SELL_UNIT_COST = :7, a.STOCK_SELL_QTY = :8, a.STOCK_SELL_AMOUNT = :9, a.EARNING_AMOUNT = :10, a.EARNING_RATE = :11"
                                    + " ,a.COMMISION_TAX = :12, a.STOCK_BUY_TIME = :13, a.STOCK_SELL_TIME = :14, a.STOCK_DIFF_TIME = :15, a.LAST_TIMESTAMP = sysdate"
                                    + " when not matched then insert (STOCK_TRADING_DATE, STOCK_ITEM_CODE, STOCK_ITEM_NM, STOCK_BUY_UNIT_COST, STOCK_BUY_QTY, STOCK_BUY_AMOUNT"
                                    + " , STOCK_SELL_UNIT_COST, STOCK_SELL_QTY, STOCK_SELL_AMOUNT, EARNING_AMOUNT, EARNING_RATE, COMMISION_TAX, STOCK_BUY_TIME, STOCK_SELL_TIME"
                                    + " , STOCK_DIFF_TIME, CREATE_TIMESTAMP, LAST_TIMESTAMP)"
                                    + " values (to_date(:1, 'yyyy-mm-dd'), :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, sysdate, sysdate)"
                                , params)

                con.commit()

        con.close()   # DB 연결 해제
