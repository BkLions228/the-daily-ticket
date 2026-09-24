package main

import rego.v1

required_public_access_settings := [
    "block_public_acls",
    "block_public_policy",
    "ignore_public_acls",
    "restrict_public_buckets",
]

deny contains message if {
    some change in input.resource_changes
    change.type == "aws_s3_bucket_public_access_block"

    after := change.change.after
    some setting in required_public_access_settings


    after[setting] != true

    message := sprintf(
        "%s must set %s to true",
        [change.address, setting],
    )
}

deny contains message if {
    some change in input.resource_changes
    change.type == "aws_s3_bucket_server_side_encryption_configuration"


    algorithm := change.change.after.rule[0].apply_server_side_encryption_by_default[0].sse_algorithm
    algorithm != "aws:kms"

    message := sprintf(
        "%s must use AWS KMS encryption; found %s",
        [change.address, algorithm],
    )
}