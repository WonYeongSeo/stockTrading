from time import localtime, strftime
import shutil
from helper.constants import CONST_FILE_RISE_LOG, CONST_FILE_RISE_TRA_LOG, CONST_FILE_ERROR_LOG, CONST_FILE_ANALYSIS_LOG
from helper.constants import CONST_FILE_PATH_BACKUP, CONST_FILE_NAME_RISE_LOG

def trading_logging(stock, type, msg) :
    __current_time = strftime('%Y-%m-%d %H:%M:%S', localtime())

    __file = CONST_FILE_RISE_LOG

    if stock :
        if 'BUY' == type :
            __earn_rate = float(stock.earn_rate) if stock.earn_rate else 0

            if __earn_rate < 0 :
                with open(__file, 'a', encoding='utf-8') as f :
                    f.write(__current_time + ' ===> 추가 매수 종목코드[' + stock.code  + '] 종목명[' + stock.name + '] 매수단가[' + str(stock.price) + '] 매수수량[' + str(stock.qty)
                            + '] 현재단가[' + str(stock.cur_price) + '] 수익률[' + str(stock.earn_rate) + '] 등락률[' + str(stock.flu_rt) + ']\n')
            else :
                with open(__file, 'a', encoding='utf-8') as f :
                    f.write(__current_time + ' --> 매수 종목코드[' + stock.code  + '] 종목명[' + stock.name + '] 매수단가[' + str(stock.price) + '] 매수수량[' + str(stock.qty)
                            + '] 현재단가[' + str(stock.cur_price) + '] 이전단가[' + str(stock.before_price) + '] 등락률[' + str(stock.flu_rt) + '] 검색시간[' + str(stock.time) + ']\n')
        else :
            with open(__file, 'a', encoding='utf-8') as f :
                f.write(__current_time + ' <---- 매도 종목코드['+ stock.code + '] 종목명[' + stock.name + '] 매도단가[' + str(stock.cur_price)
                        + '] 매도수량[' + str(stock.qty) + '] 수익률[' + str(stock.earn_rate) + '] 등락률[' + str(stock.flu_rt) + ']\n')
    else :
        with open(__file, 'a', encoding='utf-8') as f :
            f.write(__current_time + ' ### ' + msg + '\n')

def condition_logging(msg) :
    __current_time = strftime('%Y-%m-%d %H:%M:%S', localtime())

    with open(CONST_FILE_RISE_TRA_LOG, 'a', encoding='utf-8') as f :
        f.write(__current_time + msg + '\n')


def analysis_logging(msg) :
    __current_time = strftime('%Y-%m-%d %H:%M:%S', localtime())

    with open(CONST_FILE_ANALYSIS_LOG, 'a', encoding='utf-8') as f :
        f.write(__current_time + msg + '\n')


def error_logging(msg) :
    __current_time = strftime('%Y-%m-%d %H:%M:%S', localtime())

    with open(CONST_FILE_ERROR_LOG, 'a', encoding='utf-8') as f :
        f.write(__current_time + msg + '\n')

def file_copy() :
    __current_day = strftime('%Y%m%d', localtime()) + "_"
    shutil.copy2(CONST_FILE_RISE_LOG, CONST_FILE_PATH_BACKUP + __current_day + CONST_FILE_NAME_RISE_LOG)
    # shutil.copy2(CONST_FILE_RISE_TRA_LOG, CONST_FILE_PATH_BACKUP + __current_day + CONST_FILE_NAME_RISE_TRA_LOG + CONST_FILE_EXTENSION)

def log_truncate() :
    with open(CONST_FILE_RISE_LOG, 'w') as f :
        f.truncate(0)
    with open(CONST_FILE_RISE_TRA_LOG, 'w') as f :
        f.truncate(0)
    with open(CONST_FILE_ANALYSIS_LOG, 'w') as f :
        f.truncate(0)
