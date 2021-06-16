import os
import logging
import atexit
from pyspark.sql import SparkSession


def get_spark(app_name, queue, driver_mem='4g', driver_cores=1,
              executor_mem='8g', executor_cores=4, min_executors=4,
              max_executors=12, ini_executors=4):
    """Create Spark application.

    Parameters
    ----------
    app_name : string
        spark application name which must contain the application prd
    queue : string, either 'default', 'preprod', 'prod'
        name of the yarn queue to which the application is submitted.
    driver_mem : string, e.g. '4g'
        amount of memory to use for the driver process
    driver_cores : int
        number of cores to use for the driver process
    executor_mem : string, e.g. '8g'
        amount of memory to use per executor process
    executor_cores : int
        number of cores to use on each executor
    min_executors : int
        minimum number of executors to run if dynamic allocation is enabled
    max_executors : int
        maximum number of executors to run if dynamic allocation is enabled
    ini_executors : int
        initial number of executors to run if dynamic allocation is enabled

    Returns
    -------
    spark_context : pyspark.context.SparkContext
        context of the Spark application
    spark_session : pyspark.sql.session.SparkSession
        session of the Spark application

    """
    logging.info('Creating Spark application with the provided configuration')
    logging.info('Environment variables are the following:')
    logging.info('\n' + get_spark_environment_variables())
    spark_session = build_spark_session(app_name=app_name, queue=queue, driver_mem=driver_mem,
                                        driver_cores=driver_cores, executor_mem=executor_mem,
                                        executor_cores=executor_cores, min_executors=min_executors,
                                        max_executors=max_executors, ini_executors=ini_executors)
    spark_context = spark_session.sparkContext
    logger = spark_context._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel(logger.Level.ERROR)
    logger.LogManager.getLogger("akka").setLevel(logger.Level.ERROR)

    atexit.register(lambda: spark_context.stop())
    return spark_context, spark_session


def get_spark_environment_variables():
    return '\n'.join([
        "{} : {}".format(var, os.environ.get(var, '-variable is unset-'))
        for var in [
            'ENVIRONMENT',
            'PYSPARK_PYTHON',
            'PYSPARK_DRIVER_PYTHON',
            'SPARK_CLASSPATH',
            'SPARK_HOME',
            'PYTHONPATH',
        ]
    ])


def build_spark_session(app_name, queue, driver_mem='4g', driver_cores=1,
                        executor_mem='8g', executor_cores=4, min_executors=4,
                        max_executors=12, ini_executors=4):
    return SparkSession.builder\
        .appName(app_name) \
        .config('spark.master', 'yarn') \
        .config('spark.submit.deployMode', 'client') \
        .config("spark.yarn.queue", queue) \
        .config("spark.driver.memory", driver_mem) \
        .config("spark.driver.cores", driver_cores) \
        .config('spark.executor.memory', executor_mem) \
        .config('spark.executor.cores', executor_cores) \
        .config("spark.shuffle.service.enabled", 'true') \
        .config("spark.dynamicAllocation.enabled", 'true') \
        .config("spark.dynamicAllocation.minExecutors", min_executors) \
        .config("spark.dynamicAllocation.maxExecutors", max_executors) \
        .config("spark.dynamicAllocation.initialExecutors", ini_executors) \
        .getOrCreate()
