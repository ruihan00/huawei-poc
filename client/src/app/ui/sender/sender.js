"use client";
import { useRef, useEffect, useCallback, useState } from "react";
import Webcam from "react-webcam";
import { BASE_URL } from "../../lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";

export default function Sender({ fps }) {
  const webcamRef = useRef(null);
  const { sendMessage, readyState } = useWebSocket(`${BASE_URL}/ws/sender`);
  const [isClient, setIsClient] = useState(false);

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
    console.log("Sending frame");
    sendMessage(
      JSON.stringify({
        timestamp: new Date().toISOString(),
        image: imageSrc,
      }),
    );
  };

  useEffect(() => {
    console.log({ readyState, fps });
    setIsClient(true); // Ensure this is running in the browser

    if (readyState !== ReadyState.OPEN) {
      return;
    }

    console.log("Updating FPS");
    const interval = 1000 / fps;
    const intervalId = setInterval(handleFrameUpload, interval);

    return () => {
      console.log("Interval cleared");
      clearInterval(intervalId);
    };
  }, [readyState, fps]);

  return (
    <div>
      {isClient && <Webcam ref={webcamRef} height={720} width={1280} />}
    </div>
  );
}
