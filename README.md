# Nautobot Golden Config Custom Compliance

This is a proof of concept implementation of a custom compliance function for [Nautobot Golden Config](https://github.com/nautobot/nautobot-plugin-golden-config). It can be used as it is written or used as a starting point to create your own custom compliance function.

## What it Does

This function serves 2 distinct purposes:

1. To ignore patterns that are not required to be in the `Intended` configuration, but that you have deemed as benign to be present in the `Actual` configuration.

> For example: you don't mind if someone adds descriptions to interfaces or access-list remarks, but you don't want to make them required.

2. To specify a pattern in both the `Actual` and `Intended` configurations as equivalent.

> For example: you use different IP's for logging per region, but they all match a specific pattern of `#.#.0.100`.

## Python Installation

Since the current implementation of Golden Config only allows for a single custom compliance function, each organization will be unique, and as such, this function is not consumable as a simple pip install. You will need to be responsible for adding the `custom_compliance.py` file as part of a python package that gets installed into your Nautobot instance(s) alongside Golden Config. For instance, you can bundle it as part of a [custom plugin](https://docs.nautobot.com/projects/core/en/stable/plugins/development/).

## Configuration

Once you have it installed and in the python path, you will need to add it to the `PLUGINS_CONFIG` section of your `nautobot_config.py` file as such:

```python
PLUGINS_CONFIG = {
    "nautobot_golden_config": {
        "get_custom_compliance": "custom_python_package.custom_compliance.custom_compliance"
    }
}
```

## Nautobot Custom Fields

This function utilizes 3 custom fields:

- `compliance_type`: The original type of compliance (i.e. `CLI` or `JSON`)
- `compliance_ignore`: A list of regex patterns to ignore in the `Actual` configuration that isn't in the `Intended`
- `compliance_equivalent`: A list of regex patterns that are equivalent in both the `Actual` and `Intended`

Each of these custom fields should be applied to the `nautobot_golden_config | compliance rule` content type.

### Compliance Type

This is the original compliance type that the compliance rule was using. 

Recommended options to create the custom field:

- Name: `Compliance Type`
- Slug: `compliance_type` (should auto populate)
- Type: `Selection`
- Content Types: `nautobot_golden_config | compliance rule`
- Custom Field Choices:
    - Value: `CLI`
    - Value: `JSON`

> This custom compliance function was written to still use the existing `CLI` or `JSON` compliance methods to prepare the `Missing` and `Extra` sections of the Compliance Rule and then modify the results. In order to use a custom compliance function, you would need to change the Compliance Rule to the type of `CUSTOM`. Because of this, we need to capture the original compliance method via a custom field.

### Compliance Ignore

This will be a list of regex patterns.

Recommended options to create the custom field:

- Name: `Compliance Ignore`
- Slug: `compliance_ignore` (should auto populate)
- Type: `JSON`
- Content Types: `nautobot_golden_config | compliance rule`

### Compliance Equivalent

This will be a list of regex patterns.

Recommended options to create the custom field:

- Name: `Compliance Equivalent`
- Slug: `compliance_equivalent` (should auto populate)
- Type: `JSON`
- Content Types: `nautobot_golden_config | compliance rule`

## Activating the Custom Compliance

Once you have create the 3 associated Custom Fields, you will need to edit the Compliance Rule that you would like the function to run on.

- (Required) Config Type: Change to `CUSTOM`
- (Required) Compliance Type: Change to either `CLI` or `JSON`
- (Optional) Compliance Ignore: Add a list of patterns (see example below)
- (Optional) Compliance Equivalent: Add a list of patterns (see example below)

Example list of ignore patterns:

```python
[
    "^interface \\S+\n description .*$",
    "^ip access-list extended \\S+\n remark .*$",
]
```

Example list of equivalent patterns:

```python
[
    "^logging host [0-9]{1,3}\.[0-9]{1,3}\.0\.100 .*$",
    "^username \\S+ privilege 15 password 0 \\S+$",
]
```

## Additional Information

For more information, feel free to see the [official documentation on custom compliance functions](https://docs.nautobot.com/projects/golden-config/en/latest/user/app_feature_compliancecustom/).
