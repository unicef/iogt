class Dataset:
    def __init__(self, database_id, table_name, dataset_name, page_id):
        self.database_id = database_id
        self.table_name = table_name
        self.dataset_name = dataset_name
        self.page_id = page_id

    @property
    def post_body(self):
        return {
            'database': self.database_id,
            'table_name': self.table_name,
        }

    @property
    def put_body(self):
        sql = f"SELECT * " \
              f"FROM {self.table_name} " \
              f"WHERE page_id = {self.page_id}"
        return {
            'sql': sql,
            'table_name': self.dataset_name,
        }
