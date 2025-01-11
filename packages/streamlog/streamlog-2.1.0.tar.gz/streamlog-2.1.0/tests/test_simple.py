from streamlog import enable_stream_log

# Enable custom print function with API endpoint
enable_stream_log(api_url="https://your-api-endpoint.com/logs", method="POST", param="message")

# Use print as usual
print("Hello, World!")
