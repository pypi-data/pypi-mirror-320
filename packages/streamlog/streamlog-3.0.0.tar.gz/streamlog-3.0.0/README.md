# StreamLog

**StreamLog** is a Python package that extends the functionality of the `print` statement by simultaneously sending printed messages to an API. It’s designed to help developers log important information to remote servers while maintaining console output.


<p id="top" align="right">
  <a href="https://github.com/PrathmeshSoni">
  <img src="https://badges.pufler.dev/visits/prathmeshsoni/StreamLog?label=VISITOR&style=for-the-badge&logoColor=FFFFFF&color=purple&labelColor=640464&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9IndoaXRlIiB2ZXJzaW9uPSIxLjEiIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDE2IDE2IiBjbGFzcz0ib2N0aWNvbiBvY3RpY29uLWV5ZSIgYXJpYS1oaWRkZW49InRydWUiPjxwYXRoIGQ9Ik04IDJjMS45ODEgMCAzLjY3MS45OTIgNC45MzMgMi4wNzggMS4yNyAxLjA5MSAyLjE4NyAyLjM0NSAyLjYzNyAzLjAyM2ExLjYyIDEuNjIgMCAwIDEgMCAxLjc5OGMtLjQ1LjY3OC0xLjM2NyAxLjkzMi0yLjYzNyAzLjAyM0MxMS42NyAxMy4wMDggOS45ODEgMTQgOCAxNGMtMS45ODEgMC0zLjY3MS0uOTkyLTQuOTMzLTIuMDc4QzEuNzk3IDEwLjgzLjg4IDkuNTc2LjQzIDguODk4YTEuNjIgMS42MiAwIDAgMSAwLTEuNzk4Yy40NS0uNjc3IDEuMzY3LTEuOTMxIDIuNjM3LTMuMDIyQzQuMzMgMi45OTIgNi4wMTkgMiA4IDJaTTEuNjc5IDcuOTMyYS4xMi4xMiAwIDAgMCAwIC4xMzZjLjQxMS42MjIgMS4yNDEgMS43NSAyLjM2NiAyLjcxN0M1LjE3NiAxMS43NTggNi41MjcgMTIuNSA4IDEyLjVjMS40NzMgMCAyLjgyNS0uNzQyIDMuOTU1LTEuNzE1IDEuMTI0LS45NjcgMS45NTQtMi4wOTYgMi4zNjYtMi43MTdhLjEyLjEyIDAgMCAwIDAtLjEzNmMtLjQxMi0uNjIxLTEuMjQyLTEuNzUtMi4zNjYtMi43MTdDMTAuODI0IDQuMjQyIDkuNDczIDMuNSA4IDMuNWMtMS40NzMgMC0yLjgyNS43NDItMy45NTUgMS43MTUtMS4xMjQuOTY3LTEuOTU0IDIuMDk2LTIuMzY2IDIuNzE3Wk04IDEwYTIgMiAwIDEgMS0uMDAxLTMuOTk5QTIgMiAwIDAgMSA4IDEwWiI+PC9wYXRoPjwvc3ZnPg==">
  </a> 
</p>

---

## Features

- Seamlessly integrates with the standard `print` function.
- Sends printed messages to a specified API endpoint.
- Retains all original `print` functionality, including custom separators, end characters, and file output.

---

## Installation

Install the package using `pip`:

```bash
pip install StreamLog
```

---

## Usage

### Enable StreamLog

To start using **StreamLog**, import and enable the custom print functionality by specifying your API endpoint:

```python
from StreamLog import enable_stream_log

# Enable StreamLog with your API endpoint
enable_stream_log(api_url="https://your-api-endpoint.com/logs")

# Use the print function as usual
print("Hello, World!")
```

### Example Output

#### Console Output:
```
Hello, World!
```

#### API Request:
**Endpoint:** `https://your-api-endpoint.com/logs`  
**Method:** `POST`
**Payload:**
```json
{
  "message": "Hello, World!"
}
```

---

## Parameters

The `enable_stream_log` function accepts the following parameter:

- `api_url` (str): The URL of the API endpoint where logs will be sent.  
  Default: `http://example.com/api/logs`

---

## Error Handling

If the API call fails (e.g., network issues, invalid endpoint), an error message is displayed in the console, and the `print` statement continues to function normally.

Example:
```
StreamLog Error: Failed to send message to API: [Error details]
```

---

## Requirements

- Python 3.6 or higher
- `requests` library

---

## Installation from Source

Clone the repository and install the package locally:

```bash
git clone https://github.com/PrathmeshSoni/StreamLog.git
cd StreamLog
pip install .
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`feature/new-feature`).
3. Commit your changes.
4. Open a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

Developed by **Prathmesh Soni**  
For more details, visit [GitHub Repo](https://github.com/PrathmeshSoni/StreamLog).


```
Let me know if you'd like any modifications!
```
