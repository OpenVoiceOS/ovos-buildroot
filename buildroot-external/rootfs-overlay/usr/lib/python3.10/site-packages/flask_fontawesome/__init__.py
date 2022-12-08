# -*- coding: utf-8 -*-
'''
flask_fontawesome
-----------------

This moudle provides helpers to quickly add FontAwesome resources to your Flask app.

:license: MIT / Apache 2.0 (seen LICENSE-MIT and LICENSE-APACHE for details)
'''

from flask import Flask, Blueprint, url_for, Markup, current_app

FONTAWESOME_VERSION = '5.14.0'
__version__ = '0.1.5'


def fontawesome_html() -> Markup:
    '''
    Returns :class:`~flask.Markup` of all the requested FontAwesome resources. This can be embedded
    in your Jinja templates to add FontAwesome to your site.
    '''
    if current_app.config['FONTAWESOME_SERVE_LOCAL']:
        return current_app.extensions['fontawesome']._static.resources_html()
    else:
        return current_app.extensions['fontawesome']._use_fa.resources_html()


def fontawesome_js() -> Markup:
    '''
    Returns :class:`~flask.Markup` of the JS FontAwesome resources.
    '''
    if current_app.config['FONTAWESOME_SERVE_LOCAL']:
        return current_app.extensions['fontawesome']._static.js_html()
    else:
        return current_app.extensions['fontawesome']._use_fa.js_html()


def fontawesome_css() -> Markup:
    '''
    Returns :class`~flask.Markup` of the CSS FontAwesome resources.
    '''
    if current_app.config['FONTAWESOME_SERVE_LOCAL']:
        return current_app.extensions['fontawesome']._static.css_html()
    else:
        return current_app.extensions['fontawesome']._use_fa.css_html()


class Cdn(object):

    def resources_html(self) -> Markup:
        return self.css_html() + self.js_html()

    def css_html(self) -> Markup:
        raise NotImplementedError()

    def js_html(self) -> Markup:
        raise NotImplementedError()

    def _check_type(self) -> None:
        typ = current_app.config['FONTAWESOME_TYPE']
        if typ not in ['webfont/css', 'svg/js']:
            raise ValueError('Illegal parameter for FONTAWESOME_TYPE: {}'.format(typ))


class StaticCdn(Cdn):

    def css_html(self) -> Markup:
        self._check_type()
        if current_app.config['FONTAWESOME_TYPE'] == 'webfont/css':
            return self.__gen_html(self.__css)
        else:
            return Markup()

    def js_html(self) -> Markup:
        self._check_type()
        if current_app.config['FONTAWESOME_TYPE'] == 'svg/js':
            return self.__gen_html(self.__js)
        else:
            return Markup()

    def __gen_html(self, func) -> Markup:
        use_min = current_app.config['FONTAWESOME_USE_MINIFIED']
        html = []

        styles = current_app.config['FONTAWESOME_STYLES']
        if 'all' in styles:
            html.append(func('all', use_min))
        else:
            html.append(func('fontawesome', use_min))
            for style in styles:
                html.append(func(style, use_min))

        if current_app.config['FONTAWESOME_INCLUDE_V4_SHIMS']:
            html.append(func('v4-shims', use_min))

        return Markup('\n'.join(html))

    def __url(self, resource: str) -> str:
        params = {'filename': resource}
        if current_app.config['FONTAWESOME_QUERYSTRING_REVVING']:
            params['version'] = FONTAWESOME_VERSION
        return url_for('fontawesome.static', **params)

    def __css(self, style: str, use_min: bool) -> str:
        min_str = '.min' if use_min else ''
        resource = 'css/{}{}.css'.format(style, min_str)
        return '<link href="{}" rel="stylesheet">'.format(self.__url(resource))

    def __js(self, style: str, use_min: bool) -> str:
        min_str = '.min' if use_min else ''
        resource = 'js/{}{}.js'.format(style, min_str)
        return '<script defer src="{}" rel="stylesheet"></script>'.format(self.__url(resource))


