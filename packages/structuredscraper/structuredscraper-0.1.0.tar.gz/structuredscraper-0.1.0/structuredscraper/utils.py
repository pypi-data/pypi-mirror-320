def get_string_matching_xpath(target: str):
    if '"' not in target:
        return f'(//*[string()="{target}"])[1]'
    elif "'" not in target:
        return f"(//*[string()='{target}'])[1]"
    else:
        # TODO: Figure out escaping for both single and double quotes in the expression.
        raise NotImplementedError(
            "XPath generation for string matching not implemented for strings with both single and double quotes"
        )
