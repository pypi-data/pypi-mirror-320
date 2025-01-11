from .toj.reconciliation import XlsxReconciliation


# 读取xlsx为数据源，并把结果输出到xlsx
def xlsx_reconciliation(rules):
    xls = XlsxReconciliation(rules)
    return xls.handle()
