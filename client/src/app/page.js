"use client";
import styles from "./page.module.css";

import { useState } from "react";

import Sender from "./ui/sender/sender";
import Receiver from "./ui/receiver/receiver";
import PHeader from "./ui/layout/pheader"
import PFooter from "./ui/layout/pfooter"
import { Layout } from "antd";

const { Content } = Layout;

export default function Home() {
  const [fps, setFps] = useState(1);

  return (
    <Layout style={{ display: 'flex', flexDirection: 'column' }}>
      <PHeader title="SGTransaid"/>
      <Content style={{ backgroundColor: '#000', color: '#FFF' }}>
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
      </Content>
      <PFooter title="SGTransaid"/>
    </Layout>
  );
}
