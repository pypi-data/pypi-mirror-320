# swagger_client.FieldsApi

All URIs are relative to *https://api.airtable.com/v0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**airtable_fields_create**](FieldsApi.md#airtable_fields_create) | **POST** /meta/bases/{baseId}/tables/{tableId}/fields | Create field
[**airtable_fields_update**](FieldsApi.md#airtable_fields_update) | **PATCH** /meta/bases/{baseId}/tables/{tableId}/fields/{columnId} | Update field

# **airtable_fields_create**
> FieldConfigResponse airtable_fields_create(body, base_id, table_id)

Create field

Creates a new column and returns the schema for the newly created column.  Refer to field types for supported field types, the write format for field options,  and other specifics for certain field types. Supported field types have a write format shown. 

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
api_instance = swagger_client.FieldsApi(swagger_client.ApiClient(configuration))
body = swagger_client.FieldConfigRequest() # FieldConfigRequest | Field model with name. This identical to Field type and options, with an additional name and description property on all types
base_id = 'base_id_example' # str | 
table_id = 'table_id_example' # str | 

try:
    # Create field
    api_response = api_instance.airtable_fields_create(body, base_id, table_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FieldsApi->airtable_fields_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**FieldConfigRequest**](FieldConfigRequest.md)| Field model with name. This identical to Field type and options, with an additional name and description property on all types | 
 **base_id** | **str**|  | 
 **table_id** | **str**|  | 

### Return type

[**FieldConfigResponse**](FieldConfigResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_fields_update**
> FieldConfigResponse airtable_fields_update(body, base_id, table_id, column_id)

Update field

Updates the name and/or description of a field. At least one of name or description must be specified.

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
api_instance = swagger_client.FieldsApi(swagger_client.ApiClient(configuration))
body = swagger_client.FieldsColumnIdBody() # FieldsColumnIdBody | 
base_id = 'base_id_example' # str | 
table_id = 'table_id_example' # str | 
column_id = 'column_id_example' # str | 

try:
    # Update field
    api_response = api_instance.airtable_fields_update(body, base_id, table_id, column_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FieldsApi->airtable_fields_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**FieldsColumnIdBody**](FieldsColumnIdBody.md)|  | 
 **base_id** | **str**|  | 
 **table_id** | **str**|  | 
 **column_id** | **str**|  | 

### Return type

[**FieldConfigResponse**](FieldConfigResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

