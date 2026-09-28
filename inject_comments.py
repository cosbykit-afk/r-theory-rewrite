#!/usr/bin/env python3
"""Inject a forum-backed comment section at the bottom of every page of the
r-theory-rewrite site.

Idempotent: the block is delimited by <!-- COMMENTS-START --> /
<!-- COMMENTS-END --> and inserted before </body>. Re-running replaces the
block in place.

The block is self-contained (scoped CSS + HTML + inline JS, no external
files). The JS talks to the Lampy forum on the same host:

    GET  /app/api/comments?page=<slug>   -> {mode, logged_in, username,
                                             csrf_token, thread, posts}
    POST /app/api/comments               -> {post, thread}

`mode` is "login" or "guest" (an admin toggle on the forum side); the panel
adapts: guest mode shows a display-name field, login mode requires a forum
session. One forum thread per page slug is the single source of truth, so
forum replies mirror onto the site and site comments mirror into the forum.

On hosts without /app (e.g. the GitHub Pages copy) the panel degrades to a
muted note instead of a broken form.
"""

import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

COMMENTS_BLOCK = '''<!-- COMMENTS-START -->
<style>
.rth-comments{font-family:Georgia,serif;max-width:860px;margin:2.5em auto 1em;
 padding:1.2em 1.4em;background:linear-gradient(180deg,#fbfbf9,#f0f0eb);
 border:1px solid #0f4c5c;border-radius:8px;box-shadow:0 2px 8px rgba(13,59,108,.15);
 line-height:1.6;color:#1a1a1a}
.rth-comments h2{margin:0 0 .2em;font-size:1.25em;color:#0d3b6c;
 border-bottom:2px solid #1b5faa;padding-bottom:.3em}
.rth-comments-on{font-size:.9em;color:#555;margin:.4em 0 1em}
.rth-comments-on span{font-weight:bold;color:#1a1a1a}
.rth-comments-list{margin:0 0 1em}
.rth-comments-loading,.rth-comments-empty,.rth-comments-note{color:#777;font-style:italic}
.rth-comment{border-top:1px dotted #ccc;padding:.6em 0}
.rth-comment-head{font-size:.9em;color:#444}
.rth-comment-date{color:#888}
.rth-comment-body{white-space:pre-wrap;margin:.3em 0 .6em;overflow-wrap:break-word}
.rth-comment-form{display:flex;flex-direction:column;gap:.6em;margin-top:1em}
.rth-comment-name,.rth-comment-body-input{font-family:Georgia,serif;font-size:1em;
 padding:.5em .7em;border:1px solid #999;border-radius:4px;background:#fff;
 color:#1a1a1a;width:100%;box-sizing:border-box}
.rth-comment-form button{align-self:flex-start;font-family:Georgia,serif;font-size:1em;
 padding:.5em 1.4em;color:#fff;background:linear-gradient(180deg,#2a7ab8,#0d3b6c);
 border:1px solid #0d3b6c;border-radius:5px;cursor:pointer}
.rth-comment-form button:hover{filter:brightness(1.12)}
.rth-comment-status{min-height:1.2em;font-size:.9em;color:#0d3b6c;margin:0}
.rth-comment-error{color:#a00}
.rth-comments-forum{margin:1em 0 0;font-size:.95em}
.rth-comments-forum a{color:#1b5faa;text-decoration:none}
.rth-comments-forum a:hover{text-decoration:underline}
.rth-comments-login{font-size:.95em}
.rth-comments-login a{color:#1b5faa}
</style>
<section class="rth-comments" id="comments" aria-label="Comments">
<h2>Comments</h2>
<p class="rth-comments-on">Commenting on: <span id="comment-page-title"></span></p>
<div class="rth-comments-list" id="comments-list"><p class="rth-comments-loading">Loading&#8230;</p></div>
<form class="rth-comment-form" id="rth-comment-form">
<input id="comment-name" class="rth-comment-name" placeholder="Display name (optional)" maxlength="60" autocomplete="nickname">
<textarea id="comment-body" class="rth-comment-body-input" rows="4" placeholder="Write a comment&#8230;" required maxlength="5000"></textarea>
<button type="submit">Post comment</button>
<p class="rth-comment-status" role="status"></p>
</form>
<p class="rth-comments-forum" hidden><a id="comments-forum-link" href="#">Continue the discussion in the forum &#8594;</a></p>
</section>
<script>
(function(){
"use strict";
var section=document.getElementById("comments");
if(!section)return;
/* Page slug, mount-agnostic: last path segment, "index" for site roots. */
var segs=location.pathname.replace(/\\/+$/,"").split("/").filter(function(s){return s.length;});
var slug=segs.length?segs[segs.length-1]:"index";
if(slug==="r-theory"||slug==="r-theory-rewrite")slug="index";
var mode="login",csrfToken="";
var listEl=document.getElementById("comments-list");
var formEl=document.getElementById("rth-comment-form");
var nameEl=document.getElementById("comment-name");
var bodyEl=document.getElementById("comment-body");
var statusEl=section.querySelector(".rth-comment-status");
var forumLink=document.getElementById("comments-forum-link");
var titleEl=document.getElementById("comment-page-title");
if(titleEl)titleEl.textContent=document.title;
function setStatus(msg,isError){
  if(!statusEl)return;
  statusEl.textContent=msg||"";
  statusEl.className="rth-comment-status"+(isError?" rth-comment-error":"");
}
function fmtDate(iso){
  try{return new Date(iso).toLocaleString();}
  catch(e){return iso||"";}
}
function renderPost(p){
  var wrap=document.createElement("article");
  wrap.className="rth-comment";
  var head=document.createElement("div");
  head.className="rth-comment-head";
  var who=document.createElement("strong");
  who.textContent=p.guest_name?(p.guest_name+" (guest)"):(p.author||"Anonymous");
  head.appendChild(who);
  var when=document.createElement("span");
  when.className="rth-comment-date";
  when.textContent=" \u2014 "+fmtDate(p.created_at);
  head.appendChild(when);
  var body=document.createElement("div");
  body.className="rth-comment-body";
  body.textContent=p.body||"";
  wrap.appendChild(head);
  wrap.appendChild(body);
  return wrap;
}
function renderPosts(posts){
  listEl.textContent="";
  if(!posts||!posts.length){
    var none=document.createElement("p");
    none.className="rth-comments-empty";
    none.textContent="No comments yet \u2014 start the discussion.";
    listEl.appendChild(none);
    return;
  }
  posts.forEach(function(p){listEl.appendChild(renderPost(p));});
}
function setForumLink(thread){
  if(!forumLink||!thread)return;
  forumLink.href=thread.url||("/app/thread/"+thread.id);
  var p=forumLink.parentElement;
  if(p&&p.hasAttribute("hidden"))p.removeAttribute("hidden");
}
function showLoginPrompt(){
  formEl.style.display="none";
  if(section.querySelector(".rth-comments-login"))return;
  var p=document.createElement("p");
  p.className="rth-comments-login";
  var a=document.createElement("a");
  /* Return here after login: the forum honors ?next= for relative paths. */
  a.href="/app/login?next="+encodeURIComponent(
    location.pathname+location.search+location.hash);
  a.textContent="Log in to the forum";
  p.appendChild(a);
  p.appendChild(document.createTextNode(" to comment — you will be brought back here."));
  formEl.parentNode.insertBefore(p,formEl);
}
/* Graceful degradation: no /app on this host (e.g. GitHub Pages copy). */
function degrade(){
  listEl.textContent="";
  var note=document.createElement("p");
  note.className="rth-comments-note";
  note.textContent="Comments are available on the Lampy-hosted copy of this site.";
  listEl.appendChild(note);
  formEl.style.display="none";
  var fp=forumLink?forumLink.parentElement:null;
  if(fp)fp.style.display="none";
}
fetch("/app/api/comments?page="+encodeURIComponent(slug),{credentials:"same-origin"})
.then(function(resp){if(!resp.ok)throw new Error("http "+resp.status);return resp.json();})
.then(function(data){
  mode=data.mode||"login";
  csrfToken=data.csrf_token||"";
  if(mode==="guest"){nameEl.style.display="";}
  else{nameEl.style.display="none";if(!data.logged_in)showLoginPrompt();}
  renderPosts(data.posts);
  if(data.thread)setForumLink(data.thread);
})
.catch(function(){degrade();});
formEl.addEventListener("submit",function(ev){
  ev.preventDefault();
  var body=bodyEl.value.trim();
  if(!body){setStatus("Please write a comment first.",true);return;}
  var payload={page:slug,page_title:document.title,body:body};
  if(mode==="guest"){var nm=nameEl.value.trim();if(nm)payload.name=nm;}
  setStatus("Posting\u2026");
  fetch("/app/api/comments",{
    method:"POST",
    headers:{"Content-Type":"application/json","X-CSRF-Token":csrfToken},
    body:JSON.stringify(payload),
    credentials:"same-origin"
  }).then(function(resp){
    if(resp.status===401){showLoginPrompt();setStatus("Please log in to comment.",true);return null;}
    if(resp.status===429){setStatus("Too many comments \u2014 please wait a bit and try again.",true);return null;}
    if(resp.status===400){return resp.json().then(function(d){
      setStatus((d&&d.error)||"Could not post the comment.",true);return null;},
      function(){setStatus("Could not post the comment.",true);return null;});}
    if(!resp.ok){setStatus("Could not post the comment. Please try again.",true);return null;}
    return resp.json();
  }).then(function(data){
    if(!data)return;
    var empty=listEl.querySelector(".rth-comments-empty");
    if(empty)empty.remove();
    var post=data.post||data;
    listEl.insertBefore(renderPost(post),listEl.firstChild);
    bodyEl.value="";
    if(nameEl)nameEl.value="";
    setStatus("Comment posted.");
    if(data.thread)setForumLink(data.thread);
  }).catch(function(){setStatus("Could not post the comment. Please try again.",true);});
});
})();
</script>
<!-- COMMENTS-END -->'''


def replace_block(text, start, end, new):
    if start in text:
        pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
        return pat.sub(lambda _: new, text, count=1), True
    return text, False


def main():
    pages = []
    for dirpath, _, filenames in os.walk(ROOT):
        if ".git" in dirpath:
            continue
        if "index.html" in filenames:
            pages.append(os.path.join(dirpath, "index.html"))
    pages.sort()
    print(f"{len(pages)} pages")
    for page in pages:
        rel = os.path.relpath(page, ROOT)
        with open(page) as fh:
            text = fh.read()

        text, had = replace_block(text, "<!-- COMMENTS-START -->",
                                  "<!-- COMMENTS-END -->", COMMENTS_BLOCK)
        if not had:
            assert "</body>" in text, page
            text = text.replace("</body>", COMMENTS_BLOCK + "\n</body>", 1)

        with open(page, "w") as fh:
            fh.write(text)
        print("injected", rel)


if __name__ == "__main__":
    main()
