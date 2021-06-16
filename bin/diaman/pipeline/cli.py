import argparse

from diaman.configuration.app import AppConfig
from diaman.configuration import spark_config
from diaman.pipeline import train_pipeline


def cli():
    """Run the complete application pipeline."""
    # Configuration
    AppConfig()

    # Parse the cli arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('standard_data_path', help='path to the standard data directory')
    parser.add_argument('queue', help='job queue')
    parser.add_argument('--app-name', help='spark application name which must contain the application prd',
                        default='gmt00-diaman-ai')
    parser.add_argument('--driver-mem', help='amount of memory to use for the driver process',
                        default='4g')
    parser.add_argument('--driver-cores', help='number of cores to use for the driver process',
                        default=1)
    parser.add_argument('--executor-mem', help='amount of memory to use per executor process',
                        default='8g')
    parser.add_argument('--executor-cores', help='number of cores to use on each executor',
                        default=4)
    parser.add_argument('--min-executors', help='minimum number of executors to run if dynamic allocation is enabled',
                        default=4)
    parser.add_argument('--max-executors', help='maximum number of executors to run if dynamic allocation is enabled',
                        default=12)
    parser.add_argument('--ini-executors', help='initial number of executors to run if dynamic allocation is enabled',
                        default=4)
    args = parser.parse_args()

    # Instantiate spark
    _, spark_session = spark_config.get_spark(app_name=args.app_name,
                                              queue=args.queue,
                                              driver_mem=args.driver_mem,
                                              driver_cores=args.driver_cores,
                                              executor_mem=args.executor_mem,
                                              executor_cores=args.executor_cores,
                                              min_executors=args.min_executors,
                                              max_executors=args.max_executors,
                                              ini_executors=args.ini_executors)

    # Run the train pipeline
    train_pipeline.run(spark_session, args.standard_data_path)


if __name__ == '__main__':
    cli()
