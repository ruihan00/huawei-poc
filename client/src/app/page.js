"use client";
import styles from "./page.module.css";

import { useRef, useEffect, useCallback, useState } from "react";
import Webcam from "react-webcam";
import { BASE_URL } from "./lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";
function Sender() {
  // send image every fps
  const fps = 5;
  const interval = 1000 / fps;
  const webcamRef = useRef(null);
  const { sendMessage, lastMessage, readyState } = useWebSocket(
    `${BASE_URL}/ws/sender`
  );

  let socket = null;
  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) {
      return;
    }
    console.log(`frame: ${imageSrc.length}`);
    return imageSrc;
  }, [webcamRef]);

  const handleFrameUpload = () => {
    const imageSrc = capture();
    if (!imageSrc) {
      return;
    }
    console.log("Sending frame");
    sendMessage(imageSrc);
  };

  useEffect(() => {
    if (readyState === ReadyState.OPEN) {
      console.log("Connected");
      const intervalId = setInterval(handleFrameUpload, interval);
      return () => clearInterval(intervalId);
    }
  }, [readyState]);
  return (
    <div>
      <Webcam ref={webcamRef} height={720} width={1280} />
    </div>
  );
}

function Receiver() {
  // send image every fps
  const [image, setImage] = useState(null);
  const { lastMessage, readyState } = useWebSocket(`${BASE_URL}/ws/receiver`, {
    onMessage: (message) => {
      const jsonData = JSON.parse(message.data);
      setImage(jsonData.image);
    },
  });

  useEffect(() => {
    if (readyState === ReadyState.OPEN) {
      console.log("Connected");
    }
  }, [readyState]);

  return (
    <div>
      <img src={`data:image/png;base64,${image}`} />
    </div>
  );
}

export default function Home() {
  return (
    <main className={styles.main}>
      <Sender />
      <Receiver />
    </main>
  );
}
