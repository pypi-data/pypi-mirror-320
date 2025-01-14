# History

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The mailbox sequence ID. | [optional] 
**labels_added** | [**list[HistoryLabelAdded]**](HistoryLabelAdded.md) | Labels added to messages in this history record. | [optional] 
**labels_removed** | [**list[HistoryLabelRemoved]**](HistoryLabelRemoved.md) | Labels removed from messages in this history record. | [optional] 
**messages** | [**list[Message]**](Message.md) | List of messages changed in this history record. The fields for specific change types, such as &#x60;messagesAdded&#x60; may duplicate messages in this field. We recommend using the specific change-type fields instead of this. | [optional] 
**messages_added** | [**list[HistoryMessageAdded]**](HistoryMessageAdded.md) | Messages added to the mailbox in this history record. | [optional] 
**messages_deleted** | [**list[HistoryMessageDeleted]**](HistoryMessageDeleted.md) | Messages deleted (not Trashed) from the mailbox in this history record. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

