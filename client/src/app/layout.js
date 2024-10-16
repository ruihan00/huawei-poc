import { Inter } from "next/font/google";
import "./globals.css";
import { AntdRegistry } from "@ant-design/nextjs-registry";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "SGTransaid",
  description: "Created by Binacloud",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" />
      </head>
      <AntdRegistry>
        <body className={inter.className}>{children}</body>
      </AntdRegistry>
    </html>
  );
}
