from datetime import datetime

CONST_SOCKET_URL = 'wss://api.kiwoom.com:10000/api/dostk/websocket'  # 접속 URL
CONST_HOST = 'https://api.kiwoom.com' # 'https://mockapi.kiwoom.com' # 모의투자
CONST_APP_KEY = 'HxIg0sKLV5tEmvfc6iBjrAiiOQOcRMfQFqAAmIFnJX8'
CONST_SECRET_KEY = 'FDyP9WISQQlRwo5IzA0Dg5sXUdl6oRR6l8ASL2cfoPE'

# 매수/매도 관련
CONST_CONDITIN_HIGH_DIFF_RATE = float(0.07) # 고가 대비 차이율
CONST_SELL_STOCK_FLU_RATE = float(25) # 종목등락률 이상이면 매도 대기
CONST_SELL_CHECK_RATE = float(10) # 수익률 이상이면 매도 대기
CONST_SELL_EARN_RATE = float(7) # 매도 수익률
CONST_SELL_LOSS_RATE = float(-3) # 매도 손절율
CONST_BUY_JUMP_PRICE_RATE = float(0.02) # 급등주 매수주문 시 매수단가 호가율
CONST_BUY_RISE_PRICE_RATE = float(0.01) # 상승주 매수주문 시 매수단가 호가율
CONST_SELL_EXCLUDE_AMOUNT = int(str('2,000,000').replace(',','')) # 매도 시 기준금액이상이면 제외
CONST_BUY_TOTAL_PRICE = int(str('200,000').replace(',','')) # 종목당 매수할 총 금액

# 급등주
CONST_JUMP_SLEEP_TIME = int(58) # 급등주 수행주기
CONST_JUMP_START_TIME = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 9, 3, 45) # 급등주 시작 시간

# 상승주
CONST_RISE_SLEEP_TIME = int(56) # 상승주 수행주기
CONST_RISE_BUY_DELAY_TIME = int(600) # 상승주 매수 대기 시간
CONST_RISE_START_TIME = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 9, 30, 45) # 상승주 시작 시간
CONST_RISE_END_TIME = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 15, 12, 0) # 상승주 종료 시간
CONST_EXCEL_DB_TIME = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 15, 35, 0) # excel logging / database save 여부 시간

# 엑셀파일 위치
CONST_EXCEL_FOLDER = '..\\stockTradingLog\\excel\\'
CONST_EXCEL_BACKUP_FOLDER = '..\\stockTradingLog\\excel\\backup\\'
CONST_EXCEL_FILE_NAME = '주식자동매매일지'
CONST_EXCEL_EXTENSION = '.xlsx'

# 로그파일 위치
CONST_FILE_PATH_LOG = '..\\stockTradingLog\\log\\'
CONST_FILE_PATH_BACKUP = '..\\stockTradingLog\\log\\backup\\'
CONST_FILE_NAME_JUMP_LOG = '급등주매매일지'
CONST_FILE_NAME_JUMP_TRA_LOG = '급등주조건검색종목리스트'
CONST_FILE_NAME_RISE_LOG = '상승주매매일지'
CONST_FILE_NAME_RISE_TRA_LOG = '상승주조건검색종목리스트'
CONST_FILE_EXTENSION = ".txt"
CONST_FILE_JUMP_LOG = CONST_FILE_PATH_LOG + CONST_FILE_NAME_JUMP_LOG + CONST_FILE_EXTENSION
CONST_FILE_JUMP_TRA_LOG = CONST_FILE_PATH_LOG + CONST_FILE_NAME_JUMP_TRA_LOG + CONST_FILE_EXTENSION
CONST_FILE_RISE_LOG = CONST_FILE_PATH_LOG + CONST_FILE_NAME_RISE_LOG + CONST_FILE_EXTENSION
CONST_FILE_RISE_TRA_LOG = CONST_FILE_PATH_LOG + CONST_FILE_NAME_RISE_TRA_LOG + CONST_FILE_EXTENSION
CONST_FILE_ERROR_LOG = CONST_FILE_PATH_LOG + '에러로그.txt'

# DB 관련
CONST_DB_USER = 'angel'
CONST_DB_PWD = 'angelpwd'
CONST_DB_DSN = 'localhost:1521/ANGELDB'
CONST_DB_INSTANT_CLIENT_PATH = 'C:\\instantclient_21_18'