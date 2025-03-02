from questionnaires.superset import ALLOWED_COLUMNS, ALLOWED_COLUMNS_REG_SURVEY


class Dataset:
    def __init__(self, database_id, owner_id, table_name, dataset_name, page_id):
        self.database_id = database_id
        self.owner_id = owner_id
        self.table_name = table_name
        self.dataset_name = dataset_name
        self.page_id = page_id

    def post_body(self):
        return {
            'database': self.database_id,
            'table_name': self.table_name,
            'owners': [
                self.owner_id,
            ],
        }

    def put_body(self, columns, metrics):
        if self.table_name != "registration_survey":
            sql = f"SELECT {', '.join(ALLOWED_COLUMNS)} FROM {self.table_name}"
        else:
            sql = f"SELECT {', '.join(ALLOWED_COLUMNS_REG_SURVEY)} FROM {self.table_name}"

        # Only apply page_id filter if table_name is not 'registration_survey'
        if self.table_name != "registration_survey":
            sql += f" WHERE page_id = {self.page_id}"

        return {
            'sql': sql,
            'table_name': self.dataset_name,
            'columns': columns,
            'metrics': metrics,
            'owners': [
                self.owner_id,
            ],
        }
