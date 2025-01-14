# FieldOptions

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prompt** | **list[OneOfFieldOptionsPromptItems]** | The prompt that is used to generate the results in the AI field, additional object types may be added in the future. Currently, this is an array of strings or objects that identify any fields interpolated into the prompt. The prompt will not currently be provided if this field config is within another fields configuration (like a lookup field). | [optional] 
**referenced_field_ids** | **list[str]** | The other fields in the record that are used in the ai field. The referencedFieldIds will not currently be provided if this field config is within another fields configuration (like a lookup field). | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

