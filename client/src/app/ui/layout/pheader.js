"use client";
import { Layout } from "antd";

const { Header } = Layout;

const PHeader = ({ title }) => {
  return (
    <Header style={{ backgroundColor: '#070738', color: '#FFF', padding: 0, height: '64px' }}>
      <h1 style={{ margin: 0, padding: '0 16px' }}>{title}</h1>
    </Header>
  );
};

export default PHeader;