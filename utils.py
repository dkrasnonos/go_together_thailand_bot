import re


def is_number_field_valid(value):
    if value.isdigit() and len(value) == 1 and int(value) >= 0:
        return True
    else:
        return False


def is_phone_field_valid(value):
    if len(value) >= 6 and len(value) <= 16:
        pattern = r'^[\d\W]+$'
        if re.match(pattern, value):
            return True
        else:
            return False
    else:
        return False

def is_field_contains_link(value):
    pattern = r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)|([\w-]+(?:\.[\w-]+)+[^\s@]*(?:@[\w]+\.[\w]+\.[\w]+\.[\w]+)?)|(@[a-zA-Z0-9_]+)'
    if re.search(pattern, value):
        return True
    else:
        return False

def is_name_field_valid(value):
    if len(value) >= 2 and len(value) <= 30 and not is_field_contains_link(value):
        pattern = r'^[^\d\W]+$'
        if re.match(pattern, value):
            return True
        else:
            return False
    else:
        return False


def is_vehicle_field_valid(value):
    if len(value) >= 2 and len(value) <= 30 and not is_field_contains_link(value):
        return True
    else:
        return False

def is_place_field_valid(value):
    if len(value) >= 3 and len(value) <= 15 and not is_field_contains_link(value):
        return True
    else:
        return False

def is_comments_field_valid(value):
    if len(value) <= 30 and not is_field_contains_link(value):
        return True
    else:
        return False