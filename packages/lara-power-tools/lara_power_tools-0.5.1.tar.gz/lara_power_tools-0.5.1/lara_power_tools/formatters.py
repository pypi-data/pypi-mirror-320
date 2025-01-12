def format_international_phone(phone_number: str) -> str:
    """
    Ensures the phone number includes a country prefix. If no prefix is provided,
    add '+1' as the default country code.

    :param phone_number: The input phone number as a string.
    :return: The formatted phone number with a country prefix.
    """
    if not phone_number.startswith("+"):
        return "+1" + phone_number
    return phone_number
