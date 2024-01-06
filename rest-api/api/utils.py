from api.constants import USER_PROFILE_RETURN_SCHEMA

# decorator code
def class_route(self, rule, endpoint, **options):
    """
    This decorator allow add routed to class view.
    :param self: any flask object that have `add_url_rule` method.
    :param rule: flask url rule.
    :param endpoint: endpoint name
    """

    def decorator(cls):
        self.add_url_rule(rule, view_func=cls.as_view(endpoint), **options)
        return cls

    return decorator

def generate_paginated_dict(api_results):
    results = []

    if type(api_results) == list:
        results = api_results
    else:
        results.append(api_results)
    
    return {
        "count":len(results),
        "next":None,
        "previous":None,
        "results": results 
    }