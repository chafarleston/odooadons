# -*- coding: utf-8 -*-
{
    'name': "FacturaloPeru API Invoice",
    'category': "web",
    'version': "11.0.1.0.0",
    'author': "FacturaloPeru",
    'website': "www.facturaloperu.com",
    'summary': "Módulo que se integra con facturación",

    'description': """
# FacturaloPeru | Odoo | Módulo de Facturación

_Módulo desarrollado para Odoo 11.0 con conexion a la API del Facturador PRO_


### Pre-requisitos 📋

Extraer de la carpeta dependencias los módulos de odoope_einvoice_base y odoope_ruc_validation y colocarlas dentro de /addons ya que estos son dependecias del módulo desarrollado


## Instalación AWS + Docker + Odoo 11 + Postgresql

Hemos realizado una instalación sobre la plataforma de Amazon Web Service y la hemos documentado, puede observar el proceso [aqui](https://docs.google.com/document/d/16Q54Lw-1km660TZOWw5EICqxkdTaZMSYk9ddoUA4E8I/edit?usp=sharing)

## Configuración 🔧

Puede visitar el siguiente enlace para ver el [manual de instalación y configuración](https://docs.google.com/document/d/1JB6krhzYcs1SkhIefsErRNmvaDBPrf31ZtMrSs5Iwrc/edit?usp=sharing)

## Funcionalidad ⚙️

Puede visitar el siguiente enlace para ver la [guia de usuario](https://docs.google.com/document/d/1qP2u0Tu-nwF78qRYzt3oZrp8B9YUtMvqEUFv5Z-oixA/edit?usp=sharing)

### Facturador PRO

* Para complementar funcionalidades puede acceder a Facturación > Comprobantes; si se le muestra una pagina con la alerta de "Parámetro no encontrado", dirigirse con acceso administrador a Ajustes > Parámetros > Parámetros del sistema > Crear
    * Ingresar clave: facturaloperu_api_invoice.api_url
    * Ingresar Valor: URL de su Facturador PRO, ejemplo: "demo.facturaloperuonline.com/documents"

## Autor

**FacturaloPeru** [facturaloperu.com](http://facturaloperu.com)
    """,

    'depends': [
        'sale_management',
        'odoope_einvoice_base',
        'odoope_ruc_validation'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/api_url.xml',
        'views/data.xml',
        'views/views.xml',
        'views/serie_view.xml',
        'views/res_company.xml',
        'views/templates.xml',
        'reports/report.xml',
    ],
    'license': 'AGPL-3',
    'auto_install': False,
    'installable': True,
    'web_preload': True,
}