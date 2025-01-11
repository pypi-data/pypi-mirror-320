import decimal

def round_down(value, decimals=0):
    with decimal.localcontext() as ctx:
        d = decimal.Decimal(value)
        ctx.rounding = decimal.ROUND_DOWN
        return round(d, decimals)
