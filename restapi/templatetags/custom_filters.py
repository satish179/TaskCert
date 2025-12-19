from django import template

register = template.Library()

@register.filter
def to_chr(value):
    try:
        return chr(int(value))
    except (ValueError, TypeError):
        return ''


@register.filter
def dict_get(mapping, key):
    """Safely get mapping[key] in templates."""
    if mapping is None:
        return None
    try:
        return mapping.get(key)
    except AttributeError:
        return None


@register.filter
def has_group(user, group_name: str) -> bool:
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    try:
        return user.groups.filter(name=group_name).exists()
    except Exception:
        return False