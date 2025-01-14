# BaseIdTableIdOrNameBody

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**perform_upsert** | [**BaseIdtableIdOrNamePerformUpsert**](BaseIdtableIdOrNamePerformUpsert.md) |  | [optional] 
**return_fields_by_field_id** | **bool** | If set to true, records in the API response will key the fields object by field ID. Defaults to false when unset, which returns fields objects keyed by field name. | [optional] [default to False]
**typecast** | **bool** | If set to true, Airtable will try to convert string values into the appropriate cell value. This conversion is only performed on a best-effort basis. To ensure your data&#x27;s integrity, this should only be used when necessary. Defaults to false when unset. | [optional] [default to False]
**records** | [**list[BaseIdtableIdOrNameRecords]**](BaseIdtableIdOrNameRecords.md) | Array of records to update | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

