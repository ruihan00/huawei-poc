"use client";
import { useRef, useEffect, useCallback, useState } from "react";
import Webcam from "react-webcam";
import { BASE_URL } from "../../lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";

export default function Sender({ fps }) {
  const webcamRef = useRef(null);
  const { sendMessage, readyState } = useWebSocket(`${BASE_URL}/sender`);
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
    sendMessage(
      JSON.stringify({
        timestamp: new Date().toISOString(),
        image: imageSrc,
      })
    );
  };

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

  return (
    <div>{isClient && <Webcam ref={webcamRef} width={720} height={480} />}</div>
  );
}
