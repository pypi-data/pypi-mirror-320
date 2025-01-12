"""
MilvusDB connector

By default, connects to an existing collection with the _default or specified
partition or creates a new one. To drop an earlier created collection,
in the code, use:

    if utility.has_collection(<collection_name>):
        utility.drop_collection(<collection_name>)
"""

from pymilvus import CollectionSchema, MilvusClient
from pymilvus.client.types import ExtraList

from lego.db.vector_db.models import EmbedModel, MilvusDBSettings
from lego.settings import MilvusConnection


class MilvusDBConnector:
    """
    A Vector index that works with just one partition.

    If no partition is specified, it will use the default partition.
    """

    def __init__(
        self,
        connection: MilvusConnection,
        settings: MilvusDBSettings,
        embed_model: EmbedModel,
        schema: CollectionSchema | None = None,
    ):
        self.settings = settings
        self.embed_model = embed_model
        self.client = MilvusClient(**connection.model_dump())
        self.set_up_connector(settings, schema)

        self.sim_threshold_to_add = settings.sim_threshold_to_add
        self._more_similar_op = settings.more_similar_op

    def set_up_connector(
        self,
        settings: MilvusDBSettings,
        schema: CollectionSchema | None = None,
    ):
        """Set up the connector."""
        self.client.create_collection(
            collection_name=settings.collection,
            schema=schema,
        )
        self.client.create_partition(
            collection_name=settings.collection,
            partition_name=settings.partition,
        )
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            settings.embedding_field,
            **settings.index_params,
        )
        self.client.create_index(
            settings.name,
            index_params=index_params,
            sync=True,
        )
        return self.client.load_collection(settings.collection)

    def register_items(
        self,
        ids: str | int | list[str | int],
        items: dict[str, str],
    ):
        """Make an entry for adding it to a data batch."""
        ids = [ids] if isinstance(ids, (str, int)) else ids
        existing_ids = self.client.get(
            collection_name=self.settings.collection,
            output_fields=[self.settings.primary_key],
            ids=ids,
        ).values()
        self.client.insert(
            collection_name=self.settings.collection,
            data={id: items[id] for id in set(ids) - existing_ids},
        )

    def query(
        self,
        text_filter: tuple[str, str] | None = None,
        filter: str = "",
        **kwargs,
    ) -> ExtraList:
        """Query the partition."""
        expr = ""
        if text_filter:
            key, value = text_filter
            safe_text = str(value).replace("'", r"\'")
            first_part = f"{key} == '{safe_text}'"
            expr += first_part

        if text_filter and filter:
            expr += f" && {filter}"

        return self.client.query(
            collection_name=self.settings.collection,
            filter=expr,
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
            data=self.embed_model(texts),
            anns_field=self.settings.embedding_field,
            search_params=self.settings.search_params,
            limit=limit,
            filter=filter,
            **kwargs,
        )
