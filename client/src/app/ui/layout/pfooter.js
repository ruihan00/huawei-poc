"use client";
import { Layout } from "antd";

const { Footer } = Layout;

const PFooter = ({ title }) => {
  return (
    <Footer style={{ backgroundColor: '#070738', color: '#FFF', textAlign: 'center', height: '64px' }}>
        {title} ©{new Date().getFullYear()} Created by BinaCloud
    </Footer>
  );
};

export default PFooter;