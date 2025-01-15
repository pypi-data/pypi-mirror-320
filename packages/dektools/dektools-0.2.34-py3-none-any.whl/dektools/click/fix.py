import typer

app = typer.Typer(add_completion=False)


@app.command()
def playwright():
    from ..playwright.route import RouteTool
    RouteTool.fix_package()
