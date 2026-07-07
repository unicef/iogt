from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone

from wagtail import blocks
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.snippets.models import register_snippet
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


###############################
######## CUSTOM MODELS ########
###############################
@register_snippet
class SBCResource(models.Model):
    title = models.CharField(max_length=255, verbose_name="Title")
    author = models.CharField(max_length=255, blank=True, verbose_name="Author")

    date = models.DateField(
        verbose_name="Published date",
        default=timezone.now
    )

    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Thumbnail"
    )
    link = models.URLField(
        blank=True,
        verbose_name="Link",
        help_text="External links must begin with http:// or https://"
    )
    file = models.ForeignKey(
        'wagtaildocs.Document',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="File (PDF, etc.)"
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('author'),
        FieldPanel('date'),
        FieldPanel('thumbnail'),
        MultiFieldPanel([
            FieldPanel('link'),
            FieldPanel('file'),
        ], heading="Resource"),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Resource"
        verbose_name_plural = "Resources"
        ordering = ['-date']


############################
######## COMPONENTS ########
############################
@register_snippet
class SBCHeader(models.Model):
    class Meta:
        verbose_name = "SBC Header"
        verbose_name_plural = "SBC Headers"

    def clean(self):
        """Only one SBC Header allow"""
        model = self.__class__
        if (model.objects.count() > 0 and self.id != model.objects.get().id):
            raise ValidationError("Only one SBC Header allow")

    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    links = StreamField([
        ('link', blocks.StructBlock([
            ('label', blocks.CharBlock(label="Label")),
            ('url', blocks.PageChooserBlock(
                required=False, 
                label="Link to Page"
            ))
        ])),
    ], use_json_field=True, null=True, blank=True)

    panels = [
        FieldPanel('logo', heading="Logo"),
        FieldPanel('links', heading="Links")
    ]

    def __str__(self):
        return "SBC Header"


@register_snippet
class SBCFooter(models.Model):
    class Meta:
        verbose_name = "SBC Footer"
        verbose_name_plural = "SBC Footers"

    def clean(self):
        """Only one SBC Footer allow"""
        model = self.__class__
        if (model.objects.count() > 0 and self.id != model.objects.get().id):
            raise ValidationError("Only one SBC Footer allow")

    university_link = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator(schemes=['http', 'https'])],
        help_text="Link must begin with http:// or https://",
        default="https://uninorte.edu.co/"
    )
    university_address = models.TextField(blank=True, null=True)
    university_logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    unicef_link = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator(schemes=['http', 'https'])],
        help_text="Link must begin with http:// or https://",
        default="https://unicef.org/"
    )
    unicef_address = models.TextField(blank=True, null=True)
    unicef_logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    links = StreamField([
        ('link', blocks.StructBlock([
            ('label', blocks.CharBlock(label="Label")),
            ('url', blocks.PageChooserBlock(
                required=False, 
                label="Link to Page"
            ))
        ])),
    ], use_json_field=True, null=True, blank=True)

    panels = [
        FieldPanel('university_link', heading="University Link"),
        FieldPanel('university_address', heading="University Address"),
        FieldPanel('university_logo', heading="University Logo (Uninorte)"),
        FieldPanel('unicef_link', heading="UNICEF Link"),
        FieldPanel('unicef_address', heading="UNICEF Address"),
        FieldPanel('unicef_logo', heading="UNICEF Logo"),
        FieldPanel('links', heading="Links")
    ]

    def __str__(self):
        return "SBC Footer"


