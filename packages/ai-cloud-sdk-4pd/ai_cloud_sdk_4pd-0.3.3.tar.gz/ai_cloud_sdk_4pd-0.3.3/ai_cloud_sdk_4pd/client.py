import base64
import datetime
import json
import logging

import requests

from ai_cloud_sdk_4pd import models as ai_cloud_sdk_4pd_models


class Client:
    def __init__(
        self,
        config: ai_cloud_sdk_4pd_models.Config,
    ):
        self._token = config.token
        self._call_token = config.call_token

        self._blacklist_token = []
        self._blacklist_call_token = []

        # proxies 格式 {"China": ["http://localhost:port"], "HongKong": [], "Other": []}
        self._proxies = None
        # self._proxies = {"China": ["http://localhost:8202"]}
        self._endpoint = config.endpoint
        self._region = config.region

        self.__get_proxy_ip_config()
        self.__set_region_and_endpoint()
        self.__verify_tokens()

    def __set_region_and_endpoint(self) -> None:
        # 如果endpoint已给出且合法，则直接返回
        if self._endpoint:
            for region, endpoints in self._proxies.items():
                if self._endpoint in endpoints:
                    self._region = region
                    return

        # 如果endpoint未给出或不合法，且region存在且合法，则根据region确定endpoint
        if self._region:
            for region, endpoints in self._proxies.items():
                if self._region == region:
                    self._endpoint = endpoints[0]
                    return

        # 如果endpoint未给出或不合法，且region不存在或不合法，则默认endpoint(China)
        self._region = 'China'
        self._endpoint = self._proxies.get('China')[0]
        return

    def __verify_tokens(self) -> None:
        # 如果token或call_token未给出，则抛出异常
        if self._token is None or self._call_token is None:
            raise ValueError('token and call_token is required')

    def __get_proxy_ip_config(self) -> None:
        try:
            proxy_config_url = 'https://sagegpt.4paradigm.com/4pd_aiclound/config'
            response = requests.get(proxy_config_url)
            response_json = response.json()
            data = response_json.get('data', {})
            proxies = data.get('proxies', {})
            self._proxies = proxies
        except Exception as e:
            raise e

    def audio_language_detection(
        self,
        request: ai_cloud_sdk_4pd_models.AudioLanguageDetectionRequest = None,
    ) -> ai_cloud_sdk_4pd_models.AudioLanguageDetectionResponse:

        # 如果token或call_token在黑名单中，则抛出异常
        if (
            self._token in self._blacklist_token
            or self._call_token in self._blacklist_call_token
        ):
            raise ValueError('token or call_token is forbidden to send request')

        full_url = f'{self._endpoint}{request.api}'

        headers = {
            'token': self._token,
            'call_token': self._call_token,
        }

        file_url = request.audio
        metadata = request.metadata
        choices = request.choices
        files = {'audio': (file_url, open(file_url, 'rb'))}

        response = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
            data={'metadata': metadata, 'choices': choices},
            files=files,
        )

        # 如果返回码为503，则将token和call_token加入黑名单
        if response.json().get('code', None) == 503:
            self._blacklist_token.append(self._token)
            self._blacklist_call_token.append(self._call_token)
            raise ValueError('token or call_token is invalid')

        base_resp = ai_cloud_sdk_4pd_models.BaseResponse(
            code=response.json().get('code', None),
            data=response.json().get('data', None),
            message=response.json().get('message', None),
        )
        return ai_cloud_sdk_4pd_models.AudioLanguageDetectionResponse(
            response=base_resp
        )

    def asr(
        self,
        request: ai_cloud_sdk_4pd_models.ASRRequest = None,
        on_ready: callable = None,
        on_response: callable = None,
        on_completed: callable = None,
    ) -> None:

        if (
            self._token in self._blacklist_token
            or self._call_token in self._blacklist_call_token
        ):
            raise ValueError('token or call_token is forbidden to send request')

        full_url = f"{self._endpoint}{request.api}"
        headers = {
            'token': self._token,
            'call_token': self._call_token,
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
        }

        file_url = request.audio_url
        try:
            with open(file_url, 'rb') as f:
                audio_data = f.read()
                audio_base64 = base64.b64encode(audio_data)
                audio_base64 = audio_base64.decode('utf-8')
        except FileNotFoundError:
            raise ValueError('File not found. Please check the path and try again.')

        # 发送音频数据
        message = {
            "enableWords": True,
            "lang": request.language,
            "fileBase64": audio_base64,
            "finalResult": 'true' if request.final_result else 'false',
        }

        message = json.dumps(message)

        try:
            session = requests.Session()
            with session.post(
                full_url,
                data=message,
                headers=headers,
                stream=True,
                timeout=600,
            ) as response:
                if response.status_code == 200:
                    logging.info('HTTP STREAM connection established')

                if response.status_code == 503:
                    self._blacklist_token.append(self._token)
                    self._blacklist_call_token.append(self._call_token)
                    raise ValueError('token or call_token is invalid')

                for chunk in response.iter_lines():
                    if chunk:
                        chunk_str = chunk.decode('utf-8')
                        chunk_json = chunk_str.split(":", 1)[1]
                        resp = json.loads(chunk_json)
                        if 'success' in resp and bool(resp['success']):
                            on_ready()
                            continue

                        if 'end' in resp and bool(resp['end']):
                            on_completed()
                            break

                        if request.final_result is False:
                            on_response(resp)
                            continue

                        if (
                            'asr_results' in resp
                            and 'final_result' in resp['asr_results']
                            and bool(resp['asr_results']['final_result'])
                        ):
                            on_response(resp)
                            continue
        except Exception as e:
            print(e)
            print(datetime.datetime.now())

    def translate_text(
        self,
        request: ai_cloud_sdk_4pd_models.TranslateTextRequest = None,
    ) -> ai_cloud_sdk_4pd_models.TranslateTextResponse:

        # 如果token或call_token在黑名单中，则抛出异常
        if (
            self._token in self._blacklist_token
            or self._call_token in self._blacklist_call_token
        ):
            raise ValueError('token or call_token is forbidden to send request')

        full_url = f'{self._endpoint}{request.api}'
        headers = {
            'token': self._token,
            'call_token': self._call_token,
            'content-type': request.content_type,
        }

        payload = {'text': request.text}

        response = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
            data=json.dumps(payload),
        )

        # 如果返回码为503，则将token和call_token加入黑名单
        if response.json().get('code', None) == 503:
            self._blacklist_token.append(self._token)
            self._blacklist_call_token.append(self._call_token)
            raise ValueError('token or call_token is invalid')

        base_resp = ai_cloud_sdk_4pd_models.BaseResponse(
            code=response.json().get('code', None),
            data=response.json().get('data', None),
            message=response.json().get('message', None),
        )
        return ai_cloud_sdk_4pd_models.TranslateTextResponse(response=base_resp)

    def tts(
        self,
        request: ai_cloud_sdk_4pd_models.TTSRequest = None,
    ):

        # 如果token或call_token在黑名单中，则抛出异常
        if (
            self._token in self._blacklist_token
            or self._call_token in self._blacklist_call_token
        ):
            raise ValueError('token or call_token is forbidden to send request')

        full_url = f'{self._endpoint}{request.api}'
        headers = {
            'token': self._token,
            'call_token': self._call_token,
            'content-type': request.content_type,
        }

        payload = {
            'transcription': str(request.transcription),
            'voiceName': request.voice_name,
            'language': request.language,
        }

        response = requests.request(
            method=request.method,
            url=full_url,
            headers=headers,
            data=json.dumps(payload),
        )

        return response

    #
    # @staticmethod
    # async def _send_data(websocket, file_path):
    #     with open(file_path, 'rb') as f:
    #         # 去除wav头文件
    #         f.seek(44)
    #         while True:
    #             data = f.read(3200)
    #             if not data:
    #                 break
    #             await websocket.send(data)
    #             # print('send data')
    #             # print(datetime.datetime.now())
    #             # 100ms延迟
    #             await asyncio.sleep(0.6)
    #
    #     await asyncio.sleep(10)
    #     await websocket.send('{"end": true}')
    #     # print(datetime.datetime.now())
    #
    #     # print('------------------send end------------------')
    #
    # @staticmethod
    # async def _receive_data(
    #     websocket,
    #     request,
    #     on_ready,
    #     on_response,
    #     on_completed,
    # ):
    #     # count = 0
    #     try:
    #         while True:
    #             resp = await websocket.recv()
    #             resp_json = json.loads(resp)
    #
    #             if 'success' in resp_json and bool(resp_json['success']):
    #                 print('ready')
    #                 await on_ready()
    #                 continue
    #
    #             if request.final_result is False:
    #                 await on_response(resp_json)
    #                 continue
    #
    #             if (
    #                 'asr_results' in resp_json
    #                 and 'final_result' in resp_json['asr_results']
    #                 and bool(resp_json['asr_results']['final_result'])
    #             ):
    #                 await on_response(resp_json)
    #                 # print('------------------------------')
    #                 # print(count)
    #                 # count += 1
    #                 # print('recv resp:', resp_json)
    #                 # print('------------------------------')
    #     except websockets.exceptions.ConnectionClosedOK:
    #         # print('ConnectionClosedOK')
    #         await on_completed()
    #
    # async def asr_direct(
    #     self,
    #     request: ai_cloud_sdk_4pd_models.ASRRequest = None,
    #     on_ready: callable = None,
    #     on_response: callable = None,
    #     on_completed: callable = None,
    # ):
    #     # print('-------------test asr-------------')
    #
    #     file_path = request.audio_url
    #
    #     hello_message = '{"parameter": {"lang": null,"enable_words": true}}'
    #
    #     async with websockets.connect(
    #         'ws://172.26.1.45:31529/recognition',
    #         ping_timeout=60,
    #         ping_interval=60,
    #         close_timeout=60,
    #     ) as websocket:
    #         await websocket.send(hello_message)
    #         # print('send hello message')
    #         resp = await websocket.recv()
    #         # print('recv resp:', resp)
    #
    #         # 创建并发任务：一个发送数据，一个接收数据
    #         send_task = asyncio.create_task(self._send_data(websocket, file_path))
    #         receive_task = asyncio.create_task(
    #             self._receive_data(
    #                 websocket, request, on_ready, on_response, on_completed
    #             )
    #         )
    #
    #         # 等待发送任务完成
    #         await send_task
    #         # 等待接收任务完成
    #         await receive_task
    #
    # async def asr_direct_vi(
    #     self,
    #     request: ai_cloud_sdk_4pd_models.ASRRequest = None,
    #     on_ready: callable = None,
    #     on_response: callable = None,
    #     on_completed: callable = None,
    # ):
    #     # print('-------------test asr-------------')
    #
    #     file_path = request.audio_url
    #
    #     hello_message = '{"parameter": {"lang": null,"enable_words": true}}'
    #
    #     async with websockets.connect(
    #         'ws://172.26.1.45:23238/recognition',
    #         ping_timeout=60,
    #         ping_interval=60,
    #         close_timeout=60,
    #     ) as websocket:
    #         await websocket.send(hello_message)
    #         # print('send hello message')
    #         resp = await websocket.recv()
    #         # print('recv resp:', resp)
    #
    #         # 创建并发任务：一个发送数据，一个接收数据
    #         send_task = asyncio.create_task(self._send_data(websocket, file_path))
    #         receive_task = asyncio.create_task(
    #             self._receive_data(
    #                 websocket, request, on_ready, on_response, on_completed
    #             )
    #         )
    #
    #         # 等待发送任务完成
    #         await send_task
    #         # 等待接收任务完成
    #         await receive_task
