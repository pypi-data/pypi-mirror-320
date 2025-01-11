# Standard Library
from itertools import chain

# Third party
from django import forms
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext
from mptt.forms import TreeNodeMultipleChoiceField

# Local application / specific library imports
from kapt_catalog.models.characteristic import Characteristic


class CharacteristicsMultipleChoiceField(TreeNodeMultipleChoiceField):
    def __init__(self, queryset, *args, **kwargs):
        if "widget" not in kwargs:
            self.widget = CharacteristicsCheckboxSelectMultiple
        super().__init__(queryset, *args, **kwargs)
        self.create_choices_from_queryset()

    def create_choices_from_queryset(self):
        choices = list()
        for characteristic in self.queryset:
            choices.append(
                [
                    self.prepare_value(characteristic),
                    self.label_from_instance(characteristic),
                    int(characteristic.level),
                    characteristic.is_category,
                    characteristic.in_search_engine,
                ]
            )
        self.choices = choices


class CharacteristicsCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and "id" in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        # Normalize to strings
        str_values = {force_text(v) for v in value}

        checkbox_final_attrs = final_attrs
        if "class" in checkbox_final_attrs:
            checkbox_final_attrs["class"] += " CharacteristicsCheckbox"
        else:
            checkbox_final_attrs["class"] = "CharacteristicsCheckbox"

        choices_list = list(enumerate(chain(self.choices, choices)))
        init_level = choices_list[0][1][2]
        output = self.create_dom(
            choices_list,
            init_level,
            checkbox_final_attrs,
            str_values,
            has_id,
            final_attrs,
            attrs,
            name,
        )
        return mark_safe(output)

    def create_dom(
        self,
        choices_list,
        init_level,
        checkbox_final_attrs,
        str_values,
        has_id,
        final_attrs,
        attrs,
        name,
        loop_init=0,
    ):
        sub_choices = []
        inner_html = "<ul>%s</ul>"
        choices_html = ""
        loop_number = loop_init
        for choice in choices_list:
            option_value, option_label, level, is_category, in_search_engine = choice[1]
            if level > init_level:
                sub_choices.append(choice)
            elif level == init_level:
                if len(sub_choices) > 0:
                    sub_init_level = sub_choices[0][1][2]
                    choices_html += self.create_dom(
                        sub_choices,
                        sub_init_level,
                        checkbox_final_attrs,
                        str_values,
                        has_id,
                        final_attrs,
                        attrs,
                        name,
                        loop_number,
                    )
                    choices_html += "</li>"
                    sub_choices = []
                elif loop_number != loop_init:
                    choices_html += "</li>"

                if has_id:
                    final_attrs = dict(
                        final_attrs, id="{}_{}".format(attrs["id"], (loop_number + 1))
                    )
                    label_for = format_html(' for="{0}"', final_attrs["id"])
                else:
                    label_for = ""

                option_label = force_text(option_label)

                if is_category:
                    choices_html += format_html("<li><b>%s</b>" % option_label)
                else:
                    cb = forms.CheckboxInput(
                        checkbox_final_attrs,
                        check_test=lambda value: value in str_values,
                    )
                    option_value = force_text(option_value)
                    rendered_cb = cb.render(name, option_value)
                    choices_html += format_html(
                        "<li><label%s>%s %s</label>"
                        % (label_for, rendered_cb, option_label)
                    )
            loop_number += 1
        if len(sub_choices) > 0:
            sub_init_level = sub_choices[0][1][2]
            choices_html += self.create_dom(
                sub_choices,
                sub_init_level,
                checkbox_final_attrs,
                str_values,
                has_id,
                final_attrs,
                attrs,
                name,
                loop_number,
            )
            choices_html += "</li>"
        else:
            choices_html += "</li>"
        return inner_html % choices_html

    class Media:
        pass


