# MessagePart

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | [**MessagePartBody**](MessagePartBody.md) |  | [optional] 
**filename** | **str** | The filename of the attachment. Only present if this message part represents an attachment. | [optional] 
**headers** | [**list[MessagePartHeader]**](MessagePartHeader.md) | List of headers on this message part. For the top-level message part, representing the entire message payload, make it contain the standard RFC 2822 email headers such as &#x60;To&#x60;, &#x60;From&#x60;, and &#x60;Subject&#x60;. | [optional] 
**mime_type** | **str** | The MIME type of the message part. | [optional] 
**part_id** | **str** | The immutable ID of the message part. | [optional] 
**parts** | [**list[MessagePart]**](MessagePart.md) | The child MIME message parts of this part. This only applies to container MIME message parts, for example &#x60;multipart/*&#x60;. For non- container MIME message part types, such as &#x60;text/plain&#x60;, this field is empty. For more information, see RFC 1521. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

