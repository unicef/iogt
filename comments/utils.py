from django_comments_xtd.models import XtdComment


def cleaned_tree(comments):
    tree = []
    for comment in comments:
        tree.append({
            'comment': comment,
            'has_child': XtdComment.objects.filter(
                parent_id=comment.pk).exclude(pk=comment.pk).exists()
        })
    return tree
