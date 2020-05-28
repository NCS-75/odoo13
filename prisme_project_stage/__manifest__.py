# -*- coding: utf-8 -*-
###########################################################################
#
#    Prisme Solutions Informatique SA
#    Copyright (c) 2016 Prisme Solutions Informatique SA <http://prisme.ch>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#    You should have received a copy of the GNU Affero General Public Lic
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Project ID:    OERP-004-05
#
#    Modifications:
#
#
##########################################################################
{
    'name' : 'Prisme Project Stage',
    'version' : '28-05-2020 14:22',
    'author' : 'Prisme Solutions Informatique SA',
    'sequence': 15,
    'category': 'Project',
    'website' : 'http://www.prisme.ch',
    'summary' : 'Add Stage to Project',
    'description' : """ """,
    'depends': [
        "project"
    ],
    'data': [
        'views/project_view.xml',
    ],

    'installable': True,
    'application': True,
}