#######################
######## PAGES ########
#######################
class SBCLandingPage(Page):
    template = 'sbc/pages/landing_page.html'

    # Hero
    hero_title = models.CharField(
        default="Red SBC LAC – Plataforma de Aprendizaje y Conocimiento",
        max_length=255
    )
    hero_description = models.TextField(
        default="Instituciones académicas de ocho países de América Latina y el Caribe unen esfuerzos para abordar temas críticos para la infancia y adolescencia."
    )
    hero_cta_label = models.CharField(
        default="Ver recursos",
        max_length=255,
        blank=True,
        null=True
    )
    hero_cta_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Hero CTA Page"
    )
    hero_bk_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    # About
    about_title = models.CharField(
        default="Acerca de la Alianza UNICEF - Uninorte",
        max_length=255
    )
    about_description_1 = models.TextField(
        default="América Latina y el Caribe enfrentan desafíos complejos en torno a las infancias y sus derechos, por ejemplo: dos de cada tres niños, niñas y adolescentes, de edades comprendidas entre 1 y 14 años, en la región experimentan disciplina violenta en el hogar."
    )
    about_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    about_description_2 = models.TextField(
        default="Esta alianza es una plataforma estratégica de reflexión y acción, fruto de un proceso de colaboración sostenida entre el sector académico, sociedad civil y UNICEF a favor de los derechos de la niñez."
    )

    # Resources
    resources_title = models.CharField(
        default="Recursos Destacados",
        max_length=255,
        blank=True,
        null=True
    )
    resources_list = StreamField([
        ('resource', SnippetChooserBlock('sbc.SBCResource'))
    ], use_json_field=True, null=True, blank=True, max_num=3)
    resources_cta_label = models.CharField(
        default="Ver mas recursos",
        max_length=255,
        blank=True,
        null=True
    )
    resources_cta_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Resources CTA Page"
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('hero_title', heading="Title"),
            FieldPanel('hero_description', heading="Description"),
            FieldPanel('hero_cta_label', heading="CTA Label"),
            FieldPanel('hero_cta_link', heading="CTA Link"),
            FieldPanel('hero_bk_image', heading="Background Image")
        ], heading='Hero'),
        MultiFieldPanel([
            FieldPanel('about_title', heading="Title"),
            FieldPanel('about_description_1', heading="Description 1"),
            FieldPanel('about_image', heading="Image"),
            FieldPanel('about_description_2', heading="Description 2"),
        ], heading='About Alliance'),
        MultiFieldPanel([
            FieldPanel('resources_title', heading="Resources Title"),
            FieldPanel('resources_list', heading="Resources List"),
            FieldPanel('resources_cta_label', heading="CTA Label"),
            FieldPanel('resources_cta_link', heading="CTA Link"),
        ], heading='Resources')
    ]


class SBCResourcesPage(Page):
    template = 'sbc/pages/resources_page.html'

    resources_title = models.CharField(
        default="Recursos",
        max_length=255
    )
    resources_description = models.TextField(
        default="Mapeo de universidades con trabajo, cursos y recursos en infancias y SBC"
    )

    content_panels = Page.content_panels + [
        FieldPanel('resources_title', heading="Title"),
        FieldPanel('resources_description', heading="Description"),
    ]

    def get_context(self, request):
        context = super().get_context(request)

        all_resources = SBCResource.objects.all()
        order = request.GET.get('order', 'date')

        if order == 'name':
            all_resources = SBCResource.objects.all().order_by('title')
        elif order == 'date':
            all_resources = SBCResource.objects.all().order_by('-date')

        paginator = Paginator(all_resources, 2)
        page_number = request.GET.get('page')

        try:
            resources = paginator.page(page_number)
        except PageNotAnInteger:
            resources = paginator.page(1)
        except EmptyPage:
            resources = paginator.page(paginator.num_pages)

        context['resources'] = resources
        context['order'] = order

        return context


