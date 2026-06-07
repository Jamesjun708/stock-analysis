"""生成 GitHub Pages 展示页"""
import json, os

out_dir = '_site'
os.makedirs(out_dir, exist_ok=True)

import shutil

# 复制报告文件
if os.path.isdir('reports'):
    for f in os.listdir('reports'):
        if f.endswith('.txt'):
            shutil.copy(os.path.join('reports', f), os.path.join(out_dir, f))

# 生成 reports.json
files = [{'name': f} for f in os.listdir(out_dir) if f.endswith('.txt')]
with open(os.path.join(out_dir, 'reports.json'), 'w') as f:
    json.dump(files, f)

# 生成 index.html
html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>每日股票分析报告</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,"Microsoft YaHei",sans-serif;background:#f5f5f5;color:#333;padding:40px 20px}
.container{max-width:900px;margin:0 auto}
h1{text-align:center;color:#1a73e8;margin-bottom:10px}
.subtitle{text-align:center;color:#666;margin-bottom:30px}
.box{background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1);padding:24px}
.item{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-bottom:1px solid #eee}
.item:hover{background:#f0f7ff}
.item:last-child{border-bottom:none}
.date{font-weight:600;font-size:16px}
.link{color:#1a73e8;text-decoration:none;padding:6px 16px;border-radius:6px;border:1px solid #1a73e8;font-size:14px}
.link:hover{background:#1a73e8;color:#fff}
.empty{text-align:center;padding:40px;color:#999}
</style>
</head>
<body>
<div class="container">
<h1>每日股票分析报告</h1>
<p class="subtitle">多智能体协作 A 股市场分析系统</p>
<div class="box" id="list">
<h2>历史报告</h2>
<p class="empty">加载中...</p>
</div>
</div>
<script>
fetch("reports.json").then(function(r){return r.json()}).then(function(files){
  var h="";
  files.filter(function(f){return f.name.endsWith(".txt")}).sort().reverse().forEach(function(f,i){
    var d=f.name.replace("daily_report_","").replace(".txt","");
    h+="<div class=item><span class=date>"+d.slice(0,4)+"年"+d.slice(4,6)+"月"+d.slice(6,8)+"日"+(i===0?" <b>NEW</b>":"")+"</span><a class=link href="+f.name+" target=_blank>查看报告</a></div>"
  });
  document.getElementById("list").innerHTML="<h2>历史报告</h2>"+(h||"<p class=empty>暂无报告</p>")
}).catch(function(){document.getElementById("list").innerHTML='<h2>历史报告</h2><p class=empty>加载失败</p>'});
</script>
</body>
</html>'''

with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html)

print(f"页面已生成: {out_dir}/")
