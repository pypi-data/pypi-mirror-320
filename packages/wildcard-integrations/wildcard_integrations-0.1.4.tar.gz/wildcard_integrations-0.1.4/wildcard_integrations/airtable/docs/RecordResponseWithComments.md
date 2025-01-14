# RecordResponseWithComments

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Record ID | 
**created_time** | **datetime** | A date timestamp in the ISO format, eg:\&quot;2018-01-01T00:00:00.000Z\&quot; | 
**fields** | **dict(str, object)** | Cell values are keyed by either field name or field ID (conditioned on returnFieldsByFieldId). See Cell Values for more information on cell value response types. | 
**comment_count** | **float** | The number of comments (if there are any) on the record. The recordMetadata query parameter must include \&quot;commentCount\&quot; in order to receive this. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

