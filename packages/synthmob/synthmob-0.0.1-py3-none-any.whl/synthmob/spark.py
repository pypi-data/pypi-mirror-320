from pyspark.sql import SparkSession
from sedona.register import SedonaRegistrator
from sedona.utils import SedonaKryoRegistrator, KryoSerializer

def load_spark(n_cores = 20, region_name = 'us-west-2'):
    
    jars_pkg = [
        'org.apache.sedona:sedona-spark-3.4_2.12:1.6.0',
        'org.apache.hadoop:hadoop-aws:3.3.4',
    ]
    
    spark_configs = {
                        "spark.memory.offHeap.enabled": "true",
                        "spark.memory.offHeap.size": "200g",
                        "spark.serializer": KryoSerializer.getName,
                        "spark.kryo.registrator": SedonaKryoRegistrator.getName,
                        "spark.jars.packages": ",".join(jars_pkg),
                        "spark.driver.extraJavaOptions": "-Dio.netty.tryReflectionSetAccessible=true",
                        "spark.executor.extraJavaOptions": "-Dio.netty.tryReflectionSetAccessible=true",
                        "spark.hadoop.fs.s3a.aws.credentials.provider" : "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider",
                        "spark.hadoop.fs.s3a.endpoint": f"s3.{region_name}.amazonaws.com",
                        "spark.hadoop.fs.s3a.connection.ssl.enabled" : "true",
                    }

    spark_build = SparkSession.builder.master(f"local[{n_cores}]")
            
    for k, v in spark_configs.items():
        spark_build = spark_build.config(k, v)
    
    spark = spark_build.getOrCreate()
    SedonaRegistrator.registerAll(spark)
    
    return spark