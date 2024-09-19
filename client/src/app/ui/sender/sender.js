"use client";
import { useRef, useEffect, useCallback, useState } from "react";
import Webcam from "react-webcam";
import { BASE_URL } from "../../lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";

export default function Sender() {
  const fps = 5;
  const interval = 1000 / fps;
  const webcamRef = useRef(null);
  const { sendMessage, readyState } = useWebSocket(
    `${BASE_URL}/ws/sender`
  );
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
    sendMessage(imageSrc);
  };

  useEffect(() => {
    setIsClient(true); // Ensure this is running in the browser

    if (readyState === ReadyState.OPEN) {
      console.log("Connected");
      const intervalId = setInterval(handleFrameUpload, interval);
      return () => clearInterval(intervalId);
    }
  }, [readyState]);

  return (
    <div>
      {isClient && (
        <Webcam ref={webcamRef} height={720} width={1280} />
      )}
    </div>
  );
}
