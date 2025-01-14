# MessagePartBody

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attachment_id** | **str** | When present, contains the ID of an external attachment that can be retrieved in a separate &#x60;messages.attachments.get&#x60; request. When not present, the entire content of the message part body is contained in the data field. | [optional] 
**data** | **str** | The body data of a MIME message part as a base64url encoded string. May be empty for MIME container types that have no message body or when the body data is sent as a separate attachment. An attachment ID is present if the body data is contained in a separate attachment. | [optional] 
**size** | **int** | Number of bytes for the message part data (encoding notwithstanding). | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

