"use client";
import styles from "./page.module.css";

import { useState } from "react";

import Sender from "./ui/sender/sender";
import Receiver from "./ui/receiver/receiver";
import PHeader from "./ui/layout/pheader";
import PFooter from "./ui/layout/pfooter";
import { Layout } from "antd";

const { Content } = Layout;

export default function Home() {
  return (
    <Layout style={{ display: "flex", flexDirection: "column" }}>
      <PHeader title="SGTransaid" />
      <Content style={{ backgroundColor: "#FFFFE4", color: "#FFF" }}>
        <main className={styles.main}>
          <Sender />
          <Receiver />
        </main>
      </Content>
      <PFooter title="SGTransaid" />
    </Layout>
  );
}
