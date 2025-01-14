# CseKeyPair

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**disable_time** | **str** | Output only. If a key pair is set to &#x60;DISABLED&#x60;, the time that the key pair&#x27;s state changed from &#x60;ENABLED&#x60; to &#x60;DISABLED&#x60;. This field is present only when the key pair is in state &#x60;DISABLED&#x60;. | [optional] 
**enablement_state** | **str** | Output only. The current state of the key pair. | [optional] 
**key_pair_id** | **str** | Output only. The immutable ID for the client-side encryption S/MIME key pair. | [optional] 
**pem** | **str** | Output only. The public key and its certificate chain, in [PEM](https://en.wikipedia.org/wiki/Privacy-Enhanced_Mail) format. | [optional] 
**pkcs7** | **str** | Input only. The public key and its certificate chain. The chain must be in [PKCS#7](https://en.wikipedia.org/wiki/PKCS_7) format and use PEM encoding and ASCII armor. | [optional] 
**private_key_metadata** | [**list[CsePrivateKeyMetadata]**](CsePrivateKeyMetadata.md) | Metadata for instances of this key pair&#x27;s private key. | [optional] 
**subject_email_addresses** | **list[str]** | Output only. The email address identities that are specified on the leaf certificate. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

