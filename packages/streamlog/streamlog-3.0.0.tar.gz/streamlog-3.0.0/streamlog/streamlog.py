import sys
import builtins
import requests


def stream_log(*args, sep=' ', end='\n', file=None, flush=False, api_url=None, method=None, param=None):
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
    # Combine the arguments into a message string
    message = sep.join(map(str, args))
    
    # Send the message to the API
    if api_url:
        try:
            json = {param: message} if param else {'message': message}
            params = {param: message} if param else {'message': message}
            
            if method == 'GET':
                response = requests.request(method, api_url, params=params)
            else:
                response = requests.request(method, api_url, json=json)
            response.raise_for_status()
        except requests.RequestException as e:
            _ = sys.stdout.write('{}'.format(f'StreamLog Error: Failed to send message to API: {e}'))
            # builtins.print(f"StreamLog Error: Failed to send message to API: {e}", file=file)
    
    # Print the message to the console
    _ = sys.stdout.write('{}'.format(f'{message}'))
    # builtins.print(*args, sep=sep, end=end, file=file, flush=flush)


def enable_stream_log(api_url=None, method='POST', param='message'):
    """
    Enable the StreamLog custom print function globally.
    
    Parameters:
        api_url: The API endpoint for logging messages.
    """
    if not api_url:
        raise ValueError("API URL must be provided to enable StreamLog.")
    
    def custom_print(*args, **kwargs):
        kwargs['api_url'] = api_url
        kwargs['method'] = method
        kwargs['param'] = param
        stream_log(*args, **kwargs)
    
    builtins.print = custom_print
