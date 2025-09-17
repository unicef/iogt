import logging
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from wagtail.models import Page, Revision

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Copy missing revisions from wagtailcore_pagerevision to wagtail_revision"

    def handle(self, *args, **options):
        page_ct = ContentType.objects.get_for_model(Page)
        copied, skipped, errors = 0, 0, 0

        logger.info("Starting migration from wagtailcore_pagerevision → wagtail_revision")

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, created_at, content, approved_go_live_at, page_id, user_id
                FROM wagtailcore_pagerevision
            """)
            rows = cursor.fetchall()

        for row in rows:
            pr_id, created_at, content, approved_go_live_at, page_id, user_id = row

            page = Page.objects.filter(id=page_id).first()
            if not page:
                logger.warning(f"Skipping orphaned revision {pr_id}, page_id={page_id} not found")
                continue

            # Deduplication check
            if Revision.objects.filter(
                content_type=page_ct,
                object_id=str(page.id),
                created_at=created_at,
            ).exists():
                skipped += 1
                logger.debug(f"Skipped duplicate revision {pr_id} for page {page_id}")
                continue

            try:
                Revision.objects.create(
                    base_content_type=page_ct,
                    content=content,
                    approved_go_live_at=approved_go_live_at,
                    created_at=created_at,
                    user_id=user_id,
                    content_type=page_ct,
                    object_id=str(page.id),
                    object_str=str(page),
                )
                copied += 1
                logger.info(f"Copied revision {pr_id} → page {page_id}")
            except Exception as e:
                errors += 1
                logger.error(f"Error copying revision {pr_id}: {e}")

        logger.info(f"Migration completed. Copied={copied}, Skipped={skipped}, Errors={errors}")
