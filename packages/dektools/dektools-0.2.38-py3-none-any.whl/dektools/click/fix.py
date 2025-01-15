import typer

app = typer.Typer(add_completion=False)


@app.command()
def playwright(reverse: bool = typer.Option(False, "--reverse", "-r")):
    from ..playwright.route import RouteTool
    RouteTool.fix_package(reverse)
