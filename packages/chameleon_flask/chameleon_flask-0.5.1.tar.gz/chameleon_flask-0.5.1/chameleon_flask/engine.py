import inspect
import os
from functools import wraps
from typing import Optional, Union, Callable, Any

import flask
from chameleon import PageTemplateLoader, PageTemplate

from chameleon_flask.exceptions import FlaskChameleonException, FlaskChameleonNotFoundException

__templates: Optional[PageTemplateLoader] = None
template_path: Optional[str] = None

response_classes = {
    "<class 'flask.wrappers.Response'>",
    "<class 'quart.wrappers.response.Response'>",
    "<class 'flask.Response'>",
    "<class 'quart.response.Response'>",
    "<class 'quart.Response'>",
}


def global_init(template_folder: str, auto_reload=False, cache_init=True):
    global __templates, template_path

    if __templates and cache_init:
        return

    if not template_folder:
        msg = 'The template_folder must be specified.'
        raise FlaskChameleonException(msg)

    if not os.path.isdir(template_folder):
        msg = f"The specified template folder must be a folder, it's not: {template_folder}"
        raise FlaskChameleonException(msg)

    template_path = template_folder
    __templates = PageTemplateLoader(template_folder, auto_reload=auto_reload)


def clear():
    global __templates, template_path
    __templates = None
    template_path = None


def render(template_file: str, **template_data: dict) -> str:
    if not __templates:
        raise FlaskChameleonException('You must call global_init() before rendering templates.')

    page: PageTemplate = __templates[template_file]
    return page.render(encoding='utf-8', **template_data)


def response(template_file: str, content_type='text/html', status_code=200, **template_data) -> flask.Response:
    html = render(template_file, **template_data)
    return flask.Response(response=html, content_type=content_type, status=status_code)


def template(
    template_file: Optional[Union[Callable, str]] = None, content_type: str = 'text/html', status_code: int = 200
):
    """
    Decorate a FastAPI view method to render an HTML response.

    :param status_code: Default status code for responses. For example 201 on a POST/create action.
    :param str template_file: Optional, the Chameleon template file (path relative to template folder, *.pt).
    :param str content_type: The mimetype response (defaults to text/html).
    :return: Decorator to be consumed by FastAPI
    """

    wrapped_function = None
    if callable(template_file):
        wrapped_function = template_file
        template_file = None

    def response_inner(f):
        nonlocal template_file
        global template_path

        if not template_path:
            template_path = 'templates'

        if not template_file:
            # Use the default naming scheme: template_folder/module_name/function_name.pt
            module = f.__module__
            if '.' in module:
                module = module.split('.')[-1]
            view = f.__name__
            template_file = f'{module}/{view}.html'

            if not os.path.exists(os.path.join(template_path, template_file)):
                template_file = f'{module}/{view}.pt'

        @wraps(f)
        def sync_view_method(*args, **kwargs) -> flask.Response:
            try:
                response_val = f(*args, **kwargs)
                return __render_response(template_file, response_val, content_type, status_code)
            except FlaskChameleonNotFoundException as nfe:
                return __render_response(nfe.template_file, {}, 'text/html', 404)

        @wraps(f)
        async def async_view_method(*args, **kwargs) -> flask.Response:
            try:
                response_val = await f(*args, **kwargs)
                return __render_response(template_file, response_val, content_type, status_code)
            except FlaskChameleonNotFoundException as nfe:
                return __render_response(nfe.template_file, {}, 'text/html', 404)

        if inspect.iscoroutinefunction(f):
            return async_view_method
        else:
            return sync_view_method

    return response_inner(wrapped_function) if wrapped_function else response_inner


def __render_response(
    template_file: str, response_val: Any, content_type: str, status_code: int = 200
) -> flask.Response:
    val_type = str(type(response_val))
    if val_type in response_classes:
        return response_val

    if template_file and not isinstance(response_val, dict):
        msg = f'Invalid return type {type(response_val)}, we expected a dict or flask.Response as the return value.'
        raise FlaskChameleonException(msg)

    model = response_val

    html = render(template_file, **model)
    return flask.Response(response=html, content_type=content_type, status=status_code)


def not_found(four04template_file: str = 'errors/404.pt'):
    msg = 'The URL resulted in a 404 response.'

    if four04template_file and four04template_file.strip():
        raise FlaskChameleonNotFoundException(msg, four04template_file)
    else:
        raise FlaskChameleonNotFoundException(msg)
