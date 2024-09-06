"use client";
import { useRef, useEffect, useCallback, useState } from "react";
import Webcam from "react-webcam";
import { BASE_URL } from "../../lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";

export default function Receiver() {
  // send image every fps
  const [image, setImage] = useState(null);
  const { lastMessage, readyState } = useWebSocket(`${BASE_URL}/ws/receiver`, {
    onMessage: (message) => {
      const jsonData = JSON.parse(message.data);
      console.log("Received")
      setImage(`${BASE_URL}/files/${jsonData.image}`);
    },
  });

  useEffect(() => {
    if (readyState === ReadyState.OPEN) {
      console.log("Connected");
    }
  }, [readyState]);

  return (
    <div>
      <img src={image} />
    </div>
  );
}
