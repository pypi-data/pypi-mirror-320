# InlineResponse20011

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | A comment ID | 
**created_time** | **datetime** | A date timestamp in the ISO format, eg:\&quot;2018-01-01T00:00:00.000Z\&quot; | 
**last_updated_time** | **datetime** | A date timestamp in the ISO format, eg- \&quot;2018-01-01T00:00:00.000Z\&quot;, or null if this comment has not been updated since creation. | [optional] 
**text** | **str** | The comment text itself. Note that this can contain the user mentioned in the text. See user mentioned for more. | 
**parent_comment_id** | **str** | The comment ID of the parent comment, if this comment is a threaded reply | [optional] 
**mentioned** | [**dict(str, UserMentioned)**](UserMentioned.md) |  | [optional] 
**reactions** | [**list[InlineResponse2008Reactions]**](InlineResponse2008Reactions.md) | A list of reactions on this comment. Each entry contains information about the emoji itself, along with metadata about the user who reacted. | [optional] 
**author** | [**InlineResponse2008Author**](InlineResponse2008Author.md) |  | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

