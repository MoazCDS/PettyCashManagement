{
    'name' : "Petty Cash Management",
    'author' : "Moaz Elbahr",
    'category': '',
    'version': '17.0.0.1.0',
    'depends': ['base', 'hr', 'account', 'account_accountant'],
    'data': [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/base_menu.xml",
        "views/petty_cash_request_view.xml",
        "views/petty_cash_reconciliation_view.xml",
        "reports/petty_cash_report.xml",
    ],
    'application': True,
}