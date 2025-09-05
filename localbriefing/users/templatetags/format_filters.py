from django import template

register = template.Library()

@register.filter
def format_view_count(value):
    """조회수를 1.5천회, 2.3만회 형식으로 포맷팅"""
    try:
        count = int(value)
        if count >= 100000000:  # 1억 이상
            return f"{count/100000000:.1f}억회"
        elif count >= 10000:  # 1만 이상
            return f"{count/10000:.1f}만회"
        elif count >= 1000:  # 1천 이상
            return f"{count/1000:.1f}천회"
        else:
            return f"{count}회"
    except (ValueError, TypeError):
        return "0회"