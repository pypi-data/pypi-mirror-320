# ListMessagesResponse

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**messages** | [**list[Message]**](Message.md) | List of messages. Note that each message resource contains only an &#x60;id&#x60; and a &#x60;threadId&#x60;. Additional message details can be fetched using the messages.get method. | [optional] 
**next_page_token** | **str** | Token to retrieve the next page of results in the list. | [optional] 
**result_size_estimate** | **int** | Estimated total number of results. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

