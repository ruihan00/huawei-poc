"use client";
import { useRef, useEffect, useCallback, useState } from "react";
import Webcam from "react-webcam";
import { BASE_URL } from "../../lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";

const blobFromBase64String = base64String => {
  const byteArray = Uint8Array.from(
    atob(base64String)
      .split('')
      .map(char => char.charCodeAt(0))
  );
 return new Blob([byteArray], { type: 'image/png' });
};

export default function Receiver() {
  // send image every fps
  const { lastMessage, readyState } = useWebSocket(`${BASE_URL}/ws/receiver`, {
    filter: () => false, // don't re-render on new websocket msg
    onMessage: (message) => {
      const data = JSON.parse(message.data);
      console.log("Received");
      // setImage(`${BASE_URL}/files/${jsonData.image}`);
      // Assuming `imageBytes` is an ArrayBuffer or Uint8Array containing the raw image data
      const blob = blobFromBase64String(data.image);
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
      <img id="result" />
    </div>
  );
}
