# DraftMessage

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**history_id** | **str** | The ID of the last history record that modified this message. | [optional] 
**id** | **str** | The immutable ID of the message. | [optional] 
**internal_date** | **str** | The internal message creation timestamp (epoch ms), which determines ordering in the inbox. For normal SMTP-received email, this represents the time the message was originally accepted by Google, which is more reliable than the &#x60;Date&#x60; header. However, for API-migrated mail, it can be configured by client to be based on the &#x60;Date&#x60; header. | [optional] 
**label_ids** | **list[str]** | List of IDs of labels applied to this message. | [optional] 
**payload** | [**MessagePart**](MessagePart.md) |  | [optional] 
**raw** | **str** | REQUIRED. Always populate this field. Make this entire email message in an RFC 2822 formatted string and base64url encoded string. Returned in &#x60;messages.get&#x60; and &#x60;drafts.get&#x60; responses when the &#x60;format&#x3D;byte&#x60; parameter is supplied. When creating a draft, the complete message needs to be passed in the raw parameter, see the example: From: John Doe &lt;jdoe@machine.example&gt; To: Mary Smith &lt;mary@example.net&gt; Subject: Saying Hello  Date [optional]: Fri, 21 Nov 1997 09:55:06 -0600 Message-ID [optional]: &lt;1234@local.machine.example&gt; ...&lt;other RFC 2822 headers&gt; ...  Hi Mary,  This is the body of the message.  Regards, John Doe  If you are replying to an existing message, make sure to include the &#x60;References&#x60; and &#x60;In-Reply-To&#x60; headers. See the example below: From: John Doe &lt;jdoe@machine.example&gt; To: Mary Smith &lt;mary@example.net&gt; Subject: Re: Saying Hello  References: &lt;CADsZLRxZDUGn4Frx80qe2_bE5H5bQhgcqGk&#x3D;GwFN9gs7Z_8oZw@mail.gmail.com&gt; &lt;CADsZLRyzVPLRQuTthGSHKMCXL7Ora1jNW7h0jvoNgR+hU59BYg@mail.gmail.com&gt; &lt;CADsZLRwQWzLB-uq4_4G2E64NX9G6grn0cEeO0L&#x3D;avY7ajzuAFg@mail.gmail.com&gt; In-Reply-To: &lt;CADsZLRwQWzLB-uq4_4G2E64NX9G6grn0cEeO0L&#x3D;avY7ajzuAFg@mail.gmail.com&gt; ...&lt;other RFC 2822 headers&gt; ...  Hi Mary,  This is the body of the message.  Regards, John Doe  | 
**size_estimate** | **int** | Estimated size in bytes of the message. | [optional] 
**snippet** | **str** | A short part of the message text. | [optional] 
**thread_id** | **str** | REQUIRED if replying to an existing message. The ID of the thread the message belongs to. To add a message or draft to a thread, the following criteria must be met: 1. The requested &#x60;threadId&#x60; must be specified on the &#x60;Message&#x60; or &#x60;Draft.Message&#x60; you supply with your request. 2. The &#x60;References&#x60; and &#x60;In-Reply-To&#x60; headers must be set in compliance with the [RFC 2822](https://tools.ietf.org/html/rfc2822) standard. 3. The &#x60;Subject&#x60; headers must match.  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

