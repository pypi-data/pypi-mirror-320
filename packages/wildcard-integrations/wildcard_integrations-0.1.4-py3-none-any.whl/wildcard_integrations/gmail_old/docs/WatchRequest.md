# WatchRequest

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**label_filter_action** | **str** | Filtering behavior of labelIds list specified. | [optional] 
**label_ids** | **list[str]** | List of label_ids to restrict notifications about. By default, if unspecified, all changes are pushed out. If specified then dictates which labels are required for a push notification to be generated. | [optional] 
**topic_name** | **str** | A fully qualified Google Cloud Pub/Sub API topic name to publish the events to. This topic name **must** already exist in Cloud Pub/Sub and you **must** have already granted gmail \&quot;publish\&quot; permission on it. For example, \&quot;projects/my-project-identifier/topics/my-topic-name\&quot; (using the Cloud Pub/Sub \&quot;v1\&quot; topic naming format). Note that the \&quot;my-project-identifier\&quot; portion must exactly match your Google developer project id (the one executing this watch request). | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

