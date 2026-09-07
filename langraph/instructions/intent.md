# Intent Instructions

Classify the customer request into exactly one intent:

- `refund`: The customer wants money returned for an order.
- `cancel`: The customer wants to cancel an order.
- `status`: The customer asks where an order is or asks for delivery status.
- `faq`: Anything that does not match refund, cancel, or status.

Return only the structured intent value.
