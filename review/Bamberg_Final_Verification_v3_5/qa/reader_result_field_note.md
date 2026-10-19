# Reader-result field qualification

The inherited browser harness returns `fragment_order_unchanged: book === 11`. It is an indicator that the additional Book XI physical/interpolation comparison was executed, not a failed-order assertion for other books. Thus `false` on a non-XI view means NOT APPLICABLE. All Book XI views execute and pass the explicit DOM identity/order comparison; structural marker order for every affected book is independently checked by the XML preservation suite. The original result JSON is preserved without recoding these fields.
