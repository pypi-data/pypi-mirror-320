import asyncio
import json
import websockets
from aiohttp import ContentTypeError
from urllib3.util import parse_url
from websockets.exceptions import ConnectionClosedError
import urllib
from urllib.parse import urlparse
from typing import *
from datetime import datetime
import tzlocal
import aiohttp
import aioftp

from PIL import Image
import base64
from io import BytesIO

from IPython import get_ipython
try:
    if 'IPKernelApp' in get_ipython().config:
        import nest_asyncio
        nest_asyncio.apply()
except Exception:
    pass

from AIDepot import Resources, VISION

# Note on vision support from the client:
#
# The client accepts the following format, for vision enabled models, and will put it into the server-side API format.
# Optionally, you may build the message directly in API format and send it through the client.
# Note that if you do that then the image needs to be sized correctly for the model that you are using,
# the size can be seen in AIDepot.Resources
#
# image_path may be a local file name, an http URL or an ftp URL
#
# Client assist format:
#
# response = client.chat.completions.create(
# conversations = [{
#     'messages': [
#         {
#             "role": "user",
#             "content": [
#                 {"type": "text", "data": "What’s in this image?"},
#                 {
#                     "type": "image_path",
#                     "data": "/home/me/myImage.png",
#                     - or -
#                     "data": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
#                     - or -
#                     "data": "ftps://username:password@hostname/path/to/file",
#                 },
#             ],
#         }
#     ],
#     'max_tokens': 1000,
# }]
#
# API format:
#
# conversations = [{
#     'messages': [
#         {
#             "role": "user",
#             "content": [
#                 {"type": "text", "data": "What’s in this image?"},
#                 {
#                     "type": "image",
#                     "data": "data:image/jpeg;base64,{base64string}",
#                 },
#             ],
#         }
#     ],
#     'max_tokens': 1000,
# }]


