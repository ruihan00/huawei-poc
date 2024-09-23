"use client";

import { useRef, useEffect, useCallback, useState } from "react";
import { BASE_URL } from "../lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";

export default function Page() {
  const [cameras, setCameras] = useState([])
  const { lastMessage, readyState } = useWebSocket(`${BASE_URL}/ws/receiver`, {
    filter: () => false, // don't re-render on new websocket msg
    onMessage: (message) => {
      data = JSON.parse(message.data)
      const id = data.id
      if (! cameras.includes(id)) {
        setCameras(prev => [...prev, id])
      }
        
      const bytes = data.data;
      console.log("Received");
      // setImage(`${BASE_URL}/files/${jsonData.image}`);
      // Assuming `imageBytes` is an ArrayBuffer or Uint8Array containing the raw image data
      const blob = new Blob([bytes], { type: "image/jpeg" }); // Adjust MIME type as needed
      const newUrl = URL.createObjectURL(blob);
        
      const img = document.getElementById(id);
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
    <main>
      {
        cameras.map((key) => {
            <img id={key} />
        })
      }
      
    </main>
  );
}
