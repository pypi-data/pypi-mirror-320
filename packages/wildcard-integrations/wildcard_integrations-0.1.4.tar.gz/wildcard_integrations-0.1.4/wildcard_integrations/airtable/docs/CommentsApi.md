# swagger_client.CommentsApi

All URIs are relative to *https://api.airtable.com/v0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**airtable_comments_create**](CommentsApi.md#airtable_comments_create) | **POST** /{baseId}/{tableIdOrName}/{recordId}/comments | Create comment
[**airtable_comments_delete**](CommentsApi.md#airtable_comments_delete) | **DELETE** /{baseId}/{tableIdOrName}/{recordId}/comments/{rowCommentId} | Delete comment
[**airtable_comments_list**](CommentsApi.md#airtable_comments_list) | **GET** /{baseId}/{tableIdOrName}/{recordId}/comments | List comments
[**airtable_comments_update**](CommentsApi.md#airtable_comments_update) | **PATCH** /{baseId}/{tableIdOrName}/{recordId}/comments/{rowCommentId} | Update comment

# **airtable_comments_create**
> InlineResponse2009 airtable_comments_create(body, base_id, table_id_or_name, record_id)

Create comment

Creates a comment on a record. User mentioned is supported.

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
api_instance = swagger_client.CommentsApi(swagger_client.ApiClient(configuration))
body = swagger_client.RecordIdCommentsBody() # RecordIdCommentsBody | 
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 
record_id = 'record_id_example' # str | 

try:
    # Create comment
    api_response = api_instance.airtable_comments_create(body, base_id, table_id_or_name, record_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CommentsApi->airtable_comments_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**RecordIdCommentsBody**](RecordIdCommentsBody.md)|  | 
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 
 **record_id** | **str**|  | 

### Return type

[**InlineResponse2009**](InlineResponse2009.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_comments_delete**
> InlineResponse20010 airtable_comments_delete(base_id, table_id_or_name, record_id, row_comment_id)

Delete comment

Deletes a comment from a record. Non-admin API users can only delete comments they have created. Enterprise Admins can delete any comment from a record.

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
api_instance = swagger_client.CommentsApi(swagger_client.ApiClient(configuration))
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 
record_id = 'record_id_example' # str | 
row_comment_id = 'row_comment_id_example' # str | 

try:
    # Delete comment
    api_response = api_instance.airtable_comments_delete(base_id, table_id_or_name, record_id, row_comment_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CommentsApi->airtable_comments_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 
 **record_id** | **str**|  | 
 **row_comment_id** | **str**|  | 

### Return type

[**InlineResponse20010**](InlineResponse20010.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_comments_list**
> InlineResponse2008 airtable_comments_list(base_id, table_id_or_name, record_id, page_size=page_size, offset=offset)

List comments

Returns a list of comments for the record from newest to oldest.  Note: Comments in reply to another comment (where parentCommentId is set) may not have  their parent comment in the same page of results and vice versa. 

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
api_instance = swagger_client.CommentsApi(swagger_client.ApiClient(configuration))
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 
record_id = 'record_id_example' # str | 
page_size = 100 # int | If specified, this will determine the number of comments to return (optional) (default to 100)
offset = 'offset_example' # str | A pointer to a specific comment for pagination (optional)

try:
    # List comments
    api_response = api_instance.airtable_comments_list(base_id, table_id_or_name, record_id, page_size=page_size, offset=offset)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CommentsApi->airtable_comments_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 
 **record_id** | **str**|  | 
 **page_size** | **int**| If specified, this will determine the number of comments to return | [optional] [default to 100]
 **offset** | **str**| A pointer to a specific comment for pagination | [optional] 

### Return type

[**InlineResponse2008**](InlineResponse2008.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_comments_update**
> InlineResponse20011 airtable_comments_update(body, base_id, table_id_or_name, record_id, row_comment_id)

Update comment

Updates a comment on a record. API users can only update comments they have created.  User mentioned is supported. 

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
api_instance = swagger_client.CommentsApi(swagger_client.ApiClient(configuration))
body = swagger_client.CommentsRowCommentIdBody() # CommentsRowCommentIdBody | 
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 
record_id = 'record_id_example' # str | 
row_comment_id = 'row_comment_id_example' # str | 

try:
    # Update comment
    api_response = api_instance.airtable_comments_update(body, base_id, table_id_or_name, record_id, row_comment_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CommentsApi->airtable_comments_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**CommentsRowCommentIdBody**](CommentsRowCommentIdBody.md)|  | 
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 
 **record_id** | **str**|  | 
 **row_comment_id** | **str**|  | 

### Return type

[**InlineResponse20011**](InlineResponse20011.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

