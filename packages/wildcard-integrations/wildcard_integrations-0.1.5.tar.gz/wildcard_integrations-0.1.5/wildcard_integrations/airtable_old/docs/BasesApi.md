# swagger_client.BasesApi

All URIs are relative to *https://api.airtable.com/v0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**airtable_bases_create**](BasesApi.md#airtable_bases_create) | **POST** /meta/bases | Create base
[**airtable_bases_list**](BasesApi.md#airtable_bases_list) | **GET** /meta/bases | List bases
[**airtable_bases_schema**](BasesApi.md#airtable_bases_schema) | **GET** /meta/bases/{baseId}/tables | Get base schema

# **airtable_bases_create**
> InlineResponse20014 airtable_bases_create(body)

Create base

Creates a new base with the provided tables and returns the schema for the newly created base.  Refer to field types for supported field types, the write format for field options,  and other specifics for certain field types. Supported field types have a write format shown.  At least one table and field must be specified. The first field in the fields array will be used as  the table's primary field and must be a supported primary field type. Fields must have  case-insensitive unique names within the table.  A default grid view will be created with all fields visible for each provided table. 

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
api_instance = swagger_client.BasesApi(swagger_client.ApiClient(configuration))
body = swagger_client.MetaBasesBody() # MetaBasesBody | 

try:
    # Create base
    api_response = api_instance.airtable_bases_create(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BasesApi->airtable_bases_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**MetaBasesBody**](MetaBasesBody.md)|  | 

### Return type

[**InlineResponse20014**](InlineResponse20014.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_bases_list**
> InlineResponse20013 airtable_bases_list(offset=offset)

List bases

Returns the list of bases the token can access, 1000 bases at a time.  If there is another page to request, pass the offset as a URL query parameter.  (e.g. ?offset=itr23sEjsdfEr3282/appSW9R5uCNmRmfl6) 

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
api_instance = swagger_client.BasesApi(swagger_client.ApiClient(configuration))
offset = 'offset_example' # str | Pagination offset for the next page of results (optional)

try:
    # List bases
    api_response = api_instance.airtable_bases_list(offset=offset)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BasesApi->airtable_bases_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **offset** | **str**| Pagination offset for the next page of results | [optional] 

### Return type

[**InlineResponse20013**](InlineResponse20013.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_bases_schema**
> InlineResponse20012 airtable_bases_schema(base_id, include=include)

Get base schema

Returns the schema of the tables in the specified base.

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
api_instance = swagger_client.BasesApi(swagger_client.ApiClient(configuration))
base_id = 'base_id_example' # str | 
include = ['include_example'] # list[str] | Additional fields to include in the views object response (optional)

try:
    # Get base schema
    api_response = api_instance.airtable_bases_schema(base_id, include=include)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling BasesApi->airtable_bases_schema: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **base_id** | **str**|  | 
 **include** | [**list[str]**](str.md)| Additional fields to include in the views object response | [optional] 

### Return type

[**InlineResponse20012**](InlineResponse20012.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

