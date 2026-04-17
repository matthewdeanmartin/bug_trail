"""Route for /help — setup instructions for new users."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import HTMLResponse

from bug_trail.app import app, render


@app.get("/help", response_class=HTMLResponse)
def help_page(request: Request) -> HTMLResponse:
    return render(request, "view_help.jinja")
