# kafka script to generate the report

import json
import time
import logging

from datetime import datetime

from typing import Optional
from typing import Dict

from jmxquery import JMXQuery
from jmxquery import JMXConnection

from neso_utils.assessment_report.kafka.metrics import KafkaMetrics
from neso_utils.assessment_report.utils.dict import aggregator
from neso_utils.assessment_report.utils.sparql import run_sparql_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssessmentReport:
    """
    Class to generate the report with kafka metrics and or custom metrics (e.g. metrics around
    the type of messages vehiculated).

    Most of the default metrics are around:
    - Producer latency;
    - Consumer latency;
    - Number of messages vehiculated.

    However, the user can add custom metrics to the report.

    Args:
        target_topic (str): topic to which the messages are produced
        source_topic (str, optional): topic from which the messages are consumed
        broker (str, optional): broker to connect to
        frequency (int, optional): how often the metrics are determined
        metrics (Dict, optional): custom metrics to add to the report
        agg_results (bool, optional): whether to aggregate the results or not
        export_file (bool, optional): whether to export the report in the form of a json file or not
        sparql_secret (str, optional): the secret to use for the SPARQL queries
    """

    def __init__(
        self,
        target_topic: str,
        source_topic: Optional[str] = None,
        # TODO. adjust this value to the EKS value - but it needs to be JMX hostname and port
        broker: str = "kafka-0.kafka.default.svc.cluster.local:9101",
        frequency: int = 1,
        metrics: Dict = KafkaMetrics().to_dict(),
        agg_results: bool = False,
        export_file: bool = False,
        sparql_secret: Optional[str] = None,
    ):
        self.broker = broker
        self.frequency = frequency
        self.target_topic = target_topic
        self.source_topic = source_topic
        self.metrics = metrics
        self.agg_results = agg_results
        self.export_file = export_file
        self.sparql_secret = sparql_secret

        self._handler()

    def _handler(self):
        """
        Heart of the operations.

        This function will be used to call all the modules from the class to produce the report.

        The way it works is for frequency defined (in seconds) - let's say 10 seconds - it will query the
        broker every 10 seconds until there's no more messages to be read.

        Additionally, it is important to mention, that the collection of metrics is only triggered when
        there's incoming messages to the topic.

        The course of action is:
        - Setup the connection to the broker;
        - Extract the metrics from the broker;
        - [_If needed_] Aggregate the results;
        - [_If needed_] Export the report.
        """

        metrics_collected = False
        prev_messages_in = 0

        self.report_data = []
        self.connection = self._setup_connection()
        self.topics = (
            [self.target_topic, self.source_topic] if self.source_topic else [self.target_topic]
        )

        logger.info("Collecting metrics...")

        messages_query = KafkaMetrics().messages_in_per_second(self.target_topic)

        while True:
            time.sleep(self.frequency)
            messages_in = self.connection.query([JMXQuery(messages_query)])

            if len(messages_in) != 0:
                metrics_collected = True
                metrics = self._extract_metrics()
                self.report_data.append(metrics)
                prev_messages_in = len(messages_in)

            if metrics_collected and (len(messages_in) == prev_messages_in):
                break

        if self.export_file:
            self.export_report()

        else:
            return self.report_data

    def _setup_connection(self) -> JMXConnection:
        """
        Setup the connection to the broker.
        """

        return JMXConnection(f"service:jmx:rmi:///jndi/rmi://{self.broker}/jmxrmi")

    def _extract_metrics(self) -> Dict:
        """
        Extract the metrics from the broker.

        The metrics extracted are the ones defined in the KafkaMetrics class. They leverage the JMXQuery
        to extract the metrics from the broker.

        The output is a dictionary with the following structure:
        {
            "timestamp": timestamp of the report,
            "topic_1": {"metric_1": value, "metric_2": value},
            "topic_2": {"metric_1": value, "metric_2": value},
        }

        Additionally, if a sparql secret is provided, a sample of the sparql query is added to the report.

        Returns:
            Dict: dictionary with the metrics extracted from the broker
        """

        output = {topic: {} for topic in self.topics}
        kafka_metrics = KafkaMetrics().to_dict()

        for topic in self.topics:

            # Define the set of queries that will be performed
            queries_lst = [JMXQuery(kafka_metrics[key](topic)) for key in kafka_metrics]

            # Query the connection once and process the response
            response = self.connection.query(queries_lst)
            response_converted = {
                key: result.value for key, result in zip(kafka_metrics.keys(), response)
            }

            # Apply aggregation if needed
            if self.agg_results:
                response_converted = aggregator(response_converted)

            output[topic] = response_converted

        # Create a sparql sample if the secret is provided - should be provided is target topic is knowledge
        data_sample = {"sparql_sample": run_sparql_query(self.sparql_secret)} if self.sparql_secret else {}

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **output,
            **data_sample,
        }

    def export_report(self, file_name: str = "kafka_report.json") -> None:
        """
        Export the report.

        The report produced will be extracted in a json file.

        Args:
            file_name (str): name of the file to export the report
        """

        try:
            logger.info("Exporting the report...")
            with open(f"{file_name}", "w") as file:
                json.dump(self.report_data, file, indent=4)

        except Exception as e:
            logger.error(f"Error exporting the report: {e}")
