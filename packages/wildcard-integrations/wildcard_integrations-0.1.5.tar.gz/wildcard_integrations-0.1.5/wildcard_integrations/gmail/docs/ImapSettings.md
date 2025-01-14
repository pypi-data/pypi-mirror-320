# ImapSettings

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auto_expunge** | **bool** | If this value is true, Gmail will immediately expunge a message when it is marked as deleted in IMAP. Otherwise, Gmail will wait for an update from the client before expunging messages marked as deleted. | [optional] 
**enabled** | **bool** | Whether IMAP is enabled for the account. | [optional] 
**expunge_behavior** | **str** | The action that will be executed on a message when it is marked as deleted and expunged from the last visible IMAP folder. | [optional] 
**max_folder_size** | **int** | An optional limit on the number of messages that an IMAP folder may contain. Legal values are 0, 1000, 2000, 5000 or 10000. A value of zero is interpreted to mean that there is no limit. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