class UseFontAwesomeComCdn(Cdn):

    __URL_BASE = 'https://use.fontawesome.com/releases/v{}'.format(FONTAWESOME_VERSION)

    __INTEGRITY_MAP = {
        'webfont/css': {
            'all': 'sha384-HzLeBuhoNPvSl5KYnjx0BT+WB0QEEqLprO+NBkkk5gbc67FTaL7XIGa2w1L0Xbgc',
            'brands': 'sha384-MiOGyNsVTeSVUjE9q/52dpdZjrr7yQAjVRUs23Bir5NhrTq0YA0rny4u/qe4dxNj',
            'fontawesome': (
                'sha384-PRy/NDAXVTUcXlWA3voA+JO/UMtzWgsYuwMxjuu6DfFPgzJpciUiPwgsvp48fl3p'),
            'regular': 'sha384-e46AbGhCSICtPh8xpc35ZioOrHg2PGsH1Bpy/vyr9AhEMVhttzxc+2GSMSP+Y60P',
            'solid': 'sha384-TN9eFVoW87zV3Q7PfVXNZFuCwsmMwkuOTOUsyESfMS9uwDTf7yrxXH78rsXT3xf0',
            'v4-shims': 'sha384-9aKO2QU3KETrRCCXFbhLK16iRd15nC+OYEmpVb54jY8/CEXz/GVRsnM73wcbYw+m',
        },
        'svg/js': {
            'all': 'sha384-3Nqiqht3ZZEO8FKj7GR1upiI385J92VwWNLj+FqHxtLYxd9l+WYpeqSOrLh0T12c',
            'brands': 'sha384-V7gsTxvUZaeC6NAsCa24o3WvPOXwSsUM8/SBgy+fxlzWL3xEGXHsAv2E3UO5zKcZ',
            'fontawesome': (
                'sha384-DNo9bmYZCHLtp0n0l0XA2UsoRHX1nx38aRP+p9yoP5A8kVTfeWG3aySMOq5FD/v3'),
            'regular': 'sha384-zHXcIX0meH+eFgqCa9QdLtYfc+0p7KcF4fVB+gMVFjV6rzYv+LxSIuF5i2eGVDlt',
            'solid': 'sha384-4RG3cEPIlCBy6VNzxM9ZoEwZW+65ed5JDOfaJAnQqwV6ha/jZDJTXjFmvjFM4bk4',
            'v4-shims': 'sha384-g+ezV6Pq6549QkJkkz2wmW/wpazNaliTdSg/HX4bKsQ7S8cfyMOiyAfzfWPtlVR9',
        },
    }

    def css_html(self) -> Markup:
        self._check_type()
        if current_app.config['FONTAWESOME_TYPE'] == 'webfont/css':
            return self.__gen_html(self.__css, 'webfont/css')
        else:
            return Markup()

    def js_html(self) -> Markup:
        self._check_type()
        if current_app.config['FONTAWESOME_TYPE'] == 'svg/js':
            return self.__gen_html(self.__js, 'svg/js')
        else:
            return Markup()

    def __gen_html(self, func, typ) -> Markup:
        typ = self.__INTEGRITY_MAP[typ]
        html = []

        styles = current_app.config['FONTAWESOME_STYLES']
        if 'all' in styles:
            integrity = typ['all']
            html.append(func('all', integrity))
        else:
            html.append(func('fontawesome', typ['fontawesome']))
            for style in styles:
                integrity = typ.get(style, None)
                if integrity is None:
                    raise ValueError('Unknown style: {}'.format(style))
                html.append(func(style, integrity))

        if current_app.config['FONTAWESOME_INCLUDE_V4_SHIMS']:
            integrity = typ['v4-shims']
            html.append(func('v4-shims', integrity))

        return Markup('\n'.join(html))

    def __css(self, style: str, integrity: str) -> str:
        url = '{}/css/{}.css'.format(self.__URL_BASE, style)
        return ('<link rel="stylesheet" href="{}" integrity="{}" crossorigin="anonymous">'
                .format(url, integrity))

    def __js(self, style: str, integrity: str) -> str:
        url = '{}/js/{}.js'.format(self.__URL_BASE, style)
        return ('<script defer src="{}" integrity="{}" crossorigin="anonymous"></script>'
                .format(url, integrity))


class FontAwesome(object):

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

        self._static = StaticCdn()
        self._use_fa = UseFontAwesomeComCdn()

    def init_app(self, app: Flask) -> None:
        if not hasattr(app, 'extensions'):
            app.extensions = {}

        app.extensions['fontawesome'] = self

        app.config.setdefault('FONTAWESOME_INCLUDE_V4_SHIMS', False)
        app.config.setdefault('FONTAWESOME_QUERYSTRING_REVVING', True)
        app.config.setdefault('FONTAWESOME_SERVE_LOCAL', True)
        app.config.setdefault('FONTAWESOME_STYLES', ['solid'])
        app.config.setdefault('FONTAWESOME_TYPE', 'webfont/css')
        app.config.setdefault('FONTAWESOME_USE_MINIFIED', True)

        blueprint = Blueprint(
            'fontawesome',
            __name__,
            static_folder='static',
            static_url_path=app.static_url_path + '/fontawesome')

        app.jinja_env.globals['fontawesome_html'] = fontawesome_html
        app.jinja_env.globals['fontawesome_css'] = fontawesome_css
        app.jinja_env.globals['fontawesome_js'] = fontawesome_js
        app.register_blueprint(blueprint)
