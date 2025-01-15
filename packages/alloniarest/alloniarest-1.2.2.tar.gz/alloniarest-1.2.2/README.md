# Public Project AllOnIARest

Implements several client objects to access easily AllOnIA's public APIs
(provided you have a valid token of course).

```python
from alloniarest import Client

url = ...
token_id = ...
token_secret = ...

client = Client(
    url,
    user_token={
        "id": token_id, "token": token_secret
    },
    trace=False
)
response = client.request(
    "GET",
    "/some/route?var=value"
)
```

## Available APIs

You can manualy connect to any AllOnIA API using the example above, but some
functions are readily available through extra requirements, that you can install
like this:

```bash
pip install alloniarest[extra]
```

Here is the list of available extras:

* **external_api_keys**: provides the method
  `get_external_api_key_value` that returns an external API key's
  secret based on its name:

```python
from alloniarest.external_api_keys import get_external_api_key_value

secret = get_external_api_key_value("key_name")
```
That will suppose you have set the `USER_TOKEN_ID`, `USER_TOKEN_SECRET`,
`PROJECTS_API_INTERNAL_URL` and `TRACK_ID` environment variables.