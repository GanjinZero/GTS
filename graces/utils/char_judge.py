def is_chinese(char):
    if u'\u4e00' <= char <= u'\u9fa5' or 'a' <= char <= 'z' or 'A' <= char <= 'Z':
        return True
    return False

def is_alphabet(ch):
    if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or '0' <= ch <= '9':
        return True
    return False

