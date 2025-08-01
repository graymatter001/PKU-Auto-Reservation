#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Author  :   Arthals
# @File    :   server.py
# @Time    :   2024/08/10 05:55:05
# @Contact :   zhuozhiyongde@126.com
# @Software:   Visual Studio Code


from fastapi import FastAPI, Request, Response
import os
import re
from rich.console import Console

app = FastAPI()
console = Console()

password = "123456"


@app.post("/pku_sms")
async def sms(request: Request):
    headers = request.headers
    if headers.get("Authorization", None) != password:
        console.print("[red]❌ 未授权的请求[/red]")
        return Response(status_code=403)

    data = await request.json()
    content = data.get("content", "")
    student_id = data.get("id", None)

    if not content:
        console.print("[yellow]⚠️ 缺少短信内容[/yellow]")
        return Response(status_code=400)

    # 尝试从短信内容中提取验证码（6位数字）
    code_match = re.search(r'\d{6}', content)
    if not code_match:
        console.print("[yellow]⚠️ 无法从短信内容中提取验证码[/yellow]")
        return Response(status_code=400)
    
    verification_code = code_match.group()

    # 确定学号：优先使用请求体中的student_id，否则尝试从内容中提取
    if not student_id:
        # 尝试从短信内容中提取学号（假设学号为10位数字）
        id_match = re.search(r'\d{10}', content)
        if id_match:
            student_id = id_match.group()
        else:
            console.print("[red]❌ 无法确定学号，请在请求体中指定student_id[/red]")
            return Response(status_code=400)

    # 创建学号特定的验证码文件
    code_filename = f"{student_id}.txt"
    code_filepath = os.path.join("./", code_filename)

    with open(code_filepath, "w") as f:
        f.write(verification_code)

    console.print(
        f"[green]✅ 收到学号 {student_id} 的验证码 {verification_code}，已写入 {code_filename}[/green]"
    )
    console.print(f"[dim]短信内容: {content}[/dim]")

    return {"status": "success", "student_id": student_id, "code": verification_code, "file": code_filename}


if __name__ == "__main__":
    import uvicorn

    console.print("[bold blue]🚀 启动 PKU 短信验证码接收服务器[/bold blue]")
    console.print(
        f"[yellow]请确保在请求时配置正确的Authorization头: {password}[/yellow]"
    )
    console.print(
        "[cyan]支持的请求体格式:[/cyan]\n" +
        '{\n' +
        '    "content": "【北京大学】您的北京大学App验证码为：272473，请在2分钟内完成操作，否则验证码将失效。",\n' +
        '    "id": "2110000000"\n' +
        '}'
    )
    uvicorn.run(app, host="0.0.0.0", port=8000)