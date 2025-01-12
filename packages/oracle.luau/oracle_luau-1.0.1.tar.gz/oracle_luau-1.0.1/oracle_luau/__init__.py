import base64, aiohttp, asyncio, logging, json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DecompilerOptions:
    """
    A class to handle decompilation options to the decompilation service.
    """
    
    def __init__(self, renamingType: str = None, removeDotZero: bool = None, removeFunctionEntryNote: bool = None, swapConstantPosition: bool = None, inlineWhileConditions: bool = None, showFunctionLineDefined: bool = None, removeUselessNumericForStep: bool = None, removeUselessReturnInFunction: bool = None, sugarRecursiveLocalFunctions: bool = None, sugarLocalFunctions: bool = None, sugarGlobalFunctions: bool = None, sugarGenericFor: bool = None, showFunctionDebugName: bool = None):
        if renamingType is not None:    
            self.renamingType = renamingType

        if renamingType is not None:
            self.removeDotZero = removeDotZero

        if renamingType is not None:
            self.removeFunctionEntryNote = removeFunctionEntryNote

        if renamingType is not None:
            self.swapConstantPosition = swapConstantPosition

        if renamingType is not None:
            self.inlineWhileConditions = inlineWhileConditions

        if renamingType is not None:
            self.showFunctionLineDefined = showFunctionLineDefined

        if renamingType is not None:
            self.removeUselessNumericForStep = removeUselessNumericForStep

        if renamingType is not None:
            self.removeUselessReturnInFunction = removeUselessReturnInFunction

        if renamingType is not None:
            self.sugarRecursiveLocalFunctions = sugarRecursiveLocalFunctions

        if renamingType is not None:
            self.sugarLocalFunctions = sugarLocalFunctions

        if renamingType is not None:
            self.sugarGlobalFunctions = sugarGlobalFunctions

        if renamingType is not None:
            self.sugarGenericFor = sugarGenericFor

        if renamingType is not None:
            self.showFunctionDebugName = showFunctionDebugName 
    
    def __call__(self):
        return json.dumps(self.__dict__)

class Decompiler:
    """
    An asynchronous class to handle decompilation requests to the decompilation service.

    :param key: The API key for authorization.
    :type key: str
    :param base_url: The base URL for the decompilation service.
    :type base_url: str
    :param max_concurrent_requests: The maximum number of concurrent requests per key.
    :type max_concurrent_requests: int
    """

    def __init__(self, key: str, decompiler_options: DecompilerOptions = DecompilerOptions(), base_url: str = 'https://oracle.mshq.dev/decompile', max_concurrent_requests: int = 5, retry_attempts: int = 3, retry_delay: int = 5):
        self.key = key
        self.base_url = base_url
        self.max_concurrent_requests = max_concurrent_requests
        self.decompiler_options = decompiler_options()
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def decompile(self, script: bytes):
        """
        Sends a decompilation request for the given script.

        :param script: The script to decompile, as bytes.
        :type script: bytes
        :raises Exception: If the request fails or the server returns an error status.
        :returns: The decompiled script as a string.
        :rtype: str
        """

        post_data = '{"script": "' + base64.b64encode(script).decode('utf-8') + '", "decompilerOptions": ' + self.decompiler_options +'}'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.key}'
        }

        for attempt in range(self.retry_attempts + 1):
            async with self.semaphore:
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.post(self.base_url, headers=headers, data=post_data) as response:
                            match response.status:
                                case 200:
                                    return await response.text()
                                case 429:
                                    logging.warning(f"Rate limited. Retrying in {self.retry_delay * (2 ** attempt)} seconds...")
                                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                                case 402:
                                    raise Exception('-- API key has expired or is invalid')
                                case 500:
                                    raise Exception('-- Decompilation failed!')
                                case 400:
                                    raise Exception('-- Bad request! Check your decompliation options and try again.')
                                case 502:
                                    logging.warning(f"Vorp? 👽 (Bad Gateway 502, this should not happen). Retrying in {self.retry_delay * (2 ** attempt)} seconds...")
                                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                                case _:
                                    raise Exception(f'-- Something went wrong when decompiling: {response.status}')

                    except aiohttp.ClientError as e:
                        if attempt == self.retry_attempts:
                            raise Exception(f'-- Request failed after retries: {e}')
                        else:
                            logging.warning(f"Request failed: {e}. Retrying...")
                            await asyncio.sleep(self.retry_delay * (2 ** attempt))
                            
class SyncDecompiler:
    """
    A synchronous class to handle decompilation requests to the decompilation service.

    :param key: The API key for authorization.
    :type key: str
    :param base_url: The base URL for the decompilation service.
    :type base_url: str
    :param max_concurrent_requests: The maximum number of concurrent requests per key.
    :type max_concurrent_requests: int
    """

    def __init__(self, key: str, decompiler_options: DecompilerOptions = DecompilerOptions(), base_url: str = 'https://oracle.mshq.dev/decompile', max_concurrent_requests: int = 5, retry_attempts: int = 3, retry_delay: int = 5):
        import queue, urllib3, time
        
        self.key = key
        self.base_url = base_url
        self.max_concurrent_requests = max_concurrent_requests
        self.decompiler_options = decompiler_options()
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
        self.urllib3 = urllib3
        self.time = time
        self.request_queue = queue.Queue(maxsize=self.max_concurrent_requests)

    def decompile(self, script: bytes):
        """
        Sends a decompilation request for the given script.

        :param script: The script to decompile, as bytes.
        :type script: bytes
        :raises Exception: If the request fails or the server returns an error status.
        :returns: The decompiled script as a string.
        :rtype: str
        """

        post_data = '{"script": "' + base64.b64encode(script).decode('utf-8') + '", "decompilerOptions": ' + self.decompiler_options +'}'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.key}'
        }

        for attempt in range(self.retry_attempts + 1):
            try:
                self.request_queue.put(0)
                
                response = self.urllib3.request('POST', self.base_url, headers=headers, body=post_data)

                self.request_queue.get()
                self.request_queue.task_done()

                match response.status:
                    case 200:
                        return response.data.decode('utf-8')
                    case 429:
                        logging.warning(f"Rate limited. Retrying in {self.retry_delay * (2 ** attempt)} seconds...")
                        self.time.sleep(self.retry_delay * (2 ** attempt))
                    case 402:
                        raise Exception('-- API key has expired or is invalid')
                    case 500:
                        raise Exception('-- Decompilation failed!')
                    case 400:
                        raise Exception('-- Bad request! Check your decompliation options and try again.')
                    case _:
                        raise Exception(f'-- Something went wrong when decompiling: {response.status}')

            except self.requests.exceptions.RequestException as e:
                self.request_queue.get()
                self.request_queue.task_done()
                
                if attempt == self.retry_attempts:
                    raise Exception(f'-- Request failed after multiple retries: {e}')
                else:
                    logging.warning(f"Request failed: {e}. Retrying...")
                    self.time.sleep(self.retry_delay * (2 ** attempt))