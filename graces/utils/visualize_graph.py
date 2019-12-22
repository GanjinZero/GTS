def float_format(x):
    """ 
    0.646788 -> 0.64
    12.64657 -> 12.6
    126.4675 -> 126.
    1237.151 -> 1237
    12375.58 -> +inf
    """
    if x < 10: 
        return format(x, '0.2f')
    if x < 100:
        return format(x, '0.1f')
    if x < 1000:
        return str(round(x)) + "." 
    return '+inf'

def graph_information(s, w):
    """
    增-0.24-强-0.76-的-0.35-坐-0.43-标
    """
    m_diag = [float_format(x) for x in w]

    line = ''
    for i in range(len(s)-1):
        line += s[i] + "-" + m_diag[i] + "-"
    line += s[-1]
    return line

