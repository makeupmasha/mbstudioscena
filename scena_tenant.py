"""Independent installation defaults; existing owner edits always take priority.

Sofia Leroux is a fictional demonstration persona, not a real salon owner.
No customer database, provider credentials or original owner's media is bundled.
"""
from __future__ import annotations

import os
from urllib.parse import urlsplit

# Public brand pseudonym approved by the owner.
BRAND = 'Sofi Leroux'
BRAND_RU = 'Софи Леру'
INITIALS = 'SL'
NAME_RU = 'София Леру'
NAME_LATIN = 'Sofia Leroux'


def public_origin():
    value = (os.environ.get('SCENA_PUBLIC_BASE_URL') or
             os.environ.get('SCENA_LOCAL_BASE_URL') or 'http://localhost:8501').rstrip('/')
    parsed = urlsplit(value)
    local = parsed.hostname in {'localhost', '127.0.0.1'}
    if (parsed.scheme not in {'http', 'https'} or not parsed.hostname or
            parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment or
            (parsed.scheme == 'http' and not local)):
        raise RuntimeError('SCENA_PUBLIC_BASE_URL must be a trusted HTTPS origin.')
    return value


def is_demo():
    return os.environ.get('SCENA_DEMO_SITE', '1') == '1'


def profile_defaults():
    values = {
        'master_name': NAME_RU, 'master_name_ru': NAME_RU,
        'master_name_ro': NAME_LATIN, 'master_name_en': NAME_LATIN,
        'profile_slug': 'sofia-leroux', 'default_locale': 'ru',
        'location': 'Кишинёв', 'location_ru': 'Кишинёв',
        'location_ro': 'Chișinău', 'location_en': 'Chișinău',
        'bio': 'Я София. Создаю макияж, в котором хочется быть собой, и образы, которые интересно рассматривать. Моя студия — место для красоты, съёмок и новых идей.',
        'bio_ro': 'Sunt Sofia. Creez machiaje în care te simți tu însăți și lookuri care atrag privirea. Studioul meu este un loc pentru frumusețe, ședințe foto și idei noi.',
        'bio_en': 'I am Sofia. I create makeup that feels like you and looks worth a second glance. My studio is a space for beauty, photoshoots and new ideas.',
        'bio_translation_approved': '1',
        'beauty_title': BRAND_RU, 'beauty_title_ro': BRAND, 'beauty_title_en': BRAND,
        'beauty_desc': 'Живая кожа, точный акцент, ваш характер. Макияж для особенного дня, съёмки и встречи с собой.',
        'beauty_desc_ro': 'Ten luminos, un accent precis, caracterul tău. Machiaj pentru o zi specială, o ședință foto sau un moment al tău.',
        'beauty_desc_en': 'Luminous skin, a considered detail, your personality. Makeup for a special day, a photoshoot or a moment for yourself.',
        'model_title': 'Лицо. Характер. Движение.',
        'model_title_ro': 'Chip. Caracter. Mișcare.',
        'model_title_en': 'Face. Character. Movement.',
        'model_desc': 'Бьюти-портреты, fashion-съёмки и творческие истории. Открыта к идеям фотографов, дизайнеров и beauty-брендов.',
        'model_desc_ro': 'Portrete beauty, ședințe fashion și povești creative. Deschisă ideilor fotografilor, designerilor și brandurilor de frumusețe.',
        'model_desc_en': 'Beauty portraits, fashion editorials and creative stories. Open to ideas from photographers, designers and beauty brands.',
        'scene_hero_image': 'media/demo/studio.png',
        'professional_hero_image': 'media/demo/portrait.png',
        'professional_cover_image': 'media/demo/studio.png',
        'course_cover_image': 'media/demo/studio.png',
        'model_intro_image': 'media/demo/portrait.png',
        'model_intro_text_ru': 'Я София, визажист и модель. Люблю свет, движение и выразительные детали. Здесь — моя демонстрационная подборка бьюти- и fashion-образов.',
        'model_intro_text_ro': 'Sunt Sofia, make-up artist și model. Îmi plac lumina, mișcarea și detaliile expresive. Aici este selecția mea demonstrativă de lookuri beauty și fashion.',
        'model_intro_text_en': 'I am Sofia, a makeup artist and model. I love light, movement and expressive details. This is my demonstration collection of beauty and fashion looks.',
        'model_intro_alt_ru': 'София Леру — светловолосая героиня демонстрационного сайта',
        'model_intro_alt_ro': 'Sofia Leroux — personajul blond al site-ului demonstrativ',
        'model_intro_alt_en': 'Sofia Leroux — the blonde character of this demonstration site',
        'scene_services_text_ru': 'От лёгкого сияния до вечернего образа — выберите свой повод.',
        'scene_services_text_ro': 'De la o strălucire delicată la un look de seară — alege ocazia ta.',
        'scene_services_text_en': 'From a subtle glow to an evening look — choose your occasion.',
        'public_base_url': public_origin(), 'seo_pretty_urls': '1',
        'seo_empty_sections_noindex': '1', 'seo_google_verification': '',
        'seo_bing_verification': '', 'seo_yandex_verification': '', 'seo_yandex_counter': '',
        'instagram_url': '', 'telegram_url': '',
        'profile_indexed': '0', 'professional_indexed': '0', 'model_indexed': '0',
        'beauty_portfolio_customized': '1', 'model_portfolio_customized': '1',
    }
    for kind, images in {
        'beauty': ('portrait', 'studio', 'model-white'),
        'model': ('model-black', 'model-white', 'portrait'),
    }.items():
        for index in range(1, 13):
            values[f'{kind}_image_{index}'] = f'media/demo/{images[index - 1]}.png' if index <= len(images) else ''
    slides = (
        ('model-black', 'Мой характер — в каждом кадре.', 'Caracterul meu, în fiecare cadru.', 'My character, in every frame.'),
        ('model-white', 'Свет. Движение. Свобода.', 'Lumină. Mișcare. Libertate.', 'Light. Movement. Freedom.'),
        ('portrait', 'Красота начинается с уверенности.', 'Frumusețea începe cu încrederea.', 'Beauty begins with confidence.'),
    )
    for index in range(1, 6):
        prefix = f'model_slide_{index}'
        values[prefix + '_visible'] = '1' if index <= len(slides) else '0'
        values[prefix + '_image'] = f'media/demo/{slides[index - 1][0]}.png' if index <= len(slides) else ''
        for viewport in ('desktop', 'mobile'):
            values[f'{prefix}_{viewport}_x'] = '50'
            values[f'{prefix}_{viewport}_y'] = '40'
        if index <= len(slides):
            for lang, text in zip(('ru', 'ro', 'en'), slides[index - 1][1:]):
                values[f'{prefix}_manifesto_{lang}'] = text
                values[f'{prefix}_alt_{lang}'] = NAME_RU if lang == 'ru' else NAME_LATIN
    return values


