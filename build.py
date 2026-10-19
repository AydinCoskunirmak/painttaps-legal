"""Builds the GitHub Pages site from src/<lang>/{privacy,terms}.md.  Run: python3 build.py"""
import html, os, re, markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
LANGS = [('en', 'English'), ('tr', 'Türkçe'), ('de', 'Deutsch'), ('fr', 'Français'), ('es', 'Español'),
         ('pt', 'Português'), ('ja', '日本語'), ('ko', '한국어')]
NAMES = {  # (privacy, terms, legal)
    'en': ('Privacy Policy', 'Terms of Use', 'Legal information'),
    'tr': ('Gizlilik Politikası', 'Kullanım Koşulları', 'Yasal bilgiler'),
    'de': ('Datenschutzerklärung', 'Nutzungsbedingungen', 'Rechtliche Hinweise'),
    'fr': ('Politique de confidentialité', "Conditions d'utilisation", 'Informations légales'),
    'es': ('Política de privacidad', 'Términos de uso', 'Información legal'),
    'pt': ('Política de Privacidade', 'Termos de Uso', 'Informações legais'),
    'ja': ('プライバシーポリシー', '利用規約', '法的情報'),
    'ko': ('개인정보 처리방침', '이용약관', '법적 고지'),
}
APP = 'Paint Taps'
FULL = 'Paint Taps: Liquid Tube Puzzle'
MAIL = 'csknrmk.aydn@icloud.com'
CSS = """:root{--bg:#f5f0ff;--card:#ffffff;--ink:#241a45;--muted:#6d6290;--accent:#e2681f;--brand:#6a3fd6;--line:#e2d9fb}
@media (prefers-color-scheme:dark){:root{--bg:#150f2e;--card:#1f1842;--ink:#efeaff;--muted:#a99fd0;--accent:#ff9a4d;--brand:#b79bff;--line:#352b63}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans","Noto Sans JP","Noto Sans KR",sans-serif}
header{max-width:820px;margin:0 auto;padding:20px 16px 0;display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.brand{font-weight:800;font-size:19px;color:var(--brand);text-decoration:none;display:flex;align-items:center;gap:8px}
.brand i{width:22px;height:22px;border-radius:7px;background:linear-gradient(160deg,#ffe36b,#ffad1f);box-shadow:0 2px 0 #c47300;display:inline-block}
select{font:inherit;padding:6px 10px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--ink)}
main{max-width:820px;margin:16px auto 40px;padding:24px 20px;background:var(--card);border:1px solid var(--line);border-radius:18px}
h1{margin:0 0 8px;font-size:28px;line-height:1.25}h2{margin:28px 0 8px;font-size:19px}
p,li{overflow-wrap:anywhere}a{color:var(--accent)}ul{padding-inline-start:22px}
footer{max-width:820px;margin:0 auto 40px;padding:0 16px;color:var(--muted);font-size:14px;display:flex;gap:16px;flex-wrap:wrap}
.cards{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}.cards a{display:block;padding:14px 16px;border:1px solid var(--line);border-radius:14px;text-decoration:none;color:var(--ink);font-weight:700}"""


def page(lang, title, body, header_extra='', footer='', script=''):
    return (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} – {APP}</title>'
            f'<style>{CSS}</style>{script}</head><body><header><a class="brand" href="{{root}}"><i></i>{APP}</a>{header_extra}</header>'
            f'<main>{body}</main><footer>{footer}<span>© 2026 {APP}</span></footer></body></html>')


def md_to_html(text):
    out = markdown.markdown(text, extensions=['nl2br', 'sane_lists'])
    out = out.replace(MAIL, f'<a href="mailto:{MAIL}">{MAIL}</a>')
    # linkify bare URLs (strip trailing punctuation from the link)
    def link(m):
        url = m.group(1)
        tail = ''
        while url and url[-1] in '.,;:)）。、':
            tail = url[-1] + tail
            url = url[:-1]
        return f'<a href="{url}" rel="noopener">{url}</a>{tail}'
    out = re.sub(r'(?<![">])(https?://[^\s<]+)', link, out)
    return out


def write(rel, content, depth):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(content.replace('{root}', '../' * depth or './'))


REDIRECT = """<script>(function(){var L=%s;var n=(navigator.languages||[navigator.language||'en']);for(var i=0;i<n.length;i++){var c=(n[i]||'').toLowerCase().split('-')[0];if(L.indexOf(c)>=0){if(c!=='en')location.replace(c+'/');return;}}})();</script>"""

for kind, idx in (('privacy', 0), ('terms', 1)):
    other, oidx = ('terms', 1) if kind == 'privacy' else ('privacy', 0)
    for lang, _ in LANGS:
        src = open(os.path.join(ROOT, 'src', lang, kind + '.md'), encoding='utf-8').read()
        body = md_to_html(src)
        def sel(base):
            opts = ''.join(f'<option value="{base}{kind}/{l}/"{" selected" if l == lang else ""}>{n}</option>' for l, n in LANGS)
            return f'<select aria-label="Language" onchange="location.href=this.value">{opts}</select>'
        title = NAMES[lang][idx]
        foot = f'<a href="../../{other}/{lang}/">{NAMES[lang][oidx]}</a>'
        write(f'{kind}/{lang}/index.html', page(lang, title, body, sel('../../'), foot), 2)
        if lang == 'en':
            foot_root = f'<a href="../{other}/">{NAMES["en"][oidx]}</a>'
            body_root = body.replace('href="../../', 'href="../')
            write(f'{kind}/index.html',
                  page('en', title, body_root, sel('../'), foot_root, REDIRECT % [l for l, _ in LANGS]), 1)

cards = lambda kind, idx: ''.join(f'<a href="{kind}/{l}/">{n}</a>' for l, n in LANGS)
home = (f'<h1>{FULL}</h1><p>{NAMES["en"][2]} · <a href="mailto:{MAIL}">{MAIL}</a></p>'
        f'<div class="cards"><a href="privacy/">Privacy Policy</a><a href="terms/">Terms of Use</a></div>'
        f'<h2>Privacy Policy</h2><div class="cards">{cards("privacy", 0)}</div>'
        f'<h2>Terms of Use</h2><div class="cards">{cards("terms", 1)}</div>')
write('index.html', page('en', 'Legal', home), 0)
open(os.path.join(ROOT, '.nojekyll'), 'w').close()
print('built')
