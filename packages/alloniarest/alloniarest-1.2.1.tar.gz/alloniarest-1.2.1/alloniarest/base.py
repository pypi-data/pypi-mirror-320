class Base:
    def __init__(self, client):
        self._client = client

    def handle_api_call(
        self,
        method: str,
        path: str,
        params: dict,
        fields_to_get: dict,
        depaginate: bool,
    ) -> dict:
        """Depaginates a paginated API call response depending on the params.

        Args:
            method: The request method (get/post/patch/delete).
            path: The request path.
            params: request params. The route must accept "page_number", even if
                it is not specified in those params.
            fields_to_get: the fields to get from the response.
                The dict keys are field names (for example, "count", "objects",
                etc). The values are also dict, with two keys: 'default', the
                value being the default values for this field, and
                "aggregator", the values being an aggregator
                function (float.__add__, list.__add__, or any function taking
                two arguments of the type of the field and returning a third
                one).
            depaginate: If True, will depaginate the call
        Returns:
            The returned dict will contain the aggregated values found for the
            specified fields_to_get if depaginate is True, else simply
            the 'page_size' first values. "pagination" will not be present.
        """

        def call(current_fields=None):
            resp_ = self._client.request(method, path, params=params)
            resp_.raise_for_status()
            resp_ = resp_.json()
            if not current_fields:
                current_fields = {
                    field_name: resp_.get(field_name, field["default"])
                    for field_name, field in fields_to_get.items()
                }
            else:
                for field_name, field in fields_to_get.items():
                    current_fields[field_name] = field["aggregator"](
                        current_fields[field_name],
                        resp_.get(field_name, field["default"]),
                    )
            return (
                resp_.get("pagination", {}).get("next_page"),
                current_fields,
            )

        if depaginate:
            params["page_size"] = 1000
            params["page_number"] = 1
        else:
            params["page_number"] = params.get("page_number", 1)

        next_page, fields = call()
        if depaginate:
            while next_page:
                params["page_number"] = next_page
                next_page, fields = call(fields)
        return fields
