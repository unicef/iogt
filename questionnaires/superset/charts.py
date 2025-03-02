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
        return json.dumps({})


class PieChart(Chart):
    viz_type = 'pie'

    def params(self):
        return json.dumps({
            "groupby": [self.name],
            "metric": "response_count",
            "show_legend": False,
            "label_type": "key_percent",
        })


class BarChart(Chart):
    viz_type = 'dist_bar'

    def __init__(self, dashboard_id, dataset_id, name, x_axis=None, y_axis=None, series=None, clean_name=None):
        super().__init__(dashboard_id, dataset_id, name, clean_name)
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.series = series

    def params(self):
        if self.x_axis and self.y_axis and self.series:
            # New implementation if specific axes are provided
            return json.dumps({
                "groupby": [self.x_axis, self.y_axis],
                "metrics": [self.series],
                "show_legend": True,
                "y_axis_label": self.y_axis,
                "x_axis_label": self.x_axis,
            })
        else:
            # Existing implementation
            return json.dumps({
                "groupby": [self.name],
                "metrics": ["response_count"],
                "show_legend": False,
                "y_axis_label": "Responses",
            })


class TableChart(Chart):
    viz_type = 'table'

    def params(self):
        return json.dumps({
            "adhoc_filters": [
                {
                    "clause": "WHERE",
                    "expressionType": "SQL",
                    "sqlExpression": f"((form_data::json)->'{self.clean_name}')::text <> '\"\"'",
                }
            ],
            "groupby": [self.name],
            "metrics": ["response_count"],
        })


class BigNumberTotalChart(Chart):
    viz_type = 'big_number_total'

    def params(self):
        return json.dumps({
            "metric": "response_count",
            "subheader": "Responses"
        })


class BigNumberTotalOpenEndedQuestionChart(BigNumberTotalChart):
    viz_type = 'big_number_total'

    def params(self):
        return json.dumps({
            "adhoc_filters": [
                {
                    "clause": "WHERE",
                    "expressionType": "SQL",
                    "sqlExpression": f"((form_data::json)->'{self.clean_name}')::text <> '\"\"'",
                }
            ],
            "metric": "response_count",
            "subheader": "Responses"
        })


class BigNumberTotalMeanChart(BigNumberTotalChart):
    def params(self):
        return json.dumps({
            "metric": {
                "expressionType": "SQL",
                "sqlExpression": f"AVG((form_data::json->>'{self.clean_name}')::DECIMAL)",
            },
            "subheader": "Mean of responses",
        })