class SBCAlliancePage(Page):
    template = 'sbc/pages/alliance_page.html'

    alliance_title = models.CharField(
        default="Sobre la Alianza",
        max_length=255
    )
    alliance_description = RichTextField(
        features=['bold', 'italic', 'link'],
        default='<p>La alianza entre UNICEF LACRO y la Fundación Universidad del Norte (Uninorte) tiene como propósito fortalecer las capacidades en Cambio Social y de Comportamiento (SBC) en América Latina y el Caribe, a través de la articulación entre academia, sector público y organizaciones sociales.</p><br/><br/><p>Esta colaboración impulsa la creación y consolidación de una Red Académica Regional, orientada a generar conocimiento, formar talento y promover la implementación de estrategias de SBC contextualizadas a las realidades culturales y sociales de la región.</p>'
    )
    alliance_purpose_title = models.CharField(
        default="Propósito General",
        max_length=255
    )
    alliance_purpose_description = RichTextField(
        features=['bold', 'italic', 'link'],
        default='<p>Contribuir al fortalecimiento de capacidades técnicas, la generación de evidencia y la articulación regional en SBC, mediante la creación de una red académica sostenible que conecte universidades, gobiernos, UNICEF y otros actores clave. </p>'
    )
    alliance_purpose_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    alliance_lines_title = models.CharField(
        default="Líneas de Trabajo",
        max_length=255
    )
    alliance_lines_list = StreamField([
        ('line', blocks.StructBlock([
            ('title', blocks.CharBlock(max_length=255)),
            ('description', blocks.RichTextBlock(features=['bold', 'italic', 'link']))
        ])),
    ], use_json_field=True, null=True, blank=True)
    alliance_achievements_title = models.CharField(
        default="Principales Logros ",
        max_length=255
    )
    alliance_achievements_list = StreamField([
        ('achievement', blocks.StructBlock([
            ('description', blocks.RichTextBlock(features=['bold', 'italic', 'link']))
        ])),
    ], use_json_field=True, null=True, blank=True)
    alliance_timeline_title = models.CharField(
        default="Linea de tiempo",
        max_length=255
    )
    alliance_timeline_description = RichTextField(
        features=['bold', 'italic', 'link'],
        default='<p>ALIANZA UNICEF & UNINORTE (2022–2026)</p>'
    )
    alliance_timeline_list = StreamField([
        ('timeline', blocks.StructBlock([
            ('year', blocks.CharBlock(max_length=255)),
            ('title', blocks.CharBlock(max_length=255)),
            ('subtitle', blocks.CharBlock(max_length=255, required=False)),
            ('description', blocks.RichTextBlock(features=['bold', 'italic', 'link', 'ul', 'ol']))
        ])),
    ], use_json_field=True, null=True, blank=True)
    alliance_gallery_title = models.CharField(
        default="Galeria",
        max_length=255
    )
    alliance_gallery_description = RichTextField(
        features=['bold', 'italic', 'link'],
        default='<p>Algunas fotos relacionadas al proyecto</p>'
    )
    alliance_gallery_list = StreamField([
        ('image', ImageChooserBlock()),
    ], use_json_field=True, null=True, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('alliance_title', heading="Title"),
            FieldPanel('alliance_description', heading="Description"),
        ], heading='Head'),
        MultiFieldPanel([
            FieldPanel('alliance_purpose_title', heading="Title"),
            FieldPanel('alliance_purpose_description', heading="Description"),
            FieldPanel('alliance_purpose_image', heading="Image"),
        ], heading='Purpose'),
        MultiFieldPanel([
            FieldPanel('alliance_lines_title', heading="Title"),
            FieldPanel('alliance_lines_list', heading="Work Lines List"),
        ], heading='Work Lines'),
        MultiFieldPanel([
            FieldPanel('alliance_achievements_title', heading="Title"),
            FieldPanel('alliance_achievements_list', heading="Achievements List"),
        ], heading='Achievements'),
        MultiFieldPanel([
            FieldPanel('alliance_timeline_title', heading="Title"),
            FieldPanel('alliance_timeline_description', heading="Description"),
            FieldPanel('alliance_timeline_list', heading="Timeline List"),
        ], heading='Timeline'),
        MultiFieldPanel([
            FieldPanel('alliance_gallery_title', heading="Title"),
            FieldPanel('alliance_gallery_description', heading="Description"),
            FieldPanel('alliance_gallery_list', heading="Gallery List"),
        ], heading='Timeline')
    ]