DEMO_SERVICES = (
    ('Professional', 'appointment', 'Дневной макияж', 'Machiaj de zi',
     'Свежая кожа, мягкий румянец и выразительный взгляд. Демонстрационный пример услуги.',
     'Ten proaspăt, blush delicat și o privire expresivă. Exemplu demonstrativ de serviciu.', 800.0, 60, 10),
    ('Professional', 'appointment', 'Вечерний макияж', 'Machiaj de seară',
     'Выразительный образ для события или съёмки. Демонстрационный пример услуги.',
     'Un look expresiv pentru un eveniment sau o ședință foto. Exemplu demonstrativ.', 1200.0, 90, 10),
    ('Professional', 'appointment', 'Свадебный макияж', 'Machiaj de mireasă',
     'Нежный свет и стойкий макияж для особенного дня. Детали согласуются лично. Демонстрационная услуга.',
     'Lumină delicată și machiaj rezistent pentru o zi specială. Detaliile se discută personal. Serviciu demonstrativ.', 1600.0, 100, 10),
    ('Professional', 'course', 'Макияж для себя', 'Machiaj pentru tine',
     'Индивидуальный урок: знакомство с косметичкой, техника и ваш повседневный образ. Демонстрационная предзапись.',
     'Lecție individuală: trusa ta, tehnica și lookul de zi cu zi. Preînscriere demonstrativă.', 1800.0, 120, 0),
    ('Model', 'inquiry', 'Бьюти- и fashion-съёмка', 'Ședință beauty și fashion',
     'Творческая съёмка для фотографов, дизайнеров и beauty-проектов. Демонстрационное предложение.',
     'Ședință creativă pentru fotografi, designeri și proiecte beauty. Ofertă demonstrativă.', 0.0, 120, 0),
)

