import click


@click.command()
@click.option("--filename", type=click.Path(exists=True), required=True)
def process_blotter(filename: click.Path):
    from company_a.csv_utils import read_blotter_csv, write_blotter_csv
    from company_a.transformations import transform

    blotter = read_blotter_csv(filename)
    new_blotter = transform(blotter)
    write_blotter_csv(new_blotter, "blotter-new.csv")


if __name__ == "__main__":
    process_blotter()
