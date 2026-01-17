from time import localtime, strftime
import shutil
from helper.constants import CONST_FILE_JUMP_LOG, CONST_FILE_JUMP_TRA_LOG, CONST_FILE_RISE_LOG, CONST_FILE_RISE_TRA_LOG, CONST_FILE_ERROR_LOG
from helper.constants import CONST_FILE_PATH_BACKUP, CONST_FILE_NAME_JUMP_LOG, CONST_FILE_NAME_JUMP_TRA_LOG, CONST_FILE_NAME_RISE_LOG, CONST_FILE_NAME_RISE_TRA_LOG, CONST_FILE_EXTENSION

def trading_logging(stock, type, is_jump, msg) :
    __current_time = strftime('%Y-%m-%d %H:%M:%S', localtime())

    __file_path = CONST_FILE_RISE_LOG

    if is_jump :
        __file_path = CONST_FILE_JUMP_LOG

    if stock :
        if 'BUY' == type :
            with open(__file_path, 'a', encoding='utf-8') as f :
                f.write(__current_time + ' ** 매수 종목코드[' + stock.code  + '] 종목명[' + stock.name + '] 매수단가[' + str(stock.price) + '] 매수수량[' + str(stock.qty)
                        + '] 현재단가[' + str(stock.cur_price)+ '] 이전단가[' + str(stock.before_price) + ']\n')
        else :
            with open(__file_path, 'a', encoding='utf-8') as f :
                f.write(__current_time + ' ***** 매도 종목코드['+ stock.code + '] 종목명[' + stock.name + '] 수익률[' + str(stock.price)+ '] 현재단가[' + str(stock.cur_price)
                        + '] 매도수량[' + str(stock.qty)  + ']\n')
    else :
        with open(__file_path, 'a', encoding='utf-8') as f :
            f.write(__current_time + ' ### ' + msg + '\n')

def condition_logging(is_jump, msg) :
    __current_time = strftime('%Y-%m-%d %H:%M:%S', localtime())

    # __current_day = strftime('%Y%m%d', localtime())

    __file_path = CONST_FILE_RISE_TRA_LOG

    if is_jump :
        __file_path = CONST_FILE_JUMP_TRA_LOG

    with open(__file_path, 'a', encoding='utf-8') as f :
        f.write(__current_time + msg + '\n')


def error_logging(msg) :
    __current_time = strftime('%Y-%m-%d %H:%M:%S', localtime())

    with open(CONST_FILE_ERROR_LOG, 'a', encoding='utf-8') as f :
        f.write(__current_time + msg + '\n')

def file_copy() :
    __current_time = strftime('%Y%m%d', localtime()) + "_"
    shutil.copy2(CONST_FILE_JUMP_LOG, CONST_FILE_PATH_BACKUP + __current_time + CONST_FILE_NAME_JUMP_LOG + CONST_FILE_EXTENSION)
    shutil.copy2(CONST_FILE_JUMP_TRA_LOG, CONST_FILE_PATH_BACKUP + __current_time + CONST_FILE_NAME_JUMP_TRA_LOG + CONST_FILE_EXTENSION)
    shutil.copy2(CONST_FILE_RISE_LOG, CONST_FILE_PATH_BACKUP + __current_time + CONST_FILE_NAME_RISE_LOG + CONST_FILE_EXTENSION)
    shutil.copy2(CONST_FILE_RISE_TRA_LOG, CONST_FILE_PATH_BACKUP + __current_time + CONST_FILE_NAME_RISE_TRA_LOG + CONST_FILE_EXTENSION)

def log_truncate() :
    with open(CONST_FILE_JUMP_LOG, 'w') as f :
        f.truncate(0)
    with open(CONST_FILE_JUMP_TRA_LOG, 'w') as f :
        f.truncate(0)
    with open(CONST_FILE_RISE_LOG, 'w') as f :
        f.truncate(0)
    with open(CONST_FILE_RISE_TRA_LOG, 'w') as f :
        f.truncate(0)
