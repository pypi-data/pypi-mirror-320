import builtins
import requests


def stream_log(*args, sep=' ', end='\n', file=None, flush=False, api_url='', method='', param=''):
    """
        Custom print function that logs messages to an API and prints to the console.
        
        Parameters:
            *args: Values to print.
            sep: Separator between values (default: ' ').
            end: String appended after the last value (default: '\n').
            file: File-like object where output is sent (default: sys.stdout).
            flush: Whether to forcibly flush the stream.
            api_url: API endpoint to which the message is sent.
    """
    if not api_url:
        raise ValueError("StreamLog Error: API URL is required.")
    
    # Combine the arguments into a message string
    message = sep.join(map(str, args))
    
    # Send the message to the API
    try:
        
        json = {param: message} if param else {'message': message}
        params = {param: message} if param else {'message': message}
        
        if method == 'GET':
            response = requests.request(method, api_url, params=params)
        else:
            response = requests.request(method, api_url, json=json)
        response.raise_for_status()
    except requests.RequestException as e:
        builtins.print(f"StreamLog Error: Failed to send message to API: {e}", file=file)
    
    # Print the message to the console
    builtins.print(*args, sep=sep, end=end, file=file, flush=flush)


def enable_stream_log(api_url='', method='POST', param=''):
    """
        Enable the StreamLog custom print function globally.
        
        Parameters:
            api_url: The API endpoint for logging messages.
    """
    global print
    if not api_url:
        raise ValueError("StreamLog Error: API URL is required.")
    
    print = lambda *args, **kwargs: stream_log(*args, **kwargs, api_url=api_url, method=method, param=param)
