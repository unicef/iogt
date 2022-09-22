import json


class Chart:
    def __init__(self, dashboard_id, dataset_id, name, clean_name=None):
        self.dashboard_id = dashboard_id
        self.dataset_id = dataset_id
        self.name = name
        self.clean_name = clean_name

    @property
    def post_body(self):
        return {
            'dashboards': [self.dashboard_id],
            'datasource_id': self.dataset_id,
            'datasource_type': 'table',
        }


class TotalSubmissionsChart(Chart):
    def __init__(self, dashboard_id, dataset_id, name, clean_name=None):
        super().__init__(dashboard_id, dataset_id, name, clean_name)

    @property
    def post_body(self):
        body = super().post_body
        body.update({
            'slice_name': self.name,
            'viz_type': 'big_number_total',
            'params': self.params,
        })
        return body

    @property
    def params(self):
        return json.dumps({
            "metric": "count",
        })



class CheckboxChart(Chart):
    def __init__(self, dashboard_id, dataset_id, name, clean_name):
        super().__init__(dashboard_id, dataset_id, name, clean_name)

    @property
    def post_body(self):
        body = super().post_body
        body.update({
            'slice_name': self.name,
            'viz_type': 'dist_bar',
            'params': self.params,
        })
        return body

    @property
    def params(self):
        return json.dumps({
            "groupby": [{
                "label": "Choice",
                "sqlExpression": f"json_array_elements(form_data::json->'{self.clean_name}')::TEXT"
            }],
            "metrics": ["count"],
        })


class CheckboxesChart(Chart):
    def __init__(self, dashboard_id, dataset_id, name, clean_name):
        super().__init__(dashboard_id, dataset_id, name, clean_name)

    @property
    def post_body(self):
        body = super().post_body
        body.update({
            'slice_name': self.name,
            'viz_type': 'dist_bar',
            'params': self.params,
        })
        return body

    @property
    def params(self):
        return json.dumps({
            "groupby": [{
                "label": "Choice",
                "sqlExpression": f"json_array_elements(form_data::json->'{self.clean_name}')::TEXT"
            }],
            "metrics": ["count"],
        })


class DropdownChart(Chart):
    def __init__(self, dashboard_id, dataset_id, name, clean_name):
        super().__init__(dashboard_id, dataset_id, name, clean_name)

    @property
    def post_body(self):
        body = super().post_body
        body.update({
            'slice_name': self.name,
            'viz_type': 'dist_bar',
            'params': self.params,
        })
        return body

    @property
    def params(self):
        return json.dumps({
            "groupby": [{
                "label": "Choice",
                "sqlExpression": f"form_data::json->>'{self.clean_name}'::TEXT"
            }],
            "metrics": ["count"],
        })


class RadioChart(Chart):
    def __init__(self, dashboard_id, dataset_id, name, clean_name):
        super().__init__(dashboard_id, dataset_id, name, clean_name)

    @property
    def post_body(self):
        body = super().post_body
        body.update({
            'slice_name': self.name,
            'viz_type': 'dist_bar',
            'params': self.params,
        })
        return body

    @property
    def params(self):
        return json.dumps({
            "groupby": [{
                "label": "Choice",
                "sqlExpression": f"form_data::json->>'{self.clean_name}'::TEXT"
            }],
            "metrics": ["count"],
        })


class NumberChart(Chart):
    def __init__(self, dashboard_id, dataset_id, name, clean_name):
        super().__init__(dashboard_id, dataset_id, name, clean_name)

    @property
    def post_body(self):
        body = super().post_body
        body.update({
            'slice_name': self.name,
            'viz_type': 'big_number_total',
            'params': self.params,
        })
        return body

    @property
    def params(self):
        return json.dumps({
            "metric": {
                "expressionType": "SQL",
                "sqlExpression": f"PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY (form_data::json->>'{self.clean_name}')::DECIMAL)",
            },
        })


