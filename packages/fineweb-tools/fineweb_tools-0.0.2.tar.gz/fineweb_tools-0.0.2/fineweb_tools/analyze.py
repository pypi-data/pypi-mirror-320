from math import log10
import polars as pl


def group_domains_by_count(
        df: pl.DataFrame,
        group_fn: object = lambda x: int(log10(x))
):
    # Create the DataFrame and add the 'group' column
    df = df.with_columns(
        pl.col("count").map_elements(group_fn, return_dtype=pl.Int32).alias("group")
    )

    # First, we calculate the total sum of 'count' for the entire dataset
    total_url_sum = df.select(pl.sum("count")).to_numpy()[0][0]

    # Grouping and aggregating
    result = (
        df.group_by("group")
        .agg([
            pl.min("count").alias("group_min"),   # Min of 'count' within the group
            pl.max("count").alias("group_max"),   # Max of 'count' within the group
            pl.count("domain").alias("domains"),  # Count of domain entries per group
            pl.sum("count").alias("pages")   # Sum of 'count' per group
        ])
        .with_columns(
            # Adding the 'corpus_perc' column as the percentage of the total sum
            ((pl.col("pages") / total_url_sum * 100).round(2)).alias("corpus_perc")
        )

    ).sort('group')

    print ('Total Domains:', f"{result['domains'].sum():,}")
    print ('Total URLs:', f"{result['pages'].sum():,}")
    return result