"use client";
import styles from "./page.module.css";

import { useRef, useEffect, useCallback, useState } from "react";
import Webcam from "react-webcam";
import { BASE_URL } from "./lib/api";
import useWebSocket, { ReadyState } from "react-use-websocket";
import Sender from "./ui/sender/sender";
import Receiver from "./ui/receiver/receiver";

export default function Home() {
  const [fps, setFps] = useState(1);

  return (
    <main className={styles.main}>
      <label>FPS</label>
      <input
        type="number"
        value={fps}
        onChange={(e) => setFps(e.target.value)}
      />
      <Sender fps={fps} />
      <Receiver />
    </main>
  );
}