class SBCNetworkPage(Page):
    template = 'sbc/pages/network_page.html'

    network_title = models.CharField(
        default="Red Académica de Intercambio y Aprendizaje sobre Cambio Social y de Comportamiento (SBC)",
        max_length=255
    )
    network_description = RichTextField(
        features=['bold', 'italic', 'link'],
        default="""
            <p>La Red Académica de Intercambio y Aprendizaje sobre Cambio Social y de Comportamiento (SBC) en favor de la infancia en América Latina y el Caribe es una iniciativa impulsada por UNICEF LACRO en alianza con la Universidad del Norte (UNINORTE), orientada a fortalecer la articulación entre la academia, organismos internacionales, gobiernos y sociedad civil para promover transformaciones sociales sostenibles en la región.
            </p>
            <p>
            La Red surge como resultado de un proceso iniciado en 2023, que ha integrado formación, generación de conocimiento y diálogo regional en torno al enfoque de Cambio Social y de Comportamiento, permitiendo consolidar una base académica y técnica sólida para su desarrollo.
            </p>
            <p>
            La Red tiene como propósito consolidar una plataforma regional de aprendizaje, investigación e innovación, que contribuya al fortalecimiento de capacidades técnicas, la producción de evidencia y la implementación de estrategias de cambio social y de comportamiento orientadas a mejorar las condiciones de vida de niños, niñas y adolescentes en América Latina y el Caribe.</p>
        """
    )
    network_strategies_title = models.CharField(
        default="¿Qué hacemos?",
        max_length=255
    )
    network_strategies_description = RichTextField(
        features=['bold', 'italic', 'link'],
        default='<p>La Red articula sus acciones en torno a seis líneas estratégicas:</p>'
    )
    network_strategies_list = StreamField([
        ('strategy', blocks.StructBlock([
            ('title', blocks.CharBlock(max_length=255)),
            ('description', blocks.RichTextBlock(features=['bold', 'italic', 'link']))
        ])),
    ], use_json_field=True, null=True, blank=True)
    network_focus_title = models.CharField(
        default="Un enfoque regional, colaborativo y centrado en la niñez",
        max_length=255
    )
    network_focus_body = RichTextField(
        features=['bold', 'italic', 'link', 'ul', 'ol'],
        default="""
            <p>La Red reúne universidades y actores académicos de América Latina y el Caribe, promoviendo un enfoque:</p>
            <ul>
                <li><b>Colaborativo</b>, basado en el diálogo de saberes</li>
                <li><b>Contextualizado</b>, adaptado a las realidades culturales de la región</li>
                <li><b>Interdisciplinario</b>, integrando diversas áreas del conocimiento</li>
                <li><b>Centrado en derechos</b>, con énfasis en la niñez y la equidad</li>
            </ul>
            <p>Entre sus áreas prioritarias se encuentran la inmunización, la nutrición, la  educación, la protección contra la violencia, la salud mental, la  inclusión social y la acción climática.</p>
        """
    )
    network_focus_download_description = RichTextField(
        default="<p><i>Haz click aqui debajo para descargar la <b>“Nota Conceptual - Red Académica de Centros de Aprendizaje”</b></i></p>",
        max_length=255
    )
    network_focus_download_link = models.URLField(
        blank=True,
        verbose_name="Link",
        help_text="External links must begin with http:// or https://"
    )
    network_focus_download_file = models.ForeignKey(
        'wagtaildocs.Document',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="File (PDF, etc.)"
    )
    network_universities_title = models.CharField(default="Universidades Participantes", max_length=255)
    network_universities_map = models.CharField(null=True, blank=True, max_length=500)
    network_universities_list = StreamField([
        ('university', blocks.StructBlock([
            ('logo', ImageChooserBlock()),
            ('link', blocks.URLBlock(required=False))
        ])),
    ], use_json_field=True, null=True, blank=True)
    network_team_unicef_title = models.CharField(
        default="Equipo UNICEF",
        max_length=255
    )
    network_team_unicef_list = StreamField([
        ('member', blocks.StructBlock([
            ('title', blocks.CharBlock(max_length=255)),
            ('subtitle', blocks.CharBlock(max_length=255, required=False)),
            ('description', blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False))
        ])),
    ], use_json_field=True, null=True, blank=True)
    network_team_uninorte_title = models.CharField(
        default="Equipo UNINORTE",
        max_length=255
    )
    network_team_uninorte_list = StreamField([
        ('member', blocks.StructBlock([
            ('title', blocks.CharBlock(max_length=255)),
            ('subtitle', blocks.CharBlock(max_length=255, required=False)),
            ('description', blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False))
        ])),
    ], use_json_field=True, null=True, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('network_title', heading="Title"),
            FieldPanel('network_description', heading="Description"),
        ], heading='Head'),
        MultiFieldPanel([
            FieldPanel('network_strategies_title', heading="Title"),
            FieldPanel('network_strategies_description', heading="Description"),
            FieldPanel('network_strategies_list', heading="Strategies List"),
        ], heading='Strategies'),
        MultiFieldPanel([
            FieldPanel('network_focus_title', heading="Title"),
            FieldPanel('network_focus_body', heading="Body"),
            FieldPanel('network_focus_download_description', heading="Download Button Description"),
            FieldPanel('network_focus_download_link', heading="Download Button Link"),
            FieldPanel('network_focus_download_file', heading="Download Button File"),
        ], heading='Focus'),
        MultiFieldPanel([
            FieldPanel('network_universities_title', heading="Title"),
            FieldPanel('network_universities_map', heading="Map"),
            FieldPanel('network_universities_list', heading="List")
        ], heading="Universities"),
        MultiFieldPanel([
            FieldPanel('network_team_unicef_title', heading="Unicef Title"),
            FieldPanel('network_team_unicef_list', heading="Unicef Members List"),
            FieldPanel('network_team_uninorte_title', heading="Uninorte Title"),
            FieldPanel('network_team_uninorte_list', heading="Uninorte Members List"),
        ], heading='Members'),
    ]
