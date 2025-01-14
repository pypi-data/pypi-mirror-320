# InlineResponse2009

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | A comment ID | 
**created_time** | **datetime** | Creation timestamp | 
**last_updated_time** | **datetime** | Last update timestamp | [optional] 
**text** | **str** | The comment text, may contain user mentions | 
**parent_comment_id** | **str** | ID of parent comment if this is a reply | [optional] 
**mentioned** | [**dict(str, UserMentioned)**](UserMentioned.md) |  | [optional] 
**reactions** | [**list[InlineResponse2009Reactions]**](InlineResponse2009Reactions.md) |  | [optional] 
**author** | [**InlineResponse2009Author**](InlineResponse2009Author.md) |  | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

