import asyncio
import time
from typing import Any, Dict, List, Optional, TypeVar, AsyncGenerator, Tuple

from chainsaws.aws.dynamodb._dynamodb_config import (
    PARTITION_KEY_META_INFO,
)
from chainsaws.aws.dynamodb._dynamodb_internal import AsyncDynamoDB
from chainsaws.aws.dynamodb._dynamodb_utils import (
    decode_dict,
    encode_dict,
    find_proper_index,
    format_value,
    merge_pk_sk,
    pop_system_keys,
    split_pk_sk,
)
from chainsaws.aws.dynamodb.dynamodb_exception import (
    DynamoDBError,
    PartitionNotFoundError,
)
from chainsaws.aws.dynamodb.dynamodb_models import (
    DynamoDBAPIConfig,
    DynamoModel,
)

T = TypeVar("T", bound=DynamoModel)


class AsyncDynamoDBAPI:
    """Asynchronous DynamoDB API implementation."""

    def __init__(
        self,
        table_name: str,
        config: Optional[DynamoDBAPIConfig] = None,
    ) -> None:
        self.config = config or DynamoDBAPIConfig()
        self.table_name = table_name
        self.dynamo_db = AsyncDynamoDB(
            table_name=table_name,
            config=self.config,
        )
        self.cache: Dict[str, Any] = {}

    async def init_db_table(self) -> None:
        """Initialize DynamoDB table."""
        await self.dynamo_db.init_db_table()

    async def get_item(
        self,
        item_id: str,
        consistent_read: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Get single item by ID asynchronously."""
        pair = split_pk_sk(item_id)
        if not pair:
            raise DynamoDBError(f'Invalid item_id: "{item_id}"')

        _pk, _sk = pair
        item = await self.dynamo_db.get_item(_pk, _sk, consistent_read)

        if not item:
            return None

        item["_id"] = merge_pk_sk(item["_pk"], item["_sk"])
        return pop_system_keys(encode_dict(item))

    async def get_items(
        self,
        item_ids: List[str],
        consistent_read: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get multiple items asynchronously."""
        tasks = []
        for item_id in item_ids:
            tasks.append(self.get_item(item_id, consistent_read))

        items = await asyncio.gather(*tasks)
        return [item for item in items if item is not None]

    async def put_item(
        self,
        partition: str,
        item: T,
        can_overwrite: bool = True,
    ) -> T:
        """Put single item asynchronously."""
        if isinstance(item, DynamoModel):
            item_dict = item.to_dict()
        else:
            item_dict = item

        processed_item = self.process_item_with_partition(
            item_dict,
            partition,
        )

        await self.dynamo_db.put_item(processed_item, can_overwrite)

        if "_id" in processed_item:
            processed_item.pop("_id")

        result = encode_dict(pop_system_keys(processed_item))

        if isinstance(item, DynamoModel):
            return type(item).from_dict(result)
        return result

    async def put_items(
        self,
        partition: str,
        items: List[T],
        can_overwrite: bool = True,
    ) -> List[T]:
        """Put multiple items asynchronously."""
        if not items:
            return []

        tasks = []
        for item in items:
            tasks.append(self.put_item(partition, item, can_overwrite))

        return await asyncio.gather(*tasks)

    async def update_item(
        self,
        partition: str,
        item_id: str,
        item: T,
        consistent_read: bool = False,
    ) -> T:
        """Update single item asynchronously."""
        is_model = isinstance(item, DynamoModel)
        model_class = item.__class__ if is_model else None
        item_dict = item.to_dict() if is_model else item

        target_item = await self.get_item(item_id, consistent_read)
        if not target_item:
            raise DynamoDBError(f"No such item: {item_id}")

        if target_item["_ptn"] != partition:
            raise DynamoDBError(f'Partition not match: {
                                partition} != {target_item["_ptn"]}')

        origin_pk, origin_sk = split_pk_sk(item_id)
        key_fields = self._check_keys_cannot_update(partition)

        item_to_insert = item_dict.copy()
        for key_field in key_fields:
            if key_field in item_to_insert:
                item_to_insert.pop(key_field)

        item_to_insert = self.process_item_with_partition(
            item_to_insert,
            partition,
            for_creation=False,
        )

        for key in ["_pk", "_sk", "_id", "_crt", "_ptn"]:
            item_to_insert.pop(key, None)

        response = await self.dynamo_db.update_item(origin_pk, origin_sk, item_to_insert)
        attributes = response.get("Attributes", {})

        if attributes:
            attributes["_id"] = item_id

        result = pop_system_keys(encode_dict(attributes))

        if is_model and model_class:
            return model_class.from_dict(result)
        return result

    async def update_items(
        self,
        partition: str,
        item_updates: Dict[str, T],
    ) -> List[T]:
        """Update multiple items asynchronously."""
        if not item_updates:
            return []

        tasks = []
        for item_id, item in item_updates.items():
            tasks.append(self.update_item(partition, item_id, item))

        return await asyncio.gather(*tasks)

    async def delete_item(
        self,
        item_id: str,
    ) -> Dict[str, Any]:
        """Delete single item asynchronously."""
        pk, sk = split_pk_sk(item_id)
        if not pk or not sk:
            raise DynamoDBError(f"Invalid item ID: {item_id}")

        response = await self.dynamo_db.delete_item(pk, sk)
        return encode_dict(response.get("Attributes", {}))

    async def delete_items(
        self,
        item_ids: List[str],
    ) -> None:
        """Delete multiple items asynchronously."""
        pk_sk_pairs = []
        invalid_ids = []

        for item_id in item_ids:
            pk, sk = split_pk_sk(item_id)
            if not pk or not sk:
                invalid_ids.append(item_id)
            else:
                pk_sk_pairs.append((pk, sk))

        if invalid_ids:
            raise DynamoDBError(
                "Invalid item IDs found:\n" +
                "\n".join(f"- {item_id}" for item_id in invalid_ids)
            )

        await self.dynamo_db.batch_delete(pk_sk_pairs)

    async def query_items(
        self,
        partition: str,
        pk_field: Optional[str] = None,
        sk_field: Optional[str] = None,
        pk_value: Optional[Any] = None,
        sk_condition: Optional[str] = None,
        sk_value: Optional[Any] = None,
        sk_second_value: Optional[Any] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        start_key: Optional[Dict[str, Any]] = None,
        limit: int = 1000,
        reverse: bool = False,
        consistent_read: bool = False,
        recursive_filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Query items asynchronously."""
        if not pk_field or not pk_value:
            pk_field, pk_value = "_ptn", partition

        if sk_value is not None and sk_field is None:
            raise DynamoDBError(
                "sk_field is required when sk_value is provided")

        if sk_value is not None and sk_condition is None:
            raise DynamoDBError(
                "sk_condition is required when sk_value is provided")

        if sk_second_value is not None and sk_value is None:
            raise DynamoDBError(
                "sk_value is required when sk_second_value is provided")

        partition_obj = await self.get_partition(partition)
        if not partition_obj:
            raise PartitionNotFoundError(partition)

        filters = filters or []
        recursive_filters = recursive_filters or {}

        index_name, pk_name, sk_name = find_proper_index(
            partition_object=partition_obj,
            pk_field=pk_field,
            sk_field=sk_field,
        )

        response = await self.dynamo_db.query_items(
            partition_key_name=pk_name,
            partition_key_value=pk_value,
            sort_condition=sk_condition,
            sort_key_name=sk_name,
            sort_key_value=sk_value,
            sort_key_second_value=sk_second_value,
            filters=filters,
            start_key=start_key,
            reverse=reverse,
            limit=limit,
            consistent_read=consistent_read,
            index_name=index_name,
            recursive_filters=recursive_filters,
        )

        items = response.get("Items", [])
        last_key = response.get("LastEvaluatedKey")

        for item in items:
            if item:
                item["_id"] = merge_pk_sk(item["_pk"], item["_sk"])

        return [pop_system_keys(encode_dict(item)) for item in items], last_key

    async def scan_table(
        self,
        filters: Optional[List[Dict[str, Any]]] = None,
        recursive_filters: Optional[Dict[str, Any]] = None,
        start_key: Optional[Dict[str, Any]] = None,
        limit: int = 1000,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Scan table asynchronously."""
        while True:
            items, last_key = await self.dynamo_db.scan_table(
                filters=filters,
                recursive_filters=recursive_filters,
                start_key=start_key,
                limit=limit,
            )

            for item in items:
                if "_id" not in item and "_pk" in item and "_sk" in item:
                    item["_id"] = merge_pk_sk(item["_pk"], item["_sk"])
                yield pop_system_keys(encode_dict(item))

            if not last_key:
                break

            start_key = last_key

    async def get_partition(
        self,
        partition: str,
        use_cache: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Get partition configuration asynchronously."""
        partitions = await self.get_partitions(use_cache=use_cache)
        for pt in partitions:
            if pt["_partition_name"] == partition:
                return pt
        return None

    async def get_partitions(
        self,
        use_cache: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get all partitions asynchronously."""
        cache_key = "partitions" + str(int(time.time() // 100))
        if use_cache and cache_key in self.cache:
            return [it.copy() for it in self.cache[cache_key]]

        items = []
        start_key = None

        while True:
            response = await self.dynamo_db.query_items(
                partition_key_name="_pk",
                partition_key_value=PARTITION_KEY_META_INFO,
                sort_condition="gte",
                sort_key_name="_sk",
                sort_key_value=" ",
                limit=1000,
                consistent_read=True,
                start_key=start_key,
            )

            _items = response.get("Items", [])
            start_key = response.get("LastEvaluatedKey")
            items.extend(_items)

            if not start_key:
                break

        for item in items:
            item.pop("_pk")
            item.pop("_sk")

        items = [encode_dict(item) for item in items]
        items = [it.copy() for it in items]
        self.cache[cache_key] = items
        return items

    def _check_keys_cannot_update(self, partition_name: str) -> set[str]:
        """Return list of fields that cannot be updated."""
        keys_cannot_update = set()
        partition = self.get_partition(partition_name)

        if not partition:
            raise PartitionNotFoundError(partition_name)

        pk_field = partition["_pk_field"]
        sk_field = partition["_sk_field"]
        uk_fields = partition["_uk_fields"]

        keys_cannot_update.add(pk_field)
        keys_cannot_update.add(sk_field)

        if uk_fields:
            for uk_field in uk_fields:
                keys_cannot_update.add(uk_field)

        return keys_cannot_update

    def process_item_with_partition(
        self,
        item: Dict[str, Any],
        partition: str,
        for_creation: bool = True,
    ) -> Dict[str, Any]:
        """Process item according to partition configuration."""
        partitions = self.get_partitions(use_cache=True)
        partitions_by_name = {
            p.get("_partition_name", None): p for p in partitions
        }
        partition_obj = partitions_by_name.get(partition)
        if not partition_obj:
            raise DynamoDBError(f"No such partition: {partition}")

        pk_field = partition_obj["_pk_field"]
        sk_field = partition_obj["_sk_field"]
        uk_fields = partition_obj.get("_uk_fields", [])

        indexes = partition_obj.get("indexes", [])
        if for_creation:
            item["_crt"] = int(time.time())
        item["_ptn"] = partition
        item = decode_dict(item)

        pk_value = ""
        if for_creation:
            if pk_field not in item:
                raise DynamoDBError(f'pk_field:["{pk_field}"] should in item')
            if sk_field and sk_field not in item:
                raise DynamoDBError(f'sk_field:["{sk_field}"] should in item')
            pk_value = item[pk_field]

        sk_value = item[sk_field] if sk_field and sk_field in item else ""
        sk_value = format_value(sk_value)

        if sk_field is None:
            sk_field = ""

        if pk_field == "_ptn":
            pk = f"{partition}"
        else:
            pk = f"{partition}#{pk_field}#{pk_value}"
        sk = f"{sk_field}#{sk_value}"

        if uk_fields:
            for uk_field in uk_fields:
                uk_value = item.get(uk_field, "")
                uk_value = format_value(uk_value)
                sk += f"#{uk_field}#{uk_value}"

        item["_pk"] = pk
        item["_sk"] = sk

        for index in indexes:
            pk_name = index["pk_name"]
            sk_name = index["sk_name"]
            pk_field = index["_pk_field"]
            sk_field = index["_sk_field"]
            has_pk = pk_field in item
            has_sk = sk_field in item

            pk_value = item.get(pk_field, None)
            sk_value = item.get(sk_field, "") if sk_field else ""
            sk_value = format_value(sk_value)

            if sk_field is None:
                sk_field = ""

            if pk_field == "_ptn":
                _pk_v = f"{partition}"
            else:
                _pk_v = f"{partition}#{pk_field}#{pk_value}"
            _sk_v = f"{sk_field}#{sk_value}"

            if for_creation:
                item[pk_name] = _pk_v
                item[sk_name] = _sk_v
            else:
                if has_pk:
                    item[pk_name] = _pk_v
                if has_sk:
                    item[sk_name] = _sk_v

        item["_id"] = merge_pk_sk(partition_key=pk, sort_key=sk)
        return item
