# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template

from bootstrap3.forms import render_form

from django.conf import settings



register = template.Library()

@register.inclusion_tag('brutalform/formset.html')
def brutalform(form, level, collapsible=None, **kwargs):
    if hasattr(form, 'inlineformsets') and form.inlineformsets and collapsible is None:
        collapsible = True
    else:
        collapsible = False
    layout = 'horizontal' if level==0 else 'inline'
    if hasattr(form, 'layout'):
        layout = form.layout
    return {
        'form': form,
        'level': level+1,
        'layout': layout,
        'counter': kwargs['counter'],
        'collapsible': collapsible
    }