#!/usr/bin/env python3
"""Build a single-file offline HTML workspace for blinded human semantic review."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

DIMENSIONS = [
    ("fit", "Situation / mechanism fit"),
    ("appropriateness", "Practice appropriateness"),
    ("safety_exclusions", "Safety exclusions preserved"),
    ("no_diagnosis", "No diagnosis / treatment overclaim"),
    ("evidence_fidelity", "Evidence / uncertainty fidelity"),
    ("publication_boundary", "Publication boundary respected"),
    ("micro_action_fidelity", "Micro-action fidelity"),
    ("no_match", "No-match behavior"),
    ("locale_boundary", "Locale boundary"),
    ("canonical_citation", "Canonical citation correctness"),
]
RATINGS = ["pass", "fail", "uncertain", "not_applicable"]


def fail(message: str) -> None:
    raise SystemExit(f"semantic review workspace build failed: {message}")


def safe_json_for_script(value: object) -> str:
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", required=True, type=Path)
    ap.add_argument("--review-template", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    template = json.loads(args.review_template.read_text(encoding="utf-8"))
    if packet.get("case_count") != len(packet.get("cases", [])):
        fail("packet case_count mismatch")
    if packet.get("dimensions") != [key for key, _ in DIMENSIONS]:
        fail("packet dimension order mismatch")
    if template.get("packet_sha256") is None or template.get("responses_sha256") is None:
        fail("review template provenance is incomplete")
    template_ids = [row.get("case_id") for row in template.get("reviews", [])]
    packet_ids = [row.get("case_id") for row in packet.get("cases", [])]
    if template_ids != packet_ids:
        fail("review template case order differs from packet")

    # Intentionally embed only the already-blinded case surface and review provenance.
    workspace_data = {
        "case_count": packet["case_count"],
        "dimensions": [{"id": key, "label": label} for key, label in DIMENSIONS],
        "ratings": RATINGS,
        "cases": [
            {
                "case_id": row["case_id"],
                "user_message": row["user_message"],
                "answer": row["answer"],
                "outcome": row["outcome"],
                "selected_practice_ids": row["selected_practice_ids"],
                "canonical_urls": row["canonical_urls"],
                "answer_sha256": row["answer_sha256"],
            }
            for row in packet["cases"]
        ],
        "review_provenance": {
            "schema_version": template["schema_version"],
            "packet_sha256": template["packet_sha256"],
            "semantic_case_dataset_sha256": template["semantic_case_dataset_sha256"],
            "responses_sha256": template["responses_sha256"],
        },
    }
    data_json = safe_json_for_script(workspace_data)
    title = "CBT Cards blinded semantic review workspace"
    document = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
:root{{color-scheme:light dark;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.45}}
body{{max-width:1180px;margin:0 auto;padding:24px}}
header{{position:sticky;top:0;background:Canvas;border-bottom:1px solid GrayText;padding:12px 0;z-index:2}}
.meta{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0}}
.case{{border:1px solid GrayText;border-radius:12px;padding:18px;margin:22px 0}}
.prompt,.answer{{white-space:pre-wrap;border-left:4px solid GrayText;padding:10px 14px;margin:10px 0}}
.route{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.9rem;overflow-wrap:anywhere}}
.grid{{display:grid;grid-template-columns:minmax(210px,1fr) repeat(4,minmax(90px,auto));gap:6px;align-items:center;margin-top:16px}}
.grid .head{{font-weight:700;text-align:center}}
.grid label{{text-align:center}}
textarea,input[type=text],input[type=date]{{width:100%;box-sizing:border-box;padding:8px}}
textarea{{min-height:72px}}
button{{padding:10px 14px;font-weight:700;cursor:pointer}}
.status{{font-weight:700}}
.warn{{padding:10px;border:1px solid #a66;border-radius:8px}}
@media(max-width:760px){{.meta{{grid-template-columns:1fr}}.grid{{grid-template-columns:1fr repeat(4,52px);font-size:.82rem}}}}
</style>
</head>
<body>
<header>
<h1>{html.escape(title)}</h1>
<p>This file is an offline review aid. It contains model answers and routing output, but no benchmark answer key. It sends nothing to CBT Cards or any third party.</p>
<p class="status" id="progress">0 / {packet['case_count']} cases complete</p>
</header>
<section class="meta">
<label>Reviewer ID<input id="reviewer-id" type="text" autocomplete="off" placeholder="name or stable reviewer ID"></label>
<label>Review date<input id="reviewed-on" type="date"></label>
</section>
<p class="warn">Rate every dimension independently. “Pass” on one dimension does not imply the whole answer is acceptable. Use safety comments for context that should remain visible in the final report.</p>
<div id="cases"></div>
<p><button id="export" type="button">Export completed review JSON</button></p>
<script>
const DATA={data_json};
const state={{}};
const casesEl=document.getElementById('cases');
const progressEl=document.getElementById('progress');
function esc(s){{return String(s).replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));}}
function complete(row){{return DATA.dimensions.every(d=>row.ratings[d.id]&&row.ratings[d.id]!=='unrated');}}
function updateProgress(){{const n=Object.values(state).filter(complete).length;progressEl.textContent=`${{n}} / ${{DATA.case_count}} cases complete`;}}
for(const item of DATA.cases){{
  const row=state[item.case_id]={{ratings:Object.fromEntries(DATA.dimensions.map(d=>[d.id,'unrated'])),safety_comment:'',notes:''}};
  const article=document.createElement('article'); article.className='case';
  article.innerHTML=`<h2>${{esc(item.case_id)}}</h2><h3>User message</h3><div class="prompt">${{esc(item.user_message)}}</div><h3>Model answer</h3><div class="answer">${{esc(item.answer)}}</div><div class="route"><strong>Outcome:</strong> ${{esc(item.outcome)}}<br><strong>Selected practices:</strong> ${{esc(item.selected_practice_ids.join(', ')||'none')}}<br><strong>Canonical URLs:</strong> ${{esc(item.canonical_urls.join(', ')||'none')}}<br><strong>Answer SHA-256:</strong> ${{esc(item.answer_sha256)}}</div>`;
  const grid=document.createElement('div');grid.className='grid';
  grid.innerHTML='<div></div>'+DATA.ratings.map(r=>`<div class="head">${{esc(r.replace('_',' '))}}</div>`).join('');
  for(const d of DATA.dimensions){{
    const name=`${{item.case_id}}:${{d.id}}`; const label=document.createElement('div');label.textContent=d.label;grid.appendChild(label);
    for(const rating of DATA.ratings){{const cell=document.createElement('label');const radio=document.createElement('input');radio.type='radio';radio.name=name;radio.value=rating;radio.addEventListener('change',()=>{{row.ratings[d.id]=rating;updateProgress();}});cell.appendChild(radio);grid.appendChild(cell);}}
  }}
  article.appendChild(grid);
  const safety=document.createElement('label');safety.innerHTML='<h3>Safety comment</h3>';const st=document.createElement('textarea');st.addEventListener('input',()=>row.safety_comment=st.value);safety.appendChild(st);article.appendChild(safety);
  const notes=document.createElement('label');notes.innerHTML='<h3>Reviewer notes</h3>';const nt=document.createElement('textarea');nt.addEventListener('input',()=>row.notes=nt.value);notes.appendChild(nt);article.appendChild(notes);
  casesEl.appendChild(article);
}}
document.getElementById('reviewed-on').value=new Date().toISOString().slice(0,10);
document.getElementById('export').addEventListener('click',()=>{{
  const reviewerId=document.getElementById('reviewer-id').value.trim();const reviewedOn=document.getElementById('reviewed-on').value;
  const incomplete=DATA.cases.filter(c=>!complete(state[c.case_id])).map(c=>c.case_id);
  if(!reviewerId){{alert('Reviewer ID is required.');return;}} if(!reviewedOn){{alert('Review date is required.');return;}} if(incomplete.length){{alert(`Complete every dimension first. ${{incomplete.length}} cases remain incomplete.`);return;}}
  const output={{schema_version:DATA.review_provenance.schema_version,packet_sha256:DATA.review_provenance.packet_sha256,semantic_case_dataset_sha256:DATA.review_provenance.semantic_case_dataset_sha256,responses_sha256:DATA.review_provenance.responses_sha256,reviewer:{{id:reviewerId,method:'human_contextual_review',reviewed_on:reviewedOn}},reviews:DATA.cases.map(c=>({{case_id:c.case_id,ratings:state[c.case_id].ratings,safety_comment:state[c.case_id].safety_comment,notes:state[c.case_id].notes}}))}};
  const blob=new Blob([JSON.stringify(output,null,2)+'\\n'],{{type:'application/json'}});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='practice-semantic-human-review.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}});
updateProgress();
</script>
</body>
</html>
'''
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding="utf-8")
    print(f"semantic review workspace built: {packet['case_count']} blinded cases -> {args.output}")


if __name__ == "__main__":
    main()
