def can_process_payment(user, comment):
    # if a moderator moderate his own comment
    if comment.user == user:
        return False


