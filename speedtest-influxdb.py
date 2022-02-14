import datetime
import subprocess
import json
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Function to run speedtest process
def speedtest():
    try:
        # Run speedtest and return result dict
        process_out = subprocess.check_output(['/usr/bin/speedtest', '-f', 'json', '-s', '22669', '--accept-gdpr'])
    except subprocess.CalledProcessError as e:
        print("Error running Speedtest process\n", e.output)
        return None
    return(process_out)

def main():
    # InfluxDB parameters
    # InfluxDB server IP:port or hostname:port
    INFLUXDB_SERVER = "http://x.x.x.x:8086"
    # InfluxDB organization
    INFLUXDB_ORG = "ORG"
    # InfluxDB token
    INFLUXDB_TOKEN = "TOKEN"
    # InfluxDB bucket
    INFLUXDB_BUCKET = "speedtest"

    # Get current timestamp
    current_timestamp = datetime.datetime.utcnow()

    # Run speedtest function
    output = speedtest()

    if output != None:
        # Load output as JSON
        output_json = json.loads(output)

        # Verify that type is a speedtest result
        if(output_json['type'] == "result"):
            # Build proper JSON data format for InfluxDB
            json_body = [{
                "measurement": "bandwidth_data",
                "tags": {
                    "measurement_name": output_json['server']['name']
                },
                "time": current_timestamp.isoformat(),
                "fields": {
                    "Jitter": output_json['ping']['jitter'],
                    "Latency": output_json['ping']['latency'],
                    "Packet loss": float(output_json['packetLoss']),
                    "Download": output_json['download']['bandwidth'],
                    "Upload": output_json['upload']['bandwidth']
                }
            }]

            # Open connection to InfluxDB
            client = InfluxDBClient(url=INFLUXDB_SERVER, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

            # Set the client to write in synchronous mode
            write_api = client.write_api(write_options=SYNCHRONOUS)

            # Write the data to InfluxDB database
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=json_body)
            
            print("Speedtest output sent successfully!")
        else:
            print("Speedtest result parsing failed!")

if __name__ == "__main__":
    main()
