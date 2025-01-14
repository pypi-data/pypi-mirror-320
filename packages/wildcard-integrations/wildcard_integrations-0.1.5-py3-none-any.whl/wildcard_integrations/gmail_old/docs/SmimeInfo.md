# SmimeInfo

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**encrypted_key_password** | **str** | Encrypted key password, when key is encrypted. | [optional] 
**expiration** | **str** | When the certificate expires (in milliseconds since epoch). | [optional] 
**id** | **str** | The immutable ID for the SmimeInfo. | [optional] 
**is_default** | **bool** | Whether this SmimeInfo is the default one for this user&#x27;s send-as address. | [optional] 
**issuer_cn** | **str** | The S/MIME certificate issuer&#x27;s common name. | [optional] 
**pem** | **str** | PEM formatted X509 concatenated certificate string (standard base64 encoding). Format used for returning key, which includes public key as well as certificate chain (not private key). | [optional] 
**pkcs12** | **str** | PKCS#12 format containing a single private/public key pair and certificate chain. This format is only accepted from client for creating a new SmimeInfo and is never returned, because the private key is not intended to be exported. PKCS#12 may be encrypted, in which case encryptedKeyPassword should be set appropriately. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

