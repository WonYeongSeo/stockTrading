from datetime import datetime

CONST_SOCKET_URL = 'wss://api.kiwoom.com:10000/api/dostk/websocket'  # 접속 URL
CONST_HOST = 'https://api.kiwoom.com' # 'https://mockapi.kiwoom.com' # 모의투자
CONST_APP_KEY = 'HxIg0sKLV5tEmvfc6iBjrAiiOQOcRMfQFqAAmIFnJX8'
CONST_SECRET_KEY = 'FDyP9WISQQlRwo5IzA0Dg5sXUdl6oRR6l8ASL2cfoPE'

# 매수/매도 관련
CONST_SELL_EXCLUDE_RATE = float(29) # 종목등락률 이상이면 매도 제외
CONST_SELL_EARNING_RATE = float(5) # 매도 수익률
CONST_SELL_LOSS_RATE = float(-2) # 상승주 매도 손절율
CONST_BUY_PRICE_RATE = float(0.01) # 상승주 매수주문 시 매수단가 호가율
CONST_SELL_EXCLUDE_AMOUNT = int(str('1,500,000').replace(',','')) # 매도 시 기준금액이상이면 제외
CONST_BUY_TOTAL_AMOUNT = int(str('300,000').replace(',','')) # 종목당 매수할 금액
CONST_DEPOSIT_MINIMUM_AMOUNT = int(str('10,000').replace(',','')) # 예수금 최저 잔고 금액

CONST_SLEEP_TIME = int(3*55) # 상승주 수행주기
CONST_START_TIME = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 9, 13, 30) # 시작 시간
CONST_END_TIME = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 15, 12, 0) # 종료 시간
CONST_EXCEL_DB_TIME = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 15, 40, 0) # excel logging / database save 시간

# 엑셀파일 위치
CONST_EXCEL_FOLDER = '..\\stockTradingLog\\excel\\'
CONST_EXCEL_BACKUP_FOLDER = '..\\stockTradingLog\\excel\\backup\\'
CONST_EXCEL_FILE_NAME = '주식자동매매일지'
CONST_EXCEL_EXTENSION = '.xlsx'

# 로그파일 위치
CONST_FILE_PATH_LOG = '..\\stockTradingLog\\log\\'
CONST_FILE_PATH_BACKUP = '..\\stockTradingLog\\log\\backup\\'
CONST_FILE_NAME_TRADING_LOG = '자동매매일지.txt'
CONST_FILE_NAME_SEARCH_LOG = '자동매매검색종목리스트.txt'
CONST_FILE_TRADING_LOG = CONST_FILE_PATH_LOG + CONST_FILE_NAME_TRADING_LOG
CONST_FILE_SEARCH_LOG = CONST_FILE_PATH_LOG + CONST_FILE_NAME_SEARCH_LOG
CONST_FILE_ERROR_LOG = CONST_FILE_PATH_LOG + '에러로그.txt'
CONST_FILE_NAME_ANALYSIS_LOG = '분석용검색종목리스트.txt'
CONST_FILE_ANALYSIS_LOG = CONST_FILE_PATH_LOG + CONST_FILE_NAME_ANALYSIS_LOG

# DB 관련
CONST_DB_USER = 'angel'
CONST_DB_PWD = 'angelpwd'
CONST_DB_DSN = 'localhost:1521/ANGELDB'
CONST_DB_INSTANT_CLIENT_PATH = 'C:\\instantclient_21_18'