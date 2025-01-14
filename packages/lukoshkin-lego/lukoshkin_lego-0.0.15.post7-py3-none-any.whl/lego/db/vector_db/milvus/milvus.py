"""
MilvusDB connector

By default, connects to an existing collection with the _default or specified
partition or creates a new one. To drop an earlier created collection,
in the code, use:

    if utility.has_collection(<collection_name>):
        utility.drop_collection(<collection_name>)
"""

from typing import Any

from pymilvus import CollectionSchema, MilvusClient
from pymilvus.client.types import ExtraList

from lego.db.vector_db.models import EmbedModel, MilvusDBSettings
from lego.lego_types import OneOrMany
from lego.settings import MilvusConnection


class MilvusDBConnector:
    """
    A Vector index that works with just one partition.

    If no partition is specified, it will use the default partition.
    """

    def __init__(
        self,
        schema: CollectionSchema,
        settings: MilvusDBSettings,
        connection: MilvusConnection,
        embed_model: EmbedModel,
    ):
        self._sanity_checks(settings, schema, embed_model)

        self.schema = schema
        self.settings = settings
        self.client = MilvusClient(**connection.model_dump())
        self.embed_model = embed_model

        self.sim_threshold_to_add = settings.sim_threshold_to_add
        self._more_similar_op = settings.more_similar_op

    def ensure_built(self) -> None:
        """Build the collection, partition, and index."""
        if not self.client.has_collection(self.settings.collection):
            self.client.create_collection(
                collection_name=self.settings.collection,
                schema=self.schema,
            )
        if not self.client.has_partition(
            collection_name=self.settings.collection,
            partition_name=self.settings.partition,
        ):
            self.client.create_partition(
                collection_name=self.settings.collection,
                partition_name=self.settings.partition,
            )
        if self.settings.embedding_field not in self.client.list_indexes(
            self.settings.collection, self.settings.embedding_field
        ):
            index_params = self.client.prepare_index_params()
            index_params.add_index(
                self.settings.embedding_field,
                **self.settings.index_params,
            )
            self.client.create_index(
                self.settings.collection,
                index_params=index_params,
                sync=True,
            )
        return self.client.load_partitions(
            self.settings.collection, self.settings.partition
        )

    def register_one(self, item: dict[str, Any]) -> bool:
        """Add an item to the collection."""
        if not self.get(
            ids=item[self.settings.primary_key],
            output_fields=[self.settings.primary_key],
        ):
            self.client.insert(
                collection_name=self.settings.collection,
                partition_name=self.settings.partition,
                data=item,
            )
            return True
        return False

    def register_many(self, items: list[dict[str, Any]]) -> int:
        """Add multiple items to the collection."""
        existing_ids = [
            d[self.settings.primary_key]
            for d in self.get(
                [item[self.settings.primary_key] for item in items],
                output_fields=[self.settings.primary_key],
            )
        ]
        data = [
            item
            for item in items
            if item[self.settings.primary_key] not in existing_ids
        ]
        self.client.insert(
            collection_name=self.settings.collection,
            partition_name=self.settings.partition,
            data=data,
        )
        return len(data)

    def get(self, ids: OneOrMany[str | int], **kwargs) -> ExtraList:
        """Get items by their IDs."""
        return self.client.get(
            collection_name=self.settings.collection,
            partition_names=[self.settings.partition],
            ids=ids,
            **kwargs,
        )

    def query(
        self,
        text_filter: tuple[str, str] | None = None,
        filter: str = "",
        **kwargs,
    ) -> ExtraList:
        """Query the partition."""
        prefix = ""
        if text_filter:
            key, value = text_filter
            safe_text = str(value).replace("'", r"\'")
            prefix = f"{key} == '{safe_text}'"

        if prefix:
            filter = f"{prefix} && {filter}" if filter else prefix

        return self.client.query(
            collection_name=self.settings.collection,
            partition_names=[self.settings.partition],
            filter=filter,
            **kwargs,
        )

    def search(
        self,
        texts: list[str],
        filter: str = "",
        limit: int = 10,
        **kwargs,
    ) -> ExtraList:
        """Search for similar items in the collection."""
        if not texts:
            return []

        if "" in texts:
            raise ValueError("Empty query text is not allowed.")

        return self.client.search(
            collection_name=self.settings.collection,
            partition_names=[self.settings.partition],
            data=self.embed_model(texts),
            filter=filter,
            limit=limit,
            anns_field=self.settings.embedding_field,
            search_params=kwargs.pop("search_params", {})
            or self.settings.search_params,
            **kwargs,
        )

    def count(self) -> int:
        """Count the number of items in the collection."""
        return self.client.query(
            collection_name=self.settings.collection,
            output_fields=["count(*)"],
        )[0]["count(*)"]

    def drop_collection(self, **kwargs) -> None:
        """Drop the collection."""
        self.client.release_collection(self.settings.collection, **kwargs)
        self.client.drop_collection(self.settings.collection)

    def drop_partition(self, **kwargs) -> None:
        """Drop the partition."""
        self.client.release_partitions(
            self.settings.collection,
            self.settings.partition,
            **kwargs,
        )
        self.client.drop_partition(
            self.settings.collection,
            self.settings.partition,
        )

    def close(self) -> None:
        """Close the connection."""
        self.client.close()

    @staticmethod
    def _sanity_checks(
        settings: MilvusDBSettings,
        schema: CollectionSchema,
        embed_model: EmbedModel,
    ) -> None:
        """Perform sanity checks on the settings and schema."""
        schema_dict = {f.name: f for f in schema.fields}
        if settings.embedding_field not in schema_dict:
            raise ValueError(
                f"Embedding field '{settings.embedding_field=}'"
                " not found in the schema."
            )
        if settings.primary_key not in {f.name for f in schema.fields}:
            raise ValueError(
                f"Primary key '{settings.primary_key=}'"
                " not found in the schema."
            )
        if schema_dict[settings.embedding_field].dim != embed_model.embed_dim:
            raise ValueError(
                f"Embedding field '{settings.embedding_field=}' dimension"
                f" mismatch: {schema_dict[settings.embedding_field].dim}"
                f" != {embed_model.embed_dim}."
            )