class Client():

    URL = 'aidepot.net'
    API_PATH = 'api'
    WEBSOCKET_API_PATH = 'api/ws/status'

    def __init__(self, subscriber_id: str, api_key: str):
        self.subscriber_id = subscriber_id
        self.api_key = api_key

        self.headers = {
            'User-Agent': 'AIDepotClient/1.0',
            'accept': 'application/json',
            'X-SUBSCRIBER-ID': subscriber_id,
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

        self.session = None
        self.local_timezone = tzlocal.get_localzone()
        self.ftp_client = None

    def __del__(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._destroy_session())

    def submit_job(self, resource: Resources, job: dict, version: str = '1') -> Tuple[int, Optional[dict], dict]:
        """Submit a job to the server and wait for the response

        Returns:
        When the job submission is successful:
            (HTTP status code of completed job, completed job response, job submission response)
        When the job submission is not successful:
            (HTTP status code of job submission request, None, job submission response)
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._submit_job_async(resource, job, version))

    async def submit_job_async(self,
                               resource: Resources,
                               job: dict,
                               version: str = '1') -> Tuple[int, Optional[dict], dict]:
        """Submit a job to the server and a future waits for the response

        Returns a future. Awaiting the future will return the following:
        When the job submission is successful:
            (HTTP status code of completed job, completed job response, job submission response)
        When the job submission is not successful:
            (HTTP status code of job submission request, None, job submission response)
        """
        return await self._submit_job_async(resource, job, version)

    def start_job(self, resource: Resources, job: dict, version: str = '1') -> Tuple[int, dict]:
        """Start a job and wait for the job submittal status

        Returns (http status code, job submittal response)
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.start_job_async(resource, job, version))

    async def start_job_async(self, resource: Resources, job: dict, version: str = '1') -> Tuple[int, dict]:
        """Start a job without waiting for the job submittal status

        Returns a future, when awaited gives: (http status code, job submittal response)
        """

        # Perform any preprocessing that is needed here
        if VISION in resource.value:
            output_image_size = resource.value[VISION]
            tasks = []
            for conversation in job['conversations']:
                for message in conversation['messages']:
                    for content_item in message['content']:
                        if content_item['type'] == 'image_path':
                            task = self._enhance_message_for_vision(message, output_image_size, format='JPEG')
                            tasks.append(task)
                            break
            if tasks:
                await asyncio.gather(*tasks)

        code, response = await self._submit_http_request_async(resource, job, version)
        return (code, self._parse_dict(response))

    def get_job_result(self, resource: Resources, job_id: int, version='1') -> Tuple[int, dict]:
        """ Fetch the job results given the job_id.

        Does not wait for the job to complete.
        If you want to wait for the job to complete, call connect_and_listen_for_status(...) instead.

        When the job is complete, the responses will be included in the response.
        When the job is pending, the response will note this and not include results.
        If the job failed, the response will note this.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.get_job_result_async(resource, job_id, version))

    async def get_job_result_async(self, resource: Resources, job_id: int, version='1') -> Tuple[int, dict]:
        """ Fetch the job results given the job_id.

        Does not wait for the job to complete.
        If you want to wait for the job to complete, call connect_and_listen_for_status_async(...) instead.

        When the job is complete, the responses will be included in the response.
        When the job is pending, the response will note this and not include results.
        If the job failed, the response will note this.
        """
        job = {
            'job_id': job_id
        }

        return await self.start_job_async(resource, job, version)

    def connect_and_listen_for_status(self, job_id: int) -> Tuple[int, dict]:
        """ Waits for the job to complete and then immediately returns the response """

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.connect_and_listen_for_status_async(job_id))

    async def connect_and_listen_for_status_async(self, job_id: int) -> Tuple[int, dict]:
        """ Waits for the job to complete and then immediately returns the response """
        websocket_headers = {
            'User-Agent': 'AIDepotClient/1.0',
            'X-SUBSCRIBER-ID': self.subscriber_id,
            'X-API-KEY': self.api_key,
        }

        num_retries = 0
        num_chunks = 0
        chunks_received = 0
        chunks = []

        while True:
            try:
                websocket_url = self.build_websocket_route(job_id)

                async with websockets.connect(websocket_url, additional_headers=websocket_headers) as websocket:

                    # Listen and respond to messages indefinitely
                    while True:
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=25)

                            response = json.loads(response)
                            if response == {
                                    'message': 'pong'
                            }:
                                continue

                            if len(response.keys()) == 1 and 'chunks' in response.keys():
                                chunks_received = 0
                                num_chunks = response['chunks']
                                chunks = [None for i in range(num_chunks)]
                            elif len(response.keys()) == 1 and list(response.keys())[0].startswith('chunk_'):
                                key, payload = response.popitem()
                                current_chunk = int(key[6:])
                                if current_chunk > num_chunks:
                                    continue
                                chunks_received += 1
                                chunks[current_chunk] = payload

                                if chunks_received == num_chunks:
                                    result_json = ''.join(chunks)
                                    # Any nicety parsing of the results are done via _parse_dict,
                                    # for example putting timestamps in the user's timezone
                                    result = self._parse_dict(json.loads(result_json))
                                    return (200, result)
                            elif 'responses' in response.keys():
                                # Any nicety parsing of the results are done via _parse_dict,
                                # for example putting timestamps in the user's timezone
                                result = self._parse_dict(response)
                                return (200, result)
                            else:
                                return (
                                    500, {
                                        'error':
                                            ValueError(f"Websocket response not understood, keys: {response.keys()}")
                                    })

                        except asyncio.TimeoutError:
                            # Did not receive a response in the number of seconds waiting,
                            # so send a heartbeat to keep the connection alive
                            await websocket.send(json.dumps({'message': 'ping'}))
                        except ConnectionClosedError as e:
                            code = e.rcvd.code
                            if code >= 2000:
                                # Some unretriable error
                                print(f"Error: Connection closed by the websocket server with code : {code}")
                                return (e.rcvd.code, {})
                            else:
                                # Could be a going away notification
                                # Break the inner loop to reconnect
                                break
            except (ConnectionRefusedError, OSError):
                if num_retries < 3:
                    retry_backoff = 3
                    print(f"Failed to connect to the server. Retrying in {retry_backoff} seconds...")
                    await asyncio.sleep(retry_backoff)
                    num_retries += 1
                else:
                    raise
            except Exception as e:
                if num_retries == 0:
                    retry_backoff = 3
                    print(f"Unexpected error: {e}. Retrying in {retry_backoff} seconds...")
                    await asyncio.sleep(retry_backoff)
                else:
                    raise

    @staticmethod
    def build_http_route(resource: Resources, version: str = '1'):
        api_path = f'https://{Client.URL}/{Client.API_PATH}/v{version}/{resource.value["route"]}/'
        return api_path

    def build_websocket_route(self, job_id: int):
        subsciber_id_qt = urllib.parse.quote(self.subscriber_id)
        websocket_url = f'wss://{Client.URL}/{Client.WEBSOCKET_API_PATH}/{subsciber_id_qt}/{job_id}/'
        return websocket_url

    async def _submit_job_async(self,
                                resource: Resources,
                                job: dict,
                                version: str = '1') -> Tuple[int, Optional[dict], dict]:

        job_submittal_status, job_submittal_response = await self.start_job_async(resource, job, version)

        if job_submittal_status >= 400:
            return (job_submittal_status, None, job_submittal_response)

        # Retrieve the job id from the submission response,
        # and open a websocket to listen for the finished job's response
        job_id = job_submittal_response['job_id']
        response_code, result = await self.connect_and_listen_for_status_async(job_id)

        return response_code, result, job_submittal_response

    async def _submit_http_request_async(self, resource: Resources, job: dict, version: str):
        api_path = self.build_http_route(resource, version)

        if self.session is None:
            await self._create_session()

        async with self.session.post(api_path, json=job, headers=self.headers) as response:
            job_submittal_status = response.status
            try:
                job_submittal_response = await response.json()
            except ContentTypeError as ex:
                # When it is text, that indicates an error, put this in a dict using key 'error'
                job_submittal_response = await response.text()
                job_submittal_response = {
                    'error': job_submittal_response
                }
        return job_submittal_status, job_submittal_response

    async def _create_session(self):
        if self.session is None:
            self.session = await aiohttp.ClientSession().__aenter__()

    async def _destroy_session(self):
        if self.session is not None:
            await self.session.close()

    def _parse_dict(self, d) -> Any:
        if isinstance(d, dict):
            n = {}
            for key, value in d.items():
                if isinstance(key, str) and isinstance(value, str):
                    n[key] = self._parse_str(key, value)
                else:
                    n[key] = self._parse_dict(value)
            return n
        elif isinstance(d, list):
            v = []
            for x in d:
                v.append(self._parse_dict(x))
            return v
        else:
            return d

    def _parse_str(self, key: str, value: str) -> any:
        if key.endswith('timestamp'):
            return datetime.fromisoformat(value).astimezone(self.local_timezone)
        else:
            return value

    async def image_to_base64(self, image_path, output_size: Tuple[int, int] = (512, 512), format: str = 'JPEG') -> str:

        # HTTP
        if image_path.startswith('http://') or image_path.startswith('https://'):
            # Fetch the image from the URL
            async with self.session.get(image_path) as response:
                if response.status == 200:
                    content = await response.read()
                    image = Image.open(BytesIO(content))
                else:
                    raise Exception(f"Failed to fetch image {image_path}. Status code: {response.status}")

        # FTP
        elif image_path.startswith('ftp://') or image_path.startswith('ftps://'):
            if self.ftp_client is None:
                self.ftp_client = aioftp.Client()

            parsed_url = parse_url(image_path)
            host = parsed_url.hostname
            path = parsed_url.path
            username = parsed_url.username
            password = parsed_url.password
            port = parsed_url.port

            image_buffer = BytesIO()

            try:
                # Connect to the FTP server
                if port is None:
                    await self.ftp_client.connect(host)
                else:
                    await self.ftp_client.connect(host, port=port)

                # Login to the FTP server
                if username and password:
                    await self.ftp_client.login(username, password)
                else:
                    # anonymous login
                    await self.ftp_client.login()

                # Download the specified file
                async with self.ftp_client.download_stream(path) as stream:
                    async for block in stream.iter_by_block():
                        image_buffer.write(block)

                image_buffer.seek(0)
                image = Image.open(image_buffer)

            except Exception as e:
                raise Exception(f"Failed to fetch image {image_path}. {str(e)}")

            finally:
                # Always close the client
                await self.ftp_client.quit()

        # Local file
        else:
            image = Image.open(image_path)

        # Ensure correct size and encode as base64 string
        with image:
            if image.size != output_size:
                image = image.resize(output_size, Image.ANTIALIAS)
            img_buffer = BytesIO()
            image.save(img_buffer, format=format)
            byte_data = img_buffer.getvalue()
            base64_str = base64.b64encode(byte_data)
            return base64_str.decode('utf-8')

    async def _enhance_message_for_vision(self, message: dict, output_image_size: Tuple[int, int], format: str):
        # Replace the image_path with a properly sized image encoded in base64
        for content in message['content']:
            if content['type'] == 'image_path':
                image_path = content['data']
                image_base64 = await self.image_to_base64(image_path, output_size=output_image_size, format=format)
                content['data'] = f"data:image/{format.lower()};base64,{image_base64}"
