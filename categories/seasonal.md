---
layout: page
title: Seasonal
permalink: /category/seasonal/
---

<ul>
{% assign cat = site.categories['seasonal'] %}
{% if cat and cat != empty %}
  {% for post in cat %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> • {{ post.date | date: "%b %d, %Y" }}</li>
  {% endfor %}
{% else %}
  <p>No posts yet.</p>
{% endif %}
</ul>
