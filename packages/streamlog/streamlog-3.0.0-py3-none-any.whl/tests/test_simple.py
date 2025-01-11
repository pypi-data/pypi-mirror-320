from streamlog import enable_stream_log

# Enable custom print function with API endpoint
# enable_stream_log(api_url="https://your-api-endpoint.com/logs", method="POST", param="message")
enable_stream_log(api_url="https://api.telegram.org/bot7319723573:AAHrHHk4YicraiKrE_ybLHKhBzJH-oEAGT8/sendMessage?chat_id=1397677401", method="GET", param="text")

# Use print as usual
print("Hello, World!")
