./opt/chaosblade/blade {{ command }}  {% if classname %} --classname {{ classname }} {% endif %}{% if methodname %} --methodname {{ methodname }}{% endif %}{% if after %} --after {% endif %}