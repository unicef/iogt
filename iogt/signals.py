from translation_manager.signals import post_save as translation_post_save

translation_post_save.connect(restart_server, sender=None)
