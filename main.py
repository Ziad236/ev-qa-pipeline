from scrapper2 import DataCollector
import  config
from data_preprocessing import preprocess_data

collector = DataCollector(config)
raw_data = collector.run()
processed_data = preprocess_data(raw_data)

print(processed_data[0])
print(processed_data[1])