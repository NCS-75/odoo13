{
    'name': "Project Stages",
    'name_vi_VN':"Giai Đoạn Dự Án",
    
    'summary': "Configure project stages",
    'summary_vi_VN': "Cấu hình giai đoạn dự án",
    
    'description': """
This is a simple application that changes the project form view for the users to organise stages specific to projects
    
Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng đơn giản này cho phép người dùng thay đổi giao diện dự án để tổ chức các giai đoạn cụ thể cho dự án
    
Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,
    'version' : '0.1',
    'author' : 'T.V.T Marine Automation (aka TVTMA)',
    'website': 'https://www.tvtmarine.com',
    'live_test_url': 'https://v13demo-int.erponline.vn',
    'support': 'support@ma.tvtmarine.com',
    'category' : 'Project',
    'sequence': 11,
    # any module necessary for this one to work correctly
    'depends': ['project'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/project_stages_view.xml',

    ],

    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
