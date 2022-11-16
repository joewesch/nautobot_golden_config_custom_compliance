import re


from nautobot_golden_config.models import FUNC_MAPPER


def _compliance_ignore(obj, compliance_details):
    ignored_lines = []
    for ignore_regex in obj.rule.custom_field_data.get("compliance_ignore"):
        # Matches on `\n` before, after, or neither
        sub_regex = f"\n{ignore_regex}|{ignore_regex}\n?"
        search_extra = re.search(ignore_regex, compliance_details["extra"])
        if search_extra:
            ignored_lines.append(search_extra[0])
            compliance_details["extra"] = re.sub(sub_regex, "", compliance_details["extra"])

    return ignored_lines


def _compliance_equivalent(obj, compliance_details):
    for equivalent_regex in obj.rule.custom_field_data.get("compliance_equivalent"):
        search_missing = re.search(equivalent_regex, compliance_details["missing"])
        search_extra = re.search(equivalent_regex, compliance_details["extra"])
        if search_missing and search_extra:
            # Matches on `\n` before, after, or neither
            sub_regex = f"\n{equivalent_regex}|{equivalent_regex}\n?"
            compliance_details["missing"] = re.sub(sub_regex, "", compliance_details["missing"])
            compliance_details["extra"] = re.sub(sub_regex, "", compliance_details["extra"])


def custom_compliance(obj):
    compliance_details = {
        "compliance": False,
        "compliance_int": 0,
        "ordered": 0,
        "missing": "",
        "extra": "",
    }
    compliance_type = obj.rule.custom_field_data.get("compliance_type")
    if not compliance_type:
        # Shortcut to bypass custom logic if missing required custom field
        compliance_details["missing"] = "Missing `compliance_type` custom field"
        return compliance_details

    # Process the original compliance
    if compliance_type not in FUNC_MAPPER or compliance_type == "custom":
        # Shortcut to bypass custom logic if custom field doesn't match original compliance type
        compliance_details["missing"] = f"Compliance type '{compliance_type}' not valid"
        return compliance_details

    compliance_method = FUNC_MAPPER[compliance_type]
    compliance_details = compliance_method(obj)
    if compliance_details["compliance"]:
        # Shortcut to bypass custom logic if already compliant
        return compliance_details

    # Post-process any lines to ignore
    ignored_lines = ""
    compliance_ignore = obj.rule.custom_field_data.get("compliance_ignore")
    if compliance_ignore and isinstance(compliance_ignore, list):
        ignored_lines = _compliance_ignore(obj, compliance_details)

    # Post-process any lines that are equivalent
    compliance_equivalent = obj.rule.custom_field_data.get("compliance_equivalent")
    if compliance_equivalent and isinstance(compliance_equivalent, list):
        _compliance_equivalent(obj, compliance_details)

    # Add comments for any lines that were ignored
    ignored_output = "Ignored via Compliance Ignore custom field:\n" + "\n".join(ignored_lines) if ignored_lines else ""

    # Check if there are any missing or extra left after post-processing
    if not any((compliance_details["missing"], compliance_details["extra"])):
        compliance_details["compliance_int"] = 1
        compliance_details["compliance"] = True
    if ignored_output:
        if compliance_details["extra"]:
            ignored_output = f"\n\n{ignored_output}"
        compliance_details["extra"] += ignored_output

    return compliance_details
