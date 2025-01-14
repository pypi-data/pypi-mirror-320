# SmtpMsa

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**host** | **str** | The hostname of the SMTP service. Required. | [optional] 
**password** | **str** | The password that will be used for authentication with the SMTP service. This is a write-only field that can be specified in requests to create or update SendAs settings; it is never populated in responses. | [optional] 
**port** | **int** | The port of the SMTP service. Required. | [optional] 
**security_mode** | **str** | The protocol that will be used to secure communication with the SMTP service. Required. | [optional] 
**username** | **str** | The username that will be used for authentication with the SMTP service. This is a write-only field that can be specified in requests to create or update SendAs settings; it is never populated in responses. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

