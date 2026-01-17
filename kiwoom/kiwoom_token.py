import requests
from datetime import datetime

# 접근토큰 발급
def get_token(host, appkey, secretkey) :
	# 1. 요청할 API URL
	__endpoint = '/oauth2/token'
	__url =  host + __endpoint

	# 2. header 데이터
	__headers = {
		'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
	}
    # 3. data 데이터
	__data = {
		'grant_type': 'client_credentials',  # grant_type
		'appkey': appkey,  # 앱키
		'secretkey': secretkey,  # 시크릿키
	}

	# 4. http POST 요청
	response = requests.post(__url, headers=__headers, json=__data)

	# 5. 응답 상태 코드와 데이터 출력
	""" print('Code:', response.status_code)
	print('Header:', json.dumps({key: response.headers.get(key) for key in ['next-key', 'cont-yn', 'api-id']}, indent=4, ensure_ascii=False))
	print('Body:', json.dumps(response.json(), indent=4, ensure_ascii=False))  # JSON 응답을 파싱하여 출력
	"""

	__token = ''
	if response.json()['return_code'] == 0 :
		print(datetime.now(), '******* 접근토큰 발급이 정상처리되었습니다.')
		__token = response.json()['token']
	else :
		print(datetime.now(), '******* 접근토큰 발급시 에러가 발생했습니다.')
		print('***** 에러 내용 : ', response.json()['return_msg'])

	return __token
