# swagger_client.TablesApi

All URIs are relative to *https://api.airtable.com/v0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**airtable_tables_create**](TablesApi.md#airtable_tables_create) | **POST** /meta/bases/{baseId}/tables | Create table
[**airtable_tables_update**](TablesApi.md#airtable_tables_update) | **PATCH** /meta/bases/{baseId}/tables/{tableIdOrName} | Update table

# **airtable_tables_create**
> TableModel airtable_tables_create(body, base_id)

Create table

Creates a new table and returns the schema for the newly created table.  Refer to field types for supported field types, the write format for field options, and other specifics for certain field types. Supported field types have a write format shown.  At least one field must be specified. The first field in the fields array will be used as the table's primary field and must be a supported primary field type. Fields must have case-insensitive unique names within the table.  A default grid view will be created with all fields visible. 

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKeyAuth
configuration = swagger_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure OAuth2 access token for authorization: Oauth2
configuration = swagger_client.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.TablesApi(swagger_client.ApiClient(configuration))
body = swagger_client.BaseIdTablesBody() # BaseIdTablesBody | 
base_id = 'base_id_example' # str | 

try:
    # Create table
    api_response = api_instance.airtable_tables_create(body, base_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TablesApi->airtable_tables_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**BaseIdTablesBody**](BaseIdTablesBody.md)|  | 
 **base_id** | **str**|  | 

### Return type

[**TableModel**](TableModel.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_tables_update**
> TableModel airtable_tables_update(body, base_id, table_id_or_name)

Update table

Updates the name and/or description of a table. At least one of name or description must be specified.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKeyAuth
configuration = swagger_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure OAuth2 access token for authorization: Oauth2
configuration = swagger_client.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# create an instance of the API class
api_instance = swagger_client.TablesApi(swagger_client.ApiClient(configuration))
body = swagger_client.TablesTableIdOrNameBody() # TablesTableIdOrNameBody | 
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 

try:
    # Update table
    api_response = api_instance.airtable_tables_update(body, base_id, table_id_or_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TablesApi->airtable_tables_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**TablesTableIdOrNameBody**](TablesTableIdOrNameBody.md)|  | 
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 

### Return type

[**TableModel**](TableModel.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

