import json

from ._contexts import Context, DictContext


class ContextHttpHeaderConverter:
    @staticmethod
    def try_convert_from_raw_headers(headers: dict) -> Context | None:
        if 'edgegap-context-logger-v1' not in headers:
            return None

        context = DictContext()

        try:
            loaded_context = json.loads(headers['edgegap-context-logger-v1'])
        except json.JSONDecodeError:
            return None

        context.update(loaded_context)

        return context

    @staticmethod
    def convert_to_raw_headers(context: Context) -> dict:
        return {
            'edgegap-context-logger-v1': json.dumps(context.get_context()),
        }
