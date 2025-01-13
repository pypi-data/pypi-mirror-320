def render_template(template: str, **kwargs):
    """
    Рендерить шаблон з параметрами.

    Args:
        template (str): Шаблон тексту.
        kwargs: Параметри для вставки.

    Returns:
        str: Згенерований текст.
    """
    return template.format(**kwargs)
