---
layout: page
title: Frozen Treats
permalink: /category/frozen-treats/
---

<ul>
{% assign cat = site.categories['frozen-treats'] %}
{% if cat and cat != empty %}
  {% for post in cat %}
  <li>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    <span> • {{ post.date | date: "%b %d, %Y" }}</span>
  </li>
  {% endfor %}
{% else %}
  <p>No posts yet.</p>
{% endif %}
</ul>