class PositiveNumberChart(Chart):
    def __init__(self, dashboard_id, dataset_id, name, clean_name):
        super().__init__(dashboard_id, dataset_id, name, clean_name)

    @property
    def post_body(self):
        body = super().post_body
        body.update({
            'slice_name': self.name,
            'viz_type': 'big_number_total',
            'params': self.params,
        })
        return body

    @property
    def params(self):
        return json.dumps({
            "metric": {
                "expressionType": "SQL",
                "sqlExpression": f"PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY (form_data::json->>'{self.clean_name}')::DECIMAL)",
            },
        })


class EmailChart(Chart):
    def __init__(self, dashboard_id, dataset_id, name, clean_name):
        super().__init__(dashboard_id, dataset_id, name, clean_name)

    @property
    def post_body(self):
        body = super().post_body
        body.update({
            'slice_name': self.name,
            'viz_type': 'table',
            'params': self.params,
        })
        return body

    @property
    def params(self):
        return json.dumps({
            "adhoc_filters": [{
                "clause": "WHERE",
                "expressionType": "SQL",
                "sqlExpression": f"(form_data::json->>'{self.clean_name}')::TEXT is not null",
            }],
            "groupby": [{
                "label": "Choice",
                "sqlExpression": f"(form_data::json->>'{self.clean_name}')::TEXT"
            }],
            "metrics": ["count"],
            "query_mode": "aggregate",
        })


class URLChart(Chart):
    def __init__(self, dashboard_id, dataset_id, name, clean_name):
        super().__init__(dashboard_id, dataset_id, name, clean_name)

    @property
    def post_body(self):
        body = super().post_body
        body.update({
            'slice_name': self.name,
            'viz_type': 'table',
            'params': self.params,
        })
        return body

    @property
    def params(self):
        return json.dumps({
            "adhoc_filters": [{
                "clause": "WHERE",
                "expressionType": "SQL",
                "sqlExpression": f"(form_data::json->>'{self.clean_name}')::TEXT is not null",
            }],
            "groupby": [{
                "label": "Choice",
                "sqlExpression": f"(form_data::json->>'{self.clean_name}')::TEXT"
            }],
            "metrics": ["count"],
            "query_mode": "aggregate",
        })


class SingleLineText(Chart):
    def __init__(self, dashboard_id, dataset_id, name, clean_name):
        super().__init__(dashboard_id, dataset_id, name, clean_name)

    @property
    def post_body(self):
        body = super().post_body
        body.update({
            'slice_name': self.name,
            'viz_type': 'big_number_total',
            'params': self.params,
        })
        return body

    @property
    def params(self):
        return json.dumps({
            "adhoc_filters": [{
                "clause": "WHERE",
                "expressionType": "SQL",
                "sqlExpression": f"form_data::json->>'{self.clean_name}' is not null ",
            }],
            "metric": "count",
        })


class MultiLineText(Chart):
    def __init__(self, dashboard_id, dataset_id, name, clean_name):
        super().__init__(dashboard_id, dataset_id, name, clean_name)

    @property
    def post_body(self):
        body = super().post_body
        body.update({
            'slice_name': self.name,
            'viz_type': 'big_number_total',
            'params': self.params,
        })
        return body

    @property
    def params(self):
        return json.dumps({
            "adhoc_filters": [{
                "clause": "WHERE",
                "expressionType": "SQL",
                "sqlExpression": f"form_data::json->>'{self.clean_name}' is not null",
            }],
            "metric": "count",
        })


# class Date(Chart):
#     @property
#     def body(self):
#         return {}
#
#
# class Datetime(Chart):
#     @property
#     def body(self):
#         return {}
#
#

CHART_TYPE_MAP = {
    'checkbox': CheckboxChart,
    'checkboxes': CheckboxesChart,
    'dropdown': DropdownChart,
    'radio': RadioChart,
    'number': NumberChart,
    'positivenumber': PositiveNumberChart,
    'singleline': MultiLineText,
    'multiline': MultiLineText,
    'email': EmailChart,
    'url': URLChart,
}
