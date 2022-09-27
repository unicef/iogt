import json


class Chart:
    viz_type = None

    def __init__(self, dashboard_id, dataset_id, name, clean_name=None):
        self.dashboard_id = dashboard_id
        self.dataset_id = dataset_id
        self.name = name
        self.clean_name = clean_name

    def post_body(self):
        return {
            'dashboards': [self.dashboard_id],
            'datasource_id': self.dataset_id,
            'datasource_type': 'table',
            'slice_name': self.name,
            'viz_type': self.viz_type,
            'params': self.params(),
        }

    def params(self):
        raise json.dumps({})


class PieChart(Chart):
    viz_type = 'pie'

    def params(self):
        return json.dumps({
            "groupby": [self.clean_name],
            "metric": "count",
        })


class BarChart(Chart):
    viz_type = 'dist_bar'

    def params(self):
        return json.dumps({
            "groupby": [self.clean_name],
            "metrics": ["count"],
        })


class TableChart(Chart):
    viz_type = 'table'

    def params(self):
        return json.dumps({
            "groupby": [self.clean_name],
            "metrics": ["count"],
        })


class BigNumberTotalChart(Chart):
    viz_type = 'big_number_total'

    def params(self):
        return json.dumps({
            "metric": "count",
        })


class BigNumberTotalMeanChart(BigNumberTotalChart):
    def params(self):
        return json.dumps({
            "metric": {
                "expressionType": "SQL",
                "sqlExpression": f"PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY (form_data::json->>'{self.clean_name}')::DECIMAL)",
            },
        })
