from boto3.dynamodb.types import TypeDeserializer
from decimal import Decimal

# https://github.com/openwurl/boto3-helpers/pull/18/commits/369be8efe14a5a9c4fc31c60fb0c0e8728eabfd6#diff-6f464f669a8b7322983f3f38899f22955c30a5d7239a5ecda8520b86f6243ae3R7


class CustomTypeDeserializer(TypeDeserializer):
    def __init__(self, *args, use_decimal=False, **kwargs):
        self.use_decimal = use_decimal
        super().__init__(*args, **kwargs)

    def _deserialize_n(self, value):
        if self.use_decimal:
            return super()._deserialize_n(value)

        ret = float(value)
        return int(ret) if ret.is_integer() else ret


def deserialize_dynamodb_item(item):
    deserializer = CustomTypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in item.items()}
