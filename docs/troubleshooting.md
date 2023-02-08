# Many pages not showing up in flat menu

For a `Page` to show up in the flat menu its `show_in_menu` attribute must be `True`. By default, all `Page` types that would make sense to be seen in a flat menu have `show_in_menu=True`, but if you find yourself in a situation where many `Page`s have `show_in_menu=False`, the following command will set it to `True`, in bulk.

```
python manage.py update_show_in_menu
```
