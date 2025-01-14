# TableIdOrNameRecordIdBody

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**return_fields_by_field_id** | **bool** | An optional boolean value that lets you return field objects keyed by the field id. This defaults to false, which returns field objects where the key is the field name. | [optional] [default to False]
**typecast** | **bool** | The Airtable API will perform best-effort automatic data conversion from string values if the typecast parameter is passed in. Automatic conversion is disabled by default to ensure data integrity, but it may be helpful for integrating with 3rd party data sources. | [optional] [default to False]
**fields** | **dict(str, object)** | Cell values keyed by field name or field id | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

