# swagger_client.DefaultApi

All URIs are relative to *https://api.search.brave.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**brave_search_get_web_search_results**](DefaultApi.md#brave_search_get_web_search_results) | **GET** /res/v1/web/search | Get detailed web search results

# **brave_search_get_web_search_results**
> InlineResponse200 brave_search_get_web_search_results(q, count=count, offset=offset, safesearch=safesearch, freshness=freshness, text_decorations=text_decorations, spellcheck=spellcheck, result_filter=result_filter, goggles_id=goggles_id, units=units, extra_snippets=extra_snippets, summary=summary)

Get detailed web search results

This endpoint allows you to perform a web search using Brave's search engine. It provides detailed search results based on the query term you specify, along with optional filters to refine your search. You can apply safe search settings, filter results by their freshness, and customize how the results are formatted. The output includes a list of search results with titles, descriptions, URLs, and additional metadata, making it suitable for deep integration into applications that require web search functionality.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: apiKey
configuration = swagger_client.Configuration()
configuration.api_key['X-Subscription-Token'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Subscription-Token'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
q = 'q_example' # str | The search query term. Use this parameter to specify the topic, keywords, or phrases to search for in Brave's web index. Example: 'climate change impacts'. 
count = 20 # int | Specifies the number of search results to return per request, with a maximum value of 20.  Useful for controlling the number of items displayed in paginated lists. Example: 10.  (optional) (default to 20)
offset = 0 # int | The zero-based offset for paginating search results. Use this parameter to skip a number of results. For example, setting `offset=10` skips the first 10 results and retrieves the next set.  (optional) (default to 0)
safesearch = 'moderate' # str | A filter to control the inclusion of adult or explicit content in the search results. Options: - `off`: No filtering (all content types included). - `moderate`: Filters explicit images and videos (default). - `strict`: Strict filtering of adult content.  (optional) (default to moderate)
freshness = 'freshness_example' # str | Restricts search results based on when the content was indexed by Brave Search.  Options: - `pd`: Results from the past day. - `pw`: Results from the past week. - `pm`: Results from the past month. - `py`: Results from the past year.  (optional)
text_decorations = true # bool | Indicates whether to include highlighting or decoration markers (e.g., bolding keywords) in display strings for search results. Example: true (default).  (optional) (default to true)
spellcheck = true # bool | Enables or disables spellchecking for the query. When enabled, the API corrects misspelled words in the query to improve result relevance. Example: true (default).  (optional) (default to true)
result_filter = 'result_filter_example' # str | A comma-separated list of specific result types to include in the response. Examples: - `news,images` (to include only news articles and images).  (optional)
goggles_id = 'goggles_id_example' # str | Applies custom re-ranking logic on top of the Brave Search index.  Use this parameter with a valid `goggles_id` value for personalized results.  (optional)
units = 'units_example' # str | The preferred system of measurement for displaying unit-based content in search results. Options: - `metric`: Metric units (kilometers, kilograms, etc.). - `imperial`: Imperial units (miles, pounds, etc.).  (optional)
extra_snippets = true # bool | Allows the API to return up to 5 alternative excerpts for each result.  Useful for presenting users with multiple contexts or descriptions for a single item.  (optional)
summary = true # bool | Enables the generation of summary keys for web search results, providing concise overviews of the content.  (optional)

try:
    # Get detailed web search results
    api_response = api_instance.brave_search_get_web_search_results(q, count=count, offset=offset, safesearch=safesearch, freshness=freshness, text_decorations=text_decorations, spellcheck=spellcheck, result_filter=result_filter, goggles_id=goggles_id, units=units, extra_snippets=extra_snippets, summary=summary)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->brave_search_get_web_search_results: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **str**| The search query term. Use this parameter to specify the topic, keywords, or phrases to search for in Brave&#x27;s web index. Example: &#x27;climate change impacts&#x27;.  | 
 **count** | **int**| Specifies the number of search results to return per request, with a maximum value of 20.  Useful for controlling the number of items displayed in paginated lists. Example: 10.  | [optional] [default to 20]
 **offset** | **int**| The zero-based offset for paginating search results. Use this parameter to skip a number of results. For example, setting &#x60;offset&#x3D;10&#x60; skips the first 10 results and retrieves the next set.  | [optional] [default to 0]
 **safesearch** | **str**| A filter to control the inclusion of adult or explicit content in the search results. Options: - &#x60;off&#x60;: No filtering (all content types included). - &#x60;moderate&#x60;: Filters explicit images and videos (default). - &#x60;strict&#x60;: Strict filtering of adult content.  | [optional] [default to moderate]
 **freshness** | **str**| Restricts search results based on when the content was indexed by Brave Search.  Options: - &#x60;pd&#x60;: Results from the past day. - &#x60;pw&#x60;: Results from the past week. - &#x60;pm&#x60;: Results from the past month. - &#x60;py&#x60;: Results from the past year.  | [optional] 
 **text_decorations** | **bool**| Indicates whether to include highlighting or decoration markers (e.g., bolding keywords) in display strings for search results. Example: true (default).  | [optional] [default to true]
 **spellcheck** | **bool**| Enables or disables spellchecking for the query. When enabled, the API corrects misspelled words in the query to improve result relevance. Example: true (default).  | [optional] [default to true]
 **result_filter** | **str**| A comma-separated list of specific result types to include in the response. Examples: - &#x60;news,images&#x60; (to include only news articles and images).  | [optional] 
 **goggles_id** | **str**| Applies custom re-ranking logic on top of the Brave Search index.  Use this parameter with a valid &#x60;goggles_id&#x60; value for personalized results.  | [optional] 
 **units** | **str**| The preferred system of measurement for displaying unit-based content in search results. Options: - &#x60;metric&#x60;: Metric units (kilometers, kilograms, etc.). - &#x60;imperial&#x60;: Imperial units (miles, pounds, etc.).  | [optional] 
 **extra_snippets** | **bool**| Allows the API to return up to 5 alternative excerpts for each result.  Useful for presenting users with multiple contexts or descriptions for a single item.  | [optional] 
 **summary** | **bool**| Enables the generation of summary keys for web search results, providing concise overviews of the content.  | [optional] 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[apiKey](../README.md#apiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

