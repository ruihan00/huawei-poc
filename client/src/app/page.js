"use client";
import styles from "./page.module.css";

import { useState } from "react";

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
