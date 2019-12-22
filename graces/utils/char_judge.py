def is_chinese(ch):
    if u'\u4e00' <= ch <= u'\u9fa5' or 'a' <= ch <= 'z' or 'A' <= ch <= 'Z':
        return True
    return False

def is_chinese_not_english(ch):
    if u'\u4e00' <= ch <= u'\u9fa5':
        return True
    return False

def is_alphabet(ch):
    if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or '0' <= ch <= '9':
        return True
    return False