SERVICE_EN = {
    'Дневной макияж': ('Daytime makeup', 'Fresh skin, soft blush and expressive eyes. Demonstration service.'),
    'Вечерний макияж': ('Evening makeup', 'An expressive look for an event or photoshoot. Demonstration service.'),
    'Свадебный макияж': ('Bridal makeup', 'Soft luminosity and lasting makeup for a special day. Demonstration service.'),
    'Макияж для себя': ('Makeup for yourself', 'An individual lesson with your makeup bag, techniques and everyday look. Demo preregistration.'),
    'Бьюти- и fashion-съёмка': ('Beauty and fashion photoshoot', 'Creative shoots for photographers, designers and beauty projects. Demonstration offer.'),
}


def seed_publications(connection):
    """Seed two editable demo stories once; never restore deleted owner content."""
    import json
    from datetime import datetime, timezone
    from scena_publications import initialize_publications
    marker = 'independent_demo_content_v1'
    if connection.execute('SELECT 1 FROM app_meta WHERE key=?', (marker,)).fetchone():
        return
    if not connection.execute('SELECT 1 FROM posts LIMIT 1').fetchone():
        stories = (
            ('Свет на вашей стороне', 'Lumina este de partea ta', 'Light on your side',
             'Мягкое сияние кожи, немного цвета и ваш собственный характер. В «Софи Леру» образ начинается со знакомства. Демонстрационная история вымышленной героини.',
             'Strălucire delicată, puțină culoare și caracterul tău. În Sofi Leroux, lookul începe cu o conversație. Poveste demonstrativă a unui personaj fictiv.',
             'Softly luminous skin, a touch of colour and your own character. At Sofi Leroux, a look begins with a conversation. A demonstration story featuring a fictional character.',
             'portrait', 1, 0),
            ('Характер в движении', 'Caracter în mișcare', 'Character in motion',
             'Чёрный глянец, белый шёлк и свет студии. Моя демонстрационная fashion-история — о свободе пробовать разные роли.',
             'Luciu negru, mătase albă și lumina studioului. Povestea mea fashion demonstrativă este despre libertatea de a încerca roluri diferite.',
             'Black gloss, white silk and studio light. This demonstration fashion story is about the freedom to explore different roles.',
             'model-white', 0, 1),
        )
        for ru, ro, en, body_ru, body_ro, body_en, photo, professional, model in stories:
            cursor = connection.execute('INSERT INTO posts(title_ru,title_ro,body_ru,body_ro,image_url,link_url,translations_approved,show_scene,show_professional,show_model,active,created_at) VALUES(?,?,?,?,?,?,1,1,?,?,1,?)',
                (ru, ro, body_ru, body_ro, f'media/demo/{photo}.png', '', professional, model, datetime.now(timezone.utc).isoformat()))
            post_id = cursor.lastrowid
            initialize_publications(connection)
            row = connection.execute('SELECT draft_json FROM publication_records WHERE post_id=?', (post_id,)).fetchone()
            snapshot = json.loads(row[0])
            snapshot.update(title_en=en, body_en=body_en)
            payload = json.dumps(snapshot, ensure_ascii=False, sort_keys=True)
            connection.execute('UPDATE publication_records SET draft_json=?,published_json=? WHERE post_id=?', (payload, payload, post_id))
            connection.execute('UPDATE publication_versions SET snapshot_json=? WHERE post_id=? AND revision=1', (payload, post_id))
    connection.execute('INSERT INTO app_meta(key,value) VALUES(?,?)', (marker, '1'))
