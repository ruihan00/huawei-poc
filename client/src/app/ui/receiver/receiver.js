"use client";
import { useRef, useEffect, useCallback, useState } from "react";
import Webcam from "react-webcam";
import { BASE_URL } from "../../lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";

export default function Receiver() {
  // send image every fps
  const { lastMessage, readyState } = useWebSocket(`${BASE_URL}/ws/receiver`, {
    onMessage: (message) => {
      const bytes = message.data;
      console.log("Received")
      // setImage(`${BASE_URL}/files/${jsonData.image}`);
      // Assuming `imageBytes` is an ArrayBuffer or Uint8Array containing the raw image data
      const blob = new Blob([bytes], { type: 'image/jpeg' }); // Adjust MIME type as needed
      const newUrl = URL.createObjectURL(blob);

      const img = document.getElementById("result");
      if (!img) {
        return;
      }

      const originalUrl = img.src;
      img.src = newUrl;

      // Clean up the original URL as it is no longer needed
      URL.revokeObjectURL(originalUrl);
    },
  });

  useEffect(() => {
    if (readyState === ReadyState.OPEN) {
      console.log("Connected");
    }
  }, [readyState]);

  return (
    <div id="container">
      <img id="result"/>
    </div>
  );
}
