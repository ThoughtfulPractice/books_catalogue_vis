import pandas as pd
from pandas.api.types import CategoricalDtype
import click
from pathlib import Path
import logging
import matplotlib
matplotlib.use('TkAgg')
from plotnine import *


# Setup filepaths
project_dir = Path(__file__).resolve().parents[2]
tidy_books_data_path = project_dir.joinpath(
    'data', 'tidy', 'books.csv')
outfile_dir = project_dir.joinpath('reports', 'figures')
outfile_name = 'hehasread_category_stackedbar.png'


@click.command()
@click.option('--tidy_books_data_path', default=tidy_books_data_path,
              help='.csv path to tidy books data')
@click.option('--outfile_name', default=outfile_name,
              help='filename for generated vis')
@click.option('--outfile_dir', default=outfile_dir,
              help='folder path for generated vis')
def main(tidy_books_data_path, outfile_name, outfile_dir):
    logger = logging.getLogger(__name__)
    outfile_path = outfile_dir.joinpath(outfile_name)

    books = pd.read_csv(tidy_books_data_path)
    df = books[books['ownership'] == 'His']

    columns = ['he_has_read', 'category']
    data = pd.DataFrame(df.groupby(columns).size()).reset_index()
    data.columns = columns + ['count']
    data.sort_values('count', ascending=False, inplace=True)

    # Create ordering for categories
    categories = df.groupby('category').size().sort_values().index
    categories = CategoricalDtype(categories=categories, ordered=True)
    data['category'] = data['category'].astype(categories)

    data['he_has_read'] = data['he_has_read'].astype(str).replace(
        {'0': "No", '1': "Yes"})
    no_yes_cat = CategoricalDtype(categories=["No", "Yes"], ordered=True)
    data['he_has_read'] = data['he_has_read'].astype(no_yes_cat)

    p = (ggplot(data, aes(x='category', y='count', fill='he_has_read'))
         + geom_bar(stat='identity')
         + scale_fill_manual(values=['#99d8c9', '#2ca25f'])
         + coord_flip()
         + theme_xkcd()
         + theme(figure_size=(8, 12),
                 plot_background=element_rect(fill='white'))
         )
    ggplot.save(p, filename=outfile_name, path=str(outfile_dir))
    logger.info('%s saved to %s' % (outfile_path.stem, outfile_path))


if __name__ == "__main__":
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
