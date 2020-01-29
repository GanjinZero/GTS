def is_chinese(ch):
    if u'\u4e00' <= ch <= u'\u9fa5' or 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or u'\uff41' <= ch <= u'\uff5a' or u'\uff21' <= ch <= u'\uff3a':
        return True
    return False

def is_chinese_not_english(ch):
    if u'\u4e00' <= ch <= u'\u9fa5':
        return True
    return False

def is_english_or_number(ch):
    if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or '0' <= ch <= '9':
        return True
    return False

def is_alphabet(ch):
    if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or '0' <= ch <= '9' or u'\uff41' <= ch <= u'\uff5a' or u'\uff21' <= ch <= u'\uff3a' or u'\uff10' <= ch <= u'\uff19':
        return True
    return False

