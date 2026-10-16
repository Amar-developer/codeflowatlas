import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "CodeFlowAtlas | Understand the code AI wrote for you",
  description:
    "A visual code-flow learning lab for students and AI-assisted builders.",
};

const RootLayout = ({ children }: { children: ReactNode }) => (
  <html lang="en">
    <body>{children}</body>
  </html>
);

export default RootLayout;