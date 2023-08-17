# LenzPy

**LenzPy** is a Python wrapper designed to facilitate interaction with the [Lenz](https://getle.nz) report API. **Lenz** is a dead-simple platform for collecting, analyzing, and visualizing data from your software.

# Usage

Before using LenzPy, ensure that you have an API key from Lenz. You can provide the API key directly in function calls or store it as an environment variable named LENZ_API_KEY.

```sh
export LENZ_API_KEY=abcdef0123
```

## The @instrument Decorator

The @instrument decorator is a powerful feature of LenzPy that enables you to seamlessly integrate reporting into your functions. It automates the process of submitting reports to Lenz while allowing you to customize the reporting behavior.

A powerful use-case is to decorate the handler function for your web API, to collect data about requests & responses.

```python
from LenzPy import instrument 

@instrument(report_name="example_fnc", flatten_args=True, flatten_res=True, mock=False)
def example_fnc(input, other_inputs, default_none=None, **kwargs):
    # Your function logic here. Example:
    status_codes = {
        200: "OK",
        201: "Created",
        204: "No Content",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error"
    }
    
    code = random.choice(list(status_codes.keys()))
    message = status_codes[code]
    
    return code, message
```

```
report_name (str): The name of the report or event.
api_key (str, optional): The API key for authentication. If not provided, it's fetched from the environment variable.
flatten_args (bool, optional): Whether to flatten function arguments before reporting.
included_args (list or None, optional): List of keys to be included in the reported arguments. If not provided, no filtering is performed.
flatten_res (bool, optional): Whether to flatten the return value before reporting.
included_res (list or None, optional): List of keys to be included in the reported return value. If not provided, no filtering is performed.
mock (bool, optional): Whether to print the prepared report without actually submitting it.
```


## Reporting Directly

If you prefer more control, you can submit reports directly using the submit_report function.

```python

from LenzPy import submit_report

# ...
data = {"userId": 17, "latency": 5, "domain": "foo.bar", "path": "/register"}
submit_report(event_name="user_register", body=data)
```

```
event_name (str): The name of the event or report.
body (dict): The body of the report containing relevant data.
api_key (str, optional): The API key for authentication. If not provided, it's fetched from the environment variable.
```