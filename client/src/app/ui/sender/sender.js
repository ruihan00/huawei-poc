"use client";

import { useRef, useEffect, useCallback, useState } from "react";
import Webcam from "react-webcam";
import { BASE_URL } from "../../lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { Input, Card, Button, Dropdown, Space } from "antd";
import { PlusOutlined, MinusOutlined, DownOutlined } from "@ant-design/icons";
import styles from "./styles.module.css";
async function getAvailableVideoCameras() {
  try {
    // Request permission to access media devices if not already granted
    await navigator.mediaDevices.getUserMedia({ video: true });
    // Enumerate all available media devices
    const devices = await navigator.mediaDevices.enumerateDevices();
    // Filter out only video input devices (cameras)
    const videoCameras = devices.filter(
      (device) => device.kind === "videoinput"
    );
    return videoCameras;
    // // Log the available video cameras to the console
    // console.log("Available video cameras:", videoCameras);

    // // You can also use the devices information in your UI or application
    // videoCameras.forEach(camera => {
    //   console.log(`Camera: ${camera.label}, ID: ${camera.deviceId}`);
    // });
  } catch (error) {
    console.error("Error accessing video cameras: ", error);
    return [];
  }
}

export default function Sender() {
  const [fps, setFps] = useState(1);
  const [isClient, setIsClient] = useState(false);
  const [cameras, setCameras] = useState([]);
  const [selectedCameraId, setSelectedCameraId] = useState(null);

  const webcamRef = useRef(null);
  const { sendMessage, readyState } = useWebSocket(`${BASE_URL}/sender`);

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) {
      return;
    }
    return imageSrc;
  }, [webcamRef]);

  const handleFrameUpload = () => {
    const imageSrc = capture();
    if (!imageSrc) {
      return;
    }
    sendMessage(
      JSON.stringify({
        timestamp: new Date().toISOString(),
        image: imageSrc,
      })
    );
  };

  // On startup, get the list of cameras available
  useEffect(() => {
    async function _() {
      const cameras = await getAvailableVideoCameras();
      setCameras(cameras);
      if (cameras.length > 0) {
        setSelectedCameraId(cameras[0].deviceId);
      }
    }
    _();
  }, []);

  // As needed, change the sending interval
  useEffect(() => {
    setIsClient(true); // Ensure this is running in the browser
    if (readyState !== ReadyState.OPEN) {
      return;
    }

    const interval = 1000 / fps;
    const intervalId = setInterval(handleFrameUpload, interval);

    return () => {
      clearInterval(intervalId);
    };
  }, [readyState, fps]);

  const items = cameras.map((camera) => {
    return {
      label: camera.label,
      key: camera.deviceId,
    };
  });
  function onClick({ key }) {
    setSelectedCameraId(key);
  }

  return (
    <>
      <div>
        <Dropdown menu={{ items, onClick }}>
          <Button>
            <Space>
              {
                cameras.find((camera) => camera.deviceId === selectedCameraId)
                  ?.label
              }
              <DownOutlined />
            </Space>
          </Button>
        </Dropdown>
        <Space.Compact>
          <Button
            color="default"
            icon={<MinusOutlined />}
            onClick={() => setFps((fps) => (fps >= 1 ? fps - 1 : fps))}
          />
          <Input
            suffix="FPS"
            value={fps}
            onChange={(e) => {
              const str = e.target.value;
              if (!isNaN(str) && Number.isInteger(Number(str))) {
                setFps(Number(str));
              }
            }}
          />
          <Button
            color="default"
            icon={<PlusOutlined />}
            onClick={() => setFps((fps) => fps + 1)}
          />
        </Space.Compact>
      </div>
      <div className={styles.camera}>
        {isClient && selectedCameraId && (
          <Card bodyStyle={{ padding: "3px" }}>
            <div width={640} height={480}>
              <Webcam
                ref={webcamRef}
                videoConstraints={{
                  deviceId: selectedCameraId,
                  width: 640,
                  height: 480,
                }}
              />
            </div>
          </Card>
        )}
      </div>
    </>
  );
}
