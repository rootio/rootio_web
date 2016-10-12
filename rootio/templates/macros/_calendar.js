{% macro render_datetime_tojs(d) %}new Date({{d.year}},{{d.month}}-1,{{d.day}},{{d.hour}},{{d.minute}},{{d.second}}){% endmacro %}
{# note that months are zero-based, but everything else is not #}

{% macro render_duration_to_seconds(d) %}{{d.seconds}}{% endmacro %}
{# converts python time objects to seconds #}
