# ListDraftsResponse

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**drafts** | [**list[Draft]**](Draft.md) | List of drafts. Note that the &#x60;Message&#x60; property in each &#x60;Draft&#x60; resource only contains an &#x60;id&#x60; and a &#x60;threadId&#x60;. The messages.get method can fetch additional message details. | [optional] 
**next_page_token** | **str** | Token to retrieve the next page of results in the list. | [optional] 
**result_size_estimate** | **int** | Estimated total number of results. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

