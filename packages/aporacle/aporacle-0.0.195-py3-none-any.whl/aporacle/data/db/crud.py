from komoutils.db.mongodb_reader_writer import MongoDBReaderWriter


class Crud(MongoDBReaderWriter):
    def __init__(self, uri: str, db_name: str):
        super().__init__(uri, db_name)

    def write_to_database(self, collection=None, data=None):
        assert collection is not None, "Collection cannot be None"
        assert data is not None, "Data cannot be None"
        assert len(data) > 0, "Data cannot be empty."
        return self.write(collection=collection, data=data)

    def read_from_data(self, collection=None, filters=None, omit=None, limit: int = 1000000, sort_key='_id',
                       sort_order=-1):
        assert collection is not None, "Collection cannot be None"
        return self.read(collection=collection, filters=filters, omit=omit, limit=limit, sort_key=sort_key,
                         sort_order=sort_order)

    def drop_collection(self, collection):
        assert collection is not None, "Collection cannot be None"
        self.drop_collection(collection=collection)

    def delete(self, collection=None, filters=None):
        """Remove records from database based on filters
        
        Args:
            collection (str): Collection name
            filters (dict or list): Filter criteria for deletion. If list, performs bulk deletion
        
        Returns:
            dict: Deletion result with count of deleted documents
        """
        assert collection is not None, "Collection cannot be None"
        assert filters is not None, "Filters cannot be None"

        if isinstance(filters, list):
            # Bulk deletion
            result = self.db[collection].delete_many({"$or": filters})
        else:
            # Single filter deletion
            result = self.db[collection].delete_many(filters)
        
        return {"deleted_count": result.deleted_count}