class CharacteristicsCheckboxSelectMultipleBootstrap(forms.SelectMultiple):
    class Media:
        css = {"screen": ("kapt_catalog/css/forms/bootstrap_checkbox_tree.css",)}
        js = (
            "kapt_catalog/js/libs/underscore.min.js",
            "kapt_catalog/js/forms/bootstrap_checkbox_tree.js",
        )

    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and "id" in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        # Normalize to strings
        str_values = {force_text(v) for v in value}

        checkbox_final_attrs = final_attrs
        if "class" in checkbox_final_attrs:
            checkbox_final_attrs["class"] += " CharacteristicsCheckbox"
        else:
            checkbox_final_attrs["class"] = "CharacteristicsCheckbox"

        choices_list = list(enumerate(chain(self.choices, choices)))
        init_level = choices_list[0][1][2]
        output = (
            '<div class="listTree">'
            + mark_safe(
                self.create_dom(
                    choices_list,
                    init_level,
                    checkbox_final_attrs,
                    str_values,
                    has_id,
                    final_attrs,
                    attrs,
                    name,
                )
            )
            + "</div>"
        )
        return mark_safe(output)

    def create_dom(
        self,
        choices_list,
        init_level,
        checkbox_final_attrs,
        str_values,
        has_id,
        final_attrs,
        attrs,
        name,
        loop_init=0,
    ):
        sub_choices = []
        inner_html = (
            "<ul>%s</ul>" if loop_init == 0 else '<ul style="display:none;">%s</ul>'
        )
        choices_html = ""
        loop_number = loop_init
        for choice in choices_list:
            option_value, option_label, level, is_category, in_search_engine = choice[1]
            if force_text(option_value) in str_values:
                inner_html = "<ul>%s</ul>"
            if level > init_level:
                sub_choices.append(choice)
            elif level == init_level:
                if len(sub_choices) > 0:
                    sub_init_level = sub_choices[0][1][2]
                    choices_html += self.create_dom(
                        sub_choices,
                        sub_init_level,
                        checkbox_final_attrs,
                        str_values,
                        has_id,
                        final_attrs,
                        attrs,
                        name,
                        loop_number,
                    )
                    choices_html += "</li>"
                    sub_choices = []
                elif loop_number != loop_init:
                    choices_html += "</li>"

                if has_id:
                    final_attrs = dict(
                        final_attrs, id="{}_{}".format(attrs["id"], (loop_number + 1))
                    )

                option_label = force_text(option_label)

                if is_category:
                    cb = forms.CheckboxInput(
                        checkbox_final_attrs,
                        check_test=lambda value: value in str_values,
                    )
                    option_value = force_text(option_value)
                    rendered_cb = cb.render(name, option_value)

                    subs = (
                        Characteristic.objects.get(pk=force_text(option_value))
                        .get_descendants()
                        .values_list("pk", flat=True)
                    )
                    checked_descendants = (
                        Characteristic.objects.filter(pk__in=subs)
                        .filter(pk__in=str_values)
                        .exists()
                    )

                    icon_html = (
                        "glyphicon-chevron-down"
                        if force_text(option_value) in str_values or checked_descendants
                        else "glyphicon-chevron-right"
                    )

                    if force_text(option_value) in str_values or checked_descendants:
                        icon_text = (
                            '<span class="tree-close">'
                            + ugettext("Close")
                            + '</span><span class="tree-open" style="display:none">'
                            + ugettext("Open")
                            + "</span>"
                        )
                    else:
                        icon_text = (
                            '<span class="tree-close" style="display:none">'
                            + ugettext("Close")
                            + '</span><span class="tree-open">'
                            + ugettext("Open")
                            + "</span>"
                        )
                    choices_html += format_html(
                        """
                        <li><span class="category-main"><label>%s &nbsp;%s</label><i class="toggle-list icon-black glyphicon %s"></i><span class="button-indication">%s</span></span>
                        """
                        % (rendered_cb, option_label, icon_html, icon_text)
                    )
                else:
                    cb = forms.CheckboxInput(
                        checkbox_final_attrs,
                        check_test=lambda value: value in str_values,
                    )
                    option_value = force_text(option_value)
                    rendered_cb = cb.render(name, option_value)
                    icon_html = (
                        "glyphicon-chevron-down"
                        if force_text(option_value) in str_values
                        else "glyphicon-chevron-right"
                    )
                    if force_text(option_value) in str_values:
                        icon_text = (
                            '<span class="tree-close">'
                            + ugettext("Close")
                            + '</span><span class="tree-open" style="display:none">'
                            + ugettext("Open")
                            + "</span>"
                        )
                    else:
                        icon_text = (
                            '<span class="tree-close" style="display:none">'
                            + ugettext("Close")
                            + '</span><span class="tree-open">'
                            + ugettext("Open")
                            + "</span>"
                        )
                    if (
                        len(Characteristic.objects.get(pk=option_value).get_choices())
                        > 0
                    ):
                        choices_html += format_html(
                            """
                            <li><span class="category-sub">&mdash;&nbsp;<label>%s %s</label><i class="toggle-list icon-black glyphicon %s"></i><span class="button-indication">%s</span></span>
                            """
                            % (rendered_cb, option_label, icon_html, icon_text)
                        )
                    else:
                        choices_html += format_html(
                            """
                            <li class="cb"><span><label>%s &nbsp;&nbsp;%s</label></span>
                            """
                            % (rendered_cb, option_label)
                        )
            loop_number += 1
        if len(sub_choices) > 0:
            sub_init_level = sub_choices[0][1][2]
            choices_html += self.create_dom(
                sub_choices,
                sub_init_level,
                checkbox_final_attrs,
                str_values,
                has_id,
                final_attrs,
                attrs,
                name,
                loop_number,
            )
            choices_html += "</li>"
        else:
            choices_html += "</li>"
        return inner_html % choices_html
