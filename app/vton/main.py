import cv2
import numpy as np
from PIL import Image
import json
import os
from pathlib import Path
import torch
import shutil
import subprocess


class VTONModel:
    def __init__(self):
        self.gmm_model = "checkpoints/step_095000.pth"
        self.tom_model = "checkpoints/tom_final.pth"

    def run_gmm(self):
        gmm_cmd = [
            "python",
            "test.py",
            "--name",
            "GMM",
            "--stage",
            "GMM",
            "--workers",
            "1",
            "--datamode",
            "test",
            "--data_list",
            "test_pairs.txt",
            "--dataroot",
            os.path.abspath(self.test_dir),
            "--checkpoint",
            self.gmm_checkpoint,
        ]
        print("Running GMM...")
        gmm_process = subprocess.run(gmm_cmd, capture_output=True, text=True)
        if gmm_process.returncode != 0:
            print(f"GMM failed with error: {gmm_process.stderr}")
            raise RuntimeError("GMM processing failed.")

    def run_tom(self):
        tom_cmd = [
            "python",
            "test.py",
            "--name",
            "TOM",
            "--stage",
            "TOM",
            "--workers",
            "1",
            "--datamode",
            "test",
            "--data_list",
            "test_pairs.txt",
            "--dataroot",
            os.path.abspath(self.test_dir),
            "--checkpoint",
            self.tom_checkpoint,
        ]
        print("Running TOM...")
        tom_process = subprocess.run(tom_cmd, capture_output=True, text=True)
        if tom_process.returncode != 0:
            print(f"TOM failed with error: {tom_process.stderr}")
            raise RuntimeError("TOM processing failed.")

    def process(self):
        try:
            # GMM 실행
            self.run_gmm()

            # TOM 실행
            self.run_tom()

            # 결과 이미지 로드 (메모리에서 바로 반환)
            result_image_path = os.path.join(
                self.test_dir, "result", "TOM", "final_output.jpg"
            )
            if not os.path.exists(result_image_path):
                raise FileNotFoundError(f"Result image not found: {result_image_path}")

            # 결과 이미지를 OpenCV 형식으로 로드하여 반환
            result_image = cv2.imread(result_image_path)
            if result_image is None:
                raise RuntimeError("Failed to load the result image.")
            return result_image
        except Exception as e:
            print(f"Error during virtual fitting process: {e}")
            return None

        except Exception as e:
            print(f"Error processing dataset: {e}")
            import traceback

            traceback.print_exc()
