# swagger_client.RecordsApi

All URIs are relative to *https://api.airtable.com/v0*

Method | HTTP request | Description
------------- | ------------- | -------------
[**airtable_records_create**](RecordsApi.md#airtable_records_create) | **POST** /{baseId}/{tableIdOrName} | Create records
[**airtable_records_delete**](RecordsApi.md#airtable_records_delete) | **DELETE** /{baseId}/{tableIdOrName}/{recordId} | Delete record
[**airtable_records_delete_multiple**](RecordsApi.md#airtable_records_delete_multiple) | **DELETE** /{baseId}/{tableIdOrName} | Delete multiple records
[**airtable_records_get**](RecordsApi.md#airtable_records_get) | **GET** /{baseId}/{tableIdOrName}/{recordId} | Get record
[**airtable_records_list**](RecordsApi.md#airtable_records_list) | **GET** /{baseId}/{tableIdOrName} | List records
[**airtable_records_replace**](RecordsApi.md#airtable_records_replace) | **PUT** /{baseId}/{tableIdOrName}/{recordId} | Replace record
[**airtable_records_replace_multiple**](RecordsApi.md#airtable_records_replace_multiple) | **PUT** /{baseId}/{tableIdOrName} | Replace multiple records
[**airtable_records_sync_csv**](RecordsApi.md#airtable_records_sync_csv) | **POST** /{baseId}/{tableIdOrName}/sync/{apiEndpointSyncId} | Sync CSV data
[**airtable_records_update**](RecordsApi.md#airtable_records_update) | **PATCH** /{baseId}/{tableIdOrName}/{recordId} | Update record
[**airtable_records_update_multiple**](RecordsApi.md#airtable_records_update_multiple) | **PATCH** /{baseId}/{tableIdOrName} | Update multiple records
[**airtable_records_upload_attachment**](RecordsApi.md#airtable_records_upload_attachment) | **POST** /content.airtable.com/v0/{baseId}/{recordId}/{attachmentFieldIdOrName}/uploadAttachment | Upload attachment

# **airtable_records_create**
> InlineResponse2003 airtable_records_create(body, base_id, table_id_or_name)

Create records

Creates multiple records. Note that table names and table ids can be used interchangeably. We recommend using table IDs so you don't need to modify your API request when your table name changes.  Your request body should include an array of up to 10 record objects. Each of these objects should have one key whose value is an inner object containing your record's cell values, keyed by either field name or field id.  Returns a unique array of the newly created record ids if the call succeeds.  You can also include a single record object at the top level. 

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
api_instance = swagger_client.RecordsApi(swagger_client.ApiClient(configuration))
body = swagger_client.BaseIdTableIdOrNameBody1() # BaseIdTableIdOrNameBody1 | 
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 

try:
    # Create records
    api_response = api_instance.airtable_records_create(body, base_id, table_id_or_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RecordsApi->airtable_records_create: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**BaseIdTableIdOrNameBody1**](BaseIdTableIdOrNameBody1.md)|  | 
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 

### Return type

[**InlineResponse2003**](InlineResponse2003.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_records_delete**
> InlineResponse2005 airtable_records_delete(base_id, table_id_or_name, record_id)

Delete record

Deletes a single record

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
api_instance = swagger_client.RecordsApi(swagger_client.ApiClient(configuration))
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 
record_id = 'record_id_example' # str | 

try:
    # Delete record
    api_response = api_instance.airtable_records_delete(base_id, table_id_or_name, record_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RecordsApi->airtable_records_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 
 **record_id** | **str**|  | 

### Return type

[**InlineResponse2005**](InlineResponse2005.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_records_delete_multiple**
> InlineResponse2004 airtable_records_delete_multiple(base_id, table_id_or_name, records=records)

Delete multiple records

Deletes records given an array of record ids

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
api_instance = swagger_client.RecordsApi(swagger_client.ApiClient(configuration))
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 
records = ['records_example'] # list[str] | The recordIds of each record to be deleted. Up to 10 recordIds can be provided. (optional)

try:
    # Delete multiple records
    api_response = api_instance.airtable_records_delete_multiple(base_id, table_id_or_name, records=records)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RecordsApi->airtable_records_delete_multiple: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 
 **records** | [**list[str]**](str.md)| The recordIds of each record to be deleted. Up to 10 recordIds can be provided. | [optional] 

### Return type

[**InlineResponse2004**](InlineResponse2004.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_records_get**
> RecordResponse airtable_records_get(base_id, table_id_or_name, record_id, cell_format=cell_format, return_fields_by_field_id=return_fields_by_field_id)

Get record

Retrieve a single record. Any \"empty\" fields (e.g. \"\", [], or false) in the record will not be returned.

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
api_instance = swagger_client.RecordsApi(swagger_client.ApiClient(configuration))
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 
record_id = 'record_id_example' # str | 
cell_format = 'json' # str | The format that should be used for cell values. Supported values are:  json: cells will be formatted as JSON, depending on the field type. string: cells will be formatted as user-facing strings, regardless of the field type. The timeZone and userLocale parameters are required when using string as the cellFormat. Note: You should not rely on the format of these strings, as it is subject to change.  The default is json.  (optional) (default to json)
return_fields_by_field_id = false # bool | An optional boolean value that lets you return field objects where the key is the field id. This defaults to false, which returns field objects where the key is the field name. (optional) (default to false)

try:
    # Get record
    api_response = api_instance.airtable_records_get(base_id, table_id_or_name, record_id, cell_format=cell_format, return_fields_by_field_id=return_fields_by_field_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RecordsApi->airtable_records_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 
 **record_id** | **str**|  | 
 **cell_format** | **str**| The format that should be used for cell values. Supported values are:  json: cells will be formatted as JSON, depending on the field type. string: cells will be formatted as user-facing strings, regardless of the field type. The timeZone and userLocale parameters are required when using string as the cellFormat. Note: You should not rely on the format of these strings, as it is subject to change.  The default is json.  | [optional] [default to json]
 **return_fields_by_field_id** | **bool**| An optional boolean value that lets you return field objects where the key is the field id. This defaults to false, which returns field objects where the key is the field name. | [optional] [default to false]

### Return type

[**RecordResponse**](RecordResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_records_list**
> InlineResponse2001 airtable_records_list(base_id, table_id_or_name, time_zone=time_zone, user_locale=user_locale, page_size=page_size, max_records=max_records, offset=offset, view=view, sort=sort, filter_by_formula=filter_by_formula, cell_format=cell_format, fields=fields, return_fields_by_field_id=return_fields_by_field_id, record_metadata=record_metadata)

List records

List records in a table. Table names and IDs can be used interchangeably, though using IDs is recommended to avoid issues if table names change. The API returns records with a default `pageSize` of 100. To fetch subsequent pages use the `offset` parameter. Pagination ends when reaching the table end or maxRecords limit if specified. Empty field values (\"\", [], false) are omitted from returned records. Results can be filtered, sorted and formatted using URL-encoded query parameters. The API URL length is limited to 16,000 characters. For longer requests with encoded formulas, use POST to /v0/{baseId}/{tableIdOrName}/listRecords with parameters in the request body instead of query parameters. 

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
api_instance = swagger_client.RecordsApi(swagger_client.ApiClient(configuration))
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 
time_zone = 'time_zone_example' # str | The time zone that should be used to format dates when using string as the cellFormat. This parameter is required when using string as the cellFormat. (optional)
user_locale = 'user_locale_example' # str | The user locale that should be used to format dates when using string as the cellFormat. This parameter is required when using string as the cellFormat. (optional)
page_size = 100 # int | The number of records returned in each request. Must be less than or equal to 100. Default is 100. (optional) (default to 100)
max_records = 56 # int | The maximum total number of records that will be returned in your requests. If this value is larger than pageSize (which is 100 by default), you may have to load multiple pages to reach this total. (optional)
offset = 'offset_example' # str | To fetch the next page of records, include offset from the previous request in the next request's parameters. (optional)
view = 'view_example' # str | The name or ID of a view in the table. If set, only the records in that view will be returned. The records will be sorted according to the order of the view unless the sort parameter is included, which overrides that order. Fields hidden in this view will be returned in the results. To only return a subset of fields, use the fields parameter. (optional)
sort = [swagger_client.Sort()] # list[Sort] | A list of sort objects that specifies how the records will be ordered. Each sort object must have a field key specifying the name of the field to sort on, and an optional direction key that is either \"asc\" or \"desc\". The default direction is \"asc\".  The sort parameter overrides the sorting of the view specified in the view parameter. If neither the sort nor the view parameter is included, the order of records is arbitrary.  (optional)
filter_by_formula = 'filter_by_formula_example' # str | A formula used to filter records. The formula will be evaluated for each record, and if the result is not 0, false, \"\", NaN, [], or #Error! the record will be included in the response. We recommend testing your formula in the Formula field UI before using it in your API request. If combined with the view parameter, only records in that view which satisfy the formula will be returned. The formula must be encoded first before passing it as a value. You can use this tool to not only encode the formula but also create the entire url you need. Formulas can use field names, or field id's inside of the formula. Note Airtable's API only accepts request with a URL shorter than 16,000 characters. Encoded formulas may cause your requests to exceed this limit. To fix this issue you can instead make a POST request to /v0/{baseId}/{tableIdOrName}/listRecords while passing the parameters within the body of the request instead of the query parameters.  (optional)
cell_format = 'json' # str | The format that should be used for cell values. Supported values are:  json: cells will be formatted as JSON, depending on the field type. string: cells will be formatted as user-facing strings, regardless of the field type. The timeZone and userLocale parameters are required when using string as the cellFormat.  Note: You should not rely on the format of these strings, as it is subject to change.  The default is json.  (optional) (default to json)
fields = ['fields_example'] # list[str] | Only data for fields whose names or IDs are in this list will be included in the result. If you don't need every field, you can use this parameter to reduce the amount of data transferred.  Note Airtable's API only accepts request with a URL shorter than 16,000 characters. Encoded formulas may cause your requests to exceed this limit. To fix this issue you can instead make a POST request to /v0/{baseId}/{tableIdOrName}/listRecords while passing the parameters within the body of the request instead of the query parameters.  (optional)
return_fields_by_field_id = false # bool | An optional boolean value that lets you return field objects where the key is the field id. This defaults to false, which returns field objects where the key is the field name. (optional) (default to false)
record_metadata = ['record_metadata_example'] # list[str] | An optional field that, if specified, includes commentCount on each record returned. (optional)

try:
    # List records
    api_response = api_instance.airtable_records_list(base_id, table_id_or_name, time_zone=time_zone, user_locale=user_locale, page_size=page_size, max_records=max_records, offset=offset, view=view, sort=sort, filter_by_formula=filter_by_formula, cell_format=cell_format, fields=fields, return_fields_by_field_id=return_fields_by_field_id, record_metadata=record_metadata)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RecordsApi->airtable_records_list: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 
 **time_zone** | **str**| The time zone that should be used to format dates when using string as the cellFormat. This parameter is required when using string as the cellFormat. | [optional] 
 **user_locale** | **str**| The user locale that should be used to format dates when using string as the cellFormat. This parameter is required when using string as the cellFormat. | [optional] 
 **page_size** | **int**| The number of records returned in each request. Must be less than or equal to 100. Default is 100. | [optional] [default to 100]
 **max_records** | **int**| The maximum total number of records that will be returned in your requests. If this value is larger than pageSize (which is 100 by default), you may have to load multiple pages to reach this total. | [optional] 
 **offset** | **str**| To fetch the next page of records, include offset from the previous request in the next request&#x27;s parameters. | [optional] 
 **view** | **str**| The name or ID of a view in the table. If set, only the records in that view will be returned. The records will be sorted according to the order of the view unless the sort parameter is included, which overrides that order. Fields hidden in this view will be returned in the results. To only return a subset of fields, use the fields parameter. | [optional] 
 **sort** | [**list[Sort]**](Sort.md)| A list of sort objects that specifies how the records will be ordered. Each sort object must have a field key specifying the name of the field to sort on, and an optional direction key that is either \&quot;asc\&quot; or \&quot;desc\&quot;. The default direction is \&quot;asc\&quot;.  The sort parameter overrides the sorting of the view specified in the view parameter. If neither the sort nor the view parameter is included, the order of records is arbitrary.  | [optional] 
 **filter_by_formula** | **str**| A formula used to filter records. The formula will be evaluated for each record, and if the result is not 0, false, \&quot;\&quot;, NaN, [], or #Error! the record will be included in the response. We recommend testing your formula in the Formula field UI before using it in your API request. If combined with the view parameter, only records in that view which satisfy the formula will be returned. The formula must be encoded first before passing it as a value. You can use this tool to not only encode the formula but also create the entire url you need. Formulas can use field names, or field id&#x27;s inside of the formula. Note Airtable&#x27;s API only accepts request with a URL shorter than 16,000 characters. Encoded formulas may cause your requests to exceed this limit. To fix this issue you can instead make a POST request to /v0/{baseId}/{tableIdOrName}/listRecords while passing the parameters within the body of the request instead of the query parameters.  | [optional] 
 **cell_format** | **str**| The format that should be used for cell values. Supported values are:  json: cells will be formatted as JSON, depending on the field type. string: cells will be formatted as user-facing strings, regardless of the field type. The timeZone and userLocale parameters are required when using string as the cellFormat.  Note: You should not rely on the format of these strings, as it is subject to change.  The default is json.  | [optional] [default to json]
 **fields** | [**list[str]**](str.md)| Only data for fields whose names or IDs are in this list will be included in the result. If you don&#x27;t need every field, you can use this parameter to reduce the amount of data transferred.  Note Airtable&#x27;s API only accepts request with a URL shorter than 16,000 characters. Encoded formulas may cause your requests to exceed this limit. To fix this issue you can instead make a POST request to /v0/{baseId}/{tableIdOrName}/listRecords while passing the parameters within the body of the request instead of the query parameters.  | [optional] 
 **return_fields_by_field_id** | **bool**| An optional boolean value that lets you return field objects where the key is the field id. This defaults to false, which returns field objects where the key is the field name. | [optional] [default to false]
 **record_metadata** | [**list[str]**](str.md)| An optional field that, if specified, includes commentCount on each record returned. | [optional] 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_records_replace**
> RecordResponse airtable_records_replace(body, base_id, table_id_or_name, record_id)

Replace record

Updates a single record. Table names and table ids can be used interchangeably. We recommend using table IDs so you don't need to modify your API request when your table name changes. A PUT request will perform a destructive update and clear all unspecified cell values. A PATCH request will only update the fields you specify, leaving the rest as they were.  Your request body should include a fields property whose value is an object containing your record's cell values, keyed by either field name or field id.  Automatic data conversion for update actions can be enabled via typecast parameter. The Airtable API will perform best-effort automatic data conversion from string values if the typecast parameter is passed in. Automatic conversion is disabled by default to ensure data integrity, but it may be helpful for integrating with 3rd party data sources. 

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
api_instance = swagger_client.RecordsApi(swagger_client.ApiClient(configuration))
body = swagger_client.TableIdOrNameRecordIdBody() # TableIdOrNameRecordIdBody | 
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 
record_id = 'record_id_example' # str | 

try:
    # Replace record
    api_response = api_instance.airtable_records_replace(body, base_id, table_id_or_name, record_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RecordsApi->airtable_records_replace: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**TableIdOrNameRecordIdBody**](TableIdOrNameRecordIdBody.md)|  | 
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 
 **record_id** | **str**|  | 

### Return type

[**RecordResponse**](RecordResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_records_replace_multiple**
> InlineResponse2002 airtable_records_replace_multiple(body, base_id, table_id_or_name)

Replace multiple records

Updates up to 10 records. Use table IDs instead of names for stability.  This PUT methods CLEARS all unspecified values. If this is not what you want, use PATCH instead.  Upserts (enabled via performUpsert): - Makes record id optional - Uses fieldsToMergeOn fields as external ID to match records - Creates new record if no match found - Updates record if one match found - Fails if multiple matches found - Records with id ignore fieldsToMergeOn and follow normal update behavior - Response includes updatedRecords and createdRecords arrays - May be throttled differently than standard requests  Typecasting (enabled via typecast parameter): - Attempts to convert string values to appropriate cell types - Best-effort conversion only - Disabled by default to protect data integrity - Useful for third-party integrations 

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
api_instance = swagger_client.RecordsApi(swagger_client.ApiClient(configuration))
body = swagger_client.BaseIdTableIdOrNameBody() # BaseIdTableIdOrNameBody | 
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 

try:
    # Replace multiple records
    api_response = api_instance.airtable_records_replace_multiple(body, base_id, table_id_or_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RecordsApi->airtable_records_replace_multiple: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**BaseIdTableIdOrNameBody**](BaseIdTableIdOrNameBody.md)|  | 
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 

### Return type

[**InlineResponse2002**](InlineResponse2002.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_records_sync_csv**
> InlineResponse2006 airtable_records_sync_csv(body, base_id, table_id_or_name, api_endpoint_sync_id)

Sync CSV data

Syncs raw CSV data into a Sync API table. You must first set up a sync from a base (instructions in this support article). The apiEndpointSyncId in the path parameters can be found in the setup flow when creating a new Sync API table, or from the synced table settings.  The CSV data can contain up to 10k rows, 500 columns, and the HTTP request's size is limited to 2 MB.  There is a rate limit of 20 requests, per 5 minutes, per base for this endpoint. 

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
api_instance = swagger_client.RecordsApi(swagger_client.ApiClient(configuration))
body = '\"column1,column2\\nrow1-column1,row1-column2\\nrow2-column1,row2-column2\\n\"' # str | 
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 
api_endpoint_sync_id = 'api_endpoint_sync_id_example' # str | 

try:
    # Sync CSV data
    api_response = api_instance.airtable_records_sync_csv(body, base_id, table_id_or_name, api_endpoint_sync_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RecordsApi->airtable_records_sync_csv: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**str**](str.md)|  | 
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 
 **api_endpoint_sync_id** | **str**|  | 

### Return type

[**InlineResponse2006**](InlineResponse2006.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: text/csv
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_records_update**
> RecordResponse airtable_records_update(body, base_id, table_id_or_name, record_id)

Update record

Updates a single record. Table names and table ids can be used interchangeably. We recommend using table IDs so you don't need to modify your API request when your table name changes. A PATCH request will only update the fields you specify, leaving the rest as they were. A PUT request will perform a destructive update and clear all unspecified cell values.  Your request body should include a fields property whose value is an object containing your record's cell values, keyed by either field name or field id.  Automatic data conversion for update actions can be enabled via typecast parameter. The Airtable API will perform best-effort automatic data conversion from string values if the typecast parameter is passed in. Automatic conversion is disabled by default to ensure data integrity, but it may be helpful for integrating with 3rd party data sources. 

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
api_instance = swagger_client.RecordsApi(swagger_client.ApiClient(configuration))
body = swagger_client.TableIdOrNameRecordIdBody1() # TableIdOrNameRecordIdBody1 | 
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 
record_id = 'record_id_example' # str | 

try:
    # Update record
    api_response = api_instance.airtable_records_update(body, base_id, table_id_or_name, record_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RecordsApi->airtable_records_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**TableIdOrNameRecordIdBody1**](TableIdOrNameRecordIdBody1.md)|  | 
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 
 **record_id** | **str**|  | 

### Return type

[**RecordResponse**](RecordResponse.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_records_update_multiple**
> InlineResponse2002 airtable_records_update_multiple(body, base_id, table_id_or_name)

Update multiple records

Updates up to 10 records or upserts them when `performUpsert` is set. The URL path accepts both table names and table IDs. - **PATCH Request:** Updates only the fields included in the request; other fields remain unchanged.  **Upserts:** - Enable Upserts by setting `performUpsert` to `true`. - When upserting, the `id` property is optional. Records without `id` use `fieldsToMergeOn` to match existing records.   - **0 matches:** Creates a new record.   - **1 match:** Updates the existing record.   - **Multiple matches:** Request fails. - Records with `id` ignore `fieldsToMergeOn` and follow normal update behavior. If the `id` doesn't exist, the request fails without creating a new record. - The response includes `updatedRecords` and `createdRecords` arrays to indicate the status of each record. - Upsert requests may be throttled differently from standard rate limits.  **Typecasting:** - Enable by setting `typecast` to `true`. - Attempts to convert string values to appropriate cell types on a best-effort basis. - Disabled by default. - Useful for third-party integrations 

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
api_instance = swagger_client.RecordsApi(swagger_client.ApiClient(configuration))
body = swagger_client.BaseIdTableIdOrNameBody2() # BaseIdTableIdOrNameBody2 | 
base_id = 'base_id_example' # str | 
table_id_or_name = 'table_id_or_name_example' # str | 

try:
    # Update multiple records
    api_response = api_instance.airtable_records_update_multiple(body, base_id, table_id_or_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RecordsApi->airtable_records_update_multiple: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**BaseIdTableIdOrNameBody2**](BaseIdTableIdOrNameBody2.md)|  | 
 **base_id** | **str**|  | 
 **table_id_or_name** | **str**|  | 

### Return type

[**InlineResponse2002**](InlineResponse2002.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **airtable_records_upload_attachment**
> InlineResponse2007 airtable_records_upload_attachment(body, base_id, record_id, attachment_field_id_or_name)

Upload attachment

Upload an attachment up to 5 MB to an attachment cell via the file bytes directly.  To upload attachments above this size that are accessible by a public URL, they can be added using  https://airtable.com/developers/web/api/field-model#multipleattachment 

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
api_instance = swagger_client.RecordsApi(swagger_client.ApiClient(configuration))
body = swagger_client.AttachmentFieldIdOrNameUploadAttachmentBody() # AttachmentFieldIdOrNameUploadAttachmentBody | 
base_id = 'base_id_example' # str | 
record_id = 'record_id_example' # str | 
attachment_field_id_or_name = 'attachment_field_id_or_name_example' # str | 

try:
    # Upload attachment
    api_response = api_instance.airtable_records_upload_attachment(body, base_id, record_id, attachment_field_id_or_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling RecordsApi->airtable_records_upload_attachment: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**AttachmentFieldIdOrNameUploadAttachmentBody**](AttachmentFieldIdOrNameUploadAttachmentBody.md)|  | 
 **base_id** | **str**|  | 
 **record_id** | **str**|  | 
 **attachment_field_id_or_name** | **str**|  | 

### Return type

[**InlineResponse2007**](InlineResponse2007.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth), [Oauth2](../README.md#Oauth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

