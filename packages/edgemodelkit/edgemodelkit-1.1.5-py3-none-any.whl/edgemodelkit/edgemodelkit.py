import serial
import time
import numpy as np
import pandas as pd
import json
import os
import sys
import tensorflow as tf


def _process_packet(raw_packet, sensor_data_records, sample_index, add_timestamp, add_count):
    sensor_values = raw_packet.get("sensorValues", [])
    sensor_record = {}
    if add_timestamp:
        sensor_record["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    if add_count:
        sensor_record["sample_count"] = sample_index + 1
    sensor_record.update({f"data_value_{i + 1}": value for i, value in enumerate(sensor_values)})
    sensor_data_records.append(sensor_record)

def ensure_directory_exists(dir_path):
    os.makedirs(dir_path, exist_ok=True)

class DataFetcher:
    def __init__(self, serial_port, baud_rate=9600):
        self.serial_connection = serial.Serial(port=serial_port, baudrate=baud_rate)

    def close_connection(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Serial connection closed.")

    def fetch_data(self, return_as_numpy=False):
        try:
            raw_packet = json.loads(self.serial_connection.readline().decode())
            if return_as_numpy:
                return np.array(raw_packet['sensorValues'])
            else:
                return raw_packet['sensorValues']
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error fetching data: {e}")
            return [] if not return_as_numpy else np.array([])

    def log_sensor_data(self, class_label=None, num_samples=5, add_timestamp=True, add_count=True, output_dir="."):
        initial_packet = json.loads(self.serial_connection.readline().decode())
        sensor_name = initial_packet.get("sensorName", "Unknown")
        file_name = f"{sensor_name}_data_log.csv"
        if class_label:
            directory_path = os.path.join("Dataset", str(class_label))
        else:
            directory_path = "Dataset"

        # Ensure the directory exists
        ensure_directory_exists(directory_path)

        # Construct the full file path
        output_file_name = os.path.join(directory_path, file_name)

        sensor_data_records = []
        _process_packet(initial_packet, sensor_data_records, sample_index=0, add_timestamp=add_timestamp, add_count=add_count)

        print(f"Sampling {sensor_name} sensor.")
        for sample_index in range(1, num_samples):
            raw_packet = json.loads(self.serial_connection.readline().decode())
            _process_packet(raw_packet, sensor_data_records, sample_index, add_timestamp=add_timestamp, add_count=add_count)
            sys.stdout.write(f"\rGathering data: {sample_index + 1}/{num_samples}")
            sys.stdout.flush()
        print("\n")

        data_frame = pd.DataFrame(sensor_data_records)
        data_frame.to_csv(output_file_name, index=False)
        print(f"Data saved to {output_file_name}")

class ModelPlayGround:
    def __init__(self):
        self.output_details = None
        self.input_details = None
        self.interpreter = None
        self.loaded_model = None
        self.model_path = None

    def load_model(self, model_path: str):
        self.model_path = model_path
        self.loaded_model = tf.keras.models.load_model(self.model_path)

    def model_summary(self):
        self.loaded_model.summary()

    def model_stats(self):
        model_size = os.path.getsize(self.model_path) / 1024  # Size in KB
        print(f"Model Size: {model_size:.2f} KB")
        print(f"Number of Parameters: {self.loaded_model.count_params()}")

    def model_converter(self, quantization_type = "default"):
        saved_tflite_model_dir = "saved-model/tflite-models/"
        ensure_directory_exists(saved_tflite_model_dir)

        base_model_name = os.path.splitext(os.path.basename(self.model_path))[0]

        def save_tflite_model(tflite_model, file_suffix):
            output_file_name = os.path.join(saved_tflite_model_dir, f"{base_model_name}_{file_suffix}.tflite")
            with open(output_file_name, 'wb') as f:
                f.write(tflite_model)
            print(f"Saved {file_suffix} model at: {output_file_name}")

        # Default (float32) model
        if quantization_type == "default":
            print("Converting to default (float32) TFLite model...")
            converter = tf.lite.TFLiteConverter.from_keras_model(self.loaded_model)
            tflite_model = converter.convert()
            save_tflite_model(tflite_model, "default")

        # Float16 quantized model
        if quantization_type == "float16":
            print("Converting to float16 TFLite model...")
            converter = tf.lite.TFLiteConverter.from_keras_model(self.loaded_model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_types = [tf.float16]
            tflite_model = converter.convert()
            save_tflite_model(tflite_model, "float16")

        # Int8 quantized model
        if quantization_type == "int8":
            print("Converting to int8 TFLite model...")
            converter = tf.lite.TFLiteConverter.from_keras_model(self.loaded_model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]

            # Representative Dataset for int8 Quantization
            def representative_data_gen():
                for _ in range(100):
                    # Generate random data matching the input shape
                    yield [np.random.rand(*self.loaded_model.input_shape[1:]).astype(np.float32)]

            converter.representative_dataset = representative_data_gen
            converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
            converter.inference_input_type = tf.uint8  # or tf.int8
            converter.inference_output_type = tf.uint8  # or tf.int8
            tflite_model = converter.convert()
            save_tflite_model(tflite_model, "int8")

    def set_edge_model(self, tflite_model_path):
        self.interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def edge_testing(self, data_fetcher, preprocess_func=None, debug=False):
        if not hasattr(self, 'interpreter'):
            raise ValueError("Edge model not set. Call `set_edge_model` first.")

        sensor_data = data_fetcher.fetch_data(return_as_numpy=True)
        if sensor_data.size == 0:
            if debug:
                print("No sensor data received.")
            return None

        # Apply preprocessing if a function is provided
        if preprocess_func:
            sensor_data = preprocess_func(sensor_data)

        # Ensure the input shape matches the model's expected input
        input_shape = self.input_details[0]['shape']
        input_data = sensor_data.astype(self.input_details[0]['dtype'])

        if debug:
            print(f"Expected shape is: {input_shape}, provided shape is: {sensor_data.shape}")

        # Set input tensor
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)

        # Perform inference
        start_time = time.perf_counter()
        self.interpreter.invoke()
        stop_time = time.perf_counter()

        if debug:
            print(f"Inference time: {stop_time - start_time:.6f} seconds")

        # Get prediction
        prediction = self.interpreter.get_tensor(self.output_details[0]['index'])

        return {"SensorData": input_data, "ModelOutput": prediction}



