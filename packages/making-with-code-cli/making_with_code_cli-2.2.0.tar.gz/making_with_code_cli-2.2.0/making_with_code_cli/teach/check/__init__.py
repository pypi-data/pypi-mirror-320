import click
import requests
from pathlib import Path
from tqdm import tqdm
from making_with_code_cli.curriculum import get_curriculum
from making_with_code_cli.teach.check.check_module import TestMWCModule

@click.command()
@click.argument("url")
@click.argument("course_name")
@click.argument("repo_dir", type=click.Path(exists=True, file_okay=False, writable=True, 
        path_type=Path))
def check(url, course_name, repo_dir):
    "Test MWC curriuclum and modules"
    curriculum = get_curriculum(url, course_name)
    test_cases = []
    for unit in curriculum['units']:
        for module in unit['modules']:
            full_slug = '/'.join([curriculum['slug'], unit['slug'], module['slug']])
            path = repo_dir / full_slug
            test_cases.append((module, path, full_slug))
    results = []
    for mod, path, slug in tqdm(test_cases):
        test = TestMWCModule(module, path)
        errors = test.run()
        if errors:
            results.append((slug, errors))
    for slug, errors in results:
        print(slug)
        for error in errors:
            print(f" - {error}")
