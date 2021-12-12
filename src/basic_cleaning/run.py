#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    ######################
    # YOUR CODE HERE     #
    ######################
    logger.info("Downloading artifact")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()

    raw_df = pd.read_csv(artifact_path)

    min_price = args.min_price
    max_price = args.max_price
    logger.info("Filter artifact into Min-Max Price")
    idx = raw_df['price'].between(min_price, max_price)
    raw_df = raw_df[idx].copy()
    # Convert last_review to datetime
    logger.info("Convert last_review feature to Datetime")
    raw_df['last_review'] = pd.to_datetime(raw_df['last_review'])

    # Add to fix a failure
    idx = raw_df['longitude'].between(-74.25, -73.50) & raw_df['latitude'].between(40.5, 41.2)
    df = raw_df[idx].copy()

    raw_df.to_csv(args.output_artifact,index=False)

    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)

    logger.info("Logging artifact")
    run.log_artifact(artifact)

    os.remove(args.output_artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Fully-qualified name for the input artifact",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Fully-qualified name for the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Fully-qualified name for the type of artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Simple and meaninful description about the component",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=int,
        help="Minimum Price per Night we want",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=int,
        help="Maximum Price per Night we want",
        required=True
    )


    args = parser.parse_args()

    go(args)
