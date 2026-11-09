import cv2
import numpy as np
from hailo_platform import (
    HEF,
    VDevice,
    HailoStreamInterface,
    ConfigureParams,
    InputVStreamParams,
    OutputVStreamParams,
    FormatType
)
import json

# ---------------- USER PATHS ----------------
HEF_PATH = "/home/ssve/hailo/hailo-rpi5-examples/resources/json/1.hef"
JSON_PATH = "/home/ssve/hailo/hailo-rpi5-examples/resources/json/2.json"
INPUT_IMAGE_PATH = "/home/ssve/github-repo/rpi-cam-yolo11-main/inference_images/1.jpg"
OUTPUT_IMAGE_PATH = "/home/ssve/github-repo/rpi-cam-yolo11-main/captured_images/output.jpg"
# -------------------------------------------


def preprocess(image, input_shape):
    h, w = input_shape
    image = cv2.resize(image, (w, h))
    image = image.astype(np.float32)
    image = image / 255.0
    return image


def main():
    # Load HEF
    hef = HEF(HEF_PATH)

    # Create virtual device
    with VDevice() as vdevice:
        network_group = vdevice.configure(
            hef,
            ConfigureParams.create_from_hef(
                hef, interface=HailoStreamInterface.PCIe
            )
        )[0]

        input_info = network_group.get_input_vstream_infos()[0]
        output_infos = network_group.get_output_vstream_infos()

        input_shape = (input_info.shape.height, input_info.shape.width)

        # Load JSON (labels + thresholds)
        with open(JSON_PATH, "r") as f:
            config = json.load(f)

        labels = config["labels"]
        score_thr = config["nms_score_threshold"]

        # Read image
        image = cv2.imread(INPUT_IMAGE_PATH)
        orig = image.copy()

        input_data = preprocess(image, input_shape)
        input_data = np.expand_dims(input_data, axis=0)

        # Stream params
        in_params = InputVStreamParams.make(
            network_group, format_type=FormatType.FLOAT32
        )
        out_params = OutputVStreamParams.make(
            network_group, format_type=FormatType.FLOAT32
        )

        # Run inference
        with network_group.activate(), \
             network_group.create_input_vstreams(in_params) as in_streams, \
             network_group.create_output_vstreams(out_params) as out_streams:

            in_streams[0].send(input_data)

            outputs = {}
            for out in out_streams:
                outputs[out.info.name] = out.recv()

        # ---- SIMPLE YOLO OUTPUT VISUALIZATION ----
        # Expected output: [N, 6] -> x,y,w,h,score,class_id
        detections = np.concatenate(list(outputs.values()), axis=1)[0]

        h_img, w_img, _ = orig.shape

        for det in detections:
            score = det[4]
            if score < score_thr:
                continue

            class_id = int(det[5])
            label = labels[class_id]

            cx, cy, bw, bh = det[:4]

            x1 = int((cx - bw / 2) * w_img)
            y1 = int((cy - bh / 2) * h_img)
            x2 = int((cx + bw / 2) * w_img)
            y2 = int((cy + bh / 2) * h_img)

            cv2.rectangle(orig, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                orig,
                f"{label}:{score:.2f}",
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )

        # Save output
        cv2.imwrite(OUTPUT_IMAGE_PATH, orig)
        print("✅ Detection complete")
        print("Saved to:", OUTPUT_IMAGE_PATH)


if __name__ == "__main__":
    main()

