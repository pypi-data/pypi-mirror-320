from abc import ABC


class Context(ABC):
    def get_context(self) -> dict:
        pass


class DictContext(dict, Context):
    def get_context(self) -> dict:
        return self


class TransactionContext(Context):
    def __init__(self, transaction_id: str):
        self.transaction_id = transaction_id

    def get_context(self):
        return {
            'transaction_id': self.transaction_id,
        }

    @staticmethod
    def contains_transaction_context(context: Context) -> bool:
        return 'transaction_id' in context.get_context()
