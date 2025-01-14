from hanziconv import HanziConv


def is_chinese_char(s) -> bool:
    if "\u4e00" <= s <= "\u9fa5":
        return True
    else:
        return False


def str_contains_chinese(text) -> bool:
    if len([1 for c in text if is_chinese_char(c)]) > 0:
        return True
    return False


def is_english_char(c) -> bool:
    # 判断字符是否为英文字母（包括大小写）
    if "a" <= c <= "z" or "A" <= c <= "Z":
        return True
    else:
        return False


def str_contains_english(text) -> bool:
    # 判断字符串中是否包含至少一个英文字母
    if len([1 for c in text if is_english_char(c)]) > 0:
        return True
    return False


def is_number(s) -> bool:
    if "\u0030" <= s <= "\u0039":
        return True
    else:
        return False


def is_alphabet(s) -> bool:
    if ("\u0041" <= s <= "\u005a") or ("\u0061" <= s <= "\u007a"):
        return True
    else:
        return False


def full_to_half_width(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xFEE0
        if (
            inside_code < 0x0020 or inside_code > 0x7E
        ):  # 转完之后不是半角字符返回原来的字符
            rstring += uchar
        else:
            rstring += chr(inside_code)
    return rstring


def traditional_to_simplified(line):
    """繁体转简体"""
    return HanziConv.toSimplified(line)
