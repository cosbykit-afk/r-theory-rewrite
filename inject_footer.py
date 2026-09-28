#!/usr/bin/env python3
"""Inject a slim footer with Contact-us (Facebook) and forum sign-up links
at the very bottom of every page (after the comments section).

Idempotent: replaces the block between <!-- FOOTER-START --> and
<!-- FOOTER-END --> if present, otherwise inserts before </body>.
"""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

FACEBOOK_URL = "https://www.facebook.com/profile.php?id=61594635330402"

FOOTER_BLOCK = """<!-- FOOTER-START -->
<footer class="rth-footer" id="rth-footer">
<style>
.rth-footer{max-width:860px;margin:2.5em auto 1.5em;padding:1em 1.2em 0;
 border-top:1px solid #ddd;text-align:center;font-family:Georgia,serif;
 font-size:.92em;color:#555}
.rth-footer a{color:#1b5faa;text-decoration:none;margin:0 .8em}
.rth-footer a:hover{text-decoration:underline}
.rth-footer .rth-footer-sep{color:#aaa}
</style>
<a href="__FACEBOOK_URL__" target="_blank" rel="noopener">Contact us</a><span class="rth-footer-sep" id="rth-footer-sep">&middot;</span><a href="/app/register" id="rth-forum-signup">Sign up for the forum</a>
<script>
(function(){
  // Hide the forum sign-up link where the forum isn't reachable
  // (e.g. the GitHub Pages copy); the Contact-us link always stays.
  var link=document.getElementById('rth-forum-signup');
  var sep=document.getElementById('rth-footer-sep');
  if(!link) return;
  try{
    var ctl=new AbortController();
    var t=setTimeout(function(){ctl.abort();},6000);
    fetch('/app/api/comments?page=index',{signal:ctl.signal}).then(function(r){
      clearTimeout(t);
      if(!r.ok) throw 0;
    }).catch(function(){
      link.style.display='none';
      if(sep) sep.style.display='none';
    });
  }catch(e){
    link.style.display='none';
    if(sep) sep.style.display='none';
  }
})();
</script>
</footer>
<!-- FOOTER-END -->""".replace("__FACEBOOK_URL__", FACEBOOK_URL)

START = "<!-- FOOTER-START -->"
END = "<!-- FOOTER-END -->"


def inject(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if START in text and END in text:
        text = re.sub(re.escape(START) + r".*?" + re.escape(END),
                      lambda _: FOOTER_BLOCK, text, flags=re.S, count=1)
        changed = True
    else:
        assert "</body>" in text, path
        text = text.replace("</body>", FOOTER_BLOCK + "\n</body>", 1)
        changed = True
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return changed


def main():
    pages = []
    for dirpath, _, filenames in os.walk(ROOT):
        if ".git" in dirpath:
            continue
        if "index.html" in filenames:
            pages.append(os.path.join(dirpath, "index.html"))
    pages.sort()
    n = 0
    for page in pages:
        inject(page)
        n += 1
    print(f"{n} pages")


if __name__ == "__main__":
    main()
