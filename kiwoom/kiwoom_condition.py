import asyncio
import websockets
import json
from kiwoom.stock import Stock
from helper.constants import CONST_SOCKET_URL, CONST_BUY_TOTAL_PRICE

stocks = []

class WebSocketClient:
	def __init__(self, token):
		self.uri = CONST_SOCKET_URL
		self.token = token
		self.websocket = None
		self.connected = False
		self.keep_running = True

	# WebSocket 서버에 연결합니다.
	async def connect(self):
		try:
			self.websocket = await websockets.connect(self.uri)
			self.connected = True

			# 로그인 패킷
			param = {
				'trnm': 'LOGIN',
				'token': self.token
			}

			# 웹소켓 연결 시 로그인 정보 전달
			await self.send_message(message=param)

		except Exception as e:
			print(f'***** Connection error: {e}')
			self.connected = False

	# 서버에 메시지를 보냅니다. 연결이 없다면 자동으로 연결합니다.
	async def send_message(self, message):
		if not self.connected:
			await self.connect()  # 연결이 끊어졌다면 재연결
		if self.connected:
			# message가 문자열이 아니면 JSON으로 직렬화
			if not isinstance(message, str):
				message = json.dumps(message)

		await self.websocket.send(message)

	# 서버에서 오는 메시지를 수신하여 출력합니다.
	async def receive_messages(self):
		while self.keep_running:
			try:
				# 서버로부터 수신한 메시지를 JSON 형식으로 파싱
				response = json.loads(await self.websocket.recv())

				# 메시지 유형이 LOGIN일 경우 로그인 시도 결과 체크
				if response.get('trnm') == 'LOGIN':
					if response.get('return_code') != 0:
						print('***** LOGIN 로그인 실패하였습니다. : ', response.get('return_msg'))
						await self.disconnect()
					else:
						param = {
							'trnm': 'CNSRLST'
						}
						await self.send_message(message=param)

				# 메시지 유형이 PING일 경우 수신값 그대로 송신
				elif response.get('trnm') == 'PING':
					await self.send_message(response)

				if response.get('trnm') == 'CNSRREQ':
				# 	print(f'실시간 시세 서버 응답 수신: {response}')
					reps = response.get('data')
					if reps :
						for r in reps :
							if r.get('9001') and int(r.get('10')) <= CONST_BUY_TOTAL_PRICE :
								__stock = Stock(r.get('9001'), r.get('302'), int(r.get('10')), 0)
								__stock.before_rate = float(r.get('11')) # 전일대비
								__stock.rate = float(r.get('12')) # 등락률
								__stock.s_price = int(r.get('16')) # 시초가
								__stock.h_price = int(r.get('17')) # 고가
								__stock.l_price = int(r.get('18')) # 저가
								stocks.append(__stock)

					await self.disconnect()

			except websockets.ConnectionClosed:
				# print('***** Connection closed by the server')
				self.connected = False
				await self.websocket.close()
	# WebSocket 실행
	async def run(self):
		await self.connect()
		await self.receive_messages()

	# WebSocket 연결 종료
	async def disconnect(self):
		self.keep_running = False
		if self.connected and self.websocket:
			await self.websocket.close()
			self.connected = False
			# print('***** Disconnected from WebSocket server')

async def main(token, seq):
	# WebSocketClient 전역 변수 선언
	websocket_client = WebSocketClient(token)

	# WebSocket 클라이언트를 백그라운드에서 실행합니다.
	receive_task = asyncio.create_task(websocket_client.run())

	# 실시간 항목 등록
	await asyncio.sleep(1)
	await websocket_client.send_message({
		'trnm': 'CNSRREQ', # 서비스명
		'seq': str(seq), # 조건검색식 일련번호
		'search_type': '0', # 조회타입
		'stex_tp': 'K', # 거래소구분
		'cont_yn': 'N', # 연속조회여부
		'next_key': '', # 연속조회키
	})

	# 수신 작업이 종료될 때까지 대기
	await receive_task

def search(token, seq) :
	asyncio.run(main(token, seq))

	return stocks