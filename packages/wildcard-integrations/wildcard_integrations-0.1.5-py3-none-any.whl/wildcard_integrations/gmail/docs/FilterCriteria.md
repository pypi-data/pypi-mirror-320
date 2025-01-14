# FilterCriteria

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exclude_chats** | **bool** | Whether the response should exclude chats. | [optional] 
**_from** | **str** | The sender&#x27;s display name or email address. | [optional] 
**has_attachment** | **bool** | Whether the message has any attachment. | [optional] 
**negated_query** | **str** | Only return messages not matching the specified query. Supports the same query format as the Gmail search box. For example, &#x60;\&quot;from:someuser@example.com rfc822msgid: is:unread\&quot;&#x60;. | [optional] 
**query** | **str** | Only return messages matching the specified query. Supports the same query format as the Gmail search box. For example, &#x60;\&quot;from:someuser@example.com rfc822msgid: is:unread\&quot;&#x60;. | [optional] 
**size** | **int** | The size of the entire RFC822 message in bytes, including all headers and attachments. | [optional] 
**size_comparison** | **str** | How the message size in bytes should be in relation to the size field. | [optional] 
**subject** | **str** | Case-insensitive phrase found in the message&#x27;s subject. Trailing and leading whitespace are be trimmed and adjacent spaces are collapsed. | [optional] 
**to** | **str** | The recipient&#x27;s display name or email address. Includes recipients in the \&quot;to\&quot;, \&quot;cc\&quot;, and \&quot;bcc\&quot; header fields. You can use simply the local part of the email address. For example, \&quot;example\&quot; and \&quot;example@\&quot; both match \&quot;example@gmail.com\&quot;. This field is case-insensitive. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

