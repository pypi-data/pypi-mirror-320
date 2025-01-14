# ListThreadsResponse

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page_token** | **str** | Page token to retrieve the next page of results in the list. | [optional] 
**result_size_estimate** | **int** | Estimated total number of results. | [optional] 
**threads** | [**list[Thread]**](Thread.md) | List of threads. Note that each thread resource does not contain a list of &#x60;messages&#x60;. The list of &#x60;messages&#x60; for a given thread can be fetched using the threads.get method. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

