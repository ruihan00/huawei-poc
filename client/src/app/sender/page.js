"use client";
import { useRef, useEffect, useCallback } from "react";
import Webcam from "react-webcam";
import { BASE_URL } from "../lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";

export default function Sender() {
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
